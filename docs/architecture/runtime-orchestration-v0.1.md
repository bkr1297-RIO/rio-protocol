# Runtime Orchestration Architecture v0.1

**Version:** 0.1  
**Date:** 2026-05-06  
**Author:** B-Rass (RIO Architect)  
**Status:** Local harness — not production

---

## 1. Purpose

Runtime Orchestration is the coordination layer that connects all RIO protocol components into a single end-to-end flow. It does not govern, evaluate, or interpret. It routes signals between components that do.

> "The orchestrator connects. It does not decide."

This document defines the architecture of the local orchestration harness that proves the full stack operates correctly before any production deployment exists.

---

## 2. Position in Stack

```
Human Signal
  │
  ▼
┌─────────────────────────┐
│   Grammar Scanner        │  ← Language evaluation (verdict)
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│   Proposal Packet        │  ← Crossing structured (if WARN/HOLD)
│   Constructor            │     Refusal record (if BLOCK/INVALID)
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│   Runtime Orchestrator   │  ← THIS LAYER: routes packet to correct
│                          │     governance components
└─────────────────────────┘
  │
  ├──► ONE Answer Check (if public_claims present)
  ├──► RIO Governance (if rio_required)
  ├──► Sentinel (if sentinel_required, post-approval)
  │
  ▼
┌─────────────────────────┐
│   MUS Receipt Engine     │  ← Proof of event
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│   Ledger                 │  ← Append-only hash chain
└─────────────────────────┘
  │
  ▼
┌─────────────────────────┐
│   MANTIS Observer        │  ← Pattern observation only
└─────────────────────────┘
```

---

## 3. Architectural Invariants

These invariants are non-negotiable. Any implementation that violates them is non-conforming.

| # | Invariant | Meaning |
|---|-----------|---------|
| 1 | Orchestrator does not govern | It routes. It does not evaluate, approve, refuse, or interpret. |
| 2 | Scanner does not govern | It classifies language risk. It does not block, approve, or execute. |
| 3 | Proposal Packet does not govern | It structures crossings. It does not authorize or refuse. |
| 4 | MANTIS does not govern | It observes patterns. It never authorizes, blocks, routes, or recommends. |
| 5 | RIO governs consequence only | After valid packet routing. Not before. Not without a packet. |
| 6 | Sentinel verifies fidelity only | It checks that execution matches approved scope. It does not approve. |
| 7 | MUS proves events, not meaning | Receipts prove something happened. They do not prove it was right, wise, or meaningful. |
| 8 | Ledger preserves records, not truth | The chain is append-only and verifiable. It does not validate the content of what it records. |
| 9 | Human remains final authority | Source of meaning, consent, authority, and accountability. No component claims these. |
| 10 | Prior approval does not create future permission | Each crossing is evaluated independently. Patterns do not become implicit consent. |

---

## 4. Component Responsibilities

### 4.1 Grammar Scanner

Receives human input. Returns one of five verdicts: PASS, WARN, HOLD, BLOCK, INVALID. Does not execute, route, or govern. Hands verdict to Orchestrator.

### 4.2 Proposal Packet Constructor

If verdict is WARN or HOLD: constructs a Proposal Packet with meaning_context, reliance_context, requested_action, consequence_level, and routing flags.

If verdict is BLOCK or INVALID: constructs a refusal record only. No normal Proposal Packet for downstream routing.

If verdict is PASS: no packet. Optional evaluation log.

### 4.3 Runtime Orchestrator

Receives the scanner verdict and (if applicable) the Proposal Packet or refusal record. Routes based on packet fields:

- `public_claims` present → ONE Answer Check
- `rio_required: true` → RIO Governance
- `sentinel_required: true` → Sentinel (post-approval only)
- `receipt_required: true` → MUS Receipt Engine
- Always → Ledger update (for any non-PASS event)
- Always → MANTIS observation

The Orchestrator does not evaluate the content of any field. It reads routing flags and dispatches.

### 4.4 RIO Governance

