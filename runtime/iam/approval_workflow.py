"""
RIO Runtime — IAM: Approval Workflow with Authority Enforcement

Implements the authority-aware approval workflow that:
  1. Checks if the approver has authority to approve the action
  2. Checks approval limits (e.g., max transfer amount)
  3. Blocks self-approval for high-risk actions
  4. Issues time-limited, single-use authorization tokens
  5. Records approver identity and authority scope in the authorization

This module works alongside the existing approval_manager but adds
IAM-backed authority enforcement on top.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from runtime.iam import permissions, users, roles

logger = logging.getLogger("rio.iam.approval_workflow")


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class AuthorityCheckResult:
    """Result of an authority check for an approval."""
    authorized: bool = False
    error: str = ""
    approver_id: str = ""
    approver_role: str = ""
    authority_scope: str = ""
    approval_limits: dict = field(default_factory=dict)


@dataclass
class ApprovalAuthorizationResult:
    """Result of a full approval authorization including token issuance."""
    success: bool = False
    error: str = ""
    authorization_id: str = ""
    authorization_token: str = ""
    request_id: str = ""
    approved_by_user_id: str = ""
    approver_role: str = ""
    approval_timestamp: float = 0.0
    approval_scope: str = ""
    token_expires_at: float = 0.0
    token_single_use: bool = True


# ---------------------------------------------------------------------------
# Authority Check
# ---------------------------------------------------------------------------

def check_authority(
    approver_id: str,
    approver_role: str,
    requester_id: str,
    action: str,
    parameters: dict,
) -> AuthorityCheckResult:
    """
    Check if an approver has the authority to approve a given action.
    
    Enforces:
      1. Approver must be an active user (if registered in IAM)
      2. Approver role must have can_approve for this action
      3. Approval must be within role limits (e.g., max_amount)
      4. Self-approval blocked for high-risk actions
    """
    result = AuthorityCheckResult(
        approver_id=approver_id,
        approver_role=approver_role,
    )

    # 1. Check if approver is a known user and is active
    user = users.get_user(approver_id)
    if user is not None:
        if not user.active:
            result.error = f"Approver '{approver_id}' is deactivated"
            return result
        # Use the IAM role if available (override provided role)
        if user.role != approver_role:
            logger.info(
                "Approver role override: provided=%s, IAM=%s — using IAM role",
                approver_role, user.role,
            )
            approver_role = user.role
            result.approver_role = approver_role

    # 2. Check approval authority
    if not permissions.can_approve(approver_role, action):
        result.error = (
            f"Role '{approver_role}' is not authorized to approve action '{action}'"
        )
        return result

    # 3. Check approval limits
    within_limits, limit_error = permissions.check_approval_limits(
        approver_role, action, parameters
    )
    if not within_limits:
        result.error = limit_error
        return result

    # 4. Self-approval check for high-risk actions
    if permissions.is_self_approval_blocked(action):
        if approver_id == requester_id:
            result.error = (
                f"Self-approval is blocked for high-risk action '{action}' "
                f"(requester and approver are both '{approver_id}')"
            )
            return result

    # All checks passed
    result.authorized = True
    result.authority_scope = _compute_authority_scope(approver_role, action)
    result.approval_limits = _get_limits_for_action(approver_role, action)

    return result


def _compute_authority_scope(role: str, action: str) -> str:
    """Compute a human-readable authority scope string."""
    role_obj = roles.get_role(role)
    if role_obj is None:
        return f"{role}:{action}"

    if "*" in role_obj.can_approve:
        return f"{role}:FULL_AUTHORITY"
    else:
        return f"{role}:{action}"


def _get_limits_for_action(role: str, action: str) -> dict:
    """Get the approval limits for a role+action combination."""
    role_perms = permissions.get_permissions_for_role(role)
    limits = role_perms.get("approval_limits", {})
    return limits.get(action, {})


# ---------------------------------------------------------------------------
# Approval Authorization (with token issuance)
# ---------------------------------------------------------------------------

def authorize_approval(
    request_id: str,
    approver_id: str,
    approver_role: str,
    requester_id: str,
    action: str,
    parameters: dict,
) -> ApprovalAuthorizationResult:
    """
    Full approval authorization: check authority, then issue a time-limited
    single-use authorization token.
    
    Returns an ApprovalAuthorizationResult with the token and metadata.
    """
    result = ApprovalAuthorizationResult(
        request_id=request_id,
        approved_by_user_id=approver_id,
        approver_role=approver_role,
    )

    # Step 1: Check authority
    authority = check_authority(
        approver_id=approver_id,
        approver_role=approver_role,
        requester_id=requester_id,
        action=action,
        parameters=parameters,
    )

    if not authority.authorized:
        result.error = authority.error
        return result

    # Step 2: Issue authorization token
    now = time.time()
    ttl_ms = permissions.get_token_ttl_ms()
    ttl_sec = ttl_ms / 1000.0

    auth_id = f"AUTH-{uuid.uuid4().hex[:12].upper()}"
    token_raw = f"{auth_id}:{request_id}:{approver_id}:{now}:{uuid.uuid4().hex}"
    token = hashlib.sha256(token_raw.encode()).hexdigest()

    result.success = True
    result.authorization_id = auth_id
    result.authorization_token = token
    result.approval_timestamp = now
    result.approval_scope = authority.authority_scope
    result.token_expires_at = now + ttl_sec
    result.token_single_use = permissions.is_token_single_use()
    result.approver_role = authority.approver_role  # May have been overridden by IAM

    logger.info(
        "Approval authorized: %s by %s (role=%s, scope=%s, expires_in=%.0fs)",
        auth_id, approver_id, authority.approver_role,
        authority.authority_scope, ttl_sec,
    )

    return result


# ---------------------------------------------------------------------------
# Token Expiry Check
# ---------------------------------------------------------------------------

def is_token_expired(token_expires_at: float) -> bool:
    """Check if an authorization token has expired."""
    return time.time() > token_expires_at


def validate_approval_token(
    authorization_id: str,
    token_expires_at: float,
    consumed_tokens: set,
) -> tuple[bool, str]:
    """
    Validate an approval-issued authorization token.
    
    Checks:
      1. Token has not expired
      2. Token has not already been consumed (single-use)
    
    Returns (valid, error_message).
    """
    # Check expiry
    if is_token_expired(token_expires_at):
        return False, f"Authorization token '{authorization_id}' has expired"

    # Check single-use
    if permissions.is_token_single_use() and authorization_id in consumed_tokens:
        return False, f"Authorization token '{authorization_id}' has already been consumed"

    return True, ""
