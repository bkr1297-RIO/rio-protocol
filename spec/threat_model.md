# RIO Protocol Threat Model

## 1. Overview

This document identifies and analyzes the security threats that the RIO Protocol is designed to mitigate. It serves as a formal threat model for any organization implementing or evaluating the protocol.

**Scope.** This threat model covers all components within the RIO trust boundary: the intake service, origin verification service, canonical request formation, risk evaluation engine, policy constraints engine, authorization service, execution gate, attestation service, audit ledger, and the communication channels between them.

**Methodology.** Threats are identified using a combination of STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) and attack tree analysis. Each threat is assessed for severity (Critical, High, Medium, Low) and likelihood (High, Medium, Low), and mapped to the specific RIO mitigation mechanisms.

**Audience.** Security architects, protocol implementers, auditors, and compliance officers evaluating the RIO Protocol for deployment.

---

## 2. Security Model: Fail-Closed Enforcement

The RIO Protocol operates on a **fail-closed** security model. This means that every component in the protocol stack defaults to **denying** action execution when it cannot positively verify a required condition. There is no "fail-open" mode. This design principle applies universally:

- If the intake service cannot verify the origin signature, the request is **rejected**.
- If the risk evaluation engine cannot compute a risk score, the request is **held** (not forwarded).
- If the execution gate cannot verify the authorization signature, the action is **not executed**.
- If the execution gate cannot confirm the nonce is unused, the action is **not executed**.
- If the execution gate cannot confirm the authorization has not expired, the action is **not executed**.
- If the attestation service cannot verify all prior signatures and hashes, the attestation is **not issued**.
- If the audit ledger cannot append an entry, the system **halts** the pipeline.

This model ensures that any failure — whether caused by an attack, a misconfiguration, or a transient system error — results in the **safest possible outcome**: no action is taken. The cost of a false denial (a legitimate action is temporarily blocked) is always preferable to the cost of a false approval (an unauthorized action is executed).

---

## 3. System Boundaries

### Inside the RIO Trust Boundary

- Intake Service (receives raw action requests)
- Origin Verification Service (validates requester identity)
- Canonical Request Formation (normalizes and hashes requests)
- Risk Evaluation Engine (scores risk and produces recommendations)
- Policy Constraints Engine (evaluates organizational policies)
- Authorization Service (manages human/delegated authority decisions)
- Execution Gate (validates authorization and dispatches execution)
- Execution Service (performs the authorized action)
- Attestation Service (produces cryptographic proof of the chain)
- Audit Ledger (stores tamper-evident records)
- Nonce Registry (tracks consumed nonces for replay prevention)
- Key Management Infrastructure (manages signing keys)

### Outside the RIO Trust Boundary

- AI agents and automated systems that submit action requests
- External systems that receive executed actions (payment networks, email servers, databases)
- Human authorizers' devices (mobile phones, workstations)
- Network infrastructure between components
- Operating systems and hardware hosting RIO services

---

## 4. Threat Catalog

### T-01: Replay Attack

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-01 |
| **Threat Name** | Replay Attack |
| **Description** | An attacker captures a valid, signed authorization record and attempts to submit it a second time to execute the same action again (e.g., duplicating a $48,250 wire transfer). |
| **Attack Vector** | Network interception of the authorization record or execution token, followed by resubmission to the execution gate. |
| **Affected Components** | Execution Gate, Nonce Registry, Authorization Service |
| **Severity** | **Critical** — Could result in duplicate financial transactions, repeated data modifications, or unauthorized resource consumption. |
| **Impact** | Direct financial loss, data integrity compromise, and loss of trust in the governance system. |

**RIO Mitigation:**

1. **Single-use nonces.** Every authorization record contains a unique `nonce` field. The execution gate MUST check the nonce against the Nonce Registry before executing. If the nonce has been consumed, the request is rejected (Spec 07: Execution, Spec 15: Time-Bound Authorization).
2. **Nonce Registry.** The `nonce_registry.json` schema defines a persistent registry of all consumed nonces. Each entry records the `authorization_id`, `consumed_at` timestamp, and `execution_id`. Nonces transition to `consumed` status upon first use and cannot be reused.
3. **Time-bound authorization.** Authorization records include an `expires_at` field. Even if an attacker captures a nonce before it is consumed, the authorization window (typically 300 seconds) limits the attack surface.
4. **Attestation chain hash.** The attestation record binds the execution to a specific authorization via the `chain_hash`. A replayed authorization would produce a duplicate chain hash, detectable during attestation.

