# RIO Protocol — Receipt Specification

**Version:** 1.0.0
**Status:** Normative
**Protocol Reference:** 08 — Attestation Protocol, schemas/receipt.json

---

## 1. Overview

The receipt is the human-readable audit summary of a complete decision traceability chain in the RIO Protocol. It consolidates references to all prior records — canonical request, risk evaluation, authorization, execution, and attestation — into a single document that an auditor, regulator, or compliance officer can review to understand what happened, who was involved, and whether the process was followed correctly.

Every completed decision chain MUST produce exactly one receipt. The receipt MUST be cryptographically signed and stored alongside its corresponding ledger entry.

---

## 2. Canonical Receipt Fields

The receipt record contains the following fields, as defined in `schemas/receipt.json`:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_id` | string (UUID v4) | Yes | Unique identifier for this receipt |
| `request_id` | string (UUID v4) | Yes | Reference to the canonical request |
| `risk_evaluation_id` | string (UUID v4) | Yes | Reference to the risk evaluation record |
| `authorization_id` | string (UUID v4) | Yes | Reference to the authorization record |
| `execution_id` | string (UUID v4) or null | Yes | Reference to the execution record; null if not executed |
| `attestation_id` | string (UUID v4) or null | Yes | Reference to the attestation record; null if pending |
| `final_decision` | enum | Yes | approved, denied, approved_with_conditions, expired |
| `final_status` | enum | Yes | executed, failed, partial, cancelled, denied, expired, pending_execution |
| `timeline` | object | Yes | Chronological timestamps for every stage |
| `participants` | object | Yes | All entities involved in the decision chain |
| `action_summary` | object | Yes | Summary of what was requested and why |
| `execution_result` | object or null | Yes | Outcome of execution; null if not executed |
| `chain_integrity` | object | Yes | Cryptographic integrity verification results |
| `summary` | string | Yes | Plain-language narrative of the complete chain |
| `notes` | string or null | No | Auditor comments or follow-up actions |
| `signature` | object | Yes | Cryptographic signature over the receipt body |

### 2.1 Timeline Object

The `timeline` object MUST include timestamps for each stage that was completed:

| Field | Type | Description |
|-------|------|-------------|
| `request_timestamp` | string (ISO 8601) | When the canonical request was created |
| `risk_evaluation_timestamp` | string (ISO 8601) | When risk evaluation completed |
| `authorization_timestamp` | string (ISO 8601) | When authorization decision was made |
| `execution_timestamp` | string (ISO 8601) or null | When execution completed |
| `attestation_timestamp` | string (ISO 8601) or null | When attestation was issued |
| `receipt_timestamp` | string (ISO 8601) | When this receipt was generated |
| `total_duration_ms` | integer | Total elapsed time from request to receipt |

### 2.2 Participants Object

The `participants` object MUST identify every entity in the chain:

| Field | Type | Description |
|-------|------|-------------|
| `requester` | object | Entity that originated the request (entity_id, entity_type, display_name) |
| `risk_evaluator` | object | System or person that performed risk evaluation |
| `authorizer` | object | Person or authority that made the authorization decision |
| `executor` | object | System that performed the action |
| `attestor` | object | Service that attested the chain |

### 2.3 Chain Integrity Object

| Field | Type | Description |
|-------|------|-------------|
| `chain_hash` | string | SHA-256 hash of all record hashes concatenated |
| `all_checks_passed` | boolean | Whether all verification checks passed |
| `check_count` | integer | Total number of checks performed |
| `checks_passed` | integer | Number of checks that passed |

---

## 3. Receipt Hash Computation

The receipt hash is computed using the following algorithm. This hash is used for signature verification and ledger entry linking.

### 3.1 Algorithm

```
1. Let receipt_body = the complete receipt object
2. Remove the "signature" field from receipt_body
3. Serialize receipt_body to JSON using canonical form:
   a. Sort all object keys alphabetically at every nesting level
   b. Remove all whitespace (minified JSON)
   c. Use UTF-8 encoding
