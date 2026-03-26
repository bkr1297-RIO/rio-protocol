"""
RIO Runtime — Governed Execution Protocol v2: Ledger Verifier

Provides independent verification of the v2 ledger:

  1. Hash chain integrity — verify each entry links to the previous
  2. Entry hash integrity — recompute and compare each entry's hash
  3. Signature verification — RSA-PSS signature on each entry
  4. Receipt linkage — verify receipt_hash in entry matches the receipt
  5. Completeness — verify no gaps in the chain

Spec reference: /spec/audit_ledger_protocol.md
"""

from __future__ import annotations

import base64
import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .ledger_writer import LedgerEntryV2, _compute_ledger_hash_v2

logger = logging.getLogger("rio.ledger_v2.verifier")

# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

_KEYS_DIR = os.path.join(os.path.dirname(__file__), "..", "keys")
_PUBLIC_KEY_PATH = os.path.join(_KEYS_DIR, "public_key.pem")

_public_key = None


def _load_public_key():
    """Load the RSA public key from disk (lazy, cached)."""
    global _public_key
    if _public_key is not None:
        return _public_key
    with open(_PUBLIC_KEY_PATH, "rb") as fh:
        _public_key = serialization.load_pem_public_key(fh.read())
    return _public_key


# ---------------------------------------------------------------------------
# Verification result
# ---------------------------------------------------------------------------

@dataclass
class LedgerVerificationResult:
    """Result of a full ledger verification."""
    chain_intact: bool
    entries_verified: int
    entries_total: int
    failures: list[str]
    details: list[str]


# ---------------------------------------------------------------------------
# Individual entry verification
# ---------------------------------------------------------------------------

def verify_entry_hash(entry: LedgerEntryV2) -> bool:
    """Verify a single entry's hash by recomputing it."""
    expected = _compute_ledger_hash_v2(entry)
    return entry.ledger_hash == expected


def verify_entry_signature(entry: LedgerEntryV2) -> bool:
    """Verify the RSA-PSS signature on a v2 ledger entry."""
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


def verify_chain_link(
    entry: LedgerEntryV2,
    previous_entry: Optional[LedgerEntryV2],
) -> bool:
    """Verify that entry.previous_ledger_hash matches the prior entry's hash."""
    if previous_entry is None:
        return entry.previous_ledger_hash == ""
    return entry.previous_ledger_hash == previous_entry.ledger_hash


# ---------------------------------------------------------------------------
# Full chain verification
# ---------------------------------------------------------------------------

def verify_ledger_chain(ledger: list[LedgerEntryV2]) -> LedgerVerificationResult:
    """
    Verify the integrity of the entire v2 ledger chain.

    Checks:
      1. Each entry's hash is correctly computed
      2. Each entry's signature is valid
      3. Each entry's previous_ledger_hash links to the prior entry
      4. The genesis entry has an empty previous_ledger_hash

    Args:
        ledger: The full list of v2 ledger entries in order.

    Returns:
        A LedgerVerificationResult with pass/fail status and details.
    """
    if not ledger:
        return LedgerVerificationResult(
            chain_intact=True,
            entries_verified=0,
            entries_total=0,
            failures=[],
            details=["Empty ledger — nothing to verify"],
        )

    failures: list[str] = []
    details: list[str] = []
    verified = 0

    for i, entry in enumerate(ledger):
        previous = ledger[i - 1] if i > 0 else None
        entry_ok = True

        # Check hash
        if not verify_entry_hash(entry):
            failures.append(f"Entry {i} ({entry.ledger_entry_id}): hash mismatch")
            entry_ok = False
        else:
            details.append(f"Entry {i}: hash verified")

        # Check signature
        if not verify_entry_signature(entry):
            failures.append(f"Entry {i} ({entry.ledger_entry_id}): signature invalid")
            entry_ok = False
        else:
            details.append(f"Entry {i}: signature verified")

        # Check chain link
        if not verify_chain_link(entry, previous):
            expected = previous.ledger_hash[:16] + "..." if previous else "(empty)"
            got = entry.previous_ledger_hash[:16] + "..." if entry.previous_ledger_hash else "(empty)"
            failures.append(
                f"Entry {i} ({entry.ledger_entry_id}): chain link broken — "
                f"expected {expected}, got {got}"
            )
            entry_ok = False
        else:
            details.append(f"Entry {i}: chain link verified")

        if entry_ok:
            verified += 1

    chain_intact = len(failures) == 0

    logger.info(
        "v2 Ledger verification: %d/%d entries verified, chain %s",
        verified,
        len(ledger),
        "INTACT" if chain_intact else "BROKEN",
    )

    return LedgerVerificationResult(
        chain_intact=chain_intact,
        entries_verified=verified,
        entries_total=len(ledger),
        failures=failures,
        details=details,
    )


def verify_receipt_linkage(
    entry: LedgerEntryV2,
    receipt_hash: str,
) -> bool:
    """
    Verify that a ledger entry's receipt_hash matches the expected receipt.

    Args:
        entry: The v2 ledger entry.
        receipt_hash: The expected receipt hash.

    Returns:
        True if the receipt_hash in the entry matches.
    """
    return entry.receipt_hash == receipt_hash
