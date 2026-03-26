# RIO Protocol — Certification Criteria

**Version:** 1.0.0
**Status:** Adoption Documentation
**Category:** Compliance & Standards

---

## Purpose

This document defines what it means for an implementation to be **RIO Compliant**. It establishes three conformance levels with specific, binary (pass/fail) criteria for each level. Every criterion references a specific conformance test, verification check, or protocol invariant so that compliance can be objectively determined without subjective judgment.

Organizations use this document to self-assess their implementation, prepare for formal certification, and understand the requirements for each conformance level.

> **Relationship to other documents:** The certification criteria reference the canonical protocol specification for formal requirements, the conformance test suite (WS3) for test vectors and test case definitions, and the regulatory mapping for framework alignment.

---

## 1. Conformance Levels

RIO defines three conformance levels. Each level includes all requirements from the previous level. An implementation claims the highest level for which it satisfies all criteria.

| Level | Name | Scope | Summary |
|-------|------|-------|---------|
| **Level 1** | Receipt Format Compliance | Static receipt and ledger checks — no pipeline required | The implementation produces valid v2 receipts with correct hashes, valid signatures, and correct field structure. It can generate and verify ledger entries with hash chain integrity. This level proves cryptographic correctness. |
| **Level 2** | Pipeline Compliance | Full governance pipeline with gate enforcement | The implementation executes all 8 pipeline stages, enforces all 8 protocol invariants, produces receipts for all decision types (approved, denied, blocked), maintains a hash-chain ledger, and supports the kill switch (EKS-0). This level proves governance correctness. |
| **Level 3** | Full Protocol Compliance | Three-Loop Architecture with cross-cutting protocols | The implementation structurally separates the Intake, Governance, and Learning loops; enforces cross-cutting protocols (independence, role separation, meta-governance, orchestration); audits governance changes; and versions policies. This level proves architectural correctness. |

---

## 2. Level 1 Criteria: Receipt Format Compliance

Level 1 verifies that an implementation correctly produces and verifies the cryptographic artifacts defined by the RIO protocol. No governance pipeline is required — only the receipt and ledger data structures and their associated cryptographic operations.

### 2.1 Receipt Structure Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L1-RS-01 | Receipts contain all required fields: `receipt_id`, `timestamp`, `request_hash`, `decision`, `policy_decision`, `risk_score`, `risk_level`, `receipt_hash`, `signature` | Validate against receipt JSON schema; confirm no required field is null or missing. Reference: conformance test TC-V2-001. |
| L1-RS-02 | The `receipt_id` field is a unique identifier (UUID v4 format) | Parse receipt_id as UUID; confirm version 4 format. Verify uniqueness across a batch of 1000 generated receipts. |
| L1-RS-03 | The `timestamp` field is ISO 8601 UTC format | Parse timestamp; confirm ISO 8601 compliance and UTC timezone designation. |
| L1-RS-04 | The `decision` field contains one of the allowed values: `allow`, `block`, `escalate` | Validate decision field against the allowed enum values. |
| L1-RS-05 | Denied or blocked actions produce full v2 receipts with `decision=block` and `execution_status=BLOCKED` | Generate a receipt for a denied action; confirm all required fields are present and decision/execution_status values are correct. Reference: conformance test TC-V2-003. |

### 2.2 Hash Computation Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L1-HC-01 | The `request_hash` is computed as `SHA256(canonical_json(intent))` where canonical_json produces deterministic JSON with sorted keys, no whitespace, and UTF-8 encoding | Compute request_hash from the test intent in `hash_computation_examples.json`; confirm the output matches the expected value. Reference: conformance test TC-V2-005. |
| L1-HC-02 | The `receipt_hash` is computed as `SHA256(receipt_id + timestamp + request_hash + decision + policy_decision + risk_score + execution_status)` with fields concatenated as pipe-delimited strings | Compute receipt_hash from the test receipt in `hash_computation_examples.json`; confirm the output matches the expected value. Reference: conformance test TC-V2-006. |
| L1-HC-03 | All hash computations use SHA-256 and produce lowercase hexadecimal output | Verify all hash outputs are 64-character lowercase hexadecimal strings. |
| L1-HC-04 | The genesis hash is `SHA256(b'GENESIS')` = `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a` | Compute SHA256 of the literal bytes `GENESIS`; confirm the output matches. Reference: test vector `hash_computation_examples.json`. |
| L1-HC-05 | Hash computation is deterministic: identical inputs always produce identical outputs | Compute the same hash 100 times with identical inputs; confirm all outputs are identical. |

