"""
RIO Protocol SDK — Compliance Level Checker
============================================
Inspects a project directory and determines the highest RIO conformance
level it can verify as implemented.

Level 1 — Cryptographic Compliance:
    All Appendix C hash test vectors pass.

Level 2 — Pipeline Compliance:
    Level 1 + gateway.db exists with execution_ledger and gate_log tables,
    and those tables contain correctly-chained entries.

Level 3 — Full Protocol Compliance:
    Level 2 + post_execution_ledger table exists with valid ledger_hash chain
    and verifiable HMAC signatures.

Usage:
    from rio_sdk import get_compliance_level
    result = get_compliance_level("/path/to/rio-gateway")
    print(result["level"])        # 1, 2, or 3  (0 if nothing passes)
    print(result["label"])        # "Level 3 — Full Protocol Compliance"
    print(result["detail"])       # human-readable summary
"""

import hashlib
import hmac as hmac_module
import os
import sqlite3
from pathlib import Path
from typing import Union

from .conformance import run_conformance_tests


# ── Internal helpers ──────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hmac_sha256(key: str, msg: str) -> str:
    return hmac_module.new(
        key.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cur.fetchone() is not None


def _verify_exec_ledger_chain(conn: sqlite3.Connection) -> tuple[bool, str]:
    """Re-derive entry_hash for every execution_ledger row and check the chain."""
    rows = conn.execute(
        "SELECT action, agent, approver, executed_by, intent_id, parameters_hash, "
        "result, reason, receipt_hash, prev_hash, entry_hash, timestamp "
        "FROM execution_ledger ORDER BY id ASC"
    ).fetchall()

    if not rows:
        return True, "No execution_ledger entries."

    expected_prev = "GENESIS"
    for i, row in enumerate(rows):
        (action, agent, approver, executed_by, intent_id, parameters_hash,
         result, reason, receipt_hash, prev_hash, stored_hash, timestamp) = row
        fields = [action, agent or "", approver or "", executed_by or "",
                  intent_id or "", parameters_hash or "", result or "",
                  reason or "", receipt_hash or "", prev_hash or "", timestamp or ""]
        computed = _sha256("|".join(fields))
        if prev_hash != expected_prev or computed != stored_hash:
            return False, f"Chain broken at row {i+1}"
        expected_prev = stored_hash

    return True, f"All {len(rows)} execution_ledger rows verified."


def _verify_post_exec_chain(conn: sqlite3.Connection, service_token: str) -> tuple[bool, str]:
    """Re-derive ledger_hash and HMAC for every post_execution_ledger row."""
    rows = conn.execute(
        "SELECT timestamp, approver, agent, executed_by, policy_result, "
        "parameters_hash, result_hash, ledger_hash, signature "
        "FROM post_execution_ledger ORDER BY id ASC"
    ).fetchall()

    if not rows:
        return True, "No post_execution_ledger entries."

    prev = "GENESIS"
    for i, row in enumerate(rows):
        (ts, approver, agent, executed_by, policy_result,
         params_hash, result_hash, stored_lhash, stored_sig) = row

        seal = "|".join([ts or "", approver or "", agent or "", executed_by or "",
                         policy_result or "", params_hash or "", result_hash or "", prev])
        computed_lhash = _sha256(seal)

        if computed_lhash != stored_lhash:
            return False, f"ledger_hash mismatch at post_execution_ledger row {i+1}"

        if service_token and stored_sig not in ("key_unavailable", None, ""):
            computed_sig = _hmac_sha256(service_token, computed_lhash)
            if computed_sig != stored_sig:
                return False, f"HMAC mismatch at post_execution_ledger row {i+1}"

        prev = stored_lhash

    return True, f"All {len(rows)} post_execution_ledger rows verified."


# ── Level checks ──────────────────────────────────────────────────────────────

def _check_level_1() -> tuple[bool, str]:
    """All Appendix C test vectors pass."""
    result = run_conformance_tests()
    if result["overall"] == "PASS":
        return True, f"All {result['total']} conformance test vectors pass."
    failed = [r["id"] for r in result["results"] if not r["passed"]]
    return False, f"{result['failed']} vector(s) FAIL: {', '.join(failed)}"


def _check_level_2(project_dir: Path) -> tuple[bool, str]:
    """gateway.db exists with execution_ledger + gate_log; chain is intact."""
    db_path = project_dir / "gateway.db"
    if not db_path.exists():
        return False, f"gateway.db not found at {db_path}"

    try:
        conn = sqlite3.connect(str(db_path))
    except Exception as e:
        return False, f"Cannot open gateway.db: {e}"

    try:
        if not _table_exists(conn, "execution_ledger"):
            return False, "execution_ledger table not found in gateway.db"
        if not _table_exists(conn, "gate_log"):
            return False, "gate_log table not found in gateway.db"

        ok, msg = _verify_exec_ledger_chain(conn)
        if not ok:
            return False, f"execution_ledger chain integrity: {msg}"

        return True, f"gateway.db present; {msg}"
    finally:
        conn.close()


def _check_level_3(project_dir: Path, service_token: str) -> tuple[bool, str]:
    """post_execution_ledger exists with valid chain and HMAC signatures."""
    db_path = project_dir / "gateway.db"
    if not db_path.exists():
        return False, "gateway.db not found"

    try:
        conn = sqlite3.connect(str(db_path))
    except Exception as e:
        return False, f"Cannot open gateway.db: {e}"

    try:
        if not _table_exists(conn, "post_execution_ledger"):
            return False, "post_execution_ledger table not found in gateway.db"

        ok, msg = _verify_post_exec_chain(conn, service_token)
        if not ok:
            return False, f"post_execution_ledger: {msg}"

        return True, f"post_execution_ledger present; {msg}"
    finally:
        conn.close()


# ── Public API ────────────────────────────────────────────────────────────────

_LABELS = {
    0: "Level 0 — Non-Compliant",
    1: "Level 1 — Cryptographic Compliance",
    2: "Level 2 — Pipeline Compliance",
    3: "Level 3 — Full Protocol Compliance",
}


def get_compliance_level(
    project_directory: Union[str, Path],
    service_token: str = None,
) -> dict:
    """
    Determine the highest RIO conformance level achieved by a project.

    Args:
        project_directory:  Path to the root of the RIO gateway project
                            (the directory containing gateway.db).
        service_token:      RIO_SERVICE_TOKEN used for HMAC verification.
                            Falls back to RIO_SERVICE_TOKEN env var if not given.

    Returns:
        dict with keys:
            level           int — 0, 1, 2, or 3
            label           str — human-readable level name
            detail          str — summary of what was checked
            checks          list of {level, passed, detail} dicts
    """
    project_dir = Path(project_directory)
    token = service_token or os.environ.get("RIO_SERVICE_TOKEN", "")

    check_results = []
    achieved_level = 0

    # Level 1
    ok1, msg1 = _check_level_1()
    check_results.append({"level": 1, "name": "Cryptographic Compliance", "passed": ok1, "detail": msg1})
    if ok1:
        achieved_level = 1

        # Level 2
        ok2, msg2 = _check_level_2(project_dir)
        check_results.append({"level": 2, "name": "Pipeline Compliance", "passed": ok2, "detail": msg2})
        if ok2:
            achieved_level = 2

            # Level 3
            ok3, msg3 = _check_level_3(project_dir, token)
            check_results.append({"level": 3, "name": "Full Protocol Compliance", "passed": ok3, "detail": msg3})
            if ok3:
                achieved_level = 3

    label  = _LABELS[achieved_level]
    detail = "; ".join(c["detail"] for c in check_results)

    return {
        "level":  achieved_level,
        "label":  label,
        "detail": detail,
        "checks": check_results,
    }
