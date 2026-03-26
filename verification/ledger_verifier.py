"""
RIO Ledger Chain Verifier — 4 independent verification checks.

Check 1: entry_hash   — Recompute current_ledger_hash for every entry
Check 2: genesis_link — First entry's prev_ledger_hash must equal GENESIS_HASH
Check 3: chain_link   — Each entry's prev_ledger_hash matches previous entry's current_ledger_hash
Check 4: full_chain   — Aggregate: chain_intact = (checks 1-3 pass for all entries)
"""

import json
from typing import Union

from verification.models import (
    GENESIS_HASH,
    LedgerFailure,
    LedgerVerificationResult,
)
from verification.hash_utils import compute_ledger_chain_hash
from verification.schema_validator import validate_ledger_entry_schema


def _extract_chain(data: Union[dict, list]) -> list[dict]:
    """
    Extract ordered ledger entries from various input formats.

    Accepts:
    - A JSON array of entry dicts
    - An object with a 'chain' key containing an array
    - An object with a 'chain' key containing named entries (entry_0, entry_1, ...)
    - Entries may be wrapped in {'ledger_entry': {...}}
    """
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict):
        if "chain" in data:
            chain_val = data["chain"]
            if isinstance(chain_val, list):
                entries = chain_val
            elif isinstance(chain_val, dict):
                # Named entries: extract entry_N keys, skip metadata keys
                entry_items = []
                for k, v in chain_val.items():
                    if isinstance(v, dict):
                        entry_items.append((k, v))
                # Sort by chain_index if available, else by key name
                entry_items.sort(key=lambda x: x[1].get("chain_index", 0) if isinstance(x[1], dict) else 0)
                entries = [v for _, v in entry_items]
            else:
                entries = []
        else:
            entries = []
    else:
        entries = []

    # Unwrap {'ledger_entry': {...}} wrappers
    unwrapped = []
    for entry in entries:
        if isinstance(entry, dict) and "ledger_entry" in entry:
            unwrapped.append(entry["ledger_entry"])
        elif isinstance(entry, dict):
            unwrapped.append(entry)

    return unwrapped


def verify_ledger(chain: Union[list[dict], dict]) -> LedgerVerificationResult:
    """
    Run all 4 verification checks on a RIO ledger chain.

    Args:
        chain: Ledger chain data (list of entries, or dict with 'chain' key)

    Returns:
        LedgerVerificationResult with chain_intact flag and per-entry details.
    """
    entries = _extract_chain(chain)
    total = len(entries)
    failures: list[LedgerFailure] = []

    if total == 0:
        return LedgerVerificationResult(
            chain_intact=False,
            entries_verified=0,
            entries_total=0,
            failures=[LedgerFailure(
                entry_index=-1,
                check_name="full_chain",
                details="No ledger entries found in input",
            )],
            details="Empty chain",
        )

    # Validate schemas first
    for i, entry in enumerate(entries):
        schema_errors = validate_ledger_entry_schema(entry)
        if schema_errors:
            for err in schema_errors:
                failures.append(LedgerFailure(
                    entry_index=i,
                    check_name="schema",
                    details=err,
                ))

    # ── Check 1: Entry Hash ─────────────────────────────────────────────
    # Recompute current_ledger_hash for every entry
    for i, entry in enumerate(entries):
        if "prev_ledger_hash" not in entry or "receipt_hash" not in entry:
            continue  # Schema check already flagged this
        if "current_ledger_hash" not in entry:
            continue

        expected = compute_ledger_chain_hash(
            entry["prev_ledger_hash"],
            entry["receipt_hash"],
        )
        actual = entry["current_ledger_hash"]
        if expected != actual:
            failures.append(LedgerFailure(
                entry_index=i,
                check_name="entry_hash",
                details=f"current_ledger_hash mismatch at chain_index={entry.get('chain_index', i)}: "
                        f"expected {expected}, got {actual}",
            ))

    # ── Check 2: Genesis Link ───────────────────────────────────────────
    # First entry's prev_ledger_hash must equal GENESIS_HASH
    if entries and "prev_ledger_hash" in entries[0]:
        if entries[0]["prev_ledger_hash"] != GENESIS_HASH:
            failures.append(LedgerFailure(
                entry_index=0,
                check_name="genesis_link",
                details=f"First entry prev_ledger_hash {entries[0]['prev_ledger_hash']} "
                        f"!= GENESIS_HASH {GENESIS_HASH}",
            ))

    # ── Check 3: Chain Link ─────────────────────────────────────────────
    # Each entry's prev_ledger_hash matches previous entry's current_ledger_hash
    for i in range(1, total):
        prev_entry = entries[i - 1]
        curr_entry = entries[i]
        if "current_ledger_hash" not in prev_entry or "prev_ledger_hash" not in curr_entry:
            continue
        if curr_entry["prev_ledger_hash"] != prev_entry["current_ledger_hash"]:
            failures.append(LedgerFailure(
                entry_index=i,
                check_name="chain_link",
                details=f"chain_link broken at index {i}: "
                        f"prev={curr_entry['prev_ledger_hash']} "
                        f"!= previous.current={prev_entry['current_ledger_hash']}",
            ))

    # ── Check 4: Full Chain (aggregate) ─────────────────────────────────
    chain_intact = len(failures) == 0
    entries_verified = total if chain_intact else sum(
        1 for i in range(total)
        if not any(f.entry_index == i for f in failures)
    )

    details = "Chain intact" if chain_intact else f"{len(failures)} failure(s) detected"

    return LedgerVerificationResult(
        chain_intact=chain_intact,
        entries_verified=entries_verified,
        entries_total=total,
        failures=failures,
        details=details,
    )


def verify_ledger_from_file(ledger_path: str) -> LedgerVerificationResult:
    """
    Convenience: load ledger JSON from file path, then run verify_ledger.
    """
    with open(ledger_path, "r") as f:
        data = json.load(f)
    return verify_ledger(data)
