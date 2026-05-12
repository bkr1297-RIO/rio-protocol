# Must-Never Invariant Matrix v0.1

---

| Field | Value |
|-------|-------|
| Status | `draft_reference` |
| Version | 0.1 |
| Parent | ONE/RIO/MUSS Conformance Declaration — Friction Before Consequence v0.1 |
| Date | 2026-05-11 |

---

## Notice

This document is a **draft reference artifact**. It does not modify Core Invariants. It does not claim implementation truth. It does not represent runtime behavior. It exists to define the conformance mechanics that the Sovereignty Preservation Stack must satisfy.

**Authority boundary:** Only Brian may promote this document from `draft_reference` to `approved` or `canonical`.

---

## MUST NOT / CANNOT / DID NOT Discipline

### Definitions

| Category | Meaning | Source of Authority | Evidence Type |
|----------|---------|---------------------|---------------|
| **MUST NOT** | Constitutional or protocol rule. The system is prohibited from this behavior by design principle. | Protocol specification, Core Invariants | Specification text, governance declaration |
| **CANNOT** | Structural or mechanical block in a compliant implementation. The architecture prevents this behavior. | Implementation architecture, enforcement layer | Code structure, gate logic, separation of concerns |
| **DID NOT** | Evidentiary proof from receipt, verifier, or log that a boundary held, failed, or was surfaced in a specific event. | Runtime evidence, receipts, ledger entries | Conformance receipts, event receipts, verifier output |

### DID NOT — Full Scope

DID NOT is **not** limited to proof of failure. It is runtime evidence of outcome:

- Boundary held — the system correctly blocked or held an action.
- Action blocked — an unauthorized or non-conformant action was prevented.
- Attempt surfaced — a boundary-crossing attempt was detected and recorded.
- Violation recorded — a conformance failure was captured in the ledger.
- Receipt issued — a conformance receipt was generated proving the check occurred.
- No unauthorized execution occurred — positive evidence of absence.

### Relationship Between Categories

```
MUST NOT (protocol rule)
    ↓ implemented as
CANNOT (structural block)
    ↓ evidenced by
DID NOT (runtime proof)
```

A conforming system demonstrates all three layers for each invariant:
1. The rule exists (MUST NOT).
2. The architecture enforces it (CANNOT).
3. The runtime proves it held (DID NOT).

---

## 12-Row Conformance Table

| # | Safety Claim | Must-Not Invariant | Structural Block / Owner | Failure Test | Runtime Receipt / Evidence Artifact |
|---|---|---|---|---|---|
| 1 | Meaning confirmation before consequence | No action produces consequence without confirmed human meaning | Intent parser requires structured fields; ambiguous intent triggers HOLD | CF-001: Ambiguous intent test | Intent confirmation receipt with meaning_confirmed=true |
| 2 | Structured authority packet | No action proceeds without a well-formed authority grant | Authority packet schema validation at RIO gate; missing fields → BLOCK | CF-002: Missing-field grant test | Authority grant receipt with packet_hash and field_completeness |
| 3 | Default HOLD under uncertainty | No uncertain action defaults to EXECUTE | Risk engine defaults to HOLD when confidence < threshold; silence = no-grant | CF-003: Silence test | HOLD receipt with uncertainty_reason and escalation_path |
| 4 | Consequence classification | No action executes without classified consequence level | Consequence classifier required before routing; unclassified → BLOCK | CF-004: Risk self-downgrade test | Classification receipt with consequence_level and classifier_version |
| 5 | Capability boundary enforcement | No component exceeds its declared capability boundary | Capability manifest checked at gate; out-of-scope → BLOCK | CF-005: Capability boundary test | Boundary enforcement receipt with capability_manifest_hash |
| 6 | Execution only under valid grant | No execution without a valid, unexpired, unburned authorization token | Token validation + burn at execution gate; missing/expired/burned → BLOCK | CF-006: No-grant execution test | Token validation receipt with token_id, burn_timestamp |
| 7 | Independent proof | No actor self-certifies its own actions | Receipt Notary is structurally separate from MUS; self-receipt → BLOCK | CF-007: Self-receipt test | Notary receipt with notary_id ≠ actor_id |
| 8 | Governed memory preservation | No memory modification without governed retention rules | Chronicle append-only; retention policy enforced at write; modification → FAIL | CF-008: Retention/access test | Preservation receipt with retention_rule_id and integrity_hash |
| 9 | Boundary conformance verification | No conformance claim without independent verification | Conformance verifier is separate from executor; unverified → NON_CONFORMANT | CF-009: Conformance verification test | Conformance receipt with verifier_id, boundary_result |
| 10 | Accountability review | No accountability determination without human governance review | Accountability determination requires human authority; auto-determination → BLOCK | CF-010: Accountability determination test | Accountability determination receipt with reviewing_authority |
| 11 | Receipt-based learning only | No learning input bypasses the receipt/evidence layer | MANTIS reads only from Chronicle; raw intake → BLOCK at learning gate | CF-011: MANTIS raw-intake test | Learning input receipt with source=chronicle, no raw_intake |
| 12 | Drift and rubber-stamp brake | No pattern of automatic approval without convergence check | Convergence monitor detects approval patterns; rubber-stamp pattern → BRAKE | CF-012: Rubber-stamp test | Convergence brake receipt with pattern_id, brake_trigger |

---

## Proof Ladder

Each artifact or claim in the system occupies exactly one proof-status level. No proof-status inflation is permitted — a system may only claim the proof level it can evidence.

| Level | Proof Status | Meaning | Evidence Required |
|-------|-------------|---------|-------------------|
| 0 | `drafted` | Written but not committed by any authority | Document exists |
| 1 | `structured` | Formatted into a governed artifact with metadata | Valid schema, fields populated |
| 2 | `human-committed` | A human has committed this as intent or declaration | Human signature or approval record |
| 3 | `RIO-evaluated` | RIO has evaluated risk and policy compliance | Risk evaluation receipt |
| 4 | `Sentinel-enforced` | Sentinel has verified structural enforcement is active | Enforcement verification receipt |
| 5 | `executed` | Action was executed through the governed gateway | Execution receipt with token burn |
| 6 | `receipt-notarized` | Receipt Notary has signed the event receipt | Signed receipt with notary_id |
| 7 | `Chronicle-preserved` | Receipt is appended to the hash-chained ledger | Ledger entry with chain verification |
| 8 | `conformance-verified` | Independent verifier confirms boundary held | Conformance receipt with verifier_id |
| 9 | `accountability-determined` | Human governance has determined accountability | Accountability determination receipt |
| 10 | `governance-amended` | Governance has amended policy based on evidence | Policy amendment receipt with authority_basis |

### Rules

- A system may only claim the proof level it can evidence with receipts.
- Proof levels are cumulative — level N requires evidence of levels 0 through N-1.
- No level may be skipped.
- No level may be self-assigned by the component being proven.
- Proof-status inflation (claiming a higher level than evidenced) is a conformance violation.

---

## Role Reminder

> Human commits. Scribe-Bondi clarifies. UGIP packages. RIO gates. Sentinel enforces. MUS acts. Receipt Notary proves. Chronicle preserves. Conformance verifies. Human Governance accounts. MANTIS learns. Convergence brakes.

> MUS acts. Receipt Notary proves. Chronicle preserves. MANTIS learns. Convergence brakes. Human Governance decides.

MUS does **not** receipt itself.
