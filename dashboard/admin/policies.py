"""
RIO Dashboard — Policy Admin Routes

Provides admin pages for policy versioning, editing, approval, activation, and rollback.

Routes:
    GET  /admin/policies                     — View all policy versions and active rules
    GET  /admin/policies/{version}           — View a specific policy version's rules
    GET  /admin/policies/{version}/edit      — Edit form for a policy draft
    POST /admin/policies/propose             — Submit a new policy draft
    POST /admin/policies/{change_id}/approve — Approve a pending policy change
    POST /admin/policies/{version}/activate  — Activate an approved policy version
    POST /admin/policies/{version}/rollback  — Rollback to a previous policy version
"""

from __future__ import annotations

import json
import logging
import os
import sys

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Ensure the runtime package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from runtime.governance import policy_manager
from runtime.governance.governance_ledger import record_governance_change

logger = logging.getLogger("rio.admin.policies")

router = APIRouter(prefix="/admin/policies", tags=["admin-policies"])

# Templates directory — use the admin templates
_ADMIN_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
_DASHBOARD_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=[_ADMIN_TEMPLATES_DIR, _DASHBOARD_TEMPLATES_DIR])


# ---------------------------------------------------------------------------
# View pages
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def policies_list(request: Request):
    """View all policy versions, active rules, pending changes, and change history."""
    current = policy_manager.get_current_policy()
    versions = policy_manager.get_all_versions()
    pending = policy_manager.get_pending_changes()
    history = policy_manager.get_change_history()

    return templates.TemplateResponse("policies.html", {
        "request": request,
        "title": "Policy Admin",
        "active_page": "admin_policies",
        "current_version": current.version if current.success else "unknown",
        "current_rules": current.rules if current.success else [],
        "versions": versions.get("versions", {}),
        "pending_changes": [_change_to_dict(c) for c in pending],
        "change_history": [_change_to_dict(c) for c in history],
    })


@router.get("/{version}", response_class=HTMLResponse)
async def policy_version_detail(request: Request, version: str):
    """View a specific policy version's rules."""
    versions = policy_manager.get_all_versions()
    version_info = versions.get("versions", {}).get(version)

    if not version_info:
        return RedirectResponse(url="/admin/policies", status_code=303)

    try:
        rules_file = version_info.get("file", "")
        governance_dir = os.path.dirname(os.path.dirname(__file__))
        rules_path = os.path.join(governance_dir, "runtime", "governance", rules_file)
        with open(rules_path, "r") as f:
            rules = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        rules = {"rules": []}

    current_version = versions.get("current_version", "")

    return templates.TemplateResponse("policy_edit.html", {
        "request": request,
        "title": f"Policy v{version}",
        "active_page": "admin_policies",
        "version": version,
        "version_info": version_info,
        "rules": rules.get("rules", []),
        "rules_json": json.dumps(rules, indent=2),
        "is_active": version == current_version,
        "is_editable": False,
    })


@router.get("/{version}/edit", response_class=HTMLResponse)
async def policy_version_edit(request: Request, version: str):
    """Edit form for creating a new policy draft based on an existing version."""
    versions = policy_manager.get_all_versions()
    version_info = versions.get("versions", {}).get(version)

    if not version_info:
        return RedirectResponse(url="/admin/policies", status_code=303)

    try:
        rules_file = version_info.get("file", "")
        governance_dir = os.path.dirname(os.path.dirname(__file__))
        rules_path = os.path.join(governance_dir, "runtime", "governance", rules_file)
        with open(rules_path, "r") as f:
            rules = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        rules = {"rules": []}

    return templates.TemplateResponse("policy_edit.html", {
        "request": request,
        "title": f"Edit Policy (based on v{version})",
        "active_page": "admin_policies",
        "version": version,
        "version_info": version_info,
        "rules": rules.get("rules", []),
        "rules_json": json.dumps(rules, indent=2),
        "is_active": False,
        "is_editable": True,
    })


# ---------------------------------------------------------------------------
# Action endpoints
# ---------------------------------------------------------------------------

