# RIO Protocol — Implementation Guide

**Version:** 1.0.0
**Status:** Adoption Documentation
**Category:** Implementation & Deployment

---

## Purpose

This guide walks engineering teams through the process of implementing a RIO-compliant governance system from scratch. It covers architecture decisions, component design, integration patterns, testing strategy, and operational considerations. The guide is organized as a sequence of implementation phases, each building on the previous one.

> **Prerequisites:** Readers should be familiar with the RIO Core Runtime Behavior document, which defines the protocol's data structures, cryptographic operations, and pipeline stages. This guide explains *how* to implement those requirements; the behavior document defines *what* the requirements are.

---

## 1. Architecture Overview

A RIO-compliant system consists of five major components that work together to govern AI-initiated actions. Before writing any code, teams should understand how these components interact and where the trust boundaries lie.

### 1.1 Component Map

| Component | Responsibility | Trust Level |
|-----------|---------------|-------------|
| **Pipeline Orchestrator** | Executes the 8-stage pipeline in order; enforces stage sequencing; prevents stage skipping | Trusted — must be tamper-resistant |
| **Policy Engine** | Evaluates policy rules and computes risk scores; determines whether a request requires approval, is auto-approved, or is denied | Trusted — policy rules are the organization's governance logic |
| **Approval Service** | Routes approval requests to human approvers; collects decisions; issues authorization tokens | Trusted — handles human authority delegation |
| **Execution Gate** | Validates authorization tokens; enforces single-use nonces; controls access to execution | Trusted — the last checkpoint before real-world action |
| **Cryptographic Module** | Generates hashes, signs receipts and ledger entries, verifies signatures | Trusted — handles key material; must be isolated |

### 1.2 Trust Boundaries

The RIO protocol defines three trust boundaries that implementations must enforce.

**Boundary 1: Intake to Governance.** The Intake Loop (Stages 1-3) transforms raw requests into canonical intents. The output of the Intake Loop is the input to the Governance Loop. The Intake Loop does not make governance decisions — it only normalizes and validates.

**Boundary 2: Governance to Execution.** The Execution Gate (Stage 6) is the boundary between governance decisions and real-world actions. No execution occurs without a valid, unexpired, unconsumed authorization token. This boundary is the protocol's primary safety mechanism.

**Boundary 3: Learning to Governance.** The Learning Loop analyzes historical decisions to propose governance improvements. Learning Loop outputs are *proposals*, not directives. They must pass through the governance pipeline (meta-governance) before taking effect. The Learning Loop cannot write to the runtime, ledger, or execution gate directly.

### 1.3 Technology Choices

The RIO protocol is language-agnostic and platform-agnostic. The reference implementation uses Python, but any language that supports SHA-256 hashing, RSA-PSS or Ed25519 signatures, and JSON serialization can implement the protocol. The following table summarizes the cryptographic requirements that constrain technology choices.

| Requirement | Specification | Common Libraries |
|-------------|---------------|------------------|
| Hashing | SHA-256, lowercase hex output | OpenSSL, libsodium, Web Crypto API, hashlib (Python), crypto (Node.js) |
| Signing (Option A) | RSA-PSS, 2048-bit, SHA-256, MGF1-SHA-256, max salt length | OpenSSL, Web Crypto API, cryptography (Python), node-forge |
| Signing (Option B) | Ed25519 | libsodium, tweetnacl, cryptography (Python), @noble/ed25519 |
| JSON Serialization | Sorted keys, no whitespace, UTF-8 encoding | Standard library JSON in most languages (with sort_keys option) |
| UUID Generation | Version 4 (random) | Standard library uuid in most languages |
| Timestamp Format | ISO 8601 UTC (receipts), Unix epoch milliseconds (ledger) | Standard library datetime in most languages |

---

## 2. Phase 1: Receipt and Ledger Layer (Level 1)

The first implementation phase builds the cryptographic foundation: receipt generation, receipt verification, ledger writing, and ledger verification. This phase corresponds to **Certification Level 1** and can be completed independently of the governance pipeline.

### 2.1 Implement the Hash Functions

Start by implementing the three hash functions defined in the protocol. All three use the same pattern: construct a JSON object, serialize with sorted keys, compute SHA-256, output lowercase hex.

**Intent Hash.** Construct a JSON object with exactly five fields (`intent_id`, `action_type`, `requested_by`, `target_resource`, `parameters`). Serialize with sorted keys at every nesting level. Compute SHA-256 of the UTF-8 encoded string. Output the 64-character lowercase hex digest.

