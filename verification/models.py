"""
Data models for the RIO Independent Verifier.

All models are defined from scratch — zero imports from the reference implementation.
"""

from dataclasses import dataclass, field
from typing import Any

# ── Protocol Constants ──────────────────────────────────────────────────────

GENESIS_HASH = "901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a"

VALID_DECISIONS = frozenset({"allow", "modify", "block", "escalate"})

VALID_SIGNATURE_ALGORITHMS = frozenset({"Ed25519"})

SIGNED_FIELDS_19 = (
    "receipt_version",
    "receipt_id",
    "timestamp",
    "runtime_id",
    "runtime_version",
    "environment",
    "request_summary",
    "request_hash",
    "request_canonical_payload",
    "policy_bundle_id",
    "policy_bundle_hash",
    "decision",
    "decision_reason_codes",
    "invariant_results",
    "threshold_results",
    "model_output_hash",
    "model_output_preview",
    "prev_ledger_hash",
    "public_key_fingerprint",
)

COMPUTED_FIELDS_3 = (
    "receipt_hash",
    "signature_algorithm",
    "signature",
)

ALL_REQUIRED_FIELDS = SIGNED_FIELDS_19 + COMPUTED_FIELDS_3  # 22 total


# ── Verification Result Models ──────────────────────────────────────────────

@dataclass
class CheckResult:
    """Result of a single verification check."""
    check_name: str
    number: int
    passed: bool
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "check_name": self.check_name,
            "number": self.number,
            "passed": self.passed,
            "details": self.details,
        }


@dataclass
class ReceiptVerificationResult:
    """Aggregate result of all 7 receipt verification checks."""
    receipt_id: str
    all_passed: bool
    checks: list[CheckResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "receipt_id": self.receipt_id,
            "all_passed": self.all_passed,
            "checks": [c.to_dict() for c in self.checks],
        }

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class LedgerFailure:
    """A single ledger verification failure."""
    entry_index: int
    check_name: str
    details: str

    def to_dict(self) -> dict:
        return {
            "entry_index": self.entry_index,
            "check_name": self.check_name,
            "details": self.details,
        }


@dataclass
class LedgerVerificationResult:
    """Aggregate result of all 4 ledger verification checks."""
    chain_intact: bool
    entries_verified: int
    entries_total: int
    failures: list[LedgerFailure] = field(default_factory=list)
    details: str = ""

    def to_dict(self) -> dict:
        return {
            "chain_intact": self.chain_intact,
            "entries_verified": self.entries_verified,
            "entries_total": self.entries_total,
            "failures": [f.to_dict() for f in self.failures],
            "details": self.details,
        }

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)
