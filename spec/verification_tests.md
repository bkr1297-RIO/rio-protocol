# RIO Protocol Verification Test Suite

## 1. Overview

This document defines the formal verification tests that any RIO Protocol implementation MUST pass to demonstrate compliance with the protocol specification. These tests verify the core security properties, cryptographic integrity, and governance guarantees of the system.

**Purpose.** To provide a deterministic, repeatable set of tests that validate the correctness of a RIO implementation. Passing all tests is a necessary (though not sufficient) condition for deployment.

**Scope.** These tests cover the critical path of the decision traceability chain: request intake through ledger entry. They focus on security-critical behaviors — rejection of invalid inputs, enforcement of authorization boundaries, and integrity of the audit trail.

**Test Methodology.** Each test case specifies preconditions, exact steps, expected results, and pass/fail criteria. Tests MUST be executed against a running RIO implementation with all components operational. Tests MAY be automated using standard testing frameworks.

**Notation.** This document uses RFC 2119 keywords: MUST, MUST NOT, SHALL, SHALL NOT, SHOULD, SHOULD NOT, MAY.

---

## 2. Test Environment Requirements

A conformant test environment MUST include:

| Component | Requirement |
|-----------|-------------|
| Intake Service | Running and accepting requests |
| Origin Verification Service | Configured with at least one valid requester identity |
| Risk Evaluation Engine | Configured with default risk scoring rules |
| Policy Constraints Engine | Configured with at least one policy requiring authorization for high-risk actions |
| Authorization Service | Running with at least one registered authorizer |
| Execution Gate | Running with fail-closed default |
| Execution Service | Running (may use a mock/stub for test purposes) |
| Attestation Service | Running with a valid signing key |
| Audit Ledger | Running with an empty or known-state ledger |
| Nonce Registry | Running with an empty or known-state registry |
| Key Management | At least two key pairs: one valid, one for testing invalid signatures |
| Clock Source | Configurable for time-based tests (VT-04) |

**Test Data.** Tests use the running example: a $48,250 wire transfer from an AI finance agent (entity ID: `ai-finance-agent-001`) to Meridian Industrial Supply, authorized by CFO Sarah Mitchell (identity ID: `sarah.mitchell@acme-corp.com`).

---

## 3. Test Cases

### VT-01: Unsigned Request Blocked

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-01 |
| **Test Name** | Unsigned Request Blocked |
| **Category** | Origin Verification |
| **Priority** | Critical |

**Preconditions:**
- The intake service is running and accepting requests.
- The origin verification service is configured to require valid origin signatures.

**Test Steps:**

1. Construct a valid canonical request for a $48,250 wire transfer with all required fields populated.
2. Submit the request to the intake service WITHOUT an origin signature (omit the signature header or field entirely).
3. Observe the system response.

**Expected Result:** The intake service or origin verification service MUST reject the request with an error indicating that the origin signature is missing or invalid. The request MUST NOT proceed to risk evaluation.

**Pass Criteria:**
- HTTP response status is 401 or 403 (or equivalent rejection).
- Error message references missing or invalid origin signature.
- No risk evaluation record is created for this request.
- No entry appears in the audit ledger for this request (or an entry appears with status `rejected_at_intake`).

**Failure Behavior:** If an unsigned request proceeds past origin verification, the implementation fails this test. This indicates a critical security vulnerability — the system accepts requests from unverified sources.

**References:** Spec 01 (Intake Protocol), Spec 02 (Origin Verification)

---

### VT-02: Tampered Payload Rejected

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-02 |
| **Test Name** | Tampered Payload Rejected |
| **Category** | Integrity Verification |
| **Priority** | Critical |

**Preconditions:**
- A canonical request has been created and its SHA-256 hash computed.
- The request has passed through risk evaluation and received authorization.
- The authorization record's signature covers the original request hash.

**Test Steps:**