**Action Hash.** Same pattern applied to the execution result payload.

**Receipt Hash.** Construct a JSON object with exactly 13 fields (see Section 5.3 of the behavior document). Serialize with sorted keys. Concatenate the serialized JSON with the `previous_hash` string. Compute SHA-256 of the UTF-8 encoded concatenation.

The critical implementation detail for the receipt hash is that `previous_hash` is concatenated *after* the JSON serialization, not included within the JSON object. This makes the receipt hash dependent on both the receipt's content and its position in the chain.

**Validation step:** Compute the genesis hash `SHA256(b'GENESIS')` and confirm the output is `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a`. If this does not match, the SHA-256 implementation or encoding is incorrect.

### 2.2 Implement the Signing Module

Implement the signing and verification functions using either RSA-PSS or Ed25519.

**For RSA-PSS:** Generate a 2048-bit RSA key pair. Configure PSS padding with SHA-256 hash, MGF1 with SHA-256, and maximum salt length (32 bytes for SHA-256). Sign the UTF-8 encoded signing payload. Base64-encode the raw signature bytes.

**For Ed25519:** Generate an Ed25519 key pair. Sign the UTF-8 encoded signing payload. Base64-encode the raw signature bytes.

**Receipt signing payload construction:** Concatenate six fields with no separator: `intent_hash + action_hash + decision + timestamp_execution + receipt_hash + previous_hash`. This is the string that gets signed.

**Ledger signing payload:** The signing payload is simply the `ledger_hash` string (64-character hex).

**Validation step:** Sign a known payload, then verify the signature with the public key. Both operations must succeed. Then corrupt one byte of the signature and confirm that verification fails.

### 2.3 Implement the Ledger Writer

The ledger writer appends entries to the hash chain. Each entry requires:

1. Construct the ledger entry fields from the receipt data.
2. Look up the `ledger_hash` of the most recent entry (or use empty string for genesis).
3. Set `previous_ledger_hash` to that value.
4. Concatenate all fields in the exact order specified (Section 6.3 of the behavior document) with no separator.
5. Compute `ledger_hash` as SHA-256 of the UTF-8 encoded concatenation.
6. Sign the `ledger_hash` to produce `ledger_signature`.
7. Persist the entry.

**Validation step:** Write 3 entries to the ledger. Walk the chain and verify that each entry's `previous_ledger_hash` matches the preceding entry's `ledger_hash`. Verify all signatures. Then tamper with one entry's `decision` field and confirm that the hash verification fails.

### 2.4 Implement the Ledger Verifier

The ledger verifier walks the chain and checks four things for each entry: hash correctness, signature validity, chain linkage, and receipt linkage.

**Validation step:** Run the verifier against the test vectors in `tests/vectors/`. Confirm that `ledger_chain_valid.json` passes all checks, `ledger_chain_tampered.json` fails at the tampered entry, and `ledger_chain_deleted_entry.json` fails at the gap.

### 2.5 Level 1 Completion Checklist

At the end of Phase 1, the implementation should pass all Level 1 certification criteria (L1-RS-01 through L1-LC-05). Run the conformance test suite at Level 1 and confirm all tests pass. The implementation can now claim **Receipt Format Compliance**.

---

## 3. Phase 2: Governance Pipeline (Level 2)

The second phase builds the 8-stage governance pipeline on top of the cryptographic layer. This phase corresponds to **Certification Level 2**.

### 3.1 Stage 1: Intake

The Intake stage receives raw requests and performs initial validation. Implement the following:

1. Assign a `request_id` (UUID v4) to each incoming request.
2. Validate that the request contains the minimum required fields: `action_type`, `requested_by`, `target_resource`.
3. Resolve the actor identity from the authentication layer.
4. Record the intake timestamp (ISO 8601 UTC).
5. If validation fails, generate a denial receipt and stop processing.

### 3.2 Stage 2: Classification

The Classification stage examines the validated request to determine the action type and preliminary risk category. Implement the following:

1. Map the `action_type` to a risk category using the classification rules (see Section 1.5 of the behavior document).
2. If the action type is not recognized, assign a default risk category (MEDIUM is recommended).
3. Record the classification result in the pipeline context.

### 3.3 Stage 3: Structured Intent

The Structured Intent stage converts the validated, classified request into the canonical Intent Envelope format. Implement the following:

1. Construct the Intent Envelope with all required fields (see Section 1.2 of the behavior document).
2. Validate action-specific parameters against the Intent Requirements Matrix (see Section 1.3 of the behavior document).
3. If parameter validation fails, generate a denial receipt and stop processing.
4. Compute the intent hash using the canonicalization rules (see Section 1.4 of the behavior document).

### 3.4 Stage 4: Policy and Risk Evaluation

The Policy and Risk Evaluation stage applies policy rules and computes a numeric risk score. Implement the following:

1. Load the applicable policy rules for the action type.
2. Evaluate each rule against the intent envelope.
3. Compute a numeric risk score based on the risk engine's evaluation factors: coherence score, somatic markers, scope boundaries, and tool permissions.
4. Classify the risk level: LOW (score below low threshold), MEDIUM (between low and high thresholds), HIGH (between high and critical thresholds), CRITICAL (above critical threshold).
5. Determine the routing decision based on risk level: LOW requests are auto-approved, MEDIUM and HIGH requests require human approval, CRITICAL requests are auto-denied.
6. If the policy denies the request, generate a denial receipt and stop processing.

**Implementation note:** The risk scoring thresholds should be configurable, not hardcoded. The reference implementation uses `low_threshold=0.3`, `high_threshold=0.7`, and `critical_threshold=0.9`, but production deployments should tune these values to their domain.

### 3.5 Stage 5: Authorization

The Authorization stage handles approval routing and token issuance. Implement the following:

**For auto-approved requests (LOW risk):**
1. Generate an authorization token with `approved_by="system_auto"`.
2. Set the token expiry time (default: 300 seconds from issuance).
3. Set `single_use=true`.
4. Generate a unique `authorization_id` (UUID v4) as the nonce.
5. Proceed to Stage 6.

**For requests requiring human approval (MEDIUM/HIGH risk):**
1. Route the approval request to the appropriate approver(s) based on the action type and risk level.
2. Present the full intent envelope, risk score, and policy rationale to the approver.
3. Wait for the approval decision.
4. If approved: generate an authorization token as above, with `approved_by` set to the approver's identity.
5. If denied: generate a denial receipt and stop processing.

**For auto-denied requests (CRITICAL risk):**
1. Generate a denial receipt with `approved_by="system:policy"` and the denial reason.
2. Stop processing.

### 3.6 Stage 6: Execution Gate

The Execution Gate is the protocol's primary safety mechanism. It validates the authorization token before permitting execution. Implement the following checks in this exact order:

1. **Token presence:** Verify that an authorization token is attached to the request. If not, deny.
2. **Token expiry:** Verify that the current time is before the token's expiry time. If expired, deny.
3. **Nonce consumption:** Verify that the `authorization_id` has not been previously consumed. If consumed, deny (replay attack prevention).
4. **Scope match:** Verify that the token's authorized scope matches the requested action. If mismatched, deny.
5. **Kill switch check:** Verify that the kill switch is not engaged. If engaged, deny.

If all checks pass, mark the `authorization_id` as consumed (add to the consumed set) and permit execution.

**Implementation note:** The nonce consumption check and the mark-as-consumed operation must be atomic. If two requests arrive with the same `authorization_id`, only one should succeed. Use a database transaction, atomic compare-and-swap, or similar mechanism.

### 3.7 Stage 6b: Post-Execution Verification

After execution completes, the protocol runs a verification step. Implement the following:

1. Compare the execution result against the authorized intent.
2. Verify that the execution did not exceed the authorized scope.
3. Produce a verification result object.
4. Compute the verification hash.
5. Set `verification_status` to `"verified"` or `"failed"`.

### 3.8 Stage 7: Receipt Generation

Generate a signed v2 receipt for every governance decision. This stage uses the receipt generation logic from Phase 1 (Section 2.1-2.2 of this guide). Ensure that receipts are generated for all exit paths: successful execution, failed execution, policy denial, validation failure, kill switch block, and token rejection.

### 3.9 Stage 8: Ledger Append

Append a signed ledger entry for every receipt. This stage uses the ledger writer from Phase 1 (Section 2.3 of this guide).

### 3.10 Implement the Kill Switch (EKS-0)

The kill switch is a global halt mechanism. Implement the following:

1. A boolean state flag (`kill_switch_engaged`) that defaults to `false`.
2. When engaged: all requests that reach the Execution Gate (Stage 6) are blocked with reason `kill_switch_engaged`. Stages 1-4 continue to operate normally.
3. When disengaged: normal processing resumes. Requests blocked during the engagement period are NOT automatically re-executed; they must be re-submitted.
4. Engagement and disengagement events produce ledger entries.