@router.post("/propose", response_class=HTMLResponse)
async def propose_policy(
    request: Request,
    proposed_by: str = Form(...),
    proposed_by_role: str = Form(...),
    change_summary: str = Form(...),
    rules_json: str = Form(...),
):
    """Submit a new policy draft for approval."""
    try:
        new_rules = json.loads(rules_json)
    except json.JSONDecodeError:
        return RedirectResponse(url="/admin/policies?error=invalid_json", status_code=303)

    result = policy_manager.submit_policy_change(
        proposed_by=proposed_by,
        proposed_by_role=proposed_by_role,
        new_rules=new_rules,
        change_summary=change_summary,
    )

    if not result.success:
        logger.warning("Policy proposal failed: %s", result.error)

    return RedirectResponse(url="/admin/policies", status_code=303)


@router.post("/{change_id}/approve", response_class=HTMLResponse)
async def approve_policy(
    request: Request,
    change_id: str,
    approver_id: str = Form(...),
    approver_role: str = Form(...),
):
    """Approve a pending policy change."""
    result = policy_manager.approve_policy_change(
        change_id=change_id,
        approver_id=approver_id,
        approver_role=approver_role,
    )

    if not result.success:
        logger.warning("Policy approval failed: %s", result.error)

    return RedirectResponse(url="/admin/policies", status_code=303)


@router.post("/{version}/activate", response_class=HTMLResponse)
async def activate_policy(
    request: Request,
    version: str,
    activated_by: str = Form(...),
    activated_by_role: str = Form(...),
):
    """Activate an approved policy version."""
    # Get old version for ledger record
    current = policy_manager.get_current_policy()
    old_version = current.version if current.success else "unknown"

    result = policy_manager.activate_policy_version(
        version=version,
        activated_by=activated_by,
        activated_by_role=activated_by_role,
    )

    if result.success:
        # Record governance change in ledger
        try:
            record_governance_change(
                change_type="POLICY_ACTIVATE",
                old_version=old_version,
                new_version=version,
                proposed_by=activated_by,
                approved_by=activated_by,
                change_summary=f"Policy version {version} activated via admin UI",
            )
        except Exception as e:
            logger.error("Failed to record governance change in ledger: %s", e)
    else:
        logger.warning("Policy activation failed: %s", result.error)

    return RedirectResponse(url="/admin/policies", status_code=303)


@router.post("/{version}/rollback", response_class=HTMLResponse)
async def rollback_policy(
    request: Request,
    version: str,
    rolled_back_by: str = Form(...),
    rolled_back_by_role: str = Form(...),
):
    """Rollback to a previous policy version."""
    # Get current version for ledger record
    current = policy_manager.get_current_policy()
    old_version = current.version if current.success else "unknown"

    result = policy_manager.rollback_policy_version(
        target_version=version,
        rolled_back_by=rolled_back_by,
        rolled_back_by_role=rolled_back_by_role,
    )

    if result.success:
        # Record governance change in ledger
        try:
            record_governance_change(
                change_type="POLICY_ROLLBACK",
                old_version=old_version,
                new_version=version,
                proposed_by=rolled_back_by,
                approved_by=rolled_back_by,
                change_summary=f"Policy rolled back to version {version} via admin UI",
            )
        except Exception as e:
            logger.error("Failed to record governance change in ledger: %s", e)
    else:
        logger.warning("Policy rollback failed: %s", result.error)

    return RedirectResponse(url="/admin/policies", status_code=303)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _change_to_dict(change) -> dict:
    """Convert a PolicyChange or similar object to a dict for templates."""
    return {
        "change_id": getattr(change, "change_id", ""),
        "old_version": getattr(change, "old_version", ""),
        "new_version": getattr(change, "new_version", ""),
        "proposed_by": getattr(change, "proposed_by", ""),
        "approved_by": getattr(change, "approved_by", ""),
        "status": getattr(change, "status", ""),
        "change_summary": getattr(change, "change_summary", ""),
        "created_at_iso": getattr(change, "created_at_iso", ""),
        "resolved_at_iso": getattr(change, "resolved_at_iso", ""),
    }
