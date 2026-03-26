"""
RIO Runtime — Governed Execution Protocol v2: Ledger Writer

Appends v2 receipts to the audit ledger as hash-chained, signed entries.
Extends the v1 ledger with:

  - v2 receipt fields (intent_hash, action_hash, verification_hash)
  - ISO 8601 timestamps
  - Verification status tracking
  - Denial receipt support

The ledger remains append-only. No update or delete operations are permitted.

Spec reference: /spec/audit_ledger_protocol.md
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from ..receipts.receipt_generator import ReceiptV2

logger = logging.getLogger("rio.ledger_v2.writer")

# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

_KEYS_DIR = os.path.join(os.path.dirname(__file__), "..", "keys")
_PRIVATE_KEY_PATH = os.path.join(_KEYS_DIR, "private_key.pem")
_PUBLIC_KEY_PATH = os.path.join(_KEYS_DIR, "public_key.pem")

_private_key = None


def _load_private_key():
    """Load the RSA private key from disk (lazy, cached)."""
    global _private_key
    if _private_key is not None:
        return _private_key
    with open(_PRIVATE_KEY_PATH, "rb") as fh:
        _private_key = serialization.load_pem_private_key(fh.read(), password=None)
    return _private_key


# ---------------------------------------------------------------------------
# v2 Ledger Entry model
# ---------------------------------------------------------------------------

@dataclass
class LedgerEntryV2:
    """
    Governed Execution Protocol v2 ledger entry.

    Each entry wraps a v2 receipt and links to the previous entry via
    previous_ledger_hash, forming a tamper-evident hash chain.
    """
    ledger_entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    receipt_id: str = ""
    receipt_hash: str = ""
    intent_hash: str = ""
    action_hash: str = ""
    verification_hash: str = ""
    verification_status: str = ""
    decision: str = ""
    action: str = ""
    requested_by: str = ""
    approved_by: str = ""
    timestamp_request: str = ""
    timestamp_execution: str = ""
    previous_ledger_hash: str = ""
    ledger_hash: str = ""
    ledger_signature: str = ""
    timestamp: int = 0  # Epoch ms for backward compat


# ---------------------------------------------------------------------------
# In-memory v2 ledger store
# ---------------------------------------------------------------------------

_ledger_v2: list[LedgerEntryV2] = []


def append_v2(receipt: ReceiptV2, previous_ledger_hash: str = "") -> LedgerEntryV2:
    """
    Append a v2 receipt to the v2 audit ledger.

    The entry is hash-linked to the previous ledger entry. If no
    previous_ledger_hash is provided, the last entry's hash is used.

    Args:
        receipt: The signed ReceiptV2 from the receipt stage.
        previous_ledger_hash: Hash of the previous ledger entry (auto-detected
                              from the chain if empty).

    Returns:
        The new LedgerEntryV2 that was appended.
    """
    if not receipt.receipt_id:
        raise ValueError("Cannot append receipt without receipt_id")
    if not receipt.receipt_hash:
        raise ValueError("Cannot append receipt without receipt_hash")

    # Auto-detect previous hash from chain
    if not previous_ledger_hash and _ledger_v2:
        previous_ledger_hash = _ledger_v2[-1].ledger_hash

    now = int(time.time() * 1000)

    entry = LedgerEntryV2(
        ledger_entry_id=str(uuid.uuid4()),
        receipt_id=receipt.receipt_id,
        receipt_hash=receipt.receipt_hash,
        intent_hash=receipt.intent_hash,
        action_hash=receipt.action_hash,
        verification_hash=receipt.verification_hash,
        verification_status=receipt.verification_status,
        decision=receipt.decision,
        action=receipt.action,
        requested_by=receipt.requested_by,
        approved_by=receipt.approved_by,
        timestamp_request=receipt.timestamp_request,
        timestamp_execution=receipt.timestamp_execution,
        previous_ledger_hash=previous_ledger_hash,
        timestamp=now,
    )

    # Compute ledger hash
    entry.ledger_hash = _compute_ledger_hash_v2(entry)

    # Sign ledger entry
    entry.ledger_signature = _sign_ledger_entry(entry)

    # Append (append-only — no update, no delete)
    _ledger_v2.append(entry)

    logger.info(
        "v2 Ledger entry %s appended — receipt=%s decision=%s verification=%s chain_length=%d",
        entry.ledger_entry_id,
        entry.receipt_id,
        entry.decision,
        entry.verification_status,
        len(_ledger_v2),
    )

    return entry


def get_ledger_v2() -> list[LedgerEntryV2]:
    """Return the full v2 ledger (read-only copy)."""
    return list(_ledger_v2)


def get_entry_by_receipt_v2(receipt_id: str) -> Optional[LedgerEntryV2]:
    """Look up a v2 ledger entry by receipt ID."""
    for entry in _ledger_v2:
        if entry.receipt_id == receipt_id:
            return entry
    return None


def get_head_hash() -> str:
    """Return the hash of the most recent ledger entry, or empty string."""
    if _ledger_v2:
        return _ledger_v2[-1].ledger_hash
    return ""


def reset_v2() -> None:
    """Reset the in-memory v2 ledger. For testing only."""
    _ledger_v2.clear()


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------

def _compute_ledger_hash_v2(entry: LedgerEntryV2) -> str:
    """
    Compute the v2 ledger entry hash over all fields.

    Formula: SHA-256(
        entry_id + receipt_id + receipt_hash + intent_hash + action_hash +
        verification_hash + verification_status + decision + action +
        requested_by + approved_by + previous_ledger_hash + timestamp
    )
    """
    data = (
        f"{entry.ledger_entry_id}"
        f"{entry.receipt_id}"
        f"{entry.receipt_hash}"
        f"{entry.intent_hash}"
        f"{entry.action_hash}"
        f"{entry.verification_hash}"
        f"{entry.verification_status}"
        f"{entry.decision}"
        f"{entry.action}"
        f"{entry.requested_by}"
        f"{entry.approved_by}"
        f"{entry.previous_ledger_hash}"
        f"{entry.timestamp}"
    )
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# RSA Signing
# ---------------------------------------------------------------------------

def _sign_ledger_entry(entry: LedgerEntryV2) -> str:
    """Sign the ledger entry hash with the RSA-2048 private key."""
    private_key = _load_private_key()
    signature_bytes = private_key.sign(
        entry.ledger_hash.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature_bytes).decode("utf-8")