### 3.11 Implement the Protocol Invariants

The 8 protocol invariants must be enforced at runtime, not just documented. The following table maps each invariant to its enforcement point.

| Invariant | Enforcement Point | Implementation |
|-----------|-------------------|----------------|
| INV-01: Human Authority Preserved | Stage 5 (Authorization) | Requests above auto-approve threshold require human approval before execution |
| INV-02: All Decisions Logged | Stage 7-8 (Receipt + Ledger) | Every pipeline exit path generates a receipt and ledger entry |
| INV-03: Policy Compliance | Stage 4 (Policy Evaluation) | Requests violating policy constraints are denied |
| INV-04: Scope Integrity | Stage 6b (Verification) | Post-execution verification checks scope compliance |
| INV-05: Tool Permission Enforcement | Stage 4 (Policy Evaluation) | Policy engine validates tool permissions against declared agent capabilities |
| INV-06: Cryptographic Integrity | Stage 7 (Receipt Generation) | All receipts are signed; all hashes are computed correctly |
| INV-07: Ledger Append-Only | Stage 8 (Ledger) | Ledger entries form a valid hash chain; no deletions or modifications |
| INV-08: Fail-Closed Default | All stages | Any ambiguous or failed evaluation results in denial |

### 3.12 Level 2 Completion Checklist

At the end of Phase 2, the implementation should pass all Level 2 certification criteria (L2-PS-01 through L2-KS-05). Run the conformance test suite at Level 2 and confirm all tests pass. The implementation can now claim **Pipeline Compliance**.

---

## 4. Phase 3: Three-Loop Architecture (Level 3)

The third phase implements the structural separation required for full protocol compliance. This phase corresponds to **Certification Level 3**.

### 4.1 Structural Separation

The Three-Loop Architecture requires that the Intake Loop, Governance Loop, and Learning Loop operate as structurally independent components. "Structurally independent" means:

**The Intake Loop** receives raw requests and produces canonical intents. It does not access the policy engine, approval service, or execution gate. Its only output is a well-formed Intent Envelope.

**The Governance Loop** receives canonical intents and produces receipts and ledger entries. It contains the policy engine, approval service, execution gate, verification, receipt generation, and ledger. It does not modify the Intake Loop's behavior or the Learning Loop's analysis.

**The Learning Loop** reads historical data from the ledger and produces governance improvement proposals. It does not write to the runtime, ledger, or execution gate directly. Its proposals must pass through the governance pipeline (meta-governance) before taking effect.

### 4.2 Cross-Cutting Protocols

Implement the four cross-cutting protocols that span the architecture:

**Independence Protocol.** No single component can both authorize and execute an action. The authorization component (Stage 5) and the execution component (Stage 6) must be separate processes or modules with distinct access controls.

**Role Separation Protocol.** The 8 defined roles (Requester, Approver, Administrator, Auditor, Policy Author, Risk Analyst, System Operator, Security Officer) have non-overlapping permissions for critical operations. Implement role-based access control that enforces these boundaries.

**Meta-Governance Protocol.** Changes to governance rules (policy rules, risk thresholds, role assignments) must themselves pass through the governance pipeline. This means a policy change is treated as a governed action: it has an intent, undergoes policy evaluation, requires approval, and produces a receipt and ledger entry.

**Orchestration Protocol.** The pipeline orchestrator enforces stage ordering (1 through 8) and prevents stage skipping. No stage can be bypassed, and stages must execute in sequence.

### 4.3 Governance Change Auditing

Implement governance change auditing:

1. Record the before-state and after-state of every policy change in the ledger.
2. Track policy versions with effective dates and change history.
3. Require rationale and expected impact assessment for every governance change proposal.

### 4.4 Level 3 Completion Checklist

At the end of Phase 3, the implementation should pass all Level 3 certification criteria (L3-TL-01 through L3-GA-03). The implementation can now claim **Full Protocol Compliance**.

---

## 5. Integration Patterns

This section describes common patterns for integrating RIO into existing systems.

### 5.1 AI Agent Integration

The most common integration pattern places RIO between an AI agent and the systems it interacts with. The AI agent generates action requests, RIO governs them, and only approved actions reach the target systems.

