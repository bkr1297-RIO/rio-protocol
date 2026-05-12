# ONE/RIO/MUSS Conformance Declaration

**Version:** v0.1
**Status:** external_facing_draft
**Type:** conformance_specification
**Parent Architecture:** ONE / RIO / MUSS
**Parent Document:** Non-Sovereignty Invariants and Sovereignty Preservation Stack v0.3
**Companion Doctrine:** Integrity Phase — MUST NOT / CANNOT / DID NOT
**Audience:** regulators, auditors, investors, academic peers, federation partners, and technical AI safety reviewers

## Public Summary

A compliant ONE/RIO/MUSS system is defined not by what it can do, but by what it must not permit, what must fail closed when attempted, and what receipt or verification artifact shows the boundary held.

## Core Law

Receipts may generate learning. Only authority may generate permission.

## Discipline

Three-legged grammar:

1. **MUST NOT** — the constitutional rule
2. **CANNOT** — the structural block inside a conformant implementation
3. **DID NOT** — the receipt, ledger, test, or verifier evidence showing what happened

---

## 0. What This Document Is

This Conformance Declaration is the external-facing conformance artifact for the ONE/RIO/MUSS architecture. It does not introduce new principles. It restates the constitutional invariants of v0.3 in conformance form by separating the rule, the structural block, and the receipted evidence.

It exists because the practical gap in AI governance is no longer only policy language. As AI systems move from generating answers to coordinating tools, agents, and actions, safety claims require operational evidence. If the only evidence for a governance claim is a policy statement, the claim remains unverified.

ONE/RIO/MUSS treats conformance as a three-part discipline:

- what the system **MUST NOT** permit, as constitutional grammar;
- what the system **CANNOT** do within a conformant implementation, because the violating path is structurally blocked, gated, or separated;
- what **DID NOT** occur, as shown by receipts, ledgers, test results, verifier outputs, or other reviewable evidence.

This document expresses each load-bearing safety claim in all three forms. Where an implementation is incomplete, untested, or not yet connected to live traces, that status must be named explicitly.

Conformance is not a promise of perfection. It is the discipline of refusing to claim more than the structure and evidence can support.

---

## 1. Conformance Grammar

### 1.1 Definitions

**MUST NOT** is the constitutional or protocol-level rule. It states what the system is prohibited from permitting, regardless of context, optimization pressure, or operational convenience. MUST NOT rules derive from the Non-Sovereignty Invariants (v0.3) and are not subject to override by any automated component.

**CANNOT** is the structural block inside a conformant implementation. It means the violating path is architecturally unavailable — the component that would need to act does not have the interface, the credential, the routing path, or the structural access to perform the prohibited action. CANNOT does not mean metaphysical impossibility. It means that within a conformant implementation, the architecture prevents the violation through separation of function, gating, credential isolation, or structural absence of the required path.

**DID NOT** is the evidentiary layer. It is the receipt, ledger entry, test result, verifier output, or other reviewable artifact that shows what happened at a specific boundary during a specific event. DID NOT evidence includes: boundaries that held (the system correctly blocked or held an action), actions that were blocked (an unauthorized action was prevented), attempts that were surfaced (a boundary-crossing attempt was detected and recorded), violations that were recorded (a conformance failure was captured), and receipts that were issued (a conformance receipt was generated proving the check occurred).

### 1.2 All Three Are Required

A mature conformance claim requires all three legs. A MUST NOT rule without a structural block is a policy aspiration. A structural block without DID NOT evidence is an unverified implementation claim. DID NOT evidence without a MUST NOT rule is an observation without a standard.

The relationship is directional:

> MUST NOT (protocol rule) → implemented as → CANNOT (structural block) → evidenced by → DID NOT (runtime proof)

### 1.3 Claim Maturity

Not every invariant in this declaration has reached full three-legged maturity. Where the structural block exists but live DID NOT evidence has not yet been produced from a running system, this is stated explicitly. Where the structural block is designed but not yet implemented, that is also stated. The declaration does not hide incomplete legs.

Not all conformance claims are evidenced in the same way. Some are enforced at runtime, some by structural separation, some by schema design, and some by documentation discipline or planned test coverage. This declaration names the enforcement mode for each claim so reviewers can distinguish live-tested controls from design-time invariants.

