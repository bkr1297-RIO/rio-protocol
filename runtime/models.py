"""
RIO Runtime — Data Models

Defines the core data structures that flow through the Governed Execution Protocol.
These models correspond to the schemas defined in /spec/canonical_intent_schema.json,
/spec/authorization_token_schema.json, /spec/receipt_schema.json, and
/spec/ledger_entry_schema.json.

Each model is a dataclass with typed fields. In a production implementation,
these would include serialization, validation, and canonical hashing methods.
"""

from __future__ import annotations

import uuid
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class RiskCategory(Enum):
    """Risk classification levels assigned during the Classification stage."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Decision(Enum):
    """Authorization and policy decision outcomes."""
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


class ExecutionStatus(Enum):
    """Execution outcome states recorded in receipts."""
    EXECUTED = "EXECUTED"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"
    KILL_SWITCH_BLOCKED = "KILL_SWITCH_BLOCKED"
    PENDING_APPROVAL = "PENDING_APPROVAL"


class IntentStatus(Enum):
    """Lifecycle states for a canonical intent."""
    PENDING = "pending"
    VALIDATED = "validated"
    DENIED = "denied"
    APPROVED = "approved"
    EXECUTED = "executed"
    PENDING_APPROVAL = "pending_approval"


# ---------------------------------------------------------------------------
# Request (Intake output)
# ---------------------------------------------------------------------------

@dataclass
class Request:
    """
    Raw incoming request registered at the Intake stage.

    Produced by: Stage 1 — Intake
    Consumed by: Stage 2 — Classification
    """
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = ""
    raw_input: dict[str, Any] = field(default_factory=dict)
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    nonce: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_ip: str = ""
    authenticated: bool = False


# ---------------------------------------------------------------------------
# Classification Result (Classification output)
# ---------------------------------------------------------------------------

@dataclass
class ClassificationResult:
    """
    Classification output assigning action type and risk domain.

    Produced by: Stage 2 — Classification
    Consumed by: Stage 3 — Intent Validation / Structured Intent
    """
    request_id: str = ""
    action_type: str = ""
    domain: str = ""
    risk_category: RiskCategory = RiskCategory.MEDIUM


# ---------------------------------------------------------------------------
# Intent (Structured Intent output)
# ---------------------------------------------------------------------------

@dataclass
class Intent:
    """
    Canonical structured intent conforming to the Canonical Intent Schema.

    Produced by: Stage 4 — Structured Intent
    Consumed by: Stage 5 — Policy & Risk, Stage 6 — Authorization, Stage 7 — Execution Gate
    """
    intent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    action_type: str = ""
    target_resource: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    requested_by: str = ""
    justification: str = ""
    risk_category: RiskCategory = RiskCategory.MEDIUM
    required_approvals: list[str] = field(default_factory=list)
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    status: IntentStatus = IntentStatus.PENDING


# ---------------------------------------------------------------------------
# Policy & Risk Result
# ---------------------------------------------------------------------------

@dataclass
class PolicyRiskResult:
    """
    Output of the Policy & Risk evaluation stage.

    Produced by: Stage 5 — Policy & Risk
    Consumed by: Stage 6 — Authorization
    """
    intent_id: str = ""
    decision: Decision = Decision.DENY
    risk_score: float = 0.0
    risk_level: str = ""
    policy_rule_id: str = ""
    policy_ids: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    reason: str = ""


# ---------------------------------------------------------------------------
# Authorization Token
# ---------------------------------------------------------------------------

@dataclass
class Authorization:
    """
    Authorization decision and token issued at the Authorization stage.

    Produced by: Stage 6 — Authorization
    Consumed by: Stage 7 — Execution Gate
    """
    authorization_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent_id: str = ""
    decision: Decision = Decision.DENY
    approver_id: str = ""
    approval_timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    expiration_timestamp: int = 0
    single_use: bool = True
    signature: str = ""
    # IAM enrichment fields
    approver_role: str = ""
    authority_scope: str = ""


# ---------------------------------------------------------------------------
# Receipt
# ---------------------------------------------------------------------------

@dataclass
class Receipt:
    """
    Cryptographic receipt generated after execution or denial.

    Produced by: Stage 8 — Receipt
    Consumed by: Stage 9 — Ledger, Governed Corpus
    """
    receipt_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = ""
    intent_id: str = ""
    authorization_id: str = ""
    decision: Decision = Decision.DENY
    action_type: str = ""
    execution_status: ExecutionStatus = ExecutionStatus.BLOCKED
    execution_timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    risk_score: float = 0.0
    risk_level: str = ""
    policy_rule_id: str = ""
    policy_decision: str = ""
    result_hash: str = ""
    previous_receipt_hash: str = ""
    receipt_hash: str = ""
    signature: str = ""


# ---------------------------------------------------------------------------
# Ledger Entry
# ---------------------------------------------------------------------------

@dataclass
class LedgerEntry:
    """
    Append-only ledger entry linking a receipt into the hash chain.

    Produced by: Stage 9 — Ledger
    Consumed by: Auditors, Governed Corpus, Cross-domain verification

    The entry_hash is computed as:
        SHA-256(entry_id + receipt_id + receipt_hash + request_id + intent_id +
                authorization_id + decision + action + result_hash +
                receipt_signature + previous_hash + timestamp)
    """
    ledger_entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    receipt_id: str = ""
    receipt_hash: str = ""
    previous_ledger_hash: str = ""
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    ledger_signature: str = ""
    ledger_hash: str = ""
    # Enhanced fields for full hash chain coverage
    request_id: str = ""
    intent_id: str = ""
    authorization_id: str = ""
    decision: str = ""
    action: str = ""
    result_hash: str = ""
    receipt_signature: str = ""
    # IAM enrichment fields
    requested_by: str = ""
    approved_by: str = ""
    requester_role: str = ""
    approver_role: str = ""
    authority_scope: str = ""
