"""
RIO Runtime — Data Store (JSONL Persistence)

Writes structured records to append-only JSONL files so that the
Audit Dashboard (and any external tool) can read the full history
of requests, receipts, and ledger entries.

Files:
    runtime/data/requests.jsonl   — one JSON object per intake request
    runtime/data/receipts.jsonl   — one JSON object per receipt
    runtime/data/ledger.jsonl     — one JSON object per ledger entry

Also persists kill-switch state to:
    runtime/data/system_state.json

All writes are append-only (except system_state.json which is overwritten).
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from .models import (
    Authorization,
    Decision,
    ExecutionStatus,
    Intent,
    LedgerEntry,
    Receipt,
    Request,
)

logger = logging.getLogger("rio.data_store")

# ---------------------------------------------------------------------------
# File paths
# ---------------------------------------------------------------------------

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_REQUESTS_FILE = os.path.join(_DATA_DIR, "requests.jsonl")
_RECEIPTS_FILE = os.path.join(_DATA_DIR, "receipts.jsonl")
_LEDGER_FILE = os.path.join(_DATA_DIR, "ledger.jsonl")
_STATE_FILE = os.path.join(_DATA_DIR, "system_state.json")
_APPROVALS_FILE = os.path.join(_DATA_DIR, "approvals.jsonl")


def _ensure_data_dir() -> None:
    """Create the data directory if it doesn't exist."""
    os.makedirs(_DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def _append_jsonl(filepath: str, record: Dict[str, Any]) -> None:
    """Append a single JSON record to a JSONL file."""
    _ensure_data_dir()
    with open(filepath, "a") as fh:
        fh.write(json.dumps(record, default=str) + "\n")


def write_request(
    request: Request,
    role: str = "employee",
) -> None:
    """Persist a request record to requests.jsonl."""
    record = {
        "request_id": request.request_id,
        "actor_id": request.actor_id,
        "action_type": request.raw_input.get("action_type", "unknown"),
        "target_resource": request.raw_input.get("target_resource", ""),
        "justification": request.raw_input.get("justification", ""),
        "role": role,
        "timestamp": request.timestamp,
        "timestamp_iso": datetime.fromtimestamp(
            request.timestamp / 1000, tz=timezone.utc
        ).isoformat(),
        "source_ip": request.source_ip,
        "authenticated": request.authenticated,
    }
    _append_jsonl(_REQUESTS_FILE, record)
    logger.debug("Request %s written to data store", request.request_id)


def write_receipt(
    receipt: Receipt,
    risk_score: float = 0.0,
    risk_level: str = "",
    policy_rule_id: str = "",
    policy_decision: str = "",
    connector_id: str = "",
) -> None:
    """Persist a receipt record to receipts.jsonl."""
    record = {
        "receipt_id": receipt.receipt_id,
        "request_id": receipt.request_id,
        "intent_id": receipt.intent_id,
        "authorization_id": receipt.authorization_id,
        "action_type": receipt.action_type,
        "decision": receipt.decision.value,
        "execution_status": receipt.execution_status.value,
        "execution_timestamp": receipt.execution_timestamp,
        "timestamp_iso": datetime.fromtimestamp(
            receipt.execution_timestamp / 1000, tz=timezone.utc
        ).isoformat(),
        "risk_score": receipt.risk_score,
        "risk_level": receipt.risk_level,
        "policy_rule_id": receipt.policy_rule_id,
        "policy_decision": receipt.policy_decision,
        "receipt_hash": receipt.receipt_hash,
        "signature": receipt.signature,
        "previous_receipt_hash": receipt.previous_receipt_hash,
        "result_hash": receipt.result_hash,
        "connector_id": connector_id,
    }
    _append_jsonl(_RECEIPTS_FILE, record)
    logger.debug("Receipt %s written to data store", receipt.receipt_id)


def write_ledger_entry(entry: LedgerEntry) -> None:
    """Persist a ledger entry to ledger.jsonl."""
    record = {
        "ledger_entry_id": entry.ledger_entry_id,
        "receipt_id": entry.receipt_id,
        "receipt_hash": entry.receipt_hash,
        "previous_ledger_hash": entry.previous_ledger_hash,
        "ledger_hash": entry.ledger_hash,
        "ledger_signature": entry.ledger_signature,
        "timestamp": entry.timestamp,
        "timestamp_iso": datetime.fromtimestamp(
            entry.timestamp / 1000, tz=timezone.utc
        ).isoformat(),
    }
    _append_jsonl(_LEDGER_FILE, record)
    logger.debug("Ledger entry %s written to data store", entry.ledger_entry_id)


# ---------------------------------------------------------------------------
# System state persistence (kill switch, versions, counters)
# ---------------------------------------------------------------------------

def write_system_state(
    kill_switch_active: bool = False,
    kill_switch_engaged_by: str = "",
    kill_switch_engaged_at: int = 0,
    policy_version: str = "1.0.0",
    risk_model_version: str = "1.0.0",
    ledger_length: int = 0,
) -> None:
    """Overwrite the system state file."""
    _ensure_data_dir()
    state = {
        "kill_switch_active": kill_switch_active,
        "kill_switch_engaged_by": kill_switch_engaged_by,
        "kill_switch_engaged_at": kill_switch_engaged_at,
        "policy_version": policy_version,
        "risk_model_version": risk_model_version,
        "ledger_length": ledger_length,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    with open(_STATE_FILE, "w") as fh:
        json.dump(state, fh, indent=2)
    logger.debug("System state written to data store")


# ---------------------------------------------------------------------------
# Read helpers (used by the dashboard)
# ---------------------------------------------------------------------------

def _read_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Read all records from a JSONL file."""
    if not os.path.exists(filepath):
        return []
    records = []
    with open(filepath, "r") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("Skipping malformed JSONL line in %s", filepath)
    return records


def read_requests() -> List[Dict[str, Any]]:
    """Read all request records."""
    return _read_jsonl(_REQUESTS_FILE)


def read_receipts() -> List[Dict[str, Any]]:
    """Read all receipt records."""
    return _read_jsonl(_RECEIPTS_FILE)


def read_ledger() -> List[Dict[str, Any]]:
    """Read all ledger entries."""
    return _read_jsonl(_LEDGER_FILE)


def read_system_state() -> Dict[str, Any]:
    """Read the current system state."""
    if not os.path.exists(_STATE_FILE):
        return {
            "kill_switch_active": False,
            "kill_switch_engaged_by": "",
            "kill_switch_engaged_at": 0,
            "policy_version": "1.0.0",
            "risk_model_version": "1.0.0",
            "ledger_length": 0,
            "last_updated": "",
        }
    with open(_STATE_FILE, "r") as fh:
        return json.load(fh)


def write_approval(approval) -> None:
    """Persist an approval record to approvals.jsonl."""
    from .approvals.approval_queue import to_dict
    record = to_dict(approval)
    _append_jsonl(_APPROVALS_FILE, record)
    logger.debug("Approval %s written to data store", approval.approval_id)


def read_approvals() -> List[Dict[str, Any]]:
    """Read all approval records."""
    return _read_jsonl(_APPROVALS_FILE)


def clear_data_files() -> None:
    """Remove all JSONL data files. For testing only."""
    for f in [_REQUESTS_FILE, _RECEIPTS_FILE, _LEDGER_FILE, _STATE_FILE, _APPROVALS_FILE]:
        if os.path.exists(f):
            os.remove(f)
    logger.info("Data store files cleared")
