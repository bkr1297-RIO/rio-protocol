# RIO Verification Stack — v0.1

**Status:** Draft — Additive Clarification (Patch Pack 5A)
**Date:** 2026-05-04
**Author:** B-Rass (RIO Architect)
**Scope:** Architecture language clarification only. No runtime, schema, or policy changes.

---

## §1 — Purpose

External review identified that the current RIO documentation compresses proof, receipt, verification, and audit into a single conceptual layer. This document separates those roles with technical precision so that a verification-oriented reviewer would recognize the stack as well-formed.

This is not a rebuild. This is not a runtime change. This is a clarification of architecture language and mapping.

---

## §2 — Core Correction

> **Receipt is not verification. Receipt is the object verification acts on.**

The following six concepts are distinct layers in the RIO architecture. Each has a single responsibility:

| Layer | Role | Single Responsibility |
|-------|------|----------------------|
| Receipt | Record of claim + evidence | Captures what happened, who was involved, and what was produced |
| Attestation | Signature proving origin and integrity | Binds a receipt to a specific signer at a specific time |
| Verification | Process that checks the receipt | Evaluates structural validity, signature integrity, and chain consistency |
| Ledger | Preserves the record | Append-only, hash-chained, tamper-evident storage |
| Audit / Chronicle | Human-readable explanation layer | Provides narrative context, decision rationale, and searchable history |
| Governance | Uses verification outcome to allow or block consequence | Makes the decision that changes what can happen next |

> **Receipts record. Attestations bind. Verification checks. Ledgers preserve. Chronicle explains. Governance decides consequence.**

---

## §3 — Definitions

**Receipt.** A structured data object that records a claim together with its supporting evidence. A receipt contains: the identity of the action, the actors involved, the parameters used, the outcome produced, and the hashes that bind these elements together. A receipt is inert — it asserts nothing about its own validity. It is the raw material that verification acts upon.

**Attestation.** A cryptographic signature applied to a receipt (or to a subset of its fields) by a known signer. The attestation binds the receipt content to a specific identity and timestamp. In RIO, attestation is performed using Ed25519 signatures. An attested receipt is stronger than an unattested receipt, but attestation alone does not constitute verification — it only proves that a specific key holder signed a specific payload at a specific time.

**Verification.** The process that examines a receipt and determines its validity status. Verification checks structural completeness (all required fields present), signature integrity (attestation valid against known public key), temporal validity (not expired, not replayed), and chain consistency (previous hashes link correctly). Verification produces a verdict, not a receipt. Verification is the consumer of receipts, not the producer.

**Ledger.** The append-only, hash-chained, tamper-evident storage layer that preserves receipts and their verification outcomes. The ledger does not verify — it stores. The ledger's integrity comes from its hash chain: each entry includes the hash of the previous entry, making retroactive modification detectable. The ledger is the persistence guarantee.

**Audit / Chronicle.** The human-readable explanation layer that sits above the ledger. Chronicle provides narrative context: why a decision was made, what the human intent was, and how the outcome relates to the original goal. Chronicle is distinct from the ledger: the ledger is cryptographic proof; Chronicle is human explanation. Chronicle is explicitly deferred in the current implementation.

**Governance Consequence.** The decision layer that uses verification outcomes to allow or block real-world consequence. Governance does not verify — it receives verification verdicts and acts on them. A VERIFIED verdict may lead to execution. A FAILED verdict blocks execution. Governance is the consumer of verification, not the producer.

---

## §4 — Clean Flow

The following sequence shows how an event moves through the verification stack. Each arrow represents a handoff between layers:

```
Event / Handoff
  │
  ▼
Receipt           ← Record what happened (generateWitnessReceipt)
  │
  ▼
Attestation       ← Sign the receipt (signPayload / Ed25519)
  │
  ▼
Verification      ← Check the receipt (verifyIntentEnvelope / verifySignature)
  │
  ▼
Ledger            ← Preserve the record (appendLedger / WAL discipline)
  │
  ▼
Chronicle         ← Explain in human terms (DEFERRED — not implemented)
  │
  ▼
Governance        ← Decide consequence (evaluateGovernance / executeGatePreflight)
```

The flow is strictly ordered. No layer may skip its predecessor:

