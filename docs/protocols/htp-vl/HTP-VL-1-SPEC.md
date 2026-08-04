# HTP/VL-1 — Harmonic Transition Protocol / Voice Leading

## 0. Document Control

| Field | Value |
|---|---|
| Protocol | HTP/VL-1 |
| Version | 0.1.0 |
| Status | Candidate specification |
| Lane | Core Architecture → Transition Mechanics |
| Runtime effect | None until separately implemented and admitted |
| Primary authority boundary | Human authority remains external to and above this protocol |

---

## 1. Purpose

HTP/VL-1 defines the wire-level objects and deterministic transition sequence required to move a system from an active harmonic state to a target harmonic state without losing lineage, silently substituting functions, exceeding authorized movement, or beginning a later transition before the prior consequence has settled.

The protocol separates proposal, adjudication, evidence, and learning into four objects so that no participant authors its own authority, proof, or permanent learning.

---

## 2. The Four Objects

### 2.1 HarmonicTransitionProposal

**Question:** What movement is being requested?

Authored by the proposing/orchestration side. It may contain current and target harmonic states, requested operation and scope, designated continuity carriers, declared voice movements, displacement bounds, evidence references, prior cadence reference, and requested execution binding.

It must not contain an admissibility verdict, authorization token, actual cadence classification, claim that execution occurred, or admitted learning update.

### 2.2 HarmonicTransitionVerdict

**Question:** Is this exact proposed movement admissible?

Authored only by the independent RIO adjudication boundary. It contains immutable proposal binding, evaluated invariants, PASS/HOLD/REFUSE/INVALID status, authorized displacement and scope if any, expiry, nonce, execution limits, expected cadence class, and diagnostic failure codes.

It must not contain execution success, actual consequence, actual cadence, or a permanent learning update.

### 2.3 CadenceReceipt

**Question:** What actually occurred, and how did the transition resolve?

Authored after execution or non-execution by the receipt/attestation path. It contains proposal and verdict bindings, execution status, actual state delta, consequence evidence, actual cadence classification, settlement status, child-handle closure state, signatures, and ledger linkage.

It must not contain a new authorization, rewritten proposal, or automatically admitted future rule.

### 2.4 PatternUpdateProposal

**Question:** What might future participation learn from the settled result?

Authored only after a settled or explicitly routed cadence. It contains receipt binding, observed recurring pattern, proposed local N=1 update, conditions, exceptions, review terms, evidence sufficiency, and admission status initially `PROPOSED`.

It must not modify active policy by itself, generalize an N=1 observation to a population, overwrite human-stated meaning, self-approve, or self-admit.

---

## 3. Harmonic State Model

A harmonic state is a bounded vector over a versioned root-function registry.

```text
H = [h1, h2, ... hn]
0.0 ≤ hi ≤ 1.0
```

The v0.1 candidate registry contains twelve functions:

1. Origin
2. Relation
3. Expression
4. Structure
5. Mutation
6. Care
7. Depth
8. Power
9. Completion
10. Renewal
11. Illumination
12. Communion

The registry is versioned and experimental. Protocol validity depends on the declared registry version, not on an eternal requirement that the count remain twelve.

### 3.1 Exact invariants versus harmonic values

Qualitative state may be represented harmonically. Exact constitutional facts may not be reduced to fuzzy vector intensities.

The following require exact bindings when applicable: human authority identity, approval signature, proposal hash, verdict hash, nonce, expiry, tool/action arguments, receipt-chain continuity, provenance identity, and child-handle closure.

---

## 4. Kinematic Invariants

### INV-HTP-01 — Common Tone Continuity

Every proposal must designate at least one continuity carrier for a cross-domain or consequential transition.

Carrier types:

- `HARMONIC_FUNCTION`
- `HUMAN_AUTHORITY`
- `INTENT_BINDING`
- `PROVENANCE`
- `IDENTITY`
- `CONSENT`
- `CUSTOM_EXACT`

A harmonic carrier passes only if both conditions hold:

```text
H_B[c] >= absolute_threshold
H_B[c] / max(H_A[c], epsilon) >= retention_ratio
```

An exact carrier passes only if its expected and observed bindings are identical under the declared canonicalization rule.

### INV-HTP-02 — Minimum Admissible Displacement

The requested state change must be the smallest permitted movement that reaches the authorized target while preserving all protected dimensions.

```text
Delta_w(H_A,H_B) = sqrt(sum(w_i * (H_B[i]-H_A[i])^2))
```

A transition fails when weighted distance exceeds the allowed maximum, a protected dimension changes, an exact-binding dimension differs, a localized change could satisfy the request but a global rewrite is proposed, or a prohibited substitution occurs.

### INV-HTP-03 — Explicit Voice Movement

Every material attenuation, amplification, sustain, handoff, transform, split, merge, or rest must be represented in `voice_movements`.

Allowed movement types:

- `SUSTAIN`
- `ATTENUATE`
- `AMPLIFY`
- `HANDOFF`
- `TRANSFORM`
- `SPLIT`
- `MERGE`
- `REST`

Observed movement absent from the declared map produces `HARMONIC_DRIFT` or `UNDECLARED_SUBSTITUTION`.

### INV-HTP-04 — Prior Cadence Settlement

No new consequential proposal may advance to execution unless the required prior receipt is present, cryptographically valid, ledger-linked, cadence-classified, settled or explicitly routed, and free of intolerable open child handles.

### INV-HTP-05 — Proposal/Verdict/Execution Binding

The verdict must bind the canonical proposal hash. Execution must bind the verdict hash, proposal hash, nonce, expiry, action, scope, and maximum execution count.

