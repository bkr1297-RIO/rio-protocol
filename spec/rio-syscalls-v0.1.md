# RIO System Calls — v0.1

**Status:** Active
**Scope:** Defines the canonical system call interface surface for the RIO governed execution protocol. This document specifies the five namespaces, their operations, input/output contracts, and behavioral requirements.
**Parent Spec:** RIO Operating Spec v0.1 §4

---

## §1 — Overview

The RIO protocol exposes its governance capabilities through five namespaces. Each namespace represents a distinct responsibility boundary. Implementations must provide all operations listed as REQUIRED. Operations listed as OPTIONAL may be omitted without breaking conformance.

---

## §2 — Namespace: `rio.*`

**Responsibility:** Governance, authorization, gate enforcement, intent processing, and kernel execution.

### §2.1 — Root Authority Management

| Operation | Status | Description |
|-----------|--------|-------------|
| `rio.registerRootAuthority(publicKey, metadata)` | REQUIRED | Register the human root authority's Ed25519 public key. Only one root authority may be active at a time. |
| `rio.getActiveRootAuthority()` | REQUIRED | Return the currently active root authority record. |
| `rio.revokeRootAuthority(publicKey)` | REQUIRED | Revoke the specified root authority. System enters fail-closed state until a new root is registered. |
| `rio.verifyRootSignature(payload, signature)` | REQUIRED | Verify a payload signature against the active root authority public key. |

### §2.2 — Policy Management

| Operation | Status | Description |
|-----------|--------|-------------|
| `rio.activatePolicy(policyJson, rootSignature)` | REQUIRED | Activate a new policy. The policy hash is computed from canonical JSON. The root signature must verify. |
| `rio.getActivePolicy()` | REQUIRED | Return the currently active policy with its hash. |
| `rio.revokePolicy(policyHash)` | REQUIRED | Revoke the specified policy. System enters fail-closed state until a new policy is activated. |
| `rio.computePolicyHash(policyJson)` | REQUIRED | Compute the SHA-256 hash of the canonical JSON representation of a policy. |

### §2.3 — Authorization Tokens

| Operation | Status | Description |
|-----------|--------|-------------|
| `rio.issueAuthorizationToken(intentId, toolName, argsHash, policyHash, expiresAt, maxExecutions)` | REQUIRED | Issue a new authorization token binding human authority to a specific intent. |
| `rio.validateAuthorizationToken(tokenId, toolName, argsHash, policyHash)` | REQUIRED | Validate a token before execution. Checks: exists, not expired, not exhausted, args match, policy matches, kill switch not active. Returns pass/fail with denial reasons. |
| `rio.burnAuthorizationToken(tokenId)` | REQUIRED | Increment execution count. Mark consumed if max reached. |

### §2.4 — Gate Enforcement

| Operation | Status | Description |
|-----------|--------|-------------|
| `rio.enforceGate(executionRequest, committedPacket)` | REQUIRED | Post-commit gate validation. Compares the execution request against the committed proposal packet. Returns GATE_VALIDATED or BLOCKED. |
| `rio.executeGatePreflight(intent, approval, policy)` | REQUIRED | Run all preflight checks before execution. Returns structured pass/fail for each check. |

### §2.5 — Intent Processing

| Operation | Status | Description |
|-----------|--------|-------------|
| `rio.processIntent(rawInput, context)` | REQUIRED | Transform raw input into a structured governance packet with hash and metadata. |
| `rio.createIntentEnvelope(intent, metadata)` | REQUIRED | Wrap an intent in a canonical envelope with computed hash. |
| `rio.verifyIntentEnvelope(envelope)` | REQUIRED | Verify the structural integrity and hash of an intent envelope. |

### §2.6 — Execution

