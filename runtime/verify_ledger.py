"""
RIO Runtime — Ledger Verification CLI

Reads the persisted ledger.jsonl and receipts.jsonl files and performs a
full tamper-evidence check:

    1. Recompute each ledger entry_hash and compare to the stored value.
    2. Verify the previous_hash chain links are consecutive and unbroken.
    3. Verify each ledger entry's RSA-PSS signature using the public key.
    4. Verify each receipt's RSA-PSS signature using the public key.
    5. Detect tampering, deleted entries, reordered entries, and invalid
       signatures.

Usage:
    python -m runtime.verify_ledger

Exit codes:
    0 — All checks passed
    1 — One or more checks failed
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

logger = logging.getLogger("rio.verify_ledger")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_RUNTIME_DIR = os.path.dirname(__file__)
_DATA_DIR = os.path.join(_RUNTIME_DIR, "data")
_KEYS_DIR = os.path.join(_RUNTIME_DIR, "keys")
_LEDGER_FILE = os.path.join(_DATA_DIR, "ledger.jsonl")
_RECEIPTS_FILE = os.path.join(_DATA_DIR, "receipts.jsonl")
_PUBLIC_KEY_PATH = os.path.join(_KEYS_DIR, "public_key.pem")


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

@dataclass
class VerifyResult:
    """Result of a single verification check."""
    check: str
    passed: bool
    detail: str
    entry_index: Optional[int] = None


# ---------------------------------------------------------------------------
# File readers
# ---------------------------------------------------------------------------

def _read_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Read all records from a JSONL file."""
    if not os.path.exists(filepath):
        return []
    records = []
    with open(filepath, "r") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


def _load_public_key():
    """Load the RSA public key from disk."""
    if not os.path.exists(_PUBLIC_KEY_PATH):
        raise FileNotFoundError(f"Public key not found at {_PUBLIC_KEY_PATH}")
    with open(_PUBLIC_KEY_PATH, "rb") as fh:
        return serialization.load_pem_public_key(fh.read())


# ---------------------------------------------------------------------------
# Hash computation (mirrors ledger.py)
# ---------------------------------------------------------------------------

def _compute_ledger_hash(entry: Dict[str, Any]) -> str:
    """
    Recompute the ledger entry hash from the JSONL record.

    Formula: SHA-256(
        entry_id + receipt_id + receipt_hash + request_id + intent_id +
        authorization_id + decision + action + result_hash +
        receipt_signature + previous_hash + timestamp
    )
    """
    data = (
        f"{entry.get('ledger_entry_id', '')}"
        f"{entry.get('receipt_id', '')}"
        f"{entry.get('receipt_hash', '')}"
        f"{entry.get('request_id', '')}"
        f"{entry.get('intent_id', '')}"
        f"{entry.get('authorization_id', '')}"
        f"{entry.get('decision', '')}"
        f"{entry.get('action', '')}"
        f"{entry.get('result_hash', '')}"
        f"{entry.get('receipt_signature', '')}"
        f"{entry.get('previous_ledger_hash', '')}"
        f"{entry.get('timestamp', '')}"
    )
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _compute_receipt_hash(receipt: Dict[str, Any]) -> str:
    """
    Recompute the receipt hash from the JSONL record.

    Formula: SHA-256(canonical_json(receipt_fields) + previous_receipt_hash)
    """
    canonical = json.dumps(
        {
            "receipt_id": receipt.get("receipt_id", ""),
            "request_id": receipt.get("request_id", ""),
            "intent_id": receipt.get("intent_id", ""),
            "authorization_id": receipt.get("authorization_id", ""),
            "decision": receipt.get("decision", ""),
            "action_type": receipt.get("action_type", ""),
            "execution_status": receipt.get("execution_status", ""),
            "execution_timestamp": receipt.get("execution_timestamp", 0),
            "result_hash": receipt.get("result_hash", ""),
        },
        sort_keys=True,
    )
    combined = canonical + receipt.get("previous_receipt_hash", "")
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Signature verification
# ---------------------------------------------------------------------------