### INV-HTP-06 — Post-Action Cadence Truth

Actual cadence may be classified only after evidence is available. A pre-execution verdict may state `expected_cadence`, but never `actual_cadence`.

### INV-HTP-07 — Learning Non-Self-Admission

A PatternUpdateProposal remains inert until admitted by a separately authorized process. MANTIS observation and Learning Office proposal do not themselves change active behavior.

---

## 5. Four-Beat Runtime

### Beat 0 — Readiness

Required checks: prior cadence settled; authority identity valid; context and registry versions available; ledger chain valid; no incompatible active transition; no unresolved revocation state.

### Beat 1 — Signal / Proposal

Perceptual and Pattern offices gather signal and evidence. Interpretive and Relational offices may assemble a HarmonicTransitionProposal.

### Beat 2 — Continuity / Verdict

RIO independently validates the proposal and emits a HarmonicTransitionVerdict.

Permitted verdict states: `PASS`, `HOLD`, `REFUSE`, `INVALID`. Only `PASS` may authorize Beat 3.

### Beat 3 — Crossing

The execution kernel performs only the bound side effect under the verdict's scope, expiry, nonce, and execution count.

### Beat 4 — Return / Cadence

MUS records execution and consequence evidence. Reflective Intelligence classifies actual cadence. MANTIS may emit observations. Learning Intelligence may create a PatternUpdateProposal.

### Inter-Measure Rest

The system allows consequence propagation, child closure, review, and authorized learning admission before the next dependent measure begins.

---

## 6. Cadence Taxonomy

| Cadence | Condition |
|---|---|
| `AUTHENTIC` | Authorized execution occurred and intended consequence settled within tolerance. |
| `DECEPTIVE` | Execution occurred, but consequence diverged materially from declared intent or target state. |
| `RESTORATIVE` | Execution began or completed, then an authorized repair returned the system to a valid settled state. |
| `INTERRUPTED` | Execution was stopped by revocation, timeout, failure, or hard intercept before settlement. |
| `REFUSED` | The gate denied the transition before execution. |
| `UNSETTLED` | Evidence is incomplete or consequence has not finished propagating. |
| `INVALID` | Object binding, schema, signature, or required evidence is invalid. |

A refusal is not a rollback. A restorative cadence requires an actual prior mutation or side effect that was subsequently repaired.

---

## 7. Object Sequence and Authority

```text
Human / Orchestration
    -> HarmonicTransitionProposal

RIO Gate
    -> HarmonicTransitionVerdict

Execution + MUS / Sentinel
    -> CadenceReceipt

MANTIS + Reflective / Learning Offices
    -> PatternUpdateProposal

Authorized admission process
    -> active local update, separate from HTP/VL-1
```

No object may author the next object's authority claim.

---

## 8. Error Codes

- `SCHEMA_INVALID`
- `REGISTRY_VERSION_UNKNOWN`
- `PRIOR_CADENCE_UNSETTLED`
- `COMMON_TONE_MISSING`
- `COMMON_TONE_BELOW_THRESHOLD`
- `EXACT_CARRIER_MISMATCH`
- `DISPLACEMENT_EXCEEDED`
- `PROTECTED_DIMENSION_CHANGED`
- `UNDECLARED_SUBSTITUTION`
- `HARMONIC_DRIFT`
- `PROPOSAL_HASH_MISMATCH`
- `VERDICT_HASH_MISMATCH`
- `AUTHORITY_BINDING_INVALID`
- `NONCE_INVALID`
- `VERDICT_EXPIRED`
- `MAX_EXECUTIONS_EXCEEDED`
- `CHILD_HANDLES_OPEN`
- `CONSEQUENCE_DIVERGENCE`
- `CADENCE_UNSETTLED`
- `LEARNING_SELF_ADMISSION_PROHIBITED`

---

## 9. 7 × 12 × 4 Address Space

```text
7 Intelligence Offices
× 12 Root Functions
× 4 Transition Operations
= 336 candidate cells
```

Transition operations are `DETECT`, `PRESERVE`, `MOVE`, and `SETTLE`.

Every cell must be classified before implementation as `NATIVE`, `SUPPORTED`, `DERIVED`, `NON_APPLICABLE`, or `PROHIBITED`.

The number 336 describes the candidate address space, not a requirement that all 336 cells become executable evaluators.

---

## 10. Required Conformance Tests

An implementation is not HTP/VL-1 conformant until it proves at least:

1. Proposal cannot contain or self-author a verdict.
2. Verdict cannot claim actual cadence.
3. Receipt cannot authorize execution.
4. Learning proposal cannot self-admit.
5. Exact carriers fail on any canonical mismatch.
6. Harmonic carriers enforce absolute and retention thresholds.
7. Protected dimensions cannot move even when total weighted distance is low.
8. Undeclared substitutions fail deterministically.
9. No dependent transition starts before prior settlement.
10. Execution is bound to proposal hash, verdict hash, nonce, expiry, scope, and maximum execution count.
11. Deceptive cadence is detected after execution/consequence divergence.
12. Refused cadence produces a receipt of non-execution without pretending a rollback occurred.
13. Interrupted cadence freezes or accounts for child handles.
14. Pattern updates remain inert until separately admitted.
15. Canonical serialization yields stable hashes across compliant implementations.

---

## 11. Repository Placement and Status

Schemas live under `/schemas/htp-vl/`; examples live under `/examples/htp-vl/`.

This document is a candidate protocol specification. It does not merge, publish, authorize runtime use, or alter existing canonical contracts by itself.
