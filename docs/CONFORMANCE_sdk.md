# RIO Protocol — Conformance Guide

This document defines what it means to be a conforming RIO implementation and explains how to use test vectors and the independent verifier to verify compliance.

For the normative protocol requirements, see `spec/RIO_Protocol_Specification_v1.0.md`. The key words MUST, MUST NOT, REQUIRED, SHOULD, and MAY are used as defined in RFC 2119.

---

## Conformance Levels

RIO defines three conformance levels. Each level is a strict superset of the level below it.

---

### Level 1 — Cryptographic Compliance

A Level 1 implementation produces **correct cryptographic artifacts**: valid signatures, correct hash computations, and correct ledger entry sealing.

**A Level 1 implementation MUST:**

| # | Requirement |
|---|---|
| C1-01 | Use **ECDSA secp256k1 / SHA-256 / DER** encoding for all asymmetric signing and verification. |
| C1-02 | Sign intents as: `sig = ECDSA_sign(UTF-8_encode(intent), RIO_PRIVATE_KEY)`. |
| C1-03 | Sign execution tokens as: `sig = ECDSA_sign(UTF-8_encode(intent + "\|" + source + "\|" + timestamp), RIO_PRIVATE_KEY)`. |
| C1-04 | Compute `parameters_hash = SHA-256(UTF-8_encode(intent + "\|" + source + "\|" + timestamp))`. |
| C1-05 | Compute `intent_id = SHA-256(UTF-8_encode(intent))`. |
| C1-06 | Compute `signature_hash = SHA-256(Base64_decode(signature_b64))`. Input is raw bytes, not a string. |
| C1-07 | Compute `approver = SHA-256(UTF-8_encode(RIO_PUBLIC_KEY_env_raw))[:16]`. |
| C1-08 | Compute `entry_hash` for `execution_ledger` using the exact field order and pipe separator defined in Section 5.6 of the spec. |
| C1-09 | Compute `ledger_hash` and HMAC `signature` for `post_execution_ledger` exactly as defined in Section 5.7 of the spec. |
| C1-10 | Compute the in-memory `receipt_hash` exactly as defined in Section 5.8 of the spec, including the 500-character truncation of `ai_response`. |
| C1-11 | Use the literal ASCII string `"GENESIS"` as the initial `prev_hash` / `prev_ledger_hash` for the first row in any hash chain. |
| C1-12 | Produce all hash values as lowercase 64-character hexadecimal strings. |
| C1-13 | Encode all ECDSA signatures in Base64 (RFC 4648, `=` padding, standard alphabet). |

---

### Level 2 — Pipeline Compliance

A Level 2 implementation implements all eight pipeline stages in order and enforces all eight protocol invariants.

**A Level 2 implementation MUST satisfy all Level 1 requirements, plus:**

| # | Requirement |
|---|---|
| C2-01 | Implement all eight pipeline stages in the exact order defined in Section 3 of the spec. |
| C2-02 | Block execution and return the correct HTTP status at each stage's defined failure conditions. |
| C2-03 | Implement the **Signature Registry** with atomic check-and-insert semantics, persistent storage, and TTL-based eviction. |
| C2-04 | Implement the **Sovereign Gate** with all six checks in order (Section 3.2). |
| C2-05 | Implement the **Execution Gate** (`check_gate`) with all five guards in order (Section 3.3). |
| C2-06 | Write both a `gate_log` entry and an `execution_ledger` entry for **every** `check_gate` invocation — pass or block. |
| C2-07 | Compute and store `prev_hash` / `entry_hash` correctly for every `execution_ledger` entry. |
| C2-08 | Write a `post_execution_ledger` entry for every successful AI model execution. |
| C2-09 | Enforce invariants INV-01 through INV-08 (Section 7.1 of the spec). |
| C2-10 | Include `receipt_hash`, `ledger_index`, `signature_hash`, `model_used`, `signature_verified`, and `timestamp` in every HTTP 200 response. |
| C2-11 | Block execution with HTTP 403 when `execution_token` is absent or invalid. |
| C2-12 | Block execution with HTTP 409 when a signature has been used before. |
| C2-13 | Block execution with HTTP 401 when the Sovereign Gate fails. |
| C2-14 | Block execution with HTTP 503 when `RIO_PUBLIC_KEY` is unavailable. |

---

### Level 3 — Full Protocol Compliance

A Level 3 implementation additionally enforces the Three-Loop Architecture, supports asynchronous audit, enables independent verification, and implements the emergency kill switch.

