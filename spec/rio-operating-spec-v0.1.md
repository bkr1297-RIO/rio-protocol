# RIO Operating Spec — v0.1

**Status:** Active
**Scope:** Defines the canonical vocabulary, state machine, verdicts, roles, and invariants for the RIO governed execution protocol. This document is the single source of truth for conformance testing.

---

## §1 — Purpose

RIO is a governed execution protocol that sits between AI, humans, and real-world actions. It translates goals into structured intent, evaluates risk and policy, requires approval when necessary, controls execution, verifies outcomes, and generates cryptographically signed receipts recorded in a tamper-evident ledger. The system enforces the rules, not the AI.

This spec defines the canonical model against which any RIO implementation is measured.

---

## §2 — Principals

A RIO system operates with four structural principals. No principal may hold more than one role within a single governed action.

| Role | Symbol | Responsibility |
|------|--------|----------------|
| **Governor** | RIO | Authorizes, evaluates policy, enforces gates |
| **Operating Environment** | ONE | Human interface and operating environment through which governed actions are initiated, reviewed, and monitored |
| **Executor** | Tool / Agent / API / Robot | The adapter layer that performs approved actions — operates inside ONE under RIO governance |
| **Observer** | MANTIS | Records all events, provides advisory learning |

The **Human** is the root authority. The human is not a role within the system — the human is the source of authority that the system serves. The human may act as proposer, approver, or both (with constrained delegation friction).

---

## §3 — Invariants

These properties must hold at all times. Violation of any invariant constitutes a system failure.

**INV-1: Human Root Authority.** The human remains the ultimate authority. No system component may override, bypass, or silently expand human-granted authority.

**INV-2: Fail-Closed.** If any verification step fails, returns an unexpected result, or times out, the system must block execution. The default state is denial.

**INV-3: Proposal Before Movement.** No consequential action may occur without a prior proposal packet that has been presented for review. Movement without proposal is a violation.

**INV-4: Commit ≠ Gate.** Human commitment (COMMITTED) binds authority to a proposal packet. Gate validation (GATE_VALIDATED) confirms the exact execution request still matches the committed packet at execution time. These are distinct governance events and must not be conflated.

**INV-5: Proposer ≠ Approver.** The proposer and approver must be structurally separated. If the same identity holds both roles, constrained delegation friction (cooldown, second-step confirmation) must be enforced and recorded.

**INV-6: Token Lifecycle.** Authorization tokens must be issued after approval, validated before execution, and burned after execution. A token may not be reused.

**INV-7: Receipt Completeness.** Every consequential outcome (success, failure, block, refusal) must produce a canonical receipt containing at minimum: intent_id, approver_id, token_id, policy_hash, execution_result, receipt_hash, previous_receipt_hash, and snapshot_hash.

**INV-8: Ledger Integrity.** The ledger is append-only with SHA-256 hash chain linkage. Each entry references the hash of the previous entry. The chain must be independently verifiable.

**INV-9: Context Cannot Expand Authority.** Operational context (logs, retries, signals, learning) may inform decisions but must never grant or expand permission beyond what the frozen policy snapshot allows.

**INV-10: Learning is Advisory.** The learning loop may adjust advisory risk scores and provide recommendations. It must never silently approve, execute, or bypass governance.

---

## §4 — System Calls

The RIO protocol exposes five namespaces of system calls. These are the canonical API surface.

| Namespace | Responsibility | Key Operations |
|-----------|---------------|----------------|
| `rio.*` | Governance, authorization, gate enforcement | registerRootAuthority, activatePolicy, issueAuthorizationToken, validateAuthorizationToken, enforceGate, processIntent, kernelExecute, enforceTheOneRule, createGenesisRecord |
| `sentinel.*` | Anomaly detection, invariant monitoring | detectContrast, detectVelocityAnomaly, checkSystemInvariants, recordSignal, runSentinelSweep |
| `mus.*` | Receipts, cryptographic signing, export | generateCanonicalReceipt, generateKeypair, signPayload, verifySignature, extractProtocolReceipt, buildChainedLedger, exportReceiptBundle |
| `ledger.*` | Append-only hash chain | appendLedger, getLastLedgerEntry, getAllLedgerEntries, verifyHashChain |
| `mantis.*` | Learning, coherence, advisory | recordDecision, getAdvisoryRiskScore, getLearningSummary, runCoherenceCheck, getCoherenceState, runLearningLoopAnalysis |

See `spec/rio-syscalls-v0.1.md` for the full interface specification.

---

## §5 — Governed Action Lifecycle

A governed action is the atomic unit of work in RIO. Every action that produces a real-world side effect must pass through this lifecycle.

### §5.1 — Complete Governed Action

A governed action is complete only when all of the following conditions are met:

1. Intent created
2. Risk evaluated
3. Proposer ≠ Approver enforced (or constrained delegation recorded)
4. Approval recorded
5. Authorization token issued
6. Token validated before execution
7. Token burned after execution
8. Execution performed
9. Receipt generated with all required fields
10. Receipt signed by Gateway
11. Receipt hash written to ledger
12. Ledger hash chain verifies
13. Learning event recorded

