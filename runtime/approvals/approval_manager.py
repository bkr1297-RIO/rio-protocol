"""
RIO Runtime — Approval Manager

Orchestrates the human approval workflow:

1. **create_approval_request** — Called by the pipeline when policy decision is
   ESCALATE (REQUIRE_APPROVAL). Creates an ApprovalRequest, persists it, and
   returns it so the pipeline can halt with PENDING_APPROVAL status.

2. **approve** — Called when a human approver (manager/admin) approves a
   pending request. Generates an authorization token and resumes the pipeline
   from the execution gate onward, producing a receipt and ledger entry.

3. **deny** — Called when a human approver denies a pending request. Generates
   a denial receipt and ledger entry without executing the action.

Role enforcement: only users with role = "manager" or "admin" may approve or deny.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from ..models import (
    Authorization,
    Decision,
    ExecutionStatus,
    Intent,
    IntentStatus,
    LedgerEntry,
    PolicyRiskResult,
    Receipt,
)
from ..state import SystemState
from .. import (
    authorization as auth_module,
    execution_gate,
    receipt as receipt_module,
    ledger,
    data_store,
)
from ..invariants import check_inv_06_no_self_authorization, InvariantViolation
from . import approval_queue
from .approval_queue import ApprovalRequest

logger = logging.getLogger("rio.approval_manager")

# Roles allowed to approve or deny requests
APPROVER_ROLES = {"manager", "admin"}


# ---------------------------------------------------------------------------
# Result dataclass for approval actions
# ---------------------------------------------------------------------------

@dataclass
class ApprovalActionResult:
    """Result of an approve or deny action."""
    success: bool = False
    approval: Optional[ApprovalRequest] = None
    authorization: Optional[Authorization] = None
    execution_result: Optional[execution_gate.ExecutionResult] = None
    receipt: Optional[Receipt] = None
    ledger_entry: Optional[LedgerEntry] = None
    error: str = ""


# ---------------------------------------------------------------------------
# Stored pipeline context for pending approvals
# ---------------------------------------------------------------------------

# When the pipeline halts at PENDING_APPROVAL, we store the context needed
# to resume execution later. Keyed by approval_id.
_pending_contexts: Dict[str, Dict[str, Any]] = {}


def store_context(
    approval_id: str,
    intent: Intent,
    policy_result: PolicyRiskResult,
    state: SystemState,
    action_handler: Optional[Callable] = None,
) -> None:
    """Store pipeline context for a pending approval so it can be resumed."""
    _pending_contexts[approval_id] = {
        "intent": intent,
        "policy_result": policy_result,
        "state": state,
        "action_handler": action_handler,
    }
    logger.info("Pipeline context stored for approval %s", approval_id)


def get_context(approval_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve stored pipeline context for a pending approval."""
    return _pending_contexts.get(approval_id)


def clear_context(approval_id: str) -> None:
    """Remove stored pipeline context after resolution."""
    _pending_contexts.pop(approval_id, None)


def reset() -> None:
    """Clear all stored contexts. For testing only."""
    _pending_contexts.clear()
    approval_queue.reset()
    logger.info("Approval manager reset")


# ---------------------------------------------------------------------------
# Create approval request
# ---------------------------------------------------------------------------

def create_approval_request(
    intent: Intent,
    policy_result: PolicyRiskResult,
    role: str,
    state: SystemState,
    action_handler: Optional[Callable] = None,
) -> ApprovalRequest:
    """
    Create a new approval request and add it to the queue.

    Called by the pipeline when policy_result.decision == Decision.ESCALATE.

    Args:
        intent: The canonical intent that requires approval.
        policy_result: The policy/risk evaluation result.
        role: The requester's role.
        state: The current system state.
        action_handler: Optional action handler to use when resuming.

    Returns:
        The created ApprovalRequest.
    """
    approval = ApprovalRequest(
        request_id=intent.request_id,
        intent_id=intent.intent_id,
        action=intent.action_type,
        requester=intent.requested_by,
        role=role,
        target_resource=intent.target_resource,
        parameters=intent.parameters,
        risk_score=policy_result.risk_score,
        risk_level=policy_result.risk_level,
        policy_rule_id=policy_result.policy_rule_id,
        reason=policy_result.reason,
    )

    # Add to queue
    approval_queue.add(approval)

    # Persist to JSONL
    data_store.write_approval(approval)

    # Store pipeline context for later resumption
    store_context(
        approval_id=approval.approval_id,
        intent=intent,
        policy_result=policy_result,
        state=state,
        action_handler=action_handler,
    )

    # Mark intent as pending approval
    intent.status = IntentStatus.PENDING_APPROVAL

    logger.info(
        "Approval request %s created for intent %s (action=%s, requester=%s)",
        approval.approval_id,
        intent.intent_id,
        intent.action_type,
        intent.requested_by,
    )

    return approval


