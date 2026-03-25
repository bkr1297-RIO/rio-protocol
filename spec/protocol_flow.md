# RIO Protocol — Full Protocol Flow Reference

**Version:** 1.0.0
**Status:** Normative
**Type:** Quick Reference

---

## 1. Overview

This document describes the complete RIO Protocol flow from initial request intake to learning feedback. It serves as a concise quick-reference companion to the Orchestration Protocol (14). Each step identifies the responsible protocol, input and output records, success criteria, failure behavior, and timing expectations.

All steps execute sequentially. The orchestrator (Protocol 14) manages state transitions between steps. The system is **fail-closed**: any step failure halts the chain and produces a denial record.

---

## 2. Summary Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     RIO PROTOCOL FLOW                                │
│                                                                      │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐            │
│  │ Step 1   │──▶│ Step 2   │──▶│ Step 3   │──▶│ Step 4   │           │
│  │ INTAKE   │   │ ORIGIN   │   │ CANON.   │   │ RISK     │           │
│  │          │   │ VERIFY   │   │ REQUEST  │   │ EVAL     │           │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘            │
│       │              │              │              │                  │
│       ▼ fail         ▼ fail         ▼ fail         ▼ fail            │
│    [DENIED]       [DENIED]       [DENIED]       [DENIED]             │
│                                                                      │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐            │
│  │ Step 5   │──▶│ Step 6   │──▶│ Step 7   │──▶│ Step 8   │           │
│  │ POLICY   │   │ AUTHZ    │   │ EXECUTE  │   │ ATTEST   │           │
│  │ CHECK    │   │          │   │          │   │          │           │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘            │
│       │              │              │              │                  │
│       ▼ fail         ▼ deny         ▼ fail         ▼ fail            │
│    [DENIED]       [DENIED]       [FAILED]       [FAILED]             │
│                                                                      │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐                           │
│  │ Step 9   │──▶│ Step 10  │──▶│ Step 11  │                          │
│  │ RECEIPT  │   │ LEDGER   │   │ LEARN    │                          │
│  │          │   │          │   │          │                          │
│  └─────────┘   └─────────┘   └─────────┘                           │
│       │              │              │                                 │
│       ▼ fail         ▼ fail         ▼ fail                           │
│    [FAILED]       [FAILED]     [LOGGED]                              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 3. Protocol Flow Steps

### Step 1: Intake

| Attribute | Value |
|-----------|-------|
| **Protocol** | 01 — Intake Protocol |
| **Input** | Raw request from external source (AI agent, automated system, human, delegated process) |
| **Output** | Validated intake record with `request_id` assigned |
| **Success Criteria** | Request is well-formed, all required fields are present, request size is within limits |
| **Failure Behavior** | Reject with `400 Bad Request`. No `request_id` is assigned. Log the rejection. |
| **Timing** | < 100 ms |

### Step 2: Origin Verification

| Attribute | Value |
|-----------|-------|
| **Protocol** | 02 — Origin Verification Protocol |
| **Input** | Intake record with `request_id` |
| **Output** | Origin verification result: verified or rejected |
| **Success Criteria** | Requester identity is authenticated, signature is valid, nonce is unique, timestamp is within skew allowance |
| **Failure Behavior** | Deny. Record denial in ledger. Nonce is NOT consumed on failure. |
| **Timing** | < 200 ms |

### Step 3: Canonical Request Formation

| Attribute | Value |
|-----------|-------|
| **Protocol** | 03 — Canonical Request Protocol |
| **Input** | Verified intake record |
| **Output** | `canonical_request` record (hashable, signable) |
| **Success Criteria** | All 9 required fields populated, `action_type` matches intent ontology, canonical hash computed |
| **Failure Behavior** | Deny. Malformed requests are rejected. Log the failure. |
| **Timing** | < 100 ms |

### Step 4: Risk Evaluation

