# RETURN-GATE-SPEC-001

**Version:** 0.1  
**Status:** Candidate governance specification / non-normative until promoted  
**Register:** Public governance and developer surface  
**Runtime status:** Not implemented; no enforcement, conformance, production, or ratification claim

---

## 1. Purpose

The Return Gate governs the boundary between an ending cycle and any possible new cycle. Its design objective is simple:

> Closure, memory, forecast, or momentum must not create a new objective.

The gate defaults to Ambient Mode. A new cycle requires a distinct human initiation and later ordinary RIO admission for any consequential action.

---

## 2. State machine

```text
ACTIVE_CYCLE
  → RETURN_REVIEW
      → RETURN_INCOMPLETE → ACTIVE_CYCLE | RETURN_REVIEW
      → RETURN_HELD
      → RETURN_READY
          → RETURN_HELD
          → TERMINATED_WITH_RESIDUE
          → RETURN_CLOSED
              → AMBIENT_MODE
                  → SOURCEPOINT_DRAFTED
                      → HUMAN_REVIEW
                          → NEW_SOURCE_AUTHORIZED
                              → NEW_CYCLE / PHASE_1
```

### Prohibited transition

```text
RETURN_READY  -X->  NEW_SOURCE_AUTHORIZED
```

No forecast, phase classifier, prior authorization, machine-generated objective, or absence of a human response may bridge this prohibited edge.

---

## 3. Input record

The gate consumes a Return Packet that includes:

```text
cycle_id
current_state
declared_objective_ref
evidence_refs
active_grant_refs
closure_disposition
residue_disposition
human_actor_ref
human_confirmation_ref
receipt_ref
```

Interpretive context is optional and separately labeled. It has no authority effect.

---

## 4. Closure requirements

A candidate implementation may enter `RETURN_CLOSED` only when it has:

1. an identifiable cycle;
2. a human closure disposition or an independently defined expiry rule that does **not** initiate anything;
3. an explicit treatment for active grants;
4. a classified residue disposition;
5. a receipt or error record for the represented state change.

The gate must fail closed when a required closure field is missing. It may return `RETURN_HELD` or `RETURN_INCOMPLETE`; it may not infer completion.

---

## 5. Effects of closure

On `RETURN_CLOSED`, the implementation must:

1. record closure and its receipt reference;
2. expire or revoke grants according to their declared terms;
3. retain only the material permitted by the named retention scope;
4. render unresolved material as explicit residue;
5. enter `AMBIENT_MODE`.

Ambient Mode is not a renewal state. It must not extend prior grants, create tasks, or monitor beyond separately authorized scope.

---

## 6. New SourcePoint requirements

A candidate implementation may enter `NEW_SOURCE_AUTHORIZED` only after:

1. a human drafts a new SourcePoint;
2. a human explicitly confirms it;
3. the new objective is distinguishable from prior-cycle memory;
4. it receives its own authority, scope, consequence, and return records;
5. any consequential action later passes RIO.

A new objective may cite prior evidence. It must not reuse closed-cycle authorization as its authority basis.

---

## 7. Required negative vectors

- `SYMBOLIC_CONTEXT_AS_PERMISSION`
- `CLOSED_GRANT_REPLAY`
- `MODEL_DRAFT_AS_HUMAN_INITIATION`
- `SILENCE_AS_CONTINUATION`
- `BUNDLED_CLOSE_AND_BEGIN`
- `RESIDUE_TO_TASK_QUEUE`
- `FORECAST_TO_EXECUTION`
- `AMBIENT_SCOPE_EXPANSION`

Candidate vectors appear in [RETURN-GATE-INVARIANTS-001](../../tests/governance/return-gate-invariants-001.md).

---

## Keeper

> The default path is Return → Ambient Mode, not Return → Source. The final step into a new SourcePoint is a distinct, attributable human act.