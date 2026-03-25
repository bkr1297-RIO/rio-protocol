"""
RIO Runtime — Stage 5: Authorization

Issues authorization decisions based on the policy and risk evaluation.
Generates a signed, single-use authorization token if the decision is ALLOW.

Enforces:
- INV-06: No self-authorization (requester != approver).
- INV-08: If kill switch is ON, authorization cannot issue ALLOW.
- IAM authority: Approver must have can_approve for the action.
- IAM limits: Approval must be within role limits (e.g., max_amount).
- IAM self-approval: Self-approval blocked for high-risk actions.
- Token expiry: Tokens are time-limited (configurable via permissions).

Tokens are stored in state.token_registry for tracking.

Spec reference: /spec/06_authorization.md, /spec/15_time_bound_authorization.md
Protocol stage: Step 5 of the 8-step Governed Execution Protocol
Related invariants: INV-01, INV-06, INV-07, INV-08
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any, Optional

from .invariants import InvariantViolation, check_inv_06_no_self_authorization, check_inv_08_kill_switch
from .models import Authorization, Decision, Intent, IntentStatus, PolicyRiskResult
from .state import SystemState

logger = logging.getLogger("rio.authorization")

# Default token validity period (milliseconds) — 5 minutes
DEFAULT_TOKEN_TTL_MS = 5 * 60 * 1000

# Try to load IAM modules — graceful fallback if not available
_iam_available = False
try:
    from runtime.iam import permissions as iam_permissions
    from runtime.iam import users as iam_users
    from runtime.iam.approval_workflow import check_authority, validate_approval_token
    _iam_available = True
except ImportError:
    logger.info("IAM modules not available — using basic authorization")


def authorize(
    intent: Intent,
    policy_result: PolicyRiskResult,
    approver_id: str,
    state: SystemState,
    approver_role: str = "",
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
    - IAM authority checks (when IAM modules are available):
      - Approver must have can_approve for the action
      - Approval must be within role limits
      - Self-approval blocked for high-risk actions

    Args:
        intent: The canonical Intent from the Structured Intent stage.
        policy_result: The PolicyRiskResult from the Policy & Risk stage.
        approver_id: Identity of the actor authorizing (or denying) the request.
        state: The current system state.
        approver_role: Role of the approver (used for IAM authority checks).

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

    # Determine token TTL from IAM permissions or use default
    token_ttl_ms = DEFAULT_TOKEN_TTL_MS
    if _iam_available:
        try:
            token_ttl_ms = iam_permissions.get_token_ttl_ms()
        except Exception:
            pass

    # Build the authorization object
    authorization = Authorization(
        authorization_id=str(uuid.uuid4()),
        intent_id=intent.intent_id,
        decision=effective_decision,
        approver_id=approver_id,
        approval_timestamp=now,
        expiration_timestamp=now + token_ttl_ms,
        single_use=True,
        signature="",
        # IAM enrichment fields
        approver_role=approver_role,
        authority_scope="",
    )

    # Enforce INV-06: No self-authorization
    if authorization.decision == Decision.ALLOW:
        check_inv_06_no_self_authorization(intent, authorization)

        # IAM authority checks (if available)
        if _iam_available and approver_role:
            authority_result = check_authority(
                approver_id=approver_id,
                approver_role=approver_role,
                requester_id=intent.requested_by,
                action=intent.action_type,
                parameters=intent.parameters,
            )

            if not authority_result.authorized:
                logger.warning(
                    "IAM authority check FAILED for approver %s: %s",
                    approver_id, authority_result.error,
                )
                authorization.decision = Decision.DENY
                authorization.authority_scope = f"DENIED: {authority_result.error}"
                intent.status = IntentStatus.DENIED
                logger.info(
                    "Authorization DENY (IAM) for intent %s — %s",
                    intent.intent_id, authority_result.error,
                )
                return authorization

            # Authority check passed — enrich authorization
            authorization.approver_role = authority_result.approver_role
            authorization.authority_scope = authority_result.authority_scope

        # Sign and register token
        intent.status = IntentStatus.APPROVED
        authorization.signature = _sign_token(authorization)

        # Register token in state for tracking
        state.token_registry[authorization.authorization_id] = {
            "intent_id": intent.intent_id,
            "issued_at": now,
            "expires_at": authorization.expiration_timestamp,
            "used": False,
            "approver_id": approver_id,
            "approver_role": approver_role,
        }

        logger.info(
            "Authorization ALLOW issued for intent %s by approver %s (role=%s, scope=%s) — token %s (expires %d)",
            intent.intent_id,
            approver_id,
            approver_role,
            authorization.authority_scope,
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


def check_token_expiry(authorization: Authorization) -> tuple[bool, str]:
    """
    Check if an authorization token has expired.

    Returns (valid, error_message).
    """
    now = int(time.time() * 1000)
    if now > authorization.expiration_timestamp:
        return False, (
            f"Authorization token '{authorization.authorization_id}' has expired "
            f"(expired at {authorization.expiration_timestamp}, current time {now})"
        )
    return True, ""


def _sign_token(authorization: Authorization) -> str:
    """
    Generate a cryptographic signature for the authorization token.

    In a production implementation, this would use ECDSA-secp256k1 with the
    approver's private key. This reference skeleton returns a placeholder.
    """
    return f"sig:{authorization.authorization_id}:{authorization.approval_timestamp}"