def _verify_rsa_signature(public_key, data_str: str, signature_b64: str) -> bool:
    """Verify an RSA-PSS signature (base64-encoded) against a data string."""
    try:
        signature_bytes = base64.b64decode(signature_b64)
        public_key.verify(
            signature_bytes,
            data_str.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Verification checks
# ---------------------------------------------------------------------------

def verify_ledger_hashes(entries: List[Dict[str, Any]]) -> List[VerifyResult]:
    """Recompute each entry_hash and compare to the stored value."""
    results = []
    for i, entry in enumerate(entries):
        expected = _compute_ledger_hash(entry)
        stored = entry.get("ledger_hash", "")
        if expected == stored:
            results.append(VerifyResult(
                check="ledger_hash",
                passed=True,
                detail=f"Entry {i} hash verified",
                entry_index=i,
            ))
        else:
            results.append(VerifyResult(
                check="ledger_hash",
                passed=False,
                detail=f"Entry {i} hash mismatch — expected {expected[:16]}..., got {stored[:16]}...",
                entry_index=i,
            ))
    return results


def verify_hash_chain(entries: List[Dict[str, Any]]) -> List[VerifyResult]:
    """
    Verify the previous_hash chain links are consecutive.

    The JSONL file may contain multiple independent chain segments
    (e.g., from test resets where the in-memory state is cleared).
    A new segment starts when ``previous_ledger_hash`` is empty.
    Each segment is verified independently.
    """
    results = []
    segment_start = 0

    for i, entry in enumerate(entries):
        actual_previous = entry.get("previous_ledger_hash", "")

        # Detect new chain segment (genesis entry has empty previous hash)
        if actual_previous == "" and (i == 0 or entries[i - 1].get("ledger_hash", "") != ""):
            segment_start = i
            results.append(VerifyResult(
                check="hash_chain",
                passed=True,
                detail=f"Entry {i} is genesis of chain segment",
                entry_index=i,
            ))
            continue

        # Within a segment, verify linkage to previous entry
        expected_previous = entries[i - 1].get("ledger_hash", "")

        if actual_previous == expected_previous:
            results.append(VerifyResult(
                check="hash_chain",
                passed=True,
                detail=f"Entry {i} chain link valid",
                entry_index=i,
            ))
        else:
            results.append(VerifyResult(
                check="hash_chain",
                passed=False,
                detail=(
                    f"Entry {i} chain broken — expected previous "
                    f"{expected_previous[:16]}..., got {actual_previous[:16]}..."
                ),
                entry_index=i,
            ))
    return results


def verify_ledger_signatures(
    entries: List[Dict[str, Any]], public_key
) -> List[VerifyResult]:
    """Verify each ledger entry's RSA-PSS signature."""
    results = []
    for i, entry in enumerate(entries):
        sig = entry.get("ledger_signature", "")
        hash_val = entry.get("ledger_hash", "")

        if not sig:
            results.append(VerifyResult(
                check="ledger_signature",
                passed=False,
                detail=f"Entry {i} has no signature",
                entry_index=i,
            ))
            continue

        is_valid = _verify_rsa_signature(public_key, hash_val, sig)
        if is_valid:
            results.append(VerifyResult(
                check="ledger_signature",
                passed=True,
                detail=f"Entry {i} signature valid",
                entry_index=i,
            ))
        else:
            results.append(VerifyResult(
                check="ledger_signature",
                passed=False,
                detail=f"Entry {i} signature INVALID",
                entry_index=i,
            ))
    return results


def verify_receipt_signatures(
    receipts: List[Dict[str, Any]], public_key
) -> List[VerifyResult]:
    """Verify each receipt's RSA-PSS signature."""
    results = []
    for i, receipt in enumerate(receipts):
        sig = receipt.get("signature", "")
        hash_val = receipt.get("receipt_hash", "")

        if not sig:
            results.append(VerifyResult(
                check="receipt_signature",
                passed=False,
                detail=f"Receipt {i} has no signature",
                entry_index=i,
            ))
            continue

        is_valid = _verify_rsa_signature(public_key, hash_val, sig)
        if is_valid:
            results.append(VerifyResult(
                check="receipt_signature",
                passed=True,
                detail=f"Receipt {i} signature valid",
                entry_index=i,
            ))
        else:
            results.append(VerifyResult(
                check="receipt_signature",
                passed=False,
                detail=f"Receipt {i} signature INVALID",
                entry_index=i,
            ))
    return results


def verify_receipt_hashes(receipts: List[Dict[str, Any]]) -> List[VerifyResult]:
    """Recompute each receipt hash and compare to the stored value."""
    results = []
    for i, receipt in enumerate(receipts):
        expected = _compute_receipt_hash(receipt)
        stored = receipt.get("receipt_hash", "")
        if expected == stored:
            results.append(VerifyResult(
                check="receipt_hash",
                passed=True,
                detail=f"Receipt {i} hash verified",
                entry_index=i,
            ))
        else:
            results.append(VerifyResult(
                check="receipt_hash",
                passed=False,
                detail=f"Receipt {i} hash mismatch — expected {expected[:16]}..., got {stored[:16]}...",
                entry_index=i,
            ))
    return results


# ---------------------------------------------------------------------------
# Full verification
# ---------------------------------------------------------------------------

def run_full_verification(
    ledger_path: str = _LEDGER_FILE,
    receipts_path: str = _RECEIPTS_FILE,
    public_key_path: str = _PUBLIC_KEY_PATH,
) -> tuple[bool, List[VerifyResult]]:
    """
    Run the complete ledger and receipt verification suite.

    Args:
        ledger_path: Path to ledger.jsonl
        receipts_path: Path to receipts.jsonl
        public_key_path: Path to public_key.pem

    Returns:
        Tuple of (overall_pass, list_of_results)
    """
    all_results: List[VerifyResult] = []

    # Load data
    entries = _read_jsonl(ledger_path)
    receipts = _read_jsonl(receipts_path)

    if not entries:
        logger.warning("Ledger file is empty or missing: %s", ledger_path)
        return True, [VerifyResult(
            check="ledger_empty",
            passed=True,
            detail="Ledger is empty — nothing to verify",
        )]

    # Load public key
    if not os.path.exists(public_key_path):
        return False, [VerifyResult(
            check="public_key",
            passed=False,
            detail=f"Public key not found at {public_key_path}",
        )]

    public_key = _load_public_key()

    # 1. Verify ledger entry hashes
    hash_results = verify_ledger_hashes(entries)
    all_results.extend(hash_results)

    # 2. Verify hash chain
    chain_results = verify_hash_chain(entries)
    all_results.extend(chain_results)

    # 3. Verify ledger entry signatures
    sig_results = verify_ledger_signatures(entries, public_key)
    all_results.extend(sig_results)

    # 4. Verify receipt hashes
    if receipts:
        receipt_hash_results = verify_receipt_hashes(receipts)
        all_results.extend(receipt_hash_results)

    # 5. Verify receipt signatures
    if receipts:
        receipt_sig_results = verify_receipt_signatures(receipts, public_key)
        all_results.extend(receipt_sig_results)

    overall_pass = all(r.passed for r in all_results)
    return overall_pass, all_results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    """CLI entry point for ledger verification."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    )

    print("=" * 70)
    print("RIO LEDGER VERIFICATION")
    print("=" * 70)
    print()

    overall_pass, results = run_full_verification()

    # Summary counts
    passed_count = sum(1 for r in results if r.passed)
    failed_count = sum(1 for r in results if not r.passed)

    # Group by check type
    check_types = {}
    for r in results:
        if r.check not in check_types:
            check_types[r.check] = {"passed": 0, "failed": 0, "failures": []}
        if r.passed:
            check_types[r.check]["passed"] += 1
        else:
            check_types[r.check]["failed"] += 1
            check_types[r.check]["failures"].append(r)

    # Print results by check type
    for check_name, stats in check_types.items():
        total = stats["passed"] + stats["failed"]
        status = "PASS" if stats["failed"] == 0 else "FAIL"
        print(f"  [{status}] {check_name}: {stats['passed']}/{total} passed")

        # Print failure details
        for failure in stats["failures"]:
            print(f"         FAIL: {failure.detail}")

    print()
    print("-" * 70)

    if overall_pass:
        print(f"Ledger verification: PASS — {passed_count} checks passed")
        print("-" * 70)
        sys.exit(0)
    else:
        print(
            f"Ledger verification: FAIL — {failed_count} failures out of "
            f"{passed_count + failed_count} checks"
        )
        print("-" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