**Residual Risk:** If the Nonce Registry is compromised or unavailable, the system MUST fail closed (deny execution). Clock synchronization issues could theoretically extend the replay window; mitigated by T-10 controls.

**References:** Spec 07 (Execution), Spec 15 (Time-Bound Authorization), `nonce_registry.json`, `authorization_record.json`

---

### T-02: Forged Signature

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-02 |
| **Threat Name** | Forged Signature |
| **Description** | An attacker creates a fake cryptographic signature on an authorization record, execution token, or attestation record to impersonate a legitimate authorizer or service. |
| **Attack Vector** | Key compromise, weak key generation, or exploitation of signature verification implementation flaws. |
| **Affected Components** | Authorization Service, Execution Gate, Attestation Service, Key Management Infrastructure |
| **Severity** | **Critical** — A forged authorization signature would allow unauthorized action execution. |
| **Impact** | Complete bypass of the authorization control, enabling any action without legitimate human approval. |

**RIO Mitigation:**

1. **ECDSA-secp256k1 signatures.** All authorization records, execution tokens, and attestation records MUST be signed using ECDSA with the secp256k1 curve, providing 128-bit security equivalent.
2. **Signature verification at every boundary.** The execution gate MUST independently verify the authorization signature before proceeding. The attestation service MUST verify all prior signatures as part of its `signature_verification` check.
3. **Public key registry.** Each signing entity's public key is registered and associated with a `public_key_id`. The verifier resolves the key from the registry — not from the message itself — preventing key substitution attacks.
4. **Signed fields hash.** The signature covers a `signed_fields_hash` (SHA-256 of the canonicalized signed content), ensuring that the signature is bound to specific data and cannot be transplanted to a different record.

**Residual Risk:** If the private key of an authorizer is compromised, forged signatures become possible until the key is revoked. Key rotation and hardware security modules (HSMs) reduce this risk.

**References:** Spec 06 (Authorization), Spec 08 (Attestation), `authorization_record.json` (signature field), `attestation_record.json` (signatures array), System Manifest (cryptography section)

---

### T-03: Tampered Payload

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-03 |
| **Threat Name** | Tampered Payload |
| **Description** | An attacker intercepts and modifies the canonical request after it has been authorized — for example, changing the wire transfer amount from $48,250 to $480,250 or changing the recipient account. |
| **Attack Vector** | Man-in-the-middle attack between the authorization service and execution gate, or compromise of a message queue or API gateway. |
| **Affected Components** | Canonical Request, Execution Gate, Attestation Service |
| **Severity** | **Critical** — The executed action would differ from what was authorized, with potentially catastrophic consequences. |
| **Impact** | Financial loss, data corruption, unauthorized access, and complete loss of decision traceability integrity. |

**RIO Mitigation:**

1. **Canonical hash.** The canonical request is hashed (SHA-256 of minified, sorted JSON) at formation time. This hash is included in the risk evaluation, authorization, and execution records. Any modification to the request changes the hash.
2. **Authorization parameter binding.** The authorization record's signature covers the `signed_fields_hash`, which includes the canonical request hash. The execution gate MUST recompute the hash of the presented request and compare it against the hash in the authorization record.
3. **Authorization match flag.** The execution record includes an `authorization_match` boolean and `deviation_details` array. The execution service MUST compare every parameter of the action being performed against the authorized parameters.
4. **Attestation integrity checks.** The attestation service independently hashes all records and verifies that the `request_hash` in the attestation matches the actual canonical request content.

**Residual Risk:** If the hash algorithm (SHA-256) is compromised, collision attacks become theoretically possible. SHA-256 is currently considered secure against collision attacks for the foreseeable future.

**References:** Spec 03 (Canonical Request), Spec 07 (Execution), Spec 08 (Attestation), `canonical_request.json`, `execution_record.json` (authorization_match field)

---

### T-04: Expired Authorization Reuse

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-04 |
| **Threat Name** | Expired Authorization Reuse |
| **Description** | An attacker attempts to use an authorization record after its time-bound window has expired — for example, using a 5-minute authorization 30 minutes after it was granted. |
| **Attack Vector** | Delayed submission of a captured authorization, or exploitation of clock skew between the authorization service and execution gate. |
| **Affected Components** | Execution Gate, Authorization Service |
| **Severity** | **High** — An expired authorization may no longer reflect current risk conditions, policy state, or authorizer intent. |
| **Impact** | Execution of an action under stale authorization, potentially after conditions have changed (e.g., account balance, policy update, risk reassessment). |

**RIO Mitigation:**

