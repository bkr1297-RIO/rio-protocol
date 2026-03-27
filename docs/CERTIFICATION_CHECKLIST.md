# RIO Protocol — Certification Checklist

Complete this checklist when submitting an implementation for RIO Certification. Every item must be checked and accompanied by evidence before a submission is considered complete.

**Implementation name:** ___________________________  
**Implementation version:** ___________________________  
**Protocol version targeted:** ___________________________  
**Certification level claimed:** ☐ Level 1   ☐ Level 2   ☐ Level 3  
**Submitter name:** ___________________________  
**Date of submission:** ___________________________  

---

## Section A — Conformance Test Vectors (Required for all levels)

Run `tests/conformance/run_conformance_tests.py` and attach the full output.

| # | Check | Pass | Evidence |
|---|---|---|---|
| A-01 | TV-C1: `intent_hash` — SHA-256(UTF-8_encode(intent)) produces the correct expected value | ☐ | |
| A-02 | TV-C2: `parameters_hash` — SHA-256 of pipe-delimited canonical string produces the correct expected value | ☐ | |
| A-03 | TV-C3: `entry_hash` (blocked entry with empty agent and empty receipt_hash) — double `\|\|` handled correctly | ☐ | |
| A-04 | TV-C4: `ledger_hash` (post-exec) — SHA-256 of pipe-delimited seal fields produces the correct expected value | ☐ | |
| A-05 | TV-C5: HMAC signature — HMAC-SHA256 over ledger_hash with service token produces the correct expected value | ☐ | |
| A-06 | TV-C6: in-memory `receipt_hash` — SHA-256 with GENESIS prev_hash and 500-char truncation | ☐ | |
| A-07 | TV-C7: gate `receipt_hash` — SHA-256 of `GATE_PASSED\|intent_id\|source\|ts` | ☐ | |
| A-08 | All 7 vectors produce `PASS`; overall result is `PASS` | ☐ | Attach full test runner output |

---

## Section B — Receipt Format Validation (Required for all levels)

| # | Check | Pass | Evidence |
|---|---|---|---|
| B-01 | HTTP 200 response includes `status: "success"` | ☐ | |
| B-02 | HTTP 200 response includes `receipt_hash` (64-char lowercase hex) | ☐ | |
| B-03 | HTTP 200 response includes `ledger_index` (positive integer, 1-based) | ☐ | |
| B-04 | HTTP 200 response includes `signature_hash` (64-char lowercase hex) | ☐ | |
| B-05 | HTTP 200 response includes `model_used` (one of: `claude`, `chatgpt`, `gemini`) | ☐ | |
| B-06 | HTTP 200 response includes `signature_verified: true` | ☐ | |
| B-07 | HTTP 200 response includes `timestamp` (ISO-8601 UTC format) | ☐ | |
| B-08 | `receipt_hash` can be independently recomputed from the formula in spec Section 5.8 | ☐ | Show computation or verifier output |

---

## Section C — Signature Verification (Required for all levels)

| # | Check | Pass | Evidence |
|---|---|---|---|
| C-01 | Intent signatures use ECDSA secp256k1 / SHA-256 / DER encoding | ☐ | |
| C-02 | Execution tokens use ECDSA secp256k1 / SHA-256 / DER encoding over canonical bytes | ☐ | |
| C-03 | Canonical bytes = UTF-8_encode(intent + `\|` + source + `\|` + timestamp) | ☐ | |
| C-04 | A request with a valid signature and correct timestamp is accepted | ☐ | Show HTTP 200 response |
| C-05 | A request with an invalid signature is rejected with HTTP 401 (`bad_signature`) | ☐ | Show HTTP 401 response |
| C-06 | A request with an expired timestamp (>300s old) is rejected with HTTP 401 (`timestamp_expired`) | ☐ | Show HTTP 401 response |
| C-07 | A request with no `execution_token` is rejected with HTTP 403 (`missing_token`) | ☐ | Show HTTP 403 response |
| C-08 | A request with an invalid `execution_token` is rejected with HTTP 403 (`invalid_signature`) | ☐ | Show HTTP 403 response |
| C-09 | `signature_hash` = SHA-256(Base64_decode(signature_b64)) — input is raw bytes, not a string | ☐ | |
| C-10 | `approver` = SHA-256(UTF-8_encode(RIO_PUBLIC_KEY_env_raw))[:16] | ☐ | |

---

## Section D — Hash Verification (Required for all levels)

| # | Check | Pass | Evidence |
|---|---|---|---|
| D-01 | All hash outputs are lowercase 64-character hexadecimal strings | ☐ | |
| D-02 | `intent_id` = SHA-256(UTF-8_encode(intent)) | ☐ | |
| D-03 | `parameters_hash` = SHA-256(UTF-8_encode(intent + `\|` + source + `\|` + timestamp)) | ☐ | |
| D-04 | `entry_hash` for `execution_ledger` uses the exact 11-field pipe-delimited order from spec Section 5.6 | ☐ | |
| D-05 | Empty fields (e.g., `agent` and `receipt_hash` on blocked entries) still appear as empty strings between separators | ☐ | |
| D-06 | `ledger_hash` for `post_execution_ledger` uses the exact 8-field pipe-delimited order from spec Section 5.7 | ☐ | |
| D-07 | `result_hash` = SHA-256(UTF-8_encode(ai_response)) | ☐ | |
| D-08 | In-memory `receipt_hash` truncates `ai_response` to 500 characters before hashing | ☐ | |
| D-09 | All chains initialize with the literal ASCII string `GENESIS` as the first `prev_hash` / `prev_ledger_hash` | ☐ | |
| D-10 | HMAC-SHA256 on `post_execution_ledger` uses UTF-8_encode(RIO_SERVICE_TOKEN) as the key and UTF-8_encode(ledger_hash) as the message | ☐ | |