### 2.3 Signature Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L1-SG-01 | Receipts are signed using Ed25519 (reference implementation) or RSA-PSS (2048-bit, SHA-256) | Verify that the signature algorithm matches one of the two allowed algorithms. |
| L1-SG-02 | The signing payload is constructed as `SHA256(receipt_hash + request_hash + decision + timestamp)` with fields concatenated as pipe-delimited strings | Construct the signing payload from the test receipt in `signing_payload_examples.json`; confirm the output matches the expected payload hash. Reference: conformance test TC-V2-007. |
| L1-SG-03 | Signatures are valid and verifiable with the corresponding public key | Verify all three signatures in `signing_payload_examples.json` (allow, block, escalate) using `public_key.pem`. All must return PASS. Reference: conformance test TC-V2-008. |
| L1-SG-04 | Invalid signatures are detected and rejected | Verify that `receipt_invalid_signature.json` fails signature verification. Reference: conformance test TC-V2-009. |
| L1-SG-05 | Corrupted receipt hashes are detected and rejected | Verify that `receipt_invalid_hash.json` fails hash verification. Reference: conformance test TC-V2-009. |
| L1-SG-06 | Corrupted request hashes are detected and rejected | Verify that `receipt_invalid_intent_hash.json` fails request hash verification. Reference: conformance test TC-V2-009. |
| L1-SG-07 | Receipts with missing required fields are detected and rejected | Verify that `receipt_missing_fields.json` fails required-fields validation. Reference: conformance test TC-V2-010. |

### 2.4 Ledger Chain Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L1-LC-01 | Ledger entries contain all required fields: `entry_id`, `timestamp`, `receipt_hash`, `ledger_hash`, `previous_ledger_hash`, `signature` | Validate against ledger entry schema; confirm no required field is null or missing. |
| L1-LC-02 | The first ledger entry's `previous_ledger_hash` equals the genesis hash | Verify the first entry in `ledger_chain_valid.json` has `previous_ledger_hash` equal to the genesis hash. |
| L1-LC-03 | Each subsequent entry's `previous_ledger_hash` equals the preceding entry's `ledger_hash` | Walk `ledger_chain_valid.json`; confirm chain linkage for all entries. All must return `chain_intact=True`. |
| L1-LC-04 | Tampered ledger entries are detected | Walk `ledger_chain_tampered.json`; confirm chain integrity check fails at the tampered entry. |
| L1-LC-05 | Deleted ledger entries are detected | Walk `ledger_chain_deleted_entry.json`; confirm chain integrity check fails at the gap. |

### 2.5 Level 1 Interoperability Bar

An implementation claims **RIO Receipt Interoperability** when it satisfies all four conditions:

1. Reproduces all hashes in `hash_computation_examples.json` from the same inputs.
2. Verifies all 3 signatures in `signing_payload_examples.json` with `public_key.pem`.
3. All invalid vectors (`receipt_invalid_signature.json`, `receipt_invalid_hash.json`, `receipt_invalid_intent_hash.json`, `receipt_missing_fields.json`) return FAIL.
4. Walks `ledger_chain_valid.json` with all entries returning `chain_intact=True`.

---

## 3. Level 2 Criteria: Pipeline Compliance

Level 2 verifies that an implementation executes the full 8-stage governance pipeline and enforces all protocol invariants. Level 2 includes all Level 1 criteria.

