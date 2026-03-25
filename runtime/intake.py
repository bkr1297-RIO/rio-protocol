"""
RIO Runtime — Stage 1: Intake

Registers incoming requests, assigns a unique request_id, records the timestamp
and caller identity, and passes the request to the Classification stage.

Spec reference: /spec/01_intake_protocol.md
Protocol stage: Step 1 of the 8-step Governed Execution Protocol
Related invariants: INV-01 (Completeness)
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from .models import Request

logger = logging.getLogger("rio.intake")


def register_request(
    actor_id: str,
    raw_input: dict[str, Any],
    source_ip: str = "",
    authenticated: bool = False,
) -> Request:
    """
    Register an incoming request at the Intake stage.

    Every request that enters the system receives a unique request_id, a
    timestamp, and a cryptographic nonce. The raw input is preserved without
    modification for downstream processing.

    Args:
        actor_id: Identity of the requesting actor (human, agent, or system).
        raw_input: The unmodified request payload.
        source_ip: Source IP address of the request (for audit).
        authenticated: Whether the actor's identity has been verified.

    Returns:
        A Request object ready for the Classification stage.

    Raises:
        ValueError: If actor_id is empty or raw_input is empty.
    """
    if not actor_id:
        raise ValueError("Intake requires a non-empty actor_id")
    if not raw_input:
        raise ValueError("Intake requires a non-empty raw_input")

    request = Request(
        request_id=str(uuid.uuid4()),
        actor_id=actor_id,
        raw_input=raw_input,
        timestamp=int(time.time() * 1000),
        nonce=str(uuid.uuid4()),
        source_ip=source_ip,
        authenticated=authenticated,
    )

    logger.info(
        "Intake registered request %s from actor %s at %d",
        request.request_id,
        request.actor_id,
        request.timestamp,
    )

    return request
