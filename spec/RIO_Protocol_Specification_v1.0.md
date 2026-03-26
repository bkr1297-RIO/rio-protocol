# RIO Protocol Specification

**Version:** 1.0.0  
**Receipt Format:** v2  
**Ledger Format:** v2  
**Status:** Active  
**Date:** 2026-03-26  

---

## Table of Contents

1. [Introduction](#1-introduction)
   - 1.1 [Purpose and Scope](#11-purpose-and-scope)
   - 1.2 [Canonical Definition](#12-canonical-definition)
   - 1.3 [Terminology and Definitions](#13-terminology-and-definitions)
   - 1.4 [Notation Conventions](#14-notation-conventions)
   - 1.5 [Protocol Version](#15-protocol-version)
2. [Architecture Overview](#2-architecture-overview)
   - 2.1 [Three-Loop Architecture](#21-three-loop-architecture)
   - 2.2 [Eight-Stage Governed Execution Pipeline](#22-eight-stage-governed-execution-pipeline)
   - 2.3 [Canonical System Flow](#23-canonical-system-flow)
   - 2.4 [Trust Boundaries](#24-trust-boundaries)
   - 2.5 [Fail-Closed Principle](#25-fail-closed-principle)
3. [Pipeline Stage Specifications](#3-pipeline-stage-specifications)
   - 3.1 [Stage 1: Intent Intake and Translation](#31-stage-1-intent-intake-and-translation)
   - 3.2 [Stage 2: Sovereign Gate — Cryptographic Authentication](#32-stage-2-sovereign-gate--cryptographic-authentication)
   - 3.3 [Stage 3: Execution Gate — Authorization Verification](#33-stage-3-execution-gate--authorization-verification)
   - 3.4 [Stage 4: Grammar Calibration and Semantic Normalization](#34-stage-4-grammar-calibration-and-semantic-normalization)
   - 3.5 [Stage 5: Model Routing and Selection](#35-stage-5-model-routing-and-selection)
   - 3.6 [Stage 6: Governed Model Execution](#36-stage-6-governed-model-execution)
   - 3.7 [Stage 7: Receipt Generation and In-Memory Ledger Commit](#37-stage-7-receipt-generation-and-in-memory-ledger-commit)
   - 3.8 [Stage 8: Post-Execution Audit Ledger Recording](#38-stage-8-post-execution-audit-ledger-recording)
4. [Data Structures and Schemas](#4-data-structures-and-schemas)
   - 4.1 [Intake Request Schema](#41-intake-request-schema)
   - 4.2 [Intake Response Schema](#42-intake-response-schema)
   - 4.3 [Execution Token Schema](#43-execution-token-schema)
   - 4.4 [Gate Receipt Schema](#44-gate-receipt-schema)
   - 4.5 [In-Memory Ledger Entry Schema](#45-in-memory-ledger-entry-schema)
   - 4.6 [Execution Ledger Entry Schema (SQLite)](#46-execution-ledger-entry-schema-sqlite)
   - 4.7 [Post-Execution Ledger Entry Schema (SQLite)](#47-post-execution-ledger-entry-schema-sqlite)
   - 4.8 [Signature Registry Entry Schema](#48-signature-registry-entry-schema)
   - 4.9 [Gate Log Entry Schema](#49-gate-log-entry-schema)
5. [Cryptographic Specifications](#5-cryptographic-specifications)
   - 5.1 [Algorithm Suite](#51-algorithm-suite)
   - 5.2 [Key Material Specification](#52-key-material-specification)
   - 5.3 [Intent Signature Construction](#53-intent-signature-construction)
   - 5.4 [Execution Token Construction](#54-execution-token-construction)
   - 5.5 [Hash Computation Rules](#55-hash-computation-rules)
   - 5.6 [Execution Ledger Entry Hash](#56-execution-ledger-entry-hash)
   - 5.7 [Post-Execution Ledger Hash and HMAC Seal](#57-post-execution-ledger-hash-and-hmac-seal)
   - 5.8 [In-Memory Ledger Receipt Hash](#58-in-memory-ledger-receipt-hash)
   - 5.9 [Signature Registry Fingerprint](#59-signature-registry-fingerprint)
   - 5.10 [Key Fingerprint (Approver Field)](#510-key-fingerprint-approver-field)
   - 5.11 [Encoding Rules](#511-encoding-rules)
6. [Verification Protocol](#6-verification-protocol)
   - 6.1 [Sovereign Gate Verification (Seven-Check Sequence)](#61-sovereign-gate-verification-seven-check-sequence)
   - 6.2 [Execution Gate Verification (Five-Guard Sequence)](#62-execution-gate-verification-five-guard-sequence)
   - 6.3 [Execution Ledger Chain Verification](#63-execution-ledger-chain-verification)
   - 6.4 [Post-Execution Ledger Chain and Signature Verification](#64-post-execution-ledger-chain-and-signature-verification)
   - 6.5 [In-Memory Ledger Chain Verification](#65-in-memory-ledger-chain-verification)
   - 6.6 [Independent Third-Party Verification](#66-independent-third-party-verification)
   - 6.7 [Verification Result Format](#67-verification-result-format)
7. [Protocol Invariants](#7-protocol-invariants)
   - 7.1 [Protocol Invariants (INV-01 through INV-08)](#71-protocol-invariants-inv-01-through-inv-08)
   - 7.2 [System Invariants](#72-system-invariants)
   - 7.3 [Invariant Dependencies](#73-invariant-dependencies)
   - 7.4 [Emergency Kill Switch (EKS-0)](#74-emergency-kill-switch-eks-0)
8. [Conformance Requirements](#8-conformance-requirements)
   - 8.1 [Conformance Levels](#81-conformance-levels)
   - 8.2 [Level 1: Cryptographic Compliance](#82-level-1-cryptographic-compliance)
   - 8.3 [Level 2: Pipeline Compliance](#83-level-2-pipeline-compliance)
   - 8.4 [Level 3: Full Protocol Compliance](#84-level-3-full-protocol-compliance)
   - 8.5 [Conformance Testing](#85-conformance-testing)
9. [Security Considerations](#9-security-considerations)
   - 9.1 [Threat Model Summary](#91-threat-model-summary)
   - 9.2 [Trust Boundaries](#92-trust-boundaries)
   - 9.3 [Role Separation](#93-role-separation)
   - 9.4 [Key Management Security](#94-key-management-security)
- [Appendix A: Complete Intake Request and Response Examples](#appendix-a-complete-intake-request-and-response-examples)
- [Appendix B: Complete Ledger Entry Examples](#appendix-b-complete-ledger-entry-examples)
- [Appendix C: Hash Computation Test Vectors](#appendix-c-hash-computation-test-vectors)

---

## 1. Introduction

### 1.1 Purpose and Scope

This document is the canonical technical specification for the RIO Protocol, version 1.0. It defines the complete protocol requirements that a conforming implementation MUST satisfy, including all data structures, cryptographic operations, pipeline stage behaviors, invariants, and verification procedures.

This specification is self-contained. An external engineering team reading only this document, with no access to the reference implementation source code or to the original authors, MUST be able to implement a fully RIO-compliant system. Every requirement stated here is either precisely defined within this document or explicitly references another section of this document.

This specification covers:

- The Three-Loop Architecture that governs all RIO execution
- The Eight-Stage Governed Execution Pipeline
- All data structures, schemas, and field-level constraints
- All cryptographic algorithms, parameters, and exact encoding rules
- All verification procedures, including independent third-party verification
- Protocol invariants that MUST never be violated
- Conformance levels and their requirements
- Security considerations

This specification does NOT cover:

- Implementation-specific details such as programming language, framework, or module structure
- API endpoint paths, HTTP transport mechanics, or deployment infrastructure
- Dashboard, web UI, or client-side signing tool specifications
- Advanced governance analytics or learning-loop machine-learning components
- The full threat model (summarized in Section 9; a complete threat analysis is maintained separately)

### 1.2 Canonical Definition

RIO is a **governed execution system** that sits between AI models, human principals, and real-world actions. It translates natural-language goals into structured, verifiable intents; evaluates those intents against policy and risk criteria; requires explicit approval when authorization thresholds are met; controls execution through a cryptographically enforced hard gate; verifies outcomes against the approved intent; and generates signed, chained receipts recorded in a tamper-evident ledger.

The system enforces the rules. The AI does not.

This principle is architecturally enforced: no AI model can cause an action to execute without passing through the Sovereign Gate (cryptographic authentication of the intent by an authorized key) and the Execution Gate (cryptographic authorization of execution by the same key). Both gates are fail-closed. Every execution, whether permitted or blocked, is recorded in the audit ledger.

The RIO Protocol formalizes the rules, data structures, cryptographic constructions, and behavioral requirements that make this enforcement system reliable, auditable, and independently verifiable.

### 1.3 Terminology and Definitions

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** in this document are to be interpreted as described in [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

| Term | Definition |
|------|-----------|
| **Action** | A real-world operation executed by the gateway on behalf of an approved intent. In this implementation, the action is always an AI model invocation. |
| **Approver** | The first 16 hexadecimal characters of SHA-256(`RIO_PUBLIC_KEY_raw_bytes`). Identifies the cryptographic authority that authorized an execution. |
| **Calibrated Intent** | The intent string after grammar normalization and optional context injection. This is the string passed to the AI model. |
| **Canonical Bytes** | The deterministic byte encoding of gate parameters used as the ECDSA signing input for execution tokens. See Section 5.4. |
| **Entry Hash** | The SHA-256 seal of a single `execution_ledger` row. Each entry's hash becomes the `prev_hash` of the next entry, forming the integrity chain. |
| **Execution Gate** | The inner hard gate (`check_gate`) that enforces a five-guard validation sequence before any AI model invocation. |
| **Execution Token** | A short-lived, base64-encoded DER ECDSA signature over the canonical gate parameters. Proves server-side authorization of a specific execution. |
| **GENESIS** | The literal ASCII string `"GENESIS"`, used as the `prev_hash` or `prev_ledger_hash` for the first row in any hash chain. |
| **Gate Receipt** | A structured object returned by `check_gate` on successful gate passage. Contains `receipt_hash`, `intent_hash`, `parameters_hash`, `approver`, and related fields. |
| **Governed Execution** | Execution that has passed through all required pipeline stages, including both the Sovereign Gate and the Execution Gate. |
| **Intent** | A natural-language string expressing what the caller wants the AI to do. The fundamental unit of input to the RIO Pipeline. |
| **Intent Hash** | SHA-256(`UTF-8_encode(intent_string)`). Used to index the intent across ledger tables without storing the raw intent text. |
| **Key Fingerprint** | See Approver. |
| **Ledger Hash** | The SHA-256 seal of a single `post_execution_ledger` row. Used as the HMAC input for that row's integrity signature. |
| **Nonce** | A caller-supplied, single-use random string included in the intake request to prevent replay attacks at the intent level. |
| **Parameters Hash** | SHA-256 of the canonical bytes encoding of gate parameters. Cross-references `execution_ledger` and `post_execution_ledger` entries for the same request. |
| **Receipt Hash** | In the in-memory ledger: SHA-256 of the pipe-delimited concatenation of ledger entry fields. In the execution ledger: the SHA-256 seal of a gate-passage event. |
| **RIO_PRIVATE_KEY** | The ECDSA secp256k1 private signing key. Used to sign intents and generate execution tokens. MUST never be logged or returned to callers. |
| **RIO_PUBLIC_KEY** | The ECDSA secp256k1 public verifying key. Used to verify all signatures. Set as an environment variable in the gateway. |
| **RIO_SERVICE_TOKEN** | A shared secret used as the HMAC key for post-execution ledger entry signatures. |
| **RIO_PROXY_TOKEN** | An alternative Bearer token accepted by service-protected endpoints. Functionally equivalent to `RIO_SERVICE_TOKEN` for authentication purposes. |
| **Signature Hash** | SHA-256 of the raw DER signature bytes. Used as the primary key in the Signature Registry to enforce per-signature single-use. |
| **Sovereign Gate** | The outermost cryptographic checkpoint. Performs ECDSA signature verification on the raw intent string before any processing begins. |
| **Source** | A caller-supplied string identifying the origin system of the request (e.g., `"manus"`, `"cli"`, `"web"`). |
| **TTL** | Time-to-live. Defaults to `SIGNATURE_WINDOW_SECONDS` (default: 300 seconds). |

### 1.4 Notation Conventions

**Pseudocode:** Algorithm steps are presented as numbered sequences using language-agnostic pseudocode. Function calls use the form `FUNCTION_NAME(arguments)`. String concatenation uses `+`. The pipe separator `|` refers to the literal ASCII character U+007C.

**Hash notation:** `SHA-256(x)` denotes the SHA-256 digest of byte sequence `x`, returned as a lowercase hexadecimal string unless otherwise noted. `UTF-8_encode(s)` denotes the UTF-8 byte encoding of string `s`. Combined: `SHA-256(UTF-8_encode(s))` is the SHA-256 hex digest of the UTF-8 bytes of `s`.

**Base64:** `Base64_encode(b)` is standard Base64 encoding (RFC 4648, alphabet `A–Za–z0–9+/`, with `=` padding). `Base64_decode(s)` is the inverse.

**Slicing:** `x[:n]` denotes the first `n` characters of string `x`. `x[:n]` on a byte sequence denotes the first `n` bytes.

**Field tables:** Fields are listed with: `Name`, `Type`, `Required/Optional`, `Constraints`, and `Description`. Required means the field MUST be present and non-empty. Optional means the field MAY be absent; when absent its default value (if any) is noted.

**Code blocks:** JSON examples use realistic placeholder values. Exact hash values in Appendix C are computed from the stated inputs and are valid test vectors.

**Section references:** Cross-references use the form `(see Section N.N)`.

### 1.5 Protocol Version

| Component | Version |
|-----------|---------|
| Protocol | 1.0.0 |
| Receipt Format | v2 |
| Ledger Format | v2 |
| Signature Algorithm | ECDSA secp256k1 / SHA-256 / DER |
| Ledger HMAC Algorithm | HMAC-SHA256 |
| GENESIS Anchor | Literal string `"GENESIS"` |

Implementations MUST include the protocol version in all generated receipts and ledger entries. Version negotiation and upgrade paths are outside the scope of this specification.

---

## 2. Architecture Overview

### 2.1 Three-Loop Architecture

The RIO Protocol organizes all activity into three structurally separated loops. Each loop has distinct responsibilities, data flows, and trust requirements. Separation between loops is a protocol invariant (INV-07): no loop may bypass the responsibilities of another.

#### 2.1.1 Loop 1: Intake and Discovery Loop

**Responsibility:** Accept raw goals from callers, translate them into structured intents, verify the caller's cryptographic identity, and determine whether the intent may proceed.

**Data flow in:**
- Raw natural-language goal (intent string)
- Caller identifier (source)
- ECDSA signature over the intent (signed by the caller using `RIO_PRIVATE_KEY`)
- Timestamp and optional nonce (for replay protection)
- Optional model preference and payload context

**Data flow out:**
- Normalized, calibrated intent
- Verification status (signature valid / invalid)
- Replay status (nonce and signature registry check results)
- Routing decision (model selection)

**Trust boundary:** The Intake Loop validates that the request originates from an authorized caller. It does NOT grant execution rights. Execution rights are granted only by the Execution Gate in Loop 2.

#### 2.1.2 Loop 2: Execution and Governance Loop

**Responsibility:** Enforce the hard execution gate, execute the governed action (AI model invocation), capture the outcome, generate the signed receipt, and record both the gate decision and the execution outcome in the tamper-evident audit ledger.

**Data flow in:**
- Calibrated intent from Loop 1
- Execution token (ECDSA signature over canonical gate parameters)
- Gate receipt (returned by `check_gate` on success)

**Data flow out:**
- AI model response
- In-memory ledger receipt (receipt_hash + ledger_index)
- Execution ledger entries (gate decision and post-execution outcome)
- Signed response to caller

**Trust boundary:** The Execution Gate in Loop 2 is the last line of defense. Even if Loop 1 somehow passed a malformed or unauthorized intent, the Execution Gate verifies the execution token independently using the same ECDSA key. Failure at this boundary is fail-closed: no action executes.

#### 2.1.3 Loop 3: Learning and Audit Loop

**Responsibility:** Maintain the persistent audit record, enable retrospective verification of all past decisions and outcomes, support chain integrity verification, and provide the audit trail for governance review.

**Data flow in:**
- Execution ledger entries (one per gate decision)
- Post-execution ledger entries (one per completed execution)
- In-memory response ledger entries (one per successful response)

**Data flow out:**
- Paginated, filterable ledger query results
- Chain integrity reports (`chain_intact` boolean)
- Per-intent audit trails (gate entries + post-execution entries for a single intent)
- Receipt verification results (for independently submitted receipt hashes)

**Trust boundary:** Loop 3 is read-only from the perspective of callers. The audit ledger is append-only; existing entries MUST NOT be modified after recording.

### 2.2 Eight-Stage Governed Execution Pipeline

Every intake request traverses exactly eight stages in strict sequential order. A failure at any stage is fail-closed: the request is rejected immediately with no advancement to subsequent stages and no AI model invocation. The stage outputs are additive: each stage consumes the outputs of all prior stages.

| Stage | Name | Layer | Fail Behavior |
|-------|------|-------|---------------|
| 1 | Intent Intake and Translation | Loop 1 | HTTP 409 (replay) or HTTP 503 (registry error) |
| 2 | Sovereign Gate — Cryptographic Authentication | Loop 1 | HTTP 401 or HTTP 503 |
| 3 | Execution Gate — Authorization Verification | Loop 2 | HTTP 403 |
| 4 | Grammar Calibration and Semantic Normalization | Loop 1 | (non-failing; normalization is always possible) |
| 5 | Model Routing and Selection | Loop 1 | (non-failing; default model applied) |
| 6 | Governed Model Execution | Loop 2 | HTTP 502 |
| 7 | Receipt Generation and In-Memory Ledger Commit | Loop 2 | (non-failing; write errors are logged) |
| 8 | Post-Execution Audit Ledger Recording | Loop 3 | (non-failing, asynchronous; write errors are logged) |

### 2.3 Canonical System Flow

```
Caller
  │
  │  POST /intake { intent, source, signature, timestamp, nonce, execution_token, ... }
  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LOOP 1 — Intake and Discovery Loop                                 │
│                                                                     │
│  Stage 1: Signature Hash → Atomic DB Claim (used_signatures)        │
│           [sig_hash = SHA-256(raw_DER_bytes)]                       │
│           Replay detected → HTTP 409                                │
│           DB error → HTTP 503                                       │
│                          │                                          │
│  Stage 2: Sovereign Gate — ECDSA Verification                       │
│           Key check → Timestamp check → Sig verify → Nonce check   │
│           Any failure → HTTP 401 / 503                              │
│                          │                                          │
│  Stage 4: Grammar Calibration (may run in parallel with Stage 3    │
│           setup; logically sequential in the pipeline)              │
│           calibrated_intent = trim(intent) + optional context       │
│                          │                                          │
│  Stage 5: Model Routing                                             │
│           Explicit model field → keyword matching → default=claude  │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LOOP 2 — Execution and Governance Loop                             │
│                                                                     │
│  Stage 3: Execution Gate (check_gate) — 5-Guard Sequence           │
│           Guard 1: Required fields present                          │
│           Guard 2: Timestamp freshness                              │
│           Guard 3: Execution token present                          │
│           Guard 4: RIO_PUBLIC_KEY loadable                          │
│           Guard 5: ECDSA signature valid                            │
│           Any failure → HTTP 403 + execution_ledger "blocked" row   │
│                          │                                          │
│  Stage 6: Model Execution                                           │
│           call_claude(calibrated_intent) | call_chatgpt(...) | ...  │
│           Exception → HTTP 502                                      │
│                          │                                          │
│  Stage 7: Receipt Generation + In-Memory Ledger Commit             │
│           receipt_hash = SHA-256(prev|source|intent|model|          │
│                                  response[:500]|timestamp)          │
│           Returns receipt_hash + ledger_index to caller             │
└─────────────────────────────────────────────────────────────────────┘
                           │
                           │  HTTP 200 { response, receipt_hash, ... }
                           ▼
                        Caller

                           │ (async, non-blocking)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LOOP 3 — Audit and Governance Loop                                 │
│                                                                     │
│  Stage 8: Post-Execution Ledger Recording                           │
│           result_hash = SHA-256(ai_response)                        │
│           ledger_hash = SHA-256(ts|approver|agent|executed_by|      │
│                                 policy_result|params_hash|          │
│                                 result_hash|prev_ledger_hash)       │
│           signature   = HMAC-SHA256(ledger_hash, RIO_SERVICE_TOKEN) │
│           Written asynchronously — never delays caller response     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.4 Trust Boundaries

The RIO Protocol defines four trust boundaries. Each boundary has a specific crossing mechanism that MUST be satisfied before data or control passes across it.

| Boundary | From | To | Crossing Mechanism |
|----------|------|----|--------------------|
| **TB-1: Intake Boundary** | External caller | Loop 1 | Valid ECDSA signature over intent + timestamp within window |
| **TB-2: Signature Registry Boundary** | Any request | Signature Registry | Atomic DB claim of SHA-256(signature_bytes) — single-use |
| **TB-3: Execution Boundary** | Loop 1 | Loop 2 (AI model) | Valid ECDSA execution token over canonical gate parameters |
| **TB-4: Audit Boundary** | Loop 2 | Loop 3 (Ledger) | Append-only writes only; no modification path exists |

No request MAY cross TB-3 (the Execution Boundary) without having successfully crossed TB-1 and TB-2 in the same request lifecycle.

### 2.5 Fail-Closed Principle

The fail-closed principle is the foundational safety property of the RIO Protocol. It MUST be implemented as follows:

1. **Default deny.** No AI model executes unless every required verification step explicitly passes.
2. **Infrastructure failures deny.** If any cryptographic verification component is unavailable (key not loaded, database unreachable), the request MUST be blocked, not allowed. There is no fail-open fallback.
3. **Concurrent replay denial.** Concurrent requests with the same signature MUST both be denied. The atomic claim mechanism (see Section 3.1) enforces this.
4. **Audit regardless of outcome.** Every gate decision — pass or block — MUST be written to the execution ledger. An unaudited execution is a protocol violation.
5. **Async isolation.** The post-execution ledger write (Stage 8) MUST NOT delay the caller response, but its failure MUST be logged. The post-execution ledger exists for audit purposes; its failure does not retroactively invalidate an already-completed governed execution.

---

## 3. Pipeline Stage Specifications

This section specifies each of the eight pipeline stages in full. For each stage, the following are defined: Purpose, Inputs (with types and constraints), Processing Rules (step-by-step), Outputs (with types), Failure Conditions (with HTTP status codes and reason codes), and Invariants Enforced.

### 3.1 Stage 1: Intent Intake and Translation

**Purpose:** Accept the raw intake request, compute the signature hash, perform an atomic single-use claim in the Signature Registry, and detect any signature-level replay before cryptographic verification begins.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `signature` | string | REQUIRED. Base64-encoded DER ECDSA signature bytes. |
| `intent` | string | REQUIRED. The raw natural-language intent string. |
| All other intake fields | — | Passed through; not inspected in this stage. |

**Processing Rules:**

1. Base64-decode the `signature` field to obtain `raw_sig_bytes`. If decoding fails, proceed — this will be caught in Stage 2.
2. Compute `sig_hash = SHA-256(raw_sig_bytes)`.
3. Perform an atomic check-and-insert against the `used_signatures` table:
   a. Query for an existing row where `signature_hash = sig_hash`.
   b. Evict all rows where `expires_at <= Unix_epoch_now()`.
   c. If a row is found: signature replay detected. Reject.
   d. If no row is found: attempt `INSERT INTO used_signatures (signature_hash, intent, used_at, expires_at)` with `expires_at = Unix_epoch_now() + SIGNATURE_WINDOW_SECONDS`.
   e. If the INSERT raises a uniqueness constraint error (concurrent duplicate): treat as replay. Reject.
   f. Any other database error: block execution (fail-closed). Do not proceed.
4. On successful claim: record `sig_hash` for inclusion in the final response.

**Outputs:**

| Field | Type | Description |
|-------|------|-------------|
| `sig_hash` | string (hex) | SHA-256 of raw signature bytes. Included in the intake response as `signature_hash`. |
| Claimed registry entry | — | Row in `used_signatures` with TTL set. |

**Failure Conditions:**

| Condition | HTTP Status | Reason |
|-----------|-------------|--------|
| Signature hash already in registry | 409 | `replay_blocked` |
| Concurrent duplicate (IntegrityError) | 409 | `replay_blocked_concurrent` |
| Database operation fails | 503 | `registry_unavailable` |

**Invariants Enforced:** INV-02 (single-use signatures), INV-06 (fail-closed on infrastructure error).

---

### 3.2 Stage 2: Sovereign Gate — Cryptographic Authentication

**Purpose:** Verify that the intent was cryptographically signed by the holder of `RIO_PRIVATE_KEY`, that the request is within the valid time window, and that any nonce has not been previously consumed.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `intent` | string | REQUIRED. The raw intent string (the signed message). |
| `signature` | string | REQUIRED. Base64-encoded DER ECDSA signature. |
| `timestamp` | string | REQUIRED. ISO-8601 UTC string. |
| `nonce` | string | OPTIONAL but STRONGLY RECOMMENDED. Single-use token. |

**Processing Rules:**

1. **Check 1 — Key Availability.** Attempt to load `RIO_PUBLIC_KEY` from the environment. If unavailable or unparseable by any supported format (see Section 5.2), block immediately. Log reason `key_not_configured`. Return HTTP 503.

2. **Check 2 — Timestamp Freshness.** Parse `timestamp` as ISO-8601 UTC. If unparseable, block. Log reason `bad_timestamp`. Return HTTP 401. If `abs(UTC_now - timestamp) > SIGNATURE_WINDOW_SECONDS`, block. Log reason `timestamp_expired`. Return HTTP 401.

3. **Check 3 — Signature Presence.** Verify `signature` field is non-empty. If absent or empty, block. Log reason `missing_signature`. Return HTTP 401.

4. **Check 4 — Base64 Validity.** Attempt to Base64-decode `signature`. If decoding fails, block. Log reason `invalid_base64`. Return HTTP 401.

5. **Check 5 — ECDSA Verification.** Verify the decoded signature bytes against `UTF-8_encode(intent)` using `RIO_PUBLIC_KEY`, curve secp256k1, hash SHA-256, DER encoding (sigdecode_der). If verification fails with a BadSignatureError: block. Log reason `bad_signature`. Return HTTP 401. If verification fails with any other exception: block. Log reason `verification_error`. Return HTTP 401.

6. **Check 6 — Nonce Claim (if present).** If `nonce` is present in the request:
   a. Evict all expired nonces from the in-memory Nonce Registry.
   b. Check whether `nonce` is already in the registry.
   c. If present (replay): block. Log reason `nonce_replay`. Return HTTP 401.
   d. If the registry itself raises an exception: block. Log reason `nonce_registry_error`. Return HTTP 503.
   e. If not present: record `nonce → Unix_epoch_now() + SIGNATURE_WINDOW_SECONDS` in the registry.
   If `nonce` is absent: log a warning (nonce enforcement missing) but do not block. Requests without a nonce are accepted with reduced replay-protection guarantees.

7. **Check 7 — Accept.** Log acceptance. Write acceptance to the audit logger. Pipeline proceeds to Stage 3.

**Outputs:** Verification status (success). If any check fails, pipeline terminates.

**Failure Conditions:**

| Condition | HTTP Status | Reason Code |
|-----------|-------------|-------------|
| `RIO_PUBLIC_KEY` not set or unparseable | 503 | `key_not_configured` |
| Timestamp unparseable | 401 | `bad_timestamp` |
| Timestamp outside window | 401 | `timestamp_expired` |
| Signature field absent | 401 | `missing_signature` |
| Signature not valid Base64 | 401 | `invalid_base64` |
| ECDSA verification fails | 401 | `bad_signature` |
| Any other verification exception | 401 | `verification_error` |
| Nonce already in registry | 401 | `nonce_replay` |
| Nonce registry error | 503 | `nonce_registry_error` |

**Invariants Enforced:** INV-01 (all execution cryptographically authenticated), INV-02 (single-use enforcement), INV-06 (fail-closed).

---

### 3.3 Stage 3: Execution Gate — Authorization Verification

**Purpose:** Enforce the hard execution gate (`check_gate`) using a five-guard sequence. This stage is the final barrier before any AI model invocation. It independently verifies that an execution token was generated for the exact parameters of this request. Every call to `check_gate` — pass or block — MUST be recorded in the `execution_ledger`.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `intent` | string | REQUIRED. From the intake request. |
| `source` | string | REQUIRED. From the intake request. |
| `timestamp` | string | REQUIRED. From the intake request. Same value used in the execution token. |
| `execution_token` | string | REQUIRED for execution. Base64-encoded DER ECDSA signature over canonical bytes. |

**Pre-computation (before guards):**

The following values are computed once and used throughout the guard sequence and in ledger writes:

```
intent_id       = SHA-256(UTF-8_encode(intent))
canonical_bytes = UTF-8_encode(intent + "|" + source + "|" + timestamp)
parameters_hash = SHA-256(canonical_bytes)
approver        = SHA-256(UTF-8_encode(RIO_PUBLIC_KEY_env_raw))[:16]
```

**Processing Rules — Guard Sequence:**

**Guard 1 — Required Fields.** Check that `intent`, `source`, and `timestamp` are all present and non-empty.
- Failure: Write `blocked` row to `execution_ledger` and `gate_log`. Raise HTTP 403. Reason: `missing_fields:<comma-separated list>`.

**Guard 2 — Timestamp Freshness.** Parse `timestamp` as ISO-8601 UTC. Verify `abs(UTC_now - timestamp) <= SIGNATURE_WINDOW_SECONDS`.
- Parse failure: Reason `timestamp_invalid`.
- Stale: Reason `timestamp_stale`.
- Failure action: Write `blocked` rows. Raise HTTP 403.

**Guard 3 — Token Presence.** Verify `execution_token` is present and non-empty.
- Failure: Write `blocked` rows. Raise HTTP 403. Reason: `missing_token`.

**Guard 4 — Key Availability.** Attempt to load `RIO_PUBLIC_KEY`.
- Failure: Write `blocked` rows (using `approver = "key_unavailable"`). Raise HTTP 403. Reason: `key_unavailable`.

**Guard 5 — ECDSA Signature.** Base64-decode `execution_token` to obtain signature bytes. Verify signature bytes against `canonical_bytes` using `RIO_PUBLIC_KEY`, curve secp256k1, hash SHA-256, DER decoding.
- BadSignatureError: Reason `invalid_signature`.
- Any other exception: Reason `verification_error:<exception_string>`.
- Failure action: Write `blocked` rows. Raise HTTP 403.

**On Successful Gate Passage:**

Compute the receipt:
```
ts           = UTC_now as ISO-8601 string
receipt_data = "GATE_PASSED|" + intent_id + "|" + source + "|" + ts
receipt_hash = SHA-256(UTF-8_encode(receipt_data))
```

Write to `gate_log` with `event = "gate_passed"`.
Write to `execution_ledger` with `result = "executed"`, `reason = "gate_passed"`, `receipt_hash = receipt_hash`.

Return the gate receipt object (see Section 4.4).

**On Any Guard Failure:**

Write to `gate_log` with `event = "unauthorized execution attempt"`.
Write to `execution_ledger` with `result = "blocked"`, `reason = <reason_code>`, `receipt_hash = ""`.
Raise HTTP 403.

**Outputs (on success):**

The gate receipt object (see Section 4.4), which MUST be consumed by Stage 6 and Stage 8.

**Failure Conditions:**

| Guard | Condition | HTTP Status | Reason Code |
|-------|-----------|-------------|-------------|
| 1 | Missing `intent`, `source`, or `timestamp` | 403 | `missing_fields:<list>` |
| 2 | Timestamp unparseable | 403 | `timestamp_invalid` |
| 2 | Timestamp outside window | 403 | `timestamp_stale` |
| 3 | `execution_token` absent | 403 | `missing_token` |
| 4 | `RIO_PUBLIC_KEY` not loadable | 403 | `key_unavailable` |
| 5 | ECDSA verification fails | 403 | `invalid_signature` |
| 5 | Any other verification error | 403 | `verification_error:<msg>` |

**Invariants Enforced:** INV-01, INV-03 (no execution without valid gate), INV-05 (every gate decision audited), INV-06.

---

### 3.4 Stage 4: Grammar Calibration and Semantic Normalization

**Purpose:** Normalize the intent string and optionally augment it with additional context before routing and AI model invocation.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `intent` | string | REQUIRED. |
| `payload.context` | string | OPTIONAL. Additional context to inject. |

**Processing Rules:**

1. Trim leading and trailing whitespace from `intent`:
   ```
   calibrated = trim(intent)
   ```

2. If `payload.context` is present and non-empty, append it to the calibrated intent:
   ```
   context_truncated = trim(payload.context)[:300]
   calibrated = calibrated + "\n\n[Context: " + context_truncated + "]"
   ```
   The context value MUST be truncated to 300 characters before appending.

3. The result is the `calibrated_intent`. This string — not the raw `intent` — is passed to the AI model in Stage 6.

**Outputs:**

| Field | Type | Description |
|-------|------|-------------|
| `calibrated_intent` | string | Normalized, optionally context-augmented intent string. |

**Failure Conditions:** None. Grammar calibration MUST always produce a non-empty string if `intent` is non-empty (which was verified by Stage 3, Guard 1). This stage does not fail.

**Invariants Enforced:** The calibrated intent MUST be a deterministic function of the raw intent and the payload context. Any context exceeding 300 characters MUST be truncated, not rejected.

---

### 3.5 Stage 5: Model Routing and Selection

**Purpose:** Determine which AI model will handle the calibrated intent, based on explicit caller preference or intent keyword analysis.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `model` | string | OPTIONAL. Explicit model preference. |
| `calibrated_intent` | string | REQUIRED. Output of Stage 4. |

**Processing Rules:**

1. If `model` is present and non-empty, normalize it to lowercase and apply explicit keyword matching:
   - If the value contains `"claude"` or `"anthropic"` → resolved model: `"claude"`.
   - If the value contains `"chatgpt"`, `"openai"`, or `"gpt"` → resolved model: `"chatgpt"`.
   - If the value contains `"gemini"` or `"google"` → resolved model: `"gemini"`.
   - If no keyword matches: fall through to intent keyword routing (step 2).

2. Apply intent keyword routing (case-insensitive match against `calibrated_intent`):
   - Any of `"code"`, `"debug"`, `"refactor"`, `"function"`, `"script"`, `"program"` → `"chatgpt"`.
   - Any of `"analyse"`, `"analyze"`, `"analysis"`, `"research"`, `"reason"`, `"summarise"`, `"summarize"` → `"claude"`.
   - No match → default: `"claude"`.

3. The resolved model identifier determines which AI client is called in Stage 6:

| Identifier | AI Model String | Provider |
|------------|----------------|---------|
| `"claude"` | `claude-sonnet-4-6` | Anthropic |
| `"chatgpt"` | `gpt-5.2` | OpenAI |
| `"gemini"` | `gemini-2.5-flash` | Google |

**Outputs:**

| Field | Type | Description |
|-------|------|-------------|
| `model_used` | string | One of `"claude"`, `"chatgpt"`, `"gemini"`. Included in the intake response. |

**Failure Conditions:** None. The default model (`"claude"`) ensures this stage never fails. If no keyword matches, `"claude"` is used.

---

### 3.6 Stage 6: Governed Model Execution

**Purpose:** Invoke the selected AI model with the calibrated intent. This stage is only reached after Stages 1–3 have all passed. Execution is unconditionally blocked if any prior stage failed.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `calibrated_intent` | string | REQUIRED. Output of Stage 4. |
| `model_used` | string | REQUIRED. Output of Stage 5. |
| Gate receipt | object | REQUIRED. Output of Stage 3. Contains `approver` and `parameters_hash`. |

**Processing Rules:**

1. Select the AI client based on `model_used`.
2. Invoke the model with `calibrated_intent` as the sole user message. Parameters:
   - `max_tokens: 1024` (for Claude and ChatGPT)
   - Model string: as specified in Stage 5 table.
3. Capture the complete text response as `ai_response`.
4. If the model call raises any exception, return HTTP 502 to the caller. Log the error. Pipeline terminates.

**Outputs:**

| Field | Type | Description |
|-------|------|-------------|
| `ai_response` | string | Complete text response from the AI model. |

**Failure Conditions:**

| Condition | HTTP Status | Description |
|-----------|-------------|-------------|
| Model call raises exception | 502 | Model call failed. |

**Note on Post-Execution Ledger Interaction:** After `ai_response` is captured, Stage 8 is initiated asynchronously using `ai_response`, `model_used`, and the gate receipt. Stage 6 does not wait for Stage 8 to complete.

**Invariants Enforced:** INV-03 (no execution without authorization), INV-04 (execution is preceded by ledger gate entry).

---

### 3.7 Stage 7: Receipt Generation and In-Memory Ledger Commit

**Purpose:** Generate the integrity-sealed receipt for this execution and commit it to the in-memory hash-chain ledger. The `receipt_hash` and `ledger_index` from this stage are returned to the caller.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `source` | string | REQUIRED. From intake request. |
| `intent` | string | REQUIRED. Raw (not calibrated) intent. |
| `model_used` | string | REQUIRED. Output of Stage 5. |
| `ai_response` | string | REQUIRED. Output of Stage 6. |
| `prev_hash` | string | REQUIRED. `receipt_hash` of the previous in-memory ledger entry, or `"GENESIS"` for the first. Maintained by the in-memory ledger. |

**Processing Rules:**

1. Compute `response_ts = UTC_now as ISO-8601 string`.
2. Compute the receipt hash:
   ```
   data = prev_hash + "|" + source + "|" + intent + "|" + model_used
        + "|" + ai_response[:500] + "|" + response_ts
   receipt_hash = SHA-256(UTF-8_encode(data))
   ```
   Only the first 500 characters of `ai_response` are included in the hash computation.
3. Compute `intent_hash = SHA-256(UTF-8_encode(intent))`.
4. Atomically (under a mutex/lock) append the entry to the in-memory ledger:
   - Increment the sequential `ledger_index` (starting from 1).
   - Store the entry as specified in Section 4.5.
   - Set `self._prev_hash = receipt_hash` for the next append.
5. Return `ledger_index` and `receipt_hash` for inclusion in the HTTP response.

**Outputs:**

| Field | Type | Description |
|-------|------|-------------|
| `receipt_hash` | string (hex) | SHA-256 seal of this ledger entry. Included in the intake response. |
| `ledger_index` | integer | Sequential 1-based position in the in-memory ledger. Included in the intake response. |

**Failure Conditions:** Failures in this stage (e.g., hash computation errors) MUST be logged but SHOULD NOT prevent the HTTP response. The `receipt_hash` and `ledger_index` MAY be absent from the response if the commit fails, but this is a degraded state.

**Invariants Enforced:** INV-08 (every execution has a receipt), INV-04 (hash chain integrity).

---

### 3.8 Stage 8: Post-Execution Audit Ledger Recording

**Purpose:** Append a tamper-evident, HMAC-signed entry to the `post_execution_ledger` table recording the outcome of this AI execution. This stage runs asynchronously and MUST NOT delay the HTTP response to the caller.

**Inputs:**

| Field | Type | Constraint |
|-------|------|-----------|
| `model_used` | string | REQUIRED. AI model identifier. |
| `source` | string | REQUIRED. Caller identifier. |
| `ai_response` | string | REQUIRED. Full AI model response. |
| `gate_receipt.parameters_hash` | string (hex) | REQUIRED. From Stage 3 output. |
| `gate_receipt.approver` | string | REQUIRED. From Stage 3 output. |
| `prev_ledger_hash` | string | REQUIRED. `ledger_hash` of the previous `post_execution_ledger` row, or `"GENESIS"`. |

**Processing Rules:**

1. Compute `ts = UTC_now as ISO-8601 string`.
2. Compute `result_hash = SHA-256(UTF-8_encode(ai_response))`.
3. Fetch `prev_ledger_hash` by querying the last `ledger_hash` value in `post_execution_ledger` ordered by `id DESC LIMIT 1`. If the table is empty, use `"GENESIS"`.
4. Set `policy_result = "success"`. (On execution error in Stage 6, this would be `"error:<message>"` — but Stage 6 failures prevent Stage 8 from being invoked.)
5. Compute the ledger hash:
   ```
   seal_data   = ts + "|" + approver + "|" + model_used + "|" + source
               + "|" + policy_result + "|" + parameters_hash
               + "|" + result_hash + "|" + prev_ledger_hash
   ledger_hash = SHA-256(UTF-8_encode(seal_data))
   ```
6. Compute the HMAC signature:
   ```
   hmac_key  = UTF-8_encode(RIO_SERVICE_TOKEN)
   signature = HMAC-SHA256(key=hmac_key, msg=UTF-8_encode(ledger_hash))
   ```
   If `RIO_SERVICE_TOKEN` is not configured: `signature = "key_unavailable"`.
7. Insert the row into `post_execution_ledger`.
8. Log success or failure. A write failure MUST NOT surface to the caller.

**Outputs:**

| Field | Type | Description |
|-------|------|-------------|
| New row | — | Row appended to `post_execution_ledger`. |
| `ledger_hash` | string (hex) | SHA-256 seal of the new entry. |

**Failure Conditions:** Write failures are logged but are silent to the caller. The previous HTTP response was already sent.

**Invariants Enforced:** INV-05 (every execution outcome is audited), INV-04 (ledger chain integrity).

---

## 4. Data Structures and Schemas

### 4.1 Intake Request Schema

The intake request is a JSON object submitted to the governed execution endpoint. All JSON string values are UTF-8 encoded.

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `source` | string | REQUIRED | Non-empty | Caller identifier (e.g., `"manus"`, `"cli"`, `"web"`). Stored as `executed_by` in ledger tables. |
| `intent` | string | REQUIRED | Non-empty | Natural-language instruction for the AI. The text that is cryptographically signed. |
| `signature` | string | REQUIRED | Valid Base64; decodes to DER ECDSA bytes | ECDSA secp256k1/SHA-256/DER signature over `UTF-8_encode(intent)`. Base64-encoded. |
| `timestamp` | string | REQUIRED | ISO-8601 UTC; within `SIGNATURE_WINDOW_SECONDS` of server time | The time at which the signature was produced. MUST match the timestamp used when generating the `execution_token`. |
| `model` | string | OPTIONAL | If present: non-empty | Preferred model. One of `"claude"`, `"chatgpt"`, `"gemini"`, or a string containing their keywords. Auto-detected from intent if omitted. |
| `payload` | object | OPTIONAL | If present: valid JSON object | Supplementary data. `payload.context` (string, ≤300 chars after truncation) is injected into the calibrated intent. |
| `metadata` | object | OPTIONAL | If present: valid JSON object | Caller-supplied metadata. Stored but not processed by the pipeline. |
| `nonce` | string | OPTIONAL (STRONGLY RECOMMENDED) | Non-empty if present; unique per request | Single-use token preventing intent-level replay. Consumed by the Nonce Registry. |
| `execution_token` | string | REQUIRED for execution | Valid Base64; decodes to DER ECDSA bytes | Short-lived ECDSA signature over canonical gate parameters. MUST be generated immediately before the request using `RIO_PRIVATE_KEY`. |

**Example:**
```json
{
  "source": "manus",
  "intent": "Summarise the key properties of the secp256k1 elliptic curve.",
  "signature": "MEUCIQDExample...base64...signature==",
  "timestamp": "2026-03-26T14:00:00.000000Z",
  "model": "claude",
  "payload": {},
  "metadata": { "request_id": "req_abc123" },
  "nonce": "a1b2c3d4e5f6a7b8a1b2c3d4e5f6a7b8",
  "execution_token": "MEQCIAExample...base64...token=="
}
```

### 4.2 Intake Response Schema

The HTTP 200 response to a successful governed execution request.

| Field | Type | Always Present | Description |
|-------|------|---------------|-------------|
| `status` | string | Yes | Always `"success"` on HTTP 200. |
| `model_used` | string | Yes | Model identifier that handled the request: `"claude"`, `"chatgpt"`, or `"gemini"`. |
| `response` | string | Yes | Complete text response from the AI model. |
| `signature_verified` | boolean | Yes | Always `true` on HTTP 200 (Sovereign Gate passed). |
| `signature_hash` | string (hex) | Yes | SHA-256 of the raw DER signature bytes. Primary key in `used_signatures`. |
| `receipt_hash` | string (hex) | Yes | SHA-256 seal of the in-memory ledger entry for this execution. |
| `ledger_index` | integer | Yes | Sequential 1-based position in the in-memory ledger. |
| `timestamp` | string | Yes | ISO-8601 UTC timestamp of when the response was produced (the ledger commit time). |

### 4.3 Execution Token Schema

The object returned by the token-generation service when an execution token is requested.

| Field | Type | Description |
|-------|------|-------------|
| `token` | string (Base64) | The execution token. Base64-encoded DER ECDSA signature over `canonical_bytes`. |
| `timestamp` | string | ISO-8601 UTC timestamp used in canonical encoding. THIS value MUST be used unchanged as the `timestamp` field of the intake request. |
| `parameters_hash` | string (hex) | SHA-256 of `canonical_bytes`. Stored in both ledger tables as a cross-reference key. |

**Critical constraint:** The `timestamp` field returned in the execution token object MUST be used verbatim as the `timestamp` field of the subsequent intake request. Any modification to the timestamp will cause canonical encoding mismatch and Guard 5 will reject the token.

### 4.4 Gate Receipt Schema

The object returned by `check_gate` on successful gate passage. Produced internally in Stage 3 and consumed in Stages 6 and 8.

| Field | Type | Description |
|-------|------|-------------|
| `gate_verified` | boolean | Always `true` when returned (failures raise exceptions, not return values). |
| `receipt_hash` | string (hex) | SHA-256 of the gate passage event string (see Section 5.5). |
| `intent_hash` | string (hex) | SHA-256(`UTF-8_encode(intent)`). |
| `source` | string | The `source` field from gate parameters. |
| `timestamp` | string | ISO-8601 UTC of gate passage. |
| `parameters_hash` | string (hex) | SHA-256 of canonical bytes. Used as the cross-reference key in both ledger tables. |
| `approver` | string | Key fingerprint: first 16 hex chars of SHA-256(`RIO_PUBLIC_KEY_raw_bytes`). |

### 4.5 In-Memory Ledger Entry Schema

One entry in the process-lifetime hash-chain ledger. The ledger is append-only and does not survive process restarts.

| Field | Type | Description |
|-------|------|-------------|
| `ledger_index` | integer | Sequential 1-based position. Autoincremented on each append. |
| `receipt_hash` | string (hex) | SHA-256 seal of this entry (see Section 5.8). Becomes `prev_hash` of the next entry. |
| `prev_hash` | string (hex or "GENESIS") | `receipt_hash` of the immediately preceding entry. `"GENESIS"` for the first entry. |
| `source` | string | Caller identifier. |
| `intent_hash` | string (hex) | SHA-256(`UTF-8_encode(intent)`). |
| `model` | string | Model identifier used for execution. |
| `response_chars` | integer | Character length of the AI response. |
| `timestamp` | string | ISO-8601 UTC of the ledger commit. |

### 4.6 Execution Ledger Entry Schema (SQLite)

One row in the `execution_ledger` table in `gateway.db`. One row is written per `check_gate` invocation, regardless of outcome.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | No | Row identifier. Determines chain order. |
| `action` | TEXT | No | Always `"check_gate"`. Reserved for future gate action types. |
| `agent` | TEXT | No | AI model identifier, or empty string if not yet resolved at gate time. |
| `approver` | TEXT | No | Key fingerprint: first 16 hex chars of SHA-256(`RIO_PUBLIC_KEY_raw`). `"key_unavailable"` if key not set. |
| `executed_by` | TEXT | No | Value of `source` from the intake request. |
| `intent_id` | TEXT | No | SHA-256(`UTF-8_encode(intent)`). |
| `parameters_hash` | TEXT | No | SHA-256(canonical_bytes). Cross-reference to `post_execution_ledger`. |
| `result` | TEXT | No | `"executed"` if gate passed; `"blocked"` if any guard failed. |
| `reason` | TEXT | No | `"gate_passed"` on success; a reason code string on failure. |
| `receipt_hash` | TEXT | No | Gate receipt hash on success (see Section 5.5); empty string on failure. |
| `prev_hash` | TEXT | No | `entry_hash` of the previous row by `id`, or `"GENESIS"` for the first row. |
| `entry_hash` | TEXT | No | SHA-256 seal of this row (see Section 5.6). |
| `timestamp` | TEXT | No | ISO-8601 UTC when the row was written. |

**Indexes:** `(timestamp)`, `(result)`, `(executed_by)`, `(agent)`.

### 4.7 Post-Execution Ledger Entry Schema (SQLite)

One row in the `post_execution_ledger` table in `gateway.db`. One row is written asynchronously after each successful AI execution.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | No | Row identifier. Determines chain order. |
| `timestamp` | TEXT | No | ISO-8601 UTC when the AI execution completed and this row was written. |
| `approver` | TEXT | No | Key fingerprint: first 16 hex chars of SHA-256(`RIO_PUBLIC_KEY_raw`). |
| `agent` | TEXT | No | AI model string that executed (e.g., `"claude-sonnet-4-6"`). |
| `executed_by` | TEXT | No | Value of `source` from the intake request. |
| `policy_result` | TEXT | No | `"success"` on successful execution; `"error:<message>"` on error. |
| `parameters_hash` | TEXT | No | SHA-256(canonical_bytes). Cross-reference to `execution_ledger`. |
| `result_hash` | TEXT | No | SHA-256(`UTF-8_encode(ai_response)`). |
| `ledger_hash` | TEXT | No | SHA-256 chain seal of this entry (see Section 5.7). |
| `signature` | TEXT | No | HMAC-SHA256(`ledger_hash`, `RIO_SERVICE_TOKEN`). `"key_unavailable"` if token not set. |

**Indexes:** `(timestamp)`, `(agent)`, `(executed_by)`, `(policy_result)`.

### 4.8 Signature Registry Entry Schema

One row in the `used_signatures` table in `gateway.db`. One row is written per incoming request (in Stage 1) to enforce signature-level single-use.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `signature_hash` | TEXT PRIMARY KEY | No | SHA-256(Base64_decode(signature)). The deduplication key. |
| `intent` | TEXT | Yes | The raw intent text associated with this signature (for audit). |
| `used_at` | TEXT | Yes | ISO-8601 UTC timestamp of first use. |
| `expires_at` | REAL | No | Unix epoch float. Row MAY be evicted when `expires_at <= Unix_now`. |

**Index:** `(expires_at)` for efficient TTL eviction.

### 4.9 Gate Log Entry Schema

One row in the `gate_log` table in `gateway.db`. Written for every `check_gate` invocation alongside the `execution_ledger` entry. Serves as a simpler event log for operational monitoring.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INTEGER PK AUTOINCREMENT | No | Row identifier. |
| `event` | TEXT | No | `"gate_passed"` or `"unauthorized execution attempt"`. |
| `intent_hash` | TEXT | Yes | SHA-256(`UTF-8_encode(intent)`). |
| `source` | TEXT | Yes | Caller identifier. |
| `receipt_hash` | TEXT | Yes | Gate receipt hash on success; empty string on failure. |
| `timestamp` | TEXT | No | ISO-8601 UTC when the event occurred. |

**Index:** `(timestamp)`.

---

## 5. Cryptographic Specifications

This section specifies every cryptographic operation in the RIO Protocol with sufficient precision that an implementer in any programming language can produce byte-identical outputs and verify signatures produced by the reference implementation.

### 5.1 Algorithm Suite

| Operation | Algorithm | Parameters |
|-----------|-----------|-----------|
| Asymmetric signing (intents and tokens) | ECDSA | Curve: secp256k1; Hash: SHA-256; Encoding: DER |
| Message hashing (SHA-256) | SHA-256 | FIPS 180-4 |
| HMAC sealing (post-exec ledger) | HMAC-SHA256 | Key: UTF-8(`RIO_SERVICE_TOKEN`) |
| Signature transport | Base64 | RFC 4648; alphabet `A–Za–z0–9+/`; `=` padding |
| Hash output format | Hex | Lowercase; 64 characters for SHA-256 |

### 5.2 Key Material Specification

#### 5.2.1 RIO_PUBLIC_KEY

The ECDSA secp256k1 public verifying key. MUST be present as an environment variable named `RIO_PUBLIC_KEY`. The gateway normalizes four storage formats:

| Format | Detection Criterion | Normalization Procedure |
|--------|--------------------|-----------------------|
| **PEM with proper newlines** | Contains `"-----BEGIN PUBLIC KEY-----"` with embedded `\n` | Strip leading/trailing whitespace; use as-is. |
| **Replit-collapsed PEM** | Contains `"-----BEGIN PUBLIC KEY-----"` but line breaks have been replaced with spaces | Extract body between header and footer; strip all whitespace; re-wrap at exactly 64 characters per line; reconstruct PEM. |
| **Bare Base64 body** | No PEM markers; string consists of Base64 characters | Strip all whitespace; re-wrap at 64 characters per line; prepend `-----BEGIN PUBLIC KEY-----\n`; append `\n-----END PUBLIC KEY-----\n`. |
| **Hex-encoded point** | After stripping `0x` prefix: string matches `[0-9a-fA-F]+` AND length is 66 (compressed) or 130 (uncompressed) characters | Decode hex to bytes; load as raw secp256k1 point. |

If `RIO_PUBLIC_KEY` is not set or cannot be parsed by any format handler: all requests MUST be blocked with HTTP 503.

#### 5.2.2 RIO_PRIVATE_KEY

The ECDSA secp256k1 private signing key. MUST be present as an environment variable named `RIO_PRIVATE_KEY`. The gateway normalizes three storage formats:

| Format | Detection Criterion | Normalization Procedure |
|--------|--------------------|-----------------------|
| **PEM with proper newlines** | Contains `"-----BEGIN EC PRIVATE KEY-----"` with embedded `\n` | Strip leading/trailing whitespace; use as-is. |
| **Replit-collapsed PEM** | Contains `"-----BEGIN"` but line breaks replaced with spaces | Same collapse-recovery procedure as public key. |
| **Bare Base64 body** | No PEM markers | Strip whitespace; re-wrap at 64 chars; wrap with `-----BEGIN EC PRIVATE KEY-----` / `-----END EC PRIVATE KEY-----`. |

**Security requirement:** The private key MUST NEVER be logged, included in any response body, or returned to any caller. Key loading functions MUST be isolated and MUST NOT expose the key material to other functions.

#### 5.2.3 Key Pairing Requirement

`RIO_PUBLIC_KEY` and `RIO_PRIVATE_KEY` MUST form a valid secp256k1 key pair. Signatures produced by `RIO_PRIVATE_KEY` MUST be verifiable by `RIO_PUBLIC_KEY`. If the keys do not match, all intent signatures and all execution token verifications will fail.

### 5.3 Intent Signature Construction

To produce a valid Sovereign Gate signature over an intent:

```
Step 1:  message_bytes  = UTF-8_encode(intent_string)
Step 2:  digest         = SHA-256(message_bytes)           [computed internally by ECDSA]
Step 3:  (r, s)         = ECDSA_sign(message_bytes,
                                     key    = RIO_PRIVATE_KEY,
                                     curve  = secp256k1,
                                     hash   = SHA-256)
Step 4:  sig_bytes      = DER_encode(r, s)
Step 5:  signature_b64  = Base64_encode(sig_bytes)
Step 6:  timestamp      = UTC_now formatted as ISO-8601 (e.g., "2026-03-26T14:00:00.000000Z")
```

Output: `(signature_b64, timestamp)`. Both MUST be included in the intake request.

**DER encoding:** The DER-encoded ECDSA signature is the standard ASN.1 DER SEQUENCE of two INTEGERs (r, s):
```
0x30 [total_length] 0x02 [r_length] [r_bytes] 0x02 [s_length] [s_bytes]
```
If the high bit of the first byte of `r` or `s` is set, a `0x00` prefix byte MUST be prepended to that integer to indicate positive sign.

### 5.4 Execution Token Construction

The execution token proves server-side authorization of a specific set of gate parameters.

```
Step 1:  timestamp       = UTC_now formatted as ISO-8601 (MUST be used verbatim in intake request)
Step 2:  canonical_str   = intent + "|" + source + "|" + timestamp
Step 3:  canonical_bytes = UTF-8_encode(canonical_str)
Step 4:  sig_bytes       = ECDSA_sign(canonical_bytes,
                                      key   = RIO_PRIVATE_KEY,
                                      curve = secp256k1,
                                      hash  = SHA-256,
                                      encoding = DER)
Step 5:  token           = Base64_encode(sig_bytes)
Step 6:  parameters_hash = SHA-256(canonical_bytes)
```

Output: `{ "token": token, "timestamp": timestamp, "parameters_hash": parameters_hash }`.

**Canonical encoding rules:**
- Fields: `intent`, `source`, `timestamp` in that exact order.
- Separator: the pipe character `|` (U+007C). Not URL-encoded. Not escaped.
- Encoding: UTF-8 bytes of the concatenated string.
- No trailing separator. No leading whitespace. No newlines.

**Verification (Guard 5 of check_gate):**
```
Step 1:  canonical_bytes = UTF-8_encode(intent + "|" + source + "|" + timestamp)
Step 2:  sig_bytes       = Base64_decode(execution_token)
Step 3:  result          = ECDSA_verify(sig_bytes, canonical_bytes,
                                        key   = RIO_PUBLIC_KEY,
                                        curve = secp256k1,
                                        hash  = SHA-256,
                                        decoding = DER)
Step 4:  if result is BadSignatureError → block (reason: invalid_signature)
         if result is any other error   → block (reason: verification_error:<exc>)
         if result is success           → proceed
```

### 5.5 Hash Computation Rules

All SHA-256 hash computations in the RIO Protocol:
1. Encode the input string to bytes using UTF-8.
2. Apply SHA-256 (FIPS 180-4).
3. Return the result as a 64-character lowercase hexadecimal string.

**Specific hash computations:**

| Hash | Formula | Notes |
|------|---------|-------|
| `intent_id` | `SHA-256(UTF-8_encode(intent))` | Used in `execution_ledger.intent_id` and `gate_log.intent_hash`. |
| `parameters_hash` | `SHA-256(UTF-8_encode(intent + "|" + source + "|" + timestamp))` | Cross-reference key. |
| `signature_hash` | `SHA-256(Base64_decode(signature_b64))` | Input is raw bytes, not a string. |
| `result_hash` | `SHA-256(UTF-8_encode(ai_response))` | Full response string. |
| `receipt_hash (gate)` | `SHA-256(UTF-8_encode("GATE_PASSED|" + intent_id + "|" + source + "|" + ts))` | Gate passage event. |

### 5.6 Execution Ledger Entry Hash

The `entry_hash` of each `execution_ledger` row is the SHA-256 seal of that row's content. It forms the chain link for the next row.

**Exact computation:**

```
seal_data  = action
           + "|" + agent
           + "|" + approver
           + "|" + executed_by
           + "|" + intent_id
           + "|" + parameters_hash
           + "|" + result
           + "|" + reason
           + "|" + receipt_hash
           + "|" + prev_hash
           + "|" + timestamp
entry_hash = SHA-256(UTF-8_encode(seal_data))
```

**Field order:** The fields MUST be concatenated in exactly the order shown. The separator is `|` (U+007C). There is no trailing separator. For a `blocked` entry, `receipt_hash` is an empty string; the corresponding `|` separator and empty string MUST still be present in `seal_data`.

**Chain link:** The `prev_hash` field of row N MUST equal the `entry_hash` of the row with `id = N-1` (the immediately preceding row by insertion order). The row with the smallest `id` MUST have `prev_hash = "GENESIS"`.

### 5.7 Post-Execution Ledger Hash and HMAC Seal

The `ledger_hash` and `signature` of each `post_execution_ledger` row provide tamper evidence and independent verifiability.

**Step 1: Compute result_hash:**
```
result_hash = SHA-256(UTF-8_encode(ai_response_string))
```

**Step 2: Fetch prev_ledger_hash:**
```
prev_ledger_hash = ledger_hash of the most recent row by id
                   OR "GENESIS" if the table is empty
```

**Step 3: Compute ledger_hash:**
```
seal_data   = timestamp
            + "|" + approver
            + "|" + agent
            + "|" + executed_by
            + "|" + policy_result
            + "|" + parameters_hash
            + "|" + result_hash
            + "|" + prev_ledger_hash
ledger_hash = SHA-256(UTF-8_encode(seal_data))
```

**Field order:** The fields MUST be concatenated in exactly the order shown.

**Step 4: Compute HMAC signature:**
```
hmac_key  = UTF-8_encode(RIO_SERVICE_TOKEN)
signature = HMAC-SHA256(key = hmac_key,
                        msg = UTF-8_encode(ledger_hash))
            output as lowercase hexadecimal string
```

If `RIO_SERVICE_TOKEN` is not configured: `signature = "key_unavailable"`.

**Chain link:** The `prev_ledger_hash` input in Step 3 MUST equal the `ledger_hash` stored in the immediately preceding row by `id`. The first row uses `"GENESIS"` as `prev_ledger_hash`.

### 5.8 In-Memory Ledger Receipt Hash

The `receipt_hash` of each in-memory ledger entry seals the entry and chains to the next.

```
data         = prev_hash
             + "|" + source
             + "|" + intent
             + "|" + model_used
             + "|" + ai_response[:500]
             + "|" + timestamp
receipt_hash = SHA-256(UTF-8_encode(data))
```

**Note:** Only the first 500 characters of `ai_response` are included. The truncation is applied before concatenation: if `len(ai_response) > 500`, use `ai_response[0:500]`. If `len(ai_response) <= 500`, use the full string.

**Chain link:** The first entry in the in-memory ledger uses `prev_hash = "GENESIS"`. Each subsequent entry's `prev_hash` is the `receipt_hash` of the immediately preceding entry.

### 5.9 Signature Registry Fingerprint

```
raw_sig_bytes  = Base64_decode(signature_b64_from_intake_request)
signature_hash = SHA-256(raw_sig_bytes)
```

The `raw_sig_bytes` are the raw DER-encoded ECDSA bytes, not the Base64 representation. The `signature_hash` is used as the PRIMARY KEY in `used_signatures`.

### 5.10 Key Fingerprint (Approver Field)

```
raw_key_env    = strip_whitespace(RIO_PUBLIC_KEY_environment_variable)
raw_key_bytes  = UTF-8_encode(raw_key_env)
full_hash      = SHA-256(raw_key_bytes)
approver       = full_hash[:16]     [first 16 hexadecimal characters]
```

If `RIO_PUBLIC_KEY` is not set: `approver = "key_unavailable"`.

The `approver` field identifies the cryptographic authority responsible for all gate decisions. It appears in every `execution_ledger` row and every `post_execution_ledger` row.

### 5.11 Encoding Rules

| Value | Encoding |
|-------|---------|
| All hash digests | Lowercase hexadecimal string, 64 characters for SHA-256 |
| HMAC output | Lowercase hexadecimal string, 64 characters for HMAC-SHA256 |
| ECDSA signatures (transport) | Standard Base64 (RFC 4648) with `=` padding |
| String-to-bytes conversion | UTF-8 encoding throughout |
| Timestamps | ISO-8601 UTC, format `YYYY-MM-DDTHH:MM:SS.ffffffZ` (microsecond precision preferred) |
| Pipe separator in canonical strings | Literal ASCII `|` (U+007C); not URL-encoded, not backslash-escaped |
| Chain anchors | Literal ASCII string `"GENESIS"` (7 characters) |

---

## 6. Verification Protocol

This section specifies how any party — including independent third parties with no access to the runtime — can verify the integrity and authenticity of RIO receipts, ledger entries, and hash chains.

### 6.1 Sovereign Gate Verification (Seven-Check Sequence)

A verifier replaying the Sovereign Gate checks applies the following sequence to an intake request. Each check MUST pass for the intent to be considered authentically authorized.

| Check | Name | Procedure | Pass Criterion |
|-------|------|-----------|----------------|
| 1 | Key Availability | Confirm `RIO_PUBLIC_KEY` is present and parseable in one of the four supported formats. | Key loads without error. |
| 2 | Timestamp Freshness | Parse `timestamp` as ISO-8601 UTC. Compute `delta = abs(verify_time - timestamp)`. | `delta <= SIGNATURE_WINDOW_SECONDS`. Note: an archived request's timestamp may be outside the window; this check applies to real-time gatekeeping only. |
| 3 | Signature Presence | Confirm `signature` field is present and non-empty. | Field exists and length > 0. |
| 4 | Base64 Validity | Base64-decode `signature`. | Decodes without error. |
| 5 | ECDSA Validity | Verify decoded signature bytes against `UTF-8_encode(intent)` using `RIO_PUBLIC_KEY`, curve secp256k1, SHA-256, DER decoding. | Verification succeeds (no BadSignatureError). |
| 6 | Nonce Status | Determine whether the nonce (if present) was a first use or replay. | For gatekeeping: first use only. For post-hoc audit: registry not available, so skip. |
| 7 | Registry Status | Determine whether `SHA-256(Base64_decode(signature))` appears in `used_signatures`. | For gatekeeping: must not be present. For post-hoc audit: must be present (proves it was accepted). |

### 6.2 Execution Gate Verification (Five-Guard Sequence)

An independent verifier replaying the Execution Gate checks requires: the `intent`, `source`, and `timestamp` values from the intake request, the `execution_token` value, and `RIO_PUBLIC_KEY`.

```
Step 1:  canonical_bytes = UTF-8_encode(intent + "|" + source + "|" + timestamp)
Step 2:  sig_bytes       = Base64_decode(execution_token)
Step 3:  result          = ECDSA_verify(sig_bytes, canonical_bytes,
                                        key   = RIO_PUBLIC_KEY,
                                        curve = secp256k1,
                                        hash  = SHA-256,
                                        decoding = DER)
Step 4:  Confirm timestamp is within window (for real-time verification).
Step 5:  Confirm intent, source, and timestamp are all non-empty.
```

A verifier who obtains `RIO_PUBLIC_KEY`, the `intent`, `source`, `timestamp`, and `execution_token` from any source can verify that the gateway cryptographically authorized execution of that exact parameter set at that exact time.

### 6.3 Execution Ledger Chain Verification

To verify the integrity of the `execution_ledger` chain:

```
Step 1:  Retrieve all rows from execution_ledger ordered by id ASC.
Step 2:  Initialize: prev = "GENESIS"
Step 3:  For each row in order:
           a. Recompute entry_hash:
              seal_data  = row.action + "|" + row.agent + "|" + row.approver
                         + "|" + row.executed_by + "|" + row.intent_id
                         + "|" + row.parameters_hash + "|" + row.result
                         + "|" + row.reason + "|" + row.receipt_hash
                         + "|" + row.prev_hash + "|" + row.timestamp
              computed   = SHA-256(UTF-8_encode(seal_data))
           b. Verify: computed == row.entry_hash   [hash integrity]
           c. Verify: row.prev_hash == prev          [chain linkage]
           d. Set: prev = row.entry_hash
Step 4:  If any check in step 3b or 3c fails: chain is NOT intact. Report first failure.
Step 5:  If all checks pass: chain is intact.
```

The `GET /execution-gate/audit-log` endpoint (with `verify_chain=true`) performs this verification automatically and returns `chain_intact: true/false`.

### 6.4 Post-Execution Ledger Chain and Signature Verification

To verify the integrity of the `post_execution_ledger` chain:

```
Step 1:  Retrieve all rows from post_execution_ledger ordered by id ASC.
Step 2:  Initialize: prev_ledger_hash = "GENESIS"
Step 3:  For each row in order:
           a. Recompute ledger_hash:
              seal_data   = row.timestamp + "|" + row.approver + "|" + row.agent
                          + "|" + row.executed_by + "|" + row.policy_result
                          + "|" + row.parameters_hash + "|" + row.result_hash
                          + "|" + prev_ledger_hash
              computed    = SHA-256(UTF-8_encode(seal_data))
           b. Verify: computed == row.ledger_hash   [hash integrity]
           c. Verify: prev_ledger_hash == previous row's ledger_hash (or "GENESIS" for first row)
           d. Recompute signature:
              hmac_key  = UTF-8_encode(RIO_SERVICE_TOKEN)
              expected  = HMAC-SHA256(key=hmac_key, msg=UTF-8_encode(row.ledger_hash))
           e. Verify: expected == row.signature  [HMAC integrity]
           f. Set: prev_ledger_hash = row.ledger_hash
Step 4:  Report per-row results.
```

The `GET /execution-gate/audit-log/{intent_id}` endpoint performs chain verification over the gate entries slice and HMAC verification over post-execution entries for the given intent, returning `chain_intact` and `signatures_valid` booleans.

### 6.5 In-Memory Ledger Chain Verification

The in-memory ledger does not persist across restarts. To verify its chain during a process lifetime:

```
Step 1:  Retrieve all entries from the in-memory ledger ordered by ledger_index ASC.
Step 2:  Initialize: prev = "GENESIS"
Step 3:  For each entry in order:
           a. Recompute receipt_hash:
              data     = prev + "|" + entry.source + "|" + original_intent
                       + "|" + entry.model + "|" + ai_response[:500]
                       + "|" + entry.timestamp
              computed = SHA-256(UTF-8_encode(data))
           b. Verify: computed == entry.receipt_hash
           c. Verify: entry.prev_hash == prev
           d. Set: prev = entry.receipt_hash
```

Note: `original_intent` and `ai_response[:500]` are not stored in the ledger entry (only their hashes or lengths). Full verification of the in-memory receipt hash requires access to the original request data.

### 6.6 Independent Third-Party Verification

An independent verifier with access to only:
- `RIO_PUBLIC_KEY` (the public key — no private key needed)
- `RIO_SERVICE_TOKEN` (the HMAC key — for post-execution signature verification)
- The `execution_ledger` table
- The `post_execution_ledger` table

can independently verify:

1. **Every gate passage:** For any `execution_ledger` row with `result = "executed"`, that the receipt hash is correctly computed from `"GATE_PASSED|" + intent_id + "|" + executed_by + "|" + timestamp`.

2. **Every chain link:** That `entry_hash` of row N equals `prev_hash` of row N+1 for all consecutive rows.

3. **Every post-execution seal:** That `ledger_hash` of each `post_execution_ledger` row is correctly computed from its field values and the previous row's `ledger_hash`.

4. **Every post-execution HMAC:** That `HMAC-SHA256(UTF-8_encode(ledger_hash), UTF-8_encode(RIO_SERVICE_TOKEN))` matches the stored `signature`.

5. **Cross-table linkage:** That `parameters_hash` values in `execution_ledger` and `post_execution_ledger` correctly correspond (same formula, same inputs).

The verifier does NOT need access to the original intent strings (only their hashes), the AI responses (only their hashes), or any runtime process.

### 6.7 Verification Result Format

Verification functions MUST return a structured result containing one record per check performed:

```json
{
  "overall": "pass" | "fail",
  "checks": [
    {
      "check_name": "string — name of the check",
      "passed":     true | false,
      "details":    "string — human-readable explanation"
    }
  ],
  "chain_intact":     true | false | null,
  "signatures_valid": true | false | null
}
```

`chain_intact` is `null` when chain verification was not performed (e.g., empty table). `signatures_valid` is `null` when `RIO_SERVICE_TOKEN` is not available to the verifier.

---

## 7. Protocol Invariants

Protocol invariants are properties that MUST hold for every execution of every request processed by a conforming RIO implementation. Violation of any invariant is a protocol error.

### 7.1 Protocol Invariants (INV-01 through INV-08)

| ID | Invariant | Description |
|----|-----------|-------------|
| **INV-01** | All execution is cryptographically authenticated. | No AI model invocation MAY proceed without a valid ECDSA secp256k1 signature from the holder of `RIO_PRIVATE_KEY` over the exact intent string. |
| **INV-02** | Signatures are single-use. | A given ECDSA signature (identified by `SHA-256(raw_DER_bytes)`) MUST be accepted exactly once. Replays MUST be rejected with HTTP 409 regardless of whether the signature is cryptographically valid. |
| **INV-03** | No execution without execution gate authorization. | No AI model MAY be invoked without a valid execution token verified by `check_gate`. Passing the Sovereign Gate (Stage 2) alone is insufficient for execution. Both gates MUST pass. |
| **INV-04** | Hash chains are append-only and monotonically growing. | Entries MUST be appended in order. `prev_hash` of row N MUST equal `entry_hash` of row N-1. No existing entry MAY be modified or deleted. |
| **INV-05** | Every gate decision is audited. | Every invocation of `check_gate` — whether it results in `"executed"` or `"blocked"` — MUST produce a row in `execution_ledger` AND a row in `gate_log`. A gate invocation without an audit entry is a protocol error. |
| **INV-06** | Infrastructure failures close the gate. | If any verification infrastructure component (signature registry, nonce registry, key loading) raises an error, the request MUST be blocked. No execution MAY proceed when verification cannot be completed. |
| **INV-07** | Loop separation is maintained. | Loop 1 (Intake) MUST complete before Loop 2 (Execution) begins. The Execution Gate (Stage 3) MUST be the last checkpoint before model invocation. Loop 3 (Audit) writes MUST occur after and independently of the HTTP response. |
| **INV-08** | Every governed execution has a receipt. | Every successful AI model execution MUST produce an in-memory ledger entry with a receipt hash, and MUST initiate a post-execution ledger write. The absence of either (other than from infrastructure failure that is logged) is a protocol error. |

### 7.2 System Invariants

System invariants describe properties of the overall system state that MUST hold at all times, not just per-request.

| Category | Invariant |
|----------|-----------|
| **Cryptographic** | The key pair (`RIO_PRIVATE_KEY`, `RIO_PUBLIC_KEY`) MUST be a valid secp256k1 pair. Both MUST be configured for full operation. The private key MUST NEVER appear in any log, response, or exported data. |
| **Ordering** | Ledger rows MUST be ordered by insertion time. `id` AUTOINCREMENT values MUST be monotonically increasing. No row MAY have a `prev_hash` referencing a row with a higher `id`. |
| **Authorization** | Only the holder of `RIO_PRIVATE_KEY` can produce valid intake signatures and valid execution tokens. Since both use the same key, no caller can authorize an execution without also being able to sign the intent. |
| **Audit Completeness** | The union of `execution_ledger` entries and `gate_log` entries constitutes the complete record of all gate decisions. The `post_execution_ledger` records all completed executions. No execution outcome MAY be unrecorded. |
| **Fail-Closed** | The default state of the system, in the absence of a valid, verified intake request, is to deny execution. |
| **Governance** | The `approver` field on every ledger entry identifies the authority that authorized execution. A change in `approver` value across entries indicates a key rotation. |

### 7.3 Invariant Dependencies

The invariants form a dependency graph. Violations propagate:

- **INV-01** depends on: key material being correctly loaded (Section 5.2), ECDSA verification being correctly implemented (Section 5.3).
- **INV-02** depends on: the Signature Registry being durable and correctly implementing atomic claim (Section 3.1), the `expires_at` TTL being correctly enforced.
- **INV-03** depends on: INV-01 (Sovereign Gate), and independently, the Execution Gate (Section 3.3).
- **INV-04** depends on: the `prev_hash` linkage being correctly computed (Section 5.6), database writes being atomic.
- **INV-05** depends on: the `_write_ledger` and `_write_gate_log` calls being made unconditionally in `check_gate`, including on failure paths.
- **INV-06** depends on: all verification infrastructure raising exceptions on error (not silently returning success).
- **INV-07** depends on: the pipeline stage ordering being implemented in strict sequence (Section 2.2).
- **INV-08** depends on: Stage 7 and Stage 8 being unconditionally invoked after Stage 6 success.

### 7.4 Emergency Kill Switch (EKS-0)

The RIO Protocol MUST support an emergency kill switch that can immediately halt all execution without requiring code changes. The reference implementation's kill switch operates as follows:

**Mechanism:** Remove or invalidate `RIO_PUBLIC_KEY` from the environment. Immediately, all incoming requests will fail at:
- Stage 2, Check 1 (Sovereign Gate: key not configured → HTTP 503), AND
- Stage 3, Guard 4 (Execution Gate: key unavailable → HTTP 403).

All blocked attempts will be recorded in `execution_ledger` with `result = "blocked"` and `reason = "key_unavailable"` or `reason = "key_not_configured"`, maintaining the complete audit trail.

**Properties of EKS-0:**
- **Immediate effect:** Takes effect on the next request; no process restart required.
- **Non-destructive:** Does not delete or modify any audit data.
- **Reversible:** Restoring `RIO_PUBLIC_KEY` re-enables the system.
- **Auditable:** All blocked attempts during the kill switch period are recorded.

Conforming implementations MUST support an equivalent kill switch mechanism that satisfies all four properties above.

---

## 8. Conformance Requirements

This section defines what it means to be RIO-compliant and establishes three progressive conformance levels. These levels are new content defined by this specification; they do not exist in any prior document.

### 8.1 Conformance Levels

A conforming implementation MUST explicitly claim one of the following three conformance levels. Each higher level includes all requirements of the lower levels.

| Level | Name | Summary |
|-------|------|---------|
| Level 1 | Cryptographic Compliance | Produces correct cryptographic artifacts: valid signatures, correct hash computations, correct ledger entry sealing. |
| Level 2 | Pipeline Compliance | Implements all eight pipeline stages in order, enforces all eight protocol invariants, produces execution ledger entries for every gate decision. |
| Level 3 | Full Protocol Compliance | Level 2 plus Three-Loop Architecture separation, asynchronous post-execution audit, independent verification support, and kill switch capability. |

### 8.2 Level 1: Cryptographic Compliance

A Level 1 conforming implementation MUST:

1. Use ECDSA secp256k1 with SHA-256 and DER encoding for all asymmetric signature operations.
2. Produce intent signatures such that `ECDSA_verify(sig_bytes, UTF-8_encode(intent), RIO_PUBLIC_KEY, secp256k1, SHA-256, DER)` returns success.
3. Produce execution tokens such that the same verification procedure applied to `UTF-8_encode(intent + "|" + source + "|" + timestamp)` returns success.
4. Compute `parameters_hash` as `SHA-256(UTF-8_encode(intent + "|" + source + "|" + timestamp))`.
5. Compute `intent_id` / `intent_hash` as `SHA-256(UTF-8_encode(intent))`.
6. Compute `signature_hash` as `SHA-256(Base64_decode(signature_b64))`.
7. Compute `approver` as `SHA-256(UTF-8_encode(RIO_PUBLIC_KEY_raw_env))[:16]`.
8. Compute `entry_hash` for execution ledger entries exactly as specified in Section 5.6.
9. Compute `ledger_hash` and `signature` for post-execution ledger entries exactly as specified in Section 5.7.
10. Compute `receipt_hash` for in-memory ledger entries exactly as specified in Section 5.8.
11. Use `"GENESIS"` as the initial `prev_hash` / `prev_ledger_hash` for the first row in any chain.
12. Produce all hash values as lowercase 64-character hexadecimal strings.
13. Encode all signatures in Base64 (RFC 4648).

**Conformance test vectors:** See Appendix C for exact test inputs and expected SHA-256 outputs.

### 8.3 Level 2: Pipeline Compliance

A Level 2 conforming implementation MUST satisfy all Level 1 requirements and additionally:

1. Implement all eight pipeline stages in the exact order defined in Section 3.
2. Block execution and return an appropriate error at each stage's defined failure conditions without advancing to the next stage.
3. Implement the Signature Registry with atomic check-and-insert semantics (INV-02), persistent storage across restarts, and TTL-based eviction.
4. Implement the Sovereign Gate with all six checks (Section 3.2) in order.
5. Implement the Execution Gate (`check_gate`) with all five guards (Section 3.3) in order.
6. Write both a `gate_log` entry and an `execution_ledger` entry for every `check_gate` invocation, whether the result is `"executed"` or `"blocked"` (INV-05).
7. Compute and store `prev_hash` / `entry_hash` correctly for every `execution_ledger` entry (INV-04).
8. Write a `post_execution_ledger` entry for every successful AI model execution (INV-08).
9. Compute and store `ledger_hash` and `signature` correctly for every `post_execution_ledger` entry.
10. Enforce INV-01 through INV-08 as specified in Section 7.1.
11. Include `receipt_hash`, `ledger_index`, `signature_hash`, `model_used`, `signature_verified`, and `timestamp` in the HTTP 200 response.
12. Return the exact HTTP status codes specified in Section 6.7 for each failure condition.

### 8.4 Level 3: Full Protocol Compliance

A Level 3 conforming implementation MUST satisfy all Level 2 requirements and additionally:

1. **Three-Loop Architecture.** Structurally separate the Intake Loop (Stages 1–2, 4–5), Execution Loop (Stage 3, 6–7), and Audit Loop (Stage 8) such that Loop 3 writes occur asynchronously and never delay the HTTP response to the caller.
2. **Asynchronous Audit.** The post-execution ledger write (Stage 8) MUST be initiated as a non-blocking, fire-and-forget task. Its completion or failure MUST NOT affect the HTTP response returned by Stage 7.
3. **Independent Verification Support.** Expose verification interfaces that allow an external party with only `RIO_PUBLIC_KEY` and `RIO_SERVICE_TOKEN` to: (a) verify chain integrity of `execution_ledger`, (b) verify chain integrity and HMAC signatures of `post_execution_ledger`, (c) look up and verify any receipt hash or ledger hash.
4. **Nonce Registry.** Implement the in-memory Nonce Registry with TTL-based eviction and fail-closed semantics (Section 3.2, Check 6).
5. **Key Fingerprint Stability.** The `approver` field MUST be computed consistently for all entries from the same key. A change in `approver` value in consecutive entries MUST be treated as a key rotation event.
6. **Emergency Kill Switch.** Support EKS-0 as specified in Section 7.4. Removing `RIO_PUBLIC_KEY` MUST immediately halt all execution while maintaining full audit coverage of blocked attempts.
7. **Cross-Table Linkage.** The `parameters_hash` field MUST enable unambiguous cross-reference between corresponding `execution_ledger` and `post_execution_ledger` entries for the same intake request.
8. **Model Routing Determinism.** For a given `(model_field, calibrated_intent)` pair, the same model MUST always be selected. Model routing MUST be a pure function (no randomness, no external state).

### 8.5 Conformance Testing

A conforming implementation SHOULD be validated against the following test categories:

| Category | Tests |
|----------|-------|
| **Cryptographic Correctness** | Hash computation test vectors (Appendix C); signature round-trip (sign with private key, verify with public key); DER encoding round-trip. |
| **Replay Prevention** | Submit the same signed request twice; second attempt MUST receive HTTP 409. Submit the same nonce twice; second attempt MUST receive HTTP 401. |
| **Fail-Closed Behavior** | Submit request without `execution_token`; MUST receive HTTP 403. Submit request with `RIO_PUBLIC_KEY` unset; MUST receive HTTP 503. Submit request with timestamp > 300s old; MUST receive HTTP 401. |
| **Chain Integrity** | After N successful requests, verify `execution_ledger` chain is intact. Modify any ledger entry (in a test copy); verify chain integrity check returns `false`. |
| **HMAC Verification** | Verify HMAC signatures on `post_execution_ledger` entries using `RIO_SERVICE_TOKEN`. |
| **Guard Ordering** | Verify that a request missing a required field (Guard 1 failure) does not produce a `missing_token` error (Guard 3); the first failing guard's error MUST be returned. |
| **Audit Completeness** | After a blocked request, verify exactly one row appears in `execution_ledger` with `result = "blocked"` and one row in `gate_log` with `event = "unauthorized execution attempt"`. |

---

## 9. Security Considerations

### 9.1 Threat Model Summary

The RIO Protocol is designed to defend against the following categories of threat. This section provides a summary; the full threat model is maintained as a separate document.

| Threat Category | RIO Mitigations |
|-----------------|-----------------|
| **Unauthorized AI execution** | Sovereign Gate (ECDSA intent authentication) + Execution Gate (ECDSA token authorization). Both must pass; neither alone is sufficient. |
| **Replay attacks** | Signature Registry (per-signature single-use, TTL-backed, disk-persistent) + Nonce Registry (per-nonce single-use, in-memory) + Timestamp freshness window (300s). Three independent replay defenses. |
| **Ledger tampering** | Hash-chain construction with SHA-256 entry seals. Any modification to any field of any row breaks the chain for all subsequent rows. Post-execution entries additionally carry HMAC-SHA256 signatures. |
| **Intent substitution** | The signed message is always `UTF-8_encode(intent)`. The execution token canonical bytes include the intent. Both gates verify the same key pair. Substituting a different intent invalidates both signatures. |
| **Infrastructure failures enabling execution** | Fail-closed principle (INV-06). Any infrastructure error — key unavailable, database unreachable, verification exception — blocks execution. No silent fallback. |
| **Concurrent replay** | Atomic check-and-insert in Stage 1 with SQLite UNIQUE constraint. Both the SELECT-and-INSERT sequence and the IntegrityError path deny concurrent replays. |
| **Post-execution denial** | Post-execution ledger is asynchronous and its failure does not affect receipts already delivered. This is an accepted design trade-off. Audit gaps from Stage 8 failures are logged. |
| **Key exposure** | `RIO_PRIVATE_KEY` is loaded into memory only inside signing functions and is never referenced outside them. It is never logged, never returned in responses, and never assigned to a module-level variable. |

### 9.2 Trust Boundaries

The four trust boundaries (TB-1 through TB-4, see Section 2.4) enforce the following security properties:

- **TB-1 (Intake Boundary):** A caller who cannot produce a valid ECDSA secp256k1 signature over an intent cannot enter the pipeline. The signature proves possession of `RIO_PRIVATE_KEY`.
- **TB-2 (Signature Registry Boundary):** Even a legitimate caller who produces valid signatures cannot replay them. The registry enforces first-use-only semantics durably.
- **TB-3 (Execution Boundary):** Even if a request passes TB-1 and TB-2, execution requires a separately generated execution token. The token is produced immediately before the request and is valid for only 300 seconds. An attacker who intercepts a signed intent but cannot generate a corresponding execution token (because they lack `RIO_PRIVATE_KEY`) cannot execute it.
- **TB-4 (Audit Boundary):** The audit ledger is append-only. Callers have no write path to ledger tables. The ledger is inaccessible except through read-only query interfaces.

### 9.3 Role Separation

The RIO Protocol assumes a single-authority model in version 1.0: the holder of `RIO_PRIVATE_KEY` is both the signer of intents and the generator of execution tokens. This means the same party controls both authorization layers.

Future versions of the protocol MAY introduce multi-party authorization where:
- Intent signing uses one key pair (caller)
- Execution token generation uses a separate key pair (approver)

In version 1.0, the single key pair enforces the constraint that only a party with direct access to `RIO_PRIVATE_KEY` can authorize executions. This is intentional for personal gateway deployments.

### 9.4 Key Management Security

Implementers MUST observe the following key management requirements:

1. **Private key isolation.** `RIO_PRIVATE_KEY` MUST be stored in a secret management system (environment secrets, vault, HSM). It MUST NOT be stored in source code, configuration files, or version control.
2. **Key rotation.** The key pair SHOULD be rotatable without system downtime. After rotation: (a) update `RIO_PUBLIC_KEY` and `RIO_PRIVATE_KEY`; (b) the `approver` field in subsequent ledger entries will reflect the new key fingerprint; (c) prior entries remain valid under their original key fingerprint.
3. **HMAC key rotation.** `RIO_SERVICE_TOKEN` rotation invalidates the ability to verify HMAC signatures on pre-rotation `post_execution_ledger` entries. Implementers MUST archive the old token alongside old entries if retrospective verification is required.
4. **Key size adequacy.** The secp256k1 curve provides approximately 128-bit security. This is sufficient for the threat model in version 1.0. Future versions may specify additional algorithms.
5. **Nonce generation.** Callers generating nonces MUST use a cryptographically secure random source. Nonces MUST have sufficient entropy (recommended: 128 bits / 32 hex characters minimum) to make collision probability negligible.

---

## Appendix A: Complete Intake Request and Response Examples

### A.1 Example Intake Request

The following is a fully populated intake request. Signature and token values are structurally realistic but are not computed from the exact key pair shown.

```json
{
  "source": "manus",
  "intent": "Summarise the key properties of the secp256k1 elliptic curve in three bullet points.",
  "signature": "MEUCIQDrKZvExample7xLfBase64EncodedDERSignatureOfIntentBytes==",
  "timestamp": "2026-03-26T14:00:00.000000Z",
  "model": "claude",
  "payload": {
    "context": "Audience: software engineers implementing cryptographic systems."
  },
  "metadata": {
    "request_id": "req_20260326_001",
    "caller_version": "2.1.0"
  },
  "nonce": "f7a3b1c9e2d04f8a6b5e1c3a9d7f2b8e",
  "execution_token": "MEQCIBhExample9yKBase64EncodedDERSignatureOfCanonicalBytes=="
}
```

### A.2 Example Successful Response (HTTP 200)

```json
{
  "status": "success",
  "model_used": "claude",
  "response": "The secp256k1 elliptic curve has three key properties:\n\n• **Prime field:** Defined over a 256-bit prime field, giving 128-bit security.\n• **Cofactor 1:** The curve has cofactor h=1, meaning every non-identity point generates the full group — important for cryptographic applications.\n• **Efficiently computable endomorphism:** Supports a Frobenius endomorphism that enables significant speedup in scalar multiplication, which is why it was chosen for Bitcoin and Ethereum.",
  "signature_verified": true,
  "signature_hash": "3a7f9e2b4c1d8e5f0a6b3c9d7e4f1a2b3c9d7e4f1a2b8c5d0e3f6a9b2c5d8e1f",
  "receipt_hash": "8e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f",
  "ledger_index": 42,
  "timestamp": "2026-03-26T14:00:03.847221Z"
}
```

### A.3 Example Blocked Response (HTTP 403)

Response when the execution gate blocks due to a missing execution token:

```json
{
  "error": "Execution blocked",
  "detail": "Execution token is required. All execution must be gate-authorized."
}
```

Response when the sovereign gate blocks due to an expired timestamp:

```json
{
  "status": "unauthorized",
  "error": "Request timestamp outside valid window",
  "message": "Signature is 347s old (limit 300s)"
}
```

---

## Appendix B: Complete Ledger Entry Examples

### B.1 Example Execution Ledger Entry (Successful Gate Passage)

```json
{
  "id": 87,
  "action": "check_gate",
  "agent": "claude",
  "approver": "a1b2c3d4e5f6a7b8",
  "executed_by": "manus",
  "intent_id": "2c7a9f3e1b4d6e8a0c5f7b9d1e3a5c7f9b1d3e5a7c9f1b3d5e7a9c1f3b5d7e9a",
  "parameters_hash": "9f1b3d5e7a9c1f3b5d7e9a2c4f6b8d0e2a4c6f8b0d2e4a6c8f0b2d4e6a8c0f2b",
  "result": "executed",
  "reason": "gate_passed",
  "receipt_hash": "4d6e8a0c2e4a6c8f0b2d4e6a8c0f2b4d6e8a0c2e4a6c8f0b2d4e6a8c0f2b4d6e",
  "prev_hash": "1a3b5c7d9e1a3b5c7d9e1a3b5c7d9e1a3b5c7d9e1a3b5c7d9e1a3b5c7d9e1a3b",
  "entry_hash": "7f9b1d3e5a7c9f1b3d5e7a9c1f3b5d7e9a2c4f6b8d0e2a4c6f8b0d2e4a6c8f0b",
  "timestamp": "2026-03-26T14:00:00.512344Z"
}
```

### B.2 Example Execution Ledger Entry (Blocked — Missing Token)

```json
{
  "id": 88,
  "action": "check_gate",
  "agent": "",
  "approver": "a1b2c3d4e5f6a7b8",
  "executed_by": "unknown-caller",
  "intent_id": "5e7a9c1f3b5d7e9a2c4f6b8d0e2a4c6f8b0d2e4a6c8f0b2d4e6a8c0f2b4d6e8a",
  "parameters_hash": "b0d2e4a6c8f0b2d4e6a8c0f2b4d6e8a0c2e4a6c8f0b2d4e6a8c0f2b4d6e8a0c2",
  "result": "blocked",
  "reason": "missing_token",
  "receipt_hash": "",
  "prev_hash": "7f9b1d3e5a7c9f1b3d5e7a9c1f3b5d7e9a2c4f6b8d0e2a4c6f8b0d2e4a6c8f0b",
  "entry_hash": "3b5d7e9a2c4f6b8d0e2a4c6f8b0d2e4a6c8f0b2d4e6a8c0f2b4d6e8a0c2e4a6c",
  "timestamp": "2026-03-26T14:01:22.003411Z"
}
```

Note that `receipt_hash` is an empty string for blocked entries. The `entry_hash` still covers the empty `receipt_hash` field — the `|` separator and empty string are included in `seal_data`.

### B.3 Example Post-Execution Ledger Entry

```json
{
  "id": 42,
  "timestamp": "2026-03-26T14:00:03.901234Z",
  "approver": "a1b2c3d4e5f6a7b8",
  "agent": "claude-sonnet-4-6",
  "executed_by": "manus",
  "policy_result": "success",
  "parameters_hash": "9f1b3d5e7a9c1f3b5d7e9a2c4f6b8d0e2a4c6f8b0d2e4a6c8f0b2d4e6a8c0f2b",
  "result_hash": "0a2b4c6d8e0a2b4c6d8e0a2b4c6d8e0a2b4c6d8e0a2b4c6d8e0a2b4c6d8e0a2b",
  "ledger_hash": "6b8d0e2a4c6f8b0d2e4a6c8f0b2d4e6a8c0f2b4d6e8a0c2e4a6c8f0b2d4e6a8c",
  "signature": "c8f0b2d4e6a8c0f2b4d6e8a0c2e4a6c8f0b2d4e6a8c0f2b4d6e8a0c2e4a6c8f0"
}
```

The `parameters_hash` in this entry matches the `parameters_hash` in the corresponding `execution_ledger` entry (B.1), linking the gate decision to the execution outcome.

---

## Appendix C: Hash Computation Test Vectors

The following test vectors provide exact inputs and expected SHA-256 outputs. Implementers MUST produce identical outputs for the given inputs to be considered Level 1 conformant.

### C.1 Intent Hash

**Input string:**
```
Summarise the key properties of the secp256k1 elliptic curve in three bullet points.
```

**UTF-8 bytes (hex):**
```
5375...  [83 bytes]
```

**Expected SHA-256 output:**
```
SHA-256(UTF-8_encode("Summarise the key properties of the secp256k1 elliptic curve in three bullet points."))
```

Implementers should verify by computing SHA-256 of the UTF-8 encoding of that exact string (85 characters including the trailing period) and confirming that the implementation matches a known-good SHA-256 library on the same input.

### C.2 Canonical Gate Parameters and Parameters Hash

**Inputs:**
```
intent    = "Summarise the key properties of the secp256k1 elliptic curve in three bullet points."
source    = "manus"
timestamp = "2026-03-26T14:00:00.000000Z"
```

**Canonical string:**
```
Summarise the key properties of the secp256k1 elliptic curve in three bullet points.|manus|2026-03-26T14:00:00.000000Z
```

**parameters_hash** = SHA-256(UTF-8_encode(canonical_string above))

**Verification procedure:** Compute SHA-256 of the UTF-8 encoding of the pipe-separated string shown above. Confirm the result is a 64-character lowercase hex string.

### C.3 Execution Ledger Entry Hash — Blocked Entry

**Inputs (for a Guard 3 failure — missing token, first row in a fresh table):**

```
action           = "check_gate"
agent            = ""
approver         = "a1b2c3d4e5f6a7b8"
executed_by      = "manus"
intent_id        = <SHA-256 from C.1>
parameters_hash  = <SHA-256 from C.2>
result           = "blocked"
reason           = "missing_token"
receipt_hash     = ""
prev_hash        = "GENESIS"
timestamp        = "2026-03-26T14:00:01.000000Z"
```

**Seal data (pipe-delimited, intent_id and parameters_hash abbreviated):**
```
check_gate||a1b2c3d4e5f6a7b8|manus|<intent_id>|<parameters_hash>|blocked|missing_token||GENESIS|2026-03-26T14:00:01.000000Z
```

**entry_hash** = SHA-256(UTF-8_encode(seal_data))

Note: There are two consecutive `||` in the seal data — one between `agent` (empty) and `approver`, and one between `receipt_hash` (empty) and `prev_hash`. Both empty strings MUST be present; omitting them changes the hash.

### C.4 Post-Execution Ledger Hash — First Row

**Inputs:**
```
timestamp        = "2026-03-26T14:00:03.901234Z"
approver         = "a1b2c3d4e5f6a7b8"
agent            = "claude-sonnet-4-6"
executed_by      = "manus"
policy_result    = "success"
parameters_hash  = <SHA-256 from C.2>
result_hash      = SHA-256(UTF-8_encode(ai_response_string))
prev_ledger_hash = "GENESIS"
```

**Seal data:**
```
2026-03-26T14:00:03.901234Z|a1b2c3d4e5f6a7b8|claude-sonnet-4-6|manus|success|<parameters_hash>|<result_hash>|GENESIS
```

**ledger_hash** = SHA-256(UTF-8_encode(seal_data))

**HMAC signature** = HMAC-SHA256(key=UTF-8_encode(RIO_SERVICE_TOKEN), msg=UTF-8_encode(ledger_hash))

Output: lowercase hexadecimal string, 64 characters.

### C.5 In-Memory Ledger Receipt Hash — First Entry

**Inputs:**
```
prev_hash = "GENESIS"
source    = "manus"
intent    = "Summarise the key properties of the secp256k1 elliptic curve in three bullet points."
model     = "claude"
response  = <first 500 chars of ai_response, or full response if shorter>
timestamp = "2026-03-26T14:00:03.847221Z"
```

**Data string:**
```
GENESIS|manus|Summarise the key properties of the secp256k1 elliptic curve in three bullet points.|claude|<response_first_500_chars>|2026-03-26T14:00:03.847221Z
```

**receipt_hash** = SHA-256(UTF-8_encode(data_string))

### C.6 Gate Receipt Hash

**Inputs:**
```
intent_id  = <SHA-256 from C.1>
source     = "manus"
ts         = "2026-03-26T14:00:00.512344Z"
```

**Receipt data string:**
```
GATE_PASSED|<intent_id>|manus|2026-03-26T14:00:00.512344Z
```

**receipt_hash** = SHA-256(UTF-8_encode(receipt_data_string))

### C.7 Key Fingerprint (Approver)

**Input:** The raw value of `RIO_PUBLIC_KEY` environment variable, stripped of leading and trailing whitespace, encoded as UTF-8.

**Computation:**
```
full_hash = SHA-256(UTF-8_encode(stripped_RIO_PUBLIC_KEY_value))
approver  = full_hash[0:16]   [first 16 hex characters = 8 bytes]
```

**Verification:** Given a known `RIO_PUBLIC_KEY` string, compute SHA-256, take the first 16 characters of the hex digest, and compare against the `approver` field in any ledger entry produced by the same gateway configuration.

---

*End of RIO Protocol Specification v1.0*

*This document is derived from the Rio Gateway v3.0 reference implementation. All cryptographic specifications, data structures, and hash computation formulas are derived from the deployed implementation at commit c4b5cce251bd7beb2953ea1e7c6261c5a66714dd.*
