"""
RIO Runtime — Stage 4: Policy & Risk Check

Evaluates the canonical intent against the Policy Engine and Risk Engine.
Combines their results to produce a final recommendation for authorization.

The Policy Engine evaluates structured rules (policy_rules.json).
The Risk Engine computes a numeric risk score (risk_rules.json).

The combined decision logic:
- If policy says DENY → final decision is DENY.
- If policy says REQUIRE_APPROVAL → final decision is ESCALATE.
- If risk level is HIGH → final decision is ESCALATE (unless policy already denied).
- Otherwise → final decision is ALLOW.

Spec reference: /spec/05_policy_constraints.md
Protocol stage: Step 4 of the 8-step Governed Execution Protocol
Related invariants: INV-01 (Completeness), INV-06 (No Self-Authorization)
"""

from __future__ import annotations

import logging
from typing import Any

from .models import Decision, Intent, PolicyRiskResult, RiskCategory
from .policy.policy_engine import evaluate_policy
from .policy.risk_engine import compute_risk

logger = logging.getLogger("rio.policy_risk")


def evaluate(intent: Intent, role: str = "employee") -> PolicyRiskResult:
    """
    Evaluate the canonical intent against policy rules and risk models.

    Processing:
    1. Call the Risk Engine to compute risk score and risk level.
    2. Call the Policy Engine to evaluate policy rules.
    3. Combine results to produce a final decision.

    Args:
        intent: The canonical Intent from the Structured Intent stage.
        role: The requester's role (used by both engines).

    Returns:
        A PolicyRiskResult containing the combined decision, risk score,
        risk level, policy rule ID, and reason.
    """
    # Step 1: Compute risk score
    risk_result = compute_risk(
        action_type=intent.action_type,
        parameters=intent.parameters,
        role=role,
        target_resource=intent.target_resource,
    )

    # Step 2: Evaluate policy rules
    policy_decision = evaluate_policy(
        action_type=intent.action_type,
        parameters=intent.parameters,
        role=role,
    )

    # Step 3: Combine results
    policy_ids: list[str] = [policy_decision.policy_rule_id]
    constraints: dict[str, Any] = {}

    # Add required approvals from intent if present
    if intent.required_approvals:
        constraints["required_approvals"] = intent.required_approvals

    # Determine final decision
    if policy_decision.decision == "DENY":
        # Policy explicitly denies — final is DENY
        decision = Decision.DENY
        reason = f"Policy DENY: {policy_decision.reason}"
    elif policy_decision.decision == "REQUIRE_APPROVAL":
        # Policy requires approval — final is ESCALATE
        decision = Decision.ESCALATE
        reason = f"Policy REQUIRE_APPROVAL: {policy_decision.reason}"
    elif risk_result.risk_level == "HIGH":
        # High risk — escalate even if policy allows
        decision = Decision.ESCALATE
        reason = (
            f"Risk level HIGH (score={risk_result.risk_score:.1f}) — "
            f"escalation required despite policy {policy_decision.decision}"
        )
        policy_ids.append("RISK-HIGH-ESCALATE")
    else:
        # Policy allows and risk is acceptable
        decision = Decision.ALLOW
        reason = (
            f"Policy ALLOW ({policy_decision.reason}), "
            f"risk {risk_result.risk_level} (score={risk_result.risk_score:.1f})"
        )

    # Add risk components to constraints for downstream visibility
    constraints["risk_components"] = risk_result.components

    result = PolicyRiskResult(
        intent_id=intent.intent_id,
        decision=decision,
        risk_score=risk_result.risk_score,
        risk_level=risk_result.risk_level,
        policy_rule_id=policy_decision.policy_rule_id,
        policy_ids=policy_ids,
        constraints=constraints,
        reason=reason,
    )

    logger.info(
        "Policy & Risk for intent %s: decision=%s, risk_score=%.1f, "
        "risk_level=%s, policy_rule=%s, reason=%s",
        intent.intent_id,
        result.decision.value,
        result.risk_score,
        result.risk_level,
        result.policy_rule_id,
        result.reason,
    )

    return result