# ---------------------------------------------------------------------------
# Approve
# ---------------------------------------------------------------------------

def approve(
    approval_id: str,
    approver_id: str,
    approver_role: str,
) -> ApprovalActionResult:
    """
    Approve a pending request and resume the pipeline.

    Only users with role in APPROVER_ROLES can approve.

    Args:
        approval_id: The approval request to approve.
        approver_id: Identity of the approver.
        approver_role: Role of the approver (must be manager or admin).

    Returns:
        An ApprovalActionResult with the execution artifacts.
    """
    result = ApprovalActionResult()

    # Role check
    if approver_role not in APPROVER_ROLES:
        result.error = f"Role '{approver_role}' is not authorized to approve. Required: {APPROVER_ROLES}"
        logger.warning("Approval denied: %s", result.error)
        return result

    # Get the approval request
    approval = approval_queue.get(approval_id)
    if approval is None:
        result.error = f"Approval {approval_id} not found"
        logger.warning(result.error)
        return result

    if approval.status != "PENDING":
        result.error = f"Approval {approval_id} already resolved (status={approval.status})"
        logger.warning(result.error)
        return result

    # Get stored pipeline context
    ctx = get_context(approval_id)
    if ctx is None:
        result.error = f"No pipeline context found for approval {approval_id}"
        logger.error(result.error)
        return result

    intent: Intent = ctx["intent"]
    policy_result: PolicyRiskResult = ctx["policy_result"]
    state: SystemState = ctx["state"]
    action_handler = ctx["action_handler"]

    # INV-06: No self-authorization — approver must differ from requester
    if approver_id == intent.requested_by:
        result.error = f"INV-06 violation: approver '{approver_id}' cannot approve their own request"
        logger.warning(result.error)
        return result

    # Update approval status
    approval_queue.update_status(approval_id, "APPROVED", approver_id)
    result.approval = approval

    # Persist updated approval
    data_store.write_approval(approval)

    # --- Resume pipeline from Authorization onward ---

    # Override policy decision to ALLOW for authorization
    policy_result_for_auth = PolicyRiskResult(
        intent_id=policy_result.intent_id,
        decision=Decision.ALLOW,
        risk_score=policy_result.risk_score,
        risk_level=policy_result.risk_level,
        policy_rule_id=policy_result.policy_rule_id,
        policy_ids=policy_result.policy_ids,
        constraints=policy_result.constraints,
        reason=f"Human approved by {approver_id} (original: {policy_result.reason})",
    )

    # Stage 5: Authorization
    auth = auth_module.authorize(
        intent=intent,
        policy_result=policy_result_for_auth,
        approver_id=approver_id,
        state=state,
    )
    result.authorization = auth

    # Stage 6: Execution Gate
    exec_result = execution_gate.execute(
        intent=intent,
        authorization=auth,
        state=state,
        action_handler=action_handler,
    )
    result.execution_result = exec_result

    # Stage 7: Receipt
    rcpt = receipt_module.generate_receipt(
        intent=intent,
        authorization=auth,
        execution_status=exec_result.execution_status,
        result_data=exec_result.result_data,
        previous_receipt_hash=state.ledger_head_hash,
    )
    rcpt.risk_score = policy_result.risk_score
    rcpt.risk_level = policy_result.risk_level
    rcpt.policy_rule_id = policy_result.policy_rule_id
    rcpt.policy_decision = "APPROVED_BY_HUMAN"
    rcpt = receipt_module.rehash_receipt(rcpt)
    result.receipt = rcpt

    # Stage 8: Ledger
    entry = ledger.append(rcpt, state)
    result.ledger_entry = entry

    # Persist
    connector_id = getattr(exec_result, "connector_id", "")
    data_store.write_receipt(rcpt, connector_id=connector_id)
    data_store.write_ledger_entry(entry)
    data_store.write_system_state(
        kill_switch_active=state.kill_switch_active,
        kill_switch_engaged_by=state.kill_switch_engaged_by,
        kill_switch_engaged_at=state.kill_switch_engaged_at,
        policy_version=state.policy_version,
        risk_model_version=state.risk_model_version,
        ledger_length=state.ledger_length,
    )

    # Clean up context
    clear_context(approval_id)

    result.success = exec_result.execution_status == ExecutionStatus.EXECUTED

    logger.info(
        "Approval %s APPROVED by %s — execution_status=%s receipt=%s ledger=%s",
        approval_id,
        approver_id,
        exec_result.execution_status.value,
        rcpt.receipt_id,
        entry.ledger_entry_id,
    )

    return result