The integration flow is as follows. The AI agent produces a raw action request (e.g., "send email to client@example.com with subject 'Invoice'"). The RIO Intake Loop normalizes this into a canonical Intent Envelope. The Governance Loop evaluates the intent against policy rules and risk thresholds. If the risk level requires human approval, the Approval Service routes the request to the appropriate approver. If approved, the Execution Gate permits the action. The target system (e.g., email service) executes the action. Post-execution verification confirms the outcome. A signed receipt and ledger entry record the complete decision chain.

### 5.2 API Gateway Integration

For organizations with existing API gateways, RIO can be integrated as a middleware layer. Incoming API requests are intercepted by the RIO pipeline before reaching the backend services. This pattern is useful for governing AI-initiated API calls without modifying the backend services.

### 5.3 Event-Driven Integration

For event-driven architectures, RIO can govern events before they are published to the event bus. The event producer submits the event to RIO as an action request. If approved, the event is published. If denied, the event is blocked and a denial receipt is generated.

### 5.4 Batch Processing Integration

For batch processing systems, RIO can govern each item in the batch individually or the batch as a whole. Individual governance provides finer-grained control but increases latency. Batch-level governance is faster but provides less granularity. The choice depends on the risk profile of the batch items.

---

## 6. Operational Considerations

### 6.1 Key Management

The signing keys are the most sensitive assets in a RIO deployment. The following practices are recommended.

**Key generation:** Generate keys using a cryptographically secure random number generator. For RSA-PSS, use 2048-bit keys. For Ed25519, use the standard 256-bit key generation.

**Key storage:** Store private keys in a hardware security module (HSM), key management service (KMS), or encrypted key store. Never store private keys in plaintext on disk or in environment variables.

**Key rotation:** Establish a key rotation schedule. When rotating keys, the new key signs new receipts and ledger entries, while the old public key remains available for verifying historical artifacts. Record key rotation events in the ledger.

**Key backup:** Maintain encrypted backups of key material in a separate, secure location. Test key restoration procedures regularly.

### 6.2 Ledger Storage

The ledger is append-only and grows continuously. Plan for storage growth based on the expected request volume.

| Request Volume | Approximate Ledger Growth | Recommended Storage |
|----------------|--------------------------|---------------------|
| 100 requests/day | ~50 MB/year | Local database |
| 10,000 requests/day | ~5 GB/year | Managed database |
| 1,000,000 requests/day | ~500 GB/year | Distributed database with partitioning |

**Retention policy:** Define a retention period appropriate to your regulatory requirements. The EU AI Act requires record-keeping for the lifetime of the AI system plus a reasonable period after decommissioning. SOC 2 typically requires 12 months of audit logs. Consult your compliance team for specific requirements.

**Backup strategy:** Back up the ledger regularly. Because the ledger is a hash chain, partial backups are useful — you can verify chain integrity from any starting point by checking the chain linkage forward.

### 6.3 Performance Considerations

The RIO pipeline adds latency to every governed action. The following table provides approximate latency budgets for each stage.

| Stage | Typical Latency | Notes |
|-------|----------------|-------|
| Intake (Stage 1) | 1-5 ms | Field validation and UUID generation |
| Classification (Stage 2) | 1-5 ms | Rule lookup |
| Structured Intent (Stage 3) | 5-10 ms | Parameter validation and hash computation |
| Policy & Risk (Stage 4) | 5-20 ms | Rule evaluation and risk scoring |
| Authorization (Stage 5) | 1 ms (auto) / minutes-hours (human) | Human approval is the dominant latency factor |
| Execution Gate (Stage 6) | 1-5 ms | Token validation and nonce check |
| Verification (Stage 6b) | 5-50 ms | Depends on verification complexity |
| Receipt Generation (Stage 7) | 5-10 ms | Hash computation and signing |
| Ledger Append (Stage 8) | 5-20 ms | Hash computation, signing, and persistence |
| **Total (auto-approved)** | **30-130 ms** | Without human approval |

For latency-sensitive applications, consider the following optimizations: pre-compute intent hashes during the intake stage, use connection pooling for database-backed ledgers, and batch ledger writes for high-throughput scenarios (while maintaining per-receipt ordering guarantees).

### 6.4 Monitoring and Alerting

Implement monitoring for the following operational metrics:

| Metric | Alert Threshold | Significance |
|--------|----------------|--------------|
| Pipeline error rate | > 1% of requests | Indicates systemic issues in the pipeline |
| Denial rate | Sudden increase > 2x baseline | May indicate policy misconfiguration or attack |
| Approval queue depth | > 100 pending requests | Approvers may be overwhelmed; consider policy tuning |
| Ledger chain integrity | Any break | Critical — indicates tampering or corruption |
| Signature verification failure rate | > 0% | Critical — indicates key compromise or implementation bug |
| Kill switch engagement | Any engagement | Requires immediate investigation |
| Authorization token expiry rate | > 10% | Approval-to-execution latency may be too high |

