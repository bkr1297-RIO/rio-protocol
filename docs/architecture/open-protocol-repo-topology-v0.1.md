# Open Protocol Repo Topology v0.1

Status: draft_topology_note  
Date: 2026-05-12 MDT  
Scope: Repository strategy / open protocol boundary planning  
Canonical status: Not canonical until Brian Commit / later source-of-truth promotion  
Repository: bkr1297-RIO/rio-protocol  

---

## Purpose

This note captures the emerging repo topology for ONE/RIO/MUSS as an ecosystem of related protocols, runtimes, proof layers, observation layers, and future open-source surfaces.

It does **not** create any new repositories.

It defines when a concept is mature enough to become a repository and what role each repository should play.

---

## Current known repo posture

The current repo/license matrix already establishes an important principle:

- `rio-protocol` is the canonical protocol spec repo.
- `rio-receipt-protocol` is the proof primitive / receipt engine.
- `rio-system` is the observation / MANTIS layer.
- `language-intake-mvp` is the language governance prototype.
- `rio-proxy` is a private governed execution runtime implementation.
- public visibility does not equal open-source permission unless a license grants it.

This topology note should be read alongside `REPO-LICENSE-MATRIX.md`.

---

## Core repo principle

> Repositories should map to authority boundaries, not just feature names.

A new repo is justified when a component has:

1. a distinct role boundary;
2. a distinct license posture;
3. a distinct implementation or conformance surface;
4. a distinct audience;
5. enough stability that isolation reduces confusion instead of increasing it.

---

## Current architecture organs

| Organ / layer | Function | Current likely repo surface |
|--------------|----------|-----------------------------|
| RIO | Governance protocol for consequence and admissible action | `rio-protocol` |
| MUS | Receipt/proof primitive | `rio-receipt-protocol` |
| MANTIS | Observation, pattern-awareness, non-authoritative monitoring | `rio-system` |
| Bondi / Scribe | Language translation and intent structuring | `language-intake-mvp` or future Scribe repo |
| ONE | Human-led operating environment / workspace / cell runtime | Future ONE repo candidate |
| MUSS | Sovereignty container: authority, consent, scope, revocation, memory/proof requirements | Future MUSS protocol repo candidate |
| Sentinel / PEP | Execution-fidelity gate / policy enforcement point | May live in `rio-protocol`, `rio-proxy`, or future enforcement repo depending on maturity |
| Chronicle | Human-readable explanation/history layer | Future doc/runtime module; not yet implemented |
| Embodied Co-Regulation | Robots, exosuits, prosthetics, home/community physical MUS Units | Future protocol pack, not repo yet |
| Human-Led Operating Grammar | Translation grammar across all layers | Documentation/spec layer first, not repo yet |

---

## Candidate future repositories

These are candidates, not creation instructions.

| Candidate repo | Possible role | Open-source posture | Create only when... |
|---------------|---------------|--------------------|---------------------|
| `one-protocol` | Defines ONE as human-led operating environment / cell runtime grammar | Likely open spec, license TBD | ONE has a stable operating model, boundaries, and conformance language |
| `one-runtime` | Reference implementation of ONE workspace/cell runtime | Possibly private first, open later | Runtime exists beyond docs and should be separated from RIO protocol |
| `muss-protocol` | Consent, scope, revocation, personal constitution, sovereignty container | Open protocol candidate | MUSS fields and schemas stabilize enough for external implementers |
| `scribe-protocol` or `bondi-scribe` | Language intake, representation packets, translation grammar | Open or mixed | Language governance has a stable packet/schema surface |
| `sentinel-gate` | Policy enforcement point / execution fidelity gate reference | Open reference or private runtime | Enforcement behavior can be generalized without exposing private runtime |
| `chronicle-protocol` | Human-readable narrative history layer | Open protocol candidate | Chronicle is specified enough to avoid proof/wisdom collapse |
| `embodied-co-regulation-protocol` | Physical MUS Unit rules for robots/exosuits/prosthetics/community systems | Draft/open protocol later | Safety, liability, privacy, and local governance boundaries are clearer |
| `human-led-operating-grammar` | Educational/spec bridge for non-collapse rules | Possibly docs-only repo later | It becomes useful as a standalone teaching/standardization artifact |
| `creation-trust-protocol` | Economic stewardship layer for generated value | Separate, not core runtime | Economic model is mature and legally reviewed |

