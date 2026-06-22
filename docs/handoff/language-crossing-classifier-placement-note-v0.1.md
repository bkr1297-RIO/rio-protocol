# Language Crossing Classifier Placement Note v0.1

Status Truth Label: draft-preserved  
Maturity: protocol-facing placement note  
Date: 2026-06-22 America/Denver  
Repository: bkr1297-RIO/rio-protocol  
Scope: Documentation-only placement note for the Language Crossing Classifier validation harness candidate  
Canonical status: Not canonical until explicit source-of-truth promotion  
Runtime status: No runtime code, schema, executable test, endpoint, or deployed behavior changed by this note.

---

## Purpose

This note records where the Language Crossing Classifier belongs inside `rio-protocol` if it is later promoted from architecture/implementation-planning into protocol-facing schema and conformance work.

The classifier is a language-to-consequence gate profile. It should reuse existing proposal, authorization, receipt, and conformance lanes rather than create a parallel runtime stack.

---

## Inspection basis

This placement review inspected the existing repo signals surfaced by search and related PR status material:

- `spec/canonical_intent_schema.md`
- `spec/canonical_intent_schema.json`
- `docs/specs/proposal-packet-schema-v0.1.md`
- `schemas/proposal-packet-v0.1.schema.json`
- `spec/connector-action-authorization-packet-v0.1.md`
- `spec/connector-action-authorization-packet-v0.2.md`
- `schemas/connector-action-authorization-packet-v0.2.schema.json` candidate from PR #24
- `tests/connector-action-authorization-packet-tests-v0.1.md` candidate from PR #24
- `docs/tests/conformance-failure-tests-v0.1.md`
- `docs/architecture/proposal-packet-bridge-v0.1.md`
- `schemas/rio-state-machine-v0.1.json`
- `schemas/risk_evaluation.json`
- `schemas/authorization_record.json`

---

## Current finding

`rio-protocol` already has the necessary lanes for this work:

```text
spec/
schemas/
docs/specs/
docs/tests/
tests/
docs/handoff/
docs/architecture/
```

The correct next state is not runtime TypeScript implementation. The correct next state is a protocol-facing crosswalk and later schema/conformance candidate if Brian promotes the route.

---

## Placement map

| Component | Existing repo lane | Future candidate path |
|---|---|---|
| classifier concept | `docs/architecture/` or `docs/specs/` | `docs/specs/language-crossing-classifier-v0.1.md` |
| schema profile | `schemas/` | `schemas/language-crossing-classifier-v0.1.schema.json` |
| conformance outline | `docs/tests/` or `tests/` | `tests/language-crossing-classifier-tests-v0.1.md` |
| fixture examples | `examples/` or `tests/fixtures/` if fixture lane is created | `tests/fixtures/language-crossing-classifier/` |
| canonicalization rule | `spec/` or `docs/specs/` | `spec/canonicalization-rules-v0.1.md` or classifier-specific appendix |
| connector interaction | existing Connector Action Authorization Packet lane | crosswalk to CAAP v0.2, not replacement |
| proposal/envelope interaction | existing Proposal Packet / Canonical Intent lanes | nested profile, not duplicate packet family |

---

## Reuse-before-invention rules

Before creating schema or tests, crosswalk the classifier against:

1. existing canonical intent schema;
2. existing proposal packet schema;
3. connector action authorization packet v0.2;
4. risk/consequence vocabulary;
5. authorization record schema;
6. receipt schema and conformance receipt schema;
7. RIO state machine states;
8. existing conformance failure tests.

If a field already exists with the same function, profile or reference it. Do not create a duplicate-under-new-name field.

---

## Candidate semantics to preserve

The classifier should preserve this sequence:

```text
language or source intent
→ classify source/target register and crossing kind
→ assign consequence floor and ambiguity status
→ enrich existing proposal / authority envelope
→ validate contract and forbidden self-clearing semantics
→ candidate-stage event or rejection event
→ RIO decision / human authorization when required
→ Sentinel fidelity
→ outcome receipt
```

---

## Ten-point matrix to preserve later

A later conformance outline should include at least these cases:

1. valid low/no consequence classification;
2. valid architecture candidate classification;
3. valid runtime-action candidate classification;
4. ambiguous/conflicting classification hold;
5. top-level self-clearing field rejection;
6. invalid enum rejection;
7. malformed UUID rejection;
8. malformed payload-hash rejection;
9. nested forbidden field rejection;
10. replay / duplicate packet identity halt.

---

## Relation to Connector Action Authorization Packet v0.2

The classifier is not a replacement for connector authorization.

It sits before or beside proposal formation and helps determine whether a language payload is private, exploratory, architectural, public-facing, source-of-truth-affecting, connector-facing, or runtime-action-affecting.

Connector Action Authorization Packet v0.2 governs bounded tool/connector authority after a task is specific enough to form a connector action packet.

---

## Recommended next artifact, if promoted

If Brian chooses to continue this route inside `rio-protocol`, prepare:

```text
docs/specs/language-crossing-classifier-v0.1.md
```

That document should be a protocol-facing spec candidate only. It should not create executable code or claim conformance.

After that, and only after crosswalk, prepare:

```text
schemas/language-crossing-classifier-v0.1.schema.json
tests/language-crossing-classifier-tests-v0.1.md
```

---

## Keeper boundaries

> Classification names the crossing; it does not authorize the consequence.

> Schema candidate is not runtime proof.

> Conformance outline is not executable conformance.

> The classifier must reuse the existing packet and receipt lanes before it earns a new schema lane.

---

## Closing status

This file is a placement note, not a cryptographic receipt. It preserves the repo-facing routing decision only.
