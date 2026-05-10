# MANNY_RUNTIME_TRACE_HANDOFF

## Version

v0.1

## Status

generated_from_spec

## Purpose

This document defines how a live runtime system would connect to the Non-Collapse Conformance Harness for read-only evaluation.

## Current State

No live runtime trace integration is connected. The harness operates on synthetic vectors only. Live trace evaluation requires explicit Brian approval.

## Integration Contract

To connect a live runtime system:

1. The runtime must emit traces conforming to `tests/non_collapse/non_collapse_runtime_trace.schema.json`.
2. Traces must include: `trace_id`, `source` (set to `live_runtime`), `action`, `context`, `system_behavior`, `timestamp`.
3. Optional enrichment: `authorization_present`, `side_effect_produced`, `governance_gate_consulted`.
4. Traces are evaluated read-only. The harness does not block, modify, or authorize runtime actions.
5. Evaluation results are written to a conformance report. They do not trigger automatic patches.

## Boundary

The harness observes and reports. It does not:

- Block runtime actions
- Patch runtime behavior
- Authorize or deny execution
- Decide whether the system must change
- Decide whether a rule is correct

## Live Trace Evaluation Requirements

- Explicit Brian approval before connecting live traces
- Read-only evaluation only
- No side effects from evaluation
- Results labeled with `live_trace_evaluated` proof status
- `receipt_verified` not claimed unless receipt engine verifies a signed receipt

## Next Steps (Requires Human Decision)

- Decide whether to connect RIO runtime traces
- Decide which trace sources to evaluate first
- Decide evaluation cadence (batch vs. continuous)
- Decide whether to expose results in ONE Command Center