---

## What should **not** become a new repo yet

Do not create a new repo yet for:

- every newly named concept;
- poetic/private origin language;
- future robotics deployment claims;
- Creation Trust until legal/economic posture is clearer;
- Chronicle until proof/person/wisdom boundaries are specified;
- Human-Led Operating Grammar until it is clear whether it belongs as a protocol, appendix, or public education layer.

---

## ONE repo decision

A separate ONE repo likely becomes appropriate when ONE has at least one of these:

1. a stable public definition as an operating environment;
2. a cell/runtime schema;
3. a user-facing workspace implementation;
4. a conformance or interoperability claim distinct from RIO;
5. a need to coordinate multiple protocols under one environment.

Until then, ONE material can remain in `rio-protocol` as architecture documentation or in a private working repo.

Suggested eventual split:

```text
one-protocol       = environment / cell grammar / interface spec
rio-protocol       = consequence governance / admissibility / conformance
muss-protocol      = sovereignty container / consent / scope / revocation
mus-receipts       = proof primitive / receipt engine
rio-system         = observation / MANTIS / non-authoritative monitoring
language-intake    = Scribe/Bondi translation / representation packets
rio-proxy          = private governed execution runtime implementation
```

---

## Open-source protocol family

The system may eventually contain several open or open-adjacent protocols:

| Protocol | Core question |
|----------|---------------|
| RIO Protocol | What may become consequence? |
| MUS Receipt Protocol | What happened, and how is it proved? |
| MUSS Protocol | Who has authority, consent, scope, revocation, and memory boundary? |
| ONE Protocol | Where does human-led machine operation occur? |
| Scribe/Bondi Protocol | How does human language become structured intent without becoming authority? |
| Sentinel Gate Protocol | Does execution match what was authorized? |
| Chronicle Protocol | How is proof explained without becoming meaning? |
| Embodied Co-Regulation Protocol | How do physical machines assist without becoming authority? |
| Creation Trust Protocol | How is generated value stewarded without replacing human capability? |

---

## Repo creation checklist

Before creating a new repo, answer:

1. What authority boundary does this repo protect?
2. What is the canonical object or schema?
3. What is explicitly out of scope?
4. What license applies?
5. Is this public, private, or staged private-to-public?
6. Is it docs-only, reference implementation, runtime, or conformance suite?
7. Does it duplicate an existing repo?
8. What repo remains canonical if two artifacts conflict?
9. What does this repo prove?
10. What does this repo **not** prove?

---

## Recommended immediate posture

For now:

1. Keep RIO canonical protocol work inside `rio-protocol`.
2. Keep receipt/proof engine work inside `rio-receipt-protocol`.
3. Keep observation/MANTIS work inside `rio-system`.
4. Keep execution runtime/private MVP work inside `rio-proxy` or private implementation repos.
5. Add draft architecture concepts to `rio-protocol` as review packets until their repo boundary is stable.
6. Do not create a new ONE repo until ONE has a stable charter, schema, or runtime surface.
7. Do not create a Creation Trust repo until the economic/legal posture is clearer.

---

## Keeper lines

- Repositories should map to authority boundaries, not just feature names.
- Public does not mean open source.
- A repo is not a concept container; it is a boundary and proof surface.
- ONE may become its own repo when its operating-environment boundary is stable.
- Several open protocols may emerge, but each must protect a distinct crossing.

---

## Status note

This is a topology note only. It does not create repositories, change licenses, promote concepts to canonical status, or modify the current source-of-truth hierarchy.
