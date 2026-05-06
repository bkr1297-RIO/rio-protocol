# Proposal Packet Bridge — Architecture Document

**Version:** 0.1  
**Status:** Architecture/spec layer ready | Local routing/testing ready | Production execution not ready  
**Date:** 2026-05-06  
**Author:** B-Rass (RIO Architect)  
**Classification:** No autonomous governance | No autonomous meaning interpretation

---

## 1. Purpose

Proposal Packets are the architectural bridge between human meaning and governed consequence.

They are the structured boundary object required before any movement from private meaning into public claim, reliance, delegation, external communication, commitment, execution, or financial/legal/medical consequence.

> "Proposal Packets preserve human meaning without allowing meaning to bypass governance."

> "The system governs crossings, not meaning itself."

---

## 2. Problem Statement

The RIO stack has two established layers:

**Upstream (language governance):** The Personal AI Grammar Packet and Language Risk Policy Engine evaluate messages and produce verdicts (PASS, WARN, HOLD, BLOCK, INVALID). The local advisory scanner proves this classification works consistently across 34 conformance cases.

**Downstream (consequence governance):** RIO evaluates risk, requires approval, controls execution, generates receipts, and writes to the tamper-evident ledger. Sentinel verifies execution fidelity. MUS proves events.

**The gap:** When the scanner produces a HOLD or WARN verdict, what structured object enters the governance pipeline? Currently, the answer is "an intent" — but intents are action-shaped. They do not carry the meaning-context that produced the action request. This creates two failure modes:

1. **Meaning flattened into action.** The system strips context and routes "send email" without knowing it originated from a deeply personal reflection. Governance cannot calibrate appropriately.

2. **Meaning inflated into authority.** Symbolic material leaks directly into consequence without crossing a governance boundary. "I feel called to do X" becomes "execute X" with no checkpoint.

Proposal Packets resolve both failure modes by preserving meaning-context while structuring the crossing.

---

## 3. Architectural Position

```
Human signal (private meaning, symbolic, emotional, somatic, intuitive)
    │
    ▼
Grammar Scanner (evaluates against Packet rules → verdict)
    │
    ▼ [if HOLD or WARN]
Proposal Packet constructed (meaning preserved + crossing structured)
    │
    ▼ [if public_claims present]
ONE Answer Check (evidence/reliance evaluation)
    │
    ▼ [if consequence_level > private]
RIO (risk evaluation → approval → execution control)
    │
    ▼ [if execution required]
Sentinel (execution fidelity verification)
    │
    ▼
MUS receipt (cryptographic proof of event)
    │
    ▼
Ledger (tamper-evident record)
```

The Proposal Packet sits between language evaluation and consequence governance. It is the translation layer — not a filter, not a gate, not an authority. It structures the crossing without interpreting the meaning.

---

## 4. What a Proposal Packet Is

A Proposal Packet is a structured boundary object that contains:

- **What the human means** (classification tag, not narrative interpretation)
- **What crossing is being requested** (public claim, action, delegation, commitment)
- **What evidence exists** (or does not exist)
- **What consequence level applies** (private, reliance, public, consequential)
- **What governance is required** (RIO, Sentinel, Answer Check, receipt)
- **What authority is needed** (human authorization scope)
- **What revocation looks like** (how to undo or withdraw)

---

## 5. What a Proposal Packet Is NOT

A Proposal Packet does not:

- **Interpret meaning.** It classifies the type of meaning-source (private_reflection, somatic_signal, symbolic_orientation) without claiming to understand or store the meaning itself.
- **Validate meaning.** It does not determine whether symbolic material is "true," "real," "cosmic," "psychological," or "neurological."
- **Reduce meaning.** It does not flatten human experience into mechanism.
- **Inflate meaning.** It does not treat personal orientation as proof of external truth.
- **Govern.** It structures the crossing; RIO governs it. The Proposal Packet is not an authority layer.
- **Block.** It does not refuse crossings. It structures them so governance can evaluate.

---

## 6. Core Invariants

