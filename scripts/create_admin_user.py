#!/usr/bin/env python3
"""
RIO Protocol — Create Admin User

Creates (or updates) the first admin user in the IAM user registry.
Reads credentials from .env or prompts interactively.

Usage:
    python scripts/create_admin_user.py
    python scripts/create_admin_user.py --email admin@rio.local --password s3cret
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import logging
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [rio.admin] %(levelname)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("rio.admin")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "runtime" / "data"
USERS_FILE = DATA_DIR / "users.json"


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt via passlib.
    Falls back to SHA-256 salted hash if passlib/bcrypt is not installed.
    """
    try:
        from passlib.hash import bcrypt as bcrypt_hash
        return bcrypt_hash.using(rounds=12).hash(password)
    except ImportError:
        logger.warning("passlib not installed — using SHA-256 fallback (less secure)")
        salt = uuid.uuid4().hex[:16]
        hashed = hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()
        return f"sha256:{salt}:{hashed}"


# ---------------------------------------------------------------------------
# User creation
# ---------------------------------------------------------------------------

def load_users() -> list[dict]:
    """Load the current user registry."""
    if not USERS_FILE.exists():
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_users(users: list[dict]) -> None:
    """Save the user registry."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def create_admin_user(email: str, password: str, name: str = "System Admin") -> dict:
    """
    Create or update an admin user in the user registry.
    Returns the user record (without the password hash in the return value).
    """
    users = load_users()

    # Check if an admin with this email already exists
    existing = next((u for u in users if u.get("email") == email), None)

    password_hash = hash_password(password)
    now = datetime.now(timezone.utc).isoformat()

    if existing:
        # Update existing user
        existing["role"] = "admin"
        existing["active"] = True
        existing["password_hash"] = password_hash
        existing["updated_at"] = now
        logger.info("Updated existing user %s to admin role", email)
        user_record = existing
    else:
        # Generate a new user ID
        max_id = 0
        for u in users:
            uid = u.get("user_id", "")
            if uid.startswith("user_") and uid[5:].isdigit():
                max_id = max(max_id, int(uid[5:]))
        new_id = f"user_{max_id + 1:03d}"

        user_record = {
            "user_id": new_id,
            "name": name,
            "email": email,
            "role": "admin",
            "active": True,
            "password_hash": password_hash,
            "created_at": now,
        }
        users.append(user_record)
        logger.info("Created new admin user: %s (ID: %s)", email, new_id)

    save_users(users)

    # Return a safe copy (no password hash)
    safe_copy = {k: v for k, v in user_record.items() if k != "password_hash"}
    return safe_copy


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    """Entry point: parse arguments or prompt interactively."""
    parser = argparse.ArgumentParser(
        description="Create or update a RIO admin user",
    )
    parser.add_argument("--email", type=str, help="Admin email address")
    parser.add_argument("--password", type=str, help="Admin password")
    parser.add_argument("--name", type=str, default="System Admin", help="Display name")
    args = parser.parse_args()

    logger.info("")
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║           RIO Protocol — Create Admin User              ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")

    # Try .env first, then CLI args, then interactive prompt
    email = args.email
    password = args.password

    if not email:
        # Try .env
        try:
            from dotenv import load_dotenv
            load_dotenv(PROJECT_ROOT / ".env")
        except ImportError:
            pass
        email = os.environ.get("ADMIN_EMAIL")

    if not password:
        password_env = os.environ.get("ADMIN_PASSWORD")
        if password_env and password_env != "change_me":
            password = password_env

    # Interactive fallback
    if not email:
        email = input("Admin email [admin@rio.local]: ").strip() or "admin@rio.local"

    if not password:
        password = getpass.getpass("Admin password: ")
        if not password:
            logger.error("Password cannot be empty.")
            sys.exit(1)
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            logger.error("Passwords do not match.")
            sys.exit(1)

    name = args.name

    user = create_admin_user(email=email, password=password, name=name)

    logger.info("")
    logger.info("Admin user ready:")
    logger.info("  User ID: %s", user.get("user_id"))
    logger.info("  Name:    %s", user.get("name"))
    logger.info("  Email:   %s", user.get("email"))
    logger.info("  Role:    %s", user.get("role"))
    logger.info("")
    logger.info("You can now start the system: python scripts/run_all.py")


if __name__ == "__main__":
    main()
