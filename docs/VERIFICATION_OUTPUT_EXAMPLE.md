# RIO Protocol -- Verification Output Examples

**Version:** 1.0  
**Status:** Active

This document explains what the verification output looks like, what each check means, and how to interpret PASS and FAIL results across both the reference implementation verifier and the gateway verifier.

---

## Reference Implementation Verifier (Ed25519)

The independent verifier in `verification/` performs 7 receipt checks and 4 ledger checks. Here is what a successful verification looks like and what each check means.

### Receipt Verification -- All PASS

```
$ python -m verification.cli verify-receipt \
    tests/vectors/receipt_valid_approved.json \
    tests/vectors/public_key.pem

RIO Independent Verifier v1.0
========================================
Receipt ID: turn_abc123_1700000000
Verdict:    PASS (7/7 checks passed)
----------------------------------------
  [PASS] required_fields     All 22 required fields present
  [PASS] request_hash        Recomputed hash matches request_hash field
  [PASS] receipt_hash        Recomputed hash of 19 signed fields matches receipt_hash
  [PASS] signature           Ed25519 signature valid against public key
  [PASS] public_key_fp       SHA-256 fingerprint matches public_key_fingerprint field
  [PASS] decision_valid      governance_decision is 'allow' (valid enum value)
  [PASS] ledger_link         prev_ledger_hash is present and non-empty
========================================
```

### What Each Receipt Check Verifies

| # | Check Name | What It Does | How It Computes |
|---|------------|-------------|-----------------|
| 1 | **required_fields** | Confirms all 22 required fields exist in the receipt JSON | Checks for presence of: `receipt_id`, `turn_id`, `request_hash`, `receipt_hash`, `receipt_signature`, `public_key_fingerprint`, `governance_decision`, `timestamp`, `prev_ledger_hash`, `current_ledger_hash`, `request_canonical_payload`, `intent_type`, `risk_level`, `threshold_results`, `policy_version`, `governor_version`, `pipeline_version`, `pipeline_hash`, `invariant_results`, `execution_result`, `verification_status`, `receipt_version` |
| 2 | **request_hash** | Verifies the hash of the original request payload | `SHA256(canonical_json(request_canonical_payload))` must equal `request_hash` |
| 3 | **receipt_hash** | Verifies the hash of the 19 signed receipt fields | `SHA256(canonical_json({19 signed fields}))` must equal `receipt_hash` |
| 4 | **signature** | Verifies the Ed25519 digital signature | `Ed25519_Verify(public_key, bytes.fromhex(receipt_hash), bytes.fromhex(receipt_signature))` must succeed |
| 5 | **public_key_fp** | Verifies the public key fingerprint | `SHA256(public_key_pem_bytes).hex()` must equal `public_key_fingerprint` |
| 6 | **decision_valid** | Verifies the governance decision is a valid enum value | `governance_decision` must be one of: `allow`, `modify`, `block`, `escalate` |
| 7 | **ledger_link** | Verifies the receipt is linked to the ledger chain | `prev_ledger_hash` must be present and non-empty |

### Receipt Verification -- FAIL Example

When a receipt has been tampered with, the verifier detects the specific failure:

```
$ python -m verification.cli verify-receipt \
    tests/vectors/receipt_invalid_signature.json \
    tests/vectors/public_key.pem

RIO Independent Verifier v1.0
========================================
Receipt ID: turn_abc123_1700000000
Verdict:    FAIL (6/7 checks passed)
----------------------------------------
  [PASS] required_fields     All 22 required fields present
  [PASS] request_hash        Recomputed hash matches request_hash field
  [PASS] receipt_hash        Recomputed hash of 19 signed fields matches receipt_hash
  [FAIL] signature           Ed25519 signature verification failed
  [PASS] public_key_fp       SHA-256 fingerprint matches public_key_fingerprint field
  [PASS] decision_valid      governance_decision is 'allow' (valid enum value)
  [PASS] ledger_link         prev_ledger_hash is present and non-empty
========================================
```

The `[FAIL] signature` line tells you that the receipt's digital signature does not match the public key. This means either the receipt was modified after signing, or the wrong public key was used for verification.

### Ledger Verification -- All PASS

```
$ python -m verification.cli verify-ledger \
    tests/vectors/ledger_chain_valid.json

RIO Independent Verifier v1.0
========================================
Ledger Chain Verification
Entries:  1
Verified: 1/1
Verdict:  PASS — chain intact
========================================
```

### What Each Ledger Check Verifies

| # | Check Name | What It Does | How It Computes |
|---|------------|-------------|-----------------|
| 1 | **chain_hash** | Verifies each entry's hash links correctly | `SHA256(prev_ledger_hash + receipt_hash)` must equal `current_ledger_hash` |
| 2 | **genesis_link** | Verifies the first entry links to genesis | First entry's `prev_ledger_hash` must equal `SHA256(b'GENESIS')` |
| 3 | **continuity** | Verifies entries are linked sequentially | Each entry's `prev_ledger_hash` must equal the previous entry's `current_ledger_hash` |
| 4 | **completeness** | Verifies no entries are missing from the chain | Entry sequence numbers must be contiguous with no gaps |

### Ledger Verification -- FAIL Example (Tampered)

