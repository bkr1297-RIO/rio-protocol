# Receipt Protocol

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Data Structure / Protocol Stage

---

## Overview

The Receipt Protocol defines the structure, generation rules, and verification procedures for cryptographic receipts produced by Stage 7 (Receipt / Attestation) of the Governed Execution Protocol. A receipt is generated for every request that enters the protocol, regardless of outcome — approved, denied, escalated, or blocked by the kill switch. Receipts form a hash chain that provides tamper-evident auditability across the full decision history.

---

## Receipt Structure

Every receipt contains the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_id` | string (UUID v4) | Yes | Unique identifier for this receipt |
| `request_id` | string (UUID v4) | Yes | Reference to the original request registered at Stage 1 (Intake) |
| `canonical_intent_id` | string (UUID v4) | Yes | Reference to the canonical intent produced at Stage 3 (Structured Intent) |
| `authorization_id` | string (UUID v4) | Yes | Reference to the authorization token produced at Stage 5 (Authorization). For denied requests, this references the denial record |
| `decision` | string (enum) | Yes | Final outcome: `ALLOW` (execution proceeded) or `DENY` (execution blocked) |
| `execution_status` | string (enum) | Yes | Execution result: `completed` (action succeeded), `failed` (action attempted but failed), `blocked` (action never attempted), `denied` (authorization denied) |
| `timestamps` | object | Yes | Contains `intake_timestamp`, `authorization_timestamp`, `execution_timestamp`, and `receipt_timestamp` — all UTC Unix milliseconds |
| `result_hash` | string | Yes | SHA-256 hash of the execution result payload (or the denial/block record for non-executed requests) |
| `signature` | string | Yes | ECDSA-secp256k1 signature over the canonical JSON representation of this receipt (excluding the `signature` and `receipt_hash` fields) |
| `receipt_hash` | string | Yes | SHA-256 hash of the canonical JSON representation of this receipt (excluding the `receipt_hash` field itself). Used as the content identifier for this receipt |
| `previous_receipt_hash` | string | Yes | SHA-256 hash of the immediately preceding receipt. For the genesis receipt, this value is a defined constant (`0x0000...0000`, 64 hex characters). This field forms the hash chain |

---

## Hash Chain

Receipts form a hash chain where each receipt references the hash of the immediately preceding receipt through the `previous_receipt_hash` field. This chain provides the following properties:

**Ordering.** The hash chain establishes a total order over all receipts. Any receipt can be verified to have been generated after its predecessor by checking the hash reference.

**Tamper evidence.** Any modification to a historical receipt changes its `receipt_hash`, which breaks the `previous_receipt_hash` reference in the next receipt. An auditor can detect tampering by recomputing hashes from the genesis receipt forward.

**Completeness.** A gap in the hash chain (a receipt whose `previous_receipt_hash` does not match any known receipt's `receipt_hash`) indicates a missing or deleted entry.

**Genesis receipt.** The first receipt in the chain uses a defined constant (`0x0000...0000`, 64 hex characters) as its `previous_receipt_hash`. This is the only receipt permitted to use this value.

---

## Generation Rules

1. A receipt is generated for every request that reaches Stage 7, regardless of the decision outcome.
2. The receipt is generated after execution completes (for `ALLOW` decisions) or after the denial/block is recorded (for `DENY` decisions).
3. All required fields must be populated. A receipt with missing fields is invalid.
4. The `receipt_hash` is computed over the canonical (minified, sorted) JSON representation of the receipt, excluding the `receipt_hash` field itself.
5. The `signature` is computed over the canonical JSON representation excluding both the `signature` and `receipt_hash` fields.
6. The `previous_receipt_hash` must reference the most recently generated receipt. The Receipt Service maintains a pointer to the current chain head.
7. Receipt generation must be atomic — either a complete, valid receipt is produced or no receipt is produced. Partial receipts are not permitted.
8. If receipt generation fails, the system must halt and record the failure. A missing receipt constitutes a protocol integrity violation (INV-02).

---

## Verification Procedure

An auditor verifies a receipt by performing the following steps:

1. Obtain the receipt record.
2. Reconstruct the canonical JSON representation (minified, sorted) excluding the `signature` and `receipt_hash` fields.
3. Verify the `signature` using the Receipt Service's public key (obtained from the key registry, not from the receipt itself).
4. Recompute the `receipt_hash` from the canonical JSON (excluding `receipt_hash`) and verify it matches the stored value.
5. Verify that `previous_receipt_hash` matches the `receipt_hash` of the immediately preceding receipt in the chain.
6. Verify that all timestamps are chronologically ordered (`intake_timestamp` <= `authorization_timestamp` <= `execution_timestamp` <= `receipt_timestamp`).
7. Verify that the `canonical_intent_id` references a valid canonical intent and that the `authorization_id` references a valid authorization record.

If any verification step fails, the receipt is considered invalid and the integrity of the decision chain from that point forward is suspect.

---

## Relationship to Existing Specifications

| Document | Relationship |
|----------|-------------|
| `/spec/receipt_spec.md` | Defines canonical receipt fields and verification procedures for the original 15-protocol stack |
| `/spec/receipt_schema.json` | Machine-readable JSON Schema for the receipt structure |
| `/spec/08_attestation.md` | Attestation protocol specification (Protocol 08 in the 15-protocol stack) |
| `/spec/governed_execution_protocol.md` | Stage 7 definition in the 8-step runtime protocol |

---

## Related Invariants

| Invariant | Relevance |
|-----------|-----------|
| INV-02 | Every governed action must produce a signed receipt |
| INV-03 | Every receipt must be recorded in the audit ledger |
| INV-04 | Ledger entries (and receipts) form a hash chain; no gaps permitted |