1. Create a valid canonical request for a $48,250 wire transfer.
2. Obtain a valid authorization for this request (complete the full pipeline through authorization).
3. Modify one field in the canonical request after authorization — change the `parameters.amount` from `48250.00` to `482500.00`.
4. Submit the modified request along with the original authorization to the execution gate.
5. Observe the system response.

**Expected Result:** The execution gate MUST detect that the request hash no longer matches the hash referenced in the authorization record. The request MUST be rejected.

**Pass Criteria:**
- The execution gate rejects the request.
- Error message references hash mismatch or payload tampering.
- No execution record is created.
- The `authorization_match` check fails if any partial processing occurs.

**Failure Behavior:** If a tampered payload is accepted for execution, the implementation fails this test. This indicates that the execution gate does not verify request integrity against the authorization, enabling payload manipulation attacks (Threat T-03).

**References:** Spec 03 (Canonical Request), Spec 07 (Execution), `canonical_request.json`, Threat Model T-03

---

### VT-03: Replay Attack Blocked

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-03 |
| **Test Name** | Replay Attack Blocked |
| **Category** | Replay Prevention |
| **Priority** | Critical |

**Preconditions:**
- A canonical request has been authorized and successfully executed.
- The nonce from the authorization has been consumed and recorded in the Nonce Registry.

**Test Steps:**

1. Create a valid canonical request for a $48,250 wire transfer.
2. Complete the full pipeline: risk evaluation, authorization, and successful execution.
3. Confirm the nonce has been recorded in the Nonce Registry with status `consumed`.
4. Resubmit the SAME authorization record (with the same `authorization_id` and `nonce`) to the execution gate.
5. Observe the system response.

**Expected Result:** The execution gate MUST reject the second submission because the nonce has already been consumed. The action MUST NOT be executed a second time.

**Pass Criteria:**
- The execution gate rejects the replayed authorization.
- Error message references nonce already consumed or replay detected.
- No second execution record is created.
- The Nonce Registry entry remains in `consumed` status.

**Failure Behavior:** If a replayed authorization is accepted and the action is executed a second time, the implementation fails this test. This indicates a critical vulnerability to replay attacks (Threat T-01), which could result in duplicate financial transactions.

**References:** Spec 07 (Execution), Spec 15 (Time-Bound Authorization), `nonce_registry.json`, Threat Model T-01

---

### VT-04: Expired Timestamp Rejected

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-04 |
| **Test Name** | Expired Timestamp Rejected |
| **Category** | Time-Bound Authorization |
| **Priority** | Critical |

**Preconditions:**
- A canonical request has been authorized with a 5-minute (300-second) expiration window.
- The `expires_at` timestamp is in the past relative to the current system time.

**Test Steps:**

1. Create a valid canonical request for a $48,250 wire transfer.
2. Complete risk evaluation and obtain authorization with `expires_at` set to 5 minutes from `authorized_at`.
3. Wait until the current time exceeds `expires_at` (or advance the test clock past the expiration).
4. Submit the expired authorization to the execution gate.
5. Observe the system response.

**Expected Result:** The execution gate MUST reject the authorization because it has expired. The action MUST NOT be executed.

**Pass Criteria:**
- The execution gate rejects the expired authorization.
- Error message references authorization expired or time window exceeded.
- No execution record is created.
- The authorization record's effective status is `expired`.

**Failure Behavior:** If an expired authorization is accepted and the action is executed, the implementation fails this test. This indicates that the execution gate does not enforce time-bound authorization (Threat T-04), allowing stale approvals to be used indefinitely.

**References:** Spec 06 (Authorization), Spec 07 (Execution), Spec 15 (Time-Bound Authorization), `authorization_record.json` (expires_at), Threat Model T-04

---

### VT-05: Approved Request Executes

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-05 |
| **Test Name** | Approved Request Executes |
| **Category** | Positive Path |
| **Priority** | Critical |

**Preconditions:**
- All RIO components are running and healthy.
- A valid requester identity is registered.
- A valid authorizer identity is registered.
- Policies are configured such that a $48,250 wire transfer requires authorization.

**Test Steps:**

