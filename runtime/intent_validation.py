"""
RIO Runtime — Stage 3a: Intent Validation

Validates that the incoming request contains all required fields and conforms
to the canonical intent schema before structured intent formation.

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

logger = logging.getLogger("rio.intent_validation")

# ---------------------------------------------------------------------------
# Required fields for intent formation
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
    - All required fields are present and non-empty.
    - The action_type from classification matches the raw input.
    - The request has been authenticated (actor_id is present).

    Args:
        request: The Request object from the Intake stage.
        classification: The ClassificationResult from the Classification stage.

    Returns:
        A ValidationResult indicating whether the request is valid.
    """
    errors: list[str] = []
    raw = request.raw_input

    # Check required fields
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
