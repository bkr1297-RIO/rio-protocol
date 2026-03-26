# RIO Ledger Protocol

> **This directory contains the ledger protocol specification and documentation. It is NOT a code directory.**
> The reference implementation of the ledger lives in `/runtime/ledger_v2/`.

---

## Overview

The RIO Ledger is a tamper-evident, hash-chained audit trail that records every governed execution receipt. It provides cryptographic proof of the complete history of actions processed through the RIO pipeline.

## Ledger Format (v2)

Each ledger entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `ledger_id` | string | Unique identifier for this ledger entry |
| `receipt_id` | string | Reference to the associated v2 receipt |
| `ledger_hash` | string | SHA-256 hash of the entry contents |
| `previous_ledger_hash` | string | Hash of the preceding entry (chain link) |
| `timestamp` | string | ISO 8601 UTC timestamp of ledger recording |
| `entry_data` | object | The full v2 receipt embedded in the entry |

## Hash-Chain Integrity

The ledger uses a hash chain where each entry's `previous_ledger_hash` references the `ledger_hash` of the preceding entry. The genesis entry (first in chain) uses a well-known sentinel value. This creates a tamper-evident structure: modifying any entry breaks the chain from that point forward.

## Verification

Independent verification of ledger integrity involves:

1. Recomputing the `ledger_hash` of each entry from its contents.
2. Verifying that each entry's `previous_ledger_hash` matches the `ledger_hash` of the preceding entry.
3. Verifying the embedded receipt signatures within each entry.

## Related Files

- **Canonical Specification:** `/spec/audit_ledger_protocol.md`
- **JSON Schema:** `/spec/ledger_entry_schema.json`
- **Reference Implementation:** `/runtime/ledger_v2/`
- **Immutability Model:** `/spec/ledger_immutability_model.md`
- **Interoperability:** `/spec/ledger_interoperability.md`
