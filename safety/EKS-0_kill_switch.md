# EKS-0: Global Execution Kill Switch

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Safety Mechanism

---

## 1. Purpose

EKS-0 is a global execution halt mechanism that overrides normal authorization and execution behavior within the Governed Execution Protocol. When engaged, no new executions may proceed regardless of policy decisions, risk evaluations, or valid authorization tokens. EKS-0 is the protocol's last line of defense — a manual or automated circuit breaker that stops all consequential actions immediately.

---

## 2. Behavior

### 2.1 When Engaged

When EKS-0 is engaged, the following behavior MUST be enforced:

| Behavior | Description |
|----------|-------------|
| All pending executions are blocked | Any request that has received authorization but has not yet been executed MUST be denied at the Execution Gate |
| All new executions are blocked | Any new request arriving at the Execution Gate MUST be denied |
| Receipts are still generated | Every blocked request MUST produce a signed receipt with the block reason `kill_switch_engaged` |
| Ledger entries are still written | Every blocked request MUST produce an append-only ledger entry recording the kill switch event |
| Stages 1–4 continue to operate | Intake, Classification, Structured Intent, and Policy & Risk continue to process requests normally so that the system maintains awareness of incoming demand |
| Authorization may still be issued | Stage 5 (Authorization) may still issue tokens, but those tokens will be blocked at Stage 6 (Execution Gate) |

### 2.2 When Disengaged

When EKS-0 is disengaged, normal protocol behavior resumes:

| Behavior | Description |
|----------|-------------|
| New requests proceed normally | Requests arriving at the Execution Gate are evaluated against their authorization tokens as usual |
| Previously blocked requests do NOT auto-resume | Requests that were blocked by the kill switch MUST be re-submitted. Authorization tokens that expired during the kill switch period are invalid. |
| Disengagement event is logged | The disengagement MUST produce a receipt and ledger entry |

---

## 3. Engagement Triggers

EKS-0 MAY be engaged by:

| Trigger | Type | Description |
|---------|------|-------------|
| Manual engagement by authorized operator | Human | An operator with the `kill_switch_operator` role explicitly engages EKS-0 |
| Automated engagement by anomaly detection | System | The runtime detects a condition that exceeds a predefined safety threshold (e.g., burst of high-risk requests, hash chain integrity failure, repeated authorization failures) |
| Governance directive | Governance | The governance authority issues a directive to halt all executions (e.g., during an incident investigation) |

---

## 4. Engagement Record

Every engagement and disengagement of EKS-0 MUST produce a record:

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | string (UUID v4) | Unique identifier for this kill switch event |
| `event_type` | string | `engaged` or `disengaged` |
| `triggered_by` | string (DID or system ID) | Identity of the entity or system that triggered the event |
| `trigger_reason` | string | Human-readable reason for engagement or disengagement |
| `trigger_type` | string | `manual`, `automated`, or `governance` |
| `timestamp` | string (ISO 8601) | When the event occurred |
| `affected_requests` | integer | Number of pending requests blocked at the time of engagement |
| `signature` | string (base64) | Cryptographic signature over the event record |

---

## 5. Authorization Requirements

| Action | Required Role | Required Authorization |
|--------|--------------|----------------------|
| Engage EKS-0 (manual) | `kill_switch_operator` | Single authorized operator; no dual-authorization required (speed is critical) |
| Disengage EKS-0 | `kill_switch_operator` | Dual authorization required (two distinct operators must approve disengagement) |
| Engage EKS-0 (automated) | System | No human authorization required; the system acts on predefined thresholds |

The asymmetry is intentional: engaging the kill switch is a safety action that must be fast. Disengaging the kill switch is a resumption of operations that requires deliberate confirmation from two independent operators.

---

## 6. Invariant Enforcement

EKS-0 enforces the following protocol invariant:

> **INV-08:** When the kill switch (EKS-0) is engaged, the Execution Gate MUST deny all pending and new execution requests regardless of their authorization status. Kill switch events MUST still produce receipts and ledger entries.

---

## 7. Test Coverage

See `/tests/TC-RIO-003.md` for the test case that verifies kill switch behavior.

---

## 8. Dependencies

| Document | Relationship |
|----------|-------------|
| Governed Execution Protocol | EKS-0 overrides the Execution Gate (Stage 6) |
| Protocol Invariants (INV-08) | EKS-0 is the enforcement mechanism for INV-08 |
| Audit Ledger Protocol (09) | Kill switch events are recorded in the ledger |
| Receipt Specification | Blocked requests produce receipts with `kill_switch_engaged` reason |
| Role Model | `kill_switch_operator` role is defined in the role model |
