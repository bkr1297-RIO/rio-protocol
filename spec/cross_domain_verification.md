# RIO Protocol Extension: Cross-Domain Verification

**Version:** 1.0.0
**Status:** Extension Specification
**Category:** Advanced Infrastructure

---

## 1. Purpose

This extension defines how receipts, ledger entries, and attestation records produced by one RIO Protocol deployment can be cryptographically verified by a different system — whether that system is another RIO deployment, an external auditor, a regulatory body, or a counterparty organization. The goal is to enable trust across organizational and system boundaries without requiring shared infrastructure or direct database access.

Cross-domain verification is essential for multi-party workflows where one organization's governed action produces evidence that another organization needs to validate. For example, a vendor may need to prove to a customer that a payment was authorized through a governed process, or a regulated entity may need to submit cryptographic proof of compliance to a regulator.

This is a protocol extension. It does not modify the core 15-protocol stack. Implementations MAY adopt this extension to support inter-organizational verification and regulatory reporting.

---

## 2. Scope

This specification covers:

- Portable verification bundles that package receipts with all data needed for independent verification.
- Cryptographic proof structures for receipts and ledger entries.
- Verification procedures that external systems can execute without access to the originating system.
- Selective disclosure mechanisms that allow verification while protecting sensitive fields.
- Anchoring mechanisms that bind RIO ledger state to external trust anchors (e.g., public blockchains, timestamping authorities).
- Federation protocols for RIO-to-RIO cross-domain verification.

This specification does not cover:

- The internal implementation of external verification systems.
- Legal frameworks for cross-jurisdictional evidence acceptance.
- Network transport protocols for transmitting verification bundles.

---

## 3. Terminology

| Term | Definition |
|------|-----------|
| **Originating Domain** | The RIO Protocol deployment that produced the receipt, ledger entry, or attestation being verified. |
| **Verifying Domain** | The system or organization performing the verification. |
| **Verification Bundle** | A self-contained package containing a receipt and all cryptographic material needed to verify it independently. |
| **Selective Disclosure** | A mechanism that allows the originating domain to reveal only specific fields of a record while proving the integrity of the complete record. |
| **Trust Anchor** | An external, independent system used to anchor cryptographic commitments (e.g., a public blockchain, an RFC 3161 timestamping authority). |
| **Merkle Proof** | A cryptographic proof that a specific element is included in a Merkle tree, without revealing the entire tree. |
| **Federation** | A trust relationship between two RIO Protocol deployments that enables mutual verification. |

---

## 4. Verification Bundle

### 4.1 Purpose

A verification bundle is a self-contained, portable package that allows any external party to verify the authenticity and integrity of a RIO Protocol receipt without access to the originating system. The bundle includes the receipt, the public keys needed to verify signatures, and the hash chain context needed to verify ledger inclusion.

### 4.2 Bundle Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bundle_id` | string (UUID v4) | Yes | Unique identifier for this verification bundle |
| `bundle_version` | string | Yes | Bundle format version (currently `1.0.0`) |
| `originating_domain` | string (DID or URI) | Yes | Identifier of the RIO deployment that produced this bundle |
| `created_at` | string (ISO 8601) | Yes | When this bundle was created |
| `receipt` | object | Yes | The complete receipt record (or a selectively disclosed subset) |
| `public_keys` | array of objects | Yes | Public keys needed to verify all signatures in the bundle |
| `ledger_proof` | object | Yes | Proof of the receipt's inclusion in the originating ledger |
| `anchor_proofs` | array of objects | No | Proofs anchoring the ledger state to external trust anchors |
| `disclosure_map` | object | No | Map of which fields are disclosed vs. redacted (for selective disclosure) |
| `bundle_signature` | string (base64) | Yes | Signature over the entire bundle by the originating domain |
| `bundle_hash` | string (hex) | Yes | SHA-256 hash of the canonicalized bundle (excluding signature fields) |

### 4.3 Public Key Block

Each entry in the `public_keys` array provides the key material needed to verify a specific signature within the bundle:

