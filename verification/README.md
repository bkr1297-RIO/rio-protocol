# RIO Independent Verifier

> **This directory will contain the standalone verification tool for RIO receipts and ledger entries.**
> This is a Workstream 4 deliverable — an independent implementation that verifies RIO compliance
> without depending on the reference implementation in `/runtime`.

---

## Purpose

The independent verifier enables any party to:

1. Verify the cryptographic signature on a RIO v2 receipt.
2. Verify the hash-chain integrity of a RIO ledger.
3. Verify that receipt contents match their declared hashes (intent_hash, action_hash, verification_hash).
4. Validate receipt schema conformance against the canonical JSON schema.

## Status

**Not yet implemented.** This directory will be populated during Workstream 4 of the RIO standardization effort.

## Planned Components

| Component | Description |
|-----------|-------------|
| `verify_receipt.py` | Standalone receipt signature and hash verification |
| `verify_ledger.py` | Standalone ledger chain integrity verification |
| `verify_schema.py` | JSON Schema conformance validation |
| `README.md` | Usage instructions and verification procedures |
| `requirements.txt` | Minimal dependencies (cryptography library only) |

## Design Principles

- **Zero dependency on `/runtime`:** The verifier must not import from or depend on the reference implementation.
- **Minimal dependencies:** Only standard library + one cryptography library.
- **CLI-first:** Usable from the command line with file path or stdin input.
- **Exit codes:** Returns 0 for valid, non-zero for invalid, with human-readable output.

## Related Files

- **Verification Model:** `/spec/verification_model.md`
- **Receipt Schema:** `/spec/receipt_schema.json`
- **Ledger Schema:** `/spec/ledger_entry_schema.json`
- **Reference Implementation Verifier:** `/runtime/receipts/verifier.py`