| Attribute | Value |
|-----------|-------|
| **Protocol** | 04 — Risk Evaluation Protocol |
| **Input** | `canonical_request` |
| **Output** | `risk_evaluation` record with risk_level, risk_score, risk_factors, recommendation |
| **Success Criteria** | Risk score computed (0–100), risk level assigned (low/medium/high/critical), recommendation issued |
| **Failure Behavior** | Deny. If risk engine is unavailable, fail closed — treat as critical risk. |
| **Timing** | < 2 seconds |

### Step 5: Policy Evaluation

| Attribute | Value |
|-----------|-------|
| **Protocol** | 05 — Policy Constraints Protocol |
| **Input** | `canonical_request` + `risk_evaluation` |
| **Output** | Policy evaluation result: list of triggered policies, flags, and constraints |
| **Success Criteria** | All applicable policies evaluated, policy flags generated, authorization requirements determined |
| **Failure Behavior** | Deny. If policy engine is unavailable, fail closed — deny execution. |
| **Timing** | < 1 second |

### Step 6: Authorization

| Attribute | Value |
|-----------|-------|
| **Protocol** | 06 — Authorization Protocol + 15 — Time-Bound Authorization Protocol |
| **Input** | `canonical_request` + `risk_evaluation` + policy flags |
| **Output** | `authorization_record` with decision (approve/deny/approve_with_conditions/expired) |
| **Success Criteria** | Authorized by entity with appropriate role, signature valid, decision recorded, expiration set |
| **Failure Behavior** | Deny. Timeout results in `expired` status. Denial is a valid terminal outcome. |
| **Timing** | Variable — depends on human response. Timeout: configurable (default 300 seconds). |

### Step 7: Execution

| Attribute | Value |
|-----------|-------|
| **Protocol** | 07 — Execution Protocol |
| **Input** | `canonical_request` + `authorization_record` |
| **Output** | `execution_record` with status (success/failed/partial/cancelled) |
| **Success Criteria** | Authorization is valid and not expired, nonce is unused, parameters match authorization, execution completes within envelope constraints |
| **Failure Behavior** | Fail. Record failure in execution record. Do NOT retry without new authorization. |
| **Timing** | Variable — depends on action type. Bounded by execution envelope timeout. |

**Pre-execution gate checks (all MUST pass):**

| Check | Condition |
|-------|-----------|
| Authorization valid | `authorization_record.decision` is `approve` or `approve_with_conditions` |
| Not expired | `current_time < authorization_record.expires_at` |
| Single use | `authorization_id` has not been used for a prior execution |
| Parameter match | Execution parameters match authorized parameters |
| Signature valid | `authorization_record.signature` verifies against public key |

### Step 8: Attestation

| Attribute | Value |
|-----------|-------|
| **Protocol** | 08 — Attestation Protocol |
| **Input** | `canonical_request` + `risk_evaluation` + `authorization_record` + `execution_record` |
| **Output** | `attestation_record` with hashes of all prior records, verification checks, and signatures |
| **Success Criteria** | All record hashes computed and verified, chain integrity confirmed, attestation signed |
| **Failure Behavior** | Fail. If attestation cannot verify the chain, flag the entire decision chain as compromised. |
| **Timing** | < 1 second |

### Step 9: Receipt Generation

| Attribute | Value |
|-----------|-------|
| **Protocol** | Receipt Specification (spec/receipt_spec.md) |
| **Input** | All prior records: `canonical_request`, `risk_evaluation`, `authorization_record`, `execution_record`, `attestation_record` |
| **Output** | `receipt` — human-readable audit summary of the full decision chain |
| **Success Criteria** | All cross-references valid, timeline chronologically ordered, summary generated, receipt signed |
| **Failure Behavior** | Fail. Receipt generation failure does not reverse execution but MUST be flagged as an integrity incident. |
| **Timing** | < 500 ms |

### Step 10: Ledger Recording

