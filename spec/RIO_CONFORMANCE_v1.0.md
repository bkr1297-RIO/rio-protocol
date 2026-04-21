# RIO Conformance Specification v1.0

**Status:** Normative
**Version:** 1.0
**Date:** 2026-04-21

> `RIO_CONFORMANCE_v1.0.md` defines how compliance with the RIO Standard is verified. It maps directly to verifier behavior and converts claims into testable guarantees.

---

## 1. What Conformance Means

A system is RIO-conformant when it enforces the canonical invariant:

> No digital action occurs without explicit authorization, and all actions produce verifiable cryptographic proof.

Conformance is not self-declared. It is demonstrated by passing the tests defined in this document. If the verifier reports FAIL on any required test, the system is not conformant at that level.

---

## 2. Conformance Levels

Conformance is assessed at three levels. Each level builds on the previous one.

| Level | Name | Scope |
|-------|------|-------|
| L1 | Receipt Format | Correct receipt structure, valid signatures, correct hashes |
| L2 | Ledger and Verification | L1 + tamper-evident hash-chain ledger, chain integrity |
| L3 | Full Pipeline | L2 + complete governance pipeline, gate enforcement, denial receipts |

---

## 3. Level 1 — Receipt Format Compliance

An implementation must produce receipts that pass all 7 checks:

| Check | Name | Requirement |
|-------|------|-------------|
| 1 | `required_fields` | All 22 required fields are present with correct types |
| 2 | `request_hash` | `request_hash` equals SHA-256 of the canonical JSON of `request_canonical_payload` |
| 3 | `receipt_hash` | `receipt_hash` equals SHA-256 of the canonical JSON of the 19 signed fields |
| 4 | `signature` | Ed25519 signature over the canonical JSON of the 19 signed fields is valid |
| 5 | `public_key_fingerprint` | `public_key_fingerprint` equals SHA-256 of the raw 32-byte Ed25519 public key |
| 6 | `decision_valid` | `decision` is one of: `allow`, `modify`, `block`, `escalate` |
| 7 | `ledger_link` | `prev_ledger_hash` is a well-formed 64-character hex digest |

---

## 4. Level 2 — Ledger and Verification Compliance

An implementation must maintain a ledger that passes all 4 checks:

| Check | Name | Requirement |
|-------|------|-------------|
| 1 | `entry_hash` | `current_ledger_hash` equals SHA-256 of (`prev_ledger_hash` + `receipt_hash`) concatenated as UTF-8 strings |
| 2 | `genesis_link` | First entry's `prev_ledger_hash` equals `SHA-256(b'GENESIS')` = `901131d8...1416a` |
| 3 | `chain_link` | Each entry's `prev_ledger_hash` equals the previous entry's `current_ledger_hash` |
| 4 | `full_chain` | The entire chain is intact — no gaps, no reordering, no deletions |

Every receipt must have a corresponding ledger entry. No orphaned receipts. No orphaned ledger entries.

---

## 5. Level 3 — Full Pipeline Compliance

An implementation must enforce the eight protocol invariants defined in the RIO Standard (INV-01 through INV-08).

---

## 6. Gateway Conformance Tests (T-01 through T-06)

These six tests verify that a running gateway enforces the core guarantees. They map directly to the verifier checks in `verifier/verify.py` (in `rio-system`) and to the protocol invariants.

| Test ID | Claim | Verifier Check | Invariant | How to Test |
|---------|-------|----------------|-----------|-------------|
| T-01 | Unauthorized execution is blocked | `POST /execute` without auth token returns 400/401/403 | INV-06 (Fail-closed) | Submit execution request with no authentication. Gate must reject. |
| T-02 | Parameter mutation is blocked | Execution parameters must match approved intent | INV-04 (Scope integrity) | Submit execution with altered parameters after approval. Gate must reject. |
| T-03 | Replay is blocked | Used authorization tokens cannot be reused | INV-06 (Fail-closed) | Submit a previously consumed token. Gate must reject. |
| T-04 | Gate enforcement is active | Gateway is operational and enforcing governance | INV-01, INV-06 | `GET /health` returns operational status. `GET /verify` confirms chain integrity. |
| T-05 | Receipts are generated | Every governed action produces a cryptographic receipt | INV-02 (Every action logged) | Execute a governed action. Verify receipt exists with valid hash and signature. |
| T-06 | Ledger records are created | Every receipt is written to the hash-chained ledger | INV-02, INV-08 (Immutability) | After execution, `GET /ledger` returns entries. `GET /verify` confirms chain integrity. |

---

## 7. Mapping: Verifier to Conformance Tests

The `verifier/verify.py` script in `rio-system` runs five HTTP-based checks against a live gateway. The following table maps each verifier scenario to the conformance tests above:

| Verifier Scenario | Verifier ID | Conformance Test |
|--------------------|-------------|------------------|
| Gateway is operational | C-001 | T-04 (Gate enforcement) |
| Ledger chain verification available | C-002 | T-06 (Ledger recording) |
| Ledger is accessible and contains entries | C-003 | T-06 (Ledger recording) |
| Unauthenticated execution is blocked | C-004 | T-01 (Unauthorized execution blocked) |
| Unauthenticated intent submission is blocked | C-005 | T-01 (Unauthorized execution blocked) |

Tests T-02 (parameter mutation), T-03 (replay), and T-05 (receipt generation) require authenticated pipeline execution and are verified through the demo walkthrough (`demo/DEMO_WALKTHROUGH.md` in `rio-system`) and the full conformance suite (`tests/conformance/` in `rio-protocol`).

---

## 8. Conformance Test Vectors

Test vectors are provided in `tests/conformance/` and `tests/vectors/` for external implementers:

| File | Purpose |
|------|---------|
| `rio_conformance_suite_v1.json` | Machine-readable test definitions (57 tests) |
| `tests/vectors/` | Deterministic cryptographic test data |

---

## 9. Error Vocabulary Requirement

All verification output — whether from a standalone verifier, an SDK, or a gateway endpoint — MUST conform to the Error Vocabulary defined in `spec/error_vocabulary.v1.json` (specification: `spec/error_vocabulary.md`).

Every verification result MUST include:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vocabulary_version` | string | Yes | The vocabulary version used (e.g., "1.0") |
| `error_code` | string or null | Yes | Canonical error code from the vocabulary, or null if valid |
| `message` | string | Yes | Human-readable description |

Implementations that return verification results without `vocabulary_version` are NOT conformant at any level.

Boolean-only verification responses (e.g., `{"valid": false}` with no error code) are NOT conformant.

---

## 10. Claiming Conformance

To claim RIO conformance at any level:

1. Pass all verification checks for that level
2. Pass all applicable conformance test vectors
3. Document the conformance level claimed and the test results

Compliance is binary: either the verifier reports PASS on all checks, or the implementation is not conformant at that level.

---

## 11. Reference Documents

| Document | Role |
|----------|------|
| `spec/RIO_STANDARD_v1.0.md` | Authoritative specification |
| `spec/RIO_CONFORMANCE_v1.0.md` | How compliance is verified (this document) |
| `spec/error_vocabulary.v1.json` | Canonical error vocabulary (machine-readable) |
| `spec/error_vocabulary.md` | Error vocabulary specification |
| `docs/CONFORMANCE.md` | Detailed conformance level definitions |
| `tests/conformance/` | Machine-readable test suite |
| `tests/vectors/` | Cryptographic test vectors |
| `examples/invalid/` | Example artifacts that trigger specific error codes |
