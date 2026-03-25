"""
RIO Runtime — IAM: Permissions

Loads permission definitions from /runtime/data/permissions.json and provides
enforcement functions for request authorization, approval authority, and
approval limits.

Key functions:
    can_request(role, action)     — Can this role submit this action?
    can_approve(role, action)     — Can this role approve this action?
    check_approval_limits(role, action, params) — Within approval limits?
    is_high_risk(action)          — Is this a high-risk action?
    is_self_approval_blocked(action) — Does this action block self-approval?
    get_token_ttl_ms()            — Token time-to-live in milliseconds
"""

from __future__ import annotations

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("rio.iam.permissions")

# Path to the permissions data file
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_PERMISSIONS_FILE = os.path.join(_DATA_DIR, "permissions.json")


# ---------------------------------------------------------------------------
# In-memory permission data
# ---------------------------------------------------------------------------

_permissions: Dict = {}
_high_risk_actions: List[str] = []
_self_approval_blocked: List[str] = []
_token_ttl_ms: int = 300000  # 5 minutes default
_token_single_use: bool = True
_loaded: bool = False


def _load_permissions() -> None:
    """Load permissions from the JSON file into memory."""
    global _permissions, _high_risk_actions, _self_approval_blocked
    global _token_ttl_ms, _token_single_use, _loaded

    if not os.path.exists(_PERMISSIONS_FILE):
        logger.warning("Permissions file not found: %s — using defaults", _PERMISSIONS_FILE)
        _loaded = True
        return

    with open(_PERMISSIONS_FILE, "r") as fh:
        raw = json.load(fh)

    _permissions = raw.get("permissions", {})
    _high_risk_actions = raw.get("high_risk_actions", [])
    _self_approval_blocked = raw.get("self_approval_blocked_actions", [])
    _token_ttl_ms = raw.get("token_ttl_ms", 300000)
    _token_single_use = raw.get("token_single_use", True)
    _loaded = True
    logger.info("Loaded permissions for %d roles", len(_permissions))


def _ensure_loaded() -> None:
    """Ensure permissions are loaded before any operation."""
    if not _loaded:
        _load_permissions()


# ---------------------------------------------------------------------------
# Public API — Request Authorization
# ---------------------------------------------------------------------------

def can_request(role: str, action: str) -> bool:
    """
    Check if a role is permitted to request a given action.
    Wildcard '*' in can_request grants access to all actions.
    """
    _ensure_loaded()
    role_perms = _permissions.get(role, {})
    allowed = role_perms.get("can_request", [])
    return "*" in allowed or action in allowed


def can_approve(role: str, action: str) -> bool:
    """
    Check if a role has approval authority for a given action.
    Wildcard '*' in can_approve grants approval for all actions.
    """
    _ensure_loaded()
    role_perms = _permissions.get(role, {})
    allowed = role_perms.get("can_approve", [])
    return "*" in allowed or action in allowed


# ---------------------------------------------------------------------------
# Public API — Approval Limits
# ---------------------------------------------------------------------------

def check_approval_limits(role: str, action: str, parameters: dict) -> Tuple[bool, str]:
    """
    Check if an approval is within the role's limits for the given action.
    
    Returns (within_limits, error_message).
    If no limits are defined, the approval is allowed.
    """
    _ensure_loaded()
    role_perms = _permissions.get(role, {})
    limits = role_perms.get("approval_limits", {})

    if action not in limits:
        # No specific limits — approval is allowed
        return True, ""

    action_limits = limits[action]

    # Check max_amount limit for financial actions
    if "max_amount" in action_limits:
        max_amount = action_limits["max_amount"]
        # Extract amount from parameters
        amount = parameters.get("amount", 0)
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            amount = 0

        if amount > max_amount:
            return False, (
                f"Amount {amount} exceeds approval limit of {max_amount} "
                f"for role '{role}' on action '{action}'"
            )

    return True, ""


# ---------------------------------------------------------------------------
# Public API — Risk Classification
# ---------------------------------------------------------------------------

def is_high_risk(action: str) -> bool:
    """Check if an action is classified as high-risk."""
    _ensure_loaded()
    return action in _high_risk_actions


def is_self_approval_blocked(action: str) -> bool:
    """Check if self-approval is blocked for this action."""
    _ensure_loaded()
    return action in _self_approval_blocked


# ---------------------------------------------------------------------------
# Public API — Token Configuration
# ---------------------------------------------------------------------------

def get_token_ttl_ms() -> int:
    """Get the token time-to-live in milliseconds."""
    _ensure_loaded()
    return _token_ttl_ms


def is_token_single_use() -> bool:
    """Check if tokens are configured as single-use."""
    _ensure_loaded()
    return _token_single_use


# ---------------------------------------------------------------------------
# Public API — Utility
# ---------------------------------------------------------------------------

def get_permissions_for_role(role: str) -> dict:
    """Get the full permission set for a role."""
    _ensure_loaded()
    return _permissions.get(role, {})


def get_high_risk_actions() -> List[str]:
    """Return the list of high-risk actions."""
    _ensure_loaded()
    return list(_high_risk_actions)


def reset() -> None:
    """Clear the in-memory permission data. For testing only."""
    global _permissions, _high_risk_actions, _self_approval_blocked
    global _token_ttl_ms, _token_single_use, _loaded
    _permissions = {}
    _high_risk_actions = []
    _self_approval_blocked = []
    _token_ttl_ms = 300000
    _token_single_use = True
    _loaded = False
    logger.info("Permissions reset")