1. Submit a canonical request for a $48,250 wire transfer from AI finance agent to Meridian Industrial Supply.
2. Verify the request passes origin verification.
3. Verify a risk evaluation record is created with `recommendation: require_authorization`.
4. Submit an authorization with `decision: approve`, valid signature, valid nonce, and `expires_at` set to 5 minutes in the future.
5. Verify the execution gate accepts the authorization.
6. Verify the execution service performs the action.
7. Verify an execution record is created with `execution_status: success` and `authorization_match: true`.
8. Verify an attestation record is created with all verification checks passing.
9. Verify a receipt is created summarizing the full chain.
10. Verify a ledger entry is created with the correct hash chain linking.

**Expected Result:** The full decision traceability chain is completed successfully. All seven records are created and linked.

**Pass Criteria:**
- All seven records exist: canonical request, risk evaluation, authorization, execution, attestation, receipt, ledger entry.
- All `request_id` references match across records.
- `authorization_match` is `true` in the execution record.
- All attestation verification checks pass.
- The receipt `final_status` is `executed`.
- The ledger entry `previous_entry_hash` correctly references the prior entry (or is the genesis hash).

**Failure Behavior:** If any record is missing, any cross-reference is broken, or any verification check fails, the implementation fails this test. This indicates that the positive path — the core protocol flow — is not functioning correctly.

**References:** All 15 specs, all schemas, all example flows

---

### VT-06: Denied Request Blocked

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-06 |
| **Test Name** | Denied Request Blocked |
| **Category** | Authorization Enforcement |
| **Priority** | Critical |

**Preconditions:**
- A canonical request has been created and risk-evaluated.
- An authorization record exists with `decision: deny`.

**Test Steps:**

1. Create a valid canonical request for a $48,250 wire transfer.
2. Complete risk evaluation.
3. Submit an authorization with `decision: deny`, valid signature, and a reason in the `notes` field.
4. Attempt to submit the denied authorization to the execution gate for execution.
5. Observe the system response.

**Expected Result:** The execution gate MUST reject the request because the authorization decision is `deny`. The action MUST NOT be executed.

**Pass Criteria:**
- The execution gate rejects the request.
- Error message references authorization denied.
- No execution record is created (or an execution record is created with `execution_status: cancelled`).
- A receipt is created with `final_decision: denied` and `final_status: denied`.
- A ledger entry is created recording the denial.

**Failure Behavior:** If a denied request is executed, the implementation fails this test. This indicates a critical failure in authorization enforcement — the execution gate does not respect denial decisions.

**References:** Spec 06 (Authorization), Spec 07 (Execution), `authorization_record.json` (decision field)

---

### VT-07: Ledger Hash Chain Integrity Verified

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-07 |
| **Test Name** | Ledger Hash Chain Integrity Verified |
| **Category** | Audit Integrity |
| **Priority** | High |

**Preconditions:**
- The audit ledger contains at least 5 consecutive entries from completed decision chains.

**Test Steps:**

1. Retrieve all entries from the audit ledger in chronological order.
2. For each entry starting from the second entry:
   a. Compute the SHA-256 hash of the preceding entry (using minified, sorted JSON canonicalization).
   b. Compare the computed hash against the current entry's `previous_entry_hash` field.
3. For the first entry, verify that `previous_entry_hash` is the defined genesis hash (e.g., `"0000000000000000000000000000000000000000000000000000000000000000"`).
4. Record any mismatches.

**Expected Result:** Every entry's `previous_entry_hash` MUST match the computed hash of the preceding entry. The chain MUST be unbroken from genesis to the latest entry.

**Pass Criteria:**
- Zero hash mismatches across all entries.
- The first entry references the genesis hash.
- The chain is continuous with no gaps in sequence numbers.

**Failure Behavior:** If any `previous_entry_hash` does not match the computed hash of the preceding entry, the chain has been tampered with. This indicates a critical integrity failure (Threat T-06). The specific entry where the break occurs identifies the point of tampering.

