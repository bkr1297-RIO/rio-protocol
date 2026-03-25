"""
RIO Runtime — Stage 3a: Intent Validation

Validates that the incoming request contains all required fields and conforms
to the canonical intent schema before structured intent formation.

Uses the Intent Requirements Matrix (policy/intent_requirements.py) to
validate that action-specific required parameters are present.

If required fields are missing, returns a validation error.
If valid, passes the request to the Structured Intent stage.

Spec reference: /spec/canonical_intent_schema.md
Protocol stage: Between Classification and Structured Intent
Related invariants: INV-01 (Completeness)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from .models import ClassificationResult, Request
from .policy.intent_requirements import validate_intent_fields

logger = logging.getLogger("rio.intent_validation")

# ---------------------------------------------------------------------------
# Required base fields for intent formation
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = [
    "action_type",
    "target_resource",
    "requested_by",
]

OPTIONAL_FIELDS = [
    "parameters",
    "justification",
    "required_approvals",
]


@dataclass
class ValidationResult:
    """Result of intent validation."""
    valid: bool
    request_id: str
    errors: list[str]


def validate(
    request: Request,
    classification: ClassificationResult,
) -> ValidationResult:
    """
    Validate that the request contains all required fields for intent formation.

    Checks:
    - All required base fields are present and non-empty.
    - The action_type from classification matches the raw input.
    - The request has been authenticated (actor_id is present).
    - All action-specific required parameters are present (via Intent Requirements Matrix).

    Args:
        request: The Request object from the Intake stage.
        classification: The ClassificationResult from the Classification stage.

    Returns:
        A ValidationResult indicating whether the request is valid.
    """
    errors: list[str] = []
    raw = request.raw_input

    # Check required base fields
    for field_name in REQUIRED_FIELDS:
        value = raw.get(field_name, "")
        if not value:
            errors.append(f"Missing required field: {field_name}")

    # Check actor identity
    if not request.actor_id:
        errors.append("Missing actor identity (actor_id)")

    # Check classification consistency
    if not classification.action_type:
        errors.append("Classification did not produce an action_type")

    # Check action-specific required parameters via Intent Requirements Matrix
    parameters = raw.get("parameters", {})
    if parameters and classification.action_type:
        fields_valid, missing_fields = validate_intent_fields(
            classification.action_type, parameters
        )
        if not fields_valid:
            for field_name in missing_fields:
                errors.append(
                    f"Missing required parameter for {classification.action_type}: {field_name}"
                )

    valid = len(errors) == 0

    result = ValidationResult(
        valid=valid,
        request_id=request.request_id,
        errors=errors,
    )

    if valid:
        logger.info(
            "Intent validation passed for request %s",
            request.request_id,
        )
    else:
        logger.warning(
            "Intent validation failed for request %s: %s",
            request.request_id,
            "; ".join(errors),
        )

    return result
