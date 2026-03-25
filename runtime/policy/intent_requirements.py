"""
RIO Runtime — Intent Requirements Matrix

Defines the required fields per action type. The intent validation stage
uses this matrix to verify that all mandatory parameters are present
before the intent enters the policy and risk evaluation pipeline.

If a required field is missing, the validation stage must fail the request
and produce a receipt recording the validation failure.

Spec reference: /spec/canonical_intent_schema.md
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Intent Requirements Matrix
#
# Maps each action_type to the list of parameter keys that MUST be present
# in the intent's parameters dict. If an action_type is not listed here,
# no parameter-level validation is enforced (only the base schema fields
# are checked).
# ---------------------------------------------------------------------------

INTENT_REQUIREMENTS: dict[str, list[str]] = {
    "send_email": ["recipient", "subject", "body"],
    "transfer_funds": ["amount", "currency", "recipient", "source_account"],
    "create_event": ["title", "time", "duration"],
    "delete_data": ["dataset", "scope", "approval_authority"],
    "deploy_code": ["repository", "branch", "environment"],
    "grant_access": ["target_user", "resource", "permission_level"],
    "read_data": ["dataset"],
    "update_config": ["config_key", "config_value"],
}


def get_required_fields(action_type: str) -> list[str]:
    """
    Return the list of required parameter fields for the given action type.

    Args:
        action_type: The classified action type string.

    Returns:
        A list of required field names. Empty list if no requirements defined.
    """
    return INTENT_REQUIREMENTS.get(action_type, [])


def validate_intent_fields(action_type: str, parameters: dict) -> tuple[bool, list[str]]:
    """
    Validate that all required fields are present in the parameters.

    Args:
        action_type: The classified action type string.
        parameters: The intent's parameters dict.

    Returns:
        A tuple of (is_valid, missing_fields).
        is_valid is True if all required fields are present.
        missing_fields lists any fields that are absent.
    """
    required = get_required_fields(action_type)
    missing = [f for f in required if f not in parameters or parameters[f] is None]
    return (len(missing) == 0, missing)
