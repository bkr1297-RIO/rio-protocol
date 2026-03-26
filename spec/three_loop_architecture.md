# Three-Loop Architecture — Intake, Execution/Governance, and Learning

**Version:** 2.0.0
**Status:** Architecture Specification
**Category:** System Architecture
**Supersedes:** `/spec/two_loop_architecture.md` (v1.0.0)

---

## Overview

RIO operates as three coupled loops:

- **Intake / Discovery Loop** — translates vague goals into structured intents before governance begins. It validates incoming requests, detects missing information, uses AI-assisted refinement to clarify ambiguous goals, and produces a well-defined structured intent. Also known as the Intake Translation Layer, Universal Grammar Layer, or Goal-to-Intent Layer.
- **Execution / Governance Loop** — controls and authorizes all actions before execution, then verifies and records. Every governed request passes through the full pipeline before any action is taken. All actions produce v2 receipts. All receipts are recorded in the signed ledger.
- **Learning Loop** — analyzes history to improve future governance without bypassing runtime controls. Learning operates asynchronously on historical data and submits proposed changes through a governed approval process.

The three loops are structurally separated. The Intake Loop produces structured intents. The Execution/Governance Loop enforces policy, executes, verifies, and records decisions. The Learning Loop reads from the decision history and proposes improvements. The Learning Loop never writes to the runtime, the ledger, or the execution gate directly. Its only output channel is the governance proposal process.

---

## Canonical System Flow

```
Goal → Intake / Discovery Loop → Structured Intent → Execution / Governance Loop → Receipt → Ledger → Learning Loop → Policy / Model Updates → Future Intake and Decisions
```

---

## 1. Intake / Discovery Loop

The Intake / Discovery Loop is the pre-governance path that translates goals into structured intents.

### High-Level Flow

```
Goal → Intake Validation → Missing Info Detection → AI-Assisted Refinement → Structured Intent
```

### Stages

| Stage | Intake Loop Role |
|-------|-----------------|
| Goal Reception | Receive the raw goal or request from an external requester |
| Intake Validation | Validate the request format and required fields |
| Missing Info Detection | Identify any missing information required to form a structured intent |
| AI-Assisted Refinement | Use AI to clarify ambiguous goals and fill in missing information |
| Intent Building | Produce a well-defined structured intent for the Execution/Governance Loop |

### Responsibilities

**Translate vague goals into structured intents.** The Intake Loop ensures that the Execution/Governance Loop always operates on well-defined, machine-readable intents rather than ambiguous requests.

**Validate incoming requests.** Every request is checked for format, required fields, and basic integrity before refinement begins.

**Detect missing information.** The Intake Loop identifies what information is needed to form a complete structured intent and either requests it from the requester or uses AI-assisted refinement.

**AI-assisted refinement is advisory.** The human or system confirms the final intent. AI refinement suggests but does not decide.

### Constraints

- Must produce a well-defined structured intent before governance starts
- AI refinement is advisory — the human or system confirms the final intent
- The Intake Loop does not execute actions, authorize actions, or write to the ledger

### Related Specifications

| Document | Path |
|----------|------|
| Intent Translation Layer | `/spec/intent_translation_layer.md` |
| Canonical Intent Schema | `/spec/canonical_intent_schema.md` |
| Canonical Intent Schema (JSON) | `/spec/canonical_intent_schema.json` |

---

## 2. Execution / Governance Loop

The Execution / Governance Loop is the real-time control path that governs every action in the system.

### High-Level Flow

```
Structured Intent → Policy & Risk → Authorization → Execution Gate → Execution → Verification → Receipt → Ledger
```

This maps to the pipeline stages:

| Step | Stage | Execution Loop Role |
|------|-------|---------------------|
| 1 | Intake | Register and authenticate the incoming structured intent |
| 2 | Classification | Classify the intent into action type and risk domain |
| 3 | Structured Intent | Validate the canonical structured format |
| 4 | Policy & Risk Check | Evaluate the structured intent against policy and risk models |
| 5 | Authorization | Obtain required authorization (human or policy-based) |
| 6 | Execution Gate | Prevent execution unless authorization is valid |
| 6b | Post-Execution Verification | Compute intent_hash, action_hash, and verification_hash (SHA-256) |
| 7 | v2 Receipt Generation | Generate signed receipt with all hashes, risk data, policy decision, timestamps |
| 8 | v2 Ledger Entry | Record receipt in the signed hash-chained ledger |

### Responsibilities

**Enforce policies and risk constraints around every action.** Every request is evaluated against the current policy set and risk model before authorization. No action proceeds without passing both policy and risk evaluation.

**Ensure no execution without authorization.** The Execution Gate (Step 6) blocks all actions that do not carry a valid, signed, unexpired authorization token. There is no bypass mechanism except the kill switch, which blocks all execution.

**Verify execution against intent.** The Post-Execution Verification stage (Step 6b) computes intent_hash, action_hash, and verification_hash to cryptographically bind the intent to the action that was performed.

