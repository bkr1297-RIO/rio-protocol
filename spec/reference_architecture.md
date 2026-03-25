# RIO Reference Architecture

**Version:** 2.0.0
**Status:** Core Specification
**Category:** Architecture

---

## 1. System Overview

RIO is a governed execution architecture that converts goals and intents into authorized, executed, attested, and permanently recorded actions through a controlled protocol. Every consequential action — regardless of whether it originates from an AI agent, an automated system, or a human-initiated workflow — must traverse the full protocol before it can affect any external system.

The core flow proceeds through the following stages:

```
Goal → Intent Formation → Intent Validation → Governed Execution Protocol → Receipt → Ledger → Audit → Learning
```

The architecture is organized into four functional layers that operate in sequence:

**The Specification Layer** defines the rules. It contains schemas, constraints, invariants, and protocol definitions that govern what is permissible, how requests must be structured, and what properties the system must maintain. The specification layer does not execute anything — it provides the normative framework against which all runtime behavior is evaluated.

**The Control Plane** enforces execution. It implements the 8-step Governed Execution Protocol (Intake, Classification, Structured Intent, Policy & Risk Check, Authorization, Execution Gate, Receipt/Attestation, Audit Ledger) and ensures that every request is processed according to the rules defined in the specification layer. The control plane is the runtime enforcement mechanism.

**The Ledger** records history. Every decision — whether approved, denied, or blocked — produces a cryptographic receipt that is appended to an immutable, hash-linked audit ledger. The ledger provides the permanent, tamper-evident record of all governed actions.

**The Audit Layer** verifies correctness. Independent auditors can verify the integrity of the system by recomputing hash chains, validating signatures, checking invariants, and reconstructing decision chains from the ledger. The audit layer operates independently of the runtime and does not depend on trust in any single component.

---

## 2. System Planes

The RIO architecture is decomposed into eight system planes. Each plane has a defined responsibility and operates within explicit boundaries. No plane is trusted in isolation — system correctness depends on the interaction of all planes and the cryptographic verification that links them.

| Plane | Responsibility |
|-------|----------------|
| Specification Plane | Defines schemas, constraints, invariants, and protocol rules |
| Intent Plane | Goal clarification, intent formation, validation, authorization |
| Control Plane | Execution orchestration and enforcement |
| Execution Plane | External systems perform actions |
| Receipt Plane | Generates cryptographic proof of decisions and actions |
| Ledger Plane | Stores immutable history (append-only ledger) |
| Audit Plane | Independent verification and compliance review |
| Learning Plane | Governance learning, risk tuning, policy updates |

The **Specification Plane** is static and changes only through the governed change process (meta-governance). The **Intent Plane** and **Control Plane** operate synchronously for every request. The **Execution Plane** interfaces with external systems under the constraints set by the Control Plane. The **Receipt Plane** and **Ledger Plane** operate as write-once, append-only stores. The **Audit Plane** operates independently and asynchronously. The **Learning Plane** operates asynchronously on historical data and redeploys updates through the governed change process.

---

## 3. Reference Architecture Diagram

The following diagram shows the end-to-end flow from goal formation through governance learning:

```mermaid
flowchart LR
    Goal[Goal]
    Intent[Intent Formation]
    Validate[Intent Validation]
    Intake[Intake]
    Policy[Policy & Risk]
    Auth[Authorization]
    Gate[Execution Gate]
    Exec[Execution System]
    Receipt[Receipt]
    Ledger[Audit Ledger]
    Audit[Audit / Verification]
    Learn[Governance Learning]

    Goal --> Intent --> Validate --> Intake --> Policy --> Auth --> Gate --> Exec --> Receipt --> Ledger --> Audit --> Learn
```

![RIO Reference Architecture Diagram](../diagrams/reference_architecture.png)

The diagram illustrates the linear flow of a single request through the system. In practice, the Learning stage feeds updated risk models and policies back into the Policy & Risk stage through the governed change process, creating a closed loop. The Audit stage can query any point in the chain independently.

---

## 4. Trust Boundaries

The architecture defines six trust boundaries. No single component is trusted end-to-end. The system relies on separation of duties, cryptographic verification, and independent audit to establish correctness.

| Trust Boundary | Inside | Outside | Enforcement Mechanism |
|----------------|--------|---------|----------------------|
| AI / Agent Boundary | AI agents, automated systems, goal generators | All protocol stages | Agents may generate requests but cannot authorize, execute, or attest. All agent output enters the protocol through Intake and is treated as untrusted input. |
| Authorization Boundary | Human approvers, delegated policy authorities | Requesters, execution systems | Authorization requires a distinct identity from the requester (INV-06). Authorization tokens are signed, time-bound, and single-use. |
| Execution Boundary | Execution Gate, Execution Engine | All other components | Execution proceeds only when the Execution Gate validates a signed, unexpired, unspent authorization token bound to the correct canonical intent. The kill switch (EKS-0) overrides all execution. |
| Ledger Boundary | Ledger Service, append-only storage | Runtime components, external systems | The ledger accepts only append operations. No component can modify or delete ledger entries. The hash chain makes tampering detectable. |
| Audit Boundary | Independent auditors, verification tools | All runtime components | Auditors operate with read-only access to the ledger and receipt store. They verify correctness by recomputing hashes and signatures using public keys from the key registry. |
| Human Governance Boundary | Policy administrators, governance board | Automated systems, learning outputs | Changes to protocol rules, invariants, schemas, and policies require human governance approval. The learning loop proposes changes but cannot deploy them without governance review. |

