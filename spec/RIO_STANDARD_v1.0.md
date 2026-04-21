# RIO Standard v1.0

**Status:** Authoritative
**Version:** 1.0
**Date:** 2026-04-21

> `RIO_STANDARD_v1.0.md` is the authoritative specification for the RIO protocol. All other documents — architecture, implementation, governance — derive from this standard.

---

## 1. What RIO Is

RIO is a governed execution system that sits between AI, humans, and real-world actions. It translates goals into structured intent, evaluates risk and policy, requires approval when necessary, controls execution, verifies outcomes, and generates cryptographically signed receipts recorded in a tamper-evident ledger.

The system enforces the rules, not the AI.

> A system that organizes your data, understands your patterns, proposes actions on your behalf, requires your approval for risk, executes safely, and records proof of everything.

---

## 2. Canonical Invariant

The RIO protocol is defined by one invariant that cannot be relaxed, overridden, or deferred:

> **No digital action occurs without explicit authorization, and all actions produce verifiable cryptographic proof.**

Every protocol mechanism exists to enforce this invariant. If a mechanism does not contribute to enforcement, it is not part of the standard.

---

## 3. The Five Layers

| Layer | Name | Function | Prohibition |
|-------|------|----------|-------------|
| 1 | Cognition | AI proposes actions based on context and patterns | Cannot execute |
| 2 | Governance | Evaluates risk, enforces policy, routes for approval | Cannot execute directly |
| 3 | Execution | Performs approved actions through connectors | Cannot approve |
| 4 | Witness | Records receipts, maintains ledger, enables verification | Cannot execute or approve |
| 5 | Meta-Governance | Controls policy changes, learning, and system rules | Cannot execute actions |

---

## 4. The Three-Loop Architecture

**Intake Loop (Goal to Intent):** The user expresses a goal. The Cognition layer translates the goal into a structured intent with action type, target, parameters, and context. The intent enters the governance pipeline.

**Governance Loop (Intent to Receipt):** The intent is risk-assessed, routed for approval if required, executed through the appropriate connector, verified, and a receipt is generated and written to the ledger.

**Learning Loop (Ledger to Policy):** The Witness layer observes patterns in the ledger. Observations are escalated to Meta-Governance, which decides whether and how the system should change. Learning flows through Meta-Governance before returning to Governance.

---

## 5. The Governed Action Pipeline

Every governed action passes through a 7-stage pipeline. If any stage fails, the pipeline halts. The system fails closed. No partial executions are permitted.

| Stage | Layer | Input | Output |
|-------|-------|-------|--------|
| 1. Submit | Cognition | Natural language goal | Structured intent |
| 2. Govern | Governance | Intent | Risk assessment + routing decision |
| 3. Authorize | Governance | Risk assessment | Approval or denial (human for HIGH/CRITICAL) |
| 4. Execute | Execution | Approved intent + token | Execution result |
| 5. Verify | Witness | Execution result | Verification status |
| 6. Receipt | Witness | All pipeline artifacts | Cryptographic receipt |
| 7. Commit | Witness | Receipt | Ledger entry (hash-chained) |

---

## 6. The Three Powers

No single component may hold more than one power. This is a structural invariant.

| Power | Holder | Function | Boundary |
|-------|--------|----------|----------|
| Observation | Witness / Intake | See everything, decide nothing | May read and classify, must not approve or execute |
| Governance | RIO / Human | Evaluate risk, approve or deny | May approve or deny, must not execute |
| Execution | Gateway | Perform approved actions | May execute with valid token, must not approve |

The handoff between powers is explicit and cryptographic. Observation produces a classified intent. Governance produces an approval with a signed token. Execution consumes the token and produces a receipt. The receipt proves the handoff occurred correctly.

---

## 7. Protocol Invariants

These are the eight invariants that any RIO-compliant implementation must enforce:

| ID | Invariant | Requirement |
|----|-----------|-------------|
| INV-01 | Human authority preserved | A human can override, halt, or reverse any AI-initiated action at any point |
| INV-02 | Every action is logged | Every action (approved, denied, or failed) produces a signed receipt and a ledger entry |
| INV-03 | Policy compliance | No action executes without passing the policy engine evaluation |
| INV-04 | Scope integrity | The executed action matches the original intent — no scope creep |
| INV-05 | Tool permission check | The system verifies that the requested tool/action is within the agent's permitted scope |
| INV-06 | Fail-closed execution | If any gate fails, the system denies the action and produces a denial receipt |
| INV-07 | Denial receipts | Denied actions produce full receipts with `decision=block` and `execution_status=BLOCKED` |
| INV-08 | Ledger immutability | Once a ledger entry is written, it cannot be modified or deleted |

---

## 8. Cryptographic Mechanisms

| Mechanism | Algorithm | Purpose |
|-----------|-----------|---------|
| Receipt signing | Ed25519 | Binds approval to human identity |
| Receipt hashing | SHA-256 | Proves integrity of pipeline artifacts |
| Ledger chain | SHA-256 hash chain | Proves no records have been altered or removed |
| Token binding | JWT (Ed25519-signed) | Binds execution authorization to specific intent |
| Replay prevention | Single-use nonce registry | Prevents reuse of authorization tokens |
| TTL enforcement | Time-bound tokens (default 300s) | Prevents stale authorizations |

---

## 9. Risk Classification

| Risk Level | Blast Radius | Approval Required | Examples |
|------------|-------------|-------------------|----------|
| LOW | 1-3 | Auto-approve (policy-dependent) | Read-only queries, status checks |
| MEDIUM | 4-6 | Auto-approve with logging | Calendar events, document edits |
| HIGH | 7-9 | Human approval required | Email sending, file sharing, API calls |
| CRITICAL | 10 | Human approval + enhanced verification | Financial transactions, account changes, bulk operations |

---

## 10. Verification Model

An independent party can audit the system using only the public key and the ledger:

1. **Recompute the hash chain** for every entry. Any mismatch proves tampering.
2. **Verify receipt signatures** against the public key. Invalid signature means forgery.
3. **Check the three-hash binding** (intent, action, verification). Mismatch means drift.
4. **Test replay protection.** Submit a used nonce — the system must reject it.
5. **Test TTL enforcement.** Submit an expired token — the gate must reject it.
6. **Test fail-closed behavior.** Attempt execution without a token — the gate must remain locked.

---

## 11. Conformance

Compliance with this standard is defined in [RIO_CONFORMANCE_v1.0.md](RIO_CONFORMANCE_v1.0.md). Compliance is not self-declared; it is demonstrated by passing the conformance test suite.

---

## 12. Authority

This document is the authoritative specification for the RIO protocol. Where any other document conflicts with this standard, this standard governs.

| Document | Role |
|----------|------|
| `RIO_STANDARD_v1.0.md` | Authoritative specification (this document) |
| `RIO_CONFORMANCE_v1.0.md` | Defines how compliance is verified |
| `SYSTEM_RUNTIME_MAP.md` | Defines how the spec maps to a running system (in `rio-system`) |