### 3.1 Pipeline Stage Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L2-PS-01 | Stage 1 (Intake) validates incoming requests and rejects malformed inputs | Submit a malformed request (missing required fields); confirm rejection with appropriate error code. Reference: conformance tests TC-RIO-004 through TC-RIO-008. |
| L2-PS-02 | Stage 2 (Classification) classifies the request origin and type | Submit requests from different origins; confirm classification is recorded in the processing metadata. |
| L2-PS-03 | Stage 3 (Structured Intent) produces a canonical intent with deterministic hash | Submit a request; confirm the structured intent contains all required fields and the intent hash is deterministic (same input produces same hash). |
| L2-PS-04 | Stage 4 (Policy & Risk Evaluation) evaluates policy rules and computes a numeric risk score | Submit requests with varying risk profiles; confirm risk scores and risk levels are computed and recorded. Reference: conformance tests TC-RIO-009 through TC-RIO-015. |
| L2-PS-05 | Stage 5 (Authorization) issues time-bound authorization tokens with single-use nonces for approved requests | Submit a request that requires approval; approve it; confirm the authorization token contains expiry time, nonce, and scope. Reference: conformance tests TC-RIO-016 through TC-RIO-020. |
| L2-PS-06 | Stage 6 (Execution Gate) verifies authorization token validity before permitting execution | Submit a request with a valid token; confirm execution proceeds. Submit a request with an expired token; confirm execution is blocked. Submit a request with a consumed nonce; confirm execution is blocked. Reference: conformance tests TC-RIO-021 through TC-RIO-025. |
| L2-PS-07 | Stage 6b (Post-Execution Verification) independently validates execution results | Submit a request through the full pipeline; confirm the receipt contains `verification_status` and `verification_hash`. Reference: conformance tests TC-RIO-026 through TC-RIO-028. |
| L2-PS-08 | Stage 7 (Receipt Generation) produces a signed v2 receipt for every governance decision | Confirm that approved, denied, and blocked requests all produce signed receipts. Reference: conformance tests TC-V2-001 through TC-V2-004. |
| L2-PS-09 | Stage 8 (Ledger) appends a signed entry to the hash-chain ledger for every receipt | Confirm that every receipt produces a corresponding ledger entry with correct chain linkage. |

### 3.2 Protocol Invariant Criteria

| Criterion ID | Invariant | Requirement | Verification Method |
|--------------|-----------|-------------|---------------------|
| L2-INV-01 | INV-01: Human Authority Preserved | No autonomous execution without explicit human authorization for requests above the auto-approve threshold | Submit a HIGH-risk request without approval; confirm execution is blocked. |
| L2-INV-02 | INV-02: All Decisions Logged | Every governance decision produces a verifiable audit record | Process 100 requests (mix of approved, denied, blocked); confirm each produces a receipt and ledger entry. |
| L2-INV-03 | INV-03: Policy Compliance | Requests violating declared thresholds are denied | Submit a request that violates a policy constraint; confirm denial with the specific policy rule cited. |
| L2-INV-04 | INV-04: Scope Integrity | Response scope matches stated intent; no unexpanded execution | Submit a request with declared scope; confirm execution does not exceed the declared scope. |
| L2-INV-05 | INV-05: Tool Permission Enforcement | Tool usage is within declared agent permissions | Submit a request that attempts to use an undeclared tool; confirm execution is blocked. |
| L2-INV-06 | INV-06: Cryptographic Integrity | Receipts are signed; signatures are verifiable | Verify signatures on all receipts produced during testing; all must pass. |
| L2-INV-07 | INV-07: Ledger Append-Only | The governance ledger forms a valid hash chain from genesis | Verify chain integrity across the full ledger after processing 100 requests; all entries must have `chain_intact=True`. |
| L2-INV-08 | INV-08: Fail-Closed Default | When evaluation fails or is ambiguous, the system denies | Simulate an evaluation failure (e.g., policy engine timeout); confirm the request is denied with appropriate error code. |

