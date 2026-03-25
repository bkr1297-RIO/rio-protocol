"""
RIO Runtime — Policy Manager

Manages policy versioning, change proposals, approvals, activation, and rollback.
All policy changes are versioned (old versions are never overwritten) and require
admin approval before activation. Every governance change is recorded in the
policy change log and written to the audit ledger.

Functions:
    get_current_policy()          — Return the active policy version and its rules.
    create_new_policy_version()   — Create a new policy version from proposed rules.
    submit_policy_change()        — Submit a policy change proposal for approval.
    approve_policy_change()       — Approve a pending policy change (admin only).
    activate_policy_version()     — Activate an approved policy version (admin only).
    rollback_policy_version()     — Rollback to a previous policy version (admin only).
    reset()                       — Reset in-memory state (testing only).
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger("rio.policy_manager")

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

_GOVERNANCE_DIR = os.path.dirname(__file__)
_VERSIONS_FILE = os.path.join(_GOVERNANCE_DIR, "policy_versions.json")
_CHANGE_LOG_FILE = os.path.join(_GOVERNANCE_DIR, "policy_change_log.jsonl")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class PolicyChange:
    """A proposed policy change awaiting approval."""
    change_id: str = ""
    old_version: str = ""
    new_version: str = ""
    proposed_by: str = ""
    proposed_by_role: str = ""
    approved_by: str = ""
    status: str = "PROPOSED"       # PROPOSED | APPROVED | ACTIVATED | REJECTED | ROLLED_BACK
    change_summary: str = ""
    proposed_rules: list = field(default_factory=list)
    created_at: int = 0
    created_at_iso: str = ""
    resolved_at: int = 0
    resolved_at_iso: str = ""


@dataclass
class PolicyManagerResult:
    """Result of a policy manager operation."""
    success: bool = False
    error: str = ""
    change: Optional[PolicyChange] = None
    version: str = ""
    rules: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------

_pending_changes: Dict[str, PolicyChange] = {}
_change_history: List[PolicyChange] = []
_versions_cache: Optional[Dict[str, Any]] = None


def reset() -> None:
    """Reset in-memory state. For testing only."""
    global _pending_changes, _change_history, _versions_cache
    _pending_changes = {}
    _change_history = []
    _versions_cache = None
    logger.info("Policy manager reset")


# ---------------------------------------------------------------------------
# Version file I/O
# ---------------------------------------------------------------------------

def _load_versions() -> Dict[str, Any]:
    """Load and cache the policy versions registry."""
    global _versions_cache
    if _versions_cache is not None:
        return _versions_cache

    if not os.path.exists(_VERSIONS_FILE):
        _versions_cache = {"current_version": "1.0", "versions": {}}
        return _versions_cache

    with open(_VERSIONS_FILE, "r") as f:
        _versions_cache = json.load(f)

    logger.info("Loaded policy versions: current=%s, total=%d",
                _versions_cache["current_version"],
                len(_versions_cache["versions"]))
    return _versions_cache


def _save_versions(data: Dict[str, Any]) -> None:
    """Save the policy versions registry to disk."""
    global _versions_cache
    _versions_cache = data
    with open(_VERSIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Policy versions saved: current=%s", data["current_version"])


def _load_rules_file(filename: str) -> List[Dict[str, Any]]:
    """Load a policy rules file from the governance directory."""
    filepath = os.path.join(_GOVERNANCE_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Policy rules file not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    return data.get("rules", [])


def _save_rules_file(filename: str, rules: List[Dict[str, Any]], version: str) -> None:
    """Save a policy rules file to the governance directory."""
    filepath = os.path.join(_GOVERNANCE_DIR, filename)
    data = {
        "version": version,
        "description": f"RIO Policy Rules — version {version}",
        "rules": rules,
    }
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Policy rules file saved: %s (%d rules)", filename, len(rules))


# ---------------------------------------------------------------------------
# Change log persistence
# ---------------------------------------------------------------------------

def _write_change_log(change: PolicyChange) -> None:
    """Append a change record to the policy change log and data store."""
    record = {
        "change_id": change.change_id,
        "old_version": change.old_version,
        "new_version": change.new_version,
        "proposed_by": change.proposed_by,
        "approved_by": change.approved_by,
        "status": change.status,
        "change_summary": change.change_summary,
        "created_at": change.created_at,
        "created_at_iso": change.created_at_iso,
        "resolved_at": change.resolved_at,
        "resolved_at_iso": change.resolved_at_iso,
        "timestamp": int(time.time() * 1000),
        "timestamp_iso": datetime.now(timezone.utc).isoformat(),
    }
    os.makedirs(os.path.dirname(_CHANGE_LOG_FILE), exist_ok=True)
    with open(_CHANGE_LOG_FILE, "a") as f:
        f.write(json.dumps(record, default=str) + "\n")
    logger.debug("Policy change %s written to change log", change.change_id)


def read_change_log() -> List[Dict[str, Any]]:
    """Read all entries from the policy change log."""
    if not os.path.exists(_CHANGE_LOG_FILE):
        return []
    records = []
    with open(_CHANGE_LOG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_current_policy() -> PolicyManagerResult:
    """
    Return the active policy version and its rules.

    Returns:
        PolicyManagerResult with version string and rules list.
    """
    versions = _load_versions()
    current = versions["current_version"]
    version_info = versions["versions"].get(current)

    if not version_info:
        return PolicyManagerResult(
            success=False,
            error=f"Current version {current} not found in versions registry",
        )

    try:
        rules = _load_rules_file(version_info["file"])
    except FileNotFoundError as e:
        return PolicyManagerResult(success=False, error=str(e))

    return PolicyManagerResult(
        success=True,
        version=current,
        rules=rules,
    )


def get_all_versions() -> Dict[str, Any]:
    """Return the full versions registry."""
    return _load_versions()


def get_pending_changes() -> List[PolicyChange]:
    """Return all pending policy change proposals."""
    return [c for c in _pending_changes.values() if c.status == "PROPOSED"]


def get_change(change_id: str) -> Optional[PolicyChange]:
    """Look up a policy change by ID."""
    return _pending_changes.get(change_id)


def get_change_history() -> List[PolicyChange]:
    """Return the full history of policy changes."""
    return list(_change_history)


def submit_policy_change(
    proposed_by: str,
    proposed_by_role: str,
    new_rules: List[Dict[str, Any]],
    change_summary: str,
) -> PolicyManagerResult:
    """
    Submit a policy change proposal for approval.

    Only admin role can submit policy changes.

    Args:
        proposed_by: Identity of the proposer.
        proposed_by_role: Role of the proposer (must be admin).
        new_rules: The proposed list of policy rules.
        change_summary: Human-readable summary of the change.

    Returns:
        PolicyManagerResult with the created PolicyChange.
    """
    if proposed_by_role != "admin":
        return PolicyManagerResult(
            success=False,
            error=f"Role '{proposed_by_role}' is not authorized to propose policy changes. Required: admin",
        )

    versions = _load_versions()
    current_version = versions["current_version"]

    # Compute next version
    major, minor = current_version.split(".")
    new_version = f"{major}.{int(minor) + 1}"

    now = int(time.time() * 1000)
    now_iso = datetime.fromtimestamp(now / 1000, tz=timezone.utc).isoformat()

    change_id = f"POL-CHG-{uuid.uuid4().hex[:8].upper()}"

    change = PolicyChange(
        change_id=change_id,
        old_version=current_version,
        new_version=new_version,
        proposed_by=proposed_by,
        proposed_by_role=proposed_by_role,
        status="PROPOSED",
        change_summary=change_summary,
        proposed_rules=new_rules,
        created_at=now,
        created_at_iso=now_iso,
    )

    _pending_changes[change_id] = change
    _change_history.append(change)
    _write_change_log(change)

    logger.info(
        "Policy change %s proposed by %s: %s → %s (%s)",
        change_id, proposed_by, current_version, new_version, change_summary,
    )

    return PolicyManagerResult(
        success=True,
        change=change,
        version=new_version,
    )


def approve_policy_change(
    change_id: str,
    approver_id: str,
    approver_role: str,
) -> PolicyManagerResult:
    """
    Approve a pending policy change proposal.

    Only admin role can approve. The approver must be different from the proposer
    (no self-approval for governance changes).

    Args:
        change_id: ID of the policy change to approve.
        approver_id: Identity of the approver.
        approver_role: Role of the approver (must be admin).

    Returns:
        PolicyManagerResult with the updated PolicyChange.
    """
    if approver_role != "admin":
        return PolicyManagerResult(
            success=False,
            error=f"Role '{approver_role}' is not authorized to approve policy changes. Required: admin",
        )

    change = _pending_changes.get(change_id)
    if not change:
        return PolicyManagerResult(
            success=False,
            error=f"Policy change {change_id} not found",
        )

    if change.status != "PROPOSED":
        return PolicyManagerResult(
            success=False,
            error=f"Policy change {change_id} is not in PROPOSED status (current: {change.status})",
        )

    if approver_id == change.proposed_by:
        return PolicyManagerResult(
            success=False,
            error=f"Self-approval not allowed: {approver_id} proposed and cannot also approve",
        )

    now = int(time.time() * 1000)
    now_iso = datetime.fromtimestamp(now / 1000, tz=timezone.utc).isoformat()

    change.status = "APPROVED"
    change.approved_by = approver_id
    change.resolved_at = now
    change.resolved_at_iso = now_iso

    # Save the new version's rules file
    filename = f"policy_rules_v{change.new_version.replace('.', '_')}.json"
    _save_rules_file(filename, change.proposed_rules, change.new_version)

    # Register the new version (but do not activate yet)
    versions = _load_versions()
    versions["versions"][change.new_version] = {
        "file": filename,
        "activated_at": "",
        "activated_by": "",
        "description": change.change_summary,
        "approved_by": approver_id,
        "approved_at": now_iso,
    }
    _save_versions(versions)

    _write_change_log(change)

    logger.info(
        "Policy change %s approved by %s — version %s ready for activation",
        change_id, approver_id, change.new_version,
    )

    return PolicyManagerResult(
        success=True,
        change=change,
        version=change.new_version,
    )


def activate_policy_version(
    version: str,
    activated_by: str,
    activated_by_role: str,
) -> PolicyManagerResult:
    """
    Activate a previously approved policy version.

    Only admin role can activate. The version must exist in the versions registry.
    This updates the current_version pointer and reloads the policy engine.

    Args:
        version: The version string to activate (e.g., "1.1").
        activated_by: Identity of the admin activating the version.
        activated_by_role: Role of the activator (must be admin).

    Returns:
        PolicyManagerResult with the activated version and its rules.
    """
    if activated_by_role != "admin":
        return PolicyManagerResult(
            success=False,
            error=f"Role '{activated_by_role}' is not authorized to activate policy versions. Required: admin",
        )

    versions = _load_versions()
    version_info = versions["versions"].get(version)

    if not version_info:
        return PolicyManagerResult(
            success=False,
            error=f"Version {version} not found in versions registry",
        )

    old_version = versions["current_version"]
    if old_version == version:
        return PolicyManagerResult(
            success=False,
            error=f"Version {version} is already the active version",
        )

    now_iso = datetime.now(timezone.utc).isoformat()

    # Update the version registry
    version_info["activated_at"] = now_iso
    version_info["activated_by"] = activated_by
    versions["current_version"] = version
    _save_versions(versions)

    # Load the new rules
    try:
        rules = _load_rules_file(version_info["file"])
    except FileNotFoundError as e:
        return PolicyManagerResult(success=False, error=str(e))

    # Update the main policy_rules.json symlink/copy so the policy engine picks it up
    _update_active_policy(version_info["file"])

    # Reload the policy engine cache
    from ..policy.policy_engine import reload_rules
    reload_rules()

    # Update any pending change that matches this version
    for change in _pending_changes.values():
        if change.new_version == version and change.status == "APPROVED":
            change.status = "ACTIVATED"
            _write_change_log(change)

    logger.info(
        "Policy version %s activated by %s (was %s) — %d rules loaded",
        version, activated_by, old_version, len(rules),
    )

    return PolicyManagerResult(
        success=True,
        version=version,
        rules=rules,
    )


def rollback_policy_version(
    target_version: str,
    rolled_back_by: str,
    rolled_back_by_role: str,
) -> PolicyManagerResult:
    """
    Rollback to a previous policy version.

    Only admin role can rollback. The target version must exist in the registry.

    Args:
        target_version: The version to rollback to.
        rolled_back_by: Identity of the admin performing the rollback.
        rolled_back_by_role: Role of the admin (must be admin).

    Returns:
        PolicyManagerResult with the rolled-back version and its rules.
    """
    if rolled_back_by_role != "admin":
        return PolicyManagerResult(
            success=False,
            error=f"Role '{rolled_back_by_role}' is not authorized to rollback policy versions. Required: admin",
        )

    versions = _load_versions()
    version_info = versions["versions"].get(target_version)

    if not version_info:
        return PolicyManagerResult(
            success=False,
            error=f"Target version {target_version} not found in versions registry",
        )

    old_version = versions["current_version"]
    if old_version == target_version:
        return PolicyManagerResult(
            success=False,
            error=f"Version {target_version} is already the active version",
        )

    now = int(time.time() * 1000)
    now_iso = datetime.fromtimestamp(now / 1000, tz=timezone.utc).isoformat()

    # Create a rollback change record
    change_id = f"POL-CHG-{uuid.uuid4().hex[:8].upper()}"
    change = PolicyChange(
        change_id=change_id,
        old_version=old_version,
        new_version=target_version,
        proposed_by=rolled_back_by,
        proposed_by_role=rolled_back_by_role,
        approved_by=rolled_back_by,
        status="ROLLED_BACK",
        change_summary=f"Rollback from {old_version} to {target_version}",
        created_at=now,
        created_at_iso=now_iso,
        resolved_at=now,
        resolved_at_iso=now_iso,
    )
    _pending_changes[change_id] = change
    _change_history.append(change)
    _write_change_log(change)

    # Update the version registry
    versions["current_version"] = target_version
    _save_versions(versions)

    # Load the target rules
    try:
        rules = _load_rules_file(version_info["file"])
    except FileNotFoundError as e:
        return PolicyManagerResult(success=False, error=str(e))

    # Update the main policy_rules.json
    _update_active_policy(version_info["file"])

    # Reload the policy engine cache
    from ..policy.policy_engine import reload_rules
    reload_rules()

    logger.info(
        "Policy rolled back from %s to %s by %s",
        old_version, target_version, rolled_back_by,
    )

    return PolicyManagerResult(
        success=True,
        change=change,
        version=target_version,
        rules=rules,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _update_active_policy(rules_filename: str) -> None:
    """
    Copy the versioned rules file to the main policy_rules.json location
    so the policy engine picks up the new rules on reload.
    """
    source = os.path.join(_GOVERNANCE_DIR, rules_filename)
    target = os.path.join(os.path.dirname(_GOVERNANCE_DIR), "policy", "policy_rules.json")

    with open(source, "r") as f:
        data = f.read()
    with open(target, "w") as f:
        f.write(data)

    logger.info("Active policy updated: %s → %s", rules_filename, target)