- A receipt cannot be attested without first being generated.
- An attestation cannot be verified without the receipt it covers.
- A verification verdict cannot be stored without the ledger.
- A governance decision cannot be made without a verification verdict.

---

## §5 — Verification Status Levels

Verification produces one of the following status levels. These are conceptual and represent increasing confidence in the receipt's validity:

| Status | Meaning | What Has Been Checked |
|--------|---------|----------------------|
| UNVERIFIED | No verification has been performed | Receipt exists but has not been examined |
| STRUCTURALLY_VALID | Schema and required fields pass | All required fields present, types correct, non-empty |
| SIGNATURE_VALID | Attestation signature verified | Ed25519 signature matches known public key for the claimed signer |
| VERIFIED | Full verification passed | Structural + signature + temporal + nonce + chain consistency all pass |
| FAILED | Verification found a defect | One or more checks failed; failure reasons recorded |

The current implementation uses a binary `verified: boolean` field in `VerificationResult`. The status levels above represent the conceptual granularity that a future implementation could expose. The existing `schema_valid`, `auth_valid`, `signature_valid`, `ttl_valid`, `nonce_valid`, and `replay_check` fields in `VerificationResult` already capture the individual checks — the composite status level is derivable from them.

---

## §6 — Current Implementation Mapping

The following table maps each layer to its current implementation status in `rio-proxy/main`:

| Layer | Implementation Status | Code Location | Notes |
|-------|----------------------|---------------|-------|
| Receipt (Action) | **Implemented** | `server/rio/controlPlane.ts` → `generateWitnessReceipt()` | Produces `WitnessReceipt` with receipt_id, hashes, chain_of_custody, timestamp |
| Receipt (Handoff) | **Implemented** | `server/rio/handoffReceipt.ts` → `generateHandoffReceipt()` | Produces `HandoffReceipt` with 17 fields, SHA-256 hash, chain linking |
| Attestation (Ed25519) | **Implemented** | `server/rio/ed25519.ts` → `signPayload()`, `signAuthorization()` | Ed25519 signing via @noble/ed25519; keypair from env or derived from seed |
| Attestation (Receipt signing) | **Partial** | `controlPlane.ts` line 573: `signature: null` | Receipt struct has signature field but it is set to null; signing path exists but is not wired to receipt generation |
| Verification (Intent) | **Implemented** | `server/rio/controlPlane.ts` → `verifyIntentEnvelope()` | 6-check verification: schema, auth, signature, TTL, nonce, replay |
| Verification (Signature) | **Implemented** | `server/rio/ed25519.ts` → `verifySignature()`, `verifyAuthorization()` | Verifies Ed25519 signatures against public keys |
| Verification (Receipt) | **Not implemented** | — | No standalone receipt verifier exists; receipts are generated but not independently re-verified after storage |
| Verification (Chain) | **Implemented** | `server/rio-shield/hash-chain.ts` → `verifyChain()` | Verifies JSONL hash chain integrity: index continuity, hash linkage, record hash recomputation |
| Ledger (Database) | **Implemented** | `server/db.ts` → `appendLedger()` | Hash-chained append to database with prev_hash linkage |
| Ledger (WAL) | **Implemented** | `server/rio/kernelExecutor.ts` → `walPrepare()`, `walCommit()`, `walFail()` | Write-ahead log discipline: PREPARED before execution, COMMITTED/FAILED after |
| Ledger (File-based) | **Implemented** | `server/rio-shield/hash-chain.ts` → `finalizeChainRecord()`, `getChainTail()` | JSONL file-based hash chain for RIO Shield evaluator |
| Chronicle | **Not implemented** | — | Explicitly deferred in RIO Operating Spec §16 |
| Governance (Risk evaluation) | **Implemented** | `server/rio/controlPlane.ts` → `evaluateGovernance()` | Risk scoring, policy lookup, decision: APPROVE / DENY / REQUIRE_HUMAN_APPROVAL |
| Governance (Gate preflight) | **Implemented** | `server/rio/controlPlane.ts` → `executeGatePreflight()` | 18-point preflight check before execution |
| Governance (Three Powers) | **Implemented** | `server/rio/threePowers.ts` → `executeThreePowerLoop()` | Observer → Governor → Executor separation with queue-based handoff |

---

## §7 — Key Architectural Invariants

The following invariants hold in the current architecture:

