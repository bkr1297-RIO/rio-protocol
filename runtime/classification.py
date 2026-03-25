"""
RIO Runtime — Stage 2: Classification

Determines the action_type and risk_category for an incoming request.
Passes the classification result to the Intent Validation stage.

Spec reference: /spec/04_risk_evaluation.md
Protocol stage: Step 2 of the 8-step Governed Execution Protocol
Related invariants: INV-01 (Completeness)
"""

from __future__ import annotations

import logging
from typing import Any

from .models import ClassificationResult, Request, RiskCategory

logger = logging.getLogger("rio.classification")

# ---------------------------------------------------------------------------
# Default classification rules (reference skeleton)
# In production, these would be loaded from the policy engine or risk model.
# ---------------------------------------------------------------------------

DEFAULT_RISK_RULES: dict[str, RiskCategory] = {
    "transfer_funds": RiskCategory.HIGH,
    "delete_data": RiskCategory.CRITICAL,
    "send_email": RiskCategory.MEDIUM,
    "deploy_code": RiskCategory.HIGH,
    "grant_access": RiskCategory.CRITICAL,
    "read_data": RiskCategory.LOW,
    "update_config": RiskCategory.MEDIUM,
}


def classify(request: Request) -> ClassificationResult:
    """
    Classify the incoming request into an action type and risk domain.

    The classification stage examines the raw input to determine:
    - action_type: What kind of action is being requested.
    - domain: The system or resource domain involved.
    - risk_category: Preliminary risk level (LOW, MEDIUM, HIGH, CRITICAL).

    Args:
        request: The Request object from the Intake stage.

    Returns:
        A ClassificationResult ready for the Intent Validation stage.

    Raises:
        ValueError: If the request contains no classifiable action.
    """
    raw = request.raw_input

    # Extract action type from raw input
    action_type = raw.get("action_type", raw.get("action", ""))
    if not action_type:
        raise ValueError(
            f"Classification failed for request {request.request_id}: "
            "no action_type found in raw input"
        )

    # Extract domain from raw input
    domain = raw.get("domain", raw.get("target_resource", "unknown"))

    # Determine risk category
    risk_category = DEFAULT_RISK_RULES.get(action_type, RiskCategory.MEDIUM)

    result = ClassificationResult(
        request_id=request.request_id,
        action_type=action_type,
        domain=domain,
        risk_category=risk_category,
    )

    logger.info(
        "Classified request %s as action_type=%s, domain=%s, risk=%s",
        request.request_id,
        result.action_type,
        result.domain,
        result.risk_category.value,
    )

    return result
