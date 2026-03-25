"""
RIO Runtime — Governed Corpus Schema

Defines the CorpusRecord structure and validation helpers.

A CorpusRecord is a comprehensive snapshot of a single governed request,
combining data from every pipeline stage:
    request + intent + policy/risk + authorization + execution + receipt + ledger

The corpus is the system's structured decision history, used for:
    - Audit review
    - Policy testing via replay
    - Risk threshold tuning
    - Governance learning

Spec reference: /spec/governed_execution_protocol.md
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CorpusRecord:
    """
    A single governed corpus record — full snapshot of a completed request.

    Fields are derived from every pipeline stage:
        Intake → Classification → Intent → Policy/Risk → Authorization →
        Execution → Receipt → Ledger
    """
    # --- Identity ---
    corpus_id: str = field(default_factory=lambda: f"CORP-{uuid.uuid4().hex[:8].upper()}")
    request_id: str = ""
    intent_id: str = ""

    # --- Actor ---
    requested_by: str = ""
    requester_role: str = ""

    # --- Action ---
    action_type: str = ""
    target_resource: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    justification: str = ""

    # --- Policy & Risk ---
    risk_score: float = 0.0
    risk_level: str = ""
    policy_decision: str = ""
    policy_rule_id: str = ""
    policy_reason: str = ""

    # --- Authorization ---
    authorization_id: str = ""
    approved_by: str = ""
    approver_role: str = ""
    authority_scope: str = ""

    # --- Execution ---
    execution_status: str = ""
    adapter_id: str = ""
    external_reference: str = ""

    # --- Receipt ---
    receipt_id: str = ""
    receipt_hash: str = ""
    receipt_signature: str = ""

    # --- Ledger ---
    ledger_entry_id: str = ""
    ledger_hash: str = ""

    # --- Timestamps ---
    request_timestamp: int = 0
    execution_timestamp: int = 0
    corpus_timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    # --- Outcome ---
    outcome_summary: str = ""
    pipeline_duration_ms: int = 0
    stages_completed: List[str] = field(default_factory=list)


def to_dict(record: CorpusRecord) -> Dict[str, Any]:
    """Serialize a CorpusRecord to a dictionary for JSONL persistence."""
    return {
        "corpus_id": record.corpus_id,
        "request_id": record.request_id,
        "intent_id": record.intent_id,
        "requested_by": record.requested_by,
        "requester_role": record.requester_role,
        "action_type": record.action_type,
        "target_resource": record.target_resource,
        "parameters": record.parameters,
        "justification": record.justification,
        "risk_score": record.risk_score,
        "risk_level": record.risk_level,
        "policy_decision": record.policy_decision,
        "policy_rule_id": record.policy_rule_id,
        "policy_reason": record.policy_reason,
        "authorization_id": record.authorization_id,
        "approved_by": record.approved_by,
        "approver_role": record.approver_role,
        "authority_scope": record.authority_scope,
        "execution_status": record.execution_status,
        "adapter_id": record.adapter_id,
        "external_reference": record.external_reference,
        "receipt_id": record.receipt_id,
        "receipt_hash": record.receipt_hash,
        "receipt_signature": record.receipt_signature,
        "ledger_entry_id": record.ledger_entry_id,
        "ledger_hash": record.ledger_hash,
        "request_timestamp": record.request_timestamp,
        "execution_timestamp": record.execution_timestamp,
        "corpus_timestamp": record.corpus_timestamp,
        "outcome_summary": record.outcome_summary,
        "pipeline_duration_ms": record.pipeline_duration_ms,
        "stages_completed": record.stages_completed,
    }


def from_dict(data: Dict[str, Any]) -> CorpusRecord:
    """Deserialize a dictionary to a CorpusRecord."""
    record = CorpusRecord()
    for key, value in data.items():
        if hasattr(record, key):
            setattr(record, key, value)
    return record


def validate_record(record: CorpusRecord) -> List[str]:
    """
    Validate a corpus record for completeness.

    Returns a list of validation errors (empty list = valid).
    """
    errors = []

    if not record.request_id:
        errors.append("Missing request_id")
    if not record.intent_id:
        errors.append("Missing intent_id")
    if not record.action_type:
        errors.append("Missing action_type")
    if not record.requested_by:
        errors.append("Missing requested_by")
    if not record.policy_decision:
        errors.append("Missing policy_decision")
    if not record.execution_status:
        errors.append("Missing execution_status")
    if not record.receipt_id:
        errors.append("Missing receipt_id")
    if not record.ledger_entry_id:
        errors.append("Missing ledger_entry_id")
    if record.request_timestamp == 0:
        errors.append("Missing request_timestamp")

    return errors