### 3.3 Kill Switch Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L2-KS-01 | Kill switch (EKS-0) blocks all new executions when engaged | Engage the kill switch; submit 10 requests; confirm all are blocked with reason `kill_switch_engaged`. |
| L2-KS-02 | Kill switch generates receipts and ledger entries for blocked requests | Confirm that requests blocked by the kill switch produce signed receipts and ledger entries. |
| L2-KS-03 | Kill switch engagement and disengagement are recorded in the ledger | Engage and disengage the kill switch; confirm both events produce ledger entries. |
| L2-KS-04 | Previously blocked requests do not auto-resume after kill switch disengagement | Disengage the kill switch; confirm that requests blocked during the engagement period are not automatically re-executed. |
| L2-KS-05 | Stages 1-4 continue to operate during kill switch engagement | Engage the kill switch; submit a request; confirm it is processed through Stages 1-4 (intake, classification, structured intent, policy evaluation) before being blocked at Stage 6. |

---

## 4. Level 3 Criteria: Full Protocol Compliance

Level 3 verifies that an implementation achieves the full Three-Loop Architecture with structural separation and cross-cutting governance protocols. Level 3 includes all Level 1 and Level 2 criteria.

### 4.1 Three-Loop Architecture Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L3-TL-01 | Intake Loop, Execution/Governance Loop, and Learning Loop are structurally separated | Demonstrate that the three loops operate in separate execution contexts; the Learning Loop cannot write to the runtime, ledger, or execution gate directly. |
| L3-TL-02 | The Learning Loop's only output channel is the governance proposal process | Demonstrate that learning loop outputs are submitted as governance proposals that require approval before taking effect. |
| L3-TL-03 | The Intake Loop produces well-defined structured intents before governance begins | Demonstrate that the Intake Loop validates, refines, and produces canonical intents independently of the Governance Loop. |

### 4.2 Cross-Cutting Protocol Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L3-CC-01 | Independence: No single component can both authorize and execute an action | Demonstrate that the authorization component and execution component are separate; a single process cannot both approve and execute. |
| L3-CC-02 | Role Separation: The 8 defined roles have non-overlapping permissions for critical operations | Demonstrate that role permissions are enforced; a user with the Approver role cannot modify policy rules (Policy Author role). |
| L3-CC-03 | Meta-Governance: Changes to governance rules are themselves governed | Demonstrate that a policy rule change requires approval through the governance pipeline before taking effect. |
| L3-CC-04 | Orchestration: The pipeline orchestrator enforces stage ordering and cannot be bypassed | Demonstrate that stages execute in order (1 through 8) and that no stage can be skipped. |

### 4.3 Governance Change Auditing Criteria

| Criterion ID | Requirement | Verification Method |
|--------------|-------------|---------------------|
| L3-GA-01 | All policy changes are recorded in the ledger with before/after state | Modify a policy rule; confirm the ledger records the previous rule, the new rule, the change author, and the approval chain. |
| L3-GA-02 | Policy versions are tracked and retrievable | Modify a policy rule 3 times; confirm all 3 versions are retrievable with their effective dates and change history. |
| L3-GA-03 | Governance change proposals include rationale and expected impact | Submit a governance change proposal; confirm it includes a rationale field and expected impact assessment. |

---

## 5. Certification Process

### 5.1 Self-Assessment

Before seeking formal certification, organizations should complete a self-assessment against the criteria for their target conformance level. The self-assessment process follows these steps.

**Step 1: Select Target Level.** Determine which conformance level is appropriate for your deployment. Level 1 is sufficient for systems that consume RIO receipts but do not operate a governance pipeline. Level 2 is required for systems that operate a governance pipeline. Level 3 is required for systems that claim full RIO protocol compliance.

**Step 2: Run Conformance Tests.** Execute the conformance test suite (`tests/conformance/rio_conformance_suite_v1.json`) against your implementation. Record all test results, including pass/fail status, actual outputs, and any error messages.

**Step 3: Run Test Vectors.** Process all 12 test vector files in `tests/vectors/` through your implementation. Record hash outputs, signature verification results, and chain integrity results.

**Step 4: Document Results.** Prepare a conformance report that includes: implementation description (language, architecture, deployment model), test results for each criterion at your target level, any deviations from the reference implementation with justification, and a statement of conformance level claimed.

### 5.2 Formal Certification

Formal certification involves independent review of the self-assessment results. The process follows these steps.

