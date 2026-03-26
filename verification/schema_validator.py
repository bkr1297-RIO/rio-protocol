"""
Schema validation for RIO receipts and ledger entries.

Validates structural requirements before cryptographic checks.
"""

import re
from typing import Optional

from verification.models import (
    ALL_REQUIRED_FIELDS,
    VALID_DECISIONS,
    VALID_SIGNATURE_ALGORITHMS,
)

# 64-char lowercase hex pattern for SHA-256 digests
HEX_64_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def is_valid_hex_64(value: str) -> bool:
    """Check if a string is a valid 64-character lowercase hex digest."""
    return isinstance(value, str) and bool(HEX_64_PATTERN.match(value))


def validate_receipt_schema(receipt: dict) -> list[str]:
    """
    Validate that a receipt has all required fields with correct types.

    Returns a list of error messages. Empty list means valid.
    """
    errors = []

    # Check all 22 required fields are present
    missing = [f for f in ALL_REQUIRED_FIELDS if f not in receipt]
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    # If fields are missing, skip type checks for those fields
    present = {f for f in ALL_REQUIRED_FIELDS if f in receipt}

    # String fields
    string_fields = [
        "receipt_version", "receipt_id", "timestamp", "runtime_id",
        "runtime_version", "environment", "request_summary",
        "request_hash", "policy_bundle_id", "policy_bundle_hash",
        "decision", "model_output_hash", "model_output_preview",
        "prev_ledger_hash", "public_key_fingerprint",
        "receipt_hash", "signature_algorithm", "signature",
    ]
    for f in string_fields:
        if f in present and not isinstance(receipt[f], str):
            errors.append(f"Field '{f}' must be a string, got {type(receipt[f]).__name__}")

    # Dict fields
    dict_fields = [
        "request_canonical_payload", "invariant_results", "threshold_results",
    ]
    for f in dict_fields:
        if f in present and not isinstance(receipt[f], dict):
            errors.append(f"Field '{f}' must be an object, got {type(receipt[f]).__name__}")

    # List fields
    if "decision_reason_codes" in present and not isinstance(receipt["decision_reason_codes"], list):
        errors.append(
            f"Field 'decision_reason_codes' must be an array, "
            f"got {type(receipt['decision_reason_codes']).__name__}"
        )

    # Hex digest fields
    hex_fields = [
        "request_hash", "policy_bundle_hash", "model_output_hash",
        "prev_ledger_hash", "public_key_fingerprint", "receipt_hash",
    ]
    for f in hex_fields:
        if f in present and isinstance(receipt[f], str) and not is_valid_hex_64(receipt[f]):
            errors.append(f"Field '{f}' is not a valid 64-char hex digest")

    # Decision validation
    if "decision" in present and isinstance(receipt["decision"], str):
        if receipt["decision"] not in VALID_DECISIONS:
            errors.append(
                f"Field 'decision' value '{receipt['decision']}' "
                f"not in valid set: {sorted(VALID_DECISIONS)}"
            )

    # Signature algorithm validation
    if "signature_algorithm" in present and isinstance(receipt["signature_algorithm"], str):
        if receipt["signature_algorithm"] not in VALID_SIGNATURE_ALGORITHMS:
            errors.append(
                f"Field 'signature_algorithm' value '{receipt['signature_algorithm']}' "
                f"not in valid set: {sorted(VALID_SIGNATURE_ALGORITHMS)}"
            )

    return errors


def validate_ledger_entry_schema(entry: dict) -> list[str]:
    """
    Validate that a ledger entry has all required fields.

    Returns a list of error messages. Empty list means valid.
    """
    errors = []
    required = [
        "chain_index", "receipt_id", "receipt_hash",
        "prev_ledger_hash", "current_ledger_hash", "timestamp",
    ]

    missing = [f for f in required if f not in entry]
    if missing:
        errors.append(f"Missing required fields: {', '.join(missing)}")

    # Type checks
    if "chain_index" in entry and not isinstance(entry["chain_index"], int):
        errors.append(f"Field 'chain_index' must be an integer")

    hex_fields = ["receipt_hash", "prev_ledger_hash", "current_ledger_hash"]
    for f in hex_fields:
        if f in entry and isinstance(entry[f], str) and not is_valid_hex_64(entry[f]):
            errors.append(f"Field '{f}' is not a valid 64-char hex digest")

    return errors