| Operation | Status | Description |
|-----------|--------|-------------|
| `rio.kernelExecute(token, connector, args)` | REQUIRED | Execute an approved action through the kernel. Validates token, dispatches to connector, records outcome. Fail-closed on any error. |
| `rio.enforceTheOneRule(action, context)` | REQUIRED | Verify that the proposed action does not violate the One Rule (no action may undermine the governance system itself). |

### §2.7 — Genesis

| Operation | Status | Description |
|-----------|--------|-------------|
| `rio.createGenesisRecord(rootPublicKey, policy)` | REQUIRED | Create the initial ledger entry establishing the governance chain. |
| `rio.verifyGenesisRecord(record)` | REQUIRED | Verify a genesis record's structural integrity and signature. |

---

## §3 — Namespace: `sentinel.*`

**Responsibility:** Anomaly detection, invariant monitoring, signal recording.

**Behavioral constraint:** Sentinel may observe, compare, summarize, and notify. Sentinel must NOT execute, commit, deploy, or modify runtime without explicit human approval.

| Operation | Status | Description |
|-----------|--------|-------------|
| `sentinel.detectContrast(currentBehavior, baseline)` | REQUIRED | Detect behavioral drift between current action patterns and established baseline. |
| `sentinel.detectVelocityAnomaly(actionHistory, window)` | REQUIRED | Detect unusual action frequency within a time window. |
| `sentinel.checkSystemInvariants(systemState)` | REQUIRED | Verify all 10 invariants hold in the current system state. Returns per-invariant pass/fail. |
| `sentinel.detectAuthorizationAnomaly(tokenHistory)` | OPTIONAL | Detect unusual authorization patterns (bulk approvals, unusual timing). |
| `sentinel.recordSignal(signalType, payload)` | REQUIRED | Record an anomaly signal for human review. |
| `sentinel.getUnacknowledgedSignals()` | REQUIRED | Return all signals not yet acknowledged by a human. |
| `sentinel.acknowledgeSignal(signalId)` | REQUIRED | Mark a signal as acknowledged by human review. |
| `sentinel.runSentinelSweep()` | REQUIRED | Execute a full system sweep checking all invariants and anomaly detectors. |

---

## §4 — Namespace: `mus.*`

**Responsibility:** Receipts, cryptographic signing, verification, and export.

MUS = Minimum Undeniable Signature. The receipt and signing subsystem.

### §4.1 — Receipt Generation

| Operation | Status | Description |
|-----------|--------|-------------|
| `mus.generateCanonicalReceipt(fields)` | REQUIRED | Generate a canonical receipt with all required fields (§9.1 of Operating Spec). Computes receipt_hash and links to previous_receipt_hash. |
| `mus.getLastReceiptHash()` | REQUIRED | Return the hash of the most recent receipt for chain linkage. |

### §4.2 — Ed25519 Signing

| Operation | Status | Description |
|-----------|--------|-------------|
| `mus.generateKeypair()` | REQUIRED | Generate a new Ed25519 keypair for signing. |
| `mus.signPayload(payload, privateKey)` | REQUIRED | Sign a canonical JSON payload with an Ed25519 private key. |
| `mus.verifySignature(payload, signature, publicKey)` | REQUIRED | Verify an Ed25519 signature against a payload and public key. |

### §4.3 — Export

| Operation | Status | Description |
|-----------|--------|-------------|
| `mus.extractProtocolReceipt(internalReceipt)` | REQUIRED | Convert an internal receipt to the protocol-standard format. |
| `mus.buildChainedLedger(entries)` | REQUIRED | Build a hash-chained ledger from a sequence of entries. |
| `mus.exportReceiptBundle(receiptIds)` | OPTIONAL | Export a set of receipts as a verifiable bundle with chain proof. |

---

## §5 — Namespace: `ledger.*`

**Responsibility:** Append-only hash chain storage and verification.

