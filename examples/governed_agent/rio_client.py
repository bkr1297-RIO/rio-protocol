"""
RIO Client — Interface for Governed Agents

This module provides a high-level client that AI agents use to submit action
requests through the RIO Governed Execution Pipeline instead of acting directly.

The client wraps the RIO pipeline and approval workflow, providing a simple
interface:

    client = RIOClient(agent_id="procurement_agent")
    result = client.submit(action_type="transfer_funds", parameters={...})

The client handles:
    - Submitting the request to the pipeline
    - Detecting when human approval is required
    - Waiting for approval (with configurable timeout)
    - Returning the full execution result with receipt and ledger references

The agent never calls external systems directly. Every action goes through RIO.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import sys
import os

# Add the project root to the path so we can import the runtime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from runtime.pipeline import PipelineResult, run as pipeline_run
from runtime.state import SystemState
from runtime.approvals import approval_manager
from runtime.corpus.corpus_store import read_corpus
from runtime.corpus.replay_engine import replay_record

logger = logging.getLogger("rio.client")


# ---------------------------------------------------------------------------
# Result wrapper
# ---------------------------------------------------------------------------

@dataclass
class GovernedResult:
    """Result returned to the agent after a governed action completes."""

    success: bool = False
    status: str = ""  # EXECUTED, DENIED, BLOCKED, PENDING_APPROVAL, APPROVED, ERROR
    receipt_id: str = ""
    receipt_hash: str = ""
    ledger_entry_id: str = ""
    risk_score: float = 0.0
    risk_level: str = ""
    policy_decision: str = ""
    execution_result: Optional[dict] = None
    approval_id: str = ""
    error: str = ""
    elapsed_seconds: float = 0.0

    def __str__(self) -> str:
        lines = [
            f"GovernedResult(status={self.status})",
            f"  success:         {self.success}",
            f"  policy_decision: {self.policy_decision}",
            f"  risk_score:      {self.risk_score} ({self.risk_level})",
        ]
        if self.receipt_id:
            lines.append(f"  receipt_id:      {self.receipt_id}")
            lines.append(f"  receipt_hash:    {self.receipt_hash[:16]}...")
        if self.ledger_entry_id:
            lines.append(f"  ledger_entry_id: {self.ledger_entry_id}")
        if self.approval_id:
            lines.append(f"  approval_id:     {self.approval_id}")
        if self.error:
            lines.append(f"  error:           {self.error}")
        lines.append(f"  elapsed:         {self.elapsed_seconds:.3f}s")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# RIO Client
# ---------------------------------------------------------------------------

class RIOClient:
    """
    High-level client for governed agent interaction with the RIO pipeline.

    Usage:
        client = RIOClient(agent_id="procurement_agent")
        result = client.submit(
            action_type="transfer_funds",
            parameters={"amount": 48250, "recipient": "Vendor Corp", "currency": "USD"},
            justification="Invoice INV-2026-0042 due for payment",
        )
        if result.status == "PENDING_APPROVAL":
            # Wait for human approval (or poll)
            result = client.wait_for_approval(result.approval_id, timeout=300)
    """

    def __init__(
        self,
        agent_id: str,
        default_approver_id: str = "system",
        state: Optional[SystemState] = None,
        action_handler: Optional[Callable] = None,
    ):
        self.agent_id = agent_id
        self.default_approver_id = default_approver_id
        self.state = state or SystemState()
        self.action_handler = action_handler or self._default_handler

    @staticmethod
    def _default_handler(intent) -> dict:
        """Default simulated action handler."""
        return {
            "status": "completed",
            "action": intent.action_type,
            "simulated": True,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    def submit(
        self,
        action_type: str,
        parameters: dict[str, Any],
        justification: str = "",
        approver_id: str = "",
        target_resource: str = "",
    ) -> GovernedResult:
        """
        Submit an action request through the RIO governed execution pipeline.

        The agent calls this instead of acting directly. RIO evaluates policy,
        computes risk, obtains authorization, and either executes or escalates.

        Args:
            action_type: The type of action (e.g., "transfer_funds", "send_email").
            parameters: Action-specific parameters.
            justification: Why the agent wants to perform this action.
            approver_id: Override the default approver identity.
            target_resource: The target system or resource.

        Returns:
            A GovernedResult with the full outcome.
        """
        start = time.time()
        governed = GovernedResult()

        raw_input = {
            "action_type": action_type,
            "parameters": parameters,
            "requested_by": self.agent_id,
            "justification": justification or f"Agent {self.agent_id} automated action",
        }
        if target_resource:
            raw_input["target_resource"] = target_resource

        try:
            pipeline_result: PipelineResult = pipeline_run(
                actor_id=self.agent_id,
                raw_input=raw_input,
                approver_id=approver_id or self.default_approver_id,
                state=self.state,
                action_handler=self.action_handler,
            )

            # Map pipeline result to governed result
            governed.elapsed_seconds = time.time() - start

            if pipeline_result.pending_approval:
                governed.status = "PENDING_APPROVAL"
                governed.success = False
                governed.approval_id = (
                    pipeline_result.approval.approval_id
                    if pipeline_result.approval
                    else ""
                )
                governed.policy_decision = "ESCALATE"
                # Risk info is available on the approval object's stored context
                if pipeline_result.receipt:
                    governed.risk_score = pipeline_result.receipt.risk_score
                    governed.risk_level = pipeline_result.receipt.risk_level
                logger.info(
                    "Request escalated — approval_id=%s risk=%s",
                    governed.approval_id,
                    governed.risk_score,
                )
                return governed

            # Completed (executed or denied)
            if pipeline_result.receipt:
                governed.receipt_id = pipeline_result.receipt.receipt_id
                governed.receipt_hash = pipeline_result.receipt.receipt_hash
            if pipeline_result.ledger_entry:
                governed.ledger_entry_id = pipeline_result.ledger_entry.ledger_entry_id

            governed.success = pipeline_result.success
            if pipeline_result.execution_result:
                governed.status = pipeline_result.execution_result.execution_status.value
                governed.execution_result = pipeline_result.execution_result.result_data
            elif pipeline_result.receipt:
                governed.status = "DENIED"

            # Extract policy/risk info from the receipt
            if pipeline_result.receipt:
                governed.policy_decision = pipeline_result.receipt.policy_decision or ""
                governed.risk_score = pipeline_result.receipt.risk_score
                governed.risk_level = pipeline_result.receipt.risk_level

        except Exception as exc:
            governed.status = "ERROR"
            governed.error = str(exc)
            governed.elapsed_seconds = time.time() - start
            logger.exception("Pipeline error: %s", exc)

        return governed

    def wait_for_approval(
        self,
        approval_id: str,
        approver_id: str = "",
        approver_role: str = "manager",
        timeout: float = 300.0,
        poll_interval: float = 1.0,
    ) -> GovernedResult:
        """
        Simulate waiting for human approval and then process it.

        In a production system, this would poll an approval API. In this
        example, it directly invokes the approval_manager to demonstrate
        the full flow.

        Args:
            approval_id: The pending approval to resolve.
            approver_id: Identity of the human approver.
            approver_role: Role of the approver (manager or admin).
            timeout: Maximum seconds to wait.
            poll_interval: Seconds between polls (for future async use).

        Returns:
            A GovernedResult with the post-approval outcome.
        """
        start = time.time()
        governed = GovernedResult()

        actual_approver = approver_id or self.default_approver_id

        try:
            approval_result = approval_manager.approve(
                approval_id=approval_id,
                approver_id=actual_approver,
                approver_role=approver_role,
            )

            governed.elapsed_seconds = time.time() - start

            if approval_result.error:
                governed.status = "ERROR"
                governed.error = approval_result.error
                return governed

            governed.success = True
            governed.status = "APPROVED"
            governed.approval_id = approval_id

            if approval_result.receipt:
                governed.receipt_id = approval_result.receipt.receipt_id
                governed.receipt_hash = approval_result.receipt.receipt_hash
            if approval_result.ledger_entry:
                governed.ledger_entry_id = approval_result.ledger_entry.ledger_entry_id

        except Exception as exc:
            governed.status = "ERROR"
            governed.error = str(exc)
            governed.elapsed_seconds = time.time() - start
            logger.exception("Approval error: %s", exc)

        return governed

    def get_corpus_records(self, count: int = 5) -> list:
        """Retrieve the most recent corpus records for replay/analysis."""
        records = read_corpus()
        return records[-count:] if len(records) > count else records

    def replay(self, record, override_role: str = "") -> Any:
        """Replay a corpus record through the policy engine with optional overrides."""
        return replay_record(record, override_role=override_role)
