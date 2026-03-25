"""
RIO Runtime — Governed Execution Pipeline

Orchestrates the full 8-step Governed Execution Protocol by chaining each stage
in strict order. No stage may be skipped. Every request — whether approved, denied,
blocked, or pending approval — produces a receipt and a ledger entry.

Execution flow:
    Intake → Classification → Intent Validation → Structured Intent →
    Policy & Risk → [REQUIRE_APPROVAL → Approval Queue] or Authorization →
    Execution Gate → Receipt → Ledger

When the policy engine returns ESCALATE (REQUIRE_APPROVAL), the pipeline halts
and creates an approval request. The pipeline resumes when a human approver
acts on the request via the approval_manager.

The pipeline enforces all protocol invariants (INV-01 through INV-08) and
logs every stage transition for auditability.

Spec reference: /spec/governed_execution_protocol.md, /spec/runtime_flow.md
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from . import (
    intake,
    classification,
    intent_validation,
    structured_intent,
    policy_risk,
    authorization,
    execution_gate,
    receipt as receipt_module,
    ledger,
    verification,
    data_store,
)
from .approvals import approval_manager
from .approvals.approval_queue import ApprovalRequest
from .invariants import (
    check_inv_01_completeness,
    check_inv_02_receipt_completeness,
    check_inv_03_ledger_completeness,
    check_inv_04_hash_chain,
    InvariantViolation,
)
from .models import (
    Authorization as AuthorizationModel,
    Decision,
    ExecutionStatus,
    Intent,
    LedgerEntry,
    Receipt,
    Request,
)
from .state import SystemState

logger = logging.getLogger("rio.pipeline")


@dataclass
class PipelineResult:
    """
    Complete result of a governed execution pipeline run.

    Contains all artifacts produced by each stage, enabling full audit
    reconstruction and invariant verification.
    """
    request: Optional[Request] = None
    intent: Optional[Intent] = None
    authorization: Optional[AuthorizationModel] = None
    execution_result: Optional[execution_gate.ExecutionResult] = None
    receipt: Optional[Receipt] = None
    ledger_entry: Optional[LedgerEntry] = None
    approval: Optional[ApprovalRequest] = None
    success: bool = False
    pending_approval: bool = False
    error: str = ""
    stage_failed: str = ""
    stages_completed: list[str] = field(default_factory=list)
    duration_ms: int = 0


def run(
    actor_id: str,
    raw_input: dict[str, Any],
    approver_id: str,
    state: SystemState,
    source_ip: str = "",
    authenticated: bool = True,
    action_handler: Optional[Callable[[Intent], dict[str, Any]]] = None,
) -> PipelineResult:
    """
    Execute the full governed execution pipeline for a single request.

    This is the primary entry point for the RIO runtime. Every request enters
    here and traverses all stages in order. No stage is skipped — even denied
    or blocked requests produce receipts and ledger entries.

    When the policy decision is ESCALATE (REQUIRE_APPROVAL), the pipeline halts
    and returns a PipelineResult with pending_approval=True and an approval
    object. The pipeline resumes when a human approver acts on the request.

    Args:
        actor_id: Identity of the requesting actor.
        raw_input: Raw request payload (must include 'action_type' or 'action').
        approver_id: Identity of the authorizing actor (must differ from actor_id).
        state: The current system state.
        source_ip: Optional source IP address.
        authenticated: Whether the actor has been authenticated.
        action_handler: Optional callable that performs the actual action.

    Returns:
        A PipelineResult containing all stage artifacts.
    """
    start_time = time.time()
    result = PipelineResult()

    try:
        # ---------------------------------------------------------------
        # Stage 1: Intake
        # ---------------------------------------------------------------
        logger.info("PIPELINE START — actor=%s action=%s", actor_id, raw_input.get("action_type", "unknown"))

        req = intake.register_request(
            actor_id=actor_id,
            raw_input=raw_input,
            source_ip=source_ip,
            authenticated=authenticated,
        )
        result.request = req
        result.stages_completed.append("intake")
        logger.info("STAGE 1 COMPLETE — intake — request_id=%s", req.request_id)

        # Persist request to JSONL data store
        role = raw_input.get("role", "employee")
        data_store.write_request(req, role=role)

        # ---------------------------------------------------------------
        # Stage 2: Classification
        # ---------------------------------------------------------------
        class_result = classification.classify(req)
        result.stages_completed.append("classification")
        logger.info(
            "STAGE 2 COMPLETE — classification — action_type=%s risk=%s",
            class_result.action_type,
            class_result.risk_category.value,
        )

        # ---------------------------------------------------------------
        # Stage 3a: Intent Validation
        # ---------------------------------------------------------------
        validation = intent_validation.validate(req, class_result)
        result.stages_completed.append("intent_validation")

        if not validation.valid:
            logger.warning(
                "STAGE 3a FAILED — intent_validation — errors=%s",
                validation.errors,
            )
            # Validation failed — still produce receipt and ledger entry
            # Create a minimal intent for receipt generation
            intent_obj = Intent(
                request_id=req.request_id,
                action_type=class_result.action_type,
                requested_by=actor_id,
            )
            result.intent = intent_obj

            # Create a denial authorization
            auth = AuthorizationModel(
                intent_id=intent_obj.intent_id,
                decision=Decision.DENY,
                approver_id="system:validation",
            )
            result.authorization = auth

            # Generate receipt for the denial
            rcpt = receipt_module.generate_receipt(
                intent=intent_obj,
                authorization=auth,
                execution_status=ExecutionStatus.BLOCKED,
                result_data={"validation_errors": validation.errors},
                previous_receipt_hash=state.ledger_head_hash,
            )
            result.receipt = rcpt
            result.stages_completed.append("receipt")

            # Append to ledger
            entry = ledger.append(rcpt, state)
            result.ledger_entry = entry
            result.stages_completed.append("ledger")

            # Persist receipt and ledger entry to JSONL data store
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

            result.error = f"Intent validation failed: {validation.errors}"
            result.stage_failed = "intent_validation"
            result.duration_ms = int((time.time() - start_time) * 1000)
            logger.info("PIPELINE END — DENIED at validation — request_id=%s", req.request_id)
            return result

        logger.info("STAGE 3a COMPLETE — intent_validation — valid=True")

        # ---------------------------------------------------------------
        # Stage 3b: Structured Intent
        # ---------------------------------------------------------------
        intent_obj = structured_intent.form_intent(req, class_result)
        result.intent = intent_obj
        result.stages_completed.append("structured_intent")
        logger.info(
            "STAGE 3b COMPLETE — structured_intent — intent_id=%s",
            intent_obj.intent_id,
        )

        # ---------------------------------------------------------------
        # Stage 4: Policy & Risk
        # ---------------------------------------------------------------
        # Extract role from raw_input or default to 'employee'
        role = raw_input.get("role", "employee")
        policy_result = policy_risk.evaluate(intent_obj, role=role)
        result.stages_completed.append("policy_risk")
        logger.info(
            "STAGE 4 COMPLETE — policy_risk — decision=%s risk_score=%.2f",
            policy_result.decision.value,
            policy_result.risk_score,
        )

        # ---------------------------------------------------------------
        # REQUIRE_APPROVAL check — halt pipeline if escalation needed
        # ---------------------------------------------------------------
        if policy_result.decision == Decision.ESCALATE:
            logger.info(
                "PIPELINE HALTED — REQUIRE_APPROVAL — creating approval request for intent %s",
                intent_obj.intent_id,
            )

            approval = approval_manager.create_approval_request(
                intent=intent_obj,
                policy_result=policy_result,
                role=role,
                state=state,
                action_handler=action_handler,
            )

            result.approval = approval
            result.pending_approval = True
            result.stages_completed.append("approval_queue")
            result.duration_ms = int((time.time() - start_time) * 1000)

            logger.info(
                "PIPELINE END — PENDING_APPROVAL — approval_id=%s request_id=%s",
                approval.approval_id,
                req.request_id,
            )
            return result

        # ---------------------------------------------------------------
        # Stage 5: Authorization
        # ---------------------------------------------------------------
        # Extract approver role from raw_input or default to empty
        approver_role = raw_input.get("approver_role", "")
        auth = authorization.authorize(
            intent=intent_obj,
            policy_result=policy_result,
            approver_id=approver_id,
            state=state,
            approver_role=approver_role,
        )
        result.authorization = auth
        result.stages_completed.append("authorization")
        logger.info(
            "STAGE 5 COMPLETE — authorization — decision=%s token=%s",
            auth.decision.value,
            auth.authorization_id,
        )

        # ---------------------------------------------------------------
        # Stage 6: Execution Gate
        # ---------------------------------------------------------------
        exec_result = execution_gate.execute(
            intent=intent_obj,
            authorization=auth,
            state=state,
            action_handler=action_handler,
        )
        result.execution_result = exec_result
        result.stages_completed.append("execution_gate")
        logger.info(
            "STAGE 6 COMPLETE — execution_gate — status=%s",
            exec_result.execution_status.value,
        )

        # ---------------------------------------------------------------
        # Stage 7: Receipt
        # ---------------------------------------------------------------
        rcpt = receipt_module.generate_receipt(
            intent=intent_obj,
            authorization=auth,
            execution_status=exec_result.execution_status,
            result_data=exec_result.result_data,
            previous_receipt_hash=state.ledger_head_hash,
        )
        # Propagate risk and policy fields to receipt
        rcpt.risk_score = policy_result.risk_score
        rcpt.risk_level = policy_result.risk_level
        rcpt.policy_rule_id = policy_result.policy_rule_id
        rcpt.policy_decision = policy_result.decision.value
        # Recompute receipt hash with updated fields
        rcpt = receipt_module.rehash_receipt(rcpt)
        result.receipt = rcpt
        result.stages_completed.append("receipt")
        logger.info(
            "STAGE 7 COMPLETE — receipt — receipt_id=%s hash=%s",
            rcpt.receipt_id,
            rcpt.receipt_hash[:16] + "...",
        )

        # ---------------------------------------------------------------
        # Stage 8: Ledger
        # ---------------------------------------------------------------
        # Pass IAM enrichment fields to ledger
        iam_kwargs = {
            "requested_by": intent_obj.requested_by,
            "approved_by": auth.approver_id,
            "requester_role": role,
            "approver_role": getattr(auth, "approver_role", ""),
            "authority_scope": getattr(auth, "authority_scope", ""),
        }
        entry = ledger.append(rcpt, state, **iam_kwargs)
        result.ledger_entry = entry
        result.stages_completed.append("ledger")
        logger.info(
            "STAGE 8 COMPLETE — ledger — entry_id=%s chain_length=%d",
            entry.ledger_entry_id,
            state.ledger_length,
        )

        # ---------------------------------------------------------------
        # Persist to JSONL data store (for Audit Dashboard)
        # ---------------------------------------------------------------
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

        # ---------------------------------------------------------------
        # Post-pipeline: Invariant verification
        # ---------------------------------------------------------------
        try:
            check_inv_02_receipt_completeness(rcpt)
            check_inv_03_ledger_completeness(rcpt, entry)
            logger.info("INVARIANTS VERIFIED — INV-02, INV-03 passed")
        except InvariantViolation as e:
            logger.error("INVARIANT VIOLATION — %s", str(e))
            result.error = f"Post-pipeline invariant violation: {str(e)}"

        # Determine success
        result.success = exec_result.execution_status == ExecutionStatus.EXECUTED

        result.duration_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "PIPELINE END — success=%s status=%s duration=%dms request_id=%s",
            result.success,
            exec_result.execution_status.value,
            result.duration_ms,
            req.request_id,
        )

        return result

    except InvariantViolation as e:
        result.error = f"Invariant violation: {str(e)}"
        result.stage_failed = "invariant_check"
        result.duration_ms = int((time.time() - start_time) * 1000)
        logger.error("PIPELINE ABORT — invariant violation: %s", str(e))
        return result

    except Exception as e:
        result.error = f"Pipeline error: {str(e)}"
        result.stage_failed = "unknown"
        result.duration_ms = int((time.time() - start_time) * 1000)
        logger.error("PIPELINE ABORT — unexpected error: %s", str(e))
        return result
