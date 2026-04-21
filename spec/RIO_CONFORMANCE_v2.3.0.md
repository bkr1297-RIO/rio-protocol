# RIO Conformance Specification

**Version:** 2.3.0
**Status:** Normative
**Date:** 2026-04-21

---

## 1. Purpose

This document defines how conformance with the RIO Receipt Protocol is verified. It is the authoritative reference for determining whether an implementation is RIO-conformant.

Conformance is not self-declared. It is demonstrated by passing the tests defined in this document against the normative schemas and test vectors published in this repository.

---

## 2. Normative Ordering

When conflicts exist between documents, the following priority applies (highest first):

| Priority | Document | Role |
|----------|----------|------|
| 1 | `spec/receipt_schema.json` | Canonical receipt structure (machine-readable) |
| 2 | `spec/receipt_protocol.md` | Receipt generation and hash-chain rules |
| 3 | `spec/ledger_entry_schema.json` | Canonical ledger entry structure |
| 4 | `spec/audit_ledger_protocol.md` | Ledger append and verification rules |
| 5 | Executable test suites (`tests/`) | Behavioral expectations (test vectors) |

If any prose document contradicts the schema or test vectors, the schema and test vectors are authoritative.

This document describes conformance requirements. It does not override the schemas.

---

## 3. Required Receipt Fields

The required fields for a conformant receipt are defined exclusively by `spec/receipt_schema.json`. As of this version, the required fields are:

| Field | Type | Description |
|-------|------|-------------|
| `receipt_id` | string (UUID) | Unique receipt identifier |
| `request_id` | string (UUID) | Reference to the original request |
| `intent_id` | string (UUID) | Reference to the canonical intent |
| `authorization_id` | string (UUID) | Reference to the authorization decision |
| `decision` | string (enum) | `ALLOW` or `DENY` |
| `action_type` | string | Canonical action type from the intent |
| `execution_timestamp` | integer | UTC Unix timestamp in milliseconds |
| `result_hash` | string | SHA-256 hash of the execution result |
| `previous_receipt_hash` | string | SHA-256 hash of the preceding receipt |
| `signature` | string | Cryptographic signature of the receipt |

No additional fields are required for conformance. Implementations MAY include additional fields, but `additionalProperties` is `false` in the schema — extensions require a schema revision.

The following fields are NOT part of the current schema and MUST NOT be treated as required for conformance:

- `actor_id` (appears in broader protocol docs, not in receipt schema)
- `decision` values beyond `ALLOW` / `DENY` (the schema enum is authoritative)

---

## 4. Conformance Levels

Conformance is assessed at seven levels. Each level builds on the previous one.

| Level | Name | Scope |
|-------|------|-------|
| 1 | Receipt Generation | Produces receipts with all required fields and correct types |
| 2 | Receipt + Verification | Level 1 + receipt hashes are independently verifiable |
| 3 | Receipt + Ledger | Level 2 + receipts are written to an append-only hash-chained ledger |
| 4 | Receipt + Ledger + Verification | Level 3 + ledger chain integrity is independently verifiable |
| 5 | Full Proof Pipeline | Level 4 + complete proof-layer receipt chain (3-hash: `result_hash`, `previous_receipt_hash`, `receipt_hash`) |
| 6 | Governed Receipts | Level 5 + governed receipt chain (5-hash: adds `request_hash` and `intent_hash` binding) |
| 7 | Signed Receipts | Level 6 + Ed25519 cryptographic signatures with verifiable public key |

No additional levels exist. No renaming is permitted.

---

## 5. Level Definitions

### Level 1 — Receipt Generation

An implementation produces receipts containing all fields defined in `spec/receipt_schema.json` with correct types.

**Verification:** Schema validation against `receipt_schema.json`.

---

### Level 2 — Receipt + Verification

An implementation produces receipts where:

- `result_hash` equals SHA-256 of the canonical JSON of the execution result
- `previous_receipt_hash` correctly references the preceding receipt
- Hashes are independently recomputable from the receipt data

**Verification:** Recompute `result_hash` from the execution result payload. Confirm `previous_receipt_hash` matches the preceding receipt's computed hash.

---

### Level 3 — Receipt + Ledger

An implementation writes every receipt to an append-only ledger. The ledger:

- Contains one entry per receipt
- Links entries via hash chain (`previous_ledger_hash` → `current_ledger_hash`)
- Has no orphaned receipts (receipts without ledger entries)
- Has no orphaned ledger entries (entries without corresponding receipts)

**Verification:** Confirm every receipt has a corresponding ledger entry. Confirm `receipt_hash` in the ledger entry matches the receipt.

---

### Level 4 — Receipt + Ledger + Verification

An implementation maintains a ledger where:

- `current_ledger_hash` equals SHA-256 of (`previous_ledger_hash` + `receipt_hash`) concatenated as UTF-8 strings
- The genesis entry's `previous_ledger_hash` equals `SHA-256(b'GENESIS')`
- Each entry's `previous_ledger_hash` equals the previous entry's `current_ledger_hash`
- The full chain is intact — no gaps, no reordering, no deletions

**Verification:** Walk the chain from genesis and recompute every hash. Any mismatch is a failure.

---

### Level 5 — Full Proof Pipeline

An implementation produces receipts with a complete 3-hash proof chain:

| Hash | Computation |
|------|-------------|
| `result_hash` | SHA-256 of the canonical JSON of the execution result |
| `previous_receipt_hash` | Hash of the immediately preceding receipt |
| `receipt_hash` | SHA-256 of the canonical JSON of the receipt data (excluding `signature`) |

