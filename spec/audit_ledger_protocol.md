# Audit Ledger Protocol

**Version:** 2.0.0
**Status:** Core Specification
**Category:** Protocol Stage (Stage 8)

---

## 1. Purpose

The Audit Ledger Protocol defines how receipts are stored in an immutable, append-only ledger to provide a permanent, verifiable history of all governed decisions and actions.

The ledger ensures:

- **Every decision is recorded.** Whether a request is approved, denied, escalated, or blocked, the resulting receipt is written to the ledger.
- **Every execution is recorded.** Successful executions produce receipts that are appended to the ledger with the execution result hash.
- **Every denial is recorded.** Denied requests produce denial receipts that are appended to the ledger with the same structure and signing as execution receipts.
- **History cannot be altered.** The ledger is append-only. No update, delete, reorder, or overwrite operation is permitted on any existing entry.
- **The system can be audited and verified.** Any party with read access to the ledger and the Receipt Service's public key can independently verify the integrity of the entire decision history.

This enforces:

- **INV-03:** Every receipt must be written to the ledger.
- **INV-04:** Ledger is append-only.

---

## 2. Ledger Model

The ledger is an append-only sequence of receipt records. Each ledger entry wraps a receipt and links to the previous entry by hash, forming a tamper-evident chain.

Each ledger entry contains:

| Field | Type | Description |
|-------|------|-------------|
| `ledger_entry_id` | string (UUID) | Unique identifier for this ledger entry |
| `receipt_id` | string (UUID) | Reference to the receipt recorded by this entry |
| `receipt_hash` | string (SHA-256) | Hash of the referenced receipt's canonical JSON representation |
| `previous_receipt_hash` | string (SHA-256) | Hash of the immediately preceding ledger entry (genesis uses null hash) |
| `timestamp` | string (ISO 8601) | Time this entry was appended |
| `entry_hash` | string (SHA-256) | Hash of this ledger entry |

Entries are linked using a hash chain:

```
entry_hash = SHA-256(receipt_hash + previous_receipt_hash + timestamp)
```

This creates a tamper-evident chain of records. Any modification to a historical entry changes its `entry_hash`, which breaks the `previous_receipt_hash` reference in the next entry and all subsequent entries. The genesis entry (the first entry in the ledger) uses a null hash (`0x0000...0000`, 64 hex characters) as its `previous_receipt_hash`.

---

## 3. Append-Only Rule

The ledger must enforce the following rules:

- **No update operations.** Once an entry is appended, no field in that entry can be modified.
- **No delete operations.** No entry can be removed from the ledger, regardless of the reason.
- **Only append operations are allowed.** The Ledger Service exposes a single write operation (`append`) and no modification operations.
- **Any attempt to modify an existing entry must be rejected and logged.** Modification attempts are treated as security events and recorded in the system's operational log.

These rules are enforced at the API level (the Ledger Service does not implement update or delete endpoints), at the storage level (the underlying storage is configured for append-only writes), and at the protocol level (INV-04 requires an unbroken hash chain). This ensures ledger integrity and auditability.

---

## 4. Ledger Entry Types

The ledger must store entries for all governed actions and system events:

| Entry Type | Description |
|------------|-------------|
| Execution | Allowed and executed action |
| Denial | Denied action (by policy or authorization) |
| Blocked | Blocked by execution gate or kill switch |
| Failure | Execution attempted but failed |
| Kill Switch Event | EKS-0 engaged or disengaged |
| Governance Change | Policy or risk model update deployed through governed change process |

All entry types use the same ledger entry structure and hash chain mechanism. The entry type is determined by the `decision` and `execution_status` fields in the referenced receipt.

---

## 5. Verification

Ledger integrity must be verifiable by any party with read access to the ledger and the Receipt Service's public key. Verification does not require trust in any runtime component.

The following verification procedures are supported:

**Recomputing the hash chain.** An auditor recomputes all `entry_hash` values from the genesis entry forward using the formula `SHA-256(receipt_hash + previous_receipt_hash + timestamp)` and verifies that each computed hash matches the stored `entry_hash`. Any mismatch indicates tampering, deletion, or reordering.

**Verifying receipt signatures.** For each ledger entry, the auditor retrieves the referenced receipt and verifies its ECDSA-secp256k1 signature using the Receipt Service's public key from the key registry.

