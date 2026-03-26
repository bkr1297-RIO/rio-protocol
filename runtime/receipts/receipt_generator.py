"""
RIO Runtime — Governed Execution Protocol v2: Receipt Generator

Generates full cryptographic receipts that provide verifiable proof of intent,
approval, execution, and verification. Each receipt includes:

  - intent_hash:        SHA-256 of the canonical intent JSON
  - action_hash:        SHA-256 of the execution payload
  - verification_hash:  SHA-256 of the post-execution verification result
  - receipt_hash:       SHA-256 of the full receipt (excluding signature)
  - previous_hash:      Hash of the previous ledger receipt for chain integrity

v2 receipts extend v1 with:
  - Separate intent, action, and verification hashes
  - ISO 8601 timestamps for request, approval, and execution
  - Verification status (verified | failed | skipped)
  - requested_by / approved_by identity fields
  - Denial receipts for rejected actions

Spec reference: /spec/receipt_protocol.md
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("rio.receipts.generator")


# ---------------------------------------------------------------------------
# v2 Receipt model
# ---------------------------------------------------------------------------

@dataclass
class ReceiptV2:
    """
    Governed Execution Protocol v2 receipt.

    Every governed action — approved, denied, or blocked — produces a v2
    receipt with full cryptographic hashes and identity attribution.
    """
    receipt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent_id: str = ""
    intent_hash: str = ""
    action: str = ""
    action_hash: str = ""
    requested_by: str = ""
    approved_by: str = ""
    decision: str = ""                  # "approved" | "denied"
    timestamp_request: str = ""         # ISO 8601
    timestamp_approval: str = ""        # ISO 8601
    timestamp_execution: str = ""       # ISO 8601
    verification_status: str = "skipped"  # "verified" | "failed" | "skipped"
    verification_hash: str = ""
    receipt_hash: str = ""
    previous_hash: str = ""
    signature: str = ""
    # Extended fields for backward compatibility
    request_id: str = ""
    authorization_id: str = ""
    execution_status: str = ""
    risk_score: float = 0.0
    risk_level: str = ""
    policy_rule_id: str = ""
    policy_decision: str = ""
    result_data: dict[str, Any] = field(default_factory=dict)


def _now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _sha256(data: str) -> str:
    """Compute SHA-256 hex digest of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def compute_intent_hash(intent_data: dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of the canonical intent JSON.

    The intent is serialized with sorted keys for deterministic hashing.
    """
    canonical = json.dumps(intent_data, sort_keys=True, default=str)
    return _sha256(canonical)


def compute_action_hash(execution_payload: dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of the execution payload.

    The payload is serialized with sorted keys for deterministic hashing.
    """
    canonical = json.dumps(execution_payload, sort_keys=True, default=str)
    return _sha256(canonical)


def compute_verification_hash(verification_result: dict[str, Any]) -> str:
    """
    Compute SHA-256 hash of the post-execution verification result.
    """
    canonical = json.dumps(verification_result, sort_keys=True, default=str)
    return _sha256(canonical)


def compute_receipt_hash(receipt: ReceiptV2) -> str:
    """
    Compute the receipt hash over all fields (excluding signature).

    Formula: SHA-256(canonical_json(receipt_fields) + previous_hash)

    This is the hash that gets signed and included in the ledger chain.
    """
    canonical = json.dumps(
        {
            "receipt_id": receipt.receipt_id,
            "intent_id": receipt.intent_id,
            "intent_hash": receipt.intent_hash,
            "action": receipt.action,
            "action_hash": receipt.action_hash,
            "requested_by": receipt.requested_by,
            "approved_by": receipt.approved_by,
            "decision": receipt.decision,
            "timestamp_request": receipt.timestamp_request,
            "timestamp_approval": receipt.timestamp_approval,
            "timestamp_execution": receipt.timestamp_execution,
            "verification_status": receipt.verification_status,
            "verification_hash": receipt.verification_hash,
        },
        sort_keys=True,
    )
    combined = canonical + receipt.previous_hash
    return _sha256(combined)


# ---------------------------------------------------------------------------
# Receipt generation
# ---------------------------------------------------------------------------

def generate_receipt_v2(
    intent: Any,
    authorization: Any,
    execution_status: str,
    result_data: dict[str, Any],
    previous_hash: str,
    verification_result: Optional[dict[str, Any]] = None,
    verification_status: str = "skipped",
    timestamp_request: str = "",
    timestamp_approval: str = "",
) -> ReceiptV2:
    """
    Generate a Governed Execution Protocol v2 receipt.

    Args:
        intent: The canonical Intent object (must have intent_id, action_type,
                requested_by, request_id, parameters, etc.).
        authorization: The Authorization object (must have authorization_id,
                       decision, approver_id).
        execution_status: The execution outcome ("EXECUTED", "BLOCKED", etc.).
        result_data: The result of the executed action.
        previous_hash: Hash of the previous receipt for chain integrity.
        verification_result: Optional dict with post-execution verification data.
        verification_status: "verified", "failed", or "skipped".
        timestamp_request: ISO 8601 timestamp of the original request.
        timestamp_approval: ISO 8601 timestamp of the approval decision.

    Returns:
        A ReceiptV2 with all hashes computed (signature added by signer).
    """
    now_iso = _now_iso()

    # Build intent data for hashing
    intent_data = {
        "intent_id": getattr(intent, "intent_id", ""),
        "action_type": getattr(intent, "action_type", ""),
        "requested_by": getattr(intent, "requested_by", ""),
        "target_resource": getattr(intent, "target_resource", ""),
        "parameters": getattr(intent, "parameters", {}),
    }
    intent_hash = compute_intent_hash(intent_data)

    # Build action hash from result data
    action_hash = compute_action_hash(result_data)

    # Build verification hash
    verification_hash = ""
    if verification_result:
        verification_hash = compute_verification_hash(verification_result)

    # Map decision
    decision_val = getattr(authorization, "decision", None)
    if hasattr(decision_val, "value"):
        decision_str = decision_val.value
    else:
        decision_str = str(decision_val) if decision_val else "denied"

    # Normalize decision to v2 format
    if decision_str in ("ALLOW", "APPROVED_BY_HUMAN"):
        decision_v2 = "approved"
    else:
        decision_v2 = "denied"

    receipt = ReceiptV2(
        receipt_id=str(uuid.uuid4()),
        intent_id=getattr(intent, "intent_id", ""),
        intent_hash=intent_hash,
        action=getattr(intent, "action_type", ""),
        action_hash=action_hash,
        requested_by=getattr(intent, "requested_by", ""),
        approved_by=getattr(authorization, "approver_id", ""),
        decision=decision_v2,
        timestamp_request=timestamp_request or now_iso,
        timestamp_approval=timestamp_approval or now_iso,
        timestamp_execution=now_iso,
        verification_status=verification_status,
        verification_hash=verification_hash,
        previous_hash=previous_hash,
        # Extended fields
        request_id=getattr(intent, "request_id", ""),
        authorization_id=getattr(authorization, "authorization_id", ""),
        execution_status=execution_status,
        risk_score=0.0,
        risk_level="",
        policy_rule_id="",
        policy_decision=decision_str,
        result_data=result_data,
    )

    # Compute receipt hash
    receipt.receipt_hash = compute_receipt_hash(receipt)

    logger.info(
        "v2 Receipt %s generated — intent=%s decision=%s verification=%s hash=%s",
        receipt.receipt_id,
        receipt.intent_id,
        receipt.decision,
        receipt.verification_status,
        receipt.receipt_hash[:16] + "...",
    )

    return receipt


def generate_denial_receipt(
    intent: Any,
    decided_by: str,
    reason: str,
    previous_hash: str,
    timestamp_request: str = "",
) -> ReceiptV2:
    """
    Generate a denial receipt for a rejected action.

    Denial receipts are written to the ledger just like approval receipts,
    ensuring a complete audit trail of all decisions.

    Args:
        intent: The canonical Intent object.
        decided_by: Identity of the actor who denied the request.
        reason: The reason for denial.
        previous_hash: Hash of the previous receipt for chain integrity.
        timestamp_request: ISO 8601 timestamp of the original request.

    Returns:
        A ReceiptV2 denial receipt with all hashes computed.
    """
    now_iso = _now_iso()

    intent_data = {
        "intent_id": getattr(intent, "intent_id", ""),
        "action_type": getattr(intent, "action_type", ""),
        "requested_by": getattr(intent, "requested_by", ""),
        "target_resource": getattr(intent, "target_resource", ""),
        "parameters": getattr(intent, "parameters", {}),
    }
    intent_hash = compute_intent_hash(intent_data)

    receipt = ReceiptV2(
        receipt_id=str(uuid.uuid4()),
        intent_id=getattr(intent, "intent_id", ""),
        intent_hash=intent_hash,
        action=getattr(intent, "action_type", ""),
        action_hash="",  # No action executed
        requested_by=getattr(intent, "requested_by", ""),
        approved_by=decided_by,
        decision="denied",
        timestamp_request=timestamp_request or now_iso,
        timestamp_approval=now_iso,
        timestamp_execution="",  # No execution
        verification_status="skipped",
        verification_hash="",
        previous_hash=previous_hash,
        # Extended fields
        request_id=getattr(intent, "request_id", ""),
        authorization_id="",
        execution_status="BLOCKED",
        result_data={"denial_reason": reason},
    )

    receipt.receipt_hash = compute_receipt_hash(receipt)

    logger.info(
        "v2 Denial receipt %s generated — intent=%s decided_by=%s reason=%s",
        receipt.receipt_id,
        receipt.intent_id,
        decided_by,
        reason,
    )

    return receipt
