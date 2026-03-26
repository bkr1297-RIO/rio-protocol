"""
RIO Protocol SDK — Verifier
============================
Independent verification of RIO receipts and ledgers.

All verification is done locally using only Python standard library crypto
(hashlib, hmac). No gateway connection is required.

Formulas implement the RIO Protocol Specification v1.0, Sections 5 and 6.
"""

import hashlib
import hmac as hmac_module
import json
import os
from pathlib import Path
from typing import Union


# ── Internal crypto helpers ───────────────────────────────────────────────────

def _sha256(s: str) -> str:
    """SHA-256 of a UTF-8-encoded string. Returns lowercase hex."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hmac_sha256(key: str, msg: str) -> str:
    """HMAC-SHA256 with UTF-8-encoded key and message. Returns lowercase hex."""
    return hmac_module.new(
        key.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _load_json(path: Union[str, Path, dict]) -> dict:
    """Accept a file path (str/Path) or a pre-loaded dict."""
    if isinstance(path, dict):
        return path
    with open(path) as f:
        return json.load(f)


def _resolve_token(service_token, ledger: dict) -> str:
    """Resolve service token: argument → env var → ledger demo field."""
    if service_token:
        return service_token
    env = os.environ.get("RIO_SERVICE_TOKEN", "")
    if env:
        return env
    return ledger.get("demo_service_token", "")


# ── Individual checks ─────────────────────────────────────────────────────────

def _check_receipt_hash(receipt: dict) -> dict:
    """
    Recompute the in-memory ledger receipt_hash from source fields.

    Formula (spec Section 5.8):
        SHA-256(prev_hash + "|" + source + "|" + intent + "|"
                + model_used + "|" + ai_response[:500] + "|" + timestamp)
    """
    vi = receipt.get("_verification_inputs", {})
    prev_hash   = vi.get("prev_hash", "")
    source      = vi.get("source", "")
    intent      = vi.get("intent", "")
    model_used  = vi.get("model_used", "")
    ai_response = vi.get("ai_response_first_500_chars", receipt.get("response", ""))[:500]
    timestamp   = vi.get("timestamp", receipt.get("timestamp", ""))
    stored      = receipt.get("receipt_hash", "")

    data     = f"{prev_hash}|{source}|{intent}|{model_used}|{ai_response}|{timestamp}"
    computed = _sha256(data)
    passed   = computed == stored

    return {
        "check_name": "receipt_hash_integrity",
        "passed": passed,
        "stored": stored,
        "computed": computed,
        "detail": (
            "Receipt hash matches. Execution record is intact."
            if passed else
            f"MISMATCH — stored: {stored[:16]}…  computed: {computed[:16]}…"
        ),
    }


def _check_execution_ledger_chain(rows: list) -> dict:
    """
    Recompute entry_hash for each execution_ledger row and verify the hash chain.

    Formula (spec Section 5.6):
        SHA-256(action|agent|approver|executed_by|intent_id|parameters_hash|
                result|reason|receipt_hash|prev_hash|timestamp)
    """
    if not rows:
        return {"check_name": "execution_ledger_chain_integrity", "passed": True,
                "chain_intact": True, "rows_checked": 0, "detail": "No entries."}

    expected_prev = "GENESIS"
    row_results   = []
    failures      = []

    for row in rows:
        fields = [
            row.get("action", ""),
            row.get("agent", ""),
            row.get("approver", ""),
            row.get("executed_by", ""),
            row.get("intent_id", ""),
            row.get("parameters_hash", ""),
            row.get("result", ""),
            row.get("reason", ""),
            row.get("receipt_hash", ""),
            row.get("prev_hash", ""),
            row.get("timestamp", ""),
        ]
        computed  = _sha256("|".join(fields))
        stored    = row.get("entry_hash", "")
        prev_ok   = row.get("prev_hash", "") == expected_prev
        hash_ok   = computed == stored
        ok        = prev_ok and hash_ok

        row_results.append({
            "row_id": row.get("id"),
            "prev_hash_ok": prev_ok,
            "entry_hash_ok": hash_ok,
            "passed": ok,
        })
        if not ok:
            failures.append(f"Row id={row.get('id')}: {'prev_hash mismatch' if not prev_ok else 'entry_hash mismatch'}")

        expected_prev = stored  # advance chain pointer

    chain_intact = len(failures) == 0
    return {
        "check_name": "execution_ledger_chain_integrity",
        "passed": chain_intact,
        "chain_intact": chain_intact,
        "rows_checked": len(rows),
        "row_results": row_results,
        "detail": (
            f"All {len(rows)} entries verify correctly. Chain is intact."
            if chain_intact else
            "; ".join(failures[:3]) + (f" (+{len(failures)-3} more)" if len(failures) > 3 else "")
        ),
    }


def _check_post_exec_ledger_hashes(rows: list) -> dict:
    """
    Recompute ledger_hash for each post_execution_ledger row.

    Formula (spec Section 5.7):
        SHA-256(timestamp|approver|agent|executed_by|policy_result|
                parameters_hash|result_hash|prev_ledger_hash)
    """
    if not rows:
        return {"check_name": "post_exec_ledger_hash_integrity", "passed": True,
                "rows_checked": 0, "detail": "No entries."}

    expected_prev = "GENESIS"
    row_results   = []
    failures      = []

    for row in rows:
        seal = "|".join([
            row.get("timestamp", ""),
            row.get("approver", ""),
            row.get("agent", ""),
            row.get("executed_by", ""),
            row.get("policy_result", ""),
            row.get("parameters_hash", ""),
            row.get("result_hash", ""),
            expected_prev,
        ])
        computed = _sha256(seal)
        stored   = row.get("ledger_hash", "")
        ok       = computed == stored

        row_results.append({"row_id": row.get("id"), "passed": ok})
        if not ok:
            failures.append(f"Row id={row.get('id')}: ledger_hash mismatch")

        expected_prev = stored

    passed = len(failures) == 0
    return {
        "check_name": "post_exec_ledger_hash_integrity",
        "passed": passed,
        "rows_checked": len(rows),
        "row_results": row_results,
        "detail": (
            f"All {len(rows)} hash values verify correctly."
            if passed else "; ".join(failures[:3])
        ),
    }


def _check_post_exec_hmac(rows: list, service_token: str) -> dict:
    """
    Recompute HMAC-SHA256 signature for each post_execution_ledger row.

    Formula (spec Section 5.7):
        HMAC-SHA256(key=UTF-8(RIO_SERVICE_TOKEN), msg=UTF-8(ledger_hash))
    """
    if not rows:
        return {"check_name": "post_exec_hmac_signatures", "passed": True,
                "rows_checked": 0, "detail": "No entries."}

    if not service_token:
        return {"check_name": "post_exec_hmac_signatures", "passed": False,
                "rows_checked": 0,
                "detail": "No service token provided. Pass service_token= or set RIO_SERVICE_TOKEN env var."}

    row_results = []
    failures    = []

    for row in rows:
        stored = row.get("signature", "")
        if stored == "key_unavailable":
            row_results.append({"row_id": row.get("id"), "passed": False,
                                 "detail": "key_unavailable at write time"})
            failures.append(f"Row id={row.get('id')}: signature=key_unavailable")
            continue

        computed = _hmac_sha256(service_token, row.get("ledger_hash", ""))
        ok       = computed == stored
        row_results.append({"row_id": row.get("id"), "passed": ok})
        if not ok:
            failures.append(f"Row id={row.get('id')}: HMAC mismatch")

    passed = len(failures) == 0
    return {
        "check_name": "post_exec_hmac_signatures",
        "passed": passed,
        "rows_checked": len(rows),
        "row_results": row_results,
        "detail": (
            f"All {len(rows)} HMAC signatures verify correctly."
            if passed else "; ".join(failures[:3])
        ),
    }


# ── Public API ────────────────────────────────────────────────────────────────

def verify_receipt(
    receipt_path: Union[str, Path, dict],
    ledger_path: Union[str, Path, dict],
    service_token: str = None,
) -> dict:
    """
    Verify a RIO receipt against a ledger.

    Runs four checks:
      1. Receipt hash integrity (in-memory ledger hash)
      2. Execution ledger chain integrity
      3. Post-execution ledger hash integrity
      4. Post-execution ledger HMAC signatures

    Args:
        receipt_path:   Path to a receipt JSON file, or a pre-loaded dict.
        ledger_path:    Path to a ledger JSON file, or a pre-loaded dict.
        service_token:  RIO_SERVICE_TOKEN for HMAC verification.
                        Falls back to RIO_SERVICE_TOKEN env var, then
                        the demo_service_token field in the ledger file.

    Returns:
        dict with keys:
            overall         "PASS" or "FAIL"
            checks_passed   int
            checks_failed   int
            checks          list of per-check result dicts
    """
    receipt = _load_json(receipt_path)
    ledger  = _load_json(ledger_path)
    token   = _resolve_token(service_token, ledger)

    exec_rows      = ledger.get("execution_ledger", [])
    post_exec_rows = ledger.get("post_execution_ledger", [])

    checks = [
        _check_receipt_hash(receipt),
        _check_execution_ledger_chain(exec_rows),
        _check_post_exec_ledger_hashes(post_exec_rows),
        _check_post_exec_hmac(post_exec_rows, token),
    ]

    n_pass = sum(1 for c in checks if c["passed"])
    n_fail = len(checks) - n_pass

    return {
        "overall":       "PASS" if n_fail == 0 else "FAIL",
        "checks_passed": n_pass,
        "checks_failed": n_fail,
        "checks":        checks,
    }


def verify_ledger(
    ledger_path: Union[str, Path, dict],
    service_token: str = None,
) -> dict:
    """
    Verify only the ledger (without a receipt file).

    Runs three checks:
      1. Execution ledger chain integrity
      2. Post-execution ledger hash integrity
      3. Post-execution ledger HMAC signatures

    Args:
        ledger_path:    Path to a ledger JSON file, or a pre-loaded dict.
        service_token:  RIO_SERVICE_TOKEN for HMAC verification.

    Returns:
        dict with keys: overall, checks_passed, checks_failed, checks
    """
    ledger = _load_json(ledger_path)
    token  = _resolve_token(service_token, ledger)

    exec_rows      = ledger.get("execution_ledger", [])
    post_exec_rows = ledger.get("post_execution_ledger", [])

    checks = [
        _check_execution_ledger_chain(exec_rows),
        _check_post_exec_ledger_hashes(post_exec_rows),
        _check_post_exec_hmac(post_exec_rows, token),
    ]

    n_pass = sum(1 for c in checks if c["passed"])
    n_fail = len(checks) - n_pass

    return {
        "overall":       "PASS" if n_fail == 0 else "FAIL",
        "checks_passed": n_pass,
        "checks_failed": n_fail,
        "checks":        checks,
    }
