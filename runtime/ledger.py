"""
RIO Runtime — Stage 9: Audit Ledger

Appends signed receipts to the append-only audit ledger. Maintains a hash chain
linking each entry to the previous one. Rejects all update and delete operations.

The ledger is the immutable record of all governed actions and is the source
of truth for audit, compliance, forensics, and governance learning.

Spec reference: /spec/audit_ledger_protocol.md, /spec/09_audit_ledger.md
Protocol stage: Step 8 of the 8-step Governed Execution Protocol
Related invariants: INV-03 (Ledger Completeness), INV-04 (Hash Chain Integrity)
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
import uuid
from typing import Any

from .models import LedgerEntry, Receipt
from .state import SystemState

logger = logging.getLogger("rio.ledger")

# ---------------------------------------------------------------------------
# In-memory ledger store (reference skeleton)
# In production, this would be a durable append-only store.
# ---------------------------------------------------------------------------

_ledger: list[LedgerEntry] = []


def append(receipt: Receipt, state: SystemState) -> LedgerEntry:
    """
    Append a receipt to the audit ledger as a new entry.

    The entry is hash-linked to the previous ledger entry. The system state
    is updated with the new ledger head hash.

    Args:
        receipt: The signed Receipt from the Receipt stage.
        state: The current system state.

    Returns:
        The new LedgerEntry that was appended.

    Raises:
        ValueError: If the receipt is missing required fields.
    """
    if not receipt.receipt_id:
        raise ValueError("Cannot append receipt without receipt_id")
    if not receipt.receipt_hash:
        raise ValueError("Cannot append receipt without receipt_hash")

    now = int(time.time() * 1000)
    previous_hash = state.ledger_head_hash

    entry = LedgerEntry(
        ledger_entry_id=str(uuid.uuid4()),
        receipt_id=receipt.receipt_id,
        receipt_hash=receipt.receipt_hash,
        previous_ledger_hash=previous_hash,
        timestamp=now,
    )

    # Compute ledger hash
    entry.ledger_hash = _compute_ledger_hash(entry)

    # Sign ledger entry
    entry.ledger_signature = _sign_ledger_entry(entry)

    # Append to ledger (append-only — no update, no delete)
    _ledger.append(entry)

    # Update system state
    state.update_ledger_head(entry.ledger_hash)

    logger.info(
        "Ledger entry %s appended — receipt=%s, hash=%s, chain_length=%d",
        entry.ledger_entry_id,
        entry.receipt_id,
        entry.ledger_hash[:16] + "...",
        state.ledger_length,
    )

    return entry


def get_ledger() -> list[LedgerEntry]:
    """
    Return the full ledger (read-only copy).

    Returns:
        A copy of all ledger entries in append order.
    """
    return list(_ledger)


def get_entry_by_receipt(receipt_id: str) -> LedgerEntry | None:
    """
    Look up a ledger entry by receipt ID.

    Args:
        receipt_id: The receipt ID to search for.

    Returns:
        The matching LedgerEntry, or None if not found.
    """
    for entry in _ledger:
        if entry.receipt_id == receipt_id:
            return entry
    return None


def verify_chain() -> bool:
    """
    Verify the integrity of the entire ledger hash chain.

    Recomputes each entry's hash and verifies that the previous_ledger_hash
    links are consistent.

    Returns:
        True if the chain is intact, False if any link is broken.
    """
    if not _ledger:
        return True

    for i, entry in enumerate(_ledger):
        # Verify hash linkage
        if i == 0:
            expected_previous = ""
        else:
            expected_previous = _ledger[i - 1].ledger_hash

        if entry.previous_ledger_hash != expected_previous:
            logger.error(
                "Hash chain broken at entry %d (%s): expected previous=%s, got=%s",
                i,
                entry.ledger_entry_id,
                expected_previous,
                entry.previous_ledger_hash,
            )
            return False

        # Verify entry hash
        expected_hash = _compute_ledger_hash(entry)
        if entry.ledger_hash != expected_hash:
            logger.error(
                "Hash mismatch at entry %d (%s): expected=%s, got=%s",
                i,
                entry.ledger_entry_id,
                expected_hash,
                entry.ledger_hash,
            )
            return False

    return True


def reset() -> None:
    """
    Reset the in-memory ledger. For testing only.
    In production, the ledger is never cleared.
    """
    _ledger.clear()


def _compute_ledger_hash(entry: LedgerEntry) -> str:
    """
    Compute the ledger entry hash.

    Formula: SHA-256(receipt_hash + previous_ledger_hash + timestamp)
    """
    data = f"{entry.receipt_hash}{entry.previous_ledger_hash}{entry.timestamp}"
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _sign_ledger_entry(entry: LedgerEntry) -> str:
    """
    Sign the ledger entry hash.

    In a production implementation, this would use ECDSA-secp256k1.
    This reference skeleton returns a placeholder signature.
    """
    return f"ledger_sig:{entry.ledger_hash[:32]}"
