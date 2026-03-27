# RIO Protocol — Certification

This document defines what it means for an implementation to be RIO Certified, the three certification levels, how certification is obtained and tested, and how it can be revoked.

---

## 1. What RIO Certification Means

**RIO Certified** status is a formal declaration that an implementation has been verified to correctly implement the RIO Protocol at a defined conformance level.

A certified implementation:

- Produces cryptographic artifacts (signatures, hashes, receipts, ledger entries) that are correct, consistent with the protocol specification, and independently verifiable.
- Enforces the protocol rules — including the fail-closed principle, replay prevention, and audit completeness — as specified.
- Can be verified by the standard independent verifier without access to the implementation's source code or runtime.

Certification is **version-specific**: an implementation certified for v1.0 is not automatically certified for v1.1 or v2.0. Re-certification is required when the implementation is updated to a new protocol version.

Certification is **level-specific**: an implementation certified at Level 2 has not been verified to meet Level 3 requirements.

---

## 2. Certification Levels

RIO defines three certification levels. Each level is a strict superset of the level below it. An implementation must fully satisfy all requirements of a level to claim certification at that level.

---

### Level 1 — Cryptographic Compliance

**Meaning:** The implementation produces cryptographically correct artifacts.

A Level 1 certified implementation has demonstrated that:

- All hash computations (intent_id, parameters_hash, entry_hash, ledger_hash, receipt_hash, signature_hash, approver fingerprint) are computed using the exact formulas, field orders, and encoding rules defined in the protocol specification.
- ECDSA signatures are produced and verified using secp256k1, SHA-256, and DER encoding.
- HMAC signatures on post_execution_ledger entries use HMAC-SHA256 with the correct key and message.
- All test vectors in Appendix C of the protocol specification produce the correct expected values.
- Hash outputs are lowercase 64-character hexadecimal strings.
- The GENESIS anchor string is used correctly as the chain initializer.

**Who this is for:** Developers building a new RIO-compatible implementation, verifier tool, or client library. Level 1 confirms the cryptographic foundation is correct.

---

### Level 2 — Pipeline Compliance

**Meaning:** The implementation enforces the full eight-stage governed execution pipeline.

A Level 2 certified implementation has demonstrated all Level 1 requirements, plus:

- All eight pipeline stages are implemented in the correct sequential order.
- The Sovereign Gate performs all six checks in order and is fail-closed.
- The Execution Gate (check_gate) performs all five guards in order and is fail-closed.
- The Signature Registry enforces single-use signatures with atomic check-and-insert and persistent storage.
- Every check_gate invocation — pass or block — produces exactly one `execution_ledger` entry and one `gate_log` entry.
- The `execution_ledger` hash chain is correctly maintained (prev_hash → entry_hash linkage from GENESIS).
- A `post_execution_ledger` entry is produced for every successful AI execution.
- All eight protocol invariants (INV-01 through INV-08) are enforced.
- HTTP 200 responses include: `receipt_hash`, `ledger_index`, `signature_hash`, `model_used`, `signature_verified`, `timestamp`.
- Blocked requests return the correct HTTP status codes (401, 403, 409, 503) for their specific failure condition.

**Who this is for:** Gateway implementations that enforce governance over AI model execution. Level 2 confirms the pipeline logic and audit record are correct.

---

### Level 3 — Full Protocol Compliance

**Meaning:** The implementation satisfies the complete Three-Loop Architecture and supports independent verification.

A Level 3 certified implementation has demonstrated all Level 1 and Level 2 requirements, plus:

- The Three-Loop Architecture is structurally enforced: Intake Loop, Execution Loop, and Audit Loop are separated.
- Stage 8 (post-execution audit ledger write) executes asynchronously and does not delay the HTTP response.
- The Nonce Registry is implemented with TTL-based eviction and fail-closed semantics.
- The `post_execution_ledger` chain is correctly maintained (prev_ledger_hash → ledger_hash linkage from GENESIS).
- All `post_execution_ledger` HMAC signatures are verifiable with `RIO_SERVICE_TOKEN`.
- The `parameters_hash` field provides unambiguous cross-reference between `execution_ledger` and `post_execution_ledger`.
- The Emergency Kill Switch (EKS-0) is supported: removing `RIO_PUBLIC_KEY` immediately blocks all requests.
- The independent verifier can confirm all of the above using only the ledger data and `RIO_SERVICE_TOKEN`, without access to the running gateway.
- Model routing is deterministic: the same `(model_field, calibrated_intent)` pair always selects the same model.

