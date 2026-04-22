# FAQ — RIO Protocol v1.0

## What is RIO?

RIO is a governed execution protocol. It sits between AI systems, humans, and real-world actions. Every action passes through an 8-stage pipeline: intake, canonical intent, risk evaluation, policy constraints, authorization, execution, attestation, and verification. The output is a cryptographically signed receipt recorded in a hash-chained ledger.

## What is RIO not?

RIO is not an AI model. It does not generate text, make predictions, or learn from data. It is not an agent framework. It does not decide what actions to take. It is not a chatbot, assistant, or automation platform.

RIO is infrastructure. It enforces rules around actions that other systems propose.

## How does RIO differ from an AI agent?

An AI agent decides what to do. RIO decides whether it is allowed to happen, records what happened, and makes the record independently verifiable. An agent without RIO can act without authorization, without audit, and without verification. An agent with RIO cannot.

## How does RIO differ from an AI model?

A model produces outputs (text, code, decisions). RIO does not produce outputs. RIO governs the execution of actions that a model may have proposed. The model is upstream of RIO. RIO is the control plane between the model's proposal and the real-world effect.

## What does a receipt prove?

A receipt proves that the system produced a record of a governed action and that the record has not been altered since it was created. It includes the intent hash (what was authorized), the result hash (what was executed), the policy hash (which rules applied), and an Ed25519 signature.

A receipt does not independently prove that the action occurred in the external world.

## What does the ledger prove?

The ledger proves ordering and completeness. Each entry contains a hash of the previous entry. Any deletion, modification, or reordering breaks the chain and is detectable by recomputing the hashes from genesis forward.

## What is the genesis hash?

The first entry in the ledger uses `SHA-256("GENESIS")` as its previous hash. This value is `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a`. It is deterministic and verifiable.

## What signing algorithms does RIO use?

Receipts use Ed25519. Gateway-level tokens use ECDSA-secp256k1. See `spec/SIGNING_ALGORITHMS.md` for the dual-signing architecture.

## What are the conformance levels?

There are 7 levels, defined in `spec/RIO_CONFORMANCE_v2.3.0.md`. Level 1 requires correct receipt generation. Level 7 requires Ed25519 signatures over a governed receipt with full hash-chain binding.

## Is this a production system?

No. This repository defines the protocol specification and provides reference verification logic. It is not a production deployment. See `docs/KNOWN_LIMITATIONS.md` for explicit boundaries.

## Where is the reference implementation?

The reference implementation is in a separate repository: [rio-reference-impl](https://github.com/bkr1297-RIO/rio-reference-impl).

## How do I verify the system?

Follow the 5-step process in [VERIFY_THIS_SYSTEM.md](../VERIFY_THIS_SYSTEM.md). It requires only Python and pynacl. No external repos needed.