---

## 2. Component Ownership Map

The ONE/RIO/MUSS architecture distributes governance across structurally separated components. No single component holds both the authority to act and the authority to certify that the action was correct.

| Component | Role | Responsibility |
|-----------|------|---------------|
| Human | Authority source | Commits intent, grants approval, determines accountability. The only source of permission in the system. |
| Scribe / Bondi | Meaning and language structuring | Clarifies human intent into structured form. Resolves ambiguity before the system acts. Does not grant authority. |
| UGIP | Authority packet / valid movement grammar | Packages human authority into a structured, schema-validated grant. Defines what constitutes a well-formed authority expression. |
| RIO | Admissibility and consequence governance | Evaluates whether an action is admissible under current policy. Gates consequence. Does not execute. |
| Sentinel | Capability and fidelity gate | Verifies that a component operates within its declared capability boundary. Enforces structural fidelity. Does not grant authority. |
| Bounded Actor | Governed action execution | Executes governed actions through the controlled gateway. Acts only under valid, unexpired authorization. Does not produce its own proof. Also referred to as the execution adapter. |
| MUS | Proof and receipt production | Produces cryptographically signed receipts binding intent to outcome. Contains the Receipt Notary as its notarial function. Structurally separate from the bounded actor. |
| Ledger / Chronicle | Durable proof history | Maintains the append-only, hash-chained record of all receipts. Cannot be modified after append. |
| MANTIS | Observation and receipt-reading learning | Reads from Chronicle. Surfaces patterns, risk signals, and policy recommendations. Advisory only. Cannot write policy. Cannot grant authority. |
| Convergence | Drift and rubber-stamp brake | Monitors approval patterns for signs of governance erosion. Applies friction when drift is detected. |

### Keeper Distinction

The bounded actor acts. RIO governs. Sentinel enforces. MUS proves. Chronicle preserves. MANTIS learns. Human authority decides.

The separation is structural, not procedural. In a conformant implementation, the bounded actor cannot access MUS's signing key. MANTIS cannot write to the policy store. The Convergence monitor cannot approve actions. These are not policy choices — they are architectural separations.

---

## 3. Must-Never Invariant Matrix

The invariants below are organized into ten groups. Each group represents a category of boundary that a conformant system must maintain. The groups are derived from the Non-Sovereignty Invariants (v0.3).

---

### 3.1 Authority Must Not Self-Generate

**Enforcement Mode:** runtime-gated, structural-separation, receipt-verifiable

**Claim:** No component in the system may generate its own authority. All permission originates from human governance.

**MUST NOT:** The system must not permit any automated component to create, extend, or escalate its own authorization without human approval.

**Structural Block:** Authorization tokens are issued only through the approval gate, which requires a human-bound authorization record or cryptographic signature where implemented. The token issuance function is not accessible to the bounded actor, MANTIS, or any execution component. RIO evaluates admissibility but does not issue tokens.

**Failure Test (CF-006):** An action reaches the execution gate without a valid authorization token (missing, expired, or already burned). The execution gate validates the token. Expected verdict: BLOCK.

**Evidence:** Token validation receipt with token_status field showing the validation result. For a held boundary: token_id, burn_timestamp, and issuer_id present. For a blocked attempt: token_status=missing|expired|burned, no execution receipt generated.

**Claim Boundary:** This does not prove that the human approval was informed or correct. It proves that no execution occurred without a token traceable to a human approval event.

---

### 3.2 Capability Must Not Become Permission

**Enforcement Mode:** runtime-gated, structural-separation, receipt-verifiable

**Claim:** The ability to perform an action does not constitute authorization to perform it. Capability and permission are structurally separated.

**MUST NOT:** The system must not permit a component to execute an action solely because it has the technical capability to do so. Capability without a valid authority grant is insufficient.

**Structural Block:** Sentinel verifies that a component operates within its declared capability manifest. The execution gate requires both a valid capability check and a valid authorization token. A component that has the capability to SEND but only the authority to DRAFT is blocked at the execution gate.

**Failure Test (CF-005):** The bounded actor has capability to DRAFT a message but not to SEND it. The bounded actor attempts to send directly. Expected verdict: BLOCK.

