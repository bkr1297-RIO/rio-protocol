# Governance Learning Protocol

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Protocol Stage (Stage 9 — Asynchronous)

---

## 1. Purpose

The Governance Learning Protocol defines how the RIO system improves over time by learning from historical decisions, outcomes, and audit data.

Learning operates on historical data and does not directly control execution. All runtime decisions must still pass through the Governed Execution Protocol (Steps 1–8). The Learning Protocol is asynchronous — it runs after execution, not during it — and its outputs are subject to governance approval before they affect the runtime.

This enforces invariant:

- **INV-05:** Learning cannot bypass runtime controls.

---

## 2. Learning Inputs

The Governance Learning system may use the following data sources:

| Data Source | Purpose |
|-------------|---------|
| Receipts | Decision history — what was requested, decided, and executed |
| Ledger | Immutable record — the authoritative, tamper-evident history of all governed actions |
| Execution outcomes | Success/failure data — whether executions achieved their intended results |
| Incident reports | Failures and policy violations — cases where the system or its operators failed |
| Human overrides | Governance corrections — cases where human governance overrode automated decisions |
| Audit findings | Compliance issues — results of periodic or on-demand audits |
| Risk scores | Model calibration — historical risk scores compared against actual outcomes |

These inputs form the **Governed Corpus**. The Governed Corpus is the structured decision-history layer that aggregates receipt data, execution outcomes, and governance events into a queryable dataset for analysis and learning. See `/spec/governed_corpus.md` for the full specification.

---

## 3. Learning Outputs

The Governance Learning system may produce the following outputs:

| Output | Description |
|--------|-------------|
| Updated risk model | Improved risk scoring based on historical outcome data |
| Updated policy rules | New or modified constraints based on observed patterns |
| Threshold adjustments | Changes to risk or approval thresholds based on calibration data |
| Classification improvements | Better action classification based on historical request patterns |
| Intent schema improvements | Improved required fields or validation rules for canonical intents |
| Governance recommendations | Suggested rule changes for human governance review |

Learning produces **recommendations and model updates**, not direct execution. No learning output takes effect in the runtime until it has been approved through the governance change process and recorded in the ledger as a governance change event.

---

## 4. Governance Control

All learning outputs must go through a governance approval process before being deployed to the runtime:

```
Learning → Proposed Change → Governance Review → Approval → Deploy to Runtime Policy/Risk
```

Learning cannot directly modify runtime behavior without governance approval. The governance review process includes:

- **Proposal.** The learning system produces a proposed change (new risk model, updated policy rule, threshold adjustment) with supporting evidence from the Governed Corpus.
- **Review.** A governance authority (human or governance committee) reviews the proposed change, its evidence, and its expected impact.
- **Approval.** The governance authority approves or rejects the proposed change. Approval is recorded as a governance decision.
- **Deployment.** The approved change is deployed to the runtime through the governed change process. The deployment is recorded in the ledger as a governance change event.

Every step in this process is auditable. The ledger records the governance change event, linking it to the proposal, the approval decision, and the deploying authority.

---

## 5. Separation from Runtime

The learning system and the runtime system are structurally separated:

| Runtime System | Learning System |
|----------------|-----------------|
| Makes decisions | Analyzes history |
| Executes actions | Suggests improvements |
| Enforces policies | Updates policies (through governance) |
| Generates receipts | Uses receipts as data |
| Writes ledger | Reads ledger |

This separation ensures learning cannot bypass safety controls. The learning system has **read-only access** to the ledger and the Governed Corpus. It has **no write access** to the runtime, the authorization system, the execution gate, or the ledger. Its only output channel is the governance proposal process.

---

## 6. Feedback Loop

The governance loop works as follows:

```
Ledger → Governed Corpus → Risk/Policy Analysis → Governance Decision → Policy Update → Runtime Enforcement → New Receipts → Ledger
```

This creates a controlled feedback loop where:

1. The **Ledger** provides the immutable record of all governed actions.
2. The **Governed Corpus** structures this data for analysis.
3. **Risk/Policy Analysis** identifies patterns, calibration errors, and improvement opportunities.
4. A **Governance Decision** approves or rejects proposed changes.
5. Approved **Policy Updates** are deployed to the runtime.
6. The **Runtime** enforces the updated policies on new requests.
7. New **Receipts** are generated and written to the ledger.
8. The cycle continues.

The feedback loop is closed but governed. No step in the loop bypasses the Governed Execution Protocol for runtime decisions, and no policy change takes effect without governance approval.

---

## 7. Safety Constraints

The learning system must never:

- **Execute actions.** The learning system has no execution capability. It cannot invoke external systems, APIs, or resources.
- **Issue authorization tokens.** The learning system cannot authorize any action. Authorization is exclusively the responsibility of Stage 5 (Authorization).
- **Modify the ledger.** The learning system has read-only access to the ledger. It cannot append, modify, or delete ledger entries.
- **Bypass the execution gate.** The learning system has no interface to the execution gate. It cannot cause an action to execute.
- **Disable the kill switch.** The learning system has no interface to EKS-0. It cannot engage or disengage the kill switch.
- **Change invariants without governance approval.** Protocol invariants are structural safety properties. Any proposed change to an invariant must go through the full governance review process with elevated approval requirements.

Violation of any of these constraints is a protocol integrity failure and must trigger an alert to the governance authority.

---

## 8. Versioning and Change Tracking

All policy and risk model updates produced by the learning system must be:

- **Versioned.** Each update receives a unique version identifier that distinguishes it from all previous versions.
- **Logged.** The update, its evidence, and its governance review are recorded in the system's operational log.
- **Approved.** The update must receive explicit governance approval before deployment.
- **Recorded in the ledger as governance change events.** The deployment of the update is recorded as a ledger entry with receipt type "Governance Change," linking the change to its version, approval, and deploying authority.

This ensures governance changes are auditable. An auditor can reconstruct the full history of policy and risk model changes, including who proposed each change, what evidence supported it, who approved it, and when it was deployed.

---

## 9. Summary

The Governance Learning Protocol allows the system to improve over time while maintaining strict runtime control, auditability, and safety.

Learning improves decisions, but governance controls learning. The learning system operates on historical data, produces recommendations, and submits them to a governance approval process. No learning output affects the runtime without explicit approval. Every governance change is versioned, logged, approved, and recorded in the ledger.

This ensures that the system becomes more effective over time without compromising the safety guarantees of the Governed Execution Protocol.

---

## References

| Document | Path |
|----------|------|
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Governed Corpus | `/spec/governed_corpus.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| Audit Ledger Protocol | `/spec/audit_ledger_protocol.md` |
| Receipt / Attestation Protocol | `/spec/receipt_protocol.md` |
| Reference Architecture | `/spec/reference_architecture.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
