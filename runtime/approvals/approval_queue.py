"""
RIO Runtime — Approval Queue

Manages a queue of pending human approval requests. When the policy engine
returns REQUIRE_APPROVAL (mapped to Decision.ESCALATE), the pipeline creates
an approval request and parks it here until a human approver acts on it.

Each approval request is persisted to /runtime/data/approvals.jsonl and
also held in an in-memory dict for fast lookup.

Approval statuses:
    PENDING   — Awaiting human decision
    APPROVED  — Human approved; pipeline will resume
    DENIED    — Human denied; denial receipt generated
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("rio.approval_queue")


# ---------------------------------------------------------------------------
# Approval Request dataclass
# ---------------------------------------------------------------------------

@dataclass
class ApprovalRequest:
    """A single approval request waiting for human decision."""
    approval_id: str = field(default_factory=lambda: f"APR-{uuid.uuid4().hex[:8].upper()}")
    request_id: str = ""
    intent_id: str = ""
    action: str = ""
    requester: str = ""
    role: str = ""
    target_resource: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    risk_score: float = 0.0
    risk_level: str = ""
    policy_rule_id: str = ""
    reason: str = ""
    status: str = "PENDING"           # PENDING | APPROVED | DENIED
    created_at: int = field(default_factory=lambda: int(time.time() * 1000))
    resolved_at: Optional[int] = None
    resolved_by: Optional[str] = None


# ---------------------------------------------------------------------------
# In-memory queue (keyed by approval_id)
# ---------------------------------------------------------------------------

_queue: Dict[str, ApprovalRequest] = {}


def add(approval: ApprovalRequest) -> ApprovalRequest:
    """Add an approval request to the queue."""
    _queue[approval.approval_id] = approval
    logger.info(
        "Approval request %s added to queue — action=%s requester=%s risk=%.1f",
        approval.approval_id,
        approval.action,
        approval.requester,
        approval.risk_score,
    )
    return approval


def get(approval_id: str) -> Optional[ApprovalRequest]:
    """Retrieve an approval request by ID."""
    return _queue.get(approval_id)


def get_all() -> List[ApprovalRequest]:
    """Return all approval requests (newest first)."""
    return sorted(_queue.values(), key=lambda a: a.created_at, reverse=True)


def get_pending() -> List[ApprovalRequest]:
    """Return only PENDING approval requests."""
    return [a for a in get_all() if a.status == "PENDING"]


def update_status(
    approval_id: str,
    status: str,
    resolved_by: str,
) -> Optional[ApprovalRequest]:
    """
    Update the status of an approval request.

    Args:
        approval_id: The approval to update.
        status: New status (APPROVED or DENIED).
        resolved_by: Identity of the approver/denier.

    Returns:
        The updated ApprovalRequest, or None if not found.
    """
    approval = _queue.get(approval_id)
    if approval is None:
        logger.warning("Approval %s not found in queue", approval_id)
        return None

    if approval.status != "PENDING":
        logger.warning(
            "Approval %s already resolved (status=%s), cannot change to %s",
            approval_id,
            approval.status,
            status,
        )
        return None

    approval.status = status
    approval.resolved_at = int(time.time() * 1000)
    approval.resolved_by = resolved_by

    logger.info(
        "Approval %s resolved: status=%s by=%s",
        approval_id,
        status,
        resolved_by,
    )
    return approval


def reset() -> None:
    """Clear all approval requests. For testing only."""
    _queue.clear()
    logger.info("Approval queue cleared")


def to_dict(approval: ApprovalRequest) -> Dict[str, Any]:
    """Serialize an ApprovalRequest to a dict for JSONL persistence."""
    return {
        "approval_id": approval.approval_id,
        "request_id": approval.request_id,
        "intent_id": approval.intent_id,
        "action": approval.action,
        "requester": approval.requester,
        "role": approval.role,
        "target_resource": approval.target_resource,
        "parameters": approval.parameters,
        "risk_score": approval.risk_score,
        "risk_level": approval.risk_level,
        "policy_rule_id": approval.policy_rule_id,
        "reason": approval.reason,
        "status": approval.status,
        "created_at": approval.created_at,
        "created_at_iso": datetime.fromtimestamp(
            approval.created_at / 1000, tz=timezone.utc
        ).isoformat(),
        "resolved_at": approval.resolved_at,
        "resolved_by": approval.resolved_by,
    }
