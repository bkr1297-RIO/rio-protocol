# RIO: Runtime Intelligence Orchestration

## A Cryptographic Protocol for Governed AI Execution

**Author / Architect:** Brian K. Rasmussen

**Version:** 2.0.0 — March 2026

---

## 1. Abstract

Runtime Intelligence Orchestration (RIO) is a fail-closed authorization and audit protocol designed to govern autonomous AI agents. As AI systems transition from passive advisors to active participants in digital environments — capable of moving funds, managing infrastructure, and accessing sensitive data — the risk of unaligned or malicious execution increases.

RIO addresses this by decoupling the "intelligence" of the agent from the "authority" to execute. Built on a **Three-Loop Architecture** (Intake/Discovery, Execution/Governance, Learning), RIO translates goals into structured intents, enforces policy and approvals before execution, controls and verifies actions, generates v2 cryptographic receipts with intent_hash, action_hash, and verification_hash, and maintains an immutable signed ledger. The Learning Loop feeds outcomes back into policy refinement without bypassing governance.

---

## 2. Introduction

The rapid advancement of Large Language Models (LLMs) has birthed a new era of autonomous agents. These agents are no longer confined to chat interfaces; they are integrated into business workflows via APIs, database connectors, and cloud infrastructure. However, this integration introduces a critical "speed asymmetry": AI can propose and attempt actions at machine speed, while human oversight remains at human speed.

Traditional security models — such as prompt engineering, system instructions, or model alignment — are advisory. They rely on the AI's "willingness" to follow rules. In a production environment, this is insufficient. A single hallucination or prompt injection can lead to irreversible consequences, such as unauthorized financial transfers or data breaches.

RIO shifts the paradigm from advisory to structural governance. It treats AI as an untrusted requester and places a hard execution gate in front of every sensitive action. By requiring a cryptographic "proof of approval" at the moment of execution, RIO ensures that the human remains the ultimate authority, without sacrificing the efficiency of AI-driven orchestration.

---

## 3. Three-Loop Architecture

RIO is built on a **Three-Loop Architecture** that governs the complete lifecycle of AI-driven actions:

### Intake / Discovery Loop

The Intake / Discovery Loop translates vague goals into structured intents before governance begins. It validates incoming requests, detects missing information, uses AI-assisted refinement to clarify ambiguous goals, and produces a well-defined structured intent. Also known as the **Intake Translation Layer**, **Universal Grammar Layer**, or **Goal-to-Intent Layer**.

**Constraints:**

- Must produce a well-defined structured intent before governance starts
- AI refinement is advisory — the human or system confirms the final intent

### Execution / Governance Loop

The Execution / Governance Loop controls and authorizes all actions before execution. It enforces policy evaluation, risk scoring, human approval workflows, execution gating, post-execution verification (computing intent_hash, action_hash, and verification_hash), v2 receipt generation, and signed ledger recording.

**Constraints:**

- No execution without authorization
- All actions must produce v2 receipts (including denials)
- All receipts must be recorded in the signed ledger

### Learning Loop

The Learning Loop improves future decisions and governance policies. It analyzes patterns from the audit trail, proposes policy updates, and enables replay/simulation.

**Constraints:**

- Learning cannot bypass governance
- Learning cannot execute actions directly
- Policy updates must go through governance before deployment

The system is **fail-closed by design**. If any component cannot positively verify a required condition, the execution gate remains locked. This ensures that no action is ever taken in an unrecorded or unauthorized state.

---

## 4. Core Design Principles

| Principle | Description |
|---|---|
| **Fail-Closed** | Default state is "deny." Every gate blocks unless explicitly opened. |
| **Structural Enforcement** | Rules are enforced by architecture, not by AI compliance. |
| **Cryptographic Proof** | Every action requires a signed, verifiable proof of authorization. |
| **Complete Audit Trail** | Every decision — approval or denial — produces a v2 receipt. |
| **Human Authority** | Humans define policies and approve high-risk actions. AI cannot override. |
| **Three-Loop Separation** | Intake, Execution, and Learning are structurally separated loops. |

---

## 5. The Governed Execution Pipeline

RIO enforces governance through the pipeline within the Execution/Governance Loop. Each stage produces a specific data structure that is passed to the next, ensuring a continuous chain of custody:

