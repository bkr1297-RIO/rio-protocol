"""
RIO SDK — Ledger Client

LedgerClient — High-level ledger operations.

    ledger = LedgerClient(client)
    latest = ledger.latest()
    result = ledger.verify_chain()
    found  = ledger.contains_receipt(receipt_hash)
    stats  = ledger.summary()
"""

from __future__ import annotations

from .gateway_client import RIOClient
from .models import LedgerEntry
from .receipt_verifier import LedgerVerifier


class LedgerClient:
    """High-level ledger operations built on top of RIOClient."""

    def __init__(self, client: RIOClient):
        self._client = client

    def latest(self) -> LedgerEntry:
        """Get the latest ledger entry from the gateway."""
        return self._client.ledger_latest()

    def full(self) -> list[LedgerEntry]:
        """Get the full in-memory session ledger."""
        return self._client.ledger_full()

    def verify_chain(self) -> dict:
        """
        Fetch the full ledger and verify chain integrity.

        Returns dict with 'intact', 'entries_checked', 'errors'.
        """
        entries = self._client.ledger_full()
        raw_entries = [e.raw for e in entries]
        return LedgerVerifier.verify_chain(raw_entries)

    def contains_receipt(self, receipt_hash: str) -> bool:
        """Check if a receipt hash exists in the ledger."""
        entries = self._client.ledger_full()
        raw_entries = [e.raw for e in entries]
        return LedgerVerifier.contains_receipt(raw_entries, receipt_hash)

    def summary(self) -> dict:
        """Get a summary of the current ledger state."""
        entries = self._client.ledger_full()
        if not entries:
            return {
                "total_entries": 0,
                "latest_entry": None,
                "chain_verified": True,
            }

        raw_entries = [e.raw for e in entries]
        chain_result = LedgerVerifier.verify_chain(raw_entries)

        return {
            "total_entries": len(entries),
            "latest_entry": {
                "id": entries[-1].id,
                "entry_hash": entries[-1].entry_hash,
                "timestamp": entries[-1].timestamp,
            },
            "chain_verified": chain_result["intact"],
            "errors": chain_result.get("errors", []),
        }
