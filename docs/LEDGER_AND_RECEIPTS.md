# Ledger and Receipts

**RIO — Cryptographic Audit System**

---

## Overview

The RIO audit system is built on two complementary structures: **receipts** and the **ledger**. Receipts are individual cryptographic proofs of decisions. The ledger is an ordered, hash-linked chain of entries that references those receipts. Together, they provide immutability, ordering, non-repudiation, and tamper detection without requiring distributed consensus or a blockchain network.

Every pipeline outcome — whether the action was executed, denied, blocked by the kill switch, or resulted in a governance change — produces both a receipt and a ledger entry. There are no silent failures and no unrecorded decisions.

---

## Receipts

A receipt is a signed, self-contained proof that a specific decision was made about a specific request at a specific time.

### Receipt Structure

| Field | Type | Description |
|-------|------|-------------|
| `receipt_id` | UUID | Unique identifier for this receipt |
| `request_id` | UUID | Reference to the original request |
| `intent_hash` | SHA-256 hex | Hash of the canonical intent object |
| `decision_hash` | SHA-256 hex | Hash of the policy decision and risk assessment |
| `execution_hash` | SHA-256 hex | Hash of the execution result (or denial/block reason) |
| `policy_decision` | String | ALLOW, DENY, ESCALATE, or KILL_SWITCH |
| `risk_level` | String | LOW, MEDIUM, HIGH, or GOVERNANCE |
| `action_type` | String | The classified action type |
| `actor_id` | String | The user who initiated the request |
| `timestamp` | ISO 8601 | When the receipt was generated |
| `signature` | Base64 | ECDSA-secp256k1 signature over the receipt content |

### How Receipts Are Generated

The receipt generator (`runtime/receipt.py`) follows this process:

1. **Collect hashes.** The intent hash, decision hash, and execution hash are computed by taking the SHA-256 digest of the minified, sorted JSON representation of each object.

2. **Build the receipt body.** All fields are assembled into a canonical JSON structure.

3. **Sign the receipt.** The receipt body is serialized to minified sorted JSON, and the resulting bytes are signed using the system's RSA-2048 private key with PKCS1v15 padding and SHA-256 hashing.

4. **Persist the receipt.** The signed receipt is appended to `runtime/data/receipts.jsonl`.

### Receipt Verification

To verify a receipt:

1. Load the system's public key from `runtime/keys/public_key.pem`.
2. Reconstruct the receipt body (all fields except the signature).
3. Serialize to minified sorted JSON.
4. Verify the ECDSA signature against the serialized bytes using the public key.

If the signature is valid, the receipt has not been altered since it was generated. If any field has been modified — even a single character — the signature verification fails.

---

## The Ledger

The ledger is an append-only, hash-linked chain of entries stored in `runtime/data/ledger.jsonl`. Each line in the file is a single JSON object representing one ledger entry.

### Ledger Entry Structure

| Field | Type | Description |
|-------|------|-------------|
| `entry_id` | UUID | Unique identifier for this entry |
| `receipt_id` | UUID | Reference to the associated receipt |
| `content_hash` | SHA-256 hex | Hash of this entry's own content |
| `previous_hash` | SHA-256 hex | Hash of the previous entry (or `"GENESIS"` for the first) |
| `timestamp` | ISO 8601 | When the entry was appended |
| `event_type` | String | EXECUTION, DENIAL, KILL_SWITCH, GOVERNANCE_CHANGE |
| `actor_id` | String | The user who initiated the action |
| `reason` | String | Human-readable description of the event |

### Hash Chain

The hash chain is the mechanism that makes the ledger tamper-evident. Each entry's `content_hash` is computed from the entry's own fields. Each entry's `previous_hash` is the `content_hash` of the entry that came before it. The first entry in the ledger uses the string `"GENESIS"` as its previous hash.

