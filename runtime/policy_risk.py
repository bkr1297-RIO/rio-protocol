"""
RIO Runtime — Stage 5: Policy & Risk Check

Evaluates the canonical intent against active policy rules and risk models.
Produces a policy decision (ALLOW, DENY, ESCALATE), a risk score, and any
constraints that must be enforced during execution.

Spec reference: /spec/05_policy_constraints.md
Protocol stage: Step 4 of the 8-step Governed Execution Protocol
Related invariants: INV-01 (Completeness), INV-06 (No Self-Authorization)
"""

from __future__ import annotations

import logging
from typing import Any

from .models import Decision, Intent, PolicyRiskResult, RiskCategory

logger = logging.getLogger("rio.policy_risk")

# ---------------------------------------------------------------------------
# Default policy rules (reference skeleton)
# In production, these would be loaded from a versioned policy store.
# ---------------------------------------------------------------------------

RISK_SCORE_MAP: dict[RiskCategory, float] = {
    RiskCategory.LOW: 0.1,
    RiskCategory.MEDIUM: 0.4,
    RiskCategory.HIGH: 0.7,
    RiskCategory.CRITICAL: 0.95,
}

DENY_THRESHOLD = 0.9
ESCALATE_THRESHOLD = 0.6


def evaluate(intent: Intent) -> PolicyRiskResult:
    """
    Evaluate the canonical intent against policy rules and risk models.

    Processing:
    1. Compute a risk score based on the risk category and action type.
    2. Apply policy rules to determine constraints.
    3. Produce a decision: ALLOW, DENY, or ESCALATE.

    Args:
        intent: The canonical Intent from the Structured Intent stage.

    Returns:
        A PolicyRiskResult containing the decision, risk score, and constraints.
    """
    # Compute base risk score
    risk_score = RISK_SCORE_MAP.get(intent.risk_category, 0.5)

    # Apply policy rules (reference skeleton — placeholder logic)
    policy_ids: list[str] = []
    constraints: dict[str, Any] = {}
    reason = ""

    # Check if required approvals are specified
    if intent.required_approvals:
        constraints["required_approvals"] = intent.required_approvals
        policy_ids.append("POL-APPROVAL-REQUIRED")

    # Determine decision based on risk score
    if risk_score >= DENY_THRESHOLD:
        decision = Decision.DENY
        reason = f"Risk score {risk_score:.2f} exceeds deny threshold {DENY_THRESHOLD}"
        policy_ids.append("POL-HIGH-RISK-DENY")
    elif risk_score >= ESCALATE_THRESHOLD:
        decision = Decision.ESCALATE
        reason = f"Risk score {risk_score:.2f} requires escalation"
        policy_ids.append("POL-ESCALATION-REQUIRED")
    else:
        decision = Decision.ALLOW
        reason = f"Risk score {risk_score:.2f} within acceptable range"
        policy_ids.append("POL-STANDARD-ALLOW")

    result = PolicyRiskResult(
        intent_id=intent.intent_id,
        decision=decision,
        risk_score=risk_score,
        policy_ids=policy_ids,
        constraints=constraints,
        reason=reason,
    )

    logger.info(
        "Policy evaluation for intent %s: decision=%s, risk_score=%.2f, reason=%s",
        intent.intent_id,
        result.decision.value,
        result.risk_score,
        result.reason,
    )

    return result
