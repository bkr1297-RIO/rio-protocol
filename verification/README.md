# RIO Independent Verifier v1.0

A standalone verification package for RIO Protocol v1.0 receipts and ledger chains. This verifier operates **independently** of the reference implementation — it uses only a public key, receipt JSON, and ledger entries.

---

## Design Principles

The verifier is built on four non-negotiable principles:

**Zero runtime imports.** No code from `/runtime` is used. All hash formulas, signing contracts, and schema definitions are reimplemented from the protocol specification. This ensures that verification is independent of the system that produced the receipts.

**Single dependency.** Only `cryptography>=41.0.0` (for Ed25519 operations). All other logic uses the Python standard library. No frameworks, no network calls, no external services.

**Deterministic.** Given the same inputs, the verifier produces the same results on any platform, any Python version (3.9+), any operating system.

**Fail-closed.** Any verification failure results in a FAIL verdict. There is no "warn" or "skip" mode. All checks always run, even if earlier checks fail, so you see the complete picture.

---

## Installation

```bash
pip install cryptography>=41.0.0
```

No other setup is required. The verifier runs from the repository root.

---

## CLI Commands

The verifier provides three commands. Each command reads input files, runs all applicable checks, and reports results.

### Verify a Single Receipt

```bash
python -m verification.cli verify-receipt <receipt.json> --public-key <key.pem>
```

This runs all 7 receipt checks against the provided receipt file using the specified public key.

**Example with the included test data:**

```bash
python -m verification.cli verify-receipt \
  examples/quickstart/example_receipt_v2.json \
  --public-key tests/vectors/public_key.pem
```

**Expected PASS output:**

```
RIO Receipt Verification
========================
Receipt: a1b2c3d4-0001-0001-0001-aabbccddeeff

Check 1 [required_fields]       PASS
Check 2 [request_hash]          PASS
Check 3 [receipt_hash]          PASS
Check 4 [signature]             PASS
Check 5 [public_key_fingerprint] PASS
Check 6 [decision_valid]        PASS
Check 7 [ledger_link]           PASS

Result: ALL CHECKS PASSED
```

### Verify a Ledger Chain

```bash
python -m verification.cli verify-ledger <ledger.json>
```

This runs all 4 ledger checks against the provided ledger file. No public key is needed for ledger-only verification.

**Example:**

```bash
python -m verification.cli verify-ledger \
  examples/quickstart/example_ledger.json
```

**Expected PASS output:**

```
RIO Ledger Verification
=======================
Entries: 1

Entry 0  PASS  (genesis → ...)

Chain intact: YES
Entries verified: 1/1
```

### Verify Both (Receipt + Ledger)

```bash
python -m verification.cli verify-all <receipt.json> <ledger.json> --public-key <key.pem>
```

This runs all 7 receipt checks and all 4 ledger checks in a single invocation.

**Example:**

```bash
python -m verification.cli verify-all \
  examples/quickstart/example_receipt_v2.json \
  examples/quickstart/example_ledger.json \
  --public-key tests/vectors/public_key.pem
```

---

## Output Modes

### Default (Human-Readable)

The default output shows each check with PASS or FAIL and a summary line. Failed checks include a `details` field explaining what went wrong.

### JSON Mode (`--json`)

```bash
python -m verification.cli --json verify-receipt receipt.json --public-key key.pem
```

Returns structured JSON with every check result, suitable for programmatic consumption. Compare against `examples/quickstart/example_verification_result.json` to validate your output format.

### Quiet Mode (`--quiet`)

```bash
python -m verification.cli --quiet verify-receipt receipt.json --public-key key.pem
```

Returns a single summary line: `Receipt <id>: PASS` or `Receipt <id>: FAIL`. Useful for scripting and CI pipelines.

---

## Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| `0` | All checks passed | Receipt/ledger is valid and can be trusted |
| `1` | One or more checks failed | Receipt/ledger has been tampered with or is malformed — do not trust |
| `2` | Input error | File not found, invalid JSON, missing arguments, or malformed public key |

---

## PASS/FAIL Criteria

**A receipt PASSES** when all 7 checks report PASS. This means: all required fields are present, the request hash is correct, the receipt hash is correct, the Ed25519 signature is valid, the public key fingerprint matches, the decision is a valid enum value, and the ledger link is well-formed.

**A receipt FAILS** when any single check reports FAIL. The verifier does not short-circuit — all 7 checks run regardless, so you see every failure. A FAIL on any check means the receipt cannot be trusted as authentic.

**A ledger PASSES** when all entries pass all 4 checks and the chain is intact from genesis to the latest entry.