**Evidence:** Boundary enforcement receipt with capability_exceeded=true, declared_capability=DRAFT, attempted_capability=SEND. No send-side-effect produced.

**Claim Boundary:** This does not prove that capability manifests are complete or that all possible capability violations are enumerated. It proves that the gate checks capability against manifest before permitting execution.

---

### 3.3 Learning Must Not Become Authorization

**Enforcement Mode:** structural-separation, runtime-gated where implemented, receipt-verifiable

**Claim:** Observational learning from receipts and patterns does not generate permission. Learning is advisory. Only human governance may amend policy or grant authority.

**MUST NOT:** The system must not permit MANTIS or any learning component to write policy changes, issue authorization tokens, or modify approval thresholds without human governance approval.

**Structural Block:** MANTIS reads only from Chronicle (the append-only ledger). MANTIS has no write access to the policy store, the token issuance function, or the approval gate. Policy amendments require a governance amendment receipt signed by human authority.

**Failure Test (CF-011):** MANTIS attempts to (a) ingest raw data not sourced from Chronicle, or (b) write back a policy change directly without governance approval. Expected verdict: BLOCK.

**Evidence:** BLOCK receipt with raw_intake_attempt=true or authority_writeback_attempt=true. No policy change recorded. No raw data ingested.

**Claim Boundary:** This does not prove that MANTIS recommendations are correct or that human governance always acts on them wisely. It proves that the path from learning to policy change requires a human governance step.

---

### 3.4 Proof Must Not Become Meaning

**Enforcement Mode:** schema-enforced, documentation-discipline

**Claim:** Receipts prove that events occurred and that boundaries held. They do not prove that the action was wise, correct, or beneficial. Proof and meaning are separate.

**MUST NOT:** The system must not permit a receipt or conformance artifact to be treated as evidence that the governed action achieved its intended real-world outcome, that the human's intent was correctly understood, or that the action was the right one to take.

**Structural Block:** Receipts record what the system did, not what the world experienced. Receipt and conformance schemas record system events and execution evidence; they must not claim real-world outcome verification unless external attestation exists. External attestation is a separate concern not covered by the receipt protocol.

**Failure Test:** No automated test can verify meaning. This invariant is enforced by documentation discipline and schema design, not by a runtime gate.

**Evidence:** Receipt schema review showing no field that claims real-world outcome verification. Documentation review showing explicit limitation statements.

**Claim Boundary:** This is a design-level invariant, not a runtime-testable gate. It is enforced through schema discipline and documentation, not through a blocking mechanism.

---

### 3.5 The Actor Must Not Self-Certify

**Enforcement Mode:** structural-separation, runtime-gated, receipt-verifiable, ledger-verifiable

**Claim:** The component that executes an action must not be the component that certifies the action occurred correctly. Execution and proof are structurally separated.

**MUST NOT:** The system must not permit the bounded actor (or any execution component) to generate, sign, or issue its own receipt for an action it performed.

**Structural Block:** MUS, through its Receipt Notary function, holds the signing key for receipt production. This key is not accessible to the bounded actor. Receipt generation requires notary_id != actor_id. Self-receipt attempts are rejected. The bounded actor does not produce its own proof.

**Failure Test (CF-007):** The bounded actor attempts to generate its own receipt for an action it executed, bypassing MUS. Receipt generation request where signer_id == actor_id. Expected verdict: BLOCK.

**Evidence:** BLOCK receipt with self_certification_attempt=true. No self-signed receipt accepted into the ledger. MUS receipt with notary_id confirmed different from actor_id.

**Claim Boundary:** This does not prove that MUS is incorruptible. It proves that the execution path (bounded actor) and the certification path (MUS / Receipt Notary) are structurally separated in a conformant implementation.

---

### 3.6 Witnessing Must Not Become Judging or Acting

**Enforcement Mode:** structural-separation, receipt-verifiable

**Claim:** Components that observe, record, or learn from system behavior must not use that position to judge, approve, or execute actions. Observation is passive.

**MUST NOT:** The system must not permit MANTIS, Chronicle, or the Convergence monitor to approve actions, issue tokens, or execute governed operations. Their role is to observe, record, surface, and brake — not to decide or act.

