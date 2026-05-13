# Five-Engine Open Protocol Map v0.1

Status Truth Label: draft-preserved  
Maturity: draft architecture / repo-family planning note  
Date: 2026-05-13 MDT  
Repository: bkr1297-RIO/rio-protocol  
Scope: Five-engine architecture, protocol-family mapping, and open-source boundary planning  
Canonical status: Not canonical until explicit source-of-truth promotion  

---

## Purpose

This note maps the emerging five-engine architecture to the current and possible future ONE/RIO/MUSS protocol family.

It does not create any new repository, change any license, promote any draft layer to canonical status, or claim implementation where none exists.

---

## Core five-engine stack

The current architecture can be read as five distinct engines:

| Engine | Core question | Current / likely surface | Current status |
|-------|---------------|--------------------------|----------------|
| Generating Engine | What can be generated, reflected, translated, or proposed? | Bondi/Scribe, language-intake, human-led operating grammar | draft-preserved / prototype-adjacent |
| Governing Engine | What may become consequence? | RIO Protocol | canonical protocol baseline documented |
| Proof Engine | What happened, and how can it be verified? | MUS / receipt protocol / ledger | separate proof primitive exists |
| Witness Engine | What patterns are recurring over time? | MANTIS / observation layer | separate observation layer exists; non-authoritative |
| Oddity Engine | What does not fit, what is rupturing, or what is emerging? | future anomaly/emergence layer | future / not yet implemented |

Compressed:

> Generate. Govern. Prove. Witness. Notice Oddity.

---

## Engine boundaries

### 1. Generating Engine

Function:

- reflects;
- drafts;
- translates;
- structures human expression;
- forms candidate packets;
- proposes options.

Must not:

- authorize consequence;
- silently expand scope;
- treat fluent language as governed intent;
- collapse expression into instruction.

Potential protocol surface:

- `scribe-protocol`
- `bondi-scribe`
- `human-led-operating-grammar`
- language-intake schema or representation-packet schema

Current posture:

- `language-intake-mvp` exists as a language governance prototype.
- `docs/spec/human-led-operating-grammar-v0.1.md` is draft-preserved.

Keeper line:

> Expression is not instruction. Translation is not authorization. Proposal is not approval.

---

### 2. Governing Engine

Function:

- evaluates admissibility;
- applies invariants;
- checks scope, policy, authority, risk, and consequence;
- permits, holds, blocks, clarifies, or denies according to protocol.

Must not:

- invent authority;
- become the human;
- let context expand permission;
- treat connected capability as authorization.

Protocol surface:

- `rio-protocol`

Current posture:

- Canonical RIO protocol baseline is documented in `rio-protocol`.
- Runtime conformance, external validation, and production readiness remain separate claims.

Keeper line:

> Capability is not permission. Execution is not authority.

---

### 3. Proof Engine

Function:

- creates receipts;
- signs receipts;
- writes ledger entries;
- preserves tamper-evident proof;
- enables independent verification.

Must not:

- decide what should happen;
- authorize execution;
- treat receipt language as cryptographic proof;
- convert proof into wisdom, meaning, or identity.

Protocol surface:

- `rio-receipt-protocol`
- future `mus-receipts` naming candidate if split/renamed later

Current posture:

- `rio-receipt-protocol` exists as an MIT proof primitive / receipt engine.
- `rio-protocol` defines proof separation at the protocol level.

Keeper line:

> A model may propose a receipt. Only the receipt engine may issue one.

---

### 4. Witness Engine

Function:

- observes patterns;
- watches drift;
- tracks recurrence;
- supports advisory coherence and review;
- surfaces long-memory signals.

Must not:

- authorize action;
- become a hidden governor;
- silently update authority;
- use observation as permission.

Protocol / repo surface:

- `rio-system`
- MANTIS observation layer

Current posture:

- `rio-system` exists as MIT observation / MANTIS layer.
- MANTIS remains non-authoritative.

Keeper line:

> MANTIS watches recurrence. It does not rule.

---

### 5. Oddity Engine

Function:

- detects anomaly;
- protects novelty;
- notices rupture;
- flags emergence;
- prevents premature flattening into known categories.

Must not:

- declare meaning;
- authorize consequence;
- become prophecy;
- overfit symbolic material;
- replace audit, Sentinel, MANTIS, or RIO.

