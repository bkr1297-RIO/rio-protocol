# 8-Step Runtime Protocol Flow

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Runtime

---

## Overview

The Governed Execution Protocol runtime executes the following steps for every request:

1. Intake
2. Classification
3. Structured Intent
4. Policy & Risk Check
5. Authorization
6. Execution Gate
7. Receipt / Attestation
8. Audit Ledger

Governance Learning operates asynchronously after execution and does not bypass runtime controls.

---

## Flow Diagram

```
Request
  │
  ▼
┌─────────────┐
│  1. Intake   │──── Reject (auth failure)
└──────┬──────┘
       ▼
┌──────────────────┐
│ 2. Classification │──── Reject (unrecognized action)
└──────┬───────────┘
       ▼
┌─────────────────────┐
│ 3. Structured Intent │──── Reject (schema failure)
└──────┬──────────────┘
       ▼
┌──────────────────────┐
│ 4. Policy & Risk Check│──┬── Deny ──────────────┐
└──────┬───────────────┘  │                       │
       ▼                   │                       │
┌─────────────────┐        │                       │
│ 5. Authorization │──┬── Deny ─────────────┐     │
└──────┬──────────┘   │                     │     │
       ▼               │                     ▼     ▼
┌──────────────────┐   │              ┌──────────────────────┐
│ 6. Execution Gate │──┤── Block ────▶│ 7. Receipt/Attestation│
└──────┬───────────┘   │              └──────┬───────────────┘
       ▼               │                     ▼
   [Execute]           │              ┌──────────────┐
       │               │              │ 8. Audit Ledger│
       ▼               │              └───────────────┘
┌──────────────────────┐│
│ 7. Receipt/Attestation││
└──────┬───────────────┘│
       ▼                │
┌──────────────┐        │
│ 8. Audit Ledger│       │
└──────┬───────┘        │
       ▼                │
   [Complete]           │
                        │
       ┌────────────────┘
       ▼
  9. Governance Learning (Asynchronous)
       │
       ▼
  Policy & Risk Model Updates
  (deployed through governed change process)
```

---

## Key Properties

Every request — whether approved, denied, or blocked — produces a receipt (Step 7) and a ledger entry (Step 8). There are no silent failures and no unrecorded decisions.

The Execution Gate (Step 6) is the single enforcement point. It re-verifies authorization validity, checks kill switch status, and confirms intent hash integrity before releasing execution.

Governance Learning (Step 9) is asynchronous. It reads from the Governed Corpus and proposes changes that must themselves be authorized through the protocol before taking effect.

---

## References

| Document | Path |
|----------|------|
| Governed Execution Protocol (full definition) | `/spec/governed_execution_protocol.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| 8-Step to 15-Protocol Mapping | `/spec/8_step_to_15_protocol_mapping.md` |
| 15-Layer System Architecture | `/architecture/15_layer_model.md` |
| Governed Corpus | `/spec/governed_corpus.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
