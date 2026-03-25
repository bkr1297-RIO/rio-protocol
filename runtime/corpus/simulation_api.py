"""
RIO Runtime — Simulation API

FastAPI router providing endpoints for corpus replay and simulation.

Safety guarantees:
    - All endpoints are read-only or simulation-only
    - No real actions are ever executed
    - No real receipts or ledger entries are created
    - Simulation results are written to a SEPARATE file (simulations.jsonl)

Endpoints:
    POST /simulate/request/{request_id}  — Replay a single request
    POST /simulate/batch                  — Replay multiple requests
    GET  /simulate/results/{simulation_id} — Retrieve simulation results
    GET  /simulate/results                — List all simulation results
    GET  /corpus                          — List all corpus records
    GET  /corpus/stats                    — Corpus statistics
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from .corpus_store import (
    get_corpus_record,
    get_corpus_stats,
    read_corpus,
    read_corpus_dicts,
)
from .replay_engine import (
    SimulationResult,
    replay_batch,
    replay_record,
    read_simulations,
    save_simulation_results,
    to_dict as sim_to_dict,
)

logger = logging.getLogger("rio.simulation_api")

router = APIRouter(prefix="/api", tags=["simulation"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class SimulateRequestBody(BaseModel):
    """Body for single-request simulation."""
    policy_version: str = ""
    override_role: str = ""
    override_parameters: Optional[Dict[str, Any]] = None


class SimulateBatchBody(BaseModel):
    """Body for batch simulation."""
    request_ids: List[str] = []
    all_records: bool = False
    policy_version: str = ""
    override_role: str = ""


# ---------------------------------------------------------------------------
# Simulation endpoints
# ---------------------------------------------------------------------------

@router.post("/simulate/request/{request_id}")
async def simulate_single_request(
    request_id: str,
    body: SimulateRequestBody = SimulateRequestBody(),
):
    """
    Replay a single corpus record under current or alternate settings.

    SAFETY: No real actions are executed. No real ledger entries are created.
    """
    record = get_corpus_record(request_id)
    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"No corpus record found for request_id={request_id}",
        )

    sim = replay_record(
        record,
        policy_version=body.policy_version,
        override_role=body.override_role,
        override_parameters=body.override_parameters,
    )

    # Save to simulations.jsonl (separate from main ledger)
    batch_id = save_simulation_results([sim])

    return {
        "status": "ok",
        "batch_id": batch_id,
        "simulation": sim_to_dict(sim),
        "safety_check": {
            "executed_real_action": sim.executed_real_action,
            "wrote_to_main_ledger": False,
            "wrote_real_receipt": False,
        },
    }


@router.post("/simulate/batch")
async def simulate_batch(body: SimulateBatchBody):
    """
    Replay multiple corpus records in batch.

    SAFETY: No real actions are executed. No real ledger entries are created.
    """
    if body.all_records:
        records = read_corpus()
    elif body.request_ids:
        records = []
        for rid in body.request_ids:
            record = get_corpus_record(rid)
            if record:
                records.append(record)
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide request_ids or set all_records=true",
        )

    if not records:
        raise HTTPException(
            status_code=404,
            detail="No corpus records found for the given criteria",
        )

    results = replay_batch(
        records,
        policy_version=body.policy_version,
        override_role=body.override_role,
    )

    # Save to simulations.jsonl (separate from main ledger)
    batch_id = save_simulation_results(results)

    decisions_changed = sum(1 for r in results if r.decision_changed)

    return {
        "status": "ok",
        "batch_id": batch_id,
        "total_records": len(results),
        "decisions_changed": decisions_changed,
        "decisions_unchanged": len(results) - decisions_changed,
        "simulations": [sim_to_dict(r) for r in results],
        "safety_check": {
            "executed_real_action": False,
            "wrote_to_main_ledger": False,
            "wrote_real_receipt": False,
        },
    }


@router.get("/simulate/results/{simulation_id}")
async def get_simulation_result(simulation_id: str):
    """Retrieve a specific simulation result by simulation_id."""
    all_sims = read_simulations()
    matches = [s for s in all_sims if s.get("simulation_id") == simulation_id]
    if not matches:
        raise HTTPException(
            status_code=404,
            detail=f"No simulation found with id={simulation_id}",
        )
    return {"status": "ok", "simulation": matches[0]}


@router.get("/simulate/results")
async def list_simulation_results(
    batch_id: str = Query(default="", description="Filter by batch ID"),
    limit: int = Query(default=100, description="Max results to return"),
):
    """List all simulation results, optionally filtered by batch_id."""
    all_sims = read_simulations()
    if batch_id:
        all_sims = [s for s in all_sims if s.get("batch_id") == batch_id]
    return {
        "status": "ok",
        "total": len(all_sims),
        "results": all_sims[-limit:],
    }


# ---------------------------------------------------------------------------
# Corpus read endpoints
# ---------------------------------------------------------------------------

@router.get("/corpus")
async def list_corpus(
    action_type: str = Query(default="", description="Filter by action type"),
    limit: int = Query(default=100, description="Max records to return"),
):
    """List all corpus records."""
    records = read_corpus_dicts()
    if action_type:
        records = [r for r in records if r.get("action_type") == action_type]
    return {
        "status": "ok",
        "total": len(records),
        "records": records[-limit:],
    }


@router.get("/corpus/stats")
async def corpus_stats():
    """Get corpus summary statistics."""
    stats = get_corpus_stats()
    return {"status": "ok", "stats": stats}