1. **Mandatory `expires_at` field.** Every authorization record with a decision of `approve` or `approve_with_conditions` MUST include an `expires_at` timestamp. The execution gate MUST reject any authorization where the current time exceeds `expires_at`.
2. **Time skew allowance.** The system manifest defines `time_skew_allowance_seconds: 300`. All timestamp comparisons MUST account for this allowance, but MUST NOT accept timestamps that exceed the allowance.
3. **Fail-closed enforcement.** If the execution gate cannot determine the current time with confidence (e.g., NTP failure), it MUST reject the authorization rather than proceed.
4. **Attestation timestamp ordering.** The attestation service verifies that all timestamps in the chain are chronologically ordered: `requested_at` < `evaluated_at` < `authorized_at` < `executed_at` < `attested_at`.

**Residual Risk:** Clock manipulation (see T-10) could theoretically extend the window. NTP authentication and multiple time sources mitigate this.

**References:** Spec 06 (Authorization), Spec 07 (Execution), Spec 15 (Time-Bound Authorization), `authorization_record.json` (expires_at field), System Manifest (time_skew_allowance_seconds)

---

### T-05: Direct Execution Bypass

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-05 |
| **Threat Name** | Direct Execution Bypass |
| **Description** | An attacker or compromised AI agent attempts to invoke the execution service directly, bypassing the RIO authorization pipeline entirely — executing an action without a canonical request, risk evaluation, or authorization. |
| **Attack Vector** | Direct API call to the execution service endpoint, exploitation of service discovery to find the execution service's internal address, or compromise of network segmentation. |
| **Affected Components** | Execution Gate, Execution Service, Network Infrastructure |
| **Severity** | **Critical** — Complete bypass of all governance controls. |
| **Impact** | Ungoverned action execution with no risk evaluation, no authorization, no audit trail, and no accountability. |

**RIO Mitigation:**

1. **Execution gate as sole entry point.** The execution service MUST only accept requests from the execution gate. The execution gate MUST only accept requests that include a valid `authorization_id` and a valid execution token.
2. **Service-to-service authentication.** The execution gate authenticates to the execution service using a service-to-service token that is not available to external callers or AI agents.
3. **Execution token requirement.** The execution gate MUST present a valid `execution_token.json` to the execution service. The token includes the `authorization_id`, `request_id`, `nonce`, `scope`, and a cryptographic signature from the authorization service.
4. **Independence protocol.** Spec 11 (Independence) requires that the RIO control plane operates on separate infrastructure from the AI agents it governs. AI agents MUST NOT have network access to the execution service.
5. **Fail-closed default.** If the execution gate cannot verify the authorization, the execution service MUST NOT proceed. The default state is denial.

**Residual Risk:** If the service-to-service token is compromised, direct access becomes possible. Token rotation, short-lived tokens, and mutual TLS reduce this risk.

**References:** Spec 07 (Execution), Spec 11 (Independence), `execution_token.json`, `execution_record.json`

---

### T-06: Ledger Tampering

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-06 |
| **Threat Name** | Ledger Tampering |
| **Description** | An attacker with access to the audit ledger storage attempts to modify, delete, or reorder entries to conceal unauthorized actions or alter the historical record. |
| **Attack Vector** | Database administrator access, storage system compromise, or exploitation of ledger write APIs. |
| **Affected Components** | Audit Ledger, Receipt Storage, Attestation Records |
| **Severity** | **High** — Compromises the integrity of the entire audit trail, undermining regulatory compliance and forensic capability. |
| **Impact** | Loss of audit integrity, inability to detect past unauthorized actions, regulatory non-compliance, and destruction of evidence. |

**RIO Mitigation:**

1. **Hash chain linking.** Each ledger entry includes a `previous_entry_hash` field containing the SHA-256 hash of the preceding entry. Modifying any entry breaks the chain, which is detectable by recomputing hashes from the genesis entry.
2. **Chain hash in attestation.** The attestation record includes a `chain_hash` that binds all records in the decision chain. This hash is independently verifiable.
3. **Append-only storage.** The audit ledger MUST be implemented as an append-only data store. Delete and update operations MUST NOT be supported at the storage layer.
4. **Independent verification.** Auditors (Spec 12: Role Separation) MUST be able to independently recompute all hashes in the ledger and verify the chain integrity without relying on the system that wrote the entries.
5. **Distributed witnesses.** The attestation record supports `multi_party` attestation type, allowing independent witnesses to co-sign the attestation, creating redundant proof that is difficult to tamper with simultaneously.

**Residual Risk:** If an attacker gains write access to the ledger storage and simultaneously compromises all witness copies, tampering could go undetected. Geographic distribution and independent witness infrastructure mitigate this.