**Who this is for:** Production RIO gateway deployments. Level 3 confirms the full protocol is correctly implemented and independently auditable.

---

## 3. How an Implementation Is Tested

Certification testing is performed using the standard RIO verification and conformance tools. No proprietary testing infrastructure is required.

### Step 1 — Run the Conformance Test Suite

```bash
python tests/conformance/run_conformance_tests.py
```

All 7 test vectors must produce `PASS`. This is required for all three levels.

### Step 2 — Run the Independent Verifier

Export `execution_ledger` and `post_execution_ledger` data from the implementation's audit database and format it as a ledger JSON file. Then run:

```bash
python demo/demo_verify.py --ledger exported_ledger.json --token $RIO_SERVICE_TOKEN
```

Or using the SDK:

```python
from rio_sdk import verify_ledger
result = verify_ledger("exported_ledger.json", service_token=token)
assert result["overall"] == "PASS"
```

All checks must produce `PASS`.

### Step 3 — Complete the Certification Checklist

Work through every item in `docs/CERTIFICATION_CHECKLIST.md`. Each item must be checked and documented with evidence (test output, screenshots, log excerpts, or written confirmation).

### Step 4 — Submit for Certification

Submit the completed checklist with supporting evidence to the Protocol Steward. The submission must include:

- The completed `CERTIFICATION_CHECKLIST.md` with all items checked and evidenced.
- The full output of `run_conformance_tests.py` (all PASS).
- The full output of the independent verifier against a real ledger export (all PASS).
- The protocol version the implementation targets.
- The certification level being claimed.
- A description of the implementation (language, framework, deployment environment).

---

## 4. How Certification Is Granted

Upon receipt of a complete submission, the Protocol Steward or an appointed Conformance Reviewer:

1. Verifies that all checklist items are correctly evidenced.
2. Independently re-runs the conformance test suite against the stated test vector expected values.
3. Independently verifies the provided ledger export using the standard verifier.
4. Confirms the correct HTTP status codes are returned for each gate failure condition.
5. Issues a written certification decision within 30 calendar days of a complete submission.

A **Certification Record** is issued for each approved implementation containing:

- Implementation name and version
- Protocol version certified against
- Certification level granted (1, 2, or 3)
- Date of certification
- Certification record ID
- Expiry date (if applicable — see Section 5)

Certification records are maintained in the protocol's certification registry.

---

## 5. How Certification Can Be Revoked

Certification is revoked when any of the following conditions are met:

| Condition | Action |
|---|---|
| A defect is found that causes the implementation to produce incorrect cryptographic artifacts | Immediate revocation. Re-certification required after fix. |
| A security vulnerability is found that allows unauthorized execution to bypass a gate | Immediate revocation. |
| The implementation is updated in a way that changes protocol behavior without re-certification | Revocation. Re-certification required before the new version can claim certified status. |
| The implementation is found to have been tested against modified or incorrect test vectors | Immediate revocation. |
| The protocol version the implementation was certified against is deprecated | Certification marked as `Expired`. Implementation may continue to operate but may not claim active certification. |
| The implementing organization requests revocation | Revocation granted on request. |

Revocations are recorded in the certification registry with the reason and effective date. The implementing organization is notified in writing before revocation takes effect (except in cases of immediate security risk, where revocation is simultaneous with notification).

An implementation whose certification has been revoked may re-submit for certification after addressing the issue. A re-submission follows the full certification process.

---

## 6. Certification Validity and Re-Certification

- Certification has no automatic expiry for the same protocol version, as long as the implementation is not modified.
- When the implementation is updated, re-certification is required for the updated version.
- When a new protocol version is released, existing certifications at the old version remain valid but are marked against the old version. The implementation must re-certify against the new version to claim certification at the new version.
- For major protocol version increments (e.g., v1.x → v2.0), all existing certifications are automatically marked as `Legacy` after the transition period ends.
