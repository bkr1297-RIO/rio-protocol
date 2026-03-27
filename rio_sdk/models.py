"""
RIO SDK — Data Models

Typed data classes for all protocol artifacts:
    Intent, Receipt, EvaluateResult, GovernorSubmission,
    LedgerEntry, GateExecuteResult, VerificationResult, VerificationCheck
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Intent:
    """A structured intent ready for submission to the governance gateway."""
    intent: str
    source: str
    timestamp: str
    intent_id: str
    signature: str
    execution_token: str
    model: str
    nonce: str
    public_key_b64: str
    public_key_hex: str
    parameters_hash: str
    context: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = {
            "intent": self.intent,
            "source": self.source,
            "timestamp": self.timestamp,
            "intent_id": self.intent_id,
            "signature": self.signature,
            "execution_token": self.execution_token,
            "model": self.model,
            "nonce": self.nonce,
            "public_key_b64": self.public_key_b64,
            "public_key_hex": self.public_key_hex,
            "parameters_hash": self.parameters_hash,
        }
        if self.context:
            d["context"] = self.context
        if self.metadata:
            d["metadata"] = self.metadata
        return d


@dataclass
class Receipt:
    """A cryptographically signed receipt from the governance gateway."""
    receipt_version: str
    receipt_id: str
    timestamp: str
    runtime_id: str
    runtime_version: str
    environment: str
    request_summary: str
    request_hash: str
    request_canonical_payload: str
    policy_bundle_id: str
    policy_bundle_hash: str
    decision: str
    decision_reason_codes: list
    invariant_results: dict
    threshold_results: dict
    model_output_hash: str
    model_output_preview: str
    prev_ledger_hash: str
    public_key_fingerprint: str
    receipt_hash: str
    signature_algorithm: str
    signature: str

    # Convenience fields (not part of the signed payload)
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> Receipt:
        return cls(
            receipt_version=data.get("receipt_version", ""),
            receipt_id=data.get("receipt_id", ""),
            timestamp=data.get("timestamp", ""),
            runtime_id=data.get("runtime_id", ""),
            runtime_version=data.get("runtime_version", ""),
            environment=data.get("environment", ""),
            request_summary=data.get("request_summary", ""),
            request_hash=data.get("request_hash", ""),
            request_canonical_payload=data.get("request_canonical_payload", ""),
            policy_bundle_id=data.get("policy_bundle_id", ""),
            policy_bundle_hash=data.get("policy_bundle_hash", ""),
            decision=data.get("decision", ""),
            decision_reason_codes=data.get("decision_reason_codes", []),
            invariant_results=data.get("invariant_results", {}),
            threshold_results=data.get("threshold_results", {}),
            model_output_hash=data.get("model_output_hash", ""),
            model_output_preview=data.get("model_output_preview", ""),
            prev_ledger_hash=data.get("prev_ledger_hash", ""),
            public_key_fingerprint=data.get("public_key_fingerprint", ""),
            receipt_hash=data.get("receipt_hash", ""),
            signature_algorithm=data.get("signature_algorithm", ""),
            signature=data.get("signature", ""),
            raw=data,
        )

    @property
    def signed_fields(self) -> dict:
        """Return the 19 fields that are included in the signed payload."""
        return {
            "receipt_version": self.receipt_version,
            "receipt_id": self.receipt_id,
            "timestamp": self.timestamp,
            "runtime_id": self.runtime_id,
            "runtime_version": self.runtime_version,
            "environment": self.environment,
            "request_summary": self.request_summary,
            "request_hash": self.request_hash,
            "request_canonical_payload": self.request_canonical_payload,
            "policy_bundle_id": self.policy_bundle_id,
            "policy_bundle_hash": self.policy_bundle_hash,
            "decision": self.decision,
            "decision_reason_codes": self.decision_reason_codes,
            "invariant_results": self.invariant_results,
            "threshold_results": self.threshold_results,
            "model_output_hash": self.model_output_hash,
            "model_output_preview": self.model_output_preview,
            "prev_ledger_hash": self.prev_ledger_hash,
            "public_key_fingerprint": self.public_key_fingerprint,
        }


@dataclass
class VerificationCheck:
    """A single verification check result."""
    name: str
    passed: bool
    detail: str = ""
    stored: str = ""
    computed: str = ""


@dataclass
class VerificationResult:
    """Result of the 7-check receipt verification."""
    overall: str  # "PASS" or "FAIL"
    checks: list[VerificationCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.overall == "PASS"

    @property
    def summary(self) -> str:
        n_pass = sum(1 for c in self.checks if c.passed)
        return f"{n_pass}/{len(self.checks)} checks passed"


@dataclass
class EvaluateResult:
    """Result from POST /v1/governance/evaluate."""
    receipt: Receipt
    decision: str
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> EvaluateResult:
        receipt_data = data.get("receipt", data)
        return cls(
            receipt=Receipt.from_dict(receipt_data),
            decision=data.get("decision", receipt_data.get("decision", "")),
            raw=data,
        )


@dataclass
class GovernorSubmission:
    """Result from POST /v1/governor/submit — AWAITING_HUMAN_SIGNATURE."""
    submission_id: str
    status: str  # "AWAITING_HUMAN_SIGNATURE"
    approval_token: str = ""
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> GovernorSubmission:
        return cls(
            submission_id=data.get("submission_id", data.get("id", "")),
            status=data.get("status", ""),
            approval_token=data.get("approval_token", ""),
            raw=data,
        )


@dataclass
class LedgerEntry:
    """A single entry in the governance ledger."""
    id: int = 0
    action: str = ""
    agent: str = ""
    approver: str = ""
    executed_by: str = ""
    intent_id: str = ""
    parameters_hash: str = ""
    result: str = ""
    reason: str = ""
    receipt_hash: str = ""
    prev_hash: str = ""
    entry_hash: str = ""
    timestamp: str = ""
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> LedgerEntry:
        return cls(
            id=data.get("id", 0),
            action=data.get("action", ""),
            agent=data.get("agent", ""),
            approver=data.get("approver", ""),
            executed_by=data.get("executed_by", ""),
            intent_id=data.get("intent_id", ""),
            parameters_hash=data.get("parameters_hash", ""),
            result=data.get("result", ""),
            reason=data.get("reason", ""),
            receipt_hash=data.get("receipt_hash", ""),
            prev_hash=data.get("prev_hash", ""),
            entry_hash=data.get("entry_hash", ""),
            timestamp=data.get("timestamp", ""),
            raw=data,
        )


@dataclass
class GateExecuteResult:
    """Result from POST /api/gate/execute."""
    status: str
    receipt_hash: str = ""
    response: str = ""
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> GateExecuteResult:
        return cls(
            status=data.get("status", ""),
            receipt_hash=data.get("receipt_hash", ""),
            response=data.get("response", ""),
            raw=data,
        )
