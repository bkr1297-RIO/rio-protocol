"""
RIO Runtime — Governed Corpus Store

Writes one structured corpus record for every completed request.
Records are derived from the full PipelineResult, combining data from
every stage: request + intent + policy/risk + authorization + execution +
receipt + ledger.

Corpus records are persisted to:
    runtime/data/governed_corpus.jsonl

The corpus is append-only and never modified. It serves as the system's
structured decision history for audit, replay, and governance learning.

Safety:
    - Corpus writes are read-only reflections of pipeline results
    - Corpus writes never trigger execution or modify system state
    - Corpus records are separate from the main ledger
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .corpus_schema import CorpusRecord, to_dict, from_dict, validate_record

logger = logging.getLogger("rio.corpus")

# ---------------------------------------------------------------------------
# File path
# ---------------------------------------------------------------------------

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_CORPUS_FILE = os.path.join(_DATA_DIR, "governed_corpus.jsonl")


def _ensure_data_dir() -> None:
    """Create the data directory if it doesn't exist."""
    os.makedirs(_DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

def write_corpus_record(record: CorpusRecord) -> str:
    """
    Persist a corpus record to governed_corpus.jsonl.

    Args:
        record: A fully populated CorpusRecord.

    Returns:
        The corpus_id of the written record.
    """
    _ensure_data_dir()
    data = to_dict(record)
    # Add ISO timestamp for human readability
    data["corpus_timestamp_iso"] = datetime.fromtimestamp(
        record.corpus_timestamp / 1000, tz=timezone.utc
    ).isoformat()

    with open(_CORPUS_FILE, "a") as fh:
        fh.write(json.dumps(data, default=str) + "\n")

    logger.info(
        "Corpus record %s written — request=%s action=%s decision=%s status=%s",
        record.corpus_id,
        record.request_id,
        record.action_type,
        record.policy_decision,
        record.execution_status,
    )
    return record.corpus_id


def build_corpus_record(pipeline_result: Any) -> Optional[CorpusRecord]:
    """
    Build a CorpusRecord from a PipelineResult.

    Extracts data from all pipeline stage artifacts to create a comprehensive
    corpus record. Returns None if the pipeline result lacks essential data
    (e.g., pending approval with no receipt yet).

    Args:
        pipeline_result: A PipelineResult from the governed execution pipeline.

    Returns:
        A CorpusRecord, or None if the result is incomplete.
    """
    result = pipeline_result

    # Skip incomplete results (pending approval, no receipt)
    if result.pending_approval:
        logger.debug("Skipping corpus write — pending approval")
        return None
    if result.receipt is None:
        logger.debug("Skipping corpus write — no receipt")
        return None

    record = CorpusRecord()

    # --- Request ---
    if result.request:
        record.request_id = result.request.request_id
        record.requested_by = result.request.actor_id
        record.request_timestamp = result.request.timestamp

    # --- Intent ---
    if result.intent:
        record.intent_id = result.intent.intent_id
        record.action_type = result.intent.action_type
        record.target_resource = result.intent.target_resource
        record.parameters = dict(result.intent.parameters)
        record.justification = result.intent.justification
        record.requester_role = getattr(result.intent, "requester_role", "")

    # --- Authorization ---
    if result.authorization:
        record.authorization_id = result.authorization.authorization_id
        record.approved_by = result.authorization.approver_id
        record.approver_role = getattr(result.authorization, "approver_role", "")
        record.authority_scope = getattr(result.authorization, "authority_scope", "")
        record.policy_decision = result.authorization.decision.value

    # --- Execution ---
    if result.execution_result:
        record.execution_status = result.execution_result.execution_status.value
        record.adapter_id = getattr(result.execution_result, "adapter_id", "")
        record.external_reference = getattr(result.execution_result, "external_reference", "")
    elif result.receipt:
        record.execution_status = result.receipt.execution_status.value

    # --- Receipt ---
    if result.receipt:
        record.receipt_id = result.receipt.receipt_id
        record.receipt_hash = result.receipt.receipt_hash
        record.receipt_signature = result.receipt.signature
        record.execution_timestamp = result.receipt.execution_timestamp
        record.risk_score = result.receipt.risk_score
        record.risk_level = result.receipt.risk_level
        record.policy_rule_id = result.receipt.policy_rule_id
        # Override policy_decision from receipt if available
        if result.receipt.policy_decision:
            record.policy_decision = result.receipt.policy_decision

    # --- Ledger ---
    if result.ledger_entry:
        record.ledger_entry_id = result.ledger_entry.ledger_entry_id
        record.ledger_hash = result.ledger_entry.ledger_hash

    # --- Pipeline metadata ---
    record.pipeline_duration_ms = result.duration_ms
    record.stages_completed = list(result.stages_completed)

    # --- Outcome summary ---
    if result.success:
        record.outcome_summary = f"EXECUTED: {record.action_type} completed successfully"
    elif result.error:
        record.outcome_summary = f"FAILED: {result.error}"
    elif record.execution_status == "BLOCKED":
        record.outcome_summary = f"BLOCKED: {record.action_type} denied by policy"
    elif record.execution_status == "KILL_SWITCH_BLOCKED":
        record.outcome_summary = f"KILL_SWITCH: {record.action_type} blocked by emergency kill switch"
    else:
        record.outcome_summary = f"{record.execution_status}: {record.action_type}"

    # Infer requester_role from raw_input if not set
    if not record.requester_role and result.request:
        record.requester_role = result.request.raw_input.get("role", "employee")

    # Infer policy_reason from receipt fields
    if result.receipt and result.receipt.policy_rule_id:
        record.policy_reason = f"Rule {result.receipt.policy_rule_id}"

    return record


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

def read_corpus() -> List[CorpusRecord]:
    """Read all corpus records from governed_corpus.jsonl."""
    if not os.path.exists(_CORPUS_FILE):
        return []
    records = []
    with open(_CORPUS_FILE, "r") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    records.append(from_dict(data))
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed JSONL line in corpus")
    return records


def read_corpus_dicts() -> List[Dict[str, Any]]:
    """Read all corpus records as raw dictionaries."""
    if not os.path.exists(_CORPUS_FILE):
        return []
    records = []
    with open(_CORPUS_FILE, "r") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed JSONL line in corpus")
    return records


def get_corpus_record(request_id: str) -> Optional[CorpusRecord]:
    """Look up a corpus record by request_id."""
    for record in read_corpus():
        if record.request_id == request_id:
            return record
    return None


def get_corpus_stats() -> Dict[str, Any]:
    """Compute summary statistics from the corpus."""
    records = read_corpus()
    total = len(records)
    if total == 0:
        return {"total": 0}

    decisions = {}
    statuses = {}
    actions = {}
    for r in records:
        decisions[r.policy_decision] = decisions.get(r.policy_decision, 0) + 1
        statuses[r.execution_status] = statuses.get(r.execution_status, 0) + 1
        actions[r.action_type] = actions.get(r.action_type, 0) + 1

    return {
        "total": total,
        "decisions": decisions,
        "statuses": statuses,
        "actions": actions,
    }


def clear_corpus() -> None:
    """Remove the corpus file. For testing only."""
    if os.path.exists(_CORPUS_FILE):
        os.remove(_CORPUS_FILE)
    logger.info("Corpus file cleared")