| Attribute | Value |
|-----------|-------|
| **Protocol** | 09 — Audit Ledger Protocol |
| **Input** | `receipt` + `attestation_record` |
| **Output** | `ledger_entry` — append-only, hash-linked entry in the tamper-evident ledger |
| **Success Criteria** | Entry hash computed, linked to previous entry via `previous_hash`, entry appended to ledger |
| **Failure Behavior** | Fail. Ledger write failure MUST be retried. If retry fails, halt system and alert operators. Ledger integrity is non-negotiable. |
| **Timing** | < 500 ms |

### Step 11: Learning Feedback

| Attribute | Value |
|-----------|-------|
| **Protocol** | 10 — Learning Protocol |
| **Input** | Completed `receipt` + `ledger_entry` |
| **Output** | Learning events (pattern detection, anomaly detection, recommendations) |
| **Success Criteria** | Decision chain data ingested for analysis. Learning events created if patterns detected. |
| **Failure Behavior** | Log. Learning failure does NOT affect the completed decision chain. The chain is already sealed in the ledger. |
| **Timing** | Asynchronous — no latency requirement for the decision chain. Batch analysis: daily/weekly. Streaming analysis: real-time. |

---

## 4. Timing Summary

| Step | Protocol | Expected Latency | Timeout |
|------|----------|-----------------|---------|
| 1. Intake | 01 | < 100 ms | 5 s |
| 2. Origin Verification | 02 | < 200 ms | 5 s |
| 3. Canonical Request | 03 | < 100 ms | 5 s |
| 4. Risk Evaluation | 04 | < 2 s | 30 s |
| 5. Policy Evaluation | 05 | < 1 s | 10 s |
| 6. Authorization | 06 + 15 | Variable (human) | 300 s (configurable) |
| 7. Execution | 07 | Variable (action) | Per envelope |
| 8. Attestation | 08 | < 1 s | 10 s |
| 9. Receipt | receipt_spec | < 500 ms | 10 s |
| 10. Ledger | 09 | < 500 ms | 30 s |
| 11. Learning | 10 | Async | None |

**Typical end-to-end latency (excluding human authorization):** < 6 seconds.
**Typical end-to-end latency (including human authorization):** 30 seconds to 5 minutes.

---

## 5. Cross-Cutting Protocols

The following protocols are not sequential steps but apply across the entire flow:

| Protocol | Number | Role |
|----------|--------|------|
| Independence | 11 | Ensures no component can override another's decision |
| Role Separation | 12 | Ensures no entity performs conflicting roles in the same chain |
| Meta-Governance | 13 | Ensures changes to the protocol itself require authorization |
| Orchestration | 14 | Manages the state machine and step sequencing |

---

## 6. Failure Modes Summary

| Failure Type | Behavior | Record Created |
|-------------|----------|----------------|
| Malformed request | Reject at intake | Rejection log |
| Invalid origin | Deny at Step 2 | Denial record + ledger entry |
| Risk engine unavailable | Deny (fail closed) | Denial record + ledger entry |
| Policy engine unavailable | Deny (fail closed) | Denial record + ledger entry |
| Authorization denied | Terminal denial | Denial receipt + ledger entry |
| Authorization expired | Terminal expiration | Expiration receipt + ledger entry |
| Execution failure | Record failure | Failure receipt + ledger entry |
| Attestation failure | Flag as compromised | Incident record + ledger entry |
| Ledger write failure | Retry, then halt | System alert |
| Learning failure | Log and continue | Error log (chain unaffected) |

---

## 7. Dependencies

| Document | Relationship |
|----------|-------------|
| Orchestration Protocol (14) | Manages the state machine for this flow |
| Protocol State Machine (spec/protocol_state_machine.md) | Formal state definitions and transitions |
| System Invariants (spec/system_invariants.md) | Properties that must hold at every step |
| Execution Envelope (spec/execution_envelope.md) | Bounds for Step 7 execution |
| All 15 Protocol Specs (spec/01–15) | Detailed specification for each step |
