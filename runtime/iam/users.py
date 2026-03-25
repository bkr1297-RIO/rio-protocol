"""
RIO Runtime — IAM: User Registry

Loads and manages the user directory from /runtime/data/users.json.
Provides lookup by user_id, validation of active status, and user
creation for runtime registration.

Each user record contains:
    user_id, name, email, role, active (bool)
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger("rio.iam.users")

# Path to the users data file
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_USERS_FILE = os.path.join(_DATA_DIR, "users.json")


# ---------------------------------------------------------------------------
# User dataclass
# ---------------------------------------------------------------------------

@dataclass
class User:
    """A registered user in the IAM system."""
    user_id: str = ""
    name: str = ""
    email: str = ""
    role: str = "employee"
    active: bool = True

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "active": self.active,
        }


# ---------------------------------------------------------------------------
# In-memory user registry
# ---------------------------------------------------------------------------

_users: Dict[str, User] = {}
_loaded: bool = False


def _load_users() -> None:
    """Load users from the JSON file into memory."""
    global _users, _loaded

    if not os.path.exists(_USERS_FILE):
        logger.warning("Users file not found: %s", _USERS_FILE)
        _loaded = True
        return

    with open(_USERS_FILE, "r") as fh:
        raw = json.load(fh)

    _users.clear()
    for entry in raw:
        user = User(
            user_id=entry["user_id"],
            name=entry.get("name", ""),
            email=entry.get("email", ""),
            role=entry.get("role", "employee"),
            active=entry.get("active", True),
        )
        _users[user.user_id] = user

    _loaded = True
    logger.info("Loaded %d users from %s", len(_users), _USERS_FILE)


def _ensure_loaded() -> None:
    """Ensure users are loaded before any operation."""
    if not _loaded:
        _load_users()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_user(user_id: str) -> Optional[User]:
    """Look up a user by user_id. Returns None if not found."""
    _ensure_loaded()
    return _users.get(user_id)


def get_all_users() -> List[User]:
    """Return all registered users."""
    _ensure_loaded()
    return list(_users.values())


def get_active_users() -> List[User]:
    """Return only active users."""
    _ensure_loaded()
    return [u for u in _users.values() if u.active]


def is_active(user_id: str) -> bool:
    """Check if a user exists and is active."""
    user = get_user(user_id)
    return user is not None and user.active


def get_role(user_id: str) -> Optional[str]:
    """Get the role of a user. Returns None if user not found."""
    user = get_user(user_id)
    return user.role if user else None


def register_user(user_id: str, name: str, email: str, role: str = "employee") -> User:
    """
    Register a new user at runtime (in-memory only).
    For testing and dynamic registration scenarios.
    """
    _ensure_loaded()
    user = User(user_id=user_id, name=name, email=email, role=role, active=True)
    _users[user_id] = user
    logger.info("Registered user: %s (role=%s)", user_id, role)
    return user


def validate_user(user_id: str) -> tuple[bool, str]:
    """
    Validate that a user exists and is active.
    Returns (valid, error_message).
    """
    _ensure_loaded()
    user = get_user(user_id)
    if user is None:
        return False, f"User '{user_id}' not found in IAM registry"
    if not user.active:
        return False, f"User '{user_id}' is deactivated"
    return True, ""


def reset() -> None:
    """Clear the in-memory user registry. For testing only."""
    global _users, _loaded
    _users.clear()
    _loaded = False
    logger.info("User registry reset")


def reload() -> None:
    """Force reload users from disk."""
    global _loaded
    _loaded = False
    _load_users()
