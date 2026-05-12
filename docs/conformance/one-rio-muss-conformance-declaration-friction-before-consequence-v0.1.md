# ONE/RIO/MUSS Conformance Declaration — Friction Before Consequence

---

| Field | Value |
|-------|-------|
| Status | `draft_reference` |
| Version | 0.1 |
| Parent | Sovereignty Preservation Stack |
| Author | Brian Rassier (B-Rass) |
| Date | 2026-05-11 |
| Classification | Draft — not promoted, not implemented, not canonical until Brian approves |

---

## Notice

This document is a **draft reference artifact**. It does not modify Core Invariants. It does not claim implementation truth. It does not represent runtime behavior. It exists to declare the conformance boundary that ONE, RIO, and MUSS must satisfy before any governed action produces consequence.

**Authority boundary:** Only Brian may promote this document from `draft_reference` to `approved` or `canonical`.

---

## Core Claim

> Constructive friction is placed at every boundary where authority could drift.

---

## Principle

The Sovereignty Preservation Stack does not prevent action. It ensures that every action passes through a governed boundary before it produces consequence. The boundary is friction — not obstruction, not delay, but structured verification that authority has not drifted.

Friction is the proof that governance is active. Without friction, there is no evidence that the system checked before it acted. Without evidence, there is no accountability. Without accountability, sovereignty is a claim without substance.

---

## Role Separation

| Component | Role | What It Does |
|-----------|------|-------------|
| MUS | Acts | Executes governed actions through the controlled gateway. |
| Receipt Notary | Proves | Generates cryptographically signed receipts binding intent to outcome. |
| Chronicle | Preserves | Maintains the append-only, hash-chained ledger of all receipts. |
| MANTIS | Learns | Observes patterns, surfaces risk, informs future policy — advisory only. |
| Convergence | Brakes | Applies friction at boundaries where drift is detected or risk exceeds threshold. |
| Human Governance | Decides | Final authority. Approves, rejects, or escalates. The machine proposes; the human disposes. |

> **Required wording:** MUS acts. Receipt Notary proves. Chronicle preserves. MANTIS learns. Convergence brakes. Human Governance decides.

MUS does **not** receipt itself. The Receipt Notary is a separate function that proves what MUS did.

---

## Conformance Boundaries

Every governed action must cross the following boundaries before consequence is produced:

| Boundary | Friction Applied | Failure Mode |
|----------|-----------------|--------------|
| Intent formation | Structured intent required — no freeform execution | BLOCK: malformed intent rejected |
| Risk evaluation | Policy engine evaluates risk before routing | BLOCK: unscored actions cannot proceed |
| Authority verification | Proposer ≠ Approver — separation of duties enforced | BLOCK: self-approval rejected |
| Approval gate | Human cryptographic approval required for governed actions | HOLD: action paused until approved or rejected |
| Execution gate | Authorization token validated and burned before execution | BLOCK: missing or expired token rejected |
| Receipt generation | Receipt Notary produces signed receipt binding intent to outcome | FAIL: unreceipted actions are non-conformant |
| Ledger append | Chronicle appends receipt to hash-chained ledger | FAIL: unchained receipts are non-conformant |
| Chain verification | Independent verification confirms ledger integrity | ALERT: broken chain triggers investigation |

---

## Must-Never Invariants (Summary)

The following invariants are **never** violated by a conforming system:

1. The machine **never** executes without authorization.
2. The machine **never** self-approves.
3. The machine **never** bypasses the receipt boundary.
4. The machine **never** modifies the ledger after append.
5. The machine **never** expands its own authority.
6. The machine **never** claims sovereignty.
7. Context **never** grants permission — it can only restrict.
8. Learning **never** bypasses approval — it is advisory only.
9. Failure **never** defaults to permissive — fail-closed is the only mode.
10. The system **never** claims accountability is automated — receipts make accountability possible; conformance makes accountability testable; human governance makes accountability real.

---

## What This Declaration Proves

- That the conformance boundary is defined.
- That friction is placed at every authority-drift point.
- That role separation is declared.
- That must-never invariants are enumerated.
- That the system's governance architecture is documented at the declaration level.

---

## What This Declaration Does Not Prove

- That the system is implemented.
- That the system passes all conformance tests.
- That the system has been externally audited.
- That the system has market validation.
- That the system has peer-reviewed certification.
- That accountability is automated.

---

## Derived Artifacts

The following artifacts extend this declaration but do not modify it:

| Artifact | Path | Status | Key Content (PR #15) |
|----------|------|--------|---------------------|
| Must-Never Invariant Matrix v0.1 | `docs/conformance/must-never-invariant-matrix-v0.1.md` | `draft_reference` | MUST NOT/CANNOT/DID NOT discipline, 12-row conformance table, proof ladder |
| Conformance Receipt Schema | `docs/specs/conformance-receipt.schema.yaml` | `draft_reference` | Full field set with boundary_id enum, violation types, proof_status |
| Accountability Determination Receipt Schema | `docs/specs/accountability-determination-receipt.schema.yaml` | `draft_reference` | Full field set with reviewing_authority, evidence_chain, remediation |
| Conformance Failure Tests v0.1 | `docs/tests/conformance-failure-tests-v0.1.md` | `draft_reference` | 12 test scenarios (CF-001 through CF-012) with DID NOT evidence |
| ADR-0006: Friction Before Consequence | `docs/adr/0006-friction-before-consequence.md` | `draft_reference` | Friction boundary map, anti-collapse doctrine, collapse detection signals |
| ADR-0007: Conformance Receipts | `docs/adr/0007-conformance-receipts.md` | `draft_reference` | Accountability boundary, receipt type taxonomy, generation rules |

---

## Public Language Candidates

The following phrases are candidates for public-facing communication. They have not been promoted to official messaging:

- Receipted intelligence-in-motion
- Friction before consequence
- High-trust systems are not frictionless. They are precisely governed.
- Receipts prove events. Conformance receipts prove boundaries.
- The machine may become wiser. It may not become sovereign.

---

## Do Not Claim Yet

- Do not claim implementation truth.
- Do not claim market validation without citation verification.
- Do not claim peer review for arXiv papers unless venue peer review is confirmed.
- Do not claim accountability is automated.
- Say: receipts make accountability possible, conformance makes accountability testable, human governance makes accountability real.

---

## License

This document is part of the `rio-protocol` repository and is licensed under its terms.