# ---------------------------------------------------------------------------
# Deny
# ---------------------------------------------------------------------------

def deny(
    approval_id: str,
    denier_id: str,
    denier_role: str,
) -> ApprovalActionResult:
    """
    Deny a pending request. Generates a denial receipt and ledger entry.

    Only users with role in APPROVER_ROLES can deny.

    Args:
        approval_id: The approval request to deny.
        denier_id: Identity of the denier.
        denier_role: Role of the denier (must be manager or admin).

    Returns:
        An ApprovalActionResult with the denial artifacts.
    """
    result = ApprovalActionResult()

    # Role check
    if denier_role not in APPROVER_ROLES:
        result.error = f"Role '{denier_role}' is not authorized to deny. Required: {APPROVER_ROLES}"
        logger.warning("Denial rejected: %s", result.error)
        return result

    # Get the approval request
    approval = approval_queue.get(approval_id)
    if approval is None:
        result.error = f"Approval {approval_id} not found"
        logger.warning(result.error)
        return result

    if approval.status != "PENDING":
        result.error = f"Approval {approval_id} already resolved (status={approval.status})"
        logger.warning(result.error)
        return result

    # Get stored pipeline context
    ctx = get_context(approval_id)
    if ctx is None:
        result.error = f"No pipeline context found for approval {approval_id}"
        logger.error(result.error)
        return result

    intent: Intent = ctx["intent"]
    policy_result: PolicyRiskResult = ctx["policy_result"]
    state: SystemState = ctx["state"]

    # Update approval status
    approval_queue.update_status(approval_id, "DENIED", denier_id)
    result.approval = approval

    # Persist updated approval
    data_store.write_approval(approval)

    # Generate denial authorization
    auth = Authorization(
        authorization_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        decision=Decision.DENY,
        approver_id=denier_id,
        approval_timestamp=int(time.time() * 1000),
    )
    result.authorization = auth
    intent.status = IntentStatus.DENIED

    # Generate denial receipt
    rcpt = receipt_module.generate_receipt(
        intent=intent,
        authorization=auth,
        execution_status=ExecutionStatus.BLOCKED,
        result_data={"denial_reason": f"Human denied by {denier_id}"},
        previous_receipt_hash=state.ledger_head_hash,
    )
    rcpt.risk_score = policy_result.risk_score
    rcpt.risk_level = policy_result.risk_level
    rcpt.policy_rule_id = policy_result.policy_rule_id
    rcpt.policy_decision = "DENIED_BY_HUMAN"
    rcpt = receipt_module.rehash_receipt(rcpt)
    result.receipt = rcpt

    # Append to ledger
    entry = ledger.append(rcpt, state)
    result.ledger_entry = entry

    # Persist
    data_store.write_receipt(rcpt)
    data_store.write_ledger_entry(entry)
    data_store.write_system_state(
        kill_switch_active=state.kill_switch_active,
        kill_switch_engaged_by=state.kill_switch_engaged_by,
        kill_switch_engaged_at=state.kill_switch_engaged_at,
        policy_version=state.policy_version,
        risk_model_version=state.risk_model_version,
        ledger_length=state.ledger_length,
    )

    # Clean up context
    clear_context(approval_id)

    result.success = False  # Denied requests are not "successful"

    logger.info(
        "Approval %s DENIED by %s — receipt=%s ledger=%s",
        approval_id,
        denier_id,
        rcpt.receipt_id,
        entry.ledger_entry_id,
    )

    return result
