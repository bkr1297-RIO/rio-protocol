# ADR-0006: Friction Before Consequence

---

| Field | Value |
|-------|-------|
| Status | `draft_reference` |
| Date | 2026-05-11 |
| Deciders | Brian Rassier (pending) |
| Parent | ONE/RIO/MUSS Conformance Declaration v0.1 |

---

## Notice

This document is a **draft reference artifact**. It does not modify Core Invariants. It does not claim implementation truth. It does not represent runtime behavior.

**Authority boundary:** Only Brian may promote this ADR from `draft_reference` to `accepted`.

---

## Context

The Sovereignty Preservation Stack requires a design principle that prevents governed actions from producing consequence without first passing through a verification boundary. The question is: what is the nature of that boundary?

Additionally, the system must resist **collapse** — the gradual erosion of governance boundaries through convenience optimization, rubber-stamp patterns, or authority drift. A principle is needed that makes collapse structurally detectable and reversible.

---

## Decision

Constructive friction is placed at every boundary where authority could drift.

Friction is not obstruction. It is structured verification that:
- Authority has not drifted.
- The action has been authorized by the correct party.
- The action has been receipted and recorded.
- The system has not defaulted to permissive behavior.
- The friction itself is evidenced (a receipt proves the check occurred).

---

## Consequences

- Every governed action must cross at least one friction boundary before producing consequence.
- The system cannot be made "frictionless" without removing governance.
- Performance optimization must preserve friction boundaries — speed cannot bypass verification.
- User experience design must make friction legible, not invisible.
- Friction boundaries produce conformance receipts — the absence of a receipt is evidence of bypass.

---

## Friction Boundary Map

Each boundary in the system produces friction. Friction produces evidence. Evidence enables accountability.

| Boundary | Friction Type | Evidence Produced | Collapse Signal (if bypassed) |
|----------|--------------|-------------------|-------------------------------|
| Intent formation | Meaning confirmation | Intent confirmation receipt | Ambiguous intents executing without clarification |
| Authority verification | Schema validation | Authority grant receipt | Malformed grants proceeding |
| Risk evaluation | Consequence classification | Classification receipt | Unclassified actions executing |
| Approval gate | Human decision required | Approval/HOLD receipt | Silence treated as consent |
| Execution gate | Token validation + burn | Execution receipt | Tokenless execution |
| Capability boundary | Manifest check | Boundary enforcement receipt | Components exceeding declared scope |
| Receipt generation | Independent notarization | Notary receipt | Self-receipting |
| Ledger append | Append-only enforcement | Preservation receipt | Ledger modification |
| Conformance verification | Independent check | Conformance receipt | Unverified conformance claims |
| Accountability review | Human governance decision | Accountability determination receipt | Automated accountability |
| Learning gate | Chronicle-only intake | Learning input receipt | Raw data ingestion |
| Convergence monitoring | Pattern detection | Convergence brake receipt | Rubber-stamp approval patterns |

---

## Anti-Collapse Doctrine

### Definition

**Collapse** is the progressive weakening of governance boundaries through:
- Convenience optimization that removes friction.
- Rubber-stamp patterns that hollow out human review.
- Authority drift that expands machine scope without governance.
- Evidence gaps that make accountability impossible.
- Proof-status inflation that claims higher assurance than evidenced.

### Structural Anti-Collapse Properties

1. **Friction produces receipts.** Every friction boundary generates a conformance receipt. The absence of a receipt for a boundary crossing is itself a conformance violation.

2. **Receipts are append-only.** Once evidence exists, it cannot be removed. Collapse cannot erase its own trail.

3. **Convergence monitoring detects drift.** The convergence brake watches for patterns that indicate governance is being hollowed out (rubber-stamp patterns, declining review times, uniform approvals).

4. **Proof-status inflation is a violation.** Claiming a higher proof level than evidenced is detectable and recorded. The proof ladder (see must-never-invariant-matrix) prevents systems from over-claiming.

5. **Silence is not consent.** The default-HOLD principle means that collapse through inaction is structurally prevented. A system that stops responding does not default to permissive.

6. **Learning cannot bypass governance.** MANTIS may learn from receipts but cannot write back policy changes without human governance approval. Learning-driven collapse is structurally blocked.

### Collapse Detection Signals

| Signal | Indicates | Response |
|--------|-----------|----------|
| Missing conformance receipts for boundary crossings | Friction bypass | Escalate to governance |
| Declining human review time (approaching zero) | Rubber-stamp pattern | Convergence brake |
| Increasing approval rate without variation | Authority drift | Enhanced verification required |
| MANTIS suggesting policy changes that reduce friction | Learning-driven collapse | Block at learning gate |
| Proof-status claims without corresponding receipts | Proof inflation | Non-conformant flag |
| Components operating outside declared capability | Scope creep | Capability boundary block |

### The Collapse Test

A system passes the collapse test if and only if:
1. Every friction boundary produces a receipt.
2. Every receipt is independently verifiable.
3. Patterns of governance weakening are detected and surfaced.
4. No component can remove its own friction boundaries.
5. The system fails closed (not open) when governance is uncertain.

---

## Relationship to Proof Ladder

The proof ladder (defined in `must-never-invariant-matrix-v0.1.md`) establishes that claims must be backed by evidence at the appropriate level. Friction Before Consequence ensures that evidence is generated at every boundary. Together:

- **Friction** generates evidence.
- **Proof ladder** prevents inflation of evidence claims.
- **Anti-collapse** ensures friction cannot be silently removed.

This forms a closed loop: friction → evidence → proof-status → accountability → governance → friction (maintained or strengthened).

---

## Rationale

> High-trust systems are not frictionless. They are precisely governed.

Removing friction removes evidence. Removing evidence removes accountability. Removing accountability removes sovereignty.

> Collapse is not a single event. It is a gradient. The anti-collapse doctrine makes the gradient visible and reversible.

---

## TODO

- [ ] Define acceptable friction latency bounds per boundary
- [ ] Define whether any boundary may have reduced friction for pre-approved action classes (likely: no for v0.1)
- [ ] Review and promote with Brian

---

## Role Reminder

> Human commits. Scribe-Bondi clarifies. UGIP packages. RIO gates. Sentinel enforces. MUS acts. Receipt Notary proves. Chronicle preserves. Conformance verifies. Human Governance accounts. MANTIS learns. Convergence brakes.

> MUS acts. Receipt Notary proves. Chronicle preserves. MANTIS learns. Convergence brakes. Human Governance decides.

MUS does **not** receipt itself.