**Checking invariant compliance.** The auditor verifies that every receipt in the system has a corresponding ledger entry (INV-03) and that the hash chain is unbroken from genesis to the current head (INV-04).

**Comparing ledger entries with receipts.** The auditor verifies that the `receipt_hash` in each ledger entry matches the SHA-256 hash of the referenced receipt's canonical JSON representation.

If any hash mismatch occurs, the ledger is considered compromised. The auditor must report the specific entry where the chain breaks and the nature of the inconsistency.

---

## 6. Relationship to Receipt Protocol

Receipts are written to the ledger after signing. The Receipt Service generates and signs the receipt, then passes it to the Ledger Service for append.

The flow is:

```
Execution → Receipt Generated → Receipt Signed → Ledger Append → Ledger Hash Updated
```

The ledger does not generate receipts; it only stores them. The separation of receipt generation (Stage 7) from ledger storage (Stage 8) ensures that the Receipt Service and Ledger Service can be independently verified and that neither component has unilateral control over the decision record.

If the Ledger Service cannot append an entry (storage failure, hash computation failure), the protocol pipeline halts. No further executions proceed until the ledger is restored to a consistent state. A failed ledger append is treated as a system integrity failure, not a recoverable error.

---

## 7. Relationship to Audit and Governance Learning

The ledger serves as the source of truth for:

- **Audit investigations.** Auditors query the ledger to reconstruct the full decision chain for any governed action — from request to classification to policy evaluation to authorization to execution to receipt.
- **Compliance reporting.** Compliance officers use ledger data to demonstrate that all actions followed the governed execution protocol and that no unauthorized executions occurred.
- **Forensic reconstruction.** In the event of an incident, investigators use the ledger to reconstruct exactly what happened, when, and who authorized it.
- **Governance learning data.** The Learning Plane reads from the Governed Corpus, which derives its structured decision history from ledger entries and their associated receipts.
- **Risk model training.** Historical ledger data provides the training set for updated risk scoring models.
- **Policy tuning.** Patterns in ledger data (excessive denials, false positives, missed risks) inform policy refinements.

---

## 8. Security Properties

The Audit Ledger provides the following security properties:

**Immutability.** Once an entry is appended, it cannot be modified or deleted. The append-only rule is enforced at the API, storage, and protocol levels.

**Tamper evidence.** The hash chain makes any modification to historical entries detectable. Changing a single bit in any entry invalidates the hash chain from that point forward.

**Full history.** Every governed action — approved, denied, blocked, or failed — produces a ledger entry. There are no gaps in the record.

**Traceability.** Every ledger entry links to a receipt, which links to a canonical intent, which links to an authorization decision, which links to an authorizer identity. The full chain is reconstructable.

**Independent verification.** Any party with read access to the ledger and the Receipt Service's public key can verify the entire decision history without trusting any runtime component.

**Forensic reconstruction capability.** The ledger provides sufficient data to reconstruct the complete sequence of events for any governed action, including timing, decisions, and outcomes.

---

## 9. Forensic Reconstruction

Using the ledger, an auditor must be able to reconstruct the following for any governed action:

| Question | Source |
|----------|--------|
| What was requested? | Canonical intent (via receipt's `intent_id`) |
| How was it classified? | Risk category and action type (via canonical intent) |
| What policies were applied? | Policy IDs (via receipt's `policy_ids`) |
| Who authorized it? | Authorizer identity (via receipt's `authorization_id`) |
| What was executed? | Execution result (via receipt's `result_hash` and `execution_status`) |
| What was the result? | Execution outcome (via receipt's `decision` and `execution_status`) |
| When did it happen? | Timestamps (via receipt's `timestamps` and ledger entry's `timestamp`) |

The ledger is the authoritative history of system behavior. If a dispute arises about what the system did, the ledger record is definitive. No runtime log, operational metric, or external record supersedes the ledger.

---

## References

| Document | Path |
|----------|------|
| Receipt / Attestation Protocol | `/spec/receipt_protocol.md` |
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Ledger Entry JSON Schema | `/spec/ledger_entry_schema.json` |
| Receipt JSON Schema | `/spec/receipt_schema.json` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| Governed Corpus | `/spec/governed_corpus.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
| Ledger Interoperability | `/spec/ledger_interoperability.md` |