**A Level 3 implementation MUST satisfy all Level 1 and Level 2 requirements, plus:**

| # | Requirement |
|---|---|
| C3-01 | **Three-Loop Architecture**: Structurally separate Intake (Stages 1-2, 4-5), Execution (Stage 3, 6-7), and Audit (Stage 8) loops. |
| C3-02 | **Asynchronous Audit**: Stage 8 MUST be initiated as a non-blocking task and MUST NOT delay the HTTP response to the caller. |
| C3-03 | **Independent Verification Support**: Expose interfaces or export capabilities allowing external verification using only `RIO_PUBLIC_KEY` and `RIO_SERVICE_TOKEN`. |
| C3-04 | **Nonce Registry**: Implement with TTL-based eviction and fail-closed semantics. |
| C3-05 | **Key Fingerprint Stability**: The `approver` field MUST be computed consistently for all entries produced from the same key pair. |
| C3-06 | **Emergency Kill Switch (EKS-0)**: Removing `RIO_PUBLIC_KEY` MUST immediately block all requests with no execution possible (Section 7.4 of the spec). |
| C3-07 | **Cross-Table Linkage**: `parameters_hash` MUST enable unambiguous cross-reference between `execution_ledger` and `post_execution_ledger`. |
| C3-08 | **Model Routing Determinism**: The same `(model_field, calibrated_intent)` pair MUST always select the same model. |

---

## Using Test Vectors

Test vectors for all hash computations are in Appendix C of `spec/RIO_Protocol_Specification_v1.0.md` and are cross-referenced in `spec/RIO_Protocol_Specification_v1.0.json` under `appendix_c_test_vectors`.

Run the conformance test runner to validate your hash implementations against all vectors:

```bash
cd tests/conformance
python run_conformance_tests.py
```

The runner checks:

| Test | Checks |
|---|---|
| `TV-C1: intent_hash` | SHA-256 of the UTF-8-encoded intent string |
| `TV-C2: parameters_hash` | SHA-256 of the pipe-delimited canonical string |
| `TV-C3: entry_hash (blocked)` | entry_hash with empty agent and empty receipt_hash; verifies `\|\|` handling |
| `TV-C4: ledger_hash (post-exec)` | SHA-256 of the pipe-delimited post-execution seal fields |
| `TV-C5: HMAC signature` | HMAC-SHA256 over the ledger_hash |
| `TV-C6: in-memory receipt_hash` | SHA-256 with GENESIS prev_hash and 500-char truncation |
| `TV-C7: gate receipt_hash` | SHA-256 of `GATE_PASSED\|intent_id\|source\|ts` |

All test vectors use publicly known input strings so that any implementation can reproduce them without access to the running gateway.

---

## Using the Independent Verifier for Compliance

The independent verifier (`demo/demo_verify.py`) demonstrates that ledger integrity can be confirmed without the gateway running.

For compliance testing, you can adapt the verification logic to:

1. **Export** `execution_ledger` and `post_execution_ledger` tables from `gateway.db`.
2. **Run** the verifier against the exported data with `RIO_SERVICE_TOKEN`.
3. **Confirm** that `chain_intact = true` and all HMAC signatures verify.

A Level 3 compliant implementation MUST produce ledger exports that pass full independent verification.

### Conformance Test Categories

| Category | What to Test |
|---|---|
| Cryptographic Correctness | All test vectors in `run_conformance_tests.py` return PASS |
| Replay Prevention | Submit same signed request twice → HTTP 409; same nonce twice → HTTP 401 |
| Fail-Closed Behavior | No `execution_token` → HTTP 403; `RIO_PUBLIC_KEY` unset → HTTP 503; expired timestamp → HTTP 401 |
| Chain Integrity | After N requests, verifier returns `chain_intact = true`. Tamper a row → verifier returns `chain_intact = false` |
| HMAC Verification | All `post_execution_ledger` HMAC signatures verify with `RIO_SERVICE_TOKEN` |
| Guard Ordering | A Guard 1 failure returns a Guard 1 error (not a Guard 3 error) |
| Audit Completeness | After a blocked request: exactly one `execution_ledger` row with `result='blocked'` and one `gate_log` row with `event='unauthorized execution attempt'` |

---

## Canonical Reference

All conformance requirements are derived from and subject to:

> **RIO Protocol Specification v1.0** — `spec/RIO_Protocol_Specification_v1.0.md`

In any conflict between this document and the protocol spec, the protocol spec is authoritative.
