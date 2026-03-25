# Two-Loop Architecture — Execution and Learning

**Version:** 1.0.0
**Status:** Architecture Specification
**Category:** System Architecture

---

## Overview

RIO operates as two coupled loops:

- **Execution Loop** — controls and records actions in real time. Every governed request passes through the full 8-step protocol before any action is taken.
- **Learning Loop** — analyzes history to improve future governance without bypassing runtime controls. Learning operates asynchronously on historical data and submits proposed changes through a governed approval process.

The two loops are structurally separated. The Execution Loop enforces policy and records decisions. The Learning Loop reads from the decision history and proposes improvements. The Learning Loop never writes to the runtime, the ledger, or the execution gate directly. Its only output channel is the governance proposal process.

---

## 1. Execution Loop

The Execution Loop is the real-time control path that governs every action in the system.

### High-Level Flow

```
Goal → Intent → Govern → Approve → Execute → Verify → Receipt → Ledger
```

This maps to the 8-step Governed Execution Protocol:

| Step | Stage | Execution Loop Role |
|------|-------|---------------------|
| 1 | Intake | Register and authenticate the incoming request |
| 2 | Classification | Classify the request into action type and risk domain |
| 3 | Structured Intent | Convert the request into canonical structured format |
| 4 | Policy & Risk Check | Evaluate the structured intent against policy and risk models |
| 5 | Authorization | Obtain required authorization (human or policy-based) |
| 6 | Execution Gate | Prevent execution unless authorization is valid |
| 7 | Receipt / Attestation | Generate cryptographic proof of decision and execution |
| 8 | Audit Ledger | Record immutable history in the append-only ledger |

### Responsibilities

The Execution Loop is responsible for the following:

**Enforce policies and risk constraints around every action.** Every request is evaluated against the current policy set and risk model before authorization. No action proceeds without passing both policy and risk evaluation.

**Ensure no execution without authorization.** The Execution Gate (Step 6) blocks all actions that do not carry a valid, signed, unexpired authorization token. There is no bypass mechanism except the kill switch, which blocks all execution.

**Emit cryptographic receipts.** Every governed action — whether approved, denied, blocked, or failed — produces a signed receipt that records the intent, decision, execution status, and result hash. Receipts are the atomic unit of the audit trail.

**Append to immutable ledger.** Every receipt is written to the append-only audit ledger with hash chain linkage. The ledger provides tamper-evident, independently verifiable history of all governed actions.

### Related Specifications

| Document | Path |
|----------|------|
| Intent Formation and Validation Protocol | `/spec/intent_formation_and_validation_protocol.md` |
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
| Receipt / Attestation Protocol | `/spec/receipt_protocol.md` |
| Audit Ledger Protocol | `/spec/audit_ledger_protocol.md` |

---

## 2. Learning Loop

The Learning Loop is the asynchronous analysis path that improves governance over time based on historical data.

### High-Level Flow

```
Ledger → Audit → Pattern Analysis → Policy Update → Model Update → Future Decisions
```

This maps to the following stages:

| Stage | Learning Loop Role |
|-------|-------------------|
| Ledger Read | Retrieve historical receipts and ledger entries |
| Audit | Verify integrity and compliance of historical records |
| Pattern Analysis | Detect patterns in intents, decisions, outcomes, and incidents |
| Policy Update | Propose updates to policy rules based on observed patterns |
| Model Update | Propose updates to risk models and classification models |
| Future Decisions | Updated policies and models are deployed to the Execution Loop through governed change |

### Responsibilities

The Learning Loop is responsible for the following:

**Analyze historical ledger and governed corpus data.** The Learning Loop reads from the Governed Corpus, which structures receipt data, execution outcomes, and governance events into a queryable dataset.

**Detect patterns in intents, decisions, outcomes, and incidents.** The Learning Loop identifies calibration errors in risk scoring, excessive false positive or false negative rates in policy evaluation, emerging action patterns that require new policy rules, and incidents that indicate gaps in the current governance model.

**Propose updates to policies, risk models, and intent patterns.** The Learning Loop produces versioned proposals with supporting evidence from the Governed Corpus. These proposals are submitted to the governance approval process.

### Safety Constraints

Learning never:

- **Directly triggers actions.** The Learning Loop has no execution capability. It cannot invoke external systems, APIs, or resources.
- **Writes to the ledger bypassing the execution loop.** The Learning Loop has read-only access to the ledger. It cannot append, modify, or delete ledger entries.
- **Modifies runtime constraints without a governed change procedure.** All proposed changes must go through governance review and approval before deployment. The deployment is recorded in the ledger as a governance change event.

### Related Specifications

| Document | Path |
|----------|------|
| Governed Corpus | `/spec/governed_corpus.md` |
| Governance Learning Protocol | `/spec/governance_learning_protocol.md` |

---

## Loop Coupling

The two loops are coupled through the ledger and the governance change process:

```
Execution Loop → Receipts → Ledger → Governed Corpus → Learning Loop → Proposals → Governance Review → Approved Changes → Execution Loop
```

The Execution Loop produces the data that the Learning Loop analyzes. The Learning Loop produces proposals that, after governance approval, update the policies and models used by the Execution Loop. This creates a controlled feedback cycle where the system improves over time without compromising runtime safety guarantees.

The coupling points are:

| Coupling Point | Direction | Mechanism |
|----------------|-----------|-----------|
| Ledger | Execution → Learning | Learning reads from the append-only ledger (read-only) |
| Governed Corpus | Execution → Learning | Learning queries structured decision history |
| Policy Updates | Learning → Execution | Approved changes deployed through governed change process |
| Model Updates | Learning → Execution | Approved risk/classification models deployed through governed change process |

No coupling point allows the Learning Loop to bypass the Execution Loop's runtime controls.

---

## References

| Document | Path |
|----------|------|
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Governance Learning Protocol | `/spec/governance_learning_protocol.md` |
| Governed Corpus | `/spec/governed_corpus.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| Reference Architecture | `/spec/reference_architecture.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
