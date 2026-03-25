# Reference Architecture

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Architecture

---

## Overview

The RIO Reference Architecture describes the overall system architecture through which AI-generated requests are converted into authorized, verifiable, and auditable actions. The architecture defines the component roles, control boundaries, and data flow from initial goal formation through execution, receipt generation, ledger recording, and governance learning.

---

## System Flow

The end-to-end system flow proceeds through the following stages:

```
Goal → Intent Formation → Intent Validation → Governed Execution Protocol → Receipt → Ledger → Learning
```

| Stage | Description |
|-------|-------------|
| Goal | An AI agent, automated system, or human-initiated workflow identifies an objective that requires a real-world action |
| Intent Formation | The raw goal is translated into a structured intent object with action type, target resource, parameters, and justification |
| Intent Validation | The structured intent is validated against schema requirements, field completeness, and format constraints before entering the protocol |
| Governed Execution Protocol | The validated intent passes through the 8-step runtime protocol: Intake, Classification, Structured Intent, Policy & Risk Check, Authorization, Execution Gate, Receipt/Attestation, Audit Ledger |
| Receipt | A cryptographic receipt is generated for every decision (approved, denied, or blocked) linking intent, authorization, and execution result |
| Ledger | The receipt is recorded as an append-only, hash-linked entry in the audit ledger |
| Learning | Historical decision data from the Governed Corpus is analyzed to update risk models and policies through a governed change process |

---

## Component Roles

The following components implement the system architecture. Each component has a defined responsibility and operates within explicit control boundaries.

| Component | Responsibility | Protocol Stage |
|-----------|---------------|----------------|
| Intake Service | Receives incoming requests, authenticates the requester, assigns request IDs, timestamps, and nonces | Step 1 — Intake |
| Classification Engine | Classifies the request into action type and risk domain, assigns preliminary risk level | Step 2 — Classification |
| Intent Normalizer | Converts the classified request into a canonical structured intent object with standardized fields | Step 3 — Structured Intent |
| Policy Engine | Evaluates the canonical intent against organizational policies, regulatory constraints, and operational boundaries | Step 4 — Policy & Risk Check |
| Risk Evaluator | Computes quantified risk scores based on action type, target resource, actor history, and contextual factors | Step 4 — Policy & Risk Check |
| Authorization Service | Routes the request to the appropriate human or delegated authority, collects the authorization decision, and issues a signed authorization token | Step 5 — Authorization |
| Execution Gate | Validates the authorization token (signature, expiration, single-use, intent binding, kill switch status) before releasing the action for execution | Step 6 — Execution Gate |
| Execution Engine | Carries out the authorized action within the constraints and scope defined by the authorization token | Step 6 — Execution Gate |
| Receipt Service | Generates a cryptographic receipt containing intent hash, decision hash, execution hash, timestamp, and ECDSA-secp256k1 signature | Step 7 — Receipt/Attestation |
| Ledger Service | Appends the receipt as a hash-linked entry in the append-only audit ledger | Step 8 — Audit Ledger |
| Learning Service | Reads historical decision data from the Governed Corpus and proposes updates to risk models and policies | Step 9 — Governance Learning |

---

## Separation of Responsibilities

The architecture enforces strict separation between the following functional domains:

**Request Generation vs. Request Authorization.** AI agents and automated systems may generate requests, but they cannot authorize their own requests. Authorization requires a distinct entity (human approver or independent delegated authority) whose identity differs from the requester. This separation is enforced structurally by the protocol (INV-06), not by policy alone.

**Policy Evaluation vs. Execution.** The Policy Engine determines whether a request is permissible. The Execution Gate determines whether the authorization is valid. The Execution Engine carries out the action. These three functions operate independently. A policy approval does not bypass authorization. An authorization does not bypass the execution gate.

**Runtime Enforcement vs. Governance Learning.** The runtime protocol (Steps 1–8) enforces controls synchronously for every request. The learning loop (Step 9) operates asynchronously on historical data. Learning outputs (updated risk models, policy changes) must themselves pass through the governed change process before taking effect in the runtime. The learning loop cannot bypass, override, or weaken runtime controls.

**Receipt Generation vs. Ledger Storage.** The Receipt Service generates cryptographic proofs. The Ledger Service stores them immutably. These are separate components with separate signing keys. A compromise of the Receipt Service does not grant write access to the ledger. A compromise of the Ledger Service does not grant the ability to forge receipts.

---

## Control Boundaries

The architecture defines three control boundaries:

| Boundary | Inside | Outside | Enforcement |
|----------|--------|---------|-------------|
| Runtime Boundary | Intake, Classification, Intent Normalization, Policy, Risk, Authorization, Execution Gate | AI agents, external systems, execution targets | All requests must enter through Intake. All executions must exit through the Execution Gate. No direct path from requester to execution target exists. |
| Audit Boundary | Receipt Service, Ledger Service, Governed Corpus | Runtime components, external systems | All runtime decisions produce receipts. All receipts are recorded in the ledger. The audit boundary is write-only from the runtime perspective — runtime components cannot modify or delete audit records. |
| Learning Boundary | Learning Service, Governed Corpus (read), Policy/Risk model updates | Runtime enforcement, authorization decisions | Learning reads historical data and proposes changes. Changes are deployed through a governed change process that is itself subject to the protocol. Learning cannot directly modify runtime behavior. |

---

## Fundamental Rule

> Agents may generate requests, but all real-world actions must pass through the Governed Execution Protocol.

No component, agent, or system may execute a consequential action without traversing the full 8-step runtime protocol. This rule applies regardless of the requester's identity, the action's risk level, or the urgency of the request. The kill switch (EKS-0) provides the only mechanism to halt all execution globally, and even kill switch events are recorded in the audit ledger.

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