---

## Section E — Ledger Chain Verification (Required for Levels 2 and 3)

Run the independent verifier against a real ledger export. Attach the full verifier output.

| # | Check | Pass | Evidence |
|---|---|---|---|
| E-01 | `execution_ledger` exists with at least one entry | ☐ | |
| E-02 | First `execution_ledger` row has `prev_hash = "GENESIS"` | ☐ | |
| E-03 | Each `execution_ledger` row's `prev_hash` equals the previous row's `entry_hash` | ☐ | Verifier output |
| E-04 | Each `execution_ledger` row's `entry_hash` can be independently recomputed from its fields | ☐ | Verifier output |
| E-05 | A blocked entry has `result = "blocked"`, `receipt_hash = ""`, and the entry_hash reflects the empty string correctly | ☐ | |
| E-06 | `gate_log` table exists and contains one entry per `execution_ledger` entry | ☐ | |
| E-07 | `post_execution_ledger` exists with at least one entry (Level 3) | ☐ | |
| E-08 | First `post_execution_ledger` row has `prev_ledger_hash = "GENESIS"` (Level 3) | ☐ | |
| E-09 | Each `post_execution_ledger` row's `ledger_hash` can be independently recomputed (Level 3) | ☐ | Verifier output |
| E-10 | `parameters_hash` in `execution_ledger` matches `parameters_hash` in the corresponding `post_execution_ledger` row | ☐ | |
| E-11 | Independent verifier reports `chain_intact = true` for `execution_ledger` | ☐ | Verifier output |
| E-12 | Independent verifier reports all HMAC signatures valid for `post_execution_ledger` (Level 3) | ☐ | Verifier output |

---

## Section F — Independent Verification PASS (Required for Levels 2 and 3)

| # | Check | Pass | Evidence |
|---|---|---|---|
| F-01 | `demo/demo_verify.py` (or SDK `verify_ledger`) runs against a real ledger export without access to the running gateway | ☐ | |
| F-02 | Check 1 — Receipt hash integrity: `PASS` | ☐ | Attach verifier output |
| F-03 | Check 2 — Execution ledger chain integrity: `PASS` | ☐ | Attach verifier output |
| F-04 | Check 3 — Post-execution ledger hash integrity: `PASS` | ☐ | Attach verifier output |
| F-05 | Check 4 — Post-execution ledger HMAC signatures: `PASS` | ☐ | Attach verifier output |
| F-06 | Overall verifier result: `PASS` | ☐ | Attach verifier output |

---

## Section G — Conformance Tests PASS (Required for all levels)

| # | Check | Pass | Evidence |
|---|---|---|---|
| G-01 | `run_conformance_tests.py` overall result: `PASS` | ☐ | Attach full output |
| G-02 | 7 of 7 vectors pass | ☐ | Attach full output |
| G-03 | SDK conformance test (`rio_sdk.run_conformance_tests()`) overall result: `PASS` (if SDK is used) | ☐ | |

---

## Section H — Fail-Closed Behavior (Required for Levels 2 and 3)

| # | Check | Pass | Evidence |
|---|---|---|---|
| H-01 | Request without `execution_token` → HTTP 403 | ☐ | |
| H-02 | Request with expired timestamp → HTTP 401 | ☐ | |
| H-03 | Replayed signature (second use) → HTTP 409 | ☐ | |
| H-04 | Replayed nonce (second use) → HTTP 401 | ☐ | |
| H-05 | `RIO_PUBLIC_KEY` not configured → HTTP 503 | ☐ | |
| H-06 | Database unavailable → HTTP 503 (not HTTP 500 or silent failure) | ☐ | |
| H-07 | No AI execution occurs when any gate check fails | ☐ | |

---

## Section I — Level 3 Specific (Required for Level 3 only)

| # | Check | Pass | Evidence |
|---|---|---|---|
| I-01 | Stage 8 (post-execution ledger write) does not delay the HTTP response | ☐ | |
| I-02 | Nonce Registry is implemented with TTL-based eviction | ☐ | |
| I-03 | Emergency Kill Switch (EKS-0): removing `RIO_PUBLIC_KEY` blocks all requests on the next incoming request, without restart | ☐ | |
| I-04 | Key fingerprint (`approver`) is computed consistently across all ledger entries for the same key | ☐ | |
| I-05 | Model routing is deterministic: same inputs always produce the same model selection | ☐ | |

---

## Submission Declaration

By submitting this checklist, the submitter declares that:

- All checked items have been verified against the named implementation version.
- The evidence provided is accurate and was produced by the named implementation.
- No test vectors or expected values have been modified from those in the canonical protocol specification.

**Submitter signature:** ___________________________  
**Date:** ___________________________  

---

*Submit this completed checklist with all attached evidence to the Protocol Steward for certification review. See `docs/CERTIFICATION.md` for the full certification process.*