**References:** Spec 08 (Attestation), Spec 09 (Audit Ledger), `attestation_record.json` (record_hashes), `receipt.json` (chain_integrity), System Manifest (ledger section)

---

### T-07: Unauthorized Policy Change

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-07 |
| **Threat Name** | Unauthorized Policy Change |
| **Description** | An attacker modifies RIO policies, risk thresholds, or authorization rules without proper authorization — for example, raising the auto-approve threshold from $1,000 to $1,000,000 to bypass human authorization for large transactions. |
| **Attack Vector** | Compromise of the policy engine's configuration store, exploitation of an administrative API, or social engineering of a meta-governor. |
| **Affected Components** | Policy Engine, Meta-Governance Protocol, Risk Evaluation Engine |
| **Severity** | **High** — Policy changes alter the behavior of the entire governance system, potentially disabling critical controls. |
| **Impact** | Systematic bypass of governance controls, allowing high-risk actions to proceed without appropriate authorization. |

**RIO Mitigation:**

1. **Meta-governance protocol.** Spec 13 (Meta-Governance) requires that all changes to RIO's own rules, policies, and configurations MUST go through the same governed action control loop as any other consequential action. Policy changes are themselves subject to risk evaluation and authorization.
2. **Policy change authorization.** The governance model in the system manifest specifies `policy_updates_require_authorization: true`. No policy change can take effect without explicit authorization from a qualified meta-governor.
3. **Policy versioning.** All policy changes MUST be versioned and recorded in the audit ledger, creating a tamper-evident history of every policy modification.
4. **Separation of duties.** The entity that proposes a policy change MUST NOT be the entity that authorizes it (Spec 12: Role Separation).

**Residual Risk:** If a meta-governor is compromised or coerced, unauthorized policy changes could be authorized through the legitimate channel. Multi-party authorization for policy changes and anomaly detection on policy modification patterns mitigate this.

**References:** Spec 05 (Policy Constraints), Spec 13 (Meta-Governance), System Manifest (governance_model)

---

### T-08: Role Collusion

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-08 |
| **Threat Name** | Role Collusion |
| **Description** | Two or more participants in the RIO pipeline collude to approve and execute an action that should have been denied — for example, a risk evaluator deliberately underscoring a request while an authorizer rubber-stamps the approval. |
| **Attack Vector** | Insider threat involving coordination between individuals holding different roles in the same decision chain. |
| **Affected Components** | Risk Evaluation Engine, Authorization Service, Role Separation Protocol |
| **Severity** | **High** — Collusion undermines the separation of duties that is fundamental to the governance model. |
| **Impact** | Unauthorized actions executed with apparent legitimacy, difficult to detect through automated controls alone. |

**RIO Mitigation:**

1. **Role separation enforcement.** Spec 12 (Role Separation) defines strict conflict rules: the requester MUST NOT be the authorizer, the executor MUST NOT be the attestor, and no single entity may hold conflicting roles in the same decision chain.
2. **Independent attestation.** The attestation service operates independently from the risk evaluator and authorizer. It performs its own verification checks, including `hash_integrity`, `signature_verification`, and `policy_compliance`, providing an independent validation layer.
3. **Audit trail completeness.** Every participant's identity and actions are recorded in the decision chain. The receipt includes a `participants` section listing every entity involved, enabling post-hoc collusion detection.
4. **Learning protocol.** Spec 10 (Learning) analyzes patterns across completed decision chains. Statistical anomalies — such as a specific evaluator-authorizer pair consistently approving high-risk requests — can be flagged for investigation.
5. **Multi-party authorization.** For high-risk actions, the authorization record supports `co_authorizers`, requiring multiple independent authorizers to agree.

**Residual Risk:** Sophisticated collusion involving all participants in a chain (evaluator + authorizer + executor + attestor) is extremely difficult to prevent through technical controls alone. Organizational controls (background checks, rotation, monitoring) and the learning protocol's anomaly detection provide defense in depth.

**References:** Spec 12 (Role Separation), Spec 10 (Learning), Spec 08 (Attestation), `authorization_record.json` (co_authorizers), `receipt.json` (participants)

---

### T-09: Execution Outside Authorization Scope

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-09 |
| **Threat Name** | Execution Outside Authorization Scope |
| **Description** | The execution service performs an action that differs from what was authorized — for example, the authorization approves a $48,250 wire transfer but the execution service sends $482,500, or sends the payment to a different account. |
| **Attack Vector** | Compromise of the execution service, bug in parameter mapping, or manipulation of the execution request between the gate and the service. |
| **Affected Components** | Execution Service, Execution Gate, Attestation Service |
| **Severity** | **Critical** — The action performed does not match the authorized action, breaking the governance guarantee. |
| **Impact** | Unauthorized action execution despite a valid authorization existing for a different action. Financial loss, data corruption, or unauthorized access. |