### §5.2 — Three-Loop Architecture

RIO operates on three loops:

**Intake Loop** (Goal → Intent): Raw input is received, interpreted into structured intent, wrapped in a governance packet with hash and metadata, and pre-checked against policy, risk tier, and blast radius.

**Governance Loop** (Policy → Approval → Execution → Verification): The proposal is presented for human review. The human commits authority (or refuses, requests clarification, or holds). If committed, the gate validates the exact execution request against the committed packet. Execution occurs only after gate validation. A receipt is generated and written to the ledger.

**Learning Loop** (Ledger → Policy Improvement): Outcomes are recorded as learning events. Advisory risk scores are adjusted. Coherence checks verify system consistency. Learning is strictly advisory — it cannot approve, execute, or bypass governance.

---

## §6 — Policy

### §6.1 — Policy Snapshot Isolation

The policy snapshot must be constructed and frozen before any operational context is read. The snapshot input is policy only (versioned, hashed). Context enrichment may inform the decision but must not modify the snapshot. The snapshot_hash must be included in the receipt.

### §6.2 — Policy Activation

A policy becomes active only when signed by the root authority. The policy hash is computed over the canonical JSON representation. The root signature is verified using Ed25519 against the registered root authority public key.

---

## §7 — State Machine

Every governed action passes through a subset of the following 16 canonical states.

| State | Description | Outcome Terminal | Lifecycle Terminal |
|-------|-------------|:----------------:|:------------------:|
| SIGNAL | Raw input received — not yet interpreted | No | No |
| INTERPRETED | Input parsed into structured intent | No | No |
| PACKETIZED | Intent wrapped in governance packet with hash + metadata | No | No |
| PRECHECKED | Pre-commit validation complete (policy, risk, blast radius) | No | No |
| REVIEWED | Presented to human for review | No | No |
| COMMITTED | Human has committed authority — authorization bound | No | No |
| CLARIFY | Clarification requested — awaiting additional information | No | No |
| HOLD | Action paused — awaiting condition or human decision | No | No |
| GATE_VALIDATED | Post-commit gate validation passed — ready for execution | No | No |
| EXECUTED | Action executed by the executor | No | No |
| BLOCKED | Action blocked by policy or gate | **Yes** | No |
| REFUSED | Action refused by human decision | **Yes** | No |
| FAILED | Execution attempted but failed | **Yes** | No |
| RECEIPTED | Canonical receipt generated and signed | No | No |
| RECORDED | Receipt written to ledger with hash chain linkage | No | No |
| LEARNED | Learning loop has processed the outcome | No | **Yes** |

**Outcome Terminal** means the action's real-world outcome is decided (it will not execute, or execution has failed). The lifecycle continues through receipt generation and ledger recording.

**Lifecycle Terminal** means the governed action lifecycle is fully complete — no further state transitions occur.

### §7.1 — State Transitions

The canonical happy path is:

```
SIGNAL → INTERPRETED → PACKETIZED → PRECHECKED → REVIEWED → COMMITTED → GATE_VALIDATED → EXECUTED → RECEIPTED → RECORDED → LEARNED
```

Branch paths:

```
REVIEWED → REFUSED                    (human rejects)
REVIEWED → CLARIFY → REVIEWED         (clarification loop)
REVIEWED → HOLD → REVIEWED            (hold and resume)
PRECHECKED → BLOCKED                  (policy denial)
GATE_VALIDATED → FAILED → RECEIPTED   (execution failure)
any → BLOCKED                         (kill switch)
```

### §7.2 — COMMITTED ≠ GATE_VALIDATED

COMMITTED means human authority is bound to the proposal packet. GATE_VALIDATED means the protocol confirmed the exact execution request still matches the committed packet at execution time. A trace must not include GATE_VALIDATED unless:

- There is an explicit gate validation event, or
- A status/context flag proves gate validation occurred, or
- The execution status is EXECUTED or FAILED (which proves a gate attempt)

See `schemas/rio-state-machine-v0.1.json` for the formal JSON representation.

---

## §8 — Authorization Tokens

Authorization tokens are the mechanism by which human authority is transferred to the execution layer.

| Field | Description |
|-------|-------------|
| token_id | Unique identifier |
| intent_id | The intent this token authorizes |
| tool_name | The specific tool authorized |
| args_hash | SHA-256 hash of the authorized arguments |
| policy_hash | Hash of the active policy at issuance |
| issued_at | Timestamp of issuance |
| expires_at | Expiration timestamp |
| max_executions | Maximum number of times this token may be used |
| execution_count | Current execution count |

Tokens must be validated before execution (matching tool, args_hash, policy_hash, not expired, not exhausted, kill switch not active). Tokens must be burned after execution (execution_count incremented, marked consumed if max reached).

---

## §9 — Receipts

Every consequential outcome produces a canonical receipt.

### §9.1 — Required Receipt Fields

