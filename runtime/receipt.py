"""
RIO Runtime — Stage 8: Receipt / Attestation

Generates a cryptographic receipt after every execution decision (allow, deny,
or block). The receipt includes hashes of the intent, authorization, and
execution result, forming a hash chain with the previous receipt.

Every action — whether executed, denied, or blocked — must produce a receipt.
This enforces INV-02 (Receipt Completeness).

Spec reference: /spec/receipt_protocol.md, /spec/08_attestation.md
Protocol stage: Step 7 of the 8-step Governed Execution Protocol
Related invariants: INV-02 (Receipt Completeness), INV-04 (Hash Chain Integrity)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import Any

from .models import Authorization, Decision, ExecutionStatus, Intent, Receipt

logger = logging.getLogger("rio.receipt")


def generate_receipt(
    intent: Intent,
    authorization: Authorization,
    execution_status: ExecutionStatus,
    result_data: dict[str, Any],
    previous_receipt_hash: str,
) -> Receipt:
    """
    Generate a signed receipt for the governed action.

    The receipt captures the full decision chain: what was requested (intent),
    what was decided (authorization), and what happened (execution result).
    It is hash-linked to the previous receipt to form a tamper-evident chain.

    Args:
        intent: The canonical Intent.
        authorization: The Authorization decision.
        execution_status: The outcome of the Execution Gate.
        result_data: The result of the executed action (or empty if blocked).
        previous_receipt_hash: Hash of the preceding receipt (empty for genesis).

    Returns:
        A signed Receipt ready for the Ledger stage.
    """
    now = int(time.time() * 1000)

    # Compute result hash
    result_hash = _compute_hash(json.dumps(result_data, sort_keys=True))

    # Build receipt
    receipt = Receipt(
        receipt_id=str(uuid.uuid4()),
        request_id=intent.request_id,
        intent_id=intent.intent_id,
        authorization_id=authorization.authorization_id,
        decision=authorization.decision,
        action_type=intent.action_type,
        execution_status=execution_status,
        execution_timestamp=now,
        result_hash=result_hash,
        previous_receipt_hash=previous_receipt_hash,
    )

    # Compute receipt hash (canonical JSON + previous_receipt_hash)
    receipt.receipt_hash = _compute_receipt_hash(receipt)

    # Sign receipt
    receipt.signature = _sign_receipt(receipt)

    logger.info(
        "Receipt %s generated for intent %s — decision=%s, status=%s, hash=%s",
        receipt.receipt_id,
        receipt.intent_id,
        receipt.decision.value,
        receipt.execution_status.value,
        receipt.receipt_hash[:16] + "...",
    )

    return receipt


def _compute_hash(data: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _compute_receipt_hash(receipt: Receipt) -> str:
    """
    Compute the receipt hash using canonical JSON serialization.

    Formula: SHA-256(canonical_json(receipt_fields) + previous_receipt_hash)

    In a production implementation, this would use a deterministic
    canonical JSON serialization (RFC 8785).
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
    return _compute_hash(combined)


def _sign_receipt(receipt: Receipt) -> str:
    """
    Sign the receipt hash with the system's attestation key.

    In a production implementation, this would use ECDSA-secp256k1.
    This reference skeleton returns a placeholder signature.
    """
    return f"sig:{receipt.receipt_hash[:32]}"