1. **Intake** — The AI agent submits a raw intent (or vague goal, which is refined by the Intake/Discovery Loop).
2. **Discovery & Refinement** — If the request is vague, AI-assisted refinement produces a structured intent.
3. **Classification** — The system identifies the action type and assigns a risk category.
4. **Policy & Risk Evaluation** — The Policy Engine checks the intent against active rules. A risk score is calculated.
5. **Authorization** — If the risk exceeds the threshold, a human approver is notified. Upon approval, an Execution Token is generated.
6. **Execution Gate** — The gate verifies the token signature, timestamp, nonce, and kill switch.
6b. **Post-Execution Verification** — Computes intent_hash, action_hash, and verification_hash (SHA-256) to cryptographically bind intent to action.
7. **v2 Receipt Generation** — A signed receipt is generated containing all hashes, risk data, policy decision, and three ISO 8601 timestamps.
8. **v2 Ledger Entry** — The receipt is recorded in the signed hash-chained ledger with its own ledger_signature.

**Denial receipts** are generated for blocked or denied actions, ensuring the audit trail covers every decision — not just successful executions.

---

## 6. System Invariants

The RIO protocol is governed by ten core invariants that must be maintained at all times:

1. **No Execution Without Authorization** — No action can be performed unless a valid, unconsumed Execution Token is presented.
2. **No Authorization Without Policy Check** — An Execution Token can only be generated after the Policy Engine has evaluated the intent.
3. **Fail-Closed Enforcement** — Any failure in a dependency must result in a blocked action.
4. **Single-Use Approvals** — Every Execution Token and its associated signature are single-use.
5. **Cryptographic Binding** — The signature must be bound to the exact payload presented for approval.
6. **Timestamp Freshness** — Execution Tokens have a maximum lifespan (default 300s).
7. **Every Action Produces a Receipt** — Every execution attempt, whether successful or blocked, must generate a cryptographic receipt.
8. **Tamper-Evident Audit Trail** — All receipts must be recorded in a hash-chained ledger.
9. **Identity Attribution** — Every action must be attributed to both the requesting agent and the authorizing human.
10. **Immutable History** — Ledger entries cannot be modified or deleted.

---

## 7. Cryptographic Audit Model (v2)

RIO v2 uses a multi-layered cryptographic model to ensure that the audit trail is both authentic and tamper-evident.

### v2 Receipt Structure

A v2 receipt is a JSON object containing:

| Field | Description |
|---|---|
| receipt_id | Unique identifier for the receipt |
| intent_id | Reference to the original intent |
| action | The action that was requested |
| requester | The agent or entity that requested the action |
| approver | The human who approved (or null for denials) |
| decision | "approved" or "denied" |
| execution_status | "EXECUTED", "BLOCKED", etc. |
| risk_score | Numeric risk assessment (0-100) |
| risk_level | "LOW", "MEDIUM", "HIGH", "CRITICAL" |
| policy_decision | "ALLOW", "BLOCK", "REQUIRE_APPROVAL" |
| intent_hash | SHA-256 of intent + action + requester + timestamp |
| action_hash | SHA-256 of action + parameters |
| verification_hash | SHA-256 of intent_hash + action_hash + execution_status |
| verification_status | "verified", "failed", or "skipped" |
| timestamp_request | ISO 8601 timestamp of the original request |
| timestamp_approval | ISO 8601 timestamp of approval |
| timestamp_execution | ISO 8601 timestamp of execution |
| receipt_hash | SHA-256 hash of the receipt contents |
| signature | Ed25519 signature over the receipt |
| previous_hash | Hash of the previous receipt (chain link) |
| protocol_version | "v2" |

### v2 Ledger Structure

The v2 ledger is a signed hash chain where each entry E_n contains:

| Field | Description |
|---|---|
| block_id | Unique block identifier |
| receipt_id | Reference to the receipt |
| receipt_hash | Hash of the associated receipt |
| previous_hash | Hash of the previous ledger entry (H_(n-1)) |
| current_hash | H_n = SHA256(E_n.data + H_(n-1)) |
| ledger_signature | Ed25519 signature over the entry |
| protocol_version | "v2" |

This structure ensures that any modification to any entry invalidates all subsequent hashes, and the per-entry signature provides independent verification. The **Receipt Verifier** and **Ledger Verifier** enable independent audit of individual receipts and the full chain.

---

## 8. Threat Model

RIO is designed to mitigate critical threats in autonomous AI environments:

| Threat | Mitigation |
|---|---|
| Unauthorized Execution | Service boundary + service-to-service auth |
| Ledger Tampering | Hash-chained ledger entries with per-entry signatures |
| Token Reuse | Single-use nonce/signature registry |
| Privilege Escalation | Independent ECDSA signature verification |
| Kill Switch Bypass | Fail-closed design |
| Missing Audit Trail | Ledger write as a prerequisite for execution |

---

## 9. Governance Model