**Structural Block:** MANTIS has read-only access to Chronicle. Chronicle accepts append-only writes from MUS (via its Receipt Notary function). The Convergence monitor can trigger a brake (increased friction) but cannot approve, reject, or execute. None of these components have access to the token issuance function or the execution gateway.

**Failure Test:** MANTIS attempts to issue an approval. Expected verdict: BLOCK — MANTIS has no interface to the approval function.

**Evidence:** Architectural review showing no approval or execution interface exposed to observer components. If attempted through an unexpected path, BLOCK receipt with unauthorized_role=observer.

**Claim Boundary:** This does not prove that observer components cannot be compromised at the infrastructure level. It proves that in a conformant implementation, the interfaces required for judging or acting are not available to observer components.

---

### 3.7 Overrides Must Not Bypass the Grammar

**Enforcement Mode:** runtime-gated, receipt-verifiable, ledger-verifiable

**Claim:** No override, emergency mode, or administrative action may bypass the three-legged conformance grammar. Overrides are governed actions, subject to the same receipt and approval requirements.

**MUST NOT:** The system must not permit an administrative override that executes without authorization, without a receipt, or without a ledger entry. There is no "god mode" that operates outside governance.

**Structural Block:** Override actions are routed through the same governance pipeline as standard actions. The execution gate does not distinguish between override and standard requests — both require a valid token. Emergency modes may reduce latency but must not remove the receipt boundary.

**Failure Test:** An administrative user attempts to execute a high-risk action by invoking an override flag that bypasses the approval gate. Expected verdict: BLOCK — the override flag is not recognized by the execution gate.

**Evidence:** BLOCK receipt with override_bypass_attempt=true. No execution without token. Override action, if approved through governance, produces a standard receipt with override_reason field.

**Claim Boundary:** This does not prove that all possible override paths have been enumerated. It proves that the known execution path requires a token regardless of the caller's administrative status.

---

### 3.8 Contribution Must Not Become Surrender

**Enforcement Mode:** planned / not-yet-live-tested, schema-enforced

**Maturity:** Design invariant. Not yet live-tested.

**Claim:** When a human contributes data, intent, or feedback to the system, that contribution does not transfer ownership or sovereignty over the contributed material. The human retains authority.

**MUST NOT:** The system must not permit contributed data to be used in ways that exceed the scope of the original contribution grant. Contribution is scoped, not blanket.

**Structural Block:** Contribution grants are schema-validated authority packets with explicit scope fields. The system records the scope of each contribution in the authority grant receipt. Processing that exceeds the declared scope is a conformance violation.

**Failure Test:** A component attempts to use contributed data for a purpose not included in the original contribution scope. Expected verdict: BLOCK at the admissibility gate.

**Evidence:** Authority grant receipt with scope fields. BLOCK receipt if scope exceeded, with scope_violation=true and original_scope vs. attempted_scope.

**Claim Boundary:** This does not prove that scope definitions are always precise or that all possible misuses are anticipated. It proves that contribution scope is recorded and checked at the admissibility gate.

---

### 3.9 Retrieval Must Not Become Training

**Enforcement Mode:** planned / not-yet-live-tested, structural-separation where implemented

**Maturity:** Design invariant. Not yet live-tested.

**Claim:** Retrieving data for operational use does not authorize using that data for model training, fine-tuning, or learning corpus construction. Retrieval and training are separate authority grants.

**MUST NOT:** The system must not permit data retrieved for operational purposes to be routed to training pipelines without a separate, explicit authority grant.

**Structural Block:** MANTIS reads from Chronicle for observational learning (pattern detection, risk surfacing). This is structurally distinct from training-corpus construction. Training-corpus construction requires a separate authority grant with explicit scope. The learning gate blocks raw data intake that does not originate from Chronicle.

**Failure Test (CF-011, variant):** A training pipeline attempts to ingest operational data directly, bypassing the Chronicle-sourced learning path. Expected verdict: BLOCK at the learning gate.

**Evidence:** BLOCK receipt with raw_intake_attempt=true, source != chronicle. No training data ingested from operational retrieval path.

**Claim Boundary:** This does not prove that all data flows are perfectly isolated at the infrastructure level. It proves that the conformant architecture requires separate authority grants for retrieval and training, and that the learning gate enforces source validation.

---

### 3.10 Shared State Must Not Become Ownership

**Enforcement Mode:** planned / not-yet-live-tested, schema-enforced

