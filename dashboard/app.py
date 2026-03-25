"""
RIO Audit Dashboard — FastAPI Application

Provides a web interface for monitoring the governed execution system.
Reads from JSONL data files written by the runtime pipeline and exposes
kill switch controls via POST endpoints.

Pages:
    /           — System overview with summary cards and kill switch status
    /requests   — Table of all intake requests
    /receipts   — Table of all cryptographic receipts
    /ledger     — Table of all ledger entries (hash chain)
    /approvals  — Human approval queue with approve/deny controls

API Endpoints:
    POST /api/kill-switch/engage    — Engage the EKS-0 kill switch
    POST /api/kill-switch/disengage — Disengage the EKS-0 kill switch

Run with:
    cd rio-protocol
    python -m dashboard.app
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so we can import runtime modules
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from runtime import data_store, kill_switch
from runtime.state import SystemState
from runtime.approvals.approval_api import router as approval_router
from runtime.approvals import approval_manager

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("rio.dashboard")

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="RIO Audit Dashboard", version="1.0.0")
app.include_router(approval_router, prefix="/api")

DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(DASHBOARD_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(DASHBOARD_DIR, "templates"))

# ---------------------------------------------------------------------------
# Shared runtime state (in-memory, synchronized with data files)
# ---------------------------------------------------------------------------
_runtime_state = SystemState()


def _sync_state_from_disk() -> None:
    """Load persisted system state from disk into the in-memory state object."""
    state_data = data_store.read_system_state()
    _runtime_state.kill_switch_active = state_data.get("kill_switch_active", False)
    _runtime_state.kill_switch_engaged_by = state_data.get("kill_switch_engaged_by", "")
    _runtime_state.kill_switch_engaged_at = state_data.get("kill_switch_engaged_at", 0)
    _runtime_state.policy_version = state_data.get("policy_version", "1.0.0")
    _runtime_state.risk_model_version = state_data.get("risk_model_version", "1.0.0")
    _runtime_state.ledger_length = state_data.get("ledger_length", 0)


def _compute_stats(receipts: list[dict], approvals: list[dict] | None = None) -> dict:
    """Compute summary statistics from receipt records."""
    requests_data = data_store.read_requests()
    total = len(requests_data)
    allowed = sum(1 for r in receipts if r.get("decision") == "ALLOW")
    denied = sum(1 for r in receipts if r.get("decision") == "DENY")
    executed = sum(1 for r in receipts if r.get("execution_status") == "EXECUTED")
    blocked = sum(
        1 for r in receipts
        if r.get("execution_status") in ("BLOCKED", "KILL_SWITCH_BLOCKED")
    )
    failed = sum(1 for r in receipts if r.get("execution_status") == "FAILED")
    pending_approvals = 0
    if approvals:
        pending_approvals = sum(1 for a in approvals if a.get("status") == "PENDING")
    return {
        "total_requests": total,
        "allowed": allowed,
        "denied": denied,
        "executed": executed,
        "blocked": blocked,
        "failed": failed,
        "pending_approvals": pending_approvals,
    }


def _enrich_requests(requests: list[dict], receipts: list[dict]) -> list[dict]:
    """
    Join request records with their corresponding receipt data to add
    decision, risk_score, and execution_status to each request row.
    """
    receipt_by_request = {}
    for r in receipts:
        rid = r.get("request_id", "")
        if rid:
            receipt_by_request[rid] = r

    enriched = []
    for req in requests:
        rid = req.get("request_id", "")
        rcpt = receipt_by_request.get(rid, {})
        req["decision"] = rcpt.get("decision", "")
        req["risk_score"] = rcpt.get("risk_score")
        req["execution_status"] = rcpt.get("execution_status", "")
        enriched.append(req)
    return enriched


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """System overview page."""
    _sync_state_from_disk()
    receipts = data_store.read_receipts()
    approvals = data_store.read_approvals()
    stats = _compute_stats(receipts, approvals)
    recent = list(reversed(receipts))[:10]  # Most recent first

    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "RIO Audit Dashboard — Overview",
        "active_page": "home",
        "system_state": {
            "kill_switch_active": _runtime_state.kill_switch_active,
            "kill_switch_engaged_by": _runtime_state.kill_switch_engaged_by,
            "kill_switch_engaged_at": _runtime_state.kill_switch_engaged_at,
            "ledger_length": _runtime_state.ledger_length,
            "policy_version": _runtime_state.policy_version,
            "risk_model_version": _runtime_state.risk_model_version,
        },
        "stats": stats,
        "recent_receipts": recent,
    })


@app.get("/requests", response_class=HTMLResponse)
async def requests_page(request: Request):
    """Requests table page."""
    requests_data = data_store.read_requests()
    receipts_data = data_store.read_receipts()
    enriched = _enrich_requests(requests_data, receipts_data)
    enriched.reverse()  # Most recent first

    return templates.TemplateResponse("requests.html", {
        "request": request,
        "title": "RIO Audit Dashboard — Requests",
        "active_page": "requests",
        "requests": enriched,
    })


@app.get("/receipts", response_class=HTMLResponse)
async def receipts_page(request: Request):
    """Receipts table page."""
    receipts = data_store.read_receipts()
    receipts.reverse()  # Most recent first

    return templates.TemplateResponse("receipts.html", {
        "request": request,
        "title": "RIO Audit Dashboard — Receipts",
        "active_page": "receipts",
        "receipts": receipts,
    })


@app.get("/approvals", response_class=HTMLResponse)
async def approvals_page(request: Request):
    """Approvals queue page."""
    # Read approvals from JSONL, deduplicate by approval_id (keep latest)
    raw_approvals = data_store.read_approvals()
    seen = {}
    for a in raw_approvals:
        seen[a.get("approval_id", "")] = a
    approvals = sorted(seen.values(), key=lambda a: a.get("created_at", 0), reverse=True)

    return templates.TemplateResponse("approvals.html", {
        "request": request,
        "title": "RIO Audit Dashboard — Approvals",
        "active_page": "approvals",
        "approvals": approvals,
    })


@app.get("/ledger", response_class=HTMLResponse)
async def ledger_page(request: Request):
    """Ledger table page."""
    entries = data_store.read_ledger()

    return templates.TemplateResponse("ledger.html", {
        "request": request,
        "title": "RIO Audit Dashboard — Ledger",
        "active_page": "ledger",
        "entries": entries,
    })


# ---------------------------------------------------------------------------
# Kill Switch API
# ---------------------------------------------------------------------------

@app.post("/api/kill-switch/engage")
async def engage_kill_switch():
    """Engage the EKS-0 global execution kill switch."""
    _sync_state_from_disk()

    if _runtime_state.kill_switch_active:
        logger.warning("Kill switch engage requested but already active")
        return RedirectResponse(url="/", status_code=303)

    try:
        event = kill_switch.engage(
            _runtime_state,
            actor_id="dashboard_admin",
            reason="Engaged via Audit Dashboard",
        )

        # Persist updated state
        data_store.write_system_state(
            kill_switch_active=_runtime_state.kill_switch_active,
            kill_switch_engaged_by=_runtime_state.kill_switch_engaged_by,
            kill_switch_engaged_at=_runtime_state.kill_switch_engaged_at,
            policy_version=_runtime_state.policy_version,
            risk_model_version=_runtime_state.risk_model_version,
            ledger_length=_runtime_state.ledger_length,
        )

        # Log kill switch event to ledger JSONL
        _log_kill_switch_event(event)

        logger.info("Kill switch ENGAGED via dashboard")
    except RuntimeError as e:
        logger.error("Kill switch engage failed: %s", e)

    return RedirectResponse(url="/", status_code=303)


@app.post("/api/kill-switch/disengage")
async def disengage_kill_switch():
    """Disengage the EKS-0 global execution kill switch."""
    _sync_state_from_disk()

    if not _runtime_state.kill_switch_active:
        logger.warning("Kill switch disengage requested but not active")
        return RedirectResponse(url="/", status_code=303)

    try:
        event = kill_switch.disengage(
            _runtime_state,
            actor_id="dashboard_admin",
            reason="Disengaged via Audit Dashboard",
        )

        # Persist updated state
        data_store.write_system_state(
            kill_switch_active=_runtime_state.kill_switch_active,
            kill_switch_engaged_by=_runtime_state.kill_switch_engaged_by,
            kill_switch_engaged_at=_runtime_state.kill_switch_engaged_at,
            policy_version=_runtime_state.policy_version,
            risk_model_version=_runtime_state.risk_model_version,
            ledger_length=_runtime_state.ledger_length,
        )

        # Log kill switch event to ledger JSONL
        _log_kill_switch_event(event)

        logger.info("Kill switch DISENGAGED via dashboard")
    except RuntimeError as e:
        logger.error("Kill switch disengage failed: %s", e)

    return RedirectResponse(url="/", status_code=303)


def _log_kill_switch_event(event) -> None:
    """Write a kill switch event as a ledger entry to the JSONL file."""
    now_iso = datetime.fromtimestamp(event.timestamp / 1000, tz=timezone.utc).isoformat()
    record = {
        "ledger_entry_id": f"ks-{event.event_type.lower()}-{event.timestamp}",
        "receipt_id": f"ks-event-{event.event_type.lower()}",
        "receipt_hash": "",
        "previous_ledger_hash": "",
        "ledger_hash": "",
        "ledger_signature": "",
        "timestamp": event.timestamp,
        "timestamp_iso": now_iso,
        "event_type": event.event_type,
        "actor_id": event.actor_id,
        "reason": event.reason,
    }
    data_store._append_jsonl(data_store._LEDGER_FILE, record)
    logger.info("Kill switch %s event logged to ledger", event.event_type)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("DASHBOARD_PORT", 8050))
    logger.info("Starting RIO Audit Dashboard on http://0.0.0.0:%d", port)
    uvicorn.run(app, host="0.0.0.0", port=port)
