"""
RIO Runtime — Governance API

FastAPI router providing admin-only endpoints for policy management:

    GET  /policy/version     — Get current active policy version and rules
    POST /policy/propose     — Submit a policy change proposal
    POST /policy/approve     — Approve a pending policy change
    POST /policy/activate    — Activate an approved policy version
    POST /policy/rollback    — Rollback to a previous policy version
    GET  /policy/changes     — List all policy change proposals
    GET  /policy/versions    — List all policy versions

All mutating endpoints require admin role.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from . import policy_manager

logger = logging.getLogger("rio.governance_api")

router = APIRouter(prefix="/policy", tags=["governance"])


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class PolicyProposeRequest(BaseModel):
    proposed_by: str
    proposed_by_role: str
    rules: List[Dict[str, Any]]
    change_summary: str


class PolicyApproveRequest(BaseModel):
    change_id: str
    approver_id: str
    approver_role: str


class PolicyActivateRequest(BaseModel):
    version: str
    activated_by: str
    activated_by_role: str


class PolicyRollbackRequest(BaseModel):
    target_version: str
    rolled_back_by: str
    rolled_back_by_role: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/version")
def get_current_version():
    """Return the current active policy version and its rules."""
    result = policy_manager.get_current_policy()
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return {
        "version": result.version,
        "rules": result.rules,
        "rule_count": len(result.rules),
    }


@router.get("/versions")
def get_all_versions():
    """Return all registered policy versions."""
    versions = policy_manager.get_all_versions()
    return versions


@router.get("/changes")
def get_changes(status: Optional[str] = Query(None)):
    """Return policy change history, optionally filtered by status."""
    history = policy_manager.get_change_history()
    if status:
        history = [c for c in history if c.status == status.upper()]
    return {
        "changes": [
            {
                "change_id": c.change_id,
                "old_version": c.old_version,
                "new_version": c.new_version,
                "proposed_by": c.proposed_by,
                "approved_by": c.approved_by,
                "status": c.status,
                "change_summary": c.change_summary,
                "created_at_iso": c.created_at_iso,
                "resolved_at_iso": c.resolved_at_iso,
            }
            for c in history
        ],
        "total": len(history),
    }


@router.get("/pending")
def get_pending_changes():
    """Return all pending (PROPOSED) policy changes."""
    pending = policy_manager.get_pending_changes()
    return {
        "pending": [
            {
                "change_id": c.change_id,
                "old_version": c.old_version,
                "new_version": c.new_version,
                "proposed_by": c.proposed_by,
                "change_summary": c.change_summary,
                "created_at_iso": c.created_at_iso,
                "rule_count": len(c.proposed_rules),
            }
            for c in pending
        ],
        "total": len(pending),
    }


@router.post("/propose")
def propose_policy_change(req: PolicyProposeRequest):
    """Submit a policy change proposal (admin only)."""
    result = policy_manager.submit_policy_change(
        proposed_by=req.proposed_by,
        proposed_by_role=req.proposed_by_role,
        new_rules=req.rules,
        change_summary=req.change_summary,
    )
    if not result.success:
        raise HTTPException(status_code=403, detail=result.error)
    return {
        "change_id": result.change.change_id,
        "new_version": result.version,
        "status": result.change.status,
    }


@router.post("/approve")
def approve_policy_change(req: PolicyApproveRequest):
    """Approve a pending policy change (admin only, no self-approval)."""
    result = policy_manager.approve_policy_change(
        change_id=req.change_id,
        approver_id=req.approver_id,
        approver_role=req.approver_role,
    )
    if not result.success:
        raise HTTPException(status_code=403, detail=result.error)
    return {
        "change_id": result.change.change_id,
        "version": result.version,
        "status": result.change.status,
        "approved_by": result.change.approved_by,
    }


@router.post("/activate")
def activate_policy_version(req: PolicyActivateRequest):
    """Activate an approved policy version (admin only)."""
    result = policy_manager.activate_policy_version(
        version=req.version,
        activated_by=req.activated_by,
        activated_by_role=req.activated_by_role,
    )
    if not result.success:
        raise HTTPException(status_code=403, detail=result.error)
    return {
        "version": result.version,
        "rule_count": len(result.rules),
        "status": "ACTIVATED",
    }


@router.post("/rollback")
def rollback_policy_version(req: PolicyRollbackRequest):
    """Rollback to a previous policy version (admin only)."""
    result = policy_manager.rollback_policy_version(
        target_version=req.target_version,
        rolled_back_by=req.rolled_back_by,
        rolled_back_by_role=req.rolled_back_by_role,
    )
    if not result.success:
        raise HTTPException(status_code=403, detail=result.error)
    return {
        "version": result.version,
        "change_id": result.change.change_id,
        "rule_count": len(result.rules),
        "status": "ROLLED_BACK",
    }