**RIO Mitigation:**

1. **Execution token scope binding.** The `execution_token.json` includes a `scope` object with `action_type`, `target_id`, and `parameter_hash`. The execution service MUST verify that the action it is about to perform matches the scope defined in the token.
2. **Authorization match verification.** The execution record includes an `authorization_match` boolean. The execution service MUST compare the `action_performed.parameters` against the authorized `parameters` and set this flag accordingly. If `authorization_match` is `false`, the `deviation_details` array MUST document every discrepancy.
3. **Attestation cross-check.** The attestation service independently compares the execution record against the canonical request and authorization record. If the executed parameters do not match the authorized parameters, the attestation's `policy_compliance` check fails.
4. **Constraint enforcement.** Authorization constraints (e.g., `amount_cap`, `parameter_override`) are enforced by the execution gate before dispatching to the execution service. The gate MUST reject any execution that would violate a constraint.

**Residual Risk:** If the execution service is fully compromised and can fabricate both the action and the execution record, the mismatch may not be detected until the attestation service performs its independent verification. Real-time monitoring of execution outputs against authorized parameters provides additional detection.

**References:** Spec 07 (Execution), `execution_token.json` (scope), `execution_record.json` (authorization_match, deviation_details), `authorization_record.json` (conditions)

---

### T-10: Time Skew Attack

| Attribute | Detail |
|-----------|--------|
| **Threat ID** | T-10 |
| **Threat Name** | Time Skew Attack |
| **Description** | An attacker manipulates system clocks on one or more RIO components to extend authorization windows, forge timestamps, or disrupt timestamp ordering validation. For example, setting the execution gate's clock back by 30 minutes to accept an expired authorization. |
| **Attack Vector** | NTP poisoning, compromise of the time source, or direct clock manipulation on a compromised host. |
| **Affected Components** | All components that generate or validate timestamps: Authorization Service, Execution Gate, Attestation Service, Audit Ledger |
| **Severity** | **High** — Clock manipulation can undermine time-bound authorization, timestamp ordering, and expiration enforcement. |
| **Impact** | Expired authorizations accepted, timestamp ordering violations undetected, and audit trail chronology corrupted. |

**RIO Mitigation:**

1. **Time skew allowance.** The system manifest defines `time_skew_allowance_seconds: 300`. All timestamp comparisons MUST account for this allowance, but MUST NOT accept timestamps that exceed the allowance.
2. **Timestamp ordering validation.** The attestation service performs a `timestamp_ordering` check, verifying that `requested_at` < `evaluated_at` < `authorized_at` < `executed_at` < `attested_at`. Violations indicate clock manipulation or record tampering.
3. **NTP authentication.** RIO components SHOULD use authenticated NTP (NTS — Network Time Security, RFC 8915) to prevent NTP poisoning attacks.
4. **Multiple time sources.** Critical components SHOULD cross-reference multiple independent time sources. If time sources disagree by more than the skew allowance, the component MUST fail closed.
5. **Relative time validation.** In addition to absolute timestamp checks, the execution gate SHOULD validate that the elapsed time between `authorized_at` and the current time is reasonable (e.g., not negative, not exceeding the authorization window plus skew allowance).

**Residual Risk:** If an attacker controls all time sources available to a component, clock manipulation becomes undetectable by that component. Hardware security modules with independent clocks and cross-component timestamp comparison provide additional defense.

**References:** Spec 15 (Time-Bound Authorization), Spec 08 (Attestation, timestamp_ordering check), System Manifest (time_skew_allowance_seconds), RFC 8915 (Network Time Security)

---

## 5. Threat Summary Matrix

| Threat ID | Threat Name | Severity | Likelihood | Primary Mitigation |
|-----------|-------------|----------|------------|-------------------|
| T-01 | Replay Attack | Critical | Medium | Single-use nonces + Nonce Registry |
| T-02 | Forged Signature | Critical | Low | ECDSA-secp256k1 + signature verification at every boundary |
| T-03 | Tampered Payload | Critical | Medium | Canonical hash + authorization parameter binding |
| T-04 | Expired Authorization Reuse | High | Medium | Mandatory expires_at + execution gate time check |
| T-05 | Direct Execution Bypass | Critical | Medium | Execution gate as sole entry point + service-to-service auth |
| T-06 | Ledger Tampering | High | Low | Hash chain linking + append-only storage |
| T-07 | Unauthorized Policy Change | High | Low | Meta-governance protocol + policy change authorization |
| T-08 | Role Collusion | High | Low | Role separation + independent attestation + anomaly detection |
| T-09 | Execution Outside Authorization Scope | Critical | Medium | Execution token scope binding + authorization match verification |
| T-10 | Time Skew Attack | High | Low | Time skew allowance + NTP authentication + timestamp ordering |