| Step | Activity | Duration | Output |
|------|----------|----------|--------|
| 1 | Submit conformance report and implementation documentation | — | Submission package |
| 2 | Independent reviewer verifies test results against test vectors | 5-10 business days | Verification report |
| 3 | Independent reviewer runs the independent verifier (WS4) against a sample of the implementation's receipts and ledger entries | 5-10 business days | Cross-verification report |
| 4 | Review panel evaluates the verification and cross-verification reports | 5 business days | Certification decision |
| 5 | Certification issued (or remediation items identified) | 2 business days | Certificate or remediation list |

### 5.3 Evidence Requirements

| Conformance Level | Required Evidence |
|-------------------|-------------------|
| Level 1 | Conformance test results for all L1 criteria; test vector outputs; hash computation logs; signature verification logs |
| Level 2 | All Level 1 evidence + pipeline execution logs for 100+ requests; invariant enforcement demonstrations; kill switch test results |
| Level 3 | All Level 2 evidence + Three-Loop Architecture documentation; cross-cutting protocol demonstrations; governance change audit logs; policy version history |

### 5.4 Reviewer Qualifications

Independent reviewers must have demonstrated expertise in cryptographic protocol verification, software security auditing, or AI governance framework assessment. The review panel should include at least one member with experience in each of these areas.

---

## 6. Certification Maintenance

### 6.1 Certification Validity

Certifications are valid for **12 months** from the date of issuance. During this period, the certified implementation must continue to satisfy all criteria for its conformance level.

### 6.2 Re-Certification Triggers

Re-certification is required when any of the following events occur, regardless of the 12-month validity period:

| Trigger | Reason | Grace Period |
|---------|--------|--------------|
| Protocol version update (major) | New major version may change cryptographic algorithms, schema, or invariants | 6 months from new version publication |
| Protocol version update (minor) | New minor version adds requirements but maintains backward compatibility | 3 months from new version publication |
| Implementation architecture change | Fundamental changes to the implementation may affect conformance | 30 days from change deployment |
| Security incident affecting governance layer | Incidents may reveal conformance gaps | Immediate re-assessment; 60 days for full re-certification |

### 6.3 Backward Compatibility

When a new protocol version is published, the following backward compatibility rules apply.

**Patch versions** (e.g., 1.0.0 to 1.0.1) do not require re-certification. Patch versions fix errata and clarify existing requirements without changing behavior.

**Minor versions** (e.g., 1.0.0 to 1.1.0) add new optional requirements. Existing certifications remain valid for the original conformance level. To claim the new minor version, the implementation must satisfy the new requirements.

**Major versions** (e.g., 1.0.0 to 2.0.0) may change fundamental requirements. Existing certifications remain valid for a 6-month grace period. After the grace period, the implementation must be re-certified against the new major version.

### 6.4 Certification Registry

Certified implementations are recorded in a public registry that includes: organization name, implementation name and version, conformance level, certification date, expiry date, and reviewer identity. The registry provides transparency for organizations evaluating RIO-compliant products and services.

---

## Appendix A: Criterion Cross-Reference

The following table maps each criterion to its corresponding conformance test case, test vector, and protocol invariant.

| Criterion | Test Case | Test Vector | Invariant |
|-----------|-----------|-------------|-----------|
| L1-RS-01 | TC-V2-001 | receipt_valid_approved.json | — |
| L1-HC-01 | TC-V2-005 | hash_computation_examples.json | — |
| L1-HC-04 | — | hash_computation_examples.json (genesis) | — |
| L1-SG-03 | TC-V2-008 | signing_payload_examples.json, public_key.pem | INV-06 |
| L1-SG-04 | TC-V2-009 | receipt_invalid_signature.json | INV-06 |
| L1-LC-03 | — | ledger_chain_valid.json | INV-07 |
| L1-LC-04 | — | ledger_chain_tampered.json | INV-07 |
| L2-INV-01 | TC-RIO-001 | — | INV-01 |
| L2-INV-08 | TC-RIO-003 | — | INV-08 |
| L2-KS-01 | TC-RIO-003 | — | INV-08 |
