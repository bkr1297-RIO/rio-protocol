"""
RIO Runtime — Governed Execution Protocol v2: Ledger Package

Provides v2 ledger writer and verifier with hash-chain integrity.
"""

from .ledger_writer import (
    LedgerEntryV2,
    append_v2,
    get_entry_by_receipt_v2,
    get_head_hash,
    get_ledger_v2,
    reset_v2,
)
from .ledger_verifier import (
    verify_ledger_chain,
    verify_entry_hash,
    verify_entry_signature,
    verify_chain_link,
    verify_receipt_linkage,
)

__all__ = [
    "LedgerEntryV2",
    "append_v2",
    "get_entry_by_receipt_v2",
    "get_head_hash",
    "get_ledger_v2",
    "reset_v2",
    "verify_ledger_chain",
    "verify_entry_hash",
    "verify_entry_signature",
    "verify_chain_link",
    "verify_receipt_linkage",
]
