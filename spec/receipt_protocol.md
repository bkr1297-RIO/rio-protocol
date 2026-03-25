# Receipt / Attestation Protocol

**Version:** 2.0.0
**Status:** Core Specification
**Category:** Protocol Stage (Stage 7)

---

## 1. Purpose

The Receipt Protocol defines how the system generates a cryptographic receipt for every authorization decision and execution outcome.

Receipts serve as:

- **Proof of what was requested.** The receipt contains the canonical intent hash, linking the receipt to the original structured request.
- **Proof of what was decided.** The receipt records the authorization decision (ALLOW, DENY, ESCALATE, or BLOCKED) and the identity of the authorizer.
- **Proof of what was executed or denied.** The receipt records the execution status and a hash of the execution result, providing a tamper-evident record of the outcome.
- **Input records for the audit ledger.** Receipts are the atomic unit of the append-only audit ledger. The ledger stores receipts, not raw logs.
- **Input records for the governed corpus and learning system.** The Governed Corpus derives its structured decision history from receipts and their associated execution outcomes.

Every governed request must produce a receipt, whether the action is allowed, denied, or blocked. There are no exceptions. A request that does not produce a receipt is a protocol violation.

This enforces:

- **INV-02:** Every execution must produce a receipt.
- **INV-03:** Every receipt must be written to the ledger.

---

## 2. Receipt Structure

Each receipt must contain the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `receipt_id` | string (UUID) | Unique receipt identifier |
| `request_id` | string (UUID) | Intake request ID |
| `intent_id` | string (UUID) | Canonical intent ID |
| `authorization_id` | string (UUID) | Authorization decision ID |
| `decision` | string (enum) | ALLOW / DENY / ESCALATE / BLOCKED |
| `action_type` | string | Action requested |
| `execution_status` | string (enum) | `executed` / `denied` / `blocked` / `failed` |
| `risk_score` | number | Risk score at decision time |
| `policy_ids` | array of strings | Policies applied during evaluation |
| `timestamps` | object | Contains `intake_time`, `authorization_time`, `execution_time` (all ISO 8601) |
| `result_hash` | string (SHA-256) | Hash of execution result (or null hash if not executed) |
| `previous_receipt_hash` | string (SHA-256) | Hash of previous ledger receipt (genesis receipt uses null hash) |
| `receipt_hash` | string (SHA-256) | Hash of this receipt |
| `signature` | string (ECDSA-secp256k1) | Cryptographic signature of the Receipt Service |

All fields are required. If a field is not applicable (e.g., `authorization_id` for a kill-switch-blocked request), the field must contain a null sentinel value, not be omitted.

---

## 3. Receipt Types

The system must generate receipts for every governed action. The receipt type is determined by the outcome:

| Receipt Type | When Generated | `decision` Value | `execution_status` Value |
|--------------|----------------|------------------|--------------------------|
| Allow Receipt | Action approved and executed successfully | ALLOW | `executed` |
| Denial Receipt | Action denied by policy or authorization | DENY | `denied` |
| Blocked Receipt | Execution blocked by gate or kill switch | BLOCKED | `blocked` |
| Failure Receipt | Execution attempted but failed | ALLOW | `failed` |
| Kill Switch Event Receipt | EKS-0 engaged or disengaged | BLOCKED | `blocked` |

Every receipt type follows the same structure and signing process. There is no distinction in how different receipt types are stored or verified — the `decision` and `execution_status` fields encode the outcome.

---

## 4. Hash Chain Requirement

Receipts must be linked using a hash chain:

```
receipt_hash = SHA-256(canonical_json(receipt_data) + previous_receipt_hash)
```

The `canonical_json` function produces a deterministic JSON serialization (sorted keys, no whitespace, UTF-8 encoding) of all receipt fields except `receipt_hash` and `signature`. The `previous_receipt_hash` is the `receipt_hash` of the immediately preceding receipt in the ledger.

This ensures:

- **Ledger entries cannot be modified.** Changing any field in a receipt changes its hash, which breaks the chain for all subsequent entries.
- **Tampering is detectable.** An auditor can recompute all hashes from the genesis receipt forward and verify that each `previous_receipt_hash` matches.
- **Full execution history is verifiable.** The hash chain provides a total ordering of all governed actions and makes deletion or reordering detectable.

The genesis receipt (the first receipt in the ledger) uses a null hash (`0x0000...0000`, 64 hex zeros) as its `previous_receipt_hash`.

This supports invariant:

- **INV-04:** Ledger is append-only.

---

## 5. Signing Requirement

Each receipt must be cryptographically signed by the Receipt Service using ECDSA-secp256k1.

The signature is computed over the `receipt_hash`:

```
signature = ECDSA_SIGN(receipt_service_private_key, receipt_hash)
```

The signature attests that:

- **The protocol executed correctly.** The Receipt Service only signs receipts that were generated through the full protocol flow.
- **The decision and execution data are authentic.** The signature binds the Receipt Service's identity to the receipt content.
- **The receipt can be independently verified.** Any party with access to the Receipt Service's public key (from the key registry) can verify the signature without trusting any runtime component.

The Receipt Service's public key is published in the key registry and is subject to the key rotation and revocation procedures defined in the identity and credentials specification.

---

## 6. Relationship to Ledger

Receipts are the atomic unit of the Audit Ledger. The ledger does not store raw logs, intermediate state, or unstructured data. Every ledger entry is a signed, hash-linked receipt.

The flow is:

```
Execution → Receipt Generated → Receipt Signed → Receipt Written to Ledger
```

A receipt that is generated but not written to the ledger is a protocol violation (INV-03). The Receipt Service must confirm ledger write acknowledgment before considering the receipt finalized. If the ledger write fails, the Receipt Service must retry until the write succeeds or escalate to the kill switch if the ledger is unavailable.

---

## 7. Relationship to Governed Corpus

The Governed Corpus stores structured decision history derived from receipts and execution outcomes. The corpus is used for:

- **Audit.** Reconstructing the full decision chain for any governed action.
- **Risk modeling.** Analyzing patterns in risk scores, outcomes, and failure rates.
- **Policy tuning.** Identifying policies that produce excessive false positives or false negatives.
- **Governance learning.** Training updated risk and classification models on historical decision data.

Receipts are the ground-truth record. The Governed Corpus may enrich receipt data with additional context (e.g., eventual outcomes, post-execution observations), but the receipt itself is immutable and serves as the authoritative record of what was decided and executed at runtime.

---

## 8. Security Properties

The Receipt Protocol ensures four fundamental security properties:

**Non-repudiation.** No party can deny that an action occurred. The receipt contains the canonical intent, the authorization decision, and the execution result, all signed by the Receipt Service and linked to the authorizer's identity.

**Integrity.** A receipt cannot be modified after generation. The hash chain and cryptographic signature make any modification detectable. Changing a single bit in any receipt field invalidates the receipt hash, breaks the chain, and invalidates the signature.

**Traceability.** Every action is linked to its authorization. The receipt contains the `authorization_id`, which links to the signed authorization token, which links to the authorizer's identity. The full chain from request to execution to authorization to identity is reconstructable.

**Auditability.** Independent verification is possible without trusting any runtime component. An auditor needs only the ledger contents and the Receipt Service's public key to verify every receipt in the system.

---

## References

| Document | Path |
|----------|------|
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Audit Ledger Protocol | `/spec/audit_ledger_protocol.md` |
| Receipt JSON Schema | `/spec/receipt_schema.json` |
| Ledger Entry JSON Schema | `/spec/ledger_entry_schema.json` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
| Governed Corpus | `/spec/governed_corpus.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
