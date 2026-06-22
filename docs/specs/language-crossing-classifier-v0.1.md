# Language Crossing Classifier v0.1

Status Truth Label: draft-preserved  
Maturity: protocol-facing spec candidate  
Date: 2026-06-22 America/Denver  
Repository: bkr1297-RIO/rio-protocol  
Scope: Documentation-only specification candidate for language-to-consequence classification  
Canonical status: Not canonical until explicit source-of-truth promotion  
Runtime status: No runtime code, schema, executable test, endpoint, or deployed behavior changed by this document.

---

## 0. Purpose

The Language Crossing Classifier defines a protocol-facing profile for classifying language before it becomes proposal, public claim, connector action, source-of-truth mutation, or runtime consequence.

It exists to preserve the boundary between language, classification, authorization, execution, and proof.

One-line definition:

> The Language Crossing Classifier names the crossing surface and consequence posture of a language payload before any governed packet, connector authorization, public claim, or runtime action may rely on it.

---

## 1. Placement in rio-protocol

This spec follows the placement decision preserved in:

```text
docs/handoff/language-crossing-classifier-placement-note-v0.1.md
```

The classifier should reuse existing protocol lanes before earning a standalone schema lane.

Related existing lanes:

- canonical intent schema;
- proposal packet schema;
- connector action authorization packet;
- authorization record schema;
- receipt schemas;
- risk / consequence schemas;
- RIO state machine;
- conformance failure tests.

---

## 2. Core invariant

```text
Classification names the crossing. It does not authorize the consequence.
```

A classifier result may inform routing, holds, required review, and packet formation. It must not itself become authorization, execution clearance, source-of-truth standing, receipt standing, or runtime proof.

---

## 3. Classification sequence

```text
language or source intent
→ classify source register
→ classify target register
→ classify crossing kind
→ assign consequence floor
→ identify ambiguity/conflict
→ determine required gate/review
→ enrich existing proposal / authority envelope
→ validate contract and forbidden self-clearing semantics
→ candidate-stage event or rejection event
→ RIO decision / human authorization when required
→ Sentinel fidelity
→ outcome receipt
```

---

## 4. Classification profile

The classifier should attach as a nested profile to an existing proposal, canonical intent, connector authorization, or public-claim review structure when possible.

Candidate profile shape:

```yaml
language_crossing_classification:
  version: "0.1"
  classifier_status: "draft-preserved"
  source_register: "private | personal | architecture | repo_safe | public | runtime | unknown"
  target_register: "private | personal | architecture | repo_safe | public | runtime | source_of_truth | external_consequence | unknown"
  crossing_kind: "reflection | formation | architecture_candidate | operative_candidate | public_claim | external_communication | connector_action | source_of_truth_candidate | runtime_action"
  consequence_floor: "none | low | medium | high | critical"
  classification_status: "classified | ambiguous | conflicting | invalid"
  ambiguity_flags: []
  matched_rules: []
  required_gate: "none | public_claim_gate | connector_authorization | rio | sentinel | human_review | combined"
  human_review_required: false
  classifier_cannot_authorize: true
```

This profile is a specification candidate only. Future schema work must crosswalk these fields against existing vocabulary before finalizing names or enum values.

---

## 5. Required classification dimensions

| Dimension | Meaning | Required outcome |
|---|---|---|
| source register | where the language comes from or what posture it carries | register label or unknown |
| target register | what surface the language is trying to enter | register label or unknown |
| crossing kind | what type of movement is being attempted | crossing label |
| consequence floor | minimum consequence posture | none/low/medium/high/critical or existing repo equivalent |
| classification status | whether the classifier resolved the case | classified/ambiguous/conflicting/invalid |
| required gate | which governance surface should inspect next | gate label |
| human review | whether human review is required before reliance | true/false |

---

## 6. Consequence and ambiguity rules

1. Multiple matches should preserve the highest applicable consequence floor.
2. Incompatible matches should set `classification_status: conflicting`.
3. Unresolved or low-confidence matches should set `classification_status: ambiguous`.
4. Ambiguous or conflicting high-consequence cases should route to hold / review rather than reliance.
5. Classification cannot downgrade an existing gate requirement.
6. Classification cannot convert private meaning into public proof.
7. Classification cannot convert a draft artifact into source-of-truth standing.
8. Classification cannot convert connector availability into connector authorization.

---

## 7. Candidate crossing kinds

