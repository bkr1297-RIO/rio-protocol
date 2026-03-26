# RIO Independent Verifier v1.0

A standalone verification package for RIO Protocol v1.0 receipts and ledger chains. This verifier operates **independently** of the reference implementation — it uses only a public key, receipt JSON, and ledger entries.

## Design Principles

- **Zero runtime imports**: No code from `/runtime` is used. All hash formulas, signing contracts, and schema definitions are reimplemented from the protocol specification.
- **Single dependency**: Only `cryptography>=41.0.0` (for Ed25519 operations). All other logic uses Python standard library.
- **Deterministic**: Given the same inputs, produces the same results on any platform.
- **Fail-closed**: Any verification failure results in a FAIL verdict. There is no "warn" or "skip" mode.

## Installation

```bash
pip install cryptography>=41.0.0
```

## CLI Usage

```bash
# Verify a single receipt
python -m verification.cli verify-receipt receipt.json --public-key key.pem

# Verify a ledger chain
python -m verification.cli verify-ledger ledger.json

# Verify both receipt and ledger
python -m verification.cli verify-all receipt.json ledger.json --public-key key.pem

# JSON output
python -m verification.cli --json verify-receipt receipt.json --public-key key.pem

# Quiet mode (single summary line)
python -m verification.cli --quiet verify-receipt receipt.json --public-key key.pem
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more checks failed |
| 2 | Input/parse/usage error |

## Receipt Verification (7 Checks)

| Check | Name | What It Verifies |
|-------|------|------------------|
| 1 | `required_fields` | All 22 required fields present with correct types |
| 2 | `request_hash` | SHA256(canonical_json(request_canonical_payload)) matches stored value |
| 3 | `receipt_hash` | SHA256(canonical_json({19 signed fields})) matches stored value |
| 4 | `signature` | Ed25519 signature over canonical JSON of 19 signed fields is valid |
| 5 | `public_key_fingerprint` | SHA256(raw_32_byte_public_key) matches stored fingerprint |
| 6 | `decision_valid` | Decision is one of: allow, modify, block, escalate |
| 7 | `ledger_link` | prev_ledger_hash is a well-formed 64-char hex digest |

All 7 checks always run, even if earlier checks fail.

## Ledger Verification (4 Checks)

| Check | Name | What It Verifies |
|-------|------|------------------|
| 1 | `entry_hash` | SHA256(prev_hash + receipt_hash) matches current_ledger_hash for every entry |
| 2 | `genesis_link` | First entry's prev_ledger_hash equals SHA256(b'GENESIS') |
| 3 | `chain_link` | Each entry's prev_ledger_hash matches previous entry's current_ledger_hash |
| 4 | `full_chain` | Aggregate: chain_intact = all above checks pass for all entries |

## Programmatic API

```python
from verification import verify_receipt, verify_ledger

# Receipt verification
result = verify_receipt(receipt_dict, public_key_pem_string)
print(result.all_passed)       # True/False
print(result.to_json())        # Structured JSON

# Ledger verification
result = verify_ledger(ledger_chain_data)
print(result.chain_intact)     # True/False
print(result.to_json())        # Structured JSON
```

## Package Structure

```
verification/
  __init__.py              Public API exports
  __main__.py              Entry point for python -m verification.cli
  models.py                Protocol constants, result dataclasses
  hash_utils.py            SHA-256 hash functions (canonical JSON, chain hash, genesis)
  crypto_utils.py          Ed25519 key loading and signature verification
  schema_validator.py      Receipt and ledger entry schema validation
  receipt_verifier.py      7-check receipt verification
  ledger_verifier.py       4-check ledger chain verification
  cli.py                   Command-line interface
  requirements.txt         Single dependency: cryptography>=41.0.0
  tests/
    test_verifier.py       32 tests + 13 subtests against WS3 conformance vectors
```

## Test Results

```
32 passed, 13 subtests passed in 0.09s
```

Run tests:

```bash
pip install pytest
python -m pytest verification/tests/ -v
```

## Cryptographic Constants

| Constant | Value |
|----------|-------|
| Signature algorithm | Ed25519 |
| Hash algorithm | SHA-256 |
| Genesis hash | `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a` |
| Signed fields | 19 (receipt_version through public_key_fingerprint) |
| Total required fields | 22 (19 signed + receipt_hash + signature_algorithm + signature) |