```json
{
  "public_keys": [
    {
      "key_id": "did:web:governance.example.com#key-1",
      "owner": "did:web:governance.example.com",
      "role": "receipt_issuer",
      "algorithm": "ECDSA-secp256k1",
      "public_key_jwk": {
        "kty": "EC",
        "crv": "secp256k1",
        "x": "WbbaSStuffx...",
        "y": "YbbaSStufffy..."
      },
      "valid_from": "2026-01-01T00:00:00Z",
      "valid_until": "2027-01-01T00:00:00Z"
    },
    {
      "key_id": "did:web:cfo.example.com#key-1",
      "owner": "did:web:cfo.example.com",
      "role": "authorizer",
      "algorithm": "ECDSA-secp256k1",
      "public_key_jwk": {
        "kty": "EC",
        "crv": "secp256k1",
        "x": "AnotherKeyX...",
        "y": "AnotherKeyY..."
      },
      "valid_from": "2026-01-01T00:00:00Z",
      "valid_until": "2027-01-01T00:00:00Z"
    }
  ]
}
```

### 4.4 Example Verification Bundle

```json
{
  "bundle_id": "vb-a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
  "bundle_version": "1.0.0",
  "originating_domain": "did:web:rio.example.com",
  "created_at": "2026-03-24T15:00:00Z",
  "receipt": {
    "receipt_id": "rcp-f1a2b3c4",
    "request_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
    "action_summary": "Wire transfer of $48,250.00 to Meridian Industrial Supply LLC",
    "decision": "approved",
    "risk_level": "high",
    "authorized_by": "did:web:cfo.example.com",
    "executed_at": "2026-03-24T14:35:12Z",
    "receipt_hash": "a3b4c5d6e7f8...",
    "receipt_signature": "MEUCIQD7x8f9..."
  },
  "public_keys": [ "..." ],
  "ledger_proof": {
    "ledger_entry_id": "le-d4e5f6a7",
    "entry_hash": "b4c5d6e7f8a9...",
    "previous_hash": "c5d6e7f8a9b0...",
    "entry_index": 14823,
    "merkle_root": "e7f8a9b0c1d2...",
    "merkle_proof": [
      { "position": "left", "hash": "f8a9b0c1d2e3..." },
      { "position": "right", "hash": "a9b0c1d2e3f4..." },
      { "position": "left", "hash": "b0c1d2e3f4a5..." }
    ]
  },
  "anchor_proofs": [
    {
      "anchor_type": "rfc3161_timestamp",
      "anchor_id": "tsa-a1b2c3d4",
      "timestamp_token": "MIIGHgYJKoZI...",
      "anchored_hash": "e7f8a9b0c1d2...",
      "anchor_time": "2026-03-24T15:00:05Z",
      "authority": "https://tsa.example.com"
    }
  ],
  "bundle_signature": "MEQCIGh5j6k7...",
  "bundle_hash": "c3d4e5f6a7b8..."
}
```

---

## 5. Verification Procedure

An external verifier receiving a verification bundle MUST perform the following checks in order. All checks MUST pass for the bundle to be considered valid.

### 5.1 Bundle Integrity

| # | Check | Condition | Failure Action |
|---|-------|-----------|----------------|
| 1 | Bundle structure valid | All required fields present, types correct | Reject bundle |
| 2 | Bundle hash valid | Recomputed hash of canonicalized bundle matches `bundle_hash` | Reject bundle |
| 3 | Bundle signature valid | `bundle_signature` verifies against the originating domain's public key | Reject bundle |

### 5.2 Receipt Integrity

| # | Check | Condition | Failure Action |
|---|-------|-----------|----------------|
| 4 | Receipt hash valid | Recomputed hash of canonicalized receipt matches `receipt.receipt_hash` | Reject bundle |
| 5 | Receipt signature valid | `receipt.receipt_signature` verifies against the receipt issuer's public key (from `public_keys`) | Reject bundle |
| 6 | Authorization signature valid | If authorization signature is included, it verifies against the authorizer's public key | Reject bundle |

### 5.3 Ledger Inclusion

| # | Check | Condition | Failure Action |
|---|-------|-----------|----------------|
| 7 | Merkle proof valid | The receipt hash, combined with the Merkle proof path, produces the stated `merkle_root` | Reject bundle |
| 8 | Entry hash valid | The `ledger_entry_id` hash matches the expected hash for the entry at `entry_index` | Reject bundle |
| 9 | Hash chain link valid | `previous_hash` is consistent with the chain (if verifier has access to adjacent entries) | Flag as unverifiable (not necessarily invalid) |

### 5.4 Anchor Verification (Optional)

| # | Check | Condition | Failure Action |
|---|-------|-----------|----------------|
| 10 | Anchor proof valid | The anchor proof verifies against the external trust anchor | Flag as unanchored |
| 11 | Anchored hash matches | The `anchored_hash` in the anchor proof matches the `merkle_root` | Reject anchor proof |
| 12 | Anchor time plausible | The `anchor_time` is consistent with the receipt and ledger timestamps | Flag as suspicious |

