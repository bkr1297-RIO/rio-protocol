# Governed Execution Protocol

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Protocol Definition

---

## Overview

The Governed Execution Protocol is an eight-stage runtime control protocol that converts AI-generated requests into authorized, verifiable, and auditable actions through intake registration, classification, structured intent formation, policy and risk evaluation, cryptographic authorization, gated execution, signed receipt generation, and immutable audit logging.

A ninth, asynchronous Governance Learning loop updates risk and policy models based on observed outcomes and does not bypass runtime controls.

---

## Protocol Stages

### Stage 1 — Intake

**Purpose:** Register and authenticate incoming request.

**Outputs:**

| Output | Description |
|--------|-------------|
| Request ID | Unique identifier assigned to this request |
| Actor Identity | Authenticated identity of the requesting entity |
| Timestamp | UTC timestamp of request registration |
| Nonce | Cryptographic nonce to prevent replay |
| Raw Input | Original, unmodified request payload |

---

### Stage 2 — Classification

**Purpose:** Classify the request into action type and risk domain.

**Outputs:**

| Output | Description |
|--------|-------------|
| Action Type | Categorized action (e.g., `transact.send_payment.wire.domestic`) |
| Domain | Risk domain the action falls under (e.g., financial, infrastructure, data) |
| Preliminary Risk Level | Initial risk assessment (`low`, `medium`, `high`, `critical`) |

---

### Stage 3 — Structured Intent

**Purpose:** Convert request into canonical structured format.

**Outputs:**

| Output | Description |
|--------|-------------|
| Canonical Intent Object | Structured, schema-validated representation of the requested action with all parameters, constraints, and scope boundaries |

---

### Stage 4 — Policy & Risk Check

**Purpose:** Evaluate structured intent against policy and risk models.

**Outputs:**

| Output | Description |
|--------|-------------|
| Policy Decision | Result of policy evaluation (`allow`, `deny`, `escalate`) |
| Risk Score | Quantified risk assessment from the risk evaluation engine |
| Constraints | Any constraints or conditions imposed by policy on execution |

---

### Stage 5 — Authorization

**Purpose:** Obtain required authorization (human or policy-based).

**Outputs:**

| Output | Description |
|--------|-------------|
| Authorization Decision | `approved`, `denied`, or `escalated` |
| Signed Authorization Token | Cryptographically signed token if approved, binding the authorizer's identity to the decision |

---

### Stage 6 — Execution Gate

**Purpose:** Prevent execution unless authorization is valid.

**Outputs:**

| Output | Description |
|--------|-------------|
| Execution Token | Time-bound, single-use token released to the executor if all preconditions are met |
| Blocked Action | If preconditions fail, execution is denied and the request is terminated |

---

### Stage 7 — Receipt / Attestation

**Purpose:** Generate cryptographic proof of decision and execution.

**Outputs:**

| Output | Description |
|--------|-------------|
| Signed Receipt | Cryptographic receipt containing intent hash, decision hash, execution hash, and timestamp |

---

### Stage 8 — Audit Ledger

**Purpose:** Record immutable history of governed actions.

**Outputs:**

| Output | Description |
|--------|-------------|
| Append-Only Ledger Entry | Immutable record linked by hash chain to the previous entry, forming a tamper-evident audit trail |

---

### Stage 9 — Governance Learning (Asynchronous)

**Purpose:** Update risk models and policies based on outcomes without bypassing runtime enforcement.

**Outputs:**

| Output | Description |
|--------|-------------|
| Updated Policy Versions | Revised policy rules informed by observed outcomes |
| Updated Risk Models | Recalibrated risk scoring models reflecting new data |

Governance Learning operates on historical governed decision data stored in the Governed Corpus. The Governed Corpus is a structured decision-history layer that records intent, classification, policy decisions, authorization outcomes, execution results, receipts, ledger references, and eventual outcomes. Learning processes use this corpus to update risk models and policies without bypassing runtime enforcement.

See `/spec/governed_corpus.md` for the Governed Corpus specification.

---

## Protocol Flow

Intake → Classification → Structured Intent → Policy & Risk → Authorization → Execution Gate → Receipt → Audit Ledger → Learning


---

## Protocol Invariants

The following invariants define safety and correctness properties that must never be violated by any implementation of the Governed Execution Protocol. These invariants apply across all runtime stages and are enforced by the runtime, authorization system, and execution gate.

See `/spec/protocol_invariants.md` for the full invariant definitions.

---

## Safety Mechanisms

The protocol includes a global execution halt mechanism (EKS-0 Kill Switch) that overrides normal authorization and execution behavior. When engaged, no new executions may proceed regardless of policy decisions. All kill switch events and blocked requests must still generate receipts and be written to the audit ledger.

See `/safety/EKS-0_kill_switch.md` and `/tests/TC-RIO-003.md` for specification and test behavior.