Potential protocol / repo surface:

- no repo yet;
- possible future MANTIS submodule;
- possible future `oddity-protocol` only if boundary stabilizes;
- possible anomaly/emergence packet schema first.

Current posture:

- future / not yet implemented.
- Preserve as draft/future layer until schema, examples, and relation to MANTIS/Sentinel/RIO are clear.

Keeper line:

> MANTIS watches recurrence. Oddity watches rupture.

---

## Why this may become four or five open surfaces

The five engines do not automatically require five repositories.

A repo should exist only when the engine has a stable authority boundary, distinct license posture, conformance surface, and implementation or protocol audience.

Current and candidate surfaces:

| Surface | Engine | Repo status | Open-source posture |
|--------|--------|-------------|--------------------|
| RIO Protocol | Governing | `rio-protocol` exists | public, All Rights Reserved until future release decision |
| MUS / Receipt Protocol | Proof | `rio-receipt-protocol` exists | MIT |
| MANTIS / Observation Layer | Witness | `rio-system` exists | MIT |
| Scribe / Language Intake | Generating | `language-intake-mvp` exists | public, license cleanup needed |
| Oddity / Emergence Layer | Oddity | no repo | future, not yet implemented |

So the likely count is:

- four current/near-current open-adjacent surfaces if Scribe/Language stabilizes;
- five only if Oddity proves distinct enough to warrant its own protocol/repo rather than living inside MANTIS, Sentinel, or failure-mode review.

Keeper boundary:

> Five engines do not automatically mean five repos. Repos follow stable authority boundaries, not named concepts.

---

## Relationship to existing RIO namespaces

The canonical syscall surface already uses five namespaces:

- `rio.*`
- `sentinel.*`
- `mus.*`
- `ledger.*`
- `mantis.*`

The five-engine map is related but not identical.

| Engine | Closest namespace(s) | Note |
|-------|----------------------|------|
| Generating | not fully captured; adjacent to intake/Scribe | May require separate language/intake surface |
| Governing | `rio.*`, `sentinel.*` | RIO governs; Sentinel enforces invariant/fidelity boundaries |
| Proof | `mus.*`, `ledger.*` | MUS receipts; Ledger preserves |
| Witness | `mantis.*` | Advisory, observation, coherence, learning |
| Oddity | `sentinel.*`, `mantis.*`, future oddity packet | Needs separation from safety/audit and pattern observation |

---

## Open questions

1. Is Oddity an engine, a MANTIS sublayer, a Sentinel trigger class, or a future standalone protocol?
2. Is Scribe/Bondi ready for a protocol surface, or should it remain inside language-intake and Human-Led Operating Grammar for now?
3. Does MUS deserve a renamed repo (`mus-receipts`) later, or should `rio-receipt-protocol` remain the stable public name?
4. When does ONE need a repo: stable environment definition, cell/runtime schema, interface, or conformance surface?
5. When does MUSS need a protocol: personal constitution schema, consent/scope/revocation packet, or broader sovereignty container spec?
6. Where does Chronicle belong: proof explanation, ledger narrative, or separate human-readable history protocol?

---

## Recommended next posture

1. Keep RIO canonical protocol work in `rio-protocol`.
2. Keep receipt/proof primitive work in `rio-receipt-protocol`.
3. Keep MANTIS/observation work in `rio-system`.
4. Keep Scribe/generating-language work as draft-preserved until language packet schemas stabilize.
5. Keep Oddity as future/not-yet-implemented until enough examples, packet semantics, and failure modes are gathered.
6. Do not create new repos solely because an engine is named.

---

## Keeper lines

- Generate. Govern. Prove. Witness. Notice Oddity.
- The model generates. RIO governs. MUS proves. MANTIS witnesses. Oddity protects the strange.
- Five engines do not automatically mean five repos.
- Repos follow authority boundaries, not excitement.
- Oddity may flag the strange. It may not declare what the strange means.
- The proof engine proves events, not meaning.
- The witness engine observes patterns, not permission.

---

## Closing status

This map is draft-preserved. It is a planning aid for review, not a canonical protocol amendment. It should be stress-tested before any engine becomes a new repo, namespace, or conformance surface.
