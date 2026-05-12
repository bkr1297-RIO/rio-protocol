# ADR-0006: Friction Before Consequence

---

| Field | Value |
|-------|-------|
| Status | `draft_reference` |
| Date | 2026-05-11 |
| Deciders | Brian Rassier (pending) |
| Parent | ONE/RIO/MUSS Conformance Declaration v0.1 |

---

## Context

The Sovereignty Preservation Stack requires a design principle that prevents governed actions from producing consequence without first passing through a verification boundary. The question is: what is the nature of that boundary?

---

## Decision

Constructive friction is placed at every boundary where authority could drift.

Friction is not obstruction. It is structured verification that:
- Authority has not drifted.
- The action has been authorized by the correct party.
- The action has been receipted and recorded.
- The system has not defaulted to permissive behavior.

---

## Consequences

- Every governed action must cross at least one friction boundary before producing consequence.
- The system cannot be made "frictionless" without removing governance.
- Performance optimization must preserve friction boundaries — speed cannot bypass verification.
- User experience design must make friction legible, not invisible.

---

## Rationale

> High-trust systems are not frictionless. They are precisely governed.

Removing friction removes evidence. Removing evidence removes accountability. Removing accountability removes sovereignty.

---

## TODO

- [ ] Link to specific conformance boundaries from the declaration
- [ ] Define acceptable friction latency bounds
- [ ] Define friction bypass conditions (if any — likely none for governed actions)
- [ ] Review and promote with Brian

---

## Role Reminder

> MUS acts. Receipt Notary proves. Chronicle preserves. MANTIS learns. Convergence brakes. Human Governance decides.