```
$ python -m verification.cli verify-ledger \
    tests/vectors/ledger_chain_tampered.json

RIO Independent Verifier v1.0
========================================
Ledger Chain Verification
Entries:  1
Verified: 0/1
Verdict:  FAIL — chain broken
  Entry 0: chain_hash mismatch (expected abc123..., got def456...)
========================================
```

---

## Gateway Verifier (ECDSA secp256k1)

The gateway verifier in `demo/demo_verify.py` performs 4 checks against the production gateway's receipt and ledger format. Here is what successful output looks like.

### Gateway Verification -- All PASS

```
$ python demo/demo_verify.py

[PASS] Required Fields
[PASS] Receipt Hash
[PASS] Ledger Presence
[PASS] Chain Link
[PASS] ECDSA Signature
[PASS] Nonce Protection
[PASS] Timestamp Skew
[PASS] Governance Decision
[PASS] Alignment Hash

Compliance: Level 2 — Governance Attested
```

### What Each Gateway Check Verifies

| # | Check Name | What It Does |
|---|------------|-------------|
| 1 | **Required Fields** | All required fields present in the gateway receipt |
| 2 | **Receipt Hash** | SHA-256 hash of pipe-delimited signed fields matches stored hash |
| 3 | **Ledger Presence** | Receipt is linked to a ledger entry |
| 4 | **Chain Link** | Ledger entry hash chain is valid (HMAC-SHA256) |
| 5 | **ECDSA Signature** | ECDSA secp256k1 signature verifies against the gateway public key |
| 6 | **Nonce Protection** | Nonce is present and unique (replay protection) |
| 7 | **Timestamp Skew** | Timestamp is within acceptable skew window |
| 8 | **Governance Decision** | Decision field contains a valid governance outcome |
| 9 | **Alignment Hash** | Alignment/intent hash matches the canonical payload |

---

## Compliance Level Determination

The `check_compliance.py` tool combines receipt and ledger verification to determine the compliance level:

### Level 2 Output (Typical)

```
$ python tools/check_compliance.py --auto

============================================================
 RIO Protocol -- Compliance Assessment
 Timestamp: 2026-03-26T23:32:08.328873+00:00
============================================================

Receipt Verification Checks:
  [PASS] Required Fields
  [PASS] Request Hash
  [PASS] Receipt Hash
  [PASS] Signature
  [PASS] Public Key Fingerprint
  [PASS] Decision Valid
  [PASS] Ledger Link

Ledger Verification:
  [PASS] Chain Integrity (1/1 entries)

Compliance: Level 2 -- Governance Attested
Summary:    Level 2 achieved -- receipt and ledger verified independently
```

### Non-Compliant Output

```
$ python tools/check_compliance.py \
    --receipt tests/vectors/receipt_invalid_signature.json \
    --key tests/vectors/public_key.pem

============================================================
 RIO Protocol -- Compliance Assessment
 Timestamp: 2026-03-26T23:32:08.551626+00:00
============================================================

Receipt Verification Checks:
  [PASS] Required Fields
  [PASS] Request Hash
  [PASS] Receipt Hash
  [FAIL] Signature
  [PASS] Public Key Fingerprint
  [PASS] Decision Valid
  [PASS] Ledger Link

Compliance: Non-Compliant
Summary:    Receipt does not meet Level 1 requirements
```

---

## Exit Codes

All verification tools use consistent exit codes:

| Exit Code | Meaning |
|-----------|---------|
| **0** | Verification completed (check output for PASS/FAIL) |
| **1** | Verification detected failures |
| **2** | Setup error (missing files, import errors, invalid arguments) |

For CI/CD integration, check both the exit code and the JSON output:

```bash
python -m verification.cli verify-receipt receipt.json key.pem --json | jq '.verdict'
```

---

## Interpreting Failures

When a check fails, the output tells you exactly what went wrong. Here is how to diagnose common failures:

| Failed Check | Likely Cause | What to Investigate |
|-------------|-------------|---------------------|
| required_fields | Receipt is missing fields | Compare your receipt against the 22-field schema |
| request_hash | Request payload was modified after hashing | Verify canonical JSON serialization (sorted keys, no whitespace) |
| receipt_hash | Receipt fields were modified after hashing | Verify the 19 signed fields match the hash computation |
| signature | Receipt was modified after signing, or wrong key | Verify the signing key matches the verification key |
| public_key_fp | Different key was used for signing | Check that the public key PEM matches the fingerprint |
| decision_valid | Invalid governance decision value | Ensure decision is one of: allow, modify, block, escalate |
| ledger_link | Receipt not linked to ledger | Ensure prev_ledger_hash is populated |
| chain_hash | Ledger entry was tampered with | Recompute SHA256(prev_hash + receipt_hash) |
| genesis_link | First entry does not link to genesis | First entry's prev_ledger_hash must be SHA256(b'GENESIS') |

---

## Related Documents

- [COMPLIANCE_BADGES.md](COMPLIANCE_BADGES.md) -- Compliance level definitions and badge usage
- [CONFORMANCE.md](CONFORMANCE.md) -- Detailed conformance check tables
- [QUICKSTART.md](QUICKSTART.md) -- Getting started with verification
- [verification/README.md](../verification/README.md) -- Verifier package documentation
