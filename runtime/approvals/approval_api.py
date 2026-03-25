"""
RIO Runtime — Approval API

FastAPI router providing HTTP endpoints for the human approval workflow.

Endpoints:
    GET  /approvals                        — List all approval requests
    GET  /approvals/pending                — List only pending approvals
    POST /approvals/{approval_id}/approve  — Approve a pending request
    POST /approvals/{approval_id}/deny     — Deny a pending request

Role enforcement: Only users with role = "manager" or "admin" can approve/deny.
The approver identity and role are passed as query parameters for this reference
implementation. In production, these would come from an authenticated session.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from . import approval_queue, approval_manager

logger = logging.getLogger("rio.approval_api")

router = APIRouter(prefix="/approvals", tags=["approvals"])


# ---------------------------------------------------------------------------
# GET /approvals — List all approval requests
# ---------------------------------------------------------------------------

@router.get("")
@router.get("/")
def list_approvals(status: Optional[str] = Query(None, description="Filter by status: PENDING, APPROVED, DENIED")):
    """List all approval requests, optionally filtered by status."""
    approvals = approval_queue.get_all()

    if status:
        status_upper = status.upper()
        approvals = [a for a in approvals if a.status == status_upper]

    return {
        "count": len(approvals),
        "approvals": [approval_queue.to_dict(a) for a in approvals],
    }


# ---------------------------------------------------------------------------
# GET /approvals/pending — List only pending approvals
# ---------------------------------------------------------------------------

@router.get("/pending")
def list_pending_approvals():
    """List only PENDING approval requests."""
    pending = approval_queue.get_pending()
    return {
        "count": len(pending),
        "approvals": [approval_queue.to_dict(a) for a in pending],
    }


# ---------------------------------------------------------------------------
# POST /approvals/{approval_id}/approve — Approve a pending request
# ---------------------------------------------------------------------------

@router.post("/{approval_id}/approve")
def approve_request(
    approval_id: str,
    approver_id: str = Query(..., description="Identity of the approver"),
    approver_role: str = Query(..., description="Role of the approver (must be manager or admin)"),
):
    """
    Approve a pending request. Resumes the pipeline and executes the action.

    Only users with role = manager or admin can approve.
    """
    result = approval_manager.approve(
        approval_id=approval_id,
        approver_id=approver_id,
        approver_role=approver_role,
    )

    if result.error:
        raise HTTPException(status_code=403 if "not authorized" in result.error else 400, detail=result.error)

    return {
        "status": "APPROVED",
        "approval_id": approval_id,
        "approver_id": approver_id,
        "execution_status": result.execution_result.execution_status.value if result.execution_result else None,
        "receipt_id": result.receipt.receipt_id if result.receipt else None,
        "ledger_entry_id": result.ledger_entry.ledger_entry_id if result.ledger_entry else None,
    }


# ---------------------------------------------------------------------------
# POST /approvals/{approval_id}/deny — Deny a pending request
# ---------------------------------------------------------------------------

@router.post("/{approval_id}/deny")
def deny_request(
    approval_id: str,
    denier_id: str = Query(..., description="Identity of the denier"),
    denier_role: str = Query(..., description="Role of the denier (must be manager or admin)"),
):
    """
    Deny a pending request. Generates a denial receipt and ledger entry.

    Only users with role = manager or admin can deny.
    """
    result = approval_manager.deny(
        approval_id=approval_id,
        denier_id=denier_id,
        denier_role=denier_role,
    )

    if result.error:
        raise HTTPException(status_code=403 if "not authorized" in result.error else 400, detail=result.error)

    return {
        "status": "DENIED",
        "approval_id": approval_id,
        "denier_id": denier_id,
        "receipt_id": result.receipt.receipt_id if result.receipt else None,
        "ledger_entry_id": result.ledger_entry.ledger_entry_id if result.ledger_entry else None,
    }