| Field | Description |
|-------|-------------|
| intent_id | The governed intent |
| approver_id | Identity that approved |
| token_id | Authorization token used |
| policy_hash | Active policy hash at decision time |
| execution_result | Outcome of execution |
| receipt_hash | SHA-256 hash of the receipt |
| previous_receipt_hash | Hash chain linkage to prior receipt |
| snapshot_hash | Hash of the frozen policy snapshot |
| ledger_entry_id | Reference to the ledger entry |
| handoff_receipt_hash | Hash of the handoff receipt that preceded this action (binding proof) |

### §9.2 — Receipt Signing

Receipts are signed using Ed25519. The signature covers the canonical JSON representation of the receipt. The signing key is the Gateway's Ed25519 private key. Verification uses the corresponding public key.

---

## §10 — Ledger

The ledger is an append-only, hash-chained record of all governance events.

Each entry contains: entryId, entryType, payload (JSON), hash (SHA-256 of entry content), prevHash (hash of previous entry), and timestamp.

The hash chain is independently verifiable: recompute each entry's hash from its content and verify it matches the stored hash, then verify each entry's prevHash matches the previous entry's hash.

---

## §11 — Sentinel

Sentinel is the anomaly detection and invariant monitoring subsystem.

Sentinel may observe, compare, summarize, and notify. Sentinel must not execute, commit, deploy, or modify runtime without explicit human approval. Sentinel operates as autonomous observation with human-gated action.

Key capabilities: contrast detection (behavioral drift), velocity anomaly detection (unusual action frequency), system invariant checking, signal recording, and periodic sweep.

---

## §12 — Verdicts

Every governance decision resolves to exactly one of 8 canonical verdicts.

| Verdict | Meaning | Terminal |
|---------|---------|----------|
| PASS | All checks passed — action may proceed | No |
| WARN | Checks passed with advisory signals — proceed with caution | No |
| CLARIFY | Insufficient information — human must clarify | No |
| HOLD | Action paused — awaiting condition or decision | No |
| BLOCK | Denied by policy or gate — not permitted | Yes |
| REFUSE | Denied by human decision — explicit refusal | Yes |
| FAILED | Execution attempted but failed | Yes |
| INVALID | Structurally invalid — cannot enter pipeline | Yes |

Verdict precedence (highest to lowest): BLOCK > HOLD > WARN > CLARIFY > PASS

---

## §13 — Kill Switch

The kill switch is a global emergency mechanism that immediately revokes all active authority.

When activated: all pending intents are set to KILLED, the proxy user status is set to KILLED, all authorization tokens become invalid (kill switch flag blocks validation), and a ledger entry is recorded.

The kill switch is accessible from every interface and requires no additional approval to activate.

---

## §14 — Write-Ahead Log (WAL)

For delegated execution (adapters executing outside the main transaction), a write-ahead log ensures atomicity:

1. WAL_PREPARED: Record the intent to execute before execution begins
2. Execution occurs
3. WAL_COMMITTED: Record successful execution with receipt
4. WAL_FAILED: Record failure if execution fails

This ensures that even if the system crashes mid-execution, the ledger reflects the true state.

---

## §15 — Constrained Delegation

When the proposer and approver are the same identity:

1. Immediate self-approval is not permitted — a cooldown or second-step confirmation is required
2. The receipt must record this as "Constrained Single-Actor Execution"
3. The delegation_type field must indicate "self" vs "separated"
4. A ledger entry of type DELEGATION_BLOCKED is recorded if the constraint is violated

---

## §16 — Chronicle (Deferred)

Chronicle is the planned human-readable explanation and narrative history layer. It is distinct from the Ledger: the Ledger is the tamper-evident audit record (append-only, hash-chained, cryptographically verifiable). Chronicle provides the human-readable narrative — the "why" behind each governed action, contextual explanations, and decision rationale in natural language. Chronicle is not yet implemented and is explicitly deferred from this spec version. No conformance tests target Chronicle.

---

## §17 — Handoff Receipts

RIO distinguishes between action receipts and handoff receipts.

**Action receipts** prove governed action: what was executed, under what authority, with what outcome.

**Handoff receipts** prove what was transferred before responsibility moved: context, proposal, authority, reliance, and responsibility transferred when work moved between a human, AI, or system.

Handoff receipts are bound to action receipts via the `handoff_receipt_hash` field. An action cannot be valid unless it is bound to the exact interpretation it relied on.

Functions: generateHandoffReceipt(), validateHandoffReceipt(), hashHandoffReceipt(), linkHandoffToActionReceipt(), appendHandoffToLedger().

---

## Appendix A — Conformance

An implementation conforms to this spec when it satisfies all 10 invariants, implements the 16-state lifecycle, produces receipts with all required fields, and maintains ledger integrity.

## Appendix B — State Machine Schema

See `schemas/rio-state-machine-v0.1.json` for the formal JSON representation of the state machine defined in §7.

## Appendix C — Verification Stack

See `spec/rio-verification-stack-v0.1.md` for the layered separation of receipt, attestation, verification, ledger, Chronicle, and governance.
