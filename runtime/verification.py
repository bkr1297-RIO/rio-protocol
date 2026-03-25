"""
RIO Runtime — Verification

Provides verification functions for receipts, ledger hash chain integrity,
and protocol invariant compliance. Used by auditors, continuous monitoring,
and the governance learning loop.

Spec reference: /spec/verification_model.md
Related invariants: INV-02, INV-03, INV-04
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Any

from .models import Authorization, Intent, LedgerEntry, Receipt
from . import ledger as ledger_module

logger = logging.getLogger("rio.verification")


@dataclass
class VerificationResult:
    """Result of a verification check."""
    check_name: str
    passed: bool
    details: str


def verify_receipt_signature(receipt: Receipt) -> VerificationResult:
    """
    Verify the cryptographic signature on a receipt.

    In a production implementation, this would verify the ECDSA-secp256k1
    signature against the system's public attestation key.

    Args:
        receipt: The receipt to verify.

    Returns:
        A VerificationResult indicating pass or fail.
    """
    if not receipt.signature:
        return VerificationResult(
            check_name="receipt_signature",
            passed=False,
            details=f"Receipt {receipt.receipt_id} has no signature",
        )

    # Placeholder verification — production would verify ECDSA signature
    expected_prefix = f"sig:{receipt.receipt_hash[:32]}"
    if receipt.signature == expected_prefix:
        return VerificationResult(
            check_name="receipt_signature",
            passed=True,
            details=f"Receipt {receipt.receipt_id} signature valid",
        )
    else:
        return VerificationResult(
            check_name="receipt_signature",
            passed=False,
            details=f"Receipt {receipt.receipt_id} signature mismatch",
        )


def verify_receipt_hash(receipt: Receipt) -> VerificationResult:
    """
    Verify the receipt hash by recomputing it from the receipt fields.

    Args:
        receipt: The receipt to verify.

    Returns:
        A VerificationResult indicating pass or fail.
    """
    canonical = json.dumps(
        {
            "receipt_id": receipt.receipt_id,
            "request_id": receipt.request_id,
            "intent_id": receipt.intent_id,
            "authorization_id": receipt.authorization_id,
            "decision": receipt.decision.value,
            "action_type": receipt.action_type,
            "execution_status": receipt.execution_status.value,
            "execution_timestamp": receipt.execution_timestamp,
            "result_hash": receipt.result_hash,
        },
        sort_keys=True,
    )
    combined = canonical + receipt.previous_receipt_hash
    expected_hash = hashlib.sha256(combined.encode("utf-8")).hexdigest()

    if receipt.receipt_hash == expected_hash:
        return VerificationResult(
            check_name="receipt_hash",
            passed=True,
            details=f"Receipt {receipt.receipt_id} hash verified",
        )
    else:
        return VerificationResult(
            check_name="receipt_hash",
            passed=False,
            details=(
                f"Receipt {receipt.receipt_id} hash mismatch: "
                f"expected {expected_hash}, got {receipt.receipt_hash}"
            ),
        )


def verify_ledger_chain() -> VerificationResult:
    """
    Verify the integrity of the entire audit ledger hash chain.

    Delegates to the ledger module's chain verification and wraps the
    result in a VerificationResult.

    Returns:
        A VerificationResult indicating pass or fail.
    """
    chain_valid = ledger_module.verify_chain()

    if chain_valid:
        entries = ledger_module.get_ledger()
        return VerificationResult(
            check_name="ledger_chain",
            passed=True,
            details=f"Ledger hash chain intact — {len(entries)} entries verified",
        )
    else:
        return VerificationResult(
            check_name="ledger_chain",
            passed=False,
            details="Ledger hash chain integrity check FAILED",
        )


def verify_completeness(
    intent: Intent,
    authorization: Authorization,
    receipt: Receipt,
    ledger_entry: LedgerEntry,
) -> VerificationResult:
    """
    Verify that all protocol stages produced their required artifacts (INV-01).

    Args:
        intent: The canonical intent.
        authorization: The authorization decision.
        receipt: The generated receipt.
        ledger_entry: The ledger entry.

    Returns:
        A VerificationResult indicating pass or fail.
    """
    missing: list[str] = []

    if not intent.intent_id:
        missing.append("intent_id")
    if not authorization.authorization_id:
        missing.append("authorization_id")
    if not receipt.receipt_id:
        missing.append("receipt_id")
    if not receipt.receipt_hash:
        missing.append("receipt_hash")
    if not receipt.signature:
        missing.append("receipt_signature")
    if not ledger_entry.ledger_entry_id:
        missing.append("ledger_entry_id")
    if not ledger_entry.ledger_hash:
        missing.append("ledger_hash")

    if missing:
        return VerificationResult(
            check_name="completeness",
            passed=False,
            details=f"Missing artifacts: {', '.join(missing)}",
        )
    else:
        return VerificationResult(
            check_name="completeness",
            passed=True,
            details="All protocol stages produced required artifacts",
        )


def run_full_verification(
    intent: Intent,
    authorization: Authorization,
    receipt: Receipt,
    ledger_entry: LedgerEntry,
) -> list[VerificationResult]:
    """
    Run all verification checks for a single governed action.

    Args:
        intent: The canonical intent.
        authorization: The authorization decision.
        receipt: The generated receipt.
        ledger_entry: The ledger entry.

    Returns:
        A list of VerificationResults for all checks.
    """
    results: list[VerificationResult] = []

    results.append(verify_completeness(intent, authorization, receipt, ledger_entry))
    results.append(verify_receipt_hash(receipt))
    results.append(verify_receipt_signature(receipt))
    results.append(verify_ledger_chain())

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    logger.info(
        "Verification complete for intent %s: %d/%d checks passed",
        intent.intent_id,
        passed,
        total,
    )

    return results
