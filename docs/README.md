# RIO Protocol — Documentation Guide

**What is RIO?**

RIO is a Governance Intelligence System. It sits between AI agents, humans, and real-world actions. Its purpose is to ensure that no consequential action occurs without structured intent, policy evaluation, human authority, controlled execution, cryptographic proof, and tamper-evident recording.

RIO does not replace human judgment. It enforces the conditions under which judgment is honored.

---

## Core Idea

AI systems can propose actions. Humans must retain authority over which actions execute. RIO provides the governance layer that makes this enforceable — not as a policy document, but as a runtime system with cryptographic proof.

The system enforces the rules, not the AI.

---

## What the Protocol Contains

RIO is defined by five canonical artifacts. Together they form a complete, inspectable protocol.

| Artifact | Location | What It Defines |
|----------|----------|-----------------|
| Operating Spec | `spec/rio-operating-spec-v0.1.md` | The rules: 10 invariants, 16 states, 8 verdicts, 4 principals, policy model, token lifecycle, receipt requirements, ledger discipline |
| State Machine | `schemas/rio-state-machine-v0.1.json` | The formal lifecycle: 16 states a governed action passes through from signal to outcome |
| Syscall Interface | `spec/rio-syscalls-v0.1.md` | The API surface: 46 operations across 5 namespaces (rio, sentinel, mus, ledger, mantis) |
| Verification Stack | `spec/rio-verification-stack-v0.1.md` | The proof layers: receipt, attestation, verification, ledger, Chronicle, governance — separated with precision |
| Runtime Tests | `tests/rio-operating-spec-runtime-tests-v0.1.md` | The conformance outline: 73 tests across 9 categories that a compliant implementation must pass |

---

## How RIO Works (Plain Language)

A governed action in RIO follows this path:

1. **Signal.** Something happens — a user request, an AI proposal, a system event.
2. **Interpretation.** The raw input is parsed into structured intent.
3. **Packetization.** The intent is wrapped in a governance packet with a hash and metadata.
4. **Pre-check.** Policy, risk tier, and blast radius are evaluated before any human sees it.
5. **Review.** The proposal is presented to a human for review.
6. **Commitment.** The human commits authority — binding their approval to the exact proposal packet.
7. **Gate Validation.** At execution time, the system confirms the execution request still matches the committed packet.
8. **Execution.** The action is performed through a controlled adapter.
9. **Receipt.** A cryptographic receipt is generated proving what happened.
10. **Ledger.** The receipt hash is written to an append-only, hash-chained ledger.
11. **Verification.** The receipt can be independently verified at any time.
12. **Learning.** The outcome feeds back into advisory risk scoring (never into authority expansion).

If any step fails, the system blocks. This is fail-closed governance.

---

## Key Invariants

These properties must hold at all times. Violation of any invariant constitutes a system failure:

- **Human Root Authority.** The human remains the ultimate authority. No system component may override or bypass human-granted authority.
- **Fail-Closed.** If any verification step fails or times out, execution is blocked. The default state is denial.
- **Proposal Before Movement.** No consequential action may occur without a prior proposal packet presented for review.
- **Proposer ≠ Approver.** Structural separation between who proposes and who approves.
- **Token Lifecycle.** Tokens are issued after approval, validated before execution, burned after execution. No reuse.
- **Receipt Completeness.** Every outcome produces a canonical receipt with all required fields.
- **Ledger Integrity.** Append-only, SHA-256 hash chain. Independently verifiable.
- **Context Cannot Expand Authority.** Operational context may inform decisions but never grants permission.
- **Learning is Advisory.** The learning loop may adjust risk scores. It must never approve or execute.

---

## The Verification Stack

RIO separates six distinct layers. Each has a single responsibility:

| Layer | Responsibility |
|-------|---------------|
| Receipt | Records what happened |
| Attestation | Binds the receipt to a signer via cryptographic signature |
| Verification | Checks the receipt for validity |
| Ledger | Preserves the record in tamper-evident storage |
| Chronicle | Explains in human terms (deferred — not yet implemented) |
| Governance | Uses verification outcome to allow or block consequence |

> Receipt is not verification. Receipt is the object verification acts on.

---

## The Five Namespaces

RIO exposes its functionality through five syscall namespaces:

- **rio.*** — Governance, authorization, gate enforcement
- **sentinel.*** — Anomaly detection, invariant monitoring
- **mus.*** — Receipts, cryptographic signing, export
- **ledger.*** — Append-only hash chain operations
- **mantis.*** — Learning, coherence, advisory

---

## Where to Start

| If you want to... | Read this |
|-------------------|-----------|
| Understand the rules | `spec/rio-operating-spec-v0.1.md` |
| See the state machine | `schemas/rio-state-machine-v0.1.json` |
| Understand the API surface | `spec/rio-syscalls-v0.1.md` |
| Understand proof separation | `spec/rio-verification-stack-v0.1.md` |
| See a complete example | `examples/minimal-conformance-example.md` |
| Run verification | `VERIFY_THIS_SYSTEM.md` |
| Check conformance levels | `spec/RIO_CONFORMANCE_v2.3.0.md` |

---

## Draft Promotion Packets

The following documents are review surfaces only. They do not modify the canonical protocol baseline and should not be read as implementation, deployment, external-validation, or conformance claims.

| Draft packet | Location | Purpose |
|-------------|----------|---------|
| Naming Promotion Index v0.1 | `docs/architecture/naming-promotion-index-v0.1.md` | Index of draft names and promotion status |
| Precision by Friction v0.1 | `docs/architecture/precision-by-friction-v0.1.md` | Explains generator-governor-gate-receipt-learning as bounded precision |
| Governed Self-Observation Layer v0.1 | `docs/architecture/governed-self-observation-layer-v0.1.md` | Failure detection + coherence monitoring + receipt validation |
| Adaptive Trust Envelope v0.1 | `docs/architecture/adaptive-trust-envelope-v0.1.md` | Relationship-aware friction without authority expansion |
| Embodied Co-Regulation Layer v0.1 | `docs/architecture/embodied-co-regulation-layer-v0.1.md` | Robots, exosuits, prosthetics, homes, and communities under governance |
| Human Control Packet v0.1 | `spec/human-control-packet-v0.1.md` | Minimal human-authored boundary packet |
| Failure Modes Catalog v0.1 | `docs/failure-modes/one-rio-muss-failure-modes-v0.1.md` | How the system breaks and what inputs reduce breakage |
| Gemini Context Packet v0.1 | `docs/handoff/gemini-context-packet-v0.1.md` | Bounded packet for external model review |

---

## What RIO Is Not

- RIO is not an AI model.
- RIO is not a chatbot framework.
- RIO is not a policy document that hopes for compliance.
- RIO is not a monitoring dashboard.

RIO is a runtime governance system with cryptographic enforcement. It proves what happened, who authorized it, and whether the rules were followed — at the protocol level, not the trust level.

---

## Current Status

RIO has a working prototype implementation (`rio-proxy`) that demonstrates:

- Governed action execution with receipt and ledger recording (live, zero-mock)
- HIGH-risk action boundary enforcement (fail-closed at connector layer)
- Handoff-to-action receipt binding (no action without prior interpretation proof)
- 2,393+ automated tests covering the governance pipeline
- Ed25519 cryptographic signing and verification
- WAL-disciplined ledger with tamper detection

Chronicle remains deferred. The system is prototype-grade, not production-deployed.