All three hashes are independently verifiable. The chain from `result_hash` through `receipt_hash` to `previous_receipt_hash` forms a tamper-evident proof of execution.

**Verification:** Recompute all three hashes from source data. Confirm chain linkage.

---

### Level 6 — Governed Receipts

An implementation produces governed receipts with a 5-hash chain that extends the proof pipeline:

| Hash | Computation |
|------|-------------|
| `request_hash` | SHA-256 of the canonical JSON of the original request |
| `intent_hash` | SHA-256 of the canonical JSON of the structured intent |
| `result_hash` | SHA-256 of the canonical JSON of the execution result |
| `previous_receipt_hash` | Hash of the immediately preceding receipt |
| `receipt_hash` | SHA-256 of the canonical JSON of the receipt data (excluding `signature`) |

The 5-hash chain binds the original request through intent, execution, and proof into a single verifiable record.

**Note:** `request_hash` and `intent_hash` are governed-receipt extensions. They are not present in the base `receipt_schema.json` (which defines the proof-layer minimum). Implementations claiming Level 6 conformance produce receipts that include these additional hash fields.

**Verification:** Recompute all five hashes from source data. Confirm the full chain from request through execution to proof.

---

### Level 7 — Signed Receipts

An implementation produces receipts with Ed25519 cryptographic signatures:

- The signature is computed over the canonical JSON of the receipt data (excluding the `signature` field itself)
- The signing key is an Ed25519 private key
- The corresponding public key is published and accessible for verification
- `public_key_fingerprint` (if present) equals SHA-256 of the raw 32-byte Ed25519 public key

**Verification:** Verify the Ed25519 signature using the published public key. Confirm `public_key_fingerprint` matches.

**Note:** The base `receipt_schema.json` defines `signature` as a string field without specifying the algorithm. Level 7 conformance requires Ed25519 specifically. Implementations using other signing algorithms (e.g., ECDSA-secp256k1) are conformant at Level 6 but not Level 7.

---

## 6. Test Coverage

The conformance test suite validates the following behaviors:

### Proof-Layer Receipts (3-hash chain)

- Receipt contains all required fields
- `result_hash` is correctly computed
- `previous_receipt_hash` links to the preceding receipt
- `receipt_hash` is correctly computed from receipt data

### Governed Receipts (5-hash chain)

- `request_hash` is correctly computed from the original request
- `intent_hash` is correctly computed from the structured intent
- All proof-layer checks also pass

### Ledger Verification

- Every receipt has a corresponding ledger entry
- `receipt_hash` in ledger entry matches the receipt
- Hash chain is intact from genesis
- No gaps, reordering, or deletions

### Batch Verification

- Multiple receipts can be verified in sequence
- Ledger chain validates across the full batch
- No orphaned receipts or ledger entries

### Signing Verification (Ed25519)

- Signature is valid for the receipt data
- Public key fingerprint matches (if present)
- Invalid signatures are detected and rejected

### Optional Extensions

The following are clearly marked as optional and are NOT required for any conformance level:

- Governed Corpus integration
- Kill switch event receipts
- Policy evaluation metadata
- Risk score fields

Implementations MAY include these extensions. The conformance suite does not test them.

---

## 7. Cross-Language Parity

Conformance expectations are identical across all implementation languages. The test vectors in `tests/vectors/` and `tests/conformance/` are language-agnostic.

Any Node.js implementation and any Python implementation MUST produce identical results when:

- Computing hashes from the same canonical JSON input
- Verifying signatures against the same public key
- Walking the same ledger chain

If a test vector passes in one language and fails in another, the failing implementation is non-conformant.

**Current state:** The test vectors are defined as static JSON files. No executable Node.js or Python test runners are currently included in this repository. Implementations are expected to write their own test runners that consume the published vectors and produce PASS/FAIL results per vector.

---

## 8. Error Vocabulary Requirement

All verification output MUST conform to the Error Vocabulary defined in `spec/error_vocabulary.v1.json` (specification: `spec/error_vocabulary.md`).

Every verification result MUST include:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vocabulary_version` | string | Yes | The vocabulary version used (e.g., "1.0") |
| `error_code` | string or null | Yes | Canonical error code from the vocabulary, or null if valid |
| `message` | string | Yes | Human-readable description |

Implementations that return verification results without `vocabulary_version` are NOT conformant at any level.

Boolean-only verification responses (e.g., `{"valid": false}` with no error code) are NOT conformant.

---

## 9. Claiming Conformance

To claim RIO conformance at any level:

1. Pass all verification checks for that level and all levels below it
2. Pass all applicable conformance test vectors
3. Document the conformance level claimed and the test results

Conformance is binary: either all checks pass for a given level, or the implementation is not conformant at that level.

An implementation conformant at Level N is automatically conformant at all levels below N.

---

## 10. Reference Documents

| Document | Role |
|----------|------|
| `spec/receipt_schema.json` | Canonical receipt structure (normative, highest priority) |
| `spec/receipt_protocol.md` | Receipt generation and hash-chain rules |
| `spec/ledger_entry_schema.json` | Canonical ledger entry structure |
| `spec/audit_ledger_protocol.md` | Ledger append and verification rules |
| `spec/error_vocabulary.v1.json` | Canonical error vocabulary (machine-readable) |
| `spec/error_vocabulary.md` | Error vocabulary specification |
| `tests/conformance/` | Machine-readable conformance test suite |
| `tests/vectors/` | Cryptographic test vectors |