**Maturity:** Design invariant. Not yet live-tested.

**Claim:** When multiple parties share state through the system (e.g., shared workspaces, collaborative documents, multi-party governance), no single party acquires ownership of the shared state by virtue of having access to it.

**MUST NOT:** The system must not permit a single party to unilaterally modify, delete, or restrict access to shared state without governance approval from all parties with standing.

**Structural Block:** Shared state modifications are governed actions requiring multi-party approval when the state is marked as shared. The approval gate requires signatures from all parties with declared standing. Unilateral modification of shared state is blocked.

**Failure Test:** A single party attempts to delete shared state without approval from other parties with standing. Expected verdict: BLOCK — multi-party approval required.

**Evidence:** BLOCK receipt with unilateral_modification_attempt=true, required_approvers vs. actual_approvers. Shared state unchanged.

**Claim Boundary:** This does not prove that all shared-state scenarios are anticipated or that standing is always correctly assigned. It proves that the governance pipeline treats shared-state modifications as multi-party governed actions.

---

## 4. Conformance Test Summary

The following table maps each invariant group to its primary failure test. Full test specifications, including setup conditions, expected verdicts, and receipt field requirements, are maintained in the companion document `conformance-failure-tests-v0.1.md`.

| Test ID | Invariant Group | Boundary Tested | Expected Verdict |
|---------|----------------|-----------------|-----------------|
| CF-001 | Meaning confirmation | Intent formation | HOLD |
| CF-002 | Structured authority | Authority verification | BLOCK |
| CF-003 | Default HOLD | Approval gate | HOLD |
| CF-004 | Consequence classification | Risk evaluation | BLOCK |
| CF-005 | Capability boundary | Execution gate | BLOCK |
| CF-006 | Authority self-generation | Execution gate | BLOCK |
| CF-007 | Self-certification | Receipt generation | BLOCK |
| CF-008 | Memory preservation | Ledger append | BLOCK |
| CF-009 | Conformance verification | Conformance verification | BLOCK |
| CF-010 | Accountability review | Accountability determination | BLOCK |
| CF-011 | Learning boundary | Learning gate | BLOCK |
| CF-012 | Drift brake | Convergence monitoring | ESCALATE |

---

## 5. Evidence and Verification Path

An external party seeking to verify conformance claims would follow this path:

### 5.1 Receipt Signature Verification

Each receipt is signed using Ed25519. The verifier obtains MUS's public signing key (the Receipt Notary key) and verifies the signature over the canonicalized receipt body. The canonicalization algorithm (recursive sorted-key JSON) is specified in the receipt protocol specification (`spec/RIO_RECEIPT_PROTOCOL_v0.1.md` in the `rio-receipt-protocol` repository). A valid signature proves the receipt was issued by the declared notary and has not been modified.

### 5.2 Ledger and Hash-Chain Integrity

Each receipt includes a `previous_receipt_hash` field linking it to the prior entry. The verifier walks the chain from the most recent entry backward, confirming that each entry's `receipt_hash` matches the `previous_receipt_hash` of the subsequent entry. A valid chain proves append-only integrity — no entries have been inserted, removed, or reordered.

### 5.3 Verifier Output

The reference implementation includes verification scripts (`verify_receipt.js`, `verify-chain.js` in the `rio-receipt-protocol` repository) that perform signature verification and chain verification programmatically. An external party can run these verifiers against any receipt or ledger segment.

### 5.4 Test Vectors

Conformance failure tests (CF-001 through CF-012) define the expected behavior when each boundary is tested. An external party can execute these test scenarios against a running implementation and compare the actual verdict and receipt output against the expected values.

### 5.5 Failure Receipts

When a boundary holds (blocks or holds an action), the system produces a failure receipt or HOLD receipt documenting what was attempted and why it was blocked. These receipts are themselves signed and ledger-appended, providing positive evidence of boundary enforcement.

### 5.6 Proof-Status Labels

Each artifact in the system carries a proof-status label (levels 0 through 10, as defined in the proof ladder). An external party can verify that no artifact claims a proof level higher than its evidence supports. Proof-status inflation — claiming a higher level than evidenced — is itself a conformance violation.

### 5.7 Implementation Separation

