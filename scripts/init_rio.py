#!/usr/bin/env python3
"""
RIO Protocol — Initialization Script

Creates all required directories, data files, cryptographic keys,
policy files, risk model files, and user/role seed data so the
system is ready to run.

Usage:
    python scripts/init_rio.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [rio.init] %(levelname)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("rio.init")

# ---------------------------------------------------------------------------
# Paths (relative to project root)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = PROJECT_ROOT / "runtime"
DATA_DIR = RUNTIME_DIR / "data"
KEYS_DIR = RUNTIME_DIR / "keys"
POLICY_DIR = RUNTIME_DIR / "policy"
GOVERNANCE_DIR = RUNTIME_DIR / "governance"


def _ensure_dir(path: Path, label: str) -> None:
    """Create a directory if it does not exist."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info("Created directory: %s (%s)", path.relative_to(PROJECT_ROOT), label)
    else:
        logger.info("Directory exists:  %s (%s)", path.relative_to(PROJECT_ROOT), label)


def _ensure_file(path: Path, default_content: str, label: str) -> None:
    """Create a file with default content if it does not exist."""
    if not path.exists():
        path.write_text(default_content, encoding="utf-8")
        logger.info("Created file:      %s (%s)", path.relative_to(PROJECT_ROOT), label)
    else:
        logger.info("File exists:       %s (%s)", path.relative_to(PROJECT_ROOT), label)


# ---------------------------------------------------------------------------
# 1. Directories
# ---------------------------------------------------------------------------

def init_directories() -> None:
    """Create all required directories."""
    logger.info("=" * 60)
    logger.info("Step 1: Directories")
    logger.info("=" * 60)
    _ensure_dir(DATA_DIR, "runtime data")
    _ensure_dir(KEYS_DIR, "cryptographic keys")
    _ensure_dir(POLICY_DIR, "policy engine rules")
    _ensure_dir(GOVERNANCE_DIR, "governance versioning")


# ---------------------------------------------------------------------------
# 2. Data Files
# ---------------------------------------------------------------------------

def init_data_files() -> None:
    """Create empty JSONL/JSON data files if they do not exist."""
    logger.info("=" * 60)
    logger.info("Step 2: Data Files")
    logger.info("=" * 60)

    jsonl_files = {
        "ledger.jsonl": "tamper-evident audit ledger",
        "receipts.jsonl": "cryptographic receipts",
        "requests.jsonl": "action request log",
        "approvals.jsonl": "approval decisions",
    }
    for filename, label in jsonl_files.items():
        _ensure_file(DATA_DIR / filename, "", label)

    # Governed corpus (JSONL)
    _ensure_file(DATA_DIR / "governed_corpus.jsonl", "", "governed corpus")

    # Log files
    log_files = {
        "sent_emails.log": "email connector log",
        "calendar_events.log": "calendar connector log",
        "http_requests.log": "HTTP connector log",
    }
    for filename, label in log_files.items():
        _ensure_file(DATA_DIR / filename, "", label)

    # System state
    default_state = json.dumps({
        "kill_switch_active": False,
        "ledger_length": 0,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }, indent=2)
    _ensure_file(DATA_DIR / "system_state.json", default_state, "system state")

    # .gitignore for data dir
    gitignore = "# Keep this directory in version control but ignore generated data\n*.jsonl\n*.log\n!.gitkeep\n!.gitignore\n"
    _ensure_file(DATA_DIR / ".gitignore", gitignore, "data .gitignore")
    _ensure_file(DATA_DIR / ".gitkeep", "", "data .gitkeep")


# ---------------------------------------------------------------------------
# 3. Cryptographic Keys
# ---------------------------------------------------------------------------

