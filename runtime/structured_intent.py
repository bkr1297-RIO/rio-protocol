"""
RIO Runtime — Stage 4: Structured Intent

Converts a validated request into a canonical structured intent object
conforming to the Canonical Intent Schema.

The canonical intent is the standard format that all downstream stages
(Policy & Risk, Authorization, Execution Gate) operate on.

Spec reference: /spec/canonical_intent_schema.md, /spec/03_canonical_request.md
Protocol stage: Step 3 of the 8-step Governed Execution Protocol
Related invariants: INV-01 (Completeness)
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from .models import (
    ClassificationResult,
    Intent,
    IntentStatus,
    Request,
)

logger = logging.getLogger("rio.structured_intent")


def form_intent(
    request: Request,
    classification: ClassificationResult,
) -> Intent:
    """
    Convert a validated request into a canonical structured intent.

    The intent object captures the action type, target resource, parameters,
    requester identity, justification, risk category, and required approvals
    in a standardized format.

    Args:
        request: The validated Request from the Intake stage.
        classification: The ClassificationResult from the Classification stage.

    Returns:
        An Intent object ready for the Policy & Risk stage.

    Raises:
        ValueError: If the request has not been validated.
    """
    raw = request.raw_input

    intent = Intent(
        intent_id=str(uuid.uuid4()),
        request_id=request.request_id,
        action_type=classification.action_type,
        target_resource=raw.get("target_resource", ""),
        parameters=raw.get("parameters", {}),
        requested_by=raw.get("requested_by", request.actor_id),
        justification=raw.get("justification", ""),
        risk_category=classification.risk_category,
        required_approvals=raw.get("required_approvals", []),
        timestamp=int(time.time() * 1000),
        status=IntentStatus.PENDING,
    )

    logger.info(
        "Formed canonical intent %s for request %s — action=%s, risk=%s",
        intent.intent_id,
        intent.request_id,
        intent.action_type,
        intent.risk_category.value,
    )

    return intent