**A ledger FAILS** when any entry has an incorrect hash, a broken chain link, a missing genesis link, or a gap in the sequence.

---

## Receipt Verification (7 Checks)

| Check | Name | What It Verifies | Failure Means |
|-------|------|------------------|---------------|
| 1 | `required_fields` | All 22 required fields present with correct types | Receipt is malformed or incomplete |
| 2 | `request_hash` | SHA256(canonical_json(request_canonical_payload)) matches stored value | The original request was modified after hashing |
| 3 | `receipt_hash` | SHA256(canonical_json({19 signed fields})) matches stored value | Receipt content was modified after signing |
| 4 | `signature` | Ed25519 signature over canonical JSON of 19 signed fields is valid | Receipt was not signed by the claimed key, or content was altered |
| 5 | `public_key_fingerprint` | SHA256(raw_32_byte_public_key) matches stored fingerprint | Public key does not match the key that signed this receipt |
| 6 | `decision_valid` | Decision is one of: allow, modify, block, escalate | Invalid governance decision — receipt is non-conformant |
| 7 | `ledger_link` | prev_ledger_hash is a well-formed 64-char hex digest | Receipt cannot be linked to the ledger chain |

All 7 checks always run, even if earlier checks fail.

---

## Ledger Verification (4 Checks)

| Check | Name | What It Verifies | Failure Means |
|-------|------|------------------|---------------|
| 1 | `entry_hash` | SHA256(prev_hash + receipt_hash) matches current_ledger_hash | Entry was modified after being written to the ledger |
| 2 | `genesis_link` | First entry's prev_ledger_hash equals SHA256(b'GENESIS') | Chain does not start from the correct genesis point |
| 3 | `chain_link` | Each entry's prev_ledger_hash matches previous entry's current_ledger_hash | An entry was inserted, deleted, or reordered |
| 4 | `full_chain` | Aggregate: chain_intact = all above checks pass for all entries | The ledger has been tampered with |

---

## What a FAIL Looks Like

When a receipt has been tampered with, the verifier reports which specific check failed:

```bash
python -m verification.cli verify-receipt \
  tests/conformance/tampered_receipt.json \
  --public-key tests/vectors/public_key.pem
```

```
Check 4 [signature]             FAIL  Ed25519 signature verification failed

Result: VERIFICATION FAILED (1 of 7 checks failed)
```

When a ledger has been tampered with:

```bash
python -m verification.cli verify-ledger \
  tests/conformance/tampered_ledger.json
```

```
Entry 0  FAIL  entry_hash mismatch

Chain intact: NO
```

---

## Programmatic API

```python
from verification import verify_receipt, verify_ledger

# Receipt verification
result = verify_receipt(receipt_dict, public_key_pem_string)
print(result.all_passed)       # True/False
for check in result.checks:
    print(f"{check.check_name}: {'PASS' if check.passed else 'FAIL'}")
print(result.to_json())        # Structured JSON output

# Ledger verification
result = verify_ledger(ledger_chain_data)
print(result.chain_intact)     # True/False
print(result.entries_verified)  # Count of verified entries
print(result.to_json())        # Structured JSON output
```

---

## Package Structure

```
verification/
  __init__.py              Public API exports (verify_receipt, verify_ledger)
  __main__.py              Entry point for python -m verification.cli
  models.py                Protocol constants, result dataclasses
  hash_utils.py            SHA-256 hash functions (canonical JSON, chain hash, genesis)
  crypto_utils.py          Ed25519 key loading and signature verification
  schema_validator.py      Receipt and ledger entry schema validation
  receipt_verifier.py      7-check receipt verification
  ledger_verifier.py       4-check ledger chain verification
  cli.py                   Command-line interface (3 commands, 3 output modes)
  requirements.txt         Single dependency: cryptography>=41.0.0
  README.md                This file
  tests/
    test_verifier.py       32 tests + 13 subtests against conformance vectors
```

---

## Running Tests

```bash
pip install pytest
python -m pytest verification/tests/ -v
```

**Latest results:** 32 passed, 13 subtests passed in 0.09s.

---

## Cryptographic Constants

| Constant | Value |
|----------|-------|
| Signature algorithm | Ed25519 |
| Hash algorithm | SHA-256 |
| Canonical JSON | Keys sorted, no whitespace, UTF-8 encoded |
| Genesis hash | `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a` |
| Signed fields | 19 (receipt_version through public_key_fingerprint) |
| Total required fields | 22 (19 signed + receipt_hash + signature_algorithm + signature) |