def init_keys() -> None:
    """Generate RSA-2048 key pair if not present."""
    logger.info("=" * 60)
    logger.info("Step 3: Cryptographic Keys")
    logger.info("=" * 60)

    private_path = KEYS_DIR / "private_key.pem"
    public_path = KEYS_DIR / "public_key.pem"

    if private_path.exists() and public_path.exists():
        logger.info("Key pair exists:   %s", KEYS_DIR.relative_to(PROJECT_ROOT))
        return

    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except ImportError:
        logger.error(
            "cryptography package not installed. Run: pip install -r requirements.txt"
        )
        sys.exit(1)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    private_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    os.chmod(str(private_path), 0o600)

    public_path.write_bytes(
        key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )

    logger.info("Generated RSA-2048 key pair at %s", KEYS_DIR.relative_to(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# 4. Policy Files
# ---------------------------------------------------------------------------

def init_policy_files() -> None:
    """Initialize policy rules and version registry."""
    logger.info("=" * 60)
    logger.info("Step 4: Policy Files")
    logger.info("=" * 60)

    # Active policy rules (used by the policy engine at runtime)
    default_policy_rules = json.dumps({
        "version": "1.0",
        "description": "RIO Default Policy Rules — defines action-level policy decisions.",
        "rules": [
            {"id": "POL-001", "description": "Intern cannot transfer funds", "role": "intern", "action": "transfer_funds", "decision": "DENY", "priority": 1},
            {"id": "POL-002", "description": "Intern cannot deploy code", "role": "intern", "action": "deploy_code", "decision": "DENY", "priority": 1},
            {"id": "POL-003", "description": "Intern cannot grant access", "role": "intern", "action": "grant_access", "decision": "DENY", "priority": 1},
            {"id": "POL-004", "description": "Intern cannot delete data", "role": "intern", "action": "delete_data", "decision": "DENY", "priority": 1},
            {"id": "POL-005", "description": "Employee cannot delete data", "role": "employee", "action": "delete_data", "decision": "DENY", "priority": 2},
            {"id": "POL-006", "description": "Employee cannot grant access", "role": "employee", "action": "grant_access", "decision": "DENY", "priority": 2},
            {"id": "POL-007", "description": "Contractor cannot deploy code", "role": "contractor", "action": "deploy_code", "decision": "DENY", "priority": 2},
            {"id": "POL-008", "description": "High-risk transfer requires approval", "action": "transfer_funds", "condition": "amount > 1000", "decision": "REQUIRE_APPROVAL", "priority": 5},
        ],
    }, indent=2)
    _ensure_file(POLICY_DIR / "policy_rules.json", default_policy_rules, "active policy rules")

    # Default risk rules
    default_risk_rules = json.dumps({
        "version": "1.0.0",
        "description": "RIO Risk Rules — defines base risk scores by action type, role, and amount thresholds.",
        "base_risk": {
            "send_email": 1, "create_event": 1, "read_data": 1,
            "update_config": 3, "transfer_funds": 5, "deploy_code": 6,
            "grant_access": 7, "delete_data": 8,
        },
        "role_risk": {
            "admin": 1, "manager": 2, "employee": 3, "contractor": 4, "intern": 6,
        },
        "amount_thresholds": [
            {"min": 0, "max": 100, "risk_add": 0},
            {"min": 100, "max": 1000, "risk_add": 1},
            {"min": 1000, "max": 10000, "risk_add": 3},
            {"min": 10000, "max": None, "risk_add": 5},
        ],
        "system_target_risk": {
            "payment_system": 3, "production_database": 4, "email_system": 1,
            "calendar_system": 1, "config_system": 2, "access_control": 3,
            "deployment_system": 3,
        },
        "risk_levels": {
            "LOW": {"min": 0, "max": 5},
            "MEDIUM": {"min": 5, "max": 10},
            "HIGH": {"min": 10, "max": 100},
        },
    }, indent=2)
    _ensure_file(POLICY_DIR / "risk_rules.json", default_risk_rules, "active risk rules")

    # Governance version registries
    now = datetime.now(timezone.utc).isoformat()

    policy_versions = json.dumps({
        "current_version": "1.0",
        "versions": {
            "1.0": {
                "file": "policy_rules_v1_0.json",
                "activated_at": now,
                "activated_by": "system",
                "description": "Initial policy rules — role-based deny rules and approval thresholds",
                "approved_by": "system",
                "approved_at": now,
            }
        },
    }, indent=2)
    _ensure_file(GOVERNANCE_DIR / "policy_versions.json", policy_versions, "policy version registry")

    risk_versions = json.dumps({
        "current_version": "1.0.0",
        "versions": {
            "1.0.0": {
                "file": "risk_rules_v1_0_0.json",
                "activated_at": now,
                "activated_by": "system",
                "description": "Initial risk model — base risk scores, role risk, amount thresholds, system target risk",
                "approved_by": "system",
                "approved_at": now,
            }
        },
    }, indent=2)
    _ensure_file(GOVERNANCE_DIR / "risk_versions.json", risk_versions, "risk version registry")

    # Versioned copies of the initial rules
    _ensure_file(GOVERNANCE_DIR / "policy_rules_v1_0.json", default_policy_rules, "policy v1.0 snapshot")
    _ensure_file(GOVERNANCE_DIR / "risk_rules_v1_0_0.json", default_risk_rules, "risk v1.0.0 snapshot")

    # Change logs (empty JSONL)
    _ensure_file(GOVERNANCE_DIR / "policy_change_log.jsonl", "", "policy change log")
    _ensure_file(GOVERNANCE_DIR / "risk_change_log.jsonl", "", "risk change log")


# ---------------------------------------------------------------------------
# 5. Users & Roles
# ---------------------------------------------------------------------------

def init_users_and_roles() -> None:
    """Initialize the default user registry and role definitions."""
    logger.info("=" * 60)
    logger.info("Step 5: Users & Roles")
    logger.info("=" * 60)

    default_users = json.dumps([
        {"user_id": "user_001", "name": "Alice Smith", "email": "alice@company.com", "role": "manager", "active": True},
        {"user_id": "user_002", "name": "Bob Johnson", "email": "bob@company.com", "role": "employee", "active": True},
        {"user_id": "user_003", "name": "Carol Williams", "email": "carol@company.com", "role": "admin", "active": True},
        {"user_id": "user_004", "name": "Dave Brown", "email": "dave@company.com", "role": "auditor", "active": True},
        {"user_id": "user_005", "name": "Eve Davis", "email": "eve@company.com", "role": "employee", "active": True},
        {"user_id": "user_006", "name": "Frank Miller", "email": "frank@company.com", "role": "intern", "active": True},
        {"user_id": "user_007", "name": "Grace Wilson", "email": "grace@company.com", "role": "manager", "active": True},
        {"user_id": "user_008", "name": "Hank Taylor", "email": "hank@company.com", "role": "admin", "active": True},
        {"user_id": "user_009", "name": "Iris Anderson", "email": "iris@company.com", "role": "employee", "active": False},
    ], indent=2)
    _ensure_file(DATA_DIR / "users.json", default_users, "user registry")

    default_roles = json.dumps({
        "roles": {
            "intern": {
                "description": "Temporary staff with minimal permissions",
                "level": 1,
                "can_request": ["send_email", "create_event"],
                "can_approve": [],
                "can_view_ledger": False,
            },
            "employee": {
                "description": "Regular staff member with standard operational permissions",
                "level": 2,
                "can_request": ["send_email", "create_event", "write_file", "read_file", "http_request"],
                "can_approve": [],
                "can_view_ledger": False,
            },
            "manager": {
                "description": "Team lead with approval authority for standard operations",
                "level": 3,
                "can_request": ["send_email", "create_event", "write_file", "read_file", "http_request", "transfer_funds"],
                "can_approve": ["send_email", "create_event", "write_file", "read_file", "http_request", "transfer_funds", "deploy_code", "grant_access"],
                "can_view_ledger": True,
                "approval_limits": {"transfer_funds": {"max_amount": 10000}},
            },
            "admin": {
                "description": "System administrator with full permissions and unlimited approval authority",
                "level": 4,
                "can_request": ["*"],
                "can_approve": ["*"],
                "can_view_ledger": True,
                "approval_limits": {},
            },
            "auditor": {
                "description": "Read-only access for compliance and audit purposes",
                "level": 2,
                "can_request": [],
                "can_approve": [],
                "can_view_ledger": True,
            },
        },
        "hierarchy": ["intern", "employee", "auditor", "manager", "admin"],
    }, indent=2)
    _ensure_file(DATA_DIR / "roles.json", default_roles, "role definitions")

    default_permissions = json.dumps({
        "permissions": {
            "intern": {"can_request": ["send_email", "create_event"], "can_approve": [], "can_view_ledger": False, "approval_limits": {}},
            "employee": {"can_request": ["send_email", "create_event", "write_file", "read_file", "http_request"], "can_approve": [], "can_view_ledger": False, "approval_limits": {}},
            "manager": {
                "can_request": ["send_email", "create_event", "write_file", "read_file", "http_request", "transfer_funds"],
                "can_approve": ["send_email", "create_event", "write_file", "read_file", "http_request", "transfer_funds", "deploy_code", "grant_access"],
                "can_view_ledger": True,
                "approval_limits": {"transfer_funds": {"max_amount": 10000, "description": "Can approve transfers up to $10,000"}},
            },
            "admin": {"can_request": ["*"], "can_approve": ["*"], "can_view_ledger": True, "approval_limits": {}},
            "auditor": {"can_request": [], "can_approve": [], "can_view_ledger": True, "approval_limits": {}},
        },
    }, indent=2)
    _ensure_file(DATA_DIR / "permissions.json", default_permissions, "permissions matrix")


# ---------------------------------------------------------------------------
# 6. Environment File
# ---------------------------------------------------------------------------

def init_env_file() -> None:
    """Copy .env.example to .env if .env does not exist."""
    logger.info("=" * 60)
    logger.info("Step 6: Environment File")
    logger.info("=" * 60)

    env_path = PROJECT_ROOT / ".env"
    example_path = PROJECT_ROOT / ".env.example"

    if env_path.exists():
        logger.info("File exists:       .env (not overwritten)")
    elif example_path.exists():
        import shutil
        shutil.copy2(str(example_path), str(env_path))
        logger.info("Created .env from .env.example — edit values before running")
    else:
        logger.warning(".env.example not found — skipping .env creation")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    """Run all initialization steps."""
    logger.info("")
    logger.info("╔══════════════════════════════════════════════════════════╗")
    logger.info("║           RIO Protocol — System Initialization          ║")
    logger.info("╚══════════════════════════════════════════════════════════╝")
    logger.info("")

    init_directories()
    init_data_files()
    init_keys()
    init_policy_files()
    init_users_and_roles()
    init_env_file()

    logger.info("")
    logger.info("=" * 60)
    logger.info("RIO initialized successfully.")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Edit .env if needed (especially ADMIN_EMAIL / ADMIN_PASSWORD)")
    logger.info("  2. Create admin user:  python scripts/create_admin_user.py")
    logger.info("  3. Start the system:   python scripts/run_all.py")
    logger.info("  4. Run tests:          python -m runtime.test_harness")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