An architectural reviewer can verify that the execution path (bounded actor), the certification path (MUS / Receipt Notary), the observation path (MANTIS), and the governance path (RIO + approval gate) are structurally separated. In a conformant implementation, these components do not share signing keys, do not have write access to each other's stores, and do not expose approval or execution interfaces to observer components.

---

## 6. Honest Limitations

This Conformance Declaration does not prove the following:

**This does not prove perfection.** A conformant system is one that enforces its declared boundaries and produces evidence when those boundaries are tested. It does not guarantee that all possible failure modes have been anticipated, that all edge cases are covered, or that the system cannot be compromised through means outside the governance architecture.

**This does not prove no harm can occur.** A governed action that is properly authorized, receipted, and ledger-appended may still produce an undesirable real-world outcome. Governance proves process, not outcome. The receipt proves the system followed its rules — not that the rules were sufficient for every situation.

**This does not prove production certification.** This declaration is versioned as v0.1 with status `external_facing_draft`. It has not been submitted to or reviewed by any external certification body, standards organization, or regulatory authority. It represents the architecture's own conformance framework, not third-party certification.

**This does not prove external-world action occurred without external attestation.** Receipts prove what the system did. They do not prove what the external world experienced. If the system reports that an email was sent, the receipt proves the system executed the send operation. It does not prove the email was received, read, or acted upon. External attestation is a separate verification concern.

**This does not prove future actions are authorized.** Each authorization token is scoped to a specific action and is burned after use. A receipt proving that action A was authorized does not prove that action B is authorized. Authorization is per-action, not blanket.

**This does not prove human meaning.** Receipts prove that a structured intent was formed and that the system acted on it. They do not prove that the structured intent correctly captured the human's actual meaning, that the human understood the consequences, or that the action was wise.

**This does not prove the full ONE product is complete.** This declaration covers the conformance framework of the ONE/RIO/MUSS architecture. It does not represent the completeness of the ONE product, its market readiness, or its fitness for any particular use case.

---

## 7. Closing

The integrity of the system is not proven by saying what it can do. It is proven by showing what it must not permit, what fails closed when attempted, and what receipt proves the boundary held.

---

## Appendix A: Role Reminder

> The bounded actor acts. RIO governs. Sentinel enforces. MUS proves. Chronicle preserves. MANTIS learns. Human authority decides.

The bounded actor does **not** produce its own proof. MUS, through its Receipt Notary function, is the sole proof-production component.

---

## Appendix B: Companion Artifacts

| Artifact | Location | Status |
|----------|----------|--------|
| Must-Never Invariant Matrix v0.1 | `docs/conformance/must-never-invariant-matrix-v0.1.md` | `draft_reference` — in repo (PR #14 merged, PR #15 merged) |
| Conformance Receipt Schema | `docs/specs/conformance-receipt.schema.yaml` | `draft_reference` — in repo (PR #14 merged, PR #15 merged) |
| Accountability Determination Receipt Schema | `docs/specs/accountability-determination-receipt.schema.yaml` | `draft_reference` — in repo (PR #14 merged, PR #15 merged) |
| Conformance Failure Tests v0.1 | `docs/tests/conformance-failure-tests-v0.1.md` | `draft_reference` — in repo (PR #14 merged, PR #15 merged) |
| ADR-0006: Friction Before Consequence | `docs/adr/0006-friction-before-consequence.md` | `draft_reference` — in repo (PR #14 merged, PR #15 merged) |
| ADR-0007: Conformance Receipts and Accountability Boundary | `docs/adr/0007-conformance-receipts.md` | `draft_reference` — in repo (PR #14 merged, PR #15 merged) |
| Receipt Protocol Specification v0.1 | `rio-receipt-protocol/spec/RIO_RECEIPT_PROTOCOL_v0.1.md` | `draft_reference` — in repo (PR #7 merged) |

---

## Appendix C: Document Metadata

| Field | Value |
|-------|-------|
| Version | v0.1 |
| Status | `external_facing_draft` |
| Parent Document | Non-Sovereignty Invariants and Sovereignty Preservation Stack v0.3 |
| Author | Brian K. Rasmussen (B-Rass) |
| Drafted by | Manny (AI agent, under Brian's direction) |
| Date | 2026-05-12 |
| License | Per rio-protocol repository terms |
