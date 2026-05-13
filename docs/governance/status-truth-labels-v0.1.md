# Status Truth Labels v0.1

Status: draft-preserved candidate  
Date: 2026-05-13 MDT  
Repository: bkr1297-RIO/rio-protocol  
Scope: Documentation/governance only  
Canonical status: Not canonical until explicit source-of-truth promotion  

---

## Purpose

Status Truth Labels define how ONE/RIO/MUSS artifacts, repos, protocols, claims, features, and roadmap items must identify their current truth condition.

The purpose is to prevent status drift, overclaiming, and accidental promotion from idea to implementation or from draft to canonical source-of-truth.

---

## Core rule

> Every artifact must show its truth condition before it shows its ambition.

Operational form:

> No artifact may be interpreted without its status label.

---

## The three labels

| Label | Meaning | What it allows | What it does not allow |
|------|---------|----------------|------------------------|
| canonical | Current source-of-truth or governing baseline | May be cited as current governing reference | Does not imply production readiness, external validation, or implementation unless separately stated |
| draft-preserved | Saved or merged for review, but not source-of-truth | May be reviewed, amended, split, stress-tested, or promoted later | Must not be treated as governing law, implemented runtime, or external validation |
| future / not yet implemented | Named, envisioned, or roadmap-level only | May guide exploration, planning, or boundary design | Must not be claimed as built, enforced, deployed, validated, or canonical |

---

## Why this exists

ONE/RIO/MUSS contains multiple kinds of artifacts:

- canonical protocol specs;
- merged draft-review docs;
- prototype implementations;
- private formation language;
- future robotics/embodiment concepts;
- connector governance drafts;
- conformance plans;
- receipt language;
- roadmap items;
- repository topology proposals.

Without explicit status labels, the system can collapse:

```text
named -> built
merged -> canonical
draft-preserved -> implemented
implemented -> externally validated
future layer -> current runtime
receipt language -> cryptographic receipt
public repo -> open-source permission
```

Status Truth Labels prevent those collapses.

---

## Required use

Every substantial artifact should declare one of the three labels near the top:

```text
Status Truth Label: canonical | draft-preserved | future / not yet implemented
```

If more precision is useful, a secondary maturity label may be added:

```text
Maturity: idea | draft | prototype | implemented | verified | deployed | externally_validated
```

But the primary status truth label must stay visible.

---

## Label definitions

### canonical

Use `canonical` only when the artifact is part of the current source-of-truth hierarchy.

Canonical means:

- governing baseline;
- current reference standard;
- source against which implementation or claims may be compared;
- overrides draft-preserved material where conflict exists.

Canonical does not automatically mean:

- production-ready;
- externally validated;
- fully implemented;
- legally approved;
- open source;
- public standard;
- complete.

Example:

```text
Status Truth Label: canonical
Maturity: documented protocol baseline
```

---

### draft-preserved

Use `draft-preserved` when an artifact has been saved, merged, or filed for review but has not been promoted into source-of-truth.

Draft-preserved means:

- inspectable;
- versioned;
- reviewable;
- available for stress testing;
- available for later promotion, revision, split, or rejection.

Draft-preserved does not mean:

- canonical;
- implemented;
- enforced;
- validated;
- deployed;
- externally approved.

Example:

```text
Status Truth Label: draft-preserved
Maturity: merged draft-review artifact
```

Keeper line:

> Merged into the repo does not mean promoted to source-of-truth. It means preserved for governed review.

---

### future / not yet implemented

Use `future / not yet implemented` when a concept is named, envisioned, or planned but not currently built, enforced, verified, or deployed.

Future/not yet implemented means:

- useful for roadmap and boundary thinking;
- may be used to test architecture against future conditions;
- must be claim-disciplined;
- should not be sold or represented as current capability.

Future/not yet implemented does not mean:

- current runtime;
- deployed product;
- validated safety system;
- existing connector behavior;
- implemented robotics/exosuit layer;
- external standard.

Example:

```text
Status Truth Label: future / not yet implemented
Maturity: future-layer concept
```

---

## Status label decision table

| Question | If yes | Label |
|---------|--------|-------|
| Is this part of the current source-of-truth hierarchy? | yes | canonical |
| Was this merged or saved for review but not promoted? | yes | draft-preserved |
| Is this named as a possible future layer but not built/enforced? | yes | future / not yet implemented |
| Is this implemented in a private runtime but not canonical? | maybe | draft-preserved + maturity: prototype/implemented |
| Is this only in conversation and not saved? | no repo label yet | use draft language only |
| Is this externally certified or validated? | only if evidence exists | add maturity: externally_validated |

---

## Interaction with source-of-truth

If a draft-preserved artifact conflicts with a canonical artifact, the canonical artifact governs.

If a future/not-yet-implemented artifact conflicts with a canonical artifact, the future artifact must be revised, held, or explicitly marked as speculative.

No artifact may promote itself to canonical status.

Canonical promotion requires an explicit human-authorized governance action and source-of-truth update.

---

## Interaction with repo topology

Status labels should be used alongside the repo maturity path:

```text
Named -> Scoped -> Prototype -> Stable Boundary -> Own Repo
```

Status Truth Labels answer:

> What is true about this artifact now?

Repo maturity answers:

> Is this boundary stable enough to deserve its own proof surface?

These are related but not identical.

---

## Interaction with connector governance

Connector status must distinguish:

- connected;
- available to session;
- tool-capable;
- authorized for task;
- executed;
- receipted.

Connector keeper line:

> Connected is not authorized. Authorized is not executed. Executed is not receipted.

---

## Interaction with receipt language

Receipt language must distinguish:

- draft receipt language;
- proposed receipt;
- local receipt;
- signed receipt;
- ledgered receipt;
- verified receipt.

Keeper line:

> Chat receipt language is not a cryptographic receipt.

---

## Recommended immediate use

Apply Status Truth Labels during the next review pass to:

1. PR #17 draft promotion artifacts;
2. PR #18 merge receipt/status note;
3. repo topology notes;
4. connector authorization packet;
5. failure modes catalog;
6. embodied co-regulation layer;
7. future ONE/MUSS/Sentinel/Chronicle/Creation Trust repo candidates.

---

## Keeper lines

- Every artifact must show its truth condition before it shows its ambition.
- No artifact may be interpreted without its status label.
- Named is not built.
- Merged is not canonical.
- Draft-preserved is not implemented.
- Implemented is not externally validated.
- Future layer is not current runtime.
- Public repo is not open-source permission.
- Chat receipt language is not cryptographic receipt.

---

## Status note

This document is itself draft-preserved candidate material until explicitly promoted. It defines a proposed labeling discipline and should be reviewed before being made canonical governance policy.