| Operation | Status | Description |
|-----------|--------|-------------|
| `ledger.appendLedger(entryType, payload)` | REQUIRED | Append a new entry to the ledger. Computes SHA-256 hash of content, links to previous entry's hash. Returns the new entry with hash. |
| `ledger.getLastLedgerEntry()` | REQUIRED | Return the most recent ledger entry (for chain linkage). |
| `ledger.getAllLedgerEntries()` | REQUIRED | Return the complete ledger for verification. |
| `ledger.getLedgerEntriesSince(timestamp)` | OPTIONAL | Return ledger entries after a given timestamp (for incremental sync). |
| `ledger.verifyHashChain()` | REQUIRED | Verify the entire ledger hash chain. Recompute each entry's hash and verify prevHash linkage. Returns pass/fail with first broken link if failed. |

---

## §6 — Namespace: `mantis.*`

**Responsibility:** Learning engine, coherence checking, advisory risk scoring.

**Behavioral constraint:** Learning is strictly advisory. MANTIS must never approve, execute, or bypass governance. Learning improves support. It does not create permission.

| Operation | Status | Description |
|-----------|--------|-------------|
| `mantis.recordDecision(decisionEvent)` | REQUIRED | Record a governance decision (approval, rejection, execution outcome) as a learning event. |
| `mantis.getAdvisoryRiskScore(actionSignature)` | REQUIRED | Return an advisory risk score based on historical patterns. This score informs but does not determine governance decisions. |
| `mantis.getLearningSummary(timeWindow)` | REQUIRED | Return a summary of learning events within a time window. |
| `mantis.runCoherenceCheck()` | REQUIRED | Verify internal consistency of the learning model against the governance state. |
| `mantis.getCoherenceState()` | REQUIRED | Return the current coherence state (aligned, drifting, inconsistent). |
| `mantis.runLearningLoopAnalysis(recentEvents)` | OPTIONAL | Perform deep analysis of recent events to identify patterns, risks, or recommendations. |

---

## §7 — Cross-Cutting Concerns

### §7.1 — Fail-Closed Default

Every system call that participates in the governance pipeline must fail closed. If a call throws an exception, returns an unexpected result, or times out, the governed action must be blocked. No partial execution is permitted.

### §7.2 — Canonical JSON

All hashing operations use canonical JSON: keys sorted alphabetically, no whitespace, no undefined values. This ensures deterministic hash computation across implementations.

### §7.3 — Timestamp Convention

All timestamps are UTC-based Unix timestamps in milliseconds. Implementations must not use local time or string-based timestamps in protocol-level operations.

### §7.4 — Hash Algorithm

SHA-256 is the canonical hash algorithm for all protocol operations (receipt hashes, ledger chain, args hashes, policy hashes). Ed25519 is the canonical signature algorithm.

---

## §8 — Implementation Mapping

The following table maps each namespace to its implementation status in the reference implementation (rio-proxy).

| Namespace | Operations Specified | Implemented | Partial | Not Implemented |
|-----------|---------------------|-------------|---------|-----------------|
| `rio.*` | 19 | 19 | 0 | 0 |
| `sentinel.*` | 8 | 8 | 0 | 0 |
| `mus.*` | 8 | 8 | 0 | 0 |
| `ledger.*` | 5 | 5 | 0 | 0 |
| `mantis.*` | 6 | 6 | 0 | 0 |
| **Total** | **46** | **46** | **0** | **0** |

All 46 specified operations have corresponding implementations in the reference implementation. This does not imply production readiness — it indicates interface coverage.

---

## §9 — Conformance Requirements

An implementation conforms to this syscall specification when:

1. All REQUIRED operations are implemented and callable.
2. All operations respect the fail-closed default (§7.1).
3. All hashing uses canonical JSON (§7.2) and SHA-256 (§7.4).
4. Sentinel operations do not execute, commit, or modify runtime state.
5. MANTIS operations do not approve, execute, or bypass governance.
6. Authorization tokens follow the full lifecycle: issue → validate → burn.
7. Ledger operations maintain append-only integrity with hash chain linkage.