```
Entry 1                Entry 2                Entry 3
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ content_hash │◀─────│ previous_hash│      │              │
│ prev: GENESIS│      │ content_hash │◀─────│ previous_hash│
│ receipt: R1  │      │ receipt: R2  │      │ content_hash │
└──────────────┘      └──────────────┘      │ receipt: R3  │
                                            └──────────────┘
```

This chain has three properties:

**Tamper detection.** If any entry is modified, its content hash changes, which breaks the `previous_hash` reference in the next entry. The break propagates through the entire chain from that point forward.

**Deletion detection.** If any entry is removed, the chain breaks at the gap. The entry after the deleted one will have a `previous_hash` that does not match any remaining entry's `content_hash`.

**Ordering.** The chain enforces a strict total order on all entries. There is no ambiguity about which event came first.

### Ledger Verification

The verification system (`runtime/verify_ledger.py`) validates the ledger by:

1. Reading every entry in order from `runtime/data/ledger.jsonl`.
2. Recomputing each entry's content hash from its fields.
3. Verifying that each entry's `previous_hash` matches the `content_hash` of the preceding entry.
4. Verifying that the first entry's `previous_hash` is `"GENESIS"`.
5. Optionally verifying the receipt signature for each referenced receipt.

The verification tool reports any broken links, tampered entries, or missing receipts.

---

## Governance Ledger

Policy and risk model changes are recorded through the governance ledger (`runtime/governance/governance_ledger.py`). When a policy version is activated, rolled back, or a risk model is updated, the governance ledger creates a receipt and ledger entry with event type `GOVERNANCE_CHANGE`.

Governance ledger entries include additional metadata:

| Field | Description |
|-------|-------------|
| `change_type` | GOVERNANCE_POLICY_ACTIVATE, GOVERNANCE_POLICY_ROLLBACK, GOVERNANCE_RISK_MODEL_ACTIVATE, etc. |
| `old_version` | The version being replaced |
| `new_version` | The version being activated |
| `proposed_by` | Who proposed the change |
| `approved_by` | Who approved the change |

This ensures that the audit trail covers not only action execution but also the evolution of the rules that govern those actions.

---

## What the Audit System Proves

The combination of receipts and the ledger provides the following guarantees:

| Guarantee | How It Is Achieved |
|-----------|-------------------|
| **Non-repudiation** | Receipts are signed with the system's private key. The signature proves the system generated the receipt. |
| **Integrity** | Receipt signatures detect any modification to receipt content. Ledger hash chain detects any modification to ledger entries. |
| **Completeness** | Protocol invariants INV-02 and INV-03 ensure every request produces a receipt and every receipt produces a ledger entry. |
| **Ordering** | The hash chain enforces a strict total order on all events. |
| **Tamper evidence** | Any modification, insertion, or deletion of ledger entries breaks the hash chain. |
| **Auditability** | The full decision context — intent, policy, risk, authorization, execution, receipt, ledger — is preserved for every request. |

---

## Cryptographic Parameters

| Parameter | Value |
|-----------|-------|
| Receipt signing key | RSA-2048 |
| Signing algorithm | PKCS1v15 with SHA-256 |
| Hash algorithm | SHA-256 |
| Canonicalization | Minified sorted JSON |
| Key storage | `runtime/keys/private_key.pem` (private), `runtime/keys/public_key.pem` (public) |
| Ledger storage | `runtime/data/ledger.jsonl` (append-only JSONL) |
| Receipt storage | `runtime/data/receipts.jsonl` (append-only JSONL) |

---

## References

| Specification | Location |
|--------------|----------|
| Receipt Protocol | `spec/receipt_protocol.md` |
| Receipt Specification | `spec/receipt_spec.md` |
| Audit Ledger Protocol | `spec/audit_ledger_protocol.md` |
| Ledger Interoperability | `spec/ledger_interoperability.md` |
| Verification Model | `spec/verification_model.md` |
| Receipt JSON Schema | `schemas/receipt.json` |