| Crossing kind | Meaning | Natural downstream lane |
|---|---|---|
| reflection | private or local meaning work | private/personal register |
| formation | exploratory shaping before architecture/protocol | architecture candidate / candidate hold |
| architecture_candidate | design or doctrine candidate | architecture repo / routing map |
| operative_candidate | instruction-like or workflow-shaping language | proposal / RIO review |
| public_claim | externally-facing claim or positioning language | Public Claim Gate |
| external_communication | outbound email/post/message/publish candidate | connector authorization / public claim gate |
| connector_action | tool or connector operation candidate | Connector Action Authorization Packet |
| source_of_truth_candidate | canon/promotion/source mutation candidate | source-of-truth promotion process |
| runtime_action | action likely to affect systems, data, people, money, safety, or external state | RIO / Sentinel / receipt path |

---

## 8. Relation to existing packet lanes

### Canonical intent / proposal packet

The classifier may enrich canonical intent or proposal packet formation by naming target register, crossing kind, consequence floor, and gate requirement.

It should not create a duplicate packet family until existing proposal/envelope structures are proven insufficient.

### Connector Action Authorization Packet

The classifier helps determine whether a language payload is connector-facing or externally consequential.

Connector Action Authorization Packet governs bounded tool/connector authority after the task is specific enough to form a connector action packet.

### Public Claim Gate

The classifier helps identify language attempting to become a public claim.

Public Claim Gate remains the lane for evidence basis, claim level, audience, proof status, runtime status, disclaimers, approval state, and receipt requirement.

### Receipt and ledger lanes

The classifier may produce or support a candidate-stage event. It does not produce an outcome receipt, signed receipt, ledgered receipt, or verified receipt.

---

## 9. Forbidden self-clearing semantics

Future schema or validators should reject fields that attempt to let a candidate carry its own clearance.

Examples to preserve:

```text
authorized_state
clear_crossing_token
authorization_token
execution_token
receipt_hash
ledger_entry_id
```

Equivalent fields with the same semantics should also fail closed.

---

## 10. Ten-point conformance outline seed

A later conformance outline should include at least:

| # | Case | Expected result |
|---|---|---|
| 1 | valid low/no consequence classification | pass |
| 2 | valid architecture candidate classification | pass |
| 3 | valid runtime-action candidate classification | pass-and-hold |
| 4 | ambiguous/conflicting classification | held / review required |
| 5 | top-level self-clearing field | reject |
| 6 | invalid enum value | reject |
| 7 | malformed UUID | reject if packet id format is used |
| 8 | malformed payload hash | reject if payload hash is required |
| 9 | nested forbidden field | reject |
| 10 | replay / duplicate packet identity | halt or require replay policy |

---

## 11. Canonicalization note

Stable hashes require stable serialization.

Before schema or executable tests are promoted, define or reuse canonicalization rules for:

- payload string/input capture;
- object key ordering;
- array preservation;
- undefined / non-finite / unsafe runtime values;
- packet fingerprinting;
- args hashing where connector actions are involved.

Keeper:

> Stable bytes before stable hashes. Stable hashes before stable packets. Stable packets before trusted receipts.

---

## 12. Future schema candidate path

If this spec is approved for schema work, prepare:

```text
schemas/language-crossing-classifier-v0.1.schema.json
```

Schema work should reuse existing `$defs` or vocabulary from proposal, authorization, risk, RIO state, and receipt schemas wherever possible.

---

## 13. Future conformance candidate path

If this spec is approved for conformance work, prepare:

```text
tests/language-crossing-classifier-tests-v0.1.md
```

A fixture lane may later be created only if the repository chooses to preserve example valid/invalid packets as discrete files:

```text
tests/fixtures/language-crossing-classifier/
```

---

## 14. Promotion conditions

This spec should not be promoted until:

1. existing canonical intent and proposal schemas are crosswalked;
2. connector action authorization packet v0.2 is crosswalked;
3. risk/consequence vocabularies are aligned;
4. authorization and receipt lanes are aligned;
5. classifier status and RIO state machine states are mapped;
6. canonicalization rules are decided;
7. conformance outline is drafted;
8. schema candidate is reviewed;
9. Brian approves the promotion path.

---

## Keeper boundaries

> Classification names the crossing; it does not authorize the consequence.

> A classified candidate is still a candidate.

> A held candidate is preserved for review, not cleared by preservation.

> Public claim, connector action, source-of-truth change, and runtime action each require their own gate.

---

## Closing status

This document is a protocol-facing spec candidate. It preserves classification grammar and placement only.

It does not create executable code, schema conformance, runtime enforcement, public claim approval, connector authorization, source-of-truth promotion, or cryptographic receipt.
