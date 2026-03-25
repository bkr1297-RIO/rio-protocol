"""
RIO Dashboard — Risk Model Admin Routes

Provides admin pages for risk model versioning, editing, approval, activation, and rollback.

Routes:
    GET  /admin/risk-models              — View all risk model versions and active thresholds
    GET  /admin/risk-models/edit         — Edit form for creating a new risk model draft
    POST /admin/risk-models/propose      — Submit a new risk model draft
    POST /admin/risk-models/{change_id}/approve — Approve a pending risk model change
    POST /admin/risk-models/{version}/activate  — Activate an approved risk model version
    POST /admin/risk-models/{version}/rollback  — Rollback to a previous risk model version
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

from runtime.governance import risk_manager
from runtime.governance.governance_ledger import record_governance_change

logger = logging.getLogger("rio.admin.risk_models")

router = APIRouter(prefix="/admin/risk-models", tags=["admin-risk-models"])

# Templates directory
_ADMIN_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
_DASHBOARD_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=[_ADMIN_TEMPLATES_DIR, _DASHBOARD_TEMPLATES_DIR])


# ---------------------------------------------------------------------------
# View pages
# ---------------------------------------------------------------------------

@router.get("", response_class=HTMLResponse)
async def risk_models_list(request: Request):
    """View all risk model versions, active thresholds, pending changes, and history."""
    current = risk_manager.get_current_risk_model()
    versions = risk_manager.get_all_versions()
    pending = risk_manager.get_pending_changes()
    history = risk_manager.get_change_history()

    return templates.TemplateResponse("risk_models.html", {
        "request": request,
        "title": "Risk Model Admin",
        "active_page": "admin_risk",
        "current_version": current.version if current.success else "unknown",
        "current_rules": current.rules if current.success else {},
        "versions": versions.get("versions", {}),
        "pending_changes": [_change_to_dict(c) for c in pending],
        "change_history": [_change_to_dict(c) for c in history],
    })


@router.get("/edit", response_class=HTMLResponse)
async def risk_model_edit(request: Request):
    """Edit form for creating a new risk model draft based on the current version."""
    current = risk_manager.get_current_risk_model()

    return templates.TemplateResponse("risk_models.html", {
        "request": request,
        "title": "Edit Risk Model",
        "active_page": "admin_risk",
        "current_version": current.version if current.success else "unknown",
        "current_rules": current.rules if current.success else {},
        "versions": risk_manager.get_all_versions().get("versions", {}),
        "pending_changes": [_change_to_dict(c) for c in risk_manager.get_pending_changes()],
        "change_history": [_change_to_dict(c) for c in risk_manager.get_change_history()],
        "is_editing": True,
    })


# ---------------------------------------------------------------------------
# Action endpoints
# ---------------------------------------------------------------------------

@router.post("/propose", response_class=HTMLResponse)
async def propose_risk_model(
    request: Request,
    proposed_by: str = Form(...),
    proposed_by_role: str = Form(...),
    change_summary: str = Form(...),
    rules_json: str = Form(...),
):
    """Submit a new risk model draft for approval."""
    try:
        new_rules = json.loads(rules_json)
    except json.JSONDecodeError:
        return RedirectResponse(url="/admin/risk-models?error=invalid_json", status_code=303)

    result = risk_manager.submit_risk_change(
        proposed_by=proposed_by,
        proposed_by_role=proposed_by_role,
        new_rules=new_rules,
        change_summary=change_summary,
    )

    if not result.success:
        logger.warning("Risk model proposal failed: %s", result.error)

    return RedirectResponse(url="/admin/risk-models", status_code=303)


@router.post("/{change_id}/approve", response_class=HTMLResponse)
async def approve_risk_model(
    request: Request,
    change_id: str,
    approver_id: str = Form(...),
    approver_role: str = Form(...),
):
    """Approve a pending risk model change."""
    result = risk_manager.approve_risk_change(
        change_id=change_id,
        approver_id=approver_id,
        approver_role=approver_role,
    )

    if not result.success:
        logger.warning("Risk model approval failed: %s", result.error)

    return RedirectResponse(url="/admin/risk-models", status_code=303)


@router.post("/{version}/activate", response_class=HTMLResponse)
async def activate_risk_model(
    request: Request,
    version: str,
    activated_by: str = Form(...),
    activated_by_role: str = Form(...),
):
    """Activate an approved risk model version."""
    # Get old version for ledger record
    current = risk_manager.get_current_risk_model()
    old_version = current.version if current.success else "unknown"

    result = risk_manager.activate_risk_version(
        version=version,
        activated_by=activated_by,
        activated_by_role=activated_by_role,
    )

    if result.success:
        # Record governance change in ledger
        try:
            record_governance_change(
                change_type="RISK_MODEL_ACTIVATE",
                old_version=old_version,
                new_version=version,
                proposed_by=activated_by,
                approved_by=activated_by,
                change_summary=f"Risk model version {version} activated via admin UI",
            )
        except Exception as e:
            logger.error("Failed to record governance change in ledger: %s", e)
    else:
        logger.warning("Risk model activation failed: %s", result.error)

    return RedirectResponse(url="/admin/risk-models", status_code=303)


@router.post("/{version}/rollback", response_class=HTMLResponse)
async def rollback_risk_model(
    request: Request,
    version: str,
    rolled_back_by: str = Form(...),
    rolled_back_by_role: str = Form(...),
):
    """Rollback to a previous risk model version."""
    current = risk_manager.get_current_risk_model()
    old_version = current.version if current.success else "unknown"

    result = risk_manager.rollback_risk_version(
        target_version=version,
        rolled_back_by=rolled_back_by,
        rolled_back_by_role=rolled_back_by_role,
    )

    if result.success:
        try:
            record_governance_change(
                change_type="RISK_MODEL_ROLLBACK",
                old_version=old_version,
                new_version=version,
                proposed_by=rolled_back_by,
                approved_by=rolled_back_by,
                change_summary=f"Risk model rolled back to version {version} via admin UI",
            )
        except Exception as e:
            logger.error("Failed to record governance change in ledger: %s", e)
    else:
        logger.warning("Risk model rollback failed: %s", result.error)

    return RedirectResponse(url="/admin/risk-models", status_code=303)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _change_to_dict(change) -> dict:
    """Convert a RiskChange object to a dict for templates."""
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