**References:** Spec 09 (Audit Ledger), System Manifest (ledger section), Threat Model T-06

---

### VT-08: Receipt Signature Valid

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-08 |
| **Test Name** | Receipt Signature Valid |
| **Category** | Cryptographic Integrity |
| **Priority** | High |

**Preconditions:**
- A completed decision chain exists with a signed receipt.
- The receipt service's public key is available from the key registry.

**Test Steps:**

1. Retrieve a receipt from a completed decision chain.
2. Extract the `signature` object from the receipt.
3. Obtain the public key corresponding to `signature.public_key_id` from the key registry.
4. Reconstruct the signed content by canonicalizing the receipt fields covered by the signature (minified, sorted JSON).
5. Compute the SHA-256 hash of the canonicalized content.
6. Verify the ECDSA-secp256k1 signature using the public key and the computed hash.

**Expected Result:** The signature verification MUST succeed, confirming that the receipt was signed by the receipt service and has not been modified since signing.

**Pass Criteria:**
- ECDSA signature verification returns `true`.
- The computed hash matches the `signed_fields_hash` in the signature object.
- The `public_key_id` resolves to a valid, non-revoked key in the registry.

**Failure Behavior:** If the signature does not verify, either the receipt has been tampered with, the wrong key was used, or the signing implementation is incorrect. This indicates a cryptographic integrity failure that undermines the non-repudiation guarantee.

**References:** Spec 08 (Attestation), `receipt.json` (signature field), System Manifest (cryptography section)

---

### VT-09: Forged Signature Rejected

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-09 |
| **Test Name** | Forged Signature Rejected |
| **Category** | Cryptographic Verification |
| **Priority** | Critical |

**Preconditions:**
- A second key pair exists that is NOT registered as a valid authorizer key.
- A valid canonical request has been created and risk-evaluated.

**Test Steps:**

1. Create a valid canonical request for a $48,250 wire transfer.
2. Complete risk evaluation.
3. Construct an authorization record with `decision: approve` and all required fields.
4. Sign the authorization using the UNREGISTERED private key (producing a syntactically valid ECDSA-secp256k1 signature, but from the wrong key).
5. Set the `public_key_id` in the signature to reference the legitimate authorizer's key ID (attempting to impersonate).
6. Submit the forged authorization to the execution gate.
7. Observe the system response.

**Expected Result:** The execution gate MUST reject the authorization because the signature does not verify against the public key associated with the claimed `public_key_id`. The action MUST NOT be executed.

**Pass Criteria:**
- The execution gate rejects the authorization.
- Error message references signature verification failure or invalid signature.
- No execution record is created.
- The system logs the failed verification attempt for security monitoring.

**Failure Behavior:** If a forged signature is accepted, the implementation fails this test. This indicates a critical vulnerability — the system does not properly verify signatures against registered keys (Threat T-02), allowing any entity with any key pair to forge authorizations.

**References:** Spec 06 (Authorization), Spec 07 (Execution), `authorization_record.json` (signature field), Threat Model T-02

---

### VT-10: Direct Execution Blocked Without Approval

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-10 |
| **Test Name** | Direct Execution Blocked Without Approval |
| **Category** | Access Control |
| **Priority** | Critical |

**Preconditions:**
- The execution service is running.
- The execution gate is running.
- No authorization has been created for the test request.

**Test Steps:**

1. Construct an execution request for a $48,250 wire transfer with all action parameters.
2. Attempt to call the execution service directly (bypassing the execution gate) with the action parameters but WITHOUT a valid `authorization_id` or execution token.
3. Observe the response from the execution service.
4. Separately, attempt to call the execution gate with the action parameters but WITHOUT a valid `authorization_id`.
5. Observe the response from the execution gate.

**Expected Result:** Both the execution service (if directly accessible) and the execution gate MUST reject the request. The action MUST NOT be executed.

**Pass Criteria:**
- Direct call to execution service: rejected with 401/403 or connection refused (if network-isolated).
- Call to execution gate without authorization: rejected with error referencing missing authorization.
- No execution record is created.
- No action is performed on the target system.

