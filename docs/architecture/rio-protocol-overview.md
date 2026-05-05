# RIO Protocol Architecture Overview

**Version:** 0.1
**Date:** 2026-05-04
**Scope:** One-page architecture overview showing the complete governed action flow.

---

## Full Flow

```
Human
  │
  │  (expresses intent)
  ▼
Packet
  │  ← Structured governance packet: intent + hash + metadata + risk tier
  │
  ▼
RIO (Governor)
  │  ← Policy evaluation, risk assessment, pre-check
  │  ← Presents proposal to human for review
  │
  ▼
Human Decision
  │  ← COMMITTED / REFUSED / CLARIFY / HOLD
  │
  ▼
Sentinel (Gate)
  │  ← Validates authorization token
  │  ← Confirms packet hash matches committed proposal
  │  ← Checks token not expired, not replayed, not burned
  │  ← Enforces proposer ≠ approver
  │
  ▼
Execution
  │  ← Controlled adapter performs the action
  │  ← Token burned immediately after execution
  │
  ▼
Receipt
  │  ← Cryptographic proof: intent_id, approver_id, token_id,
  │     policy_hash, execution_result, receipt_hash,
  │     previous_receipt_hash, snapshot_hash, handoff_receipt_hash
  │
  ▼
Ledger
  │  ← Append-only, SHA-256 hash chain
  │  ← Each entry references previous entry hash
  │  ← WAL discipline: write-ahead before confirmation
  │
  ▼
Verification
  │  ← Independent check: structure, signature, chain, temporal
  │  ← Produces verdict: VERIFIED / FAILED / STRUCTURALLY_VALID / etc.
  │
  ▼
Governance Consequence
     ← VERIFIED → action stands, learning recorded
     ← FAILED → action flagged, investigation triggered
```

---

## Principals

| Principal | System Name | Role |
|-----------|-------------|------|
| Human | — | Root authority. Source of all permission. Not a system role — the entity the system serves. |
| Governor | RIO | Evaluates policy, enforces gates, issues and burns tokens, produces receipts. |
| Operating Environment | ONE | Human interface. Where proposals are reviewed, approved, and monitored. |
| Executor | Tool / Agent / API | Performs approved actions inside the governance boundary. Untrusted by default. |
| Observer | MANTIS | Records all events. Provides advisory learning. Never approves or executes. |

---

## State Machine (16 States)

The governed action lifecycle passes through exactly 16 states organized in three phases:

**Intake Phase:**
SIGNAL → INTERPRETED → PACKETIZED → PRECHECKED

**Governance Phase:**
REVIEWED → COMMITTED → GATE_VALIDATED
(with branches to: CLARIFY, HOLD, BLOCKED, REFUSED)

**Execution Phase:**
EXECUTING → EXECUTED → RECEIPTED → LEDGERED → VERIFIED

**Terminal Outcomes:**
BLOCKED, REFUSED, FAILED, EXPIRED

Every state transition is recorded. No state may be skipped.

---

## Enforcement Boundaries

```
┌─────────────────────────────────────────────────────────┐
│                    TRUST BOUNDARY                         │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐   │
│  │   ONE    │───▶│   RIO    │───▶│    EXECUTION     │   │
│  │ (Human   │    │(Governor)│    │   (Controlled)   │   │
│  │Interface)│    │          │    │                  │   │
│  └──────────┘    └──────────┘    └──────────────────┘   │
│       │               │                   │              │
│       │               ▼                   ▼              │
│       │         ┌──────────┐       ┌──────────────┐     │
│       │         │ SENTINEL │       │   RECEIPT +   │     │
│       │         │  (Gate)  │       │    LEDGER     │     │
│       │         └──────────┘       └──────────────┘     │
│       │                                   │              │
│       │                                   ▼              │
│       │                            ┌──────────────┐     │
│       └───────────────────────────▶│   MANTIS     │     │
│                                    │  (Observer)  │     │
│                                    └──────────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

Everything inside the trust boundary is governed. Nothing outside the boundary may execute consequential actions. The Gateway (RIO + Sentinel) is the single enforcement point — all interfaces (PWA, CLI, API, Slack) are untrusted clients.

---

## Proof Chain

Every governed action produces a proof chain:

```
Handoff Receipt  ──────┐
(what was transferred)  │
                        ▼
              Action Receipt
              (what happened)
                        │
                        ▼
              Attestation
              (Ed25519 signature)
                        │
                        ▼
              Ledger Entry
              (hash-chained, append-only)
                        │
                        ▼
              Verification Verdict
              (independently checkable)
```

The handoff receipt proves what context, authority, and responsibility were transferred before the action. The action receipt proves what happened during execution. Together they form a complete provenance chain.

---

## Five Syscall Namespaces

| Namespace | Operations | Purpose |
|-----------|-----------|---------|
| `rio.*` | 9 | Governance core: authority, policy, tokens, gates, execution |
| `sentinel.*` | 5 | Anomaly detection: contrast, velocity, invariants, signals |
| `mus.*` | 7 | Cryptographic: receipts, signing, verification, export |
| `ledger.*` | 4 | Storage: append, retrieve, verify chain |
| `mantis.*` | 6 | Learning: decisions, risk scores, coherence, analysis |

Total: 46 operations forming the complete protocol interface.

---

## What Is Implemented vs. Specified

| Layer | Status |
|-------|--------|
| Governance (rio.*) | Implemented — runtime prototype |
| Gate enforcement (sentinel.*) | Implemented — fail-closed |
| Receipts and signing (mus.*) | Implemented — Ed25519 |
| Ledger (ledger.*) | Implemented — WAL + hash chain |
| Learning (mantis.*) | Partial — advisory risk scores only |
| Chronicle | Deferred — not implemented |
| Handoff-Action Binding | Implemented — validator + pipeline enforcement |

---

## Design Principles

1. **Fail-closed by default.** If uncertain, block.
2. **Prove, don't trust.** Cryptographic receipts over access control assumptions.
3. **Human authority is non-delegable.** The system serves the human; it does not replace the human.
4. **Separation of concerns.** Receipt ≠ Attestation ≠ Verification ≠ Ledger ≠ Governance.
5. **No silent expansion.** Context informs but never grants authority.
6. **Observable.** Every state transition, every decision, every outcome is recorded.
