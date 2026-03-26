"""
RIO Runtime — Governed Execution Protocol v2: Receipt Verifier

Provides independent verification of v2 receipts:

  1. Receipt hash integrity — recompute and compare receipt_hash
  2. Intent hash integrity — recompute and compare intent_hash
  3. Action hash integrity — recompute and compare action_hash
  4. Verification hash integrity — recompute and compare verification_hash
  5. Signature verification — RSA-PSS signature over critical fields
  6. Chain linkage — verify previous_hash matches prior receipt

All verification functions return a VerificationCheck dataclass with
pass/fail status and details.

Spec reference: /spec/receipt_protocol.md
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .receipt_generator import (
    ReceiptV2,
    compute_action_hash,
    compute_intent_hash,
    compute_receipt_hash,
    compute_verification_hash,
)
from .receipt_signer import get_signing_payload

logger = logging.getLogger("rio.receipts.verifier")

# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

_KEYS_DIR = os.path.join(os.path.dirname(__file__), "..", "keys")
_PUBLIC_KEY_PATH = os.path.join(_KEYS_DIR, "public_key.pem")

_public_key = None


def _load_public_key():
    """Load the RSA public key from disk (lazy, cached)."""
    global _public_key
    if _public_key is not None:
        return _public_key
    with open(_PUBLIC_KEY_PATH, "rb") as fh:
        _public_key = serialization.load_pem_public_key(fh.read())
    return _public_key


# ---------------------------------------------------------------------------
# Verification result
# ---------------------------------------------------------------------------

@dataclass
class VerificationCheck:
    """Result of a single verification check."""
    check_name: str
    passed: bool
    details: str


# ---------------------------------------------------------------------------
# Individual verification checks
# ---------------------------------------------------------------------------

def verify_receipt_hash(receipt: ReceiptV2) -> VerificationCheck:
    """Verify the receipt hash by recomputing it from receipt fields."""
    expected = compute_receipt_hash(receipt)
    passed = receipt.receipt_hash == expected
    return VerificationCheck(
        check_name="receipt_hash",
        passed=passed,
        details=(
            f"Receipt {receipt.receipt_id} hash {'verified' if passed else 'MISMATCH'}"
            + ("" if passed else f" — expected {expected[:16]}..., got {receipt.receipt_hash[:16]}...")
        ),
    )


def verify_intent_hash(
    receipt: ReceiptV2,
    intent_data: dict[str, Any],
) -> VerificationCheck:
    """Verify the intent hash matches the original intent data."""
    expected = compute_intent_hash(intent_data)
    passed = receipt.intent_hash == expected
    return VerificationCheck(
        check_name="intent_hash",
        passed=passed,
        details=(
            f"Receipt {receipt.receipt_id} intent hash {'verified' if passed else 'MISMATCH'}"
            + ("" if passed else f" — expected {expected[:16]}..., got {receipt.intent_hash[:16]}...")
        ),
    )


def verify_action_hash(
    receipt: ReceiptV2,
    execution_payload: dict[str, Any],
) -> VerificationCheck:
    """Verify the action hash matches the execution payload."""
    expected = compute_action_hash(execution_payload)
    passed = receipt.action_hash == expected
    return VerificationCheck(
        check_name="action_hash",
        passed=passed,
        details=(
            f"Receipt {receipt.receipt_id} action hash {'verified' if passed else 'MISMATCH'}"
            + ("" if passed else f" — expected {expected[:16]}..., got {receipt.action_hash[:16]}...")
        ),
    )


def verify_verification_hash(
    receipt: ReceiptV2,
    verification_result: dict[str, Any],
) -> VerificationCheck:
    """Verify the verification hash matches the verification result."""
    expected = compute_verification_hash(verification_result)
    passed = receipt.verification_hash == expected
    return VerificationCheck(
        check_name="verification_hash",
        passed=passed,
        details=(
            f"Receipt {receipt.receipt_id} verification hash {'verified' if passed else 'MISMATCH'}"
            + ("" if passed else f" — expected {expected[:16]}..., got {receipt.verification_hash[:16]}...")
        ),
    )


def verify_signature(receipt: ReceiptV2) -> VerificationCheck:
    """Verify the RSA-PSS signature on a v2 receipt."""
    if not receipt.signature:
        return VerificationCheck(
            check_name="signature",
            passed=False,
            details=f"Receipt {receipt.receipt_id} has no signature",
        )

    public_key = _load_public_key()
    payload = get_signing_payload(receipt)

    try:
        signature_bytes = base64.b64decode(receipt.signature)
        public_key.verify(
            signature_bytes,
            payload.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return VerificationCheck(
            check_name="signature",
            passed=True,
            details=f"Receipt {receipt.receipt_id} RSA-PSS signature valid",
        )
    except Exception as e:
        return VerificationCheck(
            check_name="signature",
            passed=False,
            details=f"Receipt {receipt.receipt_id} RSA-PSS signature INVALID: {e}",
        )


def verify_chain_link(
    receipt: ReceiptV2,
    previous_receipt: Optional[ReceiptV2],
) -> VerificationCheck:
    """Verify the previous_hash links to the prior receipt."""
    if previous_receipt is None:
        # Genesis receipt — previous_hash should be empty
        passed = receipt.previous_hash == ""
        return VerificationCheck(
            check_name="chain_link",
            passed=passed,
            details=(
                f"Receipt {receipt.receipt_id} genesis link {'verified' if passed else 'INVALID — expected empty previous_hash'}"
            ),
        )

    passed = receipt.previous_hash == previous_receipt.receipt_hash
    return VerificationCheck(
        check_name="chain_link",
        passed=passed,
        details=(
            f"Receipt {receipt.receipt_id} chain link {'verified' if passed else 'BROKEN'}"
            + ("" if passed else f" — expected {previous_receipt.receipt_hash[:16]}..., got {receipt.previous_hash[:16]}...")
        ),
    )


def verify_required_fields(receipt: ReceiptV2) -> VerificationCheck:
    """Verify that all required v2 receipt fields are present."""
    missing = []
    required = [
        "receipt_id", "intent_id", "intent_hash", "action", "decision",
        "timestamp_request", "receipt_hash",
    ]
    for field_name in required:
        val = getattr(receipt, field_name, "")
        if not val:
            missing.append(field_name)

    if missing:
        return VerificationCheck(
            check_name="required_fields",
            passed=False,
            details=f"Receipt {receipt.receipt_id} missing fields: {', '.join(missing)}",
        )
    return VerificationCheck(
        check_name="required_fields",
        passed=True,
        details=f"Receipt {receipt.receipt_id} all required fields present",
    )


# ---------------------------------------------------------------------------
# Full verification
# ---------------------------------------------------------------------------

def verify_receipt_full(
    receipt: ReceiptV2,
    intent_data: Optional[dict[str, Any]] = None,
    execution_payload: Optional[dict[str, Any]] = None,
    verification_result: Optional[dict[str, Any]] = None,
    previous_receipt: Optional[ReceiptV2] = None,
) -> list[VerificationCheck]:
    """
    Run all verification checks on a v2 receipt.

    Args:
        receipt: The ReceiptV2 to verify.
        intent_data: Original intent data for intent_hash verification.
        execution_payload: Original execution payload for action_hash verification.
        verification_result: Original verification result for verification_hash check.
        previous_receipt: The prior receipt for chain link verification.

    Returns:
        A list of VerificationCheck results.
    """
    checks: list[VerificationCheck] = []

    # Always run these
    checks.append(verify_required_fields(receipt))
    checks.append(verify_receipt_hash(receipt))
    checks.append(verify_signature(receipt))

    # Conditional checks
    if intent_data is not None:
        checks.append(verify_intent_hash(receipt, intent_data))

    if execution_payload is not None:
        checks.append(verify_action_hash(receipt, execution_payload))

    if verification_result is not None:
        checks.append(verify_verification_hash(receipt, verification_result))

    checks.append(verify_chain_link(receipt, previous_receipt))

    passed = sum(1 for c in checks if c.passed)
    total = len(checks)

    logger.info(
        "v2 Receipt verification for %s: %d/%d checks passed",
        receipt.receipt_id,
        passed,
        total,
    )

    return checks