---

## 6. Mitigations Summary

The following table consolidates all mitigations referenced across the threat catalog, organized by the defense layer they provide:

| Defense Layer | Mitigation | Threats Addressed |
|--------------|-----------|-------------------|
| **Cryptographic Integrity** | ECDSA-secp256k1 signatures on all records | T-02, T-03, T-06, T-09 |
| **Cryptographic Integrity** | SHA-256 canonical hashing of all records | T-03, T-06 |
| **Cryptographic Integrity** | Signed fields hash binding signatures to specific data | T-02, T-03 |
| **Replay Prevention** | Single-use nonces with persistent Nonce Registry | T-01 |
| **Time-Bound Controls** | Mandatory `expires_at` on authorization records | T-01, T-04 |
| **Time-Bound Controls** | Time skew allowance (300 seconds) | T-04, T-10 |
| **Time-Bound Controls** | Timestamp ordering validation in attestation | T-04, T-10 |
| **Access Control** | Execution gate as sole entry point to execution service | T-05 |
| **Access Control** | Service-to-service authentication tokens | T-05 |
| **Access Control** | Network isolation of execution service from AI agents | T-05 |
| **Scope Enforcement** | Execution token scope binding (action_type, target_id, parameter_hash) | T-09 |
| **Scope Enforcement** | Authorization match verification with deviation details | T-03, T-09 |
| **Audit Integrity** | Hash chain linking (previous_hash + current_hash) | T-06 |
| **Audit Integrity** | Append-only ledger storage with no update/delete operations | T-06 |
| **Audit Integrity** | Independent attestation with multi-party signatures | T-06, T-08 |
| **Governance Controls** | Role separation enforcement (no self-authorization) | T-08 |
| **Governance Controls** | Meta-governance protocol for policy changes | T-07 |
| **Governance Controls** | Independent attestation service on separate infrastructure | T-08 |
| **Monitoring** | Anomaly detection via Learning Protocol | T-08, T-09 |
| **Infrastructure** | NTP authentication (NTS, RFC 8915) | T-10 |
| **Infrastructure** | Multiple independent time sources | T-10 |
| **Infrastructure** | Hardware security modules for key storage | T-02 |

---

## 7. Assumptions

The threat model is based on the following assumptions. If any assumption is violated, the corresponding threats may not be fully mitigated:

1. **Cryptographic algorithm security.** SHA-256 and ECDSA-secp256k1 remain computationally secure against collision, preimage, and forgery attacks for the deployment lifetime of the system.

2. **Key management integrity.** Private keys used for signing authorization records, attestation records, and service-to-service tokens are stored securely (preferably in HSMs) and are not compromised. Key compromise is addressed as a residual risk in T-02.

3. **Infrastructure isolation.** The RIO control plane components operate on infrastructure that is logically and (where possible) physically separated from the AI agents and automated systems they govern. Network segmentation is correctly configured and maintained.

4. **Clock reliability.** System clocks on RIO components are synchronized to within the `time_skew_allowance_seconds` (300 seconds) using authenticated time sources. Clock manipulation is addressed in T-10.

5. **Honest majority of roles.** At least the attestation service and audit ledger are operated by entities that are independent of the requester, authorizer, and executor. If all roles are controlled by a single entity, the governance model provides no additional security.

6. **Append-only storage integrity.** The underlying storage for the audit ledger enforces append-only semantics at the infrastructure level. If the storage layer allows arbitrary writes, ledger integrity (T-06) depends solely on hash chain verification.

7. **Correct implementation.** The RIO components correctly implement the protocol specifications. Implementation bugs could introduce vulnerabilities not covered by this threat model. The Verification Test Suite (spec/verification_tests.md) provides a baseline for validating implementation correctness.

8. **Authenticated communication channels.** All communication between RIO components uses TLS 1.3 (or equivalent) with mutual authentication. Man-in-the-middle attacks on inter-component communication are outside the threat model if this assumption holds.

---

## 8. Security Boundaries

The RIO Protocol defines three security boundaries that determine trust levels and enforcement points:

### Boundary 1: External → RIO Intake