4. Compute SHA-256 hash of the canonical JSON string
5. Encode the hash as lowercase hexadecimal
6. Result = receipt_hash
```

### 3.2 Canonical JSON Rules

- Object keys MUST be sorted lexicographically (Unicode code point order) at every level of nesting.
- Arrays MUST preserve their original element order.
- Numbers MUST NOT have trailing zeros or leading plus signs.
- Strings MUST use minimal escape sequences.
- No whitespace between tokens.

### 3.3 Example

Given a receipt body (signature removed), the canonical form is:

```
{"action_summary":{...},"attestation_id":"...","authorization_id":"...","chain_integrity":{...},...}
```

The SHA-256 of this string produces the receipt hash.

---

## 4. Signature Requirements

Every receipt MUST be signed by the attestation service. The signature provides non-repudiation and tamper detection.

### 4.1 Signature Algorithm

- **Algorithm:** ECDSA with secp256k1 curve
- **Hash function:** SHA-256
- **Encoding:** DER-encoded signature, represented as lowercase hexadecimal

### 4.2 Signature Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `algorithm` | string | `ECDSA-secp256k1` |
| `public_key_id` | string | Identifier of the signing key |
| `signature_value` | string | Hexadecimal-encoded DER signature |
| `signed_fields_hash` | string | SHA-256 hash of the receipt body (excluding signature) |
| `signed_at` | string (ISO 8601) | Timestamp of signature creation |

### 4.3 Signing Procedure

```
1. Compute receipt_hash per Section 3
2. Set signed_fields_hash = receipt_hash
3. Sign receipt_hash using the attestation service private key
4. Encode signature as hexadecimal
5. Populate the signature object
```

### 4.4 Key Management

- Signing keys MUST be stored in a hardware security module (HSM) or equivalent secure key store.
- Key rotation MUST be logged in the audit ledger.
- Retired keys MUST remain available for historical receipt verification.

---

## 5. Receipt States

A receipt MUST be in exactly one of the following states:

| State | `final_decision` | `final_status` | Description |
|-------|-------------------|-----------------|-------------|
| Complete | approved | executed | Full chain completed successfully |
| Complete with conditions | approved_with_conditions | executed | Executed with constraints applied |
| Partial | approved | partial | Execution partially completed |
| Failed | approved | failed | Authorized but execution failed |
| Cancelled | approved | cancelled | Authorized but execution cancelled |
| Denied | denied | denied | Authorization denied; no execution |
| Expired | expired | expired | Authorization expired before execution |

---

## 6. Verification Procedure

An auditor MUST follow these steps to verify a receipt:

### Step 1: Recompute Receipt Hash

1. Remove the `signature` field from the receipt.
2. Compute the canonical JSON hash per Section 3.
3. Compare the computed hash with `signature.signed_fields_hash`.
4. If they do not match, the receipt has been tampered with. **FAIL.**

### Step 2: Verify Signature

1. Retrieve the public key identified by `signature.public_key_id`.
2. Verify the ECDSA signature over `signature.signed_fields_hash`.
3. If verification fails, the signature is invalid. **FAIL.**

### Step 3: Verify Chain Integrity

1. Retrieve the attestation record referenced by `attestation_id`.
2. Compare `chain_integrity.chain_hash` with the attestation record's `record_hashes.chain_hash`.
3. If they do not match, the chain has been broken. **FAIL.**

### Step 4: Verify Cross-References

1. Retrieve each referenced record: canonical request, risk evaluation, authorization, execution, attestation.
2. Verify that each record's ID matches the receipt's reference fields.
3. Verify that timestamps are chronologically ordered: request < risk_evaluation < authorization < execution < attestation < receipt.
4. If any reference is missing or timestamps are out of order, the chain is incomplete. **FAIL.**

### Step 5: Verify Record Hashes

1. For each referenced record, compute its canonical JSON hash.
2. Compare with the corresponding hash in the attestation record's `record_hashes`.
3. If any hash does not match, the referenced record has been tampered with. **FAIL.**

If all five steps pass, the receipt is **VERIFIED**.

---

## 7. Receipt Storage

Receipts MUST be stored following these requirements:

1. **Co-location with ledger.** Every receipt MUST have a corresponding ledger entry. The ledger entry's `record_id` MUST reference the `receipt_id`.
2. **Immutability.** Once stored, a receipt MUST NOT be modified. Corrections require a new receipt linked to the original.
3. **Retention.** Receipts MUST be retained for the duration specified by applicable regulatory requirements (minimum 7 years for financial operations).
4. **Redundancy.** Receipts SHOULD be stored in at least two geographically separated locations.

---

## 8. Receipt Querying

Implementations MUST support the following standard query patterns:

| Query | Parameters | Use Case |
|-------|-----------|----------|
| By receipt ID | `receipt_id` | Direct lookup of a specific receipt |
| By request ID | `request_id` | Find the receipt for a specific request |
| By time range | `start_time`, `end_time` | Audit all decisions within a period |
| By participant | `participant_id`, `participant_role` | Find all decisions involving a specific person or system |
| By final status | `final_status` | Find all denied, failed, or expired decisions |
| By action type | `action_type` | Find all decisions for a specific action class |
| By risk level | `risk_level` | Find all high or critical risk decisions |

---

## 9. Compliance Mapping

The RIO Protocol receipt satisfies requirements across multiple regulatory frameworks:

| Framework | Requirement | Receipt Field(s) |
|-----------|------------|-------------------|
| **SOX Section 302** | Management certification of financial controls | `participants.authorizer`, `final_decision`, `signature` |
| **SOX Section 404** | Internal control documentation | Full receipt — documents the complete control chain |
| **GDPR Article 5(2)** | Accountability principle | `chain_integrity`, `summary`, `signature` |
| **GDPR Article 30** | Records of processing activities | `action_summary`, `timeline`, `participants` |
| **ISO 27001 A.12.4** | Logging and monitoring | `timeline`, `execution_result`, `chain_integrity` |
| **NIST 800-53 AU-2** | Audit events | Full receipt — captures the complete audit event |
| **PCI DSS 10.2** | Audit trail for access to cardholder data | `participants`, `action_summary`, `timeline` |

### 9.1 Audit Export

For compliance reporting, receipts MAY be exported in the following formats:

- **JSON:** Complete receipt object as stored.
- **PDF:** Human-readable formatted document generated from the receipt fields.
- **CSV:** Flattened tabular format for bulk analysis.

---

## 10. Dependencies

| Dependency | Relationship |
|-----------|-------------|
| Canonical Request (schemas/canonical_request.json) | Referenced by `request_id` |
| Risk Evaluation (schemas/risk_evaluation.json) | Referenced by `risk_evaluation_id` |
| Authorization Record (schemas/authorization_record.json) | Referenced by `authorization_id` |
| Execution Record (schemas/execution_record.json) | Referenced by `execution_id` |
| Attestation Record (schemas/attestation_record.json) | Referenced by `attestation_id` |
| Audit Ledger Protocol (09) | Receipt stored as ledger entry |