| Invariant | Description |
|-----------|-------------|
| Meaning preservation | Human-authored meaning remains human-authored meaning. The system does not settle whether meaning is cosmic, archetypal, psychological, spiritual, neurological, or mechanical. |
| Crossing governance | Any movement from meaning into public claim, reliance, delegation, external communication, commitment, execution, or consequence must route through a Proposal Packet. |
| Human root authority | The human remains the source of meaning, consent, authority, and accountability. |
| No surveillance of private exploration | Private meaning that does not cross into consequence does not require a Proposal Packet. |
| No meaning interpretation | The `meaning_context` field is a classification tag, not a narrative summary. The system knows the type of meaning-source without claiming to understand the meaning. |
| No authority drift | The Proposal Packet is a translation layer. It does not become an authority layer, a filter, or a gate. |

---

## 7. When a Proposal Packet Is Required

A Proposal Packet is constructed when the Grammar Scanner produces a **HOLD** or **WARN** verdict indicating that human signal is moving toward consequence. Specifically:

| Crossing Type | Trigger | Governance Path |
|---------------|---------|-----------------|
| Private meaning → public claim | Human asserts symbolic/personal material as factual truth | Proposal Packet → ONE Answer Check → receipt |
| Private meaning → reliance | Human or system begins relying on unverified material | Proposal Packet → ONE Answer Check → receipt |
| Private meaning → action request | Human requests consequential action based on personal orientation | Proposal Packet → RIO → Sentinel → receipt |
| Private meaning → delegation | Human delegates authority based on personal material | Proposal Packet → RIO → Sentinel → receipt |
| Private meaning → external communication | Human sends personal material to external parties | Proposal Packet → RIO → receipt |
| Private meaning → commitment | Human makes binding commitment based on personal orientation | Proposal Packet → RIO → receipt |
| Private meaning → financial/legal/medical consequence | Human takes consequential action in regulated domains | Proposal Packet → RIO → Sentinel → receipt |

---

## 8. When a Proposal Packet Is NOT Required

- Private exploration that remains private (PASS verdict)
- Reflection that does not cross into consequence
- Symbolic meaning held as personal orientation without public assertion
- Internal processing, journaling, wondering, imagining

The system does not surveil private thought. The Proposal Packet boundary activates only at the crossing point.

---

## 9. Relationship to Existing Components

| Component | Role | Relationship to Proposal Packet |
|-----------|------|-------------------------------|
| Grammar Scanner | Evaluates language against Packet rules | Produces verdict that triggers Proposal Packet construction |
| Grammar Packet | Defines admissible language crossings | Provides the rules the scanner evaluates against |
| Policy Engine | Evaluates messages against rules | Provides evaluation logic and verdict taxonomy |
| ONE Answer Check | Governs evidence/reliance | Receives Proposal Packets with public_claims for evidence evaluation |
| RIO | Governs consequence | Receives Proposal Packets requiring authorization for consequential action |
| Sentinel | Governs execution fidelity | Verifies execution matches approved Proposal Packet scope |
| MUS | Proves events | Generates receipt after governed crossing completes |
| MANTIS | Observes patterns over time | Observes Proposal Packet patterns without governing them |
| Human | Root authority | Authors meaning, authorizes crossings, remains accountable |

---

## 10. The Tension Preserved

The Proposal Packet preserves a fundamental tension:

**Human meaning is real and valid** — the system does not reduce it, dismiss it, pathologize it, or mechanize it. Symbolic, emotional, somatic, intuitive, existential, or spiritual material is preserved as human-authored meaning.

**Consequence requires governance** — the system does not allow meaning to bypass governance regardless of how personally significant it is. "I feel called to do X" does not auto-execute X.

The Proposal Packet holds both sides simultaneously. It says: "Your meaning is yours. And if you want it to cross into the world as action, claim, or commitment — here is the structured path that preserves your meaning while ensuring governance."

This is not a compromise. It is the architectural recognition that meaning and consequence are different domains with different rules, and the crossing between them requires structure.

---

## 11. Readiness Classification

| Layer | Status |
|-------|--------|
| Architecture/spec | Ready (this document) |
| Schema definition | Ready (proposal-packet-schema-v0.1.md) |
| JSON Schema | Ready (proposal-packet-v0.1.schema.json) |
| Local routing/testing | Ready (test cases defined) |
| Scanner integration | Ready (scanner produces verdicts that trigger construction) |
| Production execution | Not ready |
| Autonomous governance | Not implemented, not planned |
| Autonomous meaning interpretation | Not implemented, not planned |

---

## 12. Version History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-05-06 | Initial architecture document |