Evaluates the Proposal Packet against constitutional constraints. Returns one of: APPROVED, REFUSED, ESCALATED. Does not execute. Does not interpret meaning.

### 4.5 Sentinel

Post-approval only. Receives the approved packet and the simulated execution result. Verifies that the execution matches the approved scope. If mismatch: blocks execution, generates mismatch receipt. Does not approve or refuse the original request.

### 4.6 MUS Receipt Engine

Generates cryptographically structured receipts for every governed event. Receipt types:

- Evaluation receipt (scanner verdict for HOLD)
- Refusal receipt (BLOCK/INVALID refusal record)
- Governance receipt (RIO evaluation)
- Authorization receipt (RIO approval)
- Execution receipt (simulated execution)
- Revocation receipt (human withdrawal)
- Mismatch receipt (Sentinel fidelity failure)

### 4.7 Ledger

Append-only hash chain. Each entry contains:
- `entry_id`
- `receipt_hash`
- `previous_hash`
- `timestamp`
- `event_type`

Chain integrity is verifiable at any point.

### 4.8 MANTIS Observer

Observes all packets, receipts, and ledger entries. Records pattern observations:
- Repeated similar crossings
- Repeated refusals
- Repeated revocations

MANTIS never: authorizes, blocks, routes, recommends, or modifies any other component's behavior. Its observations are available for human review only.

---

## 5. Flow Paths

### 5.1 PASS Path (Private Exploration)

```
Human input → Scanner (PASS) → Optional log → End
```

No Proposal Packet. No governance. No receipt required. Private exploration remains available without system execution.

### 5.2 WARN Path (Advisory)

```
Human input → Scanner (WARN) → Proposal Packet constructed
  → [if public_claims] ONE Answer Check → advisory response
  → Optional evaluation log
  → MANTIS observes
```

### 5.3 HOLD Path — Approved

```
Human input → Scanner (HOLD) → Proposal Packet constructed
  → [if public_claims] ONE Answer Check
  → RIO Governance evaluation → APPROVED
  → [if sentinel_required] Sentinel pre-check
  → Simulated execution
  → [if sentinel_required] Sentinel fidelity verification
  → MUS receipt generated
  → Ledger updated
  → MANTIS observes
```

### 5.4 HOLD Path — Refused

```
Human input → Scanner (HOLD) → Proposal Packet constructed
  → RIO Governance evaluation → REFUSED
  → Refusal receipt generated
  → Ledger updated
  → MANTIS observes
```

### 5.5 HOLD Path — Revoked

```
Human input → Scanner (HOLD) → Proposal Packet constructed
  → RIO Governance evaluation → APPROVED
  → Human revokes authorization before execution
  → Revocation receipt generated
  → Ledger updated
  → MANTIS observes
```

### 5.6 BLOCK/INVALID Path

```
Human input → Scanner (BLOCK/INVALID) → Refusal record only
  → Refusal receipt generated
  → Ledger updated
  → MANTIS observes
  → No normal Proposal Packet routing
```

### 5.7 Sentinel Mismatch Path

```
Human input → Scanner (HOLD) → Proposal Packet → RIO APPROVED
  → Simulated execution
  → Sentinel detects scope mismatch
  → Execution blocked
  → Mismatch receipt generated
  → Ledger updated
  → MANTIS observes
```

---

## 6. What the Orchestrator Is Not

| It is not | Because |
|-----------|---------|
| A governance layer | It routes to governance. It does not perform governance. |
| An authority | It has no opinion on whether a crossing should proceed. |
| A filter | It does not suppress, modify, or delay signals on its own judgment. |
| A learning system | It does not adapt behavior based on patterns. |
| A meaning interpreter | It reads routing flags. It does not read meaning. |

---

## 7. Readiness Classification

| Layer | Status |
|-------|--------|
| Architecture definition | Ready (this document) |
| Flow specification | Ready |
| Local harness implementation | Target ready |
| Production runtime | Not ready |
| External integrations | Not included |
| Autonomous execution | Not included |

---

## 8. Version History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-05-06 | Initial architecture document |