This is the outermost boundary where action requests enter the RIO system from AI agents, automated systems, or human-initiated workflows.

| Property | Detail |
|----------|--------|
| **Enforcement Point** | Intake Service + Origin Verification Service |
| **Trust Level** | Untrusted — all incoming requests are treated as potentially malicious |
| **Controls** | Origin signature verification, request schema validation, rate limiting |
| **Threats Addressed** | T-02 (forged signatures at intake), T-03 (malformed payloads) |

### Boundary 2: Authorization → Execution Gate

This is the critical control boundary where authorized decisions are presented for execution. This boundary enforces the core governance guarantee: no action without valid authorization.

| Property | Detail |
|----------|--------|
| **Enforcement Point** | Execution Gate |
| **Trust Level** | Conditionally trusted — authorization records are accepted only after full cryptographic verification |
| **Controls** | Signature verification, nonce validation, expiration check, scope matching, hash integrity, execution token issuance |
| **Threats Addressed** | T-01 (replay), T-02 (forged signature), T-03 (tampered payload), T-04 (expired authorization), T-05 (direct bypass), T-09 (scope violation), T-10 (time skew) |

### Boundary 3: Execution → Audit Trail

This is the post-execution boundary where the system produces cryptographic proof of what happened and records it in the tamper-evident ledger.

| Property | Detail |
|----------|--------|
| **Enforcement Point** | Attestation Service + Audit Ledger |
| **Trust Level** | Independently verified — the attestation service operates on separate infrastructure and independently verifies all prior records |
| **Controls** | Independent hash recomputation, multi-party signatures, hash chain linking, append-only storage |
| **Threats Addressed** | T-06 (ledger tampering), T-08 (role collusion detection) |

### Cross-Boundary Principle

No entity that operates within one security boundary should have privileged access to another boundary's enforcement mechanisms. Specifically:

- AI agents (Boundary 1) MUST NOT have access to the execution service (Boundary 2).
- The execution service (Boundary 2) MUST NOT have write access to the audit ledger (Boundary 3).
- The attestation service (Boundary 3) MUST NOT have the ability to modify authorization records (Boundary 2).

This cross-boundary isolation ensures that compromise of any single component does not cascade into a full system compromise.

---

## 9. Recommendations

### For Implementers

1. **Fail closed by default.** Every component MUST deny action execution when it cannot verify a required condition. The system manifest's `fail_closed: true` setting is not optional — it is a fundamental security property.

2. **Use hardware security modules.** Private keys for authorization signing, attestation signing, and service-to-service authentication SHOULD be stored in HSMs or equivalent hardware-backed key stores.

3. **Implement defense in depth.** No single mitigation is sufficient. Each threat is addressed by multiple overlapping controls. Implementers MUST NOT remove or weaken any layer under the assumption that another layer provides adequate protection.

4. **Monitor for anomalies.** The Learning Protocol (Spec 10) SHOULD be configured to detect statistical anomalies in decision chains: unusual approval rates, repeated evaluator-authorizer pairings, timestamp clustering, and deviation patterns.

5. **Rotate keys and credentials.** Signing keys, service-to-service tokens, and NTP authentication credentials SHOULD be rotated on a regular schedule and immediately upon suspected compromise.

### For Auditors

1. **Verify the hash chain.** Recompute all hashes in the audit ledger from the genesis entry and verify that each `previous_entry_hash` matches. Any break in the chain indicates tampering.

2. **Verify signatures independently.** Obtain public keys from the key registry (not from the records themselves) and independently verify all signatures in the authorization, execution, and attestation records.

3. **Check timestamp ordering.** Verify that all timestamps in every decision chain are chronologically ordered and that no authorization was used after its `expires_at` time.

4. **Review role assignments.** Verify that no entity held conflicting roles in the same decision chain (e.g., requester and authorizer, executor and attestor).

5. **Sample and deep-inspect.** Select a random sample of decision chains and verify every field, hash, signature, and timestamp from canonical request through ledger entry. The protocol is designed to make this verification deterministic and repeatable.


---

## Protocol Threat-to-Control Mapping

The following table maps core protocol threats to the specific Governed Execution Protocol stages, invariants, and controls that mitigate them. This mapping complements the threat analysis above by linking each threat directly to the 8-step runtime protocol and the protocol invariant framework defined in `/spec/protocol_invariants.md`.

