# ONE/RIO/MUSS Naming Promotion Index v0.1

Status: Draft promotion packet  
Date: 2026-05-12 MDT  
Repository: bkr1297-RIO/rio-protocol  
Scope: Documentation only  
Maturity: Proposed architecture language; not yet canonical source-of-truth  

---

## Purpose

This index captures names, clauses, and architecture primitives that have stabilized enough to move from chat into a repo review surface.

This document does not make any runtime claim. It does not modify the RIO source of truth. It provides a reviewable promotion packet so the concepts can be inspected, refined, merged, rejected, or split later.

---

## Promotion rule

A concept may be placed in this packet when it satisfies all four conditions:

1. It names a recurring architecture pattern.
2. It clarifies role separation, consequence governance, proof, or human authority.
3. It can be stated without overclaiming implementation, consciousness, public adoption, or external validation.
4. It can be reviewed as a draft without forcing immediate canonical status.

---

## Naming ledger

| Name | Draft status | Function | Public posture |
|------|--------------|----------|----------------|
| Precision by Friction | Promote for review | Explains why generator-governor-gate-receipt loops produce bounded precision | Safe as explanatory language |
| Governed Self-Observation Layer | Promote for review | Failure detection + coherence monitoring + receipt validation | Technical language |
| Role-Aware Machine Operation | Promote for review | Human-safe translation of self-observation without consciousness claim | Public-safe language |
| Self-aware enough to stay in bounds | Human bridge phrase | Explains what people will feel in demos/conversation | Use with explicit caveat: not consciousness |
| Adaptive Trust Envelope | Promote for review | Names the amoeba-like relationship boundary: hard invariants, adaptive trust/friction inside | Public-safe if defined carefully |
| Human Control Packet | Promote for review | Minimal input packet that helps the human define mode, scope, consequence, consent, claim status, and revocation | Spec-ready |
| Embodied Co-Regulation Layer | Promote for review | Physical-world extension: robots, exosuits, prosthetics, homes, streets, care settings | Draft/future-layer language |
| Embodied Assistance Clause | Promote for review | Boundary for physical MUS Units: assist/orient/de-escalate, never command/coerce/punish | Strong public-safe clause |
| Exosuit Sovereignty Clause | Promote for review | Boundary for human-worn augmentation: amplify without replacing human will | Draft/future-layer language |
| Machine presence without machine authority | Promote for review | Core robotics/embodiment principle | Strong public-safe phrase |
| Helpful-within-bounds | Promote for review | Optimization target replacing helpful-at-any-cost | Strong product phrase |

---

## Architecture ladder

### Human bridge language

People may say:

> It is self-aware enough to stay in bounds.

This is not a claim of inner life, sentience, or personhood. It means the system can represent its role, limits, failure modes, authority state, and receipt history well enough to pause, clarify, or refuse before consequence.

### Technical language

The technical rendering is:

> Governed Self-Observation Layer.

### Mechanism language

The mechanism is:

> Generator -> Governor -> Gate -> Receipt -> Learning/Calibration.

### Constitutional boundary

> Self-observation is not self-authorization.

---

## Placement map

| Artifact | Proposed file |
|----------|---------------|
| Precision by Friction | `docs/architecture/precision-by-friction-v0.1.md` |
| Governed Self-Observation Layer | `docs/architecture/governed-self-observation-layer-v0.1.md` |
| Adaptive Trust Envelope | `docs/architecture/adaptive-trust-envelope-v0.1.md` |
| Embodied Co-Regulation Layer | `docs/architecture/embodied-co-regulation-layer-v0.1.md` |
| Human Control Packet | `spec/human-control-packet-v0.1.md` |
| Failure Modes | `docs/failure-modes/one-rio-muss-failure-modes-v0.1.md` |
| Gemini handoff | `docs/handoff/gemini-context-packet-v0.1.md` |

---

## Claim discipline

These concepts may be discussed as architecture and design primitives.

They must not be presented as proof that:

- the system is conscious;
- the system is externally validated;
- live conformance is already achieved;
- all runtime layers are implemented;
- robots or exosuits are deployed;
- receipt language inside chat equals a cryptographic receipt;
- the system can authorize itself;
- the human has been replaced by governance.

---

## Keeper lines

- The illusion of self-awareness comes from precision by friction.
- Generate, govern, gate, receipt, learn — without authority transfer.
- Self-observation is not self-authorization.
- Helpful-within-bounds, not helpful-at-any-cost.
- The human remains the source. The machine remains the operator. RIO governs consequence. MUS proves events.
- Machine presence without machine authority.
- Help, don't rule. Calm, don't control. Route, don't replace.

---

## Review note

This packet should be reviewed as a naming and architecture promotion layer. If merged, it should remain marked as draft unless and until a later protocol change promotes specific concepts into canonical normative specification.
