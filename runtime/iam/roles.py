"""
RIO Runtime — IAM: Role Definitions

Loads role definitions from /runtime/data/roles.json and provides
role hierarchy, level comparison, and role validation.

Roles:
    intern   (level 1) — Minimal permissions
    employee (level 2) — Standard operations
    auditor  (level 2) — Read-only audit access
    manager  (level 3) — Approval authority for standard operations
    admin    (level 4) — Full system access and unlimited approval
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger("rio.iam.roles")

# Path to the roles data file
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_ROLES_FILE = os.path.join(_DATA_DIR, "roles.json")


# ---------------------------------------------------------------------------
# Role dataclass
# ---------------------------------------------------------------------------

@dataclass
class Role:
    """A role definition in the IAM system."""
    name: str = ""
    description: str = ""
    level: int = 0
    can_request: List[str] = field(default_factory=list)
    can_approve: List[str] = field(default_factory=list)
    can_view_ledger: bool = False
    approval_limits: Dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# In-memory role registry
# ---------------------------------------------------------------------------

_roles: Dict[str, Role] = {}
_hierarchy: List[str] = []
_loaded: bool = False


def _load_roles() -> None:
    """Load roles from the JSON file into memory."""
    global _roles, _hierarchy, _loaded

    if not os.path.exists(_ROLES_FILE):
        logger.warning("Roles file not found: %s — using defaults", _ROLES_FILE)
        _roles = {
            "intern": Role(name="intern", level=1),
            "employee": Role(name="employee", level=2),
            "auditor": Role(name="auditor", level=2, can_view_ledger=True),
            "manager": Role(name="manager", level=3, can_approve=["*"], can_view_ledger=True),
            "admin": Role(name="admin", level=4, can_request=["*"], can_approve=["*"], can_view_ledger=True),
        }
        _hierarchy = ["intern", "employee", "auditor", "manager", "admin"]
        _loaded = True
        return

    with open(_ROLES_FILE, "r") as fh:
        raw = json.load(fh)

    _roles.clear()
    for role_name, role_data in raw.get("roles", {}).items():
        _roles[role_name] = Role(
            name=role_name,
            description=role_data.get("description", ""),
            level=role_data.get("level", 0),
            can_request=role_data.get("can_request", []),
            can_approve=role_data.get("can_approve", []),
            can_view_ledger=role_data.get("can_view_ledger", False),
            approval_limits=role_data.get("approval_limits", {}),
        )

    _hierarchy = raw.get("hierarchy", list(_roles.keys()))
    _loaded = True
    logger.info("Loaded %d roles from %s", len(_roles), _ROLES_FILE)


def _ensure_loaded() -> None:
    """Ensure roles are loaded before any operation."""
    if not _loaded:
        _load_roles()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_role(role_name: str) -> Optional[Role]:
    """Look up a role by name."""
    _ensure_loaded()
    return _roles.get(role_name)


def get_all_roles() -> Dict[str, Role]:
    """Return all role definitions."""
    _ensure_loaded()
    return dict(_roles)


def get_level(role_name: str) -> int:
    """Get the authority level for a role. Returns 0 if not found."""
    _ensure_loaded()
    role = _roles.get(role_name)
    return role.level if role else 0


def is_higher_or_equal(role_a: str, role_b: str) -> bool:
    """Check if role_a has equal or higher authority than role_b."""
    return get_level(role_a) >= get_level(role_b)


def get_hierarchy() -> List[str]:
    """Return the role hierarchy from lowest to highest."""
    _ensure_loaded()
    return list(_hierarchy)


def is_valid_role(role_name: str) -> bool:
    """Check if a role name is recognized."""
    _ensure_loaded()
    return role_name in _roles


def reset() -> None:
    """Clear the in-memory role registry. For testing only."""
    global _roles, _hierarchy, _loaded
    _roles.clear()
    _hierarchy.clear()
    _loaded = False
    logger.info("Role registry reset")