| Threat | Description | Mitigating Protocol Stage | Invariants | Notes |
|--------|-------------|---------------------------|------------|-------|
| Unauthorized Execution | An action executes without valid authorization from a qualified authority | Authorization (Step 5), Execution Gate (Step 6) | INV-01, INV-06 | The Execution Gate re-verifies the authorization token's signature, expiration, single-use status, and intent binding before releasing any action. No execution proceeds without a valid, unexpired, unspent authorization token. |
| Token Reuse / Replay Attack | A previously consumed authorization token is presented a second time to authorize a new execution | Authorization token design (single-use flag), Execution Gate validation (Step 6) | INV-07 | Authorization tokens are marked single-use by default. The Execution Gate checks the nonce registry before accepting any token. A consumed nonce is permanently recorded and cannot be reused. |
| Ledger Tampering | An attacker modifies, deletes, or reorders entries in the audit ledger to conceal or alter the decision history | Append-only Audit Ledger (Step 8), Hash chain receipts (Step 7) | INV-04 | Each ledger entry contains a SHA-256 hash of the previous entry, forming a tamper-evident chain. Any modification to a prior entry breaks all subsequent hashes. The ledger permits append operations only — no update, delete, or reorder. |
| AI Self-Authorization | An AI agent generates a request and also approves its own request, bypassing human or independent oversight | Separation of requester and authorizer identity at Authorization (Step 5) | INV-06 | The protocol enforces that the `approver_id` on any authorization token must differ from the `actor_id` on the canonical intent. No entity may authorize its own request. This is structurally enforced, not policy-dependent. |
| Privilege Escalation | An entity with limited permissions obtains or forges credentials to perform actions beyond its authorized scope | Identity verification at Intake (Step 1), Policy & Risk Check (Step 4), Authorization (Step 5) | INV-01, INV-06 | Intake verifies actor identity. Policy evaluation checks whether the verified actor is permitted to request the specific action type and target resource. Authorization requires a qualified approver with appropriate authority for the risk level. All three checks must pass independently. |
| Kill Switch Bypass | An attacker or misconfigured system continues executing actions after the global kill switch has been engaged | EKS-0 Kill Switch enforced at Authorization (Step 5) and Execution Gate (Step 6) | INV-08 | When the kill switch is engaged, the Execution Gate blocks all new executions regardless of existing authorization tokens. The kill switch state is checked before every execution release. Kill switch engagement and all blocked requests are recorded in the audit ledger. |
| Missing Audit Trail | An action executes but no receipt or ledger entry is generated, leaving a gap in the decision history | Receipt generation (Step 7), Audit Ledger (Step 8) | INV-02, INV-03 | Every request — whether approved, denied, or blocked — must produce a signed receipt and a corresponding ledger entry. The protocol treats a missing receipt or ledger entry as a system integrity failure. There are no silent failures and no unrecorded decisions. |

---

## Security Model Summary

The RIO security model is constructed from six reinforcing structural controls. These controls are not policy preferences — they are architectural properties enforced by the protocol runtime.

**Separation of decision and execution.** The entity that requests an action is structurally separated from the entity that authorizes it and the component that executes it. No single entity can propose, approve, and carry out an action. This separation is enforced by identity verification at Intake (Step 1), distinct role requirements at Authorization (Step 5), and independent validation at the Execution Gate (Step 6).

**Single-use authorization tokens.** Every authorization token is bound to a specific canonical intent by `intent_id`, carries an expiration timestamp, and is flagged as single-use. The Execution Gate consumes the token upon first use and records the nonce. A consumed token cannot authorize a second execution. This eliminates replay attacks and token reuse at the protocol level.

**Append-only ledger with hash chaining.** The audit ledger accepts only append operations. Each entry contains a SHA-256 hash of the previous entry, creating a tamper-evident chain from the genesis entry forward. Any modification to a historical entry breaks all subsequent hashes and is immediately detectable by any auditor who recomputes the chain.

**Mandatory receipts for all decisions.** Every request that enters the protocol — regardless of whether it is approved, denied, escalated, or blocked by the kill switch — produces a cryptographically signed receipt. The receipt links the canonical intent, authorization decision, and execution result into a single verifiable record. No decision passes through the protocol without generating a receipt.

**Global kill switch override.** The EKS-0 Kill Switch provides a system-wide emergency halt that overrides all normal authorization and execution behavior. When engaged, no new executions proceed. The kill switch is checked at both the Authorization stage and the Execution Gate, ensuring that even pre-authorized actions cannot execute during a halt. All kill switch events are themselves recorded in the audit ledger.

**Governance learning separated from runtime execution.** The learning loop (Step 9) operates asynchronously on historical decision data stored in the Governed Corpus. It proposes updates to risk models and policies, but those updates must themselves pass through the governed change process before taking effect in the runtime. The learning loop cannot bypass, override, or weaken runtime controls.