Policies are defined as a set of rules that map actions and parameters to risk levels. The engine evaluates intents in real-time, returning a verdict of ALLOW, BLOCK, or REQUIRE_APPROVAL.

### Risk Scoring

Risk is calculated using a 4-component scoring model:

- **Base Risk** — Inherent risk of the action type
- **Role Modifier** — Adjusts based on the agent's role
- **Amount Modifier** — Scales based on financial or data volume
- **Target Modifier** — Adjusts based on target system sensitivity

### Policy Lifecycle

Policies follow a strict versioning lifecycle:

PROPOSED → APPROVED → ACTIVATED → INACTIVE (or ROLLED_BACK)

Only one policy version can be ACTIVATED at any time, ensuring deterministic evaluation.

---

## 10. Execution Token Lifecycle

The Execution Token is the cryptographic artifact that bridges human approval and machine execution:

1. **Created** — Generated after policy check determines approval is required
2. **Pending** — Awaiting human decision
3. **Approved** — Human approves; token is signed with Ed25519
4. **Consumed** — Token is presented at the execution gate and verified
5. **Expired** — Token exceeds its TTL (default 300s) without being consumed

A consumed token cannot be reused. An expired token cannot be consumed. This ensures that every execution is backed by a fresh, explicit human decision.

---

## 11. Learning Loop

The Learning Loop is the third loop in RIO's Three-Loop Architecture. It records all system interactions in a **Governed Corpus**, providing a rich dataset for learning and policy refinement.

### Replay Engine

The Replay Engine can replay historical intents through the pipeline in three modes:

- **Exact Replay** — Verifies the system produces the same result
- **Modified Policy** — Simulates how a new policy would have handled past intents
- **Modified Role** — Tests how different role assignments would change outcomes

### Policy Improvement Loop

The Policy Improvement Loop follows four steps:

1. **Record** — Capture intents and outcomes
2. **Analyze** — Identify patterns of friction or risk
3. **Simulate** — Test new rules against the corpus
4. **Deploy** — Activate refined policies with confidence

Critically, the Learning Loop **cannot bypass governance**: all policy updates must go through the Execution/Governance Loop before deployment, and the Learning Loop cannot execute actions directly.

---

## 12. Test Harness

The RIO protocol includes a comprehensive test harness with **57 automated tests** across 6 test suites:

| Suite | Tests | Coverage |
|---|---|---|
| Core Pipeline | 15 | Intent creation, policy evaluation, authorization, execution |
| Cryptographic Verification | 10 | Signature generation, verification, hash chain integrity |
| Denial & Edge Cases | 8 | Blocked actions, expired tokens, kill switch |
| Audit & Traceability | 7 | Receipt generation, ledger recording, audit log |
| Governance Model | 7 | Policy lifecycle, risk scoring, role-based access |
| v2 Receipt System | 10 | v2 receipts, hash verification, ledger chain, denial receipts |

All tests are deterministic and can be run in isolation or as a full suite.

---

## 13. Enterprise Use Cases

**Invoice Payment Approval** — A finance agent identifies an outstanding invoice. RIO intercepts the payment request, requiring a Manager's approval for any amount over $1,000.

**GDPR Data Deletion** — An agent tasked with data privacy receives a deletion request. RIO ensures the deletion is logged and verified against the correct user ID before execution.

**Production Deployment** — A DevOps agent proposes a code deployment. RIO requires a Director-level signature, ensuring that no code reaches production without a human "go" decision.

**Access Provisioning** — An HR agent requests system access for a new hire. RIO validates the request against the employee's role and requires Admin approval for privileged access.

**Agent-to-Agent Delegation** — A personal assistant agent asks a travel agent to book a flight. RIO gates the final payment, ensuring the user approves the cost and itinerary.

---

## 14. Conclusion

RIO provides the missing link in AI safety: a governed AI control plane built on a Three-Loop Architecture that translates goals into structured intents, enforces policy and approvals before execution, controls and verifies actions, generates v2 cryptographic receipts, maintains an immutable signed ledger, and learns from every decision over time. By decoupling intent from execution and anchoring every action in a cryptographic audit trail, RIO enables organizations to deploy autonomous agents with confidence. Governance does not have to be a bottleneck — it can be a verifiable, tamper-evident, and automated part of the execution itself.

---

**Repository:** [github.com/bkr1297-RIO/rio-protocol](https://github.com/bkr1297-RIO/rio-protocol)

**Protocol Version:** 2.0.0

**Architecture:** Three-Loop (Intake/Discovery, Execution/Governance, Learning)

**Test Coverage:** 57/57 tests passing