**Failure Behavior:** If the execution service accepts a direct call without going through the execution gate, or if the execution gate accepts a request without a valid authorization, the implementation fails this test. This indicates a critical bypass vulnerability (Threat T-05) — actions can be executed without any governance controls.

**References:** Spec 07 (Execution), Spec 11 (Independence), `execution_token.json`, Threat Model T-05

---

### VT-11: Execution Outside Approved Scope Blocked

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-11 |
| **Test Name** | Execution Outside Approved Scope Blocked |
| **Category** | Scope Enforcement |
| **Priority** | Critical |

**Preconditions:**
- A canonical request has been authorized for a $48,250 wire transfer to Meridian Industrial Supply (account ending 7892).
- The authorization is valid (not expired, nonce not consumed).
- The execution token has been issued with a scope binding the action to the specific `action_type`, `target_id`, and `parameter_hash`.

**Test Steps:**

1. Create a valid canonical request for a $48,250 wire transfer to Meridian Industrial Supply.
2. Complete risk evaluation and obtain a valid authorization with `decision: approve`.
3. Receive a valid execution token with scope: `action_type: finance.send_payment`, `target_id: vendor-meridian-001`, `parameter_hash: <hash of original parameters>`.
4. Attempt to execute a DIFFERENT action using the same execution token — change the target to a different vendor (e.g., `target_id: vendor-unknown-999`) while keeping the same amount.
5. Observe the system response.
6. Separately, attempt to execute the correct target but with a different amount ($148,250 instead of $48,250) using the same execution token.
7. Observe the system response.

**Expected Result:** Both attempts MUST be rejected. The execution gate or execution service MUST detect that the attempted action does not match the scope defined in the execution token. The action MUST NOT be executed.

**Pass Criteria:**
- Attempt with wrong target: rejected with error referencing scope mismatch or target mismatch.
- Attempt with wrong amount: rejected with error referencing parameter hash mismatch.
- No execution record is created for either attempt.
- The execution token remains in `active` status (not consumed by a failed scope check).
- The system logs the scope violation for security monitoring.

**Failure Behavior:** If an action outside the approved scope is executed, the implementation fails this test. This indicates that the execution gate does not enforce scope binding (Threat T-09), allowing an authorized entity to perform actions beyond what was specifically approved — a critical privilege escalation vulnerability.

**References:** Spec 07 (Execution), Spec 09 (Audit Ledger), `execution_token.json` (scope field), `execution_record.json` (authorization_match, deviation_details), Threat Model T-09

---

### VT-12: Expired Authorization Cannot Execute

| Attribute | Detail |
|-----------|--------|
| **Test ID** | VT-12 |
| **Test Name** | Expired Authorization Cannot Execute |
| **Category** | Time-Bound Authorization |
| **Priority** | Critical |

**Preconditions:**
- A canonical request has been authorized with a 5-minute (300-second) expiration window.
- The authorization was valid at the time of issuance.
- The nonce has NOT been consumed (the authorization was never used).

**Test Steps:**

1. Create a valid canonical request for a $48,250 wire transfer.
2. Complete risk evaluation and obtain authorization with `decision: approve`, `authorized_at: T`, and `expires_at: T + 300 seconds`.
3. Wait until the current time exceeds `expires_at` (or advance the test clock past `T + 300 seconds + time_skew_allowance`).
4. Submit the expired but otherwise valid authorization (correct signature, unused nonce, matching request hash) to the execution gate.
5. Observe the system response.

**Expected Result:** The execution gate MUST reject the authorization because it has expired. The action MUST NOT be executed, even though the authorization is otherwise valid (correct signature, unused nonce, matching hash).

**Pass Criteria:**
- The execution gate rejects the request.
- Error message explicitly references authorization expired or time window exceeded.
- No execution record is created.
- No execution token is issued.
- A receipt is created with `final_decision: expired` and `final_status: expired`.
- A ledger entry records the expiration event.

