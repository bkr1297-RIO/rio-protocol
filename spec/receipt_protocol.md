# Receipt / Attestation Protocol

**Version:** 3.0.0
**Status:** Core Specification
**Category:** Protocol Stage (Stage 7)

---

## 1. Purpose

The Receipt Protocol defines how the system generates a cryptographic receipt for every authorization decision and execution outcome.

Receipts serve as:

- **Proof of what was requested.** The receipt contains the request hash and canonical payload, linking the receipt to the original request.
- **Proof of what was decided.** The receipt records the decision (`allow` or `block`), invariant results, and threshold results.
- **Proof of what was evaluated.** The receipt records the model output hash and preview, providing a tamper-evident record of the evaluation.
- **Input records for the audit ledger.** Receipts are the atomic unit of the append-only audit ledger.
- **Input records for the governed corpus and learning system.** The Governed Corpus derives its structured decision history from receipts.

Every governed request must produce a receipt, whether the action is allowed or blocked. There are no exceptions. A request that does not produce a receipt is a protocol violation.

This enforces:

- **INV-02:** Every execution must produce a receipt.
- **INV-03:** Every receipt must be written to the ledger.

---

## 2. Receipt Structure

The canonical receipt schema is defined in `spec/receipt_schema.json`. Each receipt contains exactly 22 fields:

| Field | Type | Description |
|-------|------|-------------|
| `receipt_version` | string | Protocol version (e.g., "1.0") |
| `receipt_id` | string (UUID) | Unique receipt identifier |
| `timestamp` | string (ISO 8601) | Timestamp with microsecond precision and UTC (Z suffix) |
| `runtime_id` | string | Identifier of the runtime that produced this receipt |
| `runtime_version` | string | Version of the runtime |
| `environment` | string | Execution environment (test, staging, production) |
| `request_summary` | string | Human-readable summary of the original request |
| `request_hash` | string (SHA-256) | Hash of the canonical request payload |
| `request_canonical_payload` | object | Canonical representation of the original request |
| `policy_bundle_id` | string | Identifier of the policy bundle used for evaluation |
| `policy_bundle_hash` | string (SHA-256) | Hash of the policy bundle |
| `decision` | string (enum) | `allow` or `block` |
| `decision_reason_codes` | array of strings | Machine-readable codes explaining the decision |
| `invariant_results` | object | Results of invariant checks |
| `threshold_results` | object | Results of threshold evaluations |
| `model_output_hash` | string (SHA-256) | Hash of the model output |
| `model_output_preview` | string | Truncated preview of the model output |
| `prev_ledger_hash` | string (SHA-256) | Hash of the previous ledger entry |
| `public_key_fingerprint` | string (SHA-256) | Fingerprint of the Ed25519 signing key |
| `receipt_hash` | string (SHA-256) | Hash of the canonical JSON of all signed fields |
| `signature_algorithm` | string | Always `Ed25519` |
| `signature` | string (base64) | Ed25519 signature over the canonical JSON |

All fields are required. No additional fields are permitted.

---

## 3. Receipt Types

The system must generate receipts for every governed action. The receipt type is determined by the `decision` field:

| Decision | When Generated |
|----------|----------------|
| `allow` | Action approved and executed |
| `block` | Action denied by policy, invariant failure, or kill switch |

Every receipt type follows the same structure and signing process.

---

## 4. Hash Chain Requirement

### receipt_hash

The `receipt_hash` is computed over the **signed fields** — all receipt fields except `receipt_hash`, `signature`, and `signature_algorithm`:

```
signed_fields = {all fields} - {receipt_hash, signature, signature_algorithm}
canonical_json = JSON.stringify(signed_fields, sort_keys=True, separators=(',', ':'))
receipt_hash = SHA-256(canonical_json)
```

The `receipt_hash` covers the full signed payload. It is the integrity root for the receipt.

### Ledger chain

Receipts are linked into a tamper-evident ledger chain:

```
ledger_hash = SHA-256(prev_ledger_hash + receipt_hash)
```

Where `+` is string concatenation of the two hex-encoded hashes.

### Genesis

The genesis entry uses `SHA-256("GENESIS")` as its `prev_ledger_hash`:

```
SHA-256("GENESIS") = 901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a
```

This ensures:

- **Ledger entries cannot be modified.** Changing any field in a receipt changes its hash, which breaks the chain for all subsequent entries.
- **Tampering is detectable.** An auditor can recompute all hashes from genesis forward.
- **Full execution history is verifiable.** The hash chain provides a total ordering of all governed actions.

This supports invariant:

- **INV-04:** Ledger is append-only.

---

## 5. Signing Requirement

Each receipt must be cryptographically signed using **Ed25519**.

The signature is computed over the canonical JSON of the signed fields (the same bytes used to compute `receipt_hash`):

```
signature = Ed25519_SIGN(private_key, canonical_json)
```

The signature attests that:

- **The protocol executed correctly.** The signing service only signs receipts generated through the full protocol flow.
- **The decision and execution data are authentic.** The signature binds the signing key's identity to the receipt content.
- **The receipt can be independently verified.** Any party with the Ed25519 public key can verify the signature.

The public key is published in PEM format (SPKI-encoded). The raw 32-byte Ed25519 key is the last 32 bytes of the DER-decoded payload.

See `spec/SIGNING_ALGORITHMS.md` for the full signing architecture.

---

## 6. Relationship to Ledger

Receipts are the atomic unit of the Audit Ledger. The ledger does not store raw logs, intermediate state, or unstructured data. Every ledger entry is a signed, hash-linked receipt.

The flow is:

```
Execution → Receipt Generated → Receipt Signed → Receipt Written to Ledger
```

A receipt that is generated but not written to the ledger is a protocol violation (INV-03).

---

## 7. Relationship to Governed Corpus

The Governed Corpus stores structured decision history derived from receipts and execution outcomes. Receipts are the ground-truth record. The Governed Corpus may enrich receipt data with additional context, but the receipt itself is immutable and serves as the authoritative record.

---

## 8. Security Properties

The Receipt Protocol ensures four fundamental security properties:

**Non-repudiation.** No party can deny that an action occurred. The receipt contains the request hash, the decision, and the evaluation results, all signed and linked to the signing key.

**Integrity.** A receipt cannot be modified after generation. The hash chain and cryptographic signature make any modification detectable.

**Traceability.** Every action is linked to its request via `request_hash` and `request_canonical_payload`.

**Auditability.** Independent verification is possible without trusting any runtime component. An auditor needs only the ledger contents and the Ed25519 public key.

---

## References

| Document | Path |
|----------|------|
| Receipt JSON Schema | `spec/receipt_schema.json` |
| Signing Algorithms | `spec/SIGNING_ALGORITHMS.md` |
| Audit Ledger Protocol | `spec/audit_ledger_protocol.md` |
| Ledger Entry JSON Schema | `spec/ledger_entry_schema.json` |
| Conformance Specification | `spec/RIO_CONFORMANCE_v2.3.0.md` |
