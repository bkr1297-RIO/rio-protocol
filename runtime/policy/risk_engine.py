"""
RIO Runtime — Risk Engine

Computes a numeric risk score for a canonical intent based on:
- Base risk by action type
- Role risk of the requester
- Amount risk (for financial actions)
- System target risk

Risk rules are loaded from risk_rules.json.

The risk score is mapped to a risk level (LOW, MEDIUM, HIGH) based on
configurable thresholds.

Spec reference: /spec/04_risk_evaluation.md
Related invariants: INV-01 (Completeness)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger("rio.risk_engine")

# ---------------------------------------------------------------------------
# Risk Result
# ---------------------------------------------------------------------------

@dataclass
class RiskResult:
    """Result of a risk evaluation."""
    risk_score: float
    risk_level: str        # LOW | MEDIUM | HIGH
    components: dict[str, float]  # Breakdown of score components


# ---------------------------------------------------------------------------
# Risk Rules Loader
# ---------------------------------------------------------------------------

_RULES_PATH = os.path.join(os.path.dirname(__file__), "risk_rules.json")
_risk_rules_cache: Optional[dict[str, Any]] = None


def _load_risk_rules() -> dict[str, Any]:
    """Load and cache risk rules from risk_rules.json."""
    global _risk_rules_cache
    if _risk_rules_cache is not None:
        return _risk_rules_cache

    with open(_RULES_PATH, "r") as f:
        _risk_rules_cache = json.load(f)

    logger.info("Loaded risk rules from %s", _RULES_PATH)
    return _risk_rules_cache


def reload_rules() -> None:
    """Force reload of risk rules (used after governance updates)."""
    global _risk_rules_cache
    _risk_rules_cache = None
    _load_risk_rules()


# ---------------------------------------------------------------------------
# Risk Score Computation
# ---------------------------------------------------------------------------

def _compute_amount_risk(amount: Optional[float], rules: dict[str, Any]) -> float:
    """Compute the risk contribution from the transaction amount."""
    if amount is None:
        return 0.0

    thresholds = rules.get("amount_thresholds", [])
    for threshold in thresholds:
        t_min = threshold.get("min", 0)
        t_max = threshold.get("max")

        if t_max is None:
            # Open-ended upper bound
            if amount >= t_min:
                return float(threshold.get("risk_add", 0))
        else:
            if t_min <= amount < t_max:
                return float(threshold.get("risk_add", 0))

    return 0.0


def _determine_risk_level(score: float, rules: dict[str, Any]) -> str:
    """Map a numeric risk score to a risk level string."""
    levels = rules.get("risk_levels", {})

    # Check from highest to lowest
    for level_name in ["HIGH", "MEDIUM", "LOW"]:
        level = levels.get(level_name, {})
        if score >= level.get("min", 0):
            return level_name

    return "LOW"


def compute_risk(
    action_type: str,
    parameters: dict[str, Any],
    role: str = "employee",
    target_resource: str = "unknown",
) -> RiskResult:
    """
    Compute the risk score for a canonical intent.

    Risk score = base_risk + role_risk + amount_risk + system_target_risk

    Args:
        action_type: The classified action type.
        parameters: The intent's parameters dict.
        role: The requester's role.
        target_resource: The target system or resource.

    Returns:
        A RiskResult with the total score, risk level, and component breakdown.
    """
    rules = _load_risk_rules()

    # Base risk by action type
    base_risk = float(rules.get("base_risk", {}).get(action_type, 3))

    # Role risk
    role_risk = float(rules.get("role_risk", {}).get(role, 3))

    # Amount risk (if applicable)
    amount = parameters.get("amount")
    if amount is not None:
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = None
    amount_risk = _compute_amount_risk(amount, rules)

    # System target risk
    system_risk = float(
        rules.get("system_target_risk", {}).get(target_resource, 1)
    )

    # Total risk score
    total_score = base_risk + role_risk + amount_risk + system_risk

    # Determine risk level
    risk_level = _determine_risk_level(total_score, rules)

    components = {
        "base_risk": base_risk,
        "role_risk": role_risk,
        "amount_risk": amount_risk,
        "system_target_risk": system_risk,
    }

    result = RiskResult(
        risk_score=total_score,
        risk_level=risk_level,
        components=components,
    )

    logger.info(
        "Risk evaluation: action=%s, role=%s, target=%s — "
        "score=%.1f (base=%.1f + role=%.1f + amount=%.1f + target=%.1f) → %s",
        action_type,
        role,
        target_resource,
        total_score,
        base_risk,
        role_risk,
        amount_risk,
        system_risk,
        risk_level,
    )

    return result