1. **Receipt precedes ledger.** No ledger entry is written without a receipt or receipt-equivalent payload. The WAL discipline ensures that even the PREPARED entry contains the intent envelope data.

2. **Attestation is available but not universally applied.** Ed25519 signing infrastructure exists and is used for authorization tokens. Receipt-level attestation (signing the receipt itself) has the code path but is not yet wired — the `signature` field on `WitnessReceipt` is set to `null`.

3. **Verification is performed at intake, not at rest.** Intent envelopes are verified when they arrive (`verifyIntentEnvelope`). Receipts are not re-verified after storage. A future receipt verifier would enable post-hoc auditing.

4. **Ledger integrity is verifiable.** The hash chain can be independently verified via `verifyChain()` (file-based) or by walking the database ledger entries and recomputing hashes.

5. **Governance consumes verification, does not produce it.** The governance layer (`evaluateGovernance`, `executeGatePreflight`) receives the verification result and makes a decision. It does not perform verification itself.

6. **Chronicle is deferred.** No human-readable narrative layer exists. The ledger provides cryptographic proof but not human explanation.

---

## §8 — What Is Not Yet Implemented

| Gap | Description | Implication |
|-----|-------------|-------------|
| Receipt attestation wiring | `WitnessReceipt.signature` is always `null` | Receipts are generated but not cryptographically signed at generation time |
| Standalone receipt verifier | No function exists to take a stored receipt and re-verify it | Post-hoc auditing requires manual inspection; no programmatic re-verification |
| Verification status enum | Binary `verified: boolean` rather than graduated status levels | Cannot distinguish STRUCTURALLY_VALID from SIGNATURE_VALID from VERIFIED |
| Chronicle | No human-readable explanation layer | Ledger entries are machine-readable only |
| Handoff-to-action linkage (runtime) | `linkHandoffToActionReceipt()` exists in library but is not called in runtime paths | Handoff receipts and action receipts are generated independently |
| Cross-receipt verification | No function verifies that a chain of receipts (action + handoff) is internally consistent | Each receipt is valid in isolation but cross-receipt consistency is not checked |

---

## §9 — Explicit Statements

The following statements are made explicitly to prevent future ambiguity:

1. **Receipt is not verification.** A receipt is a data object. Verification is a process that acts on that object. They are not the same thing.

2. **Attestation is not verification.** Attestation proves that a specific key holder signed a specific payload. Verification checks whether that attestation is valid, whether the receipt is structurally complete, and whether it links correctly to the chain.

3. **Ledger is not verification.** The ledger preserves records. It does not check them. A tampered receipt could theoretically be written to the ledger if verification is bypassed. The ledger's hash chain detects subsequent tampering of stored records, not invalid records at write time.

4. **Governance is not verification.** Governance uses verification outcomes to make decisions. It does not perform the verification itself.

5. **Chronicle is not ledger.** Chronicle provides human explanation. Ledger provides cryptographic proof. They serve different audiences and have different integrity guarantees.

---

## §10 — Relationship to Existing Specs

This document does not replace or modify any existing specification. It provides architectural language clarification that applies across:

- **RIO Operating Spec v0.1** — §9 (Receipts), §10 (Ledger), §11 (Governance), §16 (Chronicle)
- **AI Handoff Receipt Protocol v0.1** — Receipt generation and hash chaining for handoff events
- **RIO ONE Canonical Architecture** — Layer separation between Observer, Governor, Executor
- **Governed Action Capability Audit (2026-05-04)** — Runtime evidence for receipt + ledger + governance

No existing document needs correction. This document adds precision to the vocabulary used across all of them.

---

## §11 — Handoff → Action Receipt Binding Checkpoint

Handoff → Action Receipt Binding v0.1 — Complete (checkpoint ffa1ed8e). Implemented: handoff_receipt_hash required on ExecutionReceipt, validateHandoffBinding validator (7 checks, fail-closed), pipeline enforcement before dispatchExecution, handoff receipt store, 14 tests passing, demo script showing valid chain + rejected unbound action, and architecture doc. Acceptance condition met: An action cannot be valid unless it is bound to the exact interpretation it relied on.

---

## Version History

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-05-04 | Initial verification stack clarification (Patch Pack 5A) |
| v0.1.1 | 2026-05-04 | Added keeper line (§2), handoff binding checkpoint note (§11) |
