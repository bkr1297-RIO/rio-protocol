"""
RIO Runtime — Stage 5: Authorization

Issues authorization decisions based on the policy and risk evaluation.
Generates a signed, single-use authorization token if the decision is ALLOW.

Enforces:
- INV-06: No self-authorization (requester != approver).
- INV-08: If kill switch is ON, authorization cannot issue ALLOW.

Tokens are stored in state.token_registry for tracking.

Spec reference: /spec/06_authorization.md, /spec/15_time_bound_authorization.md
Protocol stage: Step 5 of the 8-step Governed Execution Protocol
Related invariants: INV-01 (Completeness), INV-06 (No Self-Authorization), INV-07 (Single-Use), INV-08 (Kill Switch)
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from .invariants import InvariantViolation, check_inv_06_no_self_authorization, check_inv_08_kill_switch
from .models import Authorization, Decision, Intent, IntentStatus, PolicyRiskResult
from .state import SystemState

logger = logging.getLogger("rio.authorization")

# Default token validity period (milliseconds) — 5 minutes
DEFAULT_TOKEN_TTL_MS = 5 * 60 * 1000


def authorize(
    intent: Intent,
    policy_result: PolicyRiskResult,
    approver_id: str,
    state: SystemState,
) -> Authorization:
    """
    Issue an authorization decision for the evaluated intent.

    If the policy decision is ALLOW, a signed single-use authorization token
    is generated and registered in state.token_registry. If DENY or ESCALATE,
    the authorization records the denial.

    Enforces:
    - INV-06: The requester (intent.requested_by) and the approver (approver_id)
      must be distinct identities. AI agents cannot authorize their own requests.
    - INV-08: If kill switch is ON, authorization is forced to DENY regardless
      of the policy decision.

    Args:
        intent: The canonical Intent from the Structured Intent stage.
        policy_result: The PolicyRiskResult from the Policy & Risk stage.
        approver_id: Identity of the actor authorizing (or denying) the request.
        state: The current system state.

    Returns:
        An Authorization object ready for the Execution Gate stage.

    Raises:
        InvariantViolation: If INV-06 (no self-authorization) is violated.
    """
    now = int(time.time() * 1000)

    # Determine effective decision
    effective_decision = policy_result.decision

    # INV-08: Kill switch overrides — cannot issue ALLOW when kill switch is ON
    if state.kill_switch_active and effective_decision == Decision.ALLOW:
        logger.warning(
            "Kill switch is ON — overriding ALLOW to DENY for intent %s",
            intent.intent_id,
        )
        effective_decision = Decision.DENY

    authorization = Authorization(
        authorization_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        decision=effective_decision,
        approver_id=approver_id,
        approval_timestamp=now,
        expiration_timestamp=now + DEFAULT_TOKEN_TTL_MS,
        single_use=True,
        signature="",
    )

    # Enforce INV-06: No self-authorization
    if authorization.decision == Decision.ALLOW:
        check_inv_06_no_self_authorization(intent, authorization)
        intent.status = IntentStatus.APPROVED
        authorization.signature = _sign_token(authorization)

        # Register token in state for tracking
        state.token_registry[authorization.authorization_id] = {
            "intent_id": intent.intent_id,
            "issued_at": now,
            "expires_at": authorization.expiration_timestamp,
            "used": False,
        }

        logger.info(
            "Authorization ALLOW issued for intent %s by approver %s — token %s (expires %d)",
            intent.intent_id,
            approver_id,
            authorization.authorization_id,
            authorization.expiration_timestamp,
        )
    else:
        intent.status = IntentStatus.DENIED
        logger.info(
            "Authorization %s for intent %s by approver %s",
            authorization.decision.value,
            intent.intent_id,
            approver_id,
        )

    return authorization


def _sign_token(authorization: Authorization) -> str:
    """
    Generate a cryptographic signature for the authorization token.

    In a production implementation, this would use ECDSA-secp256k1 with the
    approver's private key. This reference skeleton returns a placeholder.
    """
    return f"sig:{authorization.authorization_id}:{authorization.approval_timestamp}"