### 6.5 Disaster Recovery

Define recovery procedures for the following scenarios:

**Scenario 1: Key compromise.** Rotate keys immediately. Record the rotation in the ledger. All receipts signed with the compromised key remain verifiable with the old public key but should be flagged for review.

**Scenario 2: Ledger corruption.** Restore from the most recent verified backup. Replay any receipts generated after the backup timestamp. Verify chain integrity after restoration.

**Scenario 3: Kill switch engaged in error.** Disengage the kill switch. Review the engagement event in the ledger. Re-submit any requests that were blocked during the engagement period.

**Scenario 4: Policy engine failure.** The fail-closed invariant (INV-08) ensures all requests are denied during the failure. Restore the policy engine. No requests are lost — they can be re-submitted after restoration.

---

## 7. Testing Strategy

### 7.1 Unit Tests

Write unit tests for every cryptographic operation: hash computation, signing, verification, chain linkage. Use the test vectors in `tests/vectors/` as the primary test data. Every hash computation test should compare against the pre-computed expected values in the test vectors.

### 7.2 Integration Tests

Write integration tests that exercise the full pipeline for each decision type: auto-approved, human-approved, policy-denied, validation-failed, kill-switch-blocked, token-expired. Each test should verify the complete receipt and ledger entry.

### 7.3 Conformance Tests

Run the conformance test suite (`tests/conformance/rio_conformance_suite_v1.json`) against the implementation. The suite defines 57 test cases organized by category. All tests at the target certification level must pass.

### 7.4 Invariant Tests

Write specific tests for each of the 8 protocol invariants. Each test should demonstrate both the positive case (invariant holds) and the negative case (invariant violation is detected and handled correctly).

### 7.5 Adversarial Tests

Write tests that attempt to violate the protocol's security properties: replay attacks (reuse authorization tokens), tampering (modify receipt fields after signing), chain manipulation (insert, delete, or reorder ledger entries), scope escalation (execute actions beyond the authorized scope), and bypass attempts (skip pipeline stages).

---

## 8. Migration from Non-Governed Systems

For organizations adding RIO governance to existing AI systems, the following migration strategy minimizes disruption.

### 8.1 Phase A: Audit Mode

Deploy RIO in audit mode: the pipeline runs for every request, generates receipts and ledger entries, but does not block execution. This phase reveals the governance profile of existing operations — what would be approved, denied, or escalated under the new policy rules.

**Duration:** 2-4 weeks, depending on request volume and diversity.

**Output:** Governance profile report showing risk distribution, denial rate, and approval queue projections.

### 8.2 Phase B: Soft Enforcement

Enable enforcement for low-risk action types first. Auto-approved requests pass through the pipeline with minimal latency impact. Higher-risk action types remain in audit mode.

**Duration:** 2-4 weeks per action type category.

**Output:** Validated pipeline performance for each action type; tuned risk thresholds.

### 8.3 Phase C: Full Enforcement

Enable enforcement for all action types. Human approval routing is active. The kill switch is available for emergency halt.

**Duration:** Ongoing.

**Output:** Fully governed system with complete audit trail.

### 8.4 Migration Checklist

| Step | Action | Verification |
|------|--------|--------------|
| 1 | Deploy RIO pipeline in audit mode | Receipts generated for all requests; no execution blocking |
| 2 | Analyze governance profile | Risk distribution matches expectations; denial rate is reasonable |
| 3 | Tune policy rules and risk thresholds | Thresholds produce acceptable approval queue depth |
| 4 | Enable enforcement for LOW-risk actions | Auto-approved requests pass through with < 200ms added latency |
| 5 | Enable enforcement for MEDIUM-risk actions | Human approval routing works; approvers receive requests |
| 6 | Enable enforcement for HIGH/CRITICAL actions | Full governance active; kill switch tested |
| 7 | Run Level 2 conformance tests | All tests pass |
| 8 | Decommission audit mode | All requests are governed |

---

## References

[1]: RIO Core Runtime Behavior v1.0.0 — Canonical implementation-independent reference document.

[2]: RIO Protocol Certification Criteria v1.0.0 — Conformance levels and certification requirements.

[3]: RIO Conformance Test Suite v1.0 — 57 test cases and 12 test vector files.