**Failure Behavior:** If an expired authorization is accepted for execution, the implementation fails this test. This is distinct from VT-04 (which tests expired timestamps on the request itself). This test specifically validates that the execution gate enforces the `expires_at` field on authorization records, preventing stale approvals from being used after conditions may have changed (Threat T-04).

**References:** Spec 06 (Authorization), Spec 07 (Execution), Spec 15 (Time-Bound Authorization), `authorization_record.json` (expires_at field), Threat Model T-04

---

## 4. Test Summary Matrix

| Test ID | Test Name | Category | Priority | Status |
|---------|-----------|----------|----------|--------|
| VT-01 | Unsigned Request Blocked | Origin Verification | Critical | Pending |
| VT-02 | Tampered Payload Rejected | Integrity Verification | Critical | Pending |
| VT-03 | Replay Attack Blocked | Replay Prevention | Critical | Pending |
| VT-04 | Expired Timestamp Rejected | Time-Bound Authorization | Critical | Pending |
| VT-05 | Approved Request Executes | Positive Path | Critical | Pending |
| VT-06 | Denied Request Blocked | Authorization Enforcement | Critical | Pending |
| VT-07 | Ledger Hash Chain Integrity Verified | Audit Integrity | High | Pending |
| VT-08 | Receipt Signature Valid | Cryptographic Integrity | High | Pending |
| VT-09 | Forged Signature Rejected | Cryptographic Verification | Critical | Pending |
| VT-10 | Direct Execution Blocked Without Approval | Access Control | Critical | Pending |
| VT-11 | Execution Outside Approved Scope Blocked | Scope Enforcement | Critical | Pending |
| VT-12 | Expired Authorization Cannot Execute | Time-Bound Authorization | Critical | Pending |

---

## 5. Compliance Mapping

The following table maps each verification test to the protocol specifications and schemas it validates:

| Test ID | Primary Spec | Secondary Specs | Schemas Validated | Threat Mitigated |
|---------|-------------|-----------------|-------------------|-----------------|
| VT-01 | Spec 01 (Intake) | Spec 02 (Origin Verification) | `canonical_request.json` | — |
| VT-02 | Spec 03 (Canonical Request) | Spec 07 (Execution) | `canonical_request.json`, `execution_record.json` | T-03 |
| VT-03 | Spec 07 (Execution) | Spec 15 (Time-Bound Authorization) | `nonce_registry.json`, `authorization_record.json` | T-01 |
| VT-04 | Spec 15 (Time-Bound Authorization) | Spec 06 (Authorization), Spec 07 (Execution) | `authorization_record.json` | T-04 |
| VT-05 | All specs | — | All schemas | — |
| VT-06 | Spec 06 (Authorization) | Spec 07 (Execution) | `authorization_record.json`, `receipt.json` | — |
| VT-07 | Spec 09 (Audit Ledger) | Spec 08 (Attestation) | `attestation_record.json` | T-06 |
| VT-08 | Spec 08 (Attestation) | — | `receipt.json` | T-02 |
| VT-09 | Spec 06 (Authorization) | Spec 07 (Execution) | `authorization_record.json` | T-02 |
| VT-10 | Spec 07 (Execution) | Spec 11 (Independence) | `execution_token.json` | T-05 |
| VT-11 | Spec 07 (Execution) | Spec 09 (Audit Ledger) | `execution_token.json`, `execution_record.json` | T-09 |
| VT-12 | Spec 06 (Authorization) | Spec 07 (Execution), Spec 15 (Time-Bound Authorization) | `authorization_record.json` | T-04 |

### Minimum Compliance Threshold

An implementation MUST pass ALL Critical-priority tests (VT-01 through VT-06, VT-09 through VT-12) to be considered minimally compliant. An implementation SHOULD pass all tests (including High-priority VT-07 and VT-08) for full compliance.

Failure of any Critical-priority test indicates a fundamental security vulnerability that MUST be resolved before deployment.
