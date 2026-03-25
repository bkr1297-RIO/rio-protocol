"""
RIO Runtime — IAM: Session Management

Issues session tokens when users authenticate, validates tokens on each
request, and attaches user identity (user_id, role) to the request context.

Session tokens are time-limited and tied to a specific user_id.
"""

from __future__ import annotations

import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from runtime.iam import users

logger = logging.getLogger("rio.iam.sessions")

# Default session TTL: 8 hours (in seconds)
DEFAULT_SESSION_TTL = 8 * 60 * 60


# ---------------------------------------------------------------------------
# Session dataclass
# ---------------------------------------------------------------------------

@dataclass
class Session:
    """An active user session."""
    session_id: str = ""
    token: str = ""
    user_id: str = ""
    role: str = ""
    created_at: float = 0.0
    expires_at: float = 0.0
    active: bool = True

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def is_valid(self) -> bool:
        return self.active and not self.is_expired()

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "token": self.token,
            "user_id": self.user_id,
            "role": self.role,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "active": self.active,
        }


# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------

_sessions: Dict[str, Session] = {}  # token -> Session


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_session(user_id: str, ttl: int = DEFAULT_SESSION_TTL) -> Optional[Session]:
    """
    Create a new session for a user.
    
    Validates that the user exists and is active before issuing a session.
    Returns the Session object, or None if the user is invalid.
    """
    # Validate user
    valid, error = users.validate_user(user_id)
    if not valid:
        logger.warning("Session creation denied: %s", error)
        return None

    user = users.get_user(user_id)
    now = time.time()

    # Generate session token
    raw = f"{user_id}:{uuid.uuid4().hex}:{now}"
    token = hashlib.sha256(raw.encode()).hexdigest()

    session = Session(
        session_id=f"SES-{uuid.uuid4().hex[:12].upper()}",
        token=token,
        user_id=user_id,
        role=user.role,
        created_at=now,
        expires_at=now + ttl,
        active=True,
    )

    _sessions[token] = session
    logger.info("Session created: %s for user %s (role=%s)", session.session_id, user_id, user.role)
    return session


def validate_session(token: str) -> tuple[bool, Optional[Session], str]:
    """
    Validate a session token.
    
    Returns (valid, session, error_message).
    """
    session = _sessions.get(token)
    if session is None:
        return False, None, "Invalid session token"

    if not session.active:
        return False, None, "Session has been revoked"

    if session.is_expired():
        session.active = False
        return False, None, "Session has expired"

    # Also verify user is still active
    if not users.is_active(session.user_id):
        session.active = False
        return False, None, f"User '{session.user_id}' has been deactivated"

    return True, session, ""


def get_session_user(token: str) -> Optional[dict]:
    """
    Get the user identity attached to a session token.
    
    Returns a dict with user_id and role, or None if invalid.
    """
    valid, session, _ = validate_session(token)
    if not valid or session is None:
        return None

    return {
        "user_id": session.user_id,
        "role": session.role,
        "session_id": session.session_id,
    }


def revoke_session(token: str) -> bool:
    """Revoke an active session."""
    session = _sessions.get(token)
    if session is None:
        return False
    session.active = False
    logger.info("Session revoked: %s for user %s", session.session_id, session.user_id)
    return True


def revoke_all_sessions(user_id: str) -> int:
    """Revoke all sessions for a user. Returns count of revoked sessions."""
    count = 0
    for session in _sessions.values():
        if session.user_id == user_id and session.active:
            session.active = False
            count += 1
    if count > 0:
        logger.info("Revoked %d sessions for user %s", count, user_id)
    return count


def get_active_sessions() -> list:
    """Return all active sessions."""
    return [s for s in _sessions.values() if s.is_valid()]


def reset() -> None:
    """Clear all sessions. For testing only."""
    _sessions.clear()
    logger.info("Session store reset")
