"""
RIO Runtime — Stage 9: Audit Ledger

Appends signed receipts to the append-only audit ledger. Maintains a hash chain
linking each entry to the previous one. Rejects all update and delete operations.

The ledger is the immutable record of all governed actions and is the source
of truth for audit, compliance, forensics, and governance learning.

Each ledger entry is signed with the same RSA-2048 private key used for
receipt signing (``runtime/keys/private_key.pem``).  The entry hash is
computed as:

    entry_hash = SHA-256(
        entry_id + receipt_id + receipt_hash + request_id + intent_id +
        authorization_id + decision + action + result_hash +
        previous_hash + timestamp
    )

Spec reference: /spec/audit_ledger_protocol.md, /spec/09_audit_ledger.md
Protocol stage: Step 8 of the 8-step Governed Execution Protocol
Related invariants: INV-03 (Ledger Completeness), INV-04 (Hash Chain Integrity)
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import time
import uuid
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .models import LedgerEntry, Receipt
from .state import SystemState

logger = logging.getLogger("rio.ledger")

# ---------------------------------------------------------------------------
# Key management (reuses the same key pair as receipt.py)
# ---------------------------------------------------------------------------

_KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
_PRIVATE_KEY_PATH = os.path.join(_KEYS_DIR, "private_key.pem")
_PUBLIC_KEY_PATH = os.path.join(_KEYS_DIR, "public_key.pem")

_private_key = None
_public_key = None


def _load_private_key():
    """Load the RSA private key from disk (lazy, cached)."""
    global _private_key
    if _private_key is not None:
        return _private_key
    with open(_PRIVATE_KEY_PATH, "rb") as fh:
        _private_key = serialization.load_pem_private_key(fh.read(), password=None)
    return _private_key


def _load_public_key():
    """Load the RSA public key from disk (lazy, cached)."""
    global _public_key
    if _public_key is not None:
        return _public_key
    with open(_PUBLIC_KEY_PATH, "rb") as fh:
        _public_key = serialization.load_pem_public_key(fh.read())
    return _public_key


# ---------------------------------------------------------------------------
# In-memory ledger store
# ---------------------------------------------------------------------------

_ledger: list[LedgerEntry] = []


def append(receipt: Receipt, state: SystemState, **kwargs) -> LedgerEntry:
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
        # Enhanced fields from receipt for richer hash chain
        request_id=receipt.request_id,
        intent_id=receipt.intent_id,
        authorization_id=receipt.authorization_id,
        decision=receipt.decision.value,
        action=receipt.action_type,
        result_hash=receipt.result_hash,
        receipt_signature=receipt.signature,
        # IAM enrichment fields (passed via kwargs or defaults)
        requested_by=kwargs.get("requested_by", ""),
        approved_by=kwargs.get("approved_by", ""),
        requester_role=kwargs.get("requester_role", ""),
        approver_role=kwargs.get("approver_role", ""),
        authority_scope=kwargs.get("authority_scope", ""),
    )

    # Compute ledger hash over all fields
    entry.ledger_hash = _compute_ledger_hash(entry)

    # Sign ledger entry with RSA private key
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
    """Return the full ledger (read-only copy)."""
    return list(_ledger)


def get_entry_by_receipt(receipt_id: str) -> LedgerEntry | None:
    """Look up a ledger entry by receipt ID."""
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


def verify_entry_signature(entry: LedgerEntry) -> bool:
    """
    Verify the RSA-PSS signature on a ledger entry using the public key.

    Args:
        entry: The ledger entry whose signature to verify.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not entry.ledger_signature:
        return False

    public_key = _load_public_key()
    try:
        signature_bytes = base64.b64decode(entry.ledger_signature)
        public_key.verify(
            signature_bytes,
            entry.ledger_hash.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


def reset() -> None:
    """Reset the in-memory ledger. For testing only."""
    _ledger.clear()


# ---------------------------------------------------------------------------
# Hash computation
# ---------------------------------------------------------------------------

def _compute_ledger_hash(entry: LedgerEntry) -> str:
    """
    Compute the ledger entry hash over all fields.

    Formula: SHA-256(
        entry_id + receipt_id + receipt_hash + request_id + intent_id +
        authorization_id + decision + action + result_hash +
        receipt_signature + previous_hash + timestamp
    )
    """
    data = (
        f"{entry.ledger_entry_id}"
        f"{entry.receipt_id}"
        f"{entry.receipt_hash}"
        f"{entry.request_id}"
        f"{entry.intent_id}"
        f"{entry.authorization_id}"
        f"{entry.decision}"
        f"{entry.action}"
        f"{entry.result_hash}"
        f"{entry.receipt_signature}"
        f"{entry.previous_ledger_hash}"
        f"{entry.timestamp}"
    )
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# RSA Signing
# ---------------------------------------------------------------------------

def _sign_ledger_entry(entry: LedgerEntry) -> str:
    """
    Sign the ledger entry hash with the RSA-2048 private key.

    Returns a base64-encoded RSA-PSS signature of the ledger_hash.
    """
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
