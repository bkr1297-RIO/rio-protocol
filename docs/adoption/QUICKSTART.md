# RIO Protocol — Quickstart Guide

**Get a RIO-compliant governance layer running in under an hour.**

---

## What You Need

| Requirement | Details |
|-------------|---------|
| Language runtime | Any language with SHA-256, RSA-PSS or Ed25519, and JSON serialization |
| Key pair | RSA-2048 (PSS) or Ed25519 — generate before you start |
| Storage | Any persistent store for the ledger (database, file, or key-value store) |
| Test vectors | Download from `tests/vectors/` in the RIO protocol repository |

---

## Step 1: Generate Keys

Generate an RSA-2048 key pair or an Ed25519 key pair. Store the private key securely. The public key will be used for verification.

**RSA-PSS parameters:** SHA-256 hash, MGF1 with SHA-256, max salt length (32 bytes), public exponent 65537.

**Ed25519:** Standard key generation — no additional parameters.

---

## Step 2: Implement Three Hash Functions

All three use the same pattern: build a JSON object, serialize with sorted keys (no whitespace, UTF-8), compute SHA-256, output lowercase hex (64 characters).

| Hash | Input Fields | Special Rule |
|------|-------------|--------------|
| **Intent Hash** | `intent_id`, `action_type`, `requested_by`, `target_resource`, `parameters` | Sort keys at every nesting level |
| **Action Hash** | The execution result payload (any JSON object) | Same serialization rules |
| **Receipt Hash** | 13 receipt fields (see behavior doc Section 5.3) | Concatenate serialized JSON with `previous_hash` *after* serialization, then hash the combined string |

**Verify:** Compute `SHA256(b'GENESIS')`. Expected output: `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a`. If this does not match, fix your SHA-256 or encoding before proceeding.

---

## Step 3: Implement Receipt Signing

Construct the signing payload by concatenating six fields with **no separator**:

```
intent_hash + action_hash + decision + timestamp_execution + receipt_hash + previous_hash
```

Sign the UTF-8 encoded payload with your private key. Base64-encode the signature. Store it in the receipt's `signature` field.

**Verify:** Sign a test payload, then verify with your public key. Corrupt one byte and confirm verification fails.

---

## Step 4: Implement the Ledger

Each ledger entry links to the previous one via `previous_ledger_hash`. The `ledger_hash` is computed by concatenating 13 fields (no separator) and hashing with SHA-256. Sign the `ledger_hash` to produce `ledger_signature`.

The first entry uses an empty string for `previous_ledger_hash`.

**Verify:** Write 3 entries. Walk the chain. Confirm each `previous_ledger_hash` matches the preceding `ledger_hash`. Tamper with one entry and confirm the chain breaks.

---

## Step 5: Run Test Vectors

Process the test vector files from `tests/vectors/` through your implementation:

| Vector File | Expected Result |
|-------------|-----------------|
| `receipt_valid_approved.json` | All checks PASS |
| `receipt_valid_denied.json` | All checks PASS |
| `receipt_invalid_signature.json` | Signature check FAIL |
| `receipt_invalid_hash.json` | Hash check FAIL |
| `receipt_invalid_intent_hash.json` | Request hash check FAIL |
| `receipt_missing_fields.json` | Required fields check FAIL |
| `ledger_chain_valid.json` | Chain integrity PASS |
| `ledger_chain_tampered.json` | Chain integrity FAIL |
| `ledger_chain_deleted_entry.json` | Chain integrity FAIL |
| `hash_computation_examples.json` | All computed hashes match expected values |
| `signing_payload_examples.json` | All 3 signatures verify with `public_key.pem` |

If all vectors pass, your implementation is **Level 1 compliant** (Receipt Format Compliance).

---

## Step 6: Add the Governance Pipeline

Build the 8-stage pipeline on top of your cryptographic layer:

| Stage | What It Does | Key Rule |
|-------|-------------|----------|
| 1. Intake | Validate request, assign UUID | Reject malformed requests |
| 2. Classification | Determine action type and risk category | Use configurable rules |
| 3. Structured Intent | Produce canonical intent, compute intent hash | Enforce parameter requirements |
| 4. Policy & Risk | Evaluate policy rules, compute risk score | LOW=auto-approve, CRITICAL=auto-deny |
| 5. Authorization | Route approvals, issue tokens | Tokens are single-use with expiry |
| 6. Execution Gate | Validate token, check kill switch, permit execution | Fail-closed on any check failure |
| 6b. Verification | Validate execution result matches intent | Set verification_status |
| 7. Receipt | Generate and sign v2 receipt | Every exit path gets a receipt |
| 8. Ledger | Append signed entry to hash chain | Every receipt gets a ledger entry |

Add a kill switch (boolean flag) that blocks all executions at Stage 6 when engaged.

Run the Level 2 conformance tests. If all pass, your implementation is **Level 2 compliant** (Pipeline Compliance).

---

## What's Next

| Goal | Document |
|------|----------|
| Full protocol compliance (Level 3) | Implementation Guide — Phase 3: Three-Loop Architecture |
| Regulatory compliance evidence | Regulatory Mapping — EU AI Act, NIST AI RMF, SOC 2 |
| Formal certification | Certification Criteria — self-assessment and formal review process |
