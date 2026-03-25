"""
RIO Runtime — Risk Model Manager

Manages risk model versioning, change proposals, approvals, activation, and rollback.
All risk model changes are versioned (old versions are never overwritten) and require
admin approval before activation. Every governance change is recorded in the
risk change log and written to the audit ledger.

Functions:
    get_current_risk_model()        — Return the active risk model version and its rules.
    get_all_versions()              — Return the full versions registry.
    get_pending_changes()           — Return all pending risk model change proposals.
    get_change()                    — Look up a risk model change by ID.
    get_change_history()            — Return the full history of risk model changes.
    submit_risk_change()            — Submit a risk model change proposal for approval.
    approve_risk_change()           — Approve a pending risk model change (admin only).
    activate_risk_version()         — Activate an approved risk model version (admin only).
    rollback_risk_version()         — Rollback to a previous risk model version (admin only).
    read_change_log()               — Read all entries from the risk change log.
    reset()                         — Reset in-memory state (testing only).
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

logger = logging.getLogger("rio.risk_manager")

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

_GOVERNANCE_DIR = os.path.dirname(__file__)
_VERSIONS_FILE = os.path.join(_GOVERNANCE_DIR, "risk_versions.json")
_CHANGE_LOG_FILE = os.path.join(_GOVERNANCE_DIR, "risk_change_log.jsonl")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RiskChange:
    """A proposed risk model change awaiting approval."""
    change_id: str = ""
    old_version: str = ""
    new_version: str = ""
    proposed_by: str = ""
    proposed_by_role: str = ""
    approved_by: str = ""
    status: str = "PROPOSED"       # PROPOSED | APPROVED | ACTIVATED | REJECTED | ROLLED_BACK
    change_summary: str = ""
    proposed_rules: dict = field(default_factory=dict)
    created_at: int = 0
    created_at_iso: str = ""
    resolved_at: int = 0
    resolved_at_iso: str = ""


@dataclass
class RiskManagerResult:
    """Result of a risk manager operation."""
    success: bool = False
    error: str = ""
    change: Optional[RiskChange] = None
    version: str = ""
    rules: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------

_pending_changes: Dict[str, RiskChange] = {}
_change_history: List[RiskChange] = []
_versions_cache: Optional[Dict[str, Any]] = None


def reset() -> None:
    """Reset in-memory state. For testing only."""
    global _pending_changes, _change_history, _versions_cache
    _pending_changes = {}
    _change_history = []
    _versions_cache = None
    logger.info("Risk manager reset")


# ---------------------------------------------------------------------------
# Version file I/O
# ---------------------------------------------------------------------------

def _load_versions() -> Dict[str, Any]:
    """Load and cache the risk model versions registry."""
    global _versions_cache
    if _versions_cache is not None:
        return _versions_cache

    if not os.path.exists(_VERSIONS_FILE):
        _versions_cache = {"current_version": "1.0.0", "versions": {}}
        return _versions_cache

    with open(_VERSIONS_FILE, "r") as f:
        _versions_cache = json.load(f)

    logger.info("Loaded risk versions: current=%s, total=%d",
                _versions_cache["current_version"],
                len(_versions_cache["versions"]))
    return _versions_cache


def _save_versions(data: Dict[str, Any]) -> None:
    """Save the risk model versions registry to disk."""
    global _versions_cache
    _versions_cache = data
    with open(_VERSIONS_FILE, "w") as f:
        json.dump(data, f, indent=2)
    logger.info("Risk versions saved: current=%s", data["current_version"])


def _load_rules_file(filename: str) -> Dict[str, Any]:
    """Load a risk rules file from the governance directory."""
    filepath = os.path.join(_GOVERNANCE_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Risk rules file not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def _save_rules_file(filename: str, rules: Dict[str, Any], version: str) -> None:
    """Save a risk rules file to the governance directory."""
    rules_copy = copy.deepcopy(rules)
    rules_copy["version"] = version
    rules_copy["description"] = f"RIO Risk Rules — version {version}"
    filepath = os.path.join(_GOVERNANCE_DIR, filename)
    with open(filepath, "w") as f:
        json.dump(rules_copy, f, indent=2)
    logger.info("Risk rules file saved: %s", filename)


# ---------------------------------------------------------------------------
# Change log persistence
# ---------------------------------------------------------------------------

def _write_change_log(change: RiskChange) -> None:
    """Append a change record to the risk change log."""
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
    logger.debug("Risk change %s written to change log", change.change_id)


def read_change_log() -> List[Dict[str, Any]]:
    """Read all entries from the risk change log."""
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

def get_current_risk_model() -> RiskManagerResult:
    """Return the active risk model version and its rules."""
    versions = _load_versions()
    current = versions["current_version"]
    version_info = versions["versions"].get(current)

    if not version_info:
        return RiskManagerResult(
            success=False,
            error=f"Current version {current} not found in versions registry",
        )

    try:
        rules = _load_rules_file(version_info["file"])
    except FileNotFoundError as e:
        return RiskManagerResult(success=False, error=str(e))

    return RiskManagerResult(
        success=True,
        version=current,
        rules=rules,
    )


def get_all_versions() -> Dict[str, Any]:
    """Return the full versions registry."""
    return _load_versions()


def get_pending_changes() -> List[RiskChange]:
    """Return all pending risk model change proposals."""
    return [c for c in _pending_changes.values() if c.status == "PROPOSED"]


def get_change(change_id: str) -> Optional[RiskChange]:
    """Look up a risk model change by ID."""
    return _pending_changes.get(change_id)


def get_change_history() -> List[RiskChange]:
    """Return the full history of risk model changes."""
    return list(_change_history)


def submit_risk_change(
    proposed_by: str,
    proposed_by_role: str,
    new_rules: Dict[str, Any],
    change_summary: str,
) -> RiskManagerResult:
    """
    Submit a risk model change proposal for approval.
    Only admin role can submit risk model changes.
    """
    if proposed_by_role != "admin":
        return RiskManagerResult(
            success=False,
            error=f"Role '{proposed_by_role}' is not authorized to propose risk model changes. Required: admin",
        )

    versions = _load_versions()
    current_version = versions["current_version"]

    # Compute next version (increment patch)
    parts = current_version.split(".")
    if len(parts) == 3:
        new_version = f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"
    else:
        new_version = f"{current_version}.1"

    now = int(time.time() * 1000)
    now_iso = datetime.fromtimestamp(now / 1000, tz=timezone.utc).isoformat()

    change_id = f"RISK-CHG-{uuid.uuid4().hex[:8].upper()}"

    change = RiskChange(
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
        "Risk change %s proposed by %s: %s → %s (%s)",
        change_id, proposed_by, current_version, new_version, change_summary,
    )

    return RiskManagerResult(
        success=True,
        change=change,
        version=new_version,
    )


def approve_risk_change(
    change_id: str,
    approver_id: str,
    approver_role: str,
) -> RiskManagerResult:
    """
    Approve a pending risk model change proposal.
    Only admin role can approve. No self-approval.
    """
    if approver_role != "admin":
        return RiskManagerResult(
            success=False,
            error=f"Role '{approver_role}' is not authorized to approve risk model changes. Required: admin",
        )

    change = _pending_changes.get(change_id)
    if not change:
        return RiskManagerResult(
            success=False,
            error=f"Risk change {change_id} not found",
        )

    if change.status != "PROPOSED":
        return RiskManagerResult(
            success=False,
            error=f"Risk change {change_id} is not in PROPOSED status (current: {change.status})",
        )

    if approver_id == change.proposed_by:
        return RiskManagerResult(
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
    filename = f"risk_rules_v{change.new_version.replace('.', '_')}.json"
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
        "Risk change %s approved by %s — version %s ready for activation",
        change_id, approver_id, change.new_version,
    )

    return RiskManagerResult(
        success=True,
        change=change,
        version=change.new_version,
    )


def activate_risk_version(
    version: str,
    activated_by: str,
    activated_by_role: str,
) -> RiskManagerResult:
    """
    Activate a previously approved risk model version.
    Only admin role can activate.
    """
    if activated_by_role != "admin":
        return RiskManagerResult(
            success=False,
            error=f"Role '{activated_by_role}' is not authorized to activate risk model versions. Required: admin",
        )

    versions = _load_versions()
    version_info = versions["versions"].get(version)

    if not version_info:
        return RiskManagerResult(
            success=False,
            error=f"Version {version} not found in versions registry",
        )

    old_version = versions["current_version"]
    if old_version == version:
        return RiskManagerResult(
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
        return RiskManagerResult(success=False, error=str(e))

    # Update the main risk_rules.json so the risk engine picks it up
    _update_active_risk_model(version_info["file"])

    # Reload the risk engine cache
    from ..policy.risk_engine import reload_rules
    reload_rules()

    # Update any pending change that matches this version
    for change in _pending_changes.values():
        if change.new_version == version and change.status == "APPROVED":
            change.status = "ACTIVATED"
            _write_change_log(change)

    logger.info(
        "Risk model version %s activated by %s (was %s)",
        version, activated_by, old_version,
    )

    return RiskManagerResult(
        success=True,
        version=version,
        rules=rules,
    )


def rollback_risk_version(
    target_version: str,
    rolled_back_by: str,
    rolled_back_by_role: str,
) -> RiskManagerResult:
    """
    Rollback to a previous risk model version.
    Only admin role can rollback.
    """
    if rolled_back_by_role != "admin":
        return RiskManagerResult(
            success=False,
            error=f"Role '{rolled_back_by_role}' is not authorized to rollback risk model versions. Required: admin",
        )

    versions = _load_versions()
    version_info = versions["versions"].get(target_version)

    if not version_info:
        return RiskManagerResult(
            success=False,
            error=f"Target version {target_version} not found in versions registry",
        )

    old_version = versions["current_version"]
    if old_version == target_version:
        return RiskManagerResult(
            success=False,
            error=f"Version {target_version} is already the active version",
        )

    now = int(time.time() * 1000)
    now_iso = datetime.fromtimestamp(now / 1000, tz=timezone.utc).isoformat()

    # Create a rollback change record
    change_id = f"RISK-CHG-{uuid.uuid4().hex[:8].upper()}"
    change = RiskChange(
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
        return RiskManagerResult(success=False, error=str(e))

    # Update the main risk_rules.json
    _update_active_risk_model(version_info["file"])

    # Reload the risk engine cache
    from ..policy.risk_engine import reload_rules
    reload_rules()

    logger.info(
        "Risk model rolled back from %s to %s by %s",
        old_version, target_version, rolled_back_by,
    )

    return RiskManagerResult(
        success=True,
        change=change,
        version=target_version,
        rules=rules,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _update_active_risk_model(rules_filename: str) -> None:
    """
    Copy the versioned rules file to the main risk_rules.json location
    so the risk engine picks up the new rules on reload.
    """
    source = os.path.join(_GOVERNANCE_DIR, rules_filename)
    target = os.path.join(os.path.dirname(_GOVERNANCE_DIR), "policy", "risk_rules.json")

    with open(source, "r") as f:
        data = f.read()
    with open(target, "w") as f:
        f.write(data)

    logger.info("Active risk model updated: %s → %s", rules_filename, target)