---

## 5. Data Flow Summary

The following data objects flow between protocol stages. Each object is produced by a specific stage and consumed by one or more downstream stages.

| Data Object | Produced By | Consumed By | Description |
|-------------|-------------|-------------|-------------|
| Intent Data | Intent Formation | Intent Validation, Intake | Raw structured intent containing action type, target, parameters, and justification |
| Canonical Intent | Structured Intent (Stage 3) | Policy & Risk, Authorization, Execution Gate | Normalized, validated, hashed intent object in canonical format |
| Risk and Policy Decisions | Policy & Risk Check (Stage 4) | Authorization | Risk score, policy decision (permit/deny/escalate), constraints, required approval level |
| Authorization Tokens | Authorization (Stage 5) | Execution Gate | Signed, time-bound, single-use tokens binding an approver's decision to a specific canonical intent |
| Execution Results | Execution Engine (Stage 6) | Receipt Service | Outcome of the executed action, including status, result payload, and error information |
| Receipts | Receipt Service (Stage 7) | Ledger Service, Governed Corpus | Cryptographic proof linking intent hash, authorization decision, execution result, and timestamps |
| Ledger Entries | Ledger Service (Stage 8) | Audit, Governed Corpus | Hash-linked, append-only records containing receipt references and chain pointers |
| Audit Queries | Audit Plane | Ledger, Receipt Store, Key Registry | Read-only queries to verify hash chains, signatures, invariants, and decision chain completeness |
| Learning Signals | Learning Plane | Policy Engine, Risk Evaluator (via governance) | Proposed updates to risk models, policy rules, thresholds, and classification models based on historical decision data |

---

## 6. Verification Model

System correctness can be verified independently by any party with read access to the ledger and receipt store. Verification does not require trust in any runtime component. The following verification methods are supported:

**Receipt signature verification.** Every receipt carries an ECDSA-secp256k1 signature. An auditor retrieves the Receipt Service's public key from the key registry and independently verifies the signature over the receipt's canonical JSON representation. A valid signature proves the receipt was generated by the authorized Receipt Service and has not been modified.

**Ledger hash chain integrity.** Each ledger entry contains a SHA-256 hash of the previous entry. An auditor recomputes all hashes from the genesis entry forward and verifies that each `previous_ledger_hash` matches. Any break in the chain indicates tampering, deletion, or reordering.

**Invariant checks.** The 8 protocol invariants (INV-01 through INV-08) define properties that must hold for every governed action. An auditor can verify these invariants by examining decision chains: every action traversed all stages (INV-01), every action produced a receipt (INV-02), every receipt was recorded in the ledger (INV-03), the hash chain is unbroken (INV-04), and so on.

**Test case execution.** The protocol test cases (TC-RIO-001 through TC-RIO-003) define expected behavior for allowed execution, denied execution, and kill switch scenarios. These tests can be executed against any implementation to verify conformance.

**Independent audit review.** An auditor can reconstruct the full decision chain for any governed action by starting from a ledger entry, following the receipt reference to the receipt, then following the intent and authorization references to the original request. This reconstruction is deterministic and repeatable.

---

## 7. Learning Loop

Governance Learning operates on historical ledger and receipt data stored in the Governed Corpus. It analyzes patterns in decision outcomes, risk scores, policy decisions, and execution results to propose updates to:

**Risk models.** Updated risk scoring parameters based on observed outcomes. Actions that consistently produce adverse outcomes may receive higher risk scores. Actions with clean track records may be candidates for streamlined processing.

**Policy rules.** New or modified policy rules based on observed patterns. Policies that produce excessive false positives or false negatives can be refined based on historical data.

**Thresholds.** Adjusted approval thresholds, time limits, and escalation triggers based on operational experience.

**Classification models.** Improved action type classification and risk domain assignment based on historical classification accuracy.

Learning cannot bypass runtime enforcement. All proposed changes from the learning loop must be reviewed and approved through the governed change process (meta-governance) before they take effect in the runtime. The learning loop reads from the Governed Corpus and writes proposed changes to a staging area. Deployment of those changes into the live runtime requires human governance approval and follows the same protocol controls that apply to any other consequential action.

---

## References

| Document | Path |
|----------|------|
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| 8-Step Runtime Flow | `/spec/runtime_flow.md` |
| 15-Layer System Architecture | `/architecture/15_layer_model.md` |
| 4-Layer System Architecture | `/spec/system_architecture.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
| Governed Corpus | `/spec/governed_corpus.md` |
| Threat Model | `/spec/threat_model.md` |
| Protocol Test Matrix | `/spec/protocol_test_matrix.md` |
