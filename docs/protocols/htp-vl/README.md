# HTP/VL-1 — Harmonic Transition Protocol / Voice Leading

**Status:** Candidate Protocol Specification v0.1.0  
**Classification:** Repository-safe architecture artifact; no runtime authority by itself  
**Purpose:** Define a four-object wire protocol for bounded, inspectable state transitions across ONE / RIO / MUSS.

## Protocol Objects

1. `HarmonicTransitionProposal` — requested movement.
2. `HarmonicTransitionVerdict` — independent RIO adjudication.
3. `CadenceReceipt` — post-action evidence and actual resolution.
4. `PatternUpdateProposal` — proposed learning derived from settled evidence.

## Core Sequence

```text
Beat 0 — Readiness
Beat 1 — Signal / Proposal
Beat 2 — Continuity / Verdict
Beat 3 — Crossing / Execution
Beat 4 — Return / Cadence Receipt
Inter-measure Rest — Learning Proposal and authorized admission
```

## Normative Rule

A state transition is admissible only when it:

- preserves every required continuity carrier;
- performs no more than the authorized displacement;
- declares every material functional handoff or substitution;
- begins from a settled prior cadence;
- binds execution to the exact adjudicated proposal;
- returns a verifiable cadence receipt before a later transition begins.

## Files

- `HTP-VL-1-SPEC.md` — candidate protocol specification.
- `../../../schemas/htp-vl/common.schema.json` — shared types and identifiers.
- `../../../schemas/htp-vl/harmonic-transition-proposal.schema.json`
- `../../../schemas/htp-vl/harmonic-transition-verdict.schema.json`
- `../../../schemas/htp-vl/cadence-receipt.schema.json`
- `../../../schemas/htp-vl/pattern-update-proposal.schema.json`
- `../../../examples/htp-vl/` — non-authoritative example payloads.

## Validation Boundary

All schemas use JSON Schema Draft 2020-12. Each object must validate independently. A proposal never contains its own verdict; a verdict never asserts post-action cadence; a receipt never changes future policy; a learning proposal never self-admits.

This package is a candidate docs/schema surface. It does not alter existing runtime behavior, authority, conformance status, or canonical contracts by itself.
