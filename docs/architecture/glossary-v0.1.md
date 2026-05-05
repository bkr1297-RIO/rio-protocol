# Canonical Glossary — v0.1

## Core Terms

| Term | Definition |
|------|------------|
| **ONE** | Human-led protocol operating environment. ONE is not merely an AI agent or chatbot. It is the broader human-led operating environment in which AI tools, agents, protocols, governance, and receipts can operate under human authority. ONE turns AI language into named, versioned protocols; protocols into human-led action, reflection, or decision; human reports into receipts; and receipts into accountable learning. |
| **MUSS** | Sovereignty container. The system class that holds the human's governed intelligence stack. MUSS is not the OS — it is the bounded container within which ONE operates. |
| **RIO** | Consequence governance and execution control plane. Sits between intent and consequence, enforcing that nothing executes without structured approval and producing verifiable proof of every crossing. |
| **MUS Unit** | Bounded operator and receipt-producing unit. A local instance that holds identity, keypair, ledger, and nonce store. Each MUS Unit can create, sign, and verify receipts independently. |
| **Receipt** | Proof primitive. A cryptographically signed record of a governed event, such as an approval, block, refusal, failure, execution, or verification outcome. A receipt proves the event was recorded, signed, and linked into the proof chain; it does not prove the action was wise, legal, moral, or externally certified. |
| **Ledger** | Append-only, hash-chained sequence of receipt hashes. Each entry links to the previous via `previous_receipt_hash`, creating a tamper-evident chain. |
| **MANTIS** | Observation, contrast, and pattern witness. Watches system events, detects anomalies, and surfaces patterns for human review. Does not authorize, approve, or execute. |
| **Protocol** | A finite, explicit set of rules that determines which transitions are valid between defined states. Not a prompt, workflow, suggestion, habit, or intention. See `docs/architecture/protocol-definition-v0.1.md` for the full definition. |
| **Human Protocol Runtime** | The layer where AI-supported language becomes human-led practice, and the human's report becomes governed data for future precision. Guardrail: learning improves support. It does not create permission. |
| **Governed Intelligence System** | A system in which AI capabilities operate under explicit governance: human authority, protocol constraints, receipt verification, and consequence control. Intelligence is not ungoverned; it operates within defined boundaries. |
| **Commit** | The protected human act of binding authority to a proposed consequential crossing. A Commit may authorize movement into RIO governance, execution, refusal, hold, or receipt flow. The Commit is not the execution itself; it is the human authorization point before consequence. |
| **Consequential Crossing** | The boundary between intent and real-world effect. Every action that crosses from "proposed" to "executed" is a consequential crossing. RIO governs these crossings. |
| **Learning / Permission Boundary** | A governance principle stating that learning may improve future support, surfacing, protocol suggestions, or precision, but it never creates consent, authorization, standing permission, or authority transfer. Learning improves support. It does not create permission. |
| **Proof-Status Ladder** | The honest labeling system for proof weight. See below. |

## Proof-Status Ladder

| Level | Label | Meaning |
|-------|-------|---------|
| 1 | Prompt Run | Protocol activated in conversation |
| 2 | Human Recorded | Human logged what happened |
| 3 | Structured Packet | Event converted to schema / JSON |
| 4 | Receipt Created | Packet signed with Ed25519 |
| 5 | Ledger Verified | Signature and hash chain verified |

## Usage Rule

Apply labels honestly. Do not claim a higher proof status than what
actually occurred.

- Do not claim "Receipt Created" unless a cryptographic signature exists.
- Do not claim "Ledger Verified" unless actual receipt-engine chain
  verification occurred.

Honest proof labeling is a governance requirement, not a style preference.

---

## Honest Status

This document describes architecture that is being built. Some components
are operational and tested. Others are defined but not yet implemented.
The proof-status ladder applies: do not claim a higher status than what
has actually been verified.

The human remains the source of meaning, consent, authority, and
accountability.
