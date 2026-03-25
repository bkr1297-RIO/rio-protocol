"""
RIO Runtime — Governance Ledger Integration

Creates GOVERNANCE_CHANGE receipts and ledger entries for policy changes.
Every governance action (activate, rollback) is recorded in the audit ledger
to ensure full traceability of policy evolution.

Entry type: GOVERNANCE_CHANGE

Ledger records:
- policy version change (old → new)
- who proposed
- who approved
- when activated
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import Any

from ..models import Authorization, Decision, ExecutionStatus, Intent, Receipt
from .. import ledger as ledger_module
from .. import data_store
from ..state import SystemState
from ..receipt import generate_receipt, rehash_receipt

logger = logging.getLogger("rio.governance_ledger")

# Shared system state for governance ledger entries
_governance_state: SystemState | None = None


def set_governance_state(state: SystemState) -> None:
    """Set the system state used for governance ledger entries."""
    global _governance_state
    _governance_state = state


def get_governance_state() -> SystemState:
    """Get or create the governance system state."""
    global _governance_state
    if _governance_state is None:
        _governance_state = SystemState()
    return _governance_state


def record_governance_change(
    change_type: str,
    old_version: str,
    new_version: str,
    proposed_by: str,
    approved_by: str,
    change_summary: str,
    change_id: str = "",
) -> dict[str, Any]:
    """
    Record a governance change in the audit ledger.

    Creates a synthetic intent, authorization, receipt, and ledger entry
    to represent the governance action in the immutable audit trail.

    Args:
        change_type: Type of change (ACTIVATE, ROLLBACK, etc.)
        old_version: Previous policy version.
        new_version: New policy version.
        proposed_by: Identity of the proposer.
        approved_by: Identity of the approver.
        change_summary: Human-readable summary.
        change_id: Optional change ID reference.

    Returns:
        Dict with receipt and ledger_entry objects.
    """
    state = get_governance_state()
    now = int(time.time() * 1000)

    # Create a synthetic intent for the governance action
    intent = Intent(
        intent_id=str(uuid.uuid4()),
        request_id=f"GOV-{uuid.uuid4().hex[:8].upper()}",
        action_type="GOVERNANCE_CHANGE",
        target_resource="policy_engine",
        parameters={
            "change_type": change_type,
            "old_version": old_version,
            "new_version": new_version,
            "change_id": change_id,
            "change_summary": change_summary,
        },
        requested_by=proposed_by,
        justification=change_summary,
        timestamp=now,
    )

    # Create a synthetic authorization
    authorization = Authorization(
        authorization_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        decision=Decision.ALLOW,
        approver_id=approved_by,
        approval_timestamp=now,
        expiration_timestamp=now + 60000,
        single_use=True,
        signature=f"gov_sig:{uuid.uuid4().hex[:16]}",
    )

    # Generate receipt
    previous_receipt_hash = state.ledger_head_hash
    receipt = generate_receipt(
        intent=intent,
        authorization=authorization,
        execution_status=ExecutionStatus.EXECUTED,
        result_data={
            "change_type": change_type,
            "old_version": old_version,
            "new_version": new_version,
            "proposed_by": proposed_by,
            "approved_by": approved_by,
            "change_id": change_id,
        },
        previous_receipt_hash=previous_receipt_hash,
    )

    # Annotate receipt with governance metadata
    receipt.policy_decision = f"GOVERNANCE_{change_type}"
    receipt.policy_rule_id = change_id or f"GOV-{change_type}"
    receipt.risk_score = 0.0
    receipt.risk_level = "GOVERNANCE"
    receipt = rehash_receipt(receipt)

    # Append to ledger
    ledger_entry = ledger_module.append(receipt, state)

    # Persist to data store
    data_store.write_receipt(
        receipt,
        risk_score=0.0,
        risk_level="GOVERNANCE",
        policy_rule_id=receipt.policy_rule_id,
        policy_decision=receipt.policy_decision,
        connector_id="governance",
    )
    data_store.write_ledger_entry(ledger_entry)

    logger.info(
        "Governance change recorded in ledger: %s %s → %s (change_id=%s, receipt=%s, ledger=%s)",
        change_type, old_version, new_version,
        change_id, receipt.receipt_id, ledger_entry.ledger_entry_id,
    )

    return {
        "receipt": receipt,
        "ledger_entry": ledger_entry,
    }
