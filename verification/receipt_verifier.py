"""
RIO Receipt Verifier — 7 independent verification checks.

Checks are always run in full (all 7), even if early checks fail,
so the caller gets the complete picture.

Check 1: required_fields  — All 22 required fields present with correct types
Check 2: request_hash     — Recompute request_hash and compare
Check 3: receipt_hash     — Recompute receipt_hash from 19 signed fields
Check 4: signature        — Verify Ed25519 signature over signing payload
Check 5: public_key_fingerprint — SHA256 of raw key bytes matches stored value
Check 6: decision_valid   — Decision is one of the 4 valid protocol values
Check 7: ledger_link      — prev_ledger_hash is a well-formed 64-char hex digest
"""

import json
from typing import Optional

from verification.models import (
    SIGNED_FIELDS_19,
    VALID_DECISIONS,
    CheckResult,
    ReceiptVerificationResult,
)
from verification.hash_utils import (
    canonical_json,
    compute_receipt_hash,
    compute_request_hash,
    compute_public_key_fingerprint,
)
from verification.crypto_utils import (
    load_public_key,
    get_raw_public_key_bytes,
    verify_signature,
)
from verification.schema_validator import (
    validate_receipt_schema,
    is_valid_hex_64,
)


def _unwrap_receipt(data: dict) -> dict:
    """
    Accept JSON input as either a raw receipt dict
    OR a vector-wrapped {'receipt': {...}} dict.
    """
    if "receipt" in data and isinstance(data["receipt"], dict):
        return data["receipt"]
    return data


def verify_receipt(
    receipt_data: dict,
    public_key_pem: str,
) -> ReceiptVerificationResult:
    """
    Run all 7 verification checks on a RIO receipt.

    Args:
        receipt_data: Receipt dict (or vector-wrapped {'receipt': {...}})
        public_key_pem: PEM-encoded Ed25519 public key text

    Returns:
        ReceiptVerificationResult with all_passed flag and per-check details.
    """
    receipt = _unwrap_receipt(receipt_data)
    receipt_id = receipt.get("receipt_id", "<unknown>")
    checks: list[CheckResult] = []

    # ── Check 1: Required Fields ────────────────────────────────────────
    schema_errors = validate_receipt_schema(receipt)
    checks.append(CheckResult(
        check_name="required_fields",
        number=1,
        passed=len(schema_errors) == 0,
        details="" if not schema_errors else "; ".join(schema_errors),
    ))

    # ── Check 2: Request Hash ───────────────────────────────────────────
    try:
        if "request_canonical_payload" in receipt and "request_hash" in receipt:
            expected = compute_request_hash(receipt["request_canonical_payload"])
            actual = receipt["request_hash"]
            passed = expected == actual
            details = "" if passed else f"request_hash mismatch: expected {expected}, got {actual}"
        else:
            passed = False
            details = "Missing request_canonical_payload or request_hash field"
    except Exception as e:
        passed = False
        details = f"Error computing request_hash: {e}"
    checks.append(CheckResult(check_name="request_hash", number=2, passed=passed, details=details))

    # ── Check 3: Receipt Hash ───────────────────────────────────────────
    try:
        # Only attempt if all 19 signed fields are present
        missing_signed = [f for f in SIGNED_FIELDS_19 if f not in receipt]
        if not missing_signed and "receipt_hash" in receipt:
            expected = compute_receipt_hash(receipt)
            actual = receipt["receipt_hash"]
            passed = expected == actual
            details = "" if passed else f"receipt_hash mismatch: expected {expected}, got {actual}"
        else:
            passed = False
            missing_all = missing_signed + (["receipt_hash"] if "receipt_hash" not in receipt else [])
            details = f"Missing fields needed for receipt_hash: {', '.join(missing_all)}"
    except Exception as e:
        passed = False
        details = f"Error computing receipt_hash: {e}"
    checks.append(CheckResult(check_name="receipt_hash", number=3, passed=passed, details=details))

    # ── Check 4: Signature ──────────────────────────────────────────────
    try:
        missing_signed = [f for f in SIGNED_FIELDS_19 if f not in receipt]
        if not missing_signed and "signature" in receipt:
            pub_key = load_public_key(public_key_pem)
            signing_payload = {k: receipt[k] for k in SIGNED_FIELDS_19}
            message_bytes = canonical_json(signing_payload)
            passed = verify_signature(pub_key, message_bytes, receipt["signature"])
            details = "" if passed else "Ed25519 signature is INVALID"
        else:
            passed = False
            details = "Missing fields needed for signature verification"
    except ValueError as e:
        passed = False
        details = f"Public key error: {e}"
    except Exception as e:
        passed = False
        details = f"Error verifying signature: {e}"
    checks.append(CheckResult(check_name="signature", number=4, passed=passed, details=details))

    # ── Check 5: Public Key Fingerprint ─────────────────────────────────
    try:
        if "public_key_fingerprint" in receipt:
            pub_key = load_public_key(public_key_pem)
            raw_bytes = get_raw_public_key_bytes(pub_key)
            expected = compute_public_key_fingerprint(raw_bytes)
            actual = receipt["public_key_fingerprint"]
            passed = expected == actual
            details = "" if passed else f"public_key_fingerprint mismatch: expected {expected}, got {actual}"
        else:
            passed = False
            details = "Missing public_key_fingerprint field"
    except ValueError as e:
        passed = False
        details = f"Public key error: {e}"
    except Exception as e:
        passed = False
        details = f"Error computing fingerprint: {e}"
    checks.append(CheckResult(
        check_name="public_key_fingerprint", number=5, passed=passed, details=details,
    ))

    # ── Check 6: Decision Valid ─────────────────────────────────────────
    if "decision" in receipt:
        value = receipt["decision"]
        passed = value in VALID_DECISIONS
        details = "" if passed else f"decision '{value}' not in valid set"
    else:
        passed = False
        details = "Missing decision field"
    checks.append(CheckResult(check_name="decision_valid", number=6, passed=passed, details=details))

    # ── Check 7: Ledger Link ────────────────────────────────────────────
    if "prev_ledger_hash" in receipt:
        passed = is_valid_hex_64(receipt["prev_ledger_hash"])
        details = "" if passed else "prev_ledger_hash is not a valid 64-char hex digest"
    else:
        passed = False
        details = "Missing prev_ledger_hash field"
    checks.append(CheckResult(check_name="ledger_link", number=7, passed=passed, details=details))

    # ── Aggregate ───────────────────────────────────────────────────────
    all_passed = all(c.passed for c in checks)

    return ReceiptVerificationResult(
        receipt_id=receipt_id,
        all_passed=all_passed,
        checks=checks,
    )


def verify_receipt_from_file(
    receipt_path: str,
    public_key_path: str,
) -> ReceiptVerificationResult:
    """
    Convenience: load receipt JSON and PEM key from file paths,
    then run verify_receipt.
    """
    with open(receipt_path, "r") as f:
        receipt_data = json.load(f)
    with open(public_key_path, "r") as f:
        public_key_pem = f.read()
    return verify_receipt(receipt_data, public_key_pem)
