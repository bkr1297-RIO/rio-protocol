"""
RIO Runtime — Policy Engine

Evaluates whether a canonical intent is allowed, denied, or requires approval
based on structured policy rules loaded from policy_rules.json.

Policy rules are evaluated in priority order (highest priority first).
The first matching rule determines the decision. If no rule matches,
the default decision is ALLOW.

Rule matching considers:
- action_type: Must match the intent's action type.
- role: If specified, must match the requester's role.
- condition: If specified, evaluated against intent parameters.

Spec reference: /spec/05_policy_constraints.md
Related invariants: INV-01 (Completeness), INV-06 (No Self-Authorization)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Optional

logger = logging.getLogger("rio.policy_engine")

# ---------------------------------------------------------------------------
# Policy Decision
# ---------------------------------------------------------------------------

@dataclass
class PolicyDecision:
    """Result of a policy evaluation."""
    decision: str          # ALLOW | DENY | REQUIRE_APPROVAL
    reason: str
    policy_rule_id: str    # ID of the matching rule, or "DEFAULT" if none matched


# ---------------------------------------------------------------------------
# Policy Rules Loader
# ---------------------------------------------------------------------------

_RULES_PATH = os.path.join(os.path.dirname(__file__), "policy_rules.json")
_rules_cache: Optional[list[dict[str, Any]]] = None


def _load_rules() -> list[dict[str, Any]]:
    """Load and cache policy rules from policy_rules.json, sorted by priority descending."""
    global _rules_cache
    if _rules_cache is not None:
        return _rules_cache

    with open(_RULES_PATH, "r") as f:
        data = json.load(f)

    rules = data.get("rules", [])
    # Sort by priority descending — higher priority rules evaluated first
    rules.sort(key=lambda r: r.get("priority", 0), reverse=True)
    _rules_cache = rules

    logger.info("Loaded %d policy rules from %s", len(rules), _RULES_PATH)
    return rules


def reload_rules() -> None:
    """Force reload of policy rules (used after governance updates)."""
    global _rules_cache
    _rules_cache = None
    _load_rules()


# ---------------------------------------------------------------------------
# Condition Evaluator
# ---------------------------------------------------------------------------

def _evaluate_condition(condition: str, parameters: dict[str, Any]) -> bool:
    """
    Evaluate a simple condition string against intent parameters.

    Supports:
    - "amount > 1000"
    - "amount <= 1000"
    - "scope == all"

    This is a reference implementation. Production systems should use a
    proper expression evaluator with sandboxing.
    """
    try:
        # Parse simple conditions: "field operator value"
        parts = condition.split()
        if len(parts) != 3:
            logger.warning("Cannot parse condition: %s", condition)
            return False

        field, operator, value = parts

        # Get field value from parameters
        field_value = parameters.get(field)
        if field_value is None:
            return False

        # Try numeric comparison first
        try:
            numeric_value = float(value)
            numeric_field = float(field_value)

            if operator == ">":
                return numeric_field > numeric_value
            elif operator == ">=":
                return numeric_field >= numeric_value
            elif operator == "<":
                return numeric_field < numeric_value
            elif operator == "<=":
                return numeric_field <= numeric_value
            elif operator == "==":
                return numeric_field == numeric_value
            elif operator == "!=":
                return numeric_field != numeric_value
        except (ValueError, TypeError):
            pass

        # String comparison
        str_field = str(field_value)
        str_value = value.strip("'\"")

        if operator == "==":
            return str_field == str_value
        elif operator == "!=":
            return str_field != str_value

        logger.warning("Unsupported operator in condition: %s", condition)
        return False

    except Exception as e:
        logger.error("Error evaluating condition '%s': %s", condition, e)
        return False


# ---------------------------------------------------------------------------
# Policy Evaluation
# ---------------------------------------------------------------------------

def evaluate_policy(
    action_type: str,
    parameters: dict[str, Any],
    role: str = "employee",
) -> PolicyDecision:
    """
    Evaluate the intent against policy rules.

    Rules are evaluated in priority order. The first matching rule determines
    the decision. If no rule matches, the default decision is ALLOW.

    Args:
        action_type: The classified action type.
        parameters: The intent's parameters dict.
        role: The requester's role (e.g., "admin", "manager", "intern").

    Returns:
        A PolicyDecision with the decision, reason, and matching rule ID.
    """
    rules = _load_rules()

    for rule in rules:
        # Check action match
        rule_action = rule.get("action")
        if rule_action and rule_action != action_type:
            continue

        # Check role match (if specified in rule)
        rule_role = rule.get("role")
        if rule_role and rule_role != role:
            continue

        # Check condition (if specified in rule)
        rule_condition = rule.get("condition")
        if rule_condition and not _evaluate_condition(rule_condition, parameters):
            continue

        # Rule matches
        decision = PolicyDecision(
            decision=rule["decision"],
            reason=rule.get("description", f"Matched rule {rule['id']}"),
            policy_rule_id=rule["id"],
        )

        logger.info(
            "Policy evaluation: action=%s, role=%s — matched rule %s → %s (%s)",
            action_type,
            role,
            rule["id"],
            decision.decision,
            decision.reason,
        )
        return decision

    # No rule matched — default ALLOW
    decision = PolicyDecision(
        decision="ALLOW",
        reason="No policy rule matched — default allow",
        policy_rule_id="DEFAULT",
    )

    logger.info(
        "Policy evaluation: action=%s, role=%s — no rule matched → ALLOW (default)",
        action_type,
        role,
    )
    return decision