**Emit v2 cryptographic receipts.** Every governed action — whether approved, denied, blocked, or failed — produces a signed v2 receipt containing intent_hash, action_hash, verification_hash, risk scoring, policy decisions, and three ISO 8601 timestamps. Denial receipts are generated for blocked actions.

**Append to signed ledger.** Every receipt is written to the append-only audit ledger with hash chain linkage and per-entry ledger_signature. The ledger provides tamper-evident, independently verifiable history of all governed actions.

### Related Specifications

| Document | Path |
|----------|------|
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
| Receipt Protocol | `/spec/receipt_protocol.md` |
| Audit Ledger Protocol | `/spec/audit_ledger_protocol.md` |

---

## 3. Learning Loop

The Learning Loop is the asynchronous analysis path that improves governance over time based on historical data.

### High-Level Flow

```
Ledger → Audit → Pattern Analysis → Policy Updates → Model Updates → Future Decisions
```

### Stages

| Stage | Learning Loop Role |
|-------|-------------------|
| Ledger Read | Retrieve historical receipts and ledger entries |
| Audit | Verify integrity and compliance of historical records |
| Pattern Analysis | Detect patterns in intents, decisions, outcomes, and incidents |
| Policy Update | Propose updates to policy rules based on observed patterns |
| Model Update | Propose updates to risk models and classification models |
| Future Decisions | Updated policies and models are deployed to the Execution Loop through governed change |

### Responsibilities

**Analyze historical ledger and governed corpus data.** The Learning Loop reads from the Governed Corpus, which structures receipt data, execution outcomes, and governance events into a queryable dataset.

**Detect patterns in intents, decisions, outcomes, and incidents.** The Learning Loop identifies calibration errors in risk scoring, excessive false positive or false negative rates in policy evaluation, emerging action patterns that require new policy rules, and incidents that indicate gaps in the current governance model.

**Propose updates to policies, risk models, and intent patterns.** The Learning Loop produces versioned proposals with supporting evidence from the Governed Corpus. These proposals are submitted to the governance approval process.

### Safety Constraints

Learning never:

- **Directly triggers actions.** The Learning Loop has no execution capability. It cannot invoke external systems, APIs, or resources.
- **Writes to the ledger bypassing the execution loop.** The Learning Loop has read-only access to the ledger. It cannot append, modify, or delete ledger entries.
- **Modifies runtime constraints without a governed change procedure.** All proposed changes must go through governance review and approval before deployment. The deployment is recorded in the ledger as a governance change event.
- **Bypasses governance.** All policy updates must go through the Execution/Governance Loop before deployment.

### Related Specifications

| Document | Path |
|----------|------|
| Governed Corpus | `/spec/governed_corpus.md` |
| Governance Learning Protocol | `/spec/governance_learning_protocol.md` |

---

## Loop Coupling

The three loops are coupled through structured intents, the ledger, and the governance change process:

```
Intake Loop → Structured Intent → Execution/Governance Loop → Receipts → Ledger → Governed Corpus → Learning Loop → Proposals → Governance Review → Approved Changes → Execution/Governance Loop
```

The Intake Loop produces the structured intents that the Execution/Governance Loop governs. The Execution/Governance Loop produces the data that the Learning Loop analyzes. The Learning Loop produces proposals that, after governance approval, update the policies and models used by both the Intake Loop and the Execution/Governance Loop. This creates a controlled feedback cycle where the system improves over time without compromising runtime safety guarantees.

### Coupling Points

| Coupling Point | Direction | Mechanism |
|----------------|-----------|-----------|
| Structured Intent | Intake → Execution | Intake produces structured intents consumed by the Execution/Governance Loop |
| Ledger | Execution → Learning | Learning reads from the append-only ledger (read-only) |
| Governed Corpus | Execution → Learning | Learning queries structured decision history |
| Policy Updates | Learning → Execution | Approved changes deployed through governed change process |
| Model Updates | Learning → Execution/Intake | Approved risk/classification/refinement models deployed through governed change process |

No coupling point allows the Learning Loop to bypass the Execution/Governance Loop's runtime controls.

---

## Migration from Two-Loop Architecture

The Three-Loop Architecture extends the previous Two-Loop Architecture (v1.0.0) by extracting the Intake / Discovery Loop as a first-class architectural component. The Execution Loop and Learning Loop from the Two-Loop Architecture map directly to the Execution/Governance Loop and Learning Loop in this specification. The key addition is the formalization of goal-to-intent translation as a distinct, governed loop that operates before the Execution/Governance Loop.

---

## References

| Document | Path |
|----------|------|
| Intent Translation Layer | `/spec/intent_translation_layer.md` |
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Governance Learning Protocol | `/spec/governance_learning_protocol.md` |
| Governed Corpus | `/spec/governed_corpus.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| Reference Architecture | `/spec/reference_architecture.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
