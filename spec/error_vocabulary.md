# RIO Error Vocabulary Specification

**Version:** 1.0
**Status:** Locked
**Locked:** April 21, 2026, 01:00 UTC
**Authority:** This document governs the error vocabulary for all RIO verification output.

---

## 1. Purpose

The Error Vocabulary defines the canonical set of error codes that any RIO-compliant verifier must use when reporting verification failures. It is the stable external contract for the proof layer.

A developer who installs a RIO verifier package, runs verification against a receipt or ledger, and receives structured output must see error codes from this vocabulary. No implementation-specific or ad-hoc error strings are permitted in conformant output.

---

## 2. Immutability Constraint

> **Existing codes MUST NOT change. New codes may only be added in future versions.**

Once a code is published in a vocabulary version, its `code` string, `severity`, and `description` are frozen. Implementations that depend on vocabulary v1.0 can rely on these codes remaining stable indefinitely.

If a code must be deprecated, it remains in the vocabulary with an added `deprecated` flag in a future version. It is never removed.

---

## 3. Versioning Rules

The vocabulary follows a single incrementing version number: `1.0`, `1.1`, `2.0`, etc.

| Change Type | Version Increment |
|-------------|-------------------|
| New codes added (backward-compatible) | Minor (1.0 to 1.1) |
| Severity or description change on existing code | Major (1.0 to 2.0) |
| Code removal or rename | Not permitted |

Every verification output must include `vocabulary_version` to declare which version of the vocabulary it was produced against.

---

## 4. Requirement: Implementations MUST Use Exact Codes

Implementations MUST use the exact `code` string from the vocabulary JSON file (`spec/error_vocabulary.v1.json`). Implementations MUST NOT:

- Invent new codes outside the vocabulary
- Use synonyms, abbreviations, or translations of the canonical codes
- Return boolean-only verification results without structured error output

If a verification failure does not map to any existing code, the implementation MUST use the closest applicable code and include additional context in the `details` field.

---

## 5. Verification Output Contract

Every verification result — whether pass or fail — must conform to this structure:

```json
{
  "valid": false,
  "vocabulary_version": "1.0",
  "error_code": "HASH_MISMATCH",
  "message": "Receipt hash does not match recomputed value",
  "details": {
    "field": "receipt_hash",
    "stored": "abc123...",
    "computed": "def456..."
  }
}
```

For passing verification:

```json
{
  "valid": true,
  "vocabulary_version": "1.0",
  "error_code": null,
  "message": "All checks passed",
  "details": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `valid` | boolean | Yes | Whether the artifact passed all checks |
| `vocabulary_version` | string | Yes | The vocabulary version used to produce this output |
| `error_code` | string or null | Yes | The canonical error code from the vocabulary, or null if valid |
| `message` | string | Yes | Human-readable description of the result |
| `details` | object | Yes | Implementation-specific context (stored vs. computed values, field names, etc.) |

---

## 6. Relationship to Verification Output

The error vocabulary is the bridge between the verifier implementation and the conformance specification:

- The **conformance spec** (`RIO_CONFORMANCE_v2.3.0.md`) defines what must be checked.
- The **error vocabulary** (`error_vocabulary.v1.json`) defines how failures are reported.
- The **verifier** implements the checks and reports using the vocabulary.

An implementation that passes all conformance checks but reports failures using non-vocabulary codes is NOT conformant.

---

## 7. Canonical Vocabulary (v1.0)

The following codes are locked as of v1.0:

| Code | Severity | Applies To | Description |
|------|----------|------------|-------------|
| `HASH_MISMATCH` | critical | receipt, ledger | Recomputed hash does not match stored hash |
| `CHAIN_BROKEN` | critical | ledger | Hash chain link between consecutive entries is broken |
| `MISSING_FIELD` | critical | receipt, ledger | Required field is absent |
| `INVALID_SIGNATURE` | critical | receipt | Ed25519 signature does not verify |
| `INVALID_GENESIS` | critical | ledger | First entry prev_ledger_hash does not equal SHA-256(GENESIS) |
| `INVALID_DECISION` | error | receipt | Decision field contains invalid value |
| `INVALID_LEDGER_LINK` | error | receipt, ledger | prev_ledger_hash is not well-formed hex |
| `ORPHANED_RECEIPT` | error | receipt, ledger | Receipt has no corresponding ledger entry |
| `ORPHANED_LEDGER_ENTRY` | error | ledger | Ledger entry has no corresponding receipt |
| `REPLAY_DETECTED` | critical | execution | Previously consumed token/nonce resubmitted |
| `TOKEN_EXPIRED` | error | execution | Authorization token has exceeded TTL |
| `UNAUTHORIZED` | critical | execution, intent | No valid authentication provided |
| `FINGERPRINT_MISMATCH` | critical | receipt | public_key_fingerprint does not match key |
| `CHAIN_GAP` | critical | ledger | Ledger entries are missing or out of sequence |

The machine-readable source of truth is `spec/error_vocabulary.v1.json`.

---

## 8. Reference Documents

| Document | Role |
|----------|------|
| `spec/error_vocabulary.v1.json` | Machine-readable canonical vocabulary (source of truth) |
| `spec/error_vocabulary.md` | This specification document |
| `spec/RIO_CONFORMANCE_v2.3.0.md` | Conformance requirements (references this vocabulary) |
| `examples/invalid/` | Example artifacts that trigger specific error codes |
