"""
RIO Runtime — Replay Engine

Re-runs past corpus records through current or alternate policy/risk settings
WITHOUT executing real actions. This is a pure evaluation engine.

Safety guarantees:
    - NEVER calls adapters, connectors, or action handlers
    - NEVER writes execution receipts as real execution
    - NEVER appends simulated runs to the main ledger
    - Optionally writes simulation summaries to:
        runtime/data/simulations.jsonl

Use cases:
    - Policy testing: "What would happen if we changed the threshold?"
    - Risk threshold tuning: "How many requests would be blocked at risk > 7?"
    - Audit review: "Re-evaluate this request under current policy"
    - Governance learning: "Compare old vs new policy outcomes"

Spec reference: /spec/governed_execution_protocol.md
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..models import Decision, Intent, PolicyRiskResult, RiskCategory
from ..policy_risk import evaluate as evaluate_policy_risk
from .corpus_schema import CorpusRecord, from_dict

logger = logging.getLogger("rio.replay")

# ---------------------------------------------------------------------------
# Simulation output file
# ---------------------------------------------------------------------------

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_SIMULATIONS_FILE = os.path.join(_DATA_DIR, "simulations.jsonl")


# ---------------------------------------------------------------------------
# Simulation Result
# ---------------------------------------------------------------------------

@dataclass
class SimulationResult:
    """
    Result of replaying a corpus record under current or alternate settings.

    Compares the original decision/risk with the simulated re-evaluation.
    """
    simulation_id: str = field(default_factory=lambda: f"SIM-{uuid.uuid4().hex[:8].upper()}")
    request_id: str = ""
    corpus_id: str = ""

    # Original values (from corpus)
    original_decision: str = ""
    original_risk_score: float = 0.0
    original_risk_level: str = ""
    original_policy_rule_id: str = ""
    original_execution_status: str = ""

    # Simulated values (from re-evaluation)
    simulated_decision: str = ""
    simulated_risk_score: float = 0.0
    simulated_risk_level: str = ""
    simulated_policy_rule_id: str = ""

    # Comparison
    decision_changed: bool = False
    risk_score_delta: float = 0.0
    policy_version_used: str = ""
    notes: str = ""

    # Metadata
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))
    executed_real_action: bool = False  # MUST always be False


def to_dict(result: SimulationResult) -> Dict[str, Any]:
    """Serialize a SimulationResult to a dictionary."""
    return {
        "simulation_id": result.simulation_id,
        "request_id": result.request_id,
        "corpus_id": result.corpus_id,
        "original_decision": result.original_decision,
        "original_risk_score": result.original_risk_score,
        "original_risk_level": result.original_risk_level,
        "original_policy_rule_id": result.original_policy_rule_id,
        "original_execution_status": result.original_execution_status,
        "simulated_decision": result.simulated_decision,
        "simulated_risk_score": result.simulated_risk_score,
        "simulated_risk_level": result.simulated_risk_level,
        "simulated_policy_rule_id": result.simulated_policy_rule_id,
        "decision_changed": result.decision_changed,
        "risk_score_delta": result.risk_score_delta,
        "policy_version_used": result.policy_version_used,
        "notes": result.notes,
        "timestamp": result.timestamp,
        "timestamp_iso": datetime.fromtimestamp(
            result.timestamp / 1000, tz=timezone.utc
        ).isoformat(),
        "executed_real_action": result.executed_real_action,
    }


# ---------------------------------------------------------------------------
# Replay single record
# ---------------------------------------------------------------------------

def replay_record(
    record: CorpusRecord,
    policy_version: str = "",
    override_role: str = "",
    override_parameters: Optional[Dict[str, Any]] = None,
) -> SimulationResult:
    """
    Replay a single corpus record through the policy/risk engine.

    This ONLY re-evaluates the policy and risk decision. It does NOT:
    - Call any adapter or connector
    - Generate real receipts or ledger entries
    - Modify system state

    Args:
        record: The corpus record to replay.
        policy_version: Optional policy version to use (empty = current).
        override_role: Optional role override for the simulation.
        override_parameters: Optional parameter overrides.

    Returns:
        A SimulationResult comparing original vs simulated outcomes.
    """
    sim = SimulationResult()
    sim.request_id = record.request_id
    sim.corpus_id = record.corpus_id

    # Populate original values from corpus
    sim.original_decision = record.policy_decision
    sim.original_risk_score = record.risk_score
    sim.original_risk_level = record.risk_level
    sim.original_policy_rule_id = record.policy_rule_id
    sim.original_execution_status = record.execution_status

    # Build a synthetic intent for re-evaluation
    intent = Intent(
        intent_id=f"SIM-{record.intent_id}",
        request_id=record.request_id,
        action_type=record.action_type,
        target_resource=record.target_resource,
        parameters=override_parameters if override_parameters else dict(record.parameters),
        requested_by=record.requested_by,
        justification=record.justification,
    )

    # Determine role for simulation
    role = override_role if override_role else record.requester_role
    if not role:
        role = "employee"

    # Re-evaluate through policy/risk engine
    # SAFETY: This only evaluates rules — no execution, no state mutation
    try:
        policy_result = evaluate_policy_risk(intent, role=role)

        sim.simulated_decision = policy_result.decision.value
        sim.simulated_risk_score = policy_result.risk_score
        sim.simulated_risk_level = policy_result.risk_level
        sim.simulated_policy_rule_id = policy_result.policy_rule_id
    except Exception as e:
        sim.simulated_decision = "ERROR"
        sim.notes = f"Simulation error: {str(e)}"
        logger.error("Replay error for %s: %s", record.request_id, str(e))
        return sim

    # Compare
    sim.decision_changed = sim.original_decision != sim.simulated_decision
    sim.risk_score_delta = sim.simulated_risk_score - sim.original_risk_score
    sim.policy_version_used = policy_version if policy_version else "current"

    # Generate comparison notes
    notes_parts = []
    if sim.decision_changed:
        notes_parts.append(
            f"Decision changed: {sim.original_decision} -> {sim.simulated_decision}"
        )
    else:
        notes_parts.append(f"Decision unchanged: {sim.simulated_decision}")

    if abs(sim.risk_score_delta) > 0.01:
        notes_parts.append(
            f"Risk score delta: {sim.risk_score_delta:+.2f} "
            f"({sim.original_risk_score:.2f} -> {sim.simulated_risk_score:.2f})"
        )

    if override_role:
        notes_parts.append(f"Role overridden: {record.requester_role} -> {override_role}")

    sim.notes = "; ".join(notes_parts)

    # SAFETY: Confirm no real action was executed
    sim.executed_real_action = False

    logger.info(
        "Replay %s: original=%s simulated=%s changed=%s",
        record.request_id,
        sim.original_decision,
        sim.simulated_decision,
        sim.decision_changed,
    )

    return sim


# ---------------------------------------------------------------------------
# Batch replay
# ---------------------------------------------------------------------------

def replay_batch(
    records: List[CorpusRecord],
    policy_version: str = "",
    override_role: str = "",
) -> List[SimulationResult]:
    """
    Replay multiple corpus records and return all simulation results.

    Args:
        records: List of corpus records to replay.
        policy_version: Optional policy version to use.
        override_role: Optional role override for all records.

    Returns:
        List of SimulationResults.
    """
    results = []
    for record in records:
        sim = replay_record(
            record,
            policy_version=policy_version,
            override_role=override_role,
        )
        results.append(sim)

    logger.info(
        "Batch replay complete: %d records, %d decisions changed",
        len(results),
        sum(1 for r in results if r.decision_changed),
    )

    return results


# ---------------------------------------------------------------------------
# Persistence (simulations.jsonl — separate from main ledger)
# ---------------------------------------------------------------------------

def save_simulation_results(results: List[SimulationResult]) -> str:
    """
    Save simulation results to simulations.jsonl.

    SAFETY: This writes to a SEPARATE file from the main ledger.
    Simulation results are never mixed with real execution records.

    Args:
        results: List of SimulationResults to persist.

    Returns:
        The simulation batch ID.
    """
    os.makedirs(_DATA_DIR, exist_ok=True)
    batch_id = f"BATCH-{uuid.uuid4().hex[:8].upper()}"

    with open(_SIMULATIONS_FILE, "a") as fh:
        for sim in results:
            data = to_dict(sim)
            data["batch_id"] = batch_id
            fh.write(json.dumps(data, default=str) + "\n")

    logger.info(
        "Saved %d simulation results to simulations.jsonl (batch=%s)",
        len(results),
        batch_id,
    )
    return batch_id


def read_simulations() -> List[Dict[str, Any]]:
    """Read all simulation results from simulations.jsonl."""
    if not os.path.exists(_SIMULATIONS_FILE):
        return []
    records = []
    with open(_SIMULATIONS_FILE, "r") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed JSONL line in simulations")
    return records


def clear_simulations() -> None:
    """Remove the simulations file. For testing only."""
    if os.path.exists(_SIMULATIONS_FILE):
        os.remove(_SIMULATIONS_FILE)
    logger.info("Simulations file cleared")