---

## 6. Selective Disclosure

### 6.1 Purpose

Selective disclosure allows the originating domain to share a verification bundle that proves the integrity of a complete receipt while revealing only specific fields. This is essential for privacy-preserving verification where the verifier needs to confirm that a governed action occurred and was authorized, but does not need to see all details (e.g., exact amounts, internal account numbers, or participant identities).

### 6.2 Mechanism

Selective disclosure is implemented using a per-field hashing approach:

1. Each field in the receipt is individually hashed.
2. The field hashes are combined into a Merkle tree.
3. The Merkle root serves as the receipt hash.
4. Disclosed fields are included in plaintext; redacted fields are replaced with their individual hashes.
5. The verifier can reconstruct the Merkle root from the disclosed fields and the redacted field hashes, confirming that the disclosed fields are authentic parts of the complete receipt.

### 6.3 Disclosure Map

The `disclosure_map` field in the verification bundle specifies which fields are disclosed:

```json
{
  "disclosure_map": {
    "receipt_id": "disclosed",
    "request_id": "disclosed",
    "action_summary": "redacted",
    "decision": "disclosed",
    "risk_level": "disclosed",
    "authorized_by": "redacted",
    "executed_at": "disclosed",
    "amount": "redacted",
    "recipient": "redacted"
  }
}
```

### 6.4 Redacted Field Representation

Redacted fields are replaced with their individual SHA-256 hashes:

```json
{
  "receipt": {
    "receipt_id": "rcp-f1a2b3c4",
    "request_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
    "action_summary": { "_redacted": true, "_hash": "d5e6f7a8b9c0..." },
    "decision": "approved",
    "risk_level": "high",
    "authorized_by": { "_redacted": true, "_hash": "e6f7a8b9c0d1..." },
    "executed_at": "2026-03-24T14:35:12Z",
    "amount": { "_redacted": true, "_hash": "f7a8b9c0d1e2..." },
    "recipient": { "_redacted": true, "_hash": "a8b9c0d1e2f3..." }
  }
}
```

### 6.5 Verification with Selective Disclosure

The verifier performs the same verification procedure (Section 5), with the following modification: when computing the receipt hash, the verifier uses the plaintext of disclosed fields and the provided hashes of redacted fields. If the resulting Merkle root matches the stated `receipt_hash`, the disclosed fields are verified as authentic.

---

## 7. External Trust Anchors

### 7.1 Purpose

Trust anchors provide an independent, external proof that a specific ledger state existed at a specific time. This prevents the originating domain from retroactively altering its ledger and claiming the altered version is original. Anchoring is particularly important for regulatory compliance and dispute resolution.

### 7.2 Supported Anchor Types

| Anchor Type | Description | Trust Basis |
|------------|-------------|-------------|
| `rfc3161_timestamp` | RFC 3161 Trusted Timestamping — a signed timestamp from a Time Stamping Authority (TSA) | TSA's certificate chain, typically rooted in a public CA |
| `blockchain_anchor` | Hash committed to a public blockchain (e.g., Bitcoin, Ethereum) | Blockchain consensus and immutability |
| `transparency_log` | Entry in a Certificate Transparency-style append-only log | Log operator's commitment and third-party monitoring |

### 7.3 Anchoring Procedure

1. At a configurable interval (e.g., every 100 ledger entries, or every hour), compute the Merkle root of the current ledger state.
2. Submit the Merkle root to one or more external trust anchors.
3. Receive and store the anchor proof (timestamp token, transaction hash, or log entry ID).
4. Record the anchoring event in the ledger itself as a system entry.

### 7.4 Anchor Proof Structure

```json
{
  "anchor_type": "blockchain_anchor",
  "anchor_id": "btc-tx-a1b2c3d4e5f6",
  "anchored_hash": "e7f8a9b0c1d2...",
  "anchor_time": "2026-03-24T15:00:00Z",
  "authority": "bitcoin_mainnet",
  "transaction_hash": "0x1a2b3c4d5e6f...",
  "block_number": 892341,
  "block_hash": "0x7a8b9c0d1e2f...",
  "merkle_proof_in_block": ["0x2b3c4d5e...", "0x3c4d5e6f..."]
}
```

---

## 8. Federation

### 8.1 Purpose

Federation enables two RIO Protocol deployments to establish a mutual trust relationship, allowing each deployment to verify receipts and ledger entries produced by the other. Federation is used in multi-party workflows where both parties operate their own RIO deployments.

### 8.2 Federation Agreement

A federation agreement is a bilateral trust relationship between two RIO deployments. It is established through the meta-governance process (Protocol 13) on both sides.

| Field | Type | Description |
|-------|------|-------------|
| `federation_id` | string (UUID v4) | Unique identifier for this federation agreement |
| `domain_a` | string (DID) | DID of the first RIO deployment |
| `domain_b` | string (DID) | DID of the second RIO deployment |
| `established_at` | string (ISO 8601) | When the federation was established |
| `expires_at` | string (ISO 8601) | When the federation expires |
| `verification_endpoint_a` | string (URL) | Domain A's verification API endpoint |
| `verification_endpoint_b` | string (URL) | Domain B's verification API endpoint |
| `public_keys_a` | array | Domain A's public keys for bundle verification |
| `public_keys_b` | array | Domain B's public keys for bundle verification |
| `shared_anchor_types` | array | Anchor types both domains agree to use |
| `disclosure_policy` | object | Agreed selective disclosure rules for cross-domain bundles |

### 8.3 Federated Verification Flow

1. Domain A produces a receipt for a governed action.
2. Domain A creates a verification bundle with the receipt, public keys, ledger proof, and anchor proofs.
3. Domain A applies the federation's disclosure policy to selectively disclose fields.
4. Domain A transmits the bundle to Domain B.
5. Domain B verifies the bundle using the procedure in Section 5.
6. Domain B additionally verifies that Domain A's public keys match the federation agreement.
7. Domain B records the verified cross-domain receipt in its own ledger as a reference entry.

---

## 9. Verification API

### 9.1 Endpoints

Implementations that support cross-domain verification SHOULD expose the following API endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/v1/verify/bundle` | Submit a verification bundle for verification |
| `GET` | `/api/v1/verify/receipt/{receipt_id}` | Request a verification bundle for a specific receipt |
| `POST` | `/api/v1/verify/anchor` | Verify an anchor proof against the originating ledger |
| `GET` | `/api/v1/federation/agreements` | List active federation agreements |
| `POST` | `/api/v1/federation/verify` | Verify a bundle within a federation context |

### 9.2 Verification Response

```json
{
  "verification_id": "ver-a1b2c3d4",
  "bundle_id": "vb-a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
  "result": "valid",
  "checks_performed": 12,
  "checks_passed": 12,
  "checks_failed": 0,
  "details": [
    { "check": "bundle_structure", "result": "pass" },
    { "check": "bundle_hash", "result": "pass" },
    { "check": "bundle_signature", "result": "pass" },
    { "check": "receipt_hash", "result": "pass" },
    { "check": "receipt_signature", "result": "pass" },
    { "check": "authorization_signature", "result": "pass" },
    { "check": "merkle_proof", "result": "pass" },
    { "check": "entry_hash", "result": "pass" },
    { "check": "hash_chain_link", "result": "pass" },
    { "check": "anchor_proof", "result": "pass" },
    { "check": "anchored_hash", "result": "pass" },
    { "check": "anchor_time", "result": "pass" }
  ],
  "verified_at": "2026-03-24T15:05:00Z"
}
```

---

## 10. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Bundle forgery | Bundle signature and receipt signature provide two layers of cryptographic protection. Both must verify. |
| Ledger rewriting | Merkle proofs and external trust anchors make retroactive ledger modification detectable. |
| Key compromise in originating domain | Anchor proofs provide independent evidence. If the originating domain's keys are compromised after anchoring, the anchor proof remains valid. |
| Selective disclosure leakage | Redacted field hashes do not reveal field values. However, if the value space is small (e.g., boolean fields), the hash may be brute-forced. Implementations SHOULD add salt to field hashes for low-entropy fields. |
| Federation trust decay | Federation agreements have expiration dates. Expired agreements MUST be renewed through meta-governance. |
| Replay of verification bundles | Bundles are timestamped and signed. Verifiers SHOULD check that the bundle creation time is recent relative to the verification request. |

---

## 11. Dependencies

| Document | Relationship |
|----------|-------------|
| Attestation Protocol (08) | Attestation records are included in verification bundles |
| Audit Ledger Protocol (09) | Ledger entries and hash chain are the basis for ledger proofs |
| Meta-Governance Protocol (13) | Federation agreements are governed by meta-governance |
| Receipt Specification (receipt_spec.md) | Receipts are the primary payload of verification bundles |
| Ledger Interoperability (ledger_interoperability.md) | Hash chain verification and external anchoring patterns |
| Identity and Credentials Extension | DID-based identity for originating and verifying domains |
