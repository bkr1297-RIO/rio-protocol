# RIO Protocol Extension: Identity and Credentials

**Version:** 1.0.0
**Status:** Extension Specification
**Category:** Advanced Infrastructure

---

## 1. Purpose

This extension defines how identity and authority are established, verified, and managed within a RIO Protocol deployment. It specifies the integration of Decentralized Identifiers (DIDs) and Verifiable Credentials (VCs) into the protocol's origin verification, authorization, and attestation stages. The goal is to provide a standards-based identity layer that supports both centralized and decentralized trust models while preserving the protocol's fail-closed guarantees.

This is a protocol extension. It does not modify the core 15-protocol stack. Implementations MAY adopt this extension to strengthen identity assurance beyond the baseline cryptographic key verification defined in Protocol 02 (Origin Verification).

---

## 2. Scope

This specification covers:

- Decentralized Identifier (DID) resolution and verification for protocol participants.
- Verifiable Credential (VC) issuance, presentation, and verification for authority claims.
- Credential-based authorization gating in the policy and authorization stages.
- Key management lifecycle (rotation, revocation, recovery) for protocol identities.
- Trust registry integration for credential issuer validation.

This specification does not cover:

- User interface or user experience for credential management.
- Specific DID method implementations (e.g., `did:web`, `did:key`, `did:ion`).
- Biometric authentication mechanisms.

---

## 3. Terminology

| Term | Definition |
|------|-----------|
| **DID** | Decentralized Identifier — a globally unique, self-sovereign identifier that resolves to a DID Document containing public keys and service endpoints. Defined in W3C DID Core 1.0. |
| **DID Document** | A JSON-LD document associated with a DID, containing verification methods (public keys), authentication methods, and service endpoints. |
| **Verifiable Credential (VC)** | A tamper-evident credential with cryptographic proof of authorship, conforming to W3C Verifiable Credentials Data Model 2.0. |
| **Verifiable Presentation (VP)** | A tamper-evident presentation of one or more VCs, bound to a specific holder and verifier context. |
| **Credential Issuer** | An entity authorized to issue Verifiable Credentials attesting to specific claims about a subject. |
| **Trust Registry** | A curated list of trusted credential issuers, maintained by the governance authority. |
| **Verification Method** | A public key or other mechanism listed in a DID Document that can be used to verify signatures. |

---

## 4. Identity Model

### 4.1 Participant Identity

Every participant in the RIO Protocol — requester, authorizer, executor, attester, auditor — MUST be identified by a DID. The DID serves as the canonical identifier across all protocol records.

```
did:<method>:<method-specific-id>
```

**Mapping to existing protocol fields:**

| Protocol Record | Field | Identity Value |
|----------------|-------|----------------|
| `canonical_request` | `requester_id` | DID of the requesting entity |
| `authorization_record` | `authorizer_id` | DID of the authorizing entity |
| `execution_record` | `executor_id` | DID of the executing entity |
| `attestation_record` | `attester_id` | DID of the attesting entity |
| `receipt` | `issued_by` | DID of the receipt issuer |

### 4.2 DID Resolution

Before any protocol operation that depends on identity verification, the system MUST resolve the participant's DID to its DID Document and extract the relevant verification method.

**Resolution procedure:**

1. Parse the DID string to extract the DID method.
2. Invoke the method-specific resolver to retrieve the DID Document.
3. Verify the DID Document integrity (signature, if applicable).
4. Extract the verification method identified by the `verificationMethod` reference in the protocol record.
5. Cache the resolved DID Document with a TTL not exceeding 300 seconds.

**Failure behavior:** If DID resolution fails for any reason (network error, invalid DID, revoked DID, resolver unavailable), the system MUST deny the operation. This is consistent with the fail-closed guarantee.

### 4.3 Supported DID Methods

Implementations MUST support at least one of the following DID methods:

| DID Method | Resolution | Use Case |
|-----------|-----------|----------|
| `did:web` | HTTPS resolution to `/.well-known/did.json` | Organizations with existing web infrastructure |
| `did:key` | Self-contained — public key encoded in the DID | Ephemeral or lightweight identities |

Implementations MAY support additional DID methods (e.g., `did:ion`, `did:ethr`, `did:pkh`) provided they conform to the W3C DID Core 1.0 specification.

---

## 5. Verifiable Credentials

### 5.1 Credential Structure

Verifiable Credentials used within the RIO Protocol MUST conform to the W3C Verifiable Credentials Data Model 2.0. Each credential MUST include the following properties:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `@context` | array | Yes | JSON-LD context, MUST include `https://www.w3.org/ns/credentials/v2` |
| `id` | string (URI) | Yes | Unique identifier for this credential |
| `type` | array | Yes | MUST include `VerifiableCredential` and a RIO-specific type |
| `issuer` | string (DID) | Yes | DID of the credential issuer |
| `validFrom` | string (ISO 8601) | Yes | Credential validity start |
| `validUntil` | string (ISO 8601) | Yes | Credential expiration |
| `credentialSubject` | object | Yes | Claims about the subject |
| `proof` | object | Yes | Cryptographic proof of issuance |

### 5.2 RIO Credential Types

The following credential types are defined for use within the RIO Protocol:

| Credential Type | Purpose | Issued To | Claims |
|----------------|---------|-----------|--------|
| `RIOAuthorizerCredential` | Grants authority to approve actions of specified types and risk levels | Authorizer | `authorizedActions`, `maxRiskLevel`, `scope` |
| `RIOExecutorCredential` | Grants authority to execute actions on specified systems | Executor | `allowedSystems`, `allowedActions`, `scope` |
| `RIOAuditorCredential` | Grants read access to ledger entries and receipts | Auditor | `ledgerAccess`, `receiptAccess`, `scope` |
| `RIOPolicyAdminCredential` | Grants authority to propose policy changes (subject to meta-governance) | Policy Admin | `policyScope`, `changeTypes` |
| `RIOAgentCredential` | Identifies an AI agent or automated system as a recognized requester | AI Agent | `agentType`, `allowedActions`, `riskCeiling` |

### 5.3 Example: RIOAuthorizerCredential

```json
{
  "@context": [
    "https://www.w3.org/ns/credentials/v2",
    "https://rio-protocol.org/credentials/v1"
  ],
  "id": "urn:uuid:c7e8f9a0-b1c2-4d3e-8f5a-6b7c8d9e0f1a",
  "type": ["VerifiableCredential", "RIOAuthorizerCredential"],
  "issuer": "did:web:governance.example.com",
  "validFrom": "2026-01-01T00:00:00Z",
  "validUntil": "2027-01-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:web:cfo.example.com",
    "authorizedActions": [
      "transact.send_payment.*",
      "transact.approve_invoice.*"
    ],
    "maxRiskLevel": "critical",
    "scope": {
      "organizationId": "org-example-corp",
      "departments": ["finance", "treasury"],
      "amountCeiling": {
        "currency": "USD",
        "value": 500000.00
      }
    }
  },
  "proof": {
    "type": "DataIntegrityProof",
    "cryptosuite": "ecdsa-secp256k1-2019",
    "created": "2026-01-01T00:00:00Z",
    "verificationMethod": "did:web:governance.example.com#key-1",
    "proofPurpose": "assertionMethod",
    "proofValue": "z3FXQjecWufY46..."
  }
}
```

### 5.4 Credential Verification

When a participant presents a Verifiable Credential as part of a protocol operation, the verifier MUST perform the following checks in order:

| # | Check | Failure Action |
|---|-------|----------------|
| 1 | Credential structure conforms to VC Data Model 2.0 | Reject credential |
| 2 | `issuer` DID resolves to a valid DID Document | Reject credential |
| 3 | `issuer` DID is listed in the Trust Registry | Reject credential |
| 4 | `proof` signature verifies against the issuer's public key | Reject credential |
| 5 | `validFrom` ≤ current time ≤ `validUntil` | Reject credential (expired or not yet valid) |
| 6 | Credential has not been revoked (check revocation list or status) | Reject credential |
| 7 | `credentialSubject.id` matches the presenter's DID | Reject credential (holder mismatch) |
| 8 | Claims in `credentialSubject` satisfy the required authority for the operation | Reject credential (insufficient authority) |

All 8 checks MUST pass. If any check fails, the operation MUST be denied.

---

## 6. Credential-Gated Authorization

### 6.1 Integration with Policy Evaluation (Protocol 05)

The policy engine MAY include credential-based rules that require the authorizer to present a valid credential with specific claims before authorization is accepted.

**Example policy rule:**

```json
{
  "rule_id": "POL-FIN-001",
  "description": "Wire transfers over $25,000 require an authorizer with RIOAuthorizerCredential scoped to finance with sufficient amount ceiling",
  "condition": {
    "action_type": "transact.send_payment.wire.*",
    "amount_gt": 25000.00
  },
  "requirement": {
    "credential_type": "RIOAuthorizerCredential",
    "claims": {
      "authorizedActions": { "includes": "transact.send_payment.wire.*" },
      "scope.amountCeiling.value": { "gte": "${request.amount}" },
      "scope.departments": { "includes": "finance" }
    }
  }
}
```

### 6.2 Integration with Authorization (Protocol 06)

When an authorizer submits an authorization decision, the system MUST:

1. Resolve the authorizer's DID.
2. Verify the authorization signature against the DID Document's verification method.
3. If the policy requires a credential, verify the presented Verifiable Presentation.
4. Confirm that the credential claims satisfy the policy requirements.
5. Record the credential ID and issuer in the `authorization_record.metadata` field.

### 6.3 Integration with Origin Verification (Protocol 02)

Origin verification MUST resolve the requester's DID and verify the request signature against the DID Document. If the requester is an AI agent, the system MUST additionally verify that the agent holds a valid `RIOAgentCredential` with claims that permit the requested action type.

---

## 7. Key Management

### 7.1 Key Rotation

Participants MUST be able to rotate their cryptographic keys without changing their DID. Key rotation is performed by updating the DID Document to add a new verification method and (optionally) deactivate the old one.

**Rotation procedure:**

1. Generate a new key pair.
2. Update the DID Document to include the new verification method.
3. Set the old verification method's status to `deactivated` with an effective date.
4. Sign the DID Document update with the current (old) key to prove authority.
5. Publish the updated DID Document.

**Grace period:** Implementations SHOULD support a configurable grace period (default: 24 hours) during which both the old and new keys are accepted. After the grace period, only the new key is valid.

### 7.2 Key Revocation

If a key is compromised, the participant MUST revoke it immediately by:

1. Updating the DID Document to set the compromised key's status to `revoked`.
2. Publishing the updated DID Document.
3. Notifying the governance authority.

**Effect on in-flight operations:** Any authorization or attestation signed with a revoked key that has not yet been executed MUST be invalidated. The execution gate MUST re-verify key status before releasing execution.

### 7.3 DID Deactivation

A DID MAY be deactivated (permanently disabled) by the governance authority. Deactivation removes the participant from the protocol entirely. All pending operations associated with the deactivated DID MUST be denied.

---

## 8. Trust Registry

### 8.1 Purpose

The Trust Registry is a curated, governance-controlled list of entities that are trusted to issue Verifiable Credentials within the RIO Protocol deployment. It prevents arbitrary entities from issuing credentials that would be accepted by the system.

### 8.2 Registry Structure

```json
{
  "registry_id": "urn:uuid:a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
  "version": 12,
  "updated_at": "2026-03-24T10:00:00Z",
  "governance_authority": "did:web:governance.example.com",
  "trusted_issuers": [
    {
      "issuer_did": "did:web:governance.example.com",
      "credential_types": ["RIOAuthorizerCredential", "RIOExecutorCredential", "RIOAuditorCredential", "RIOPolicyAdminCredential", "RIOAgentCredential"],
      "trust_level": "root",
      "valid_from": "2026-01-01T00:00:00Z",
      "valid_until": "2027-01-01T00:00:00Z"
    },
    {
      "issuer_did": "did:web:hr.example.com",
      "credential_types": ["RIOAuthorizerCredential"],
      "trust_level": "delegated",
      "valid_from": "2026-01-01T00:00:00Z",
      "valid_until": "2026-07-01T00:00:00Z",
      "constraints": {
        "maxRiskLevel": "medium",
        "scope.departments": ["hr"]
      }
    }
  ]
}
```

### 8.3 Registry Governance

Changes to the Trust Registry MUST be processed through the RIO Protocol's meta-governance mechanism (Protocol 13). Adding or removing a trusted issuer requires a canonical request, risk evaluation, authorization, and ledger recording — the same governance applied to any other consequential action.

---

## 9. Credential Revocation

### 9.1 Revocation Mechanisms

Implementations MUST support at least one credential revocation mechanism:

| Mechanism | Description | Latency |
|-----------|-------------|---------|
| **Status List 2021** | Bitstring-based status list referenced by credential `credentialStatus` field | Near real-time (polling interval) |
| **Revocation List** | Signed list of revoked credential IDs published by the issuer | Batch (publication interval) |

### 9.2 Revocation Check Timing

The credential revocation status MUST be checked:

1. At origin verification (Protocol 02) — for requester agent credentials.
2. At authorization (Protocol 06) — for authorizer credentials.
3. At execution gate (Protocol 07) — re-check before releasing execution.

The execution gate re-check (item 3) is critical because a credential may be revoked between authorization and execution. The fail-closed guarantee requires that revoked credentials block execution even if authorization was previously granted.

---

## 10. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| DID Document spoofing | DID resolution MUST use authenticated channels (HTTPS with certificate validation for `did:web`). DID Documents SHOULD be signed. |
| Credential replay | Verifiable Presentations MUST include a `challenge` and `domain` to bind the presentation to a specific verifier and session. |
| Issuer compromise | Trust Registry entries MUST have expiration dates. Compromised issuers MUST be removed from the registry immediately. All credentials issued by a compromised issuer MUST be treated as revoked. |
| Key compromise | Key revocation MUST propagate within the DID Document TTL (max 300 seconds). The execution gate MUST re-verify key status before execution. |
| Stale DID Document cache | DID Document cache TTL MUST NOT exceed 300 seconds. For critical operations (execution gate), implementations SHOULD bypass the cache and resolve fresh. |

---

## 11. Dependencies

| Document | Relationship |
|----------|-------------|
| Origin Verification Protocol (02) | DID-based identity replaces or augments key-based origin verification |
| Policy Constraints Protocol (05) | Credential-based policy rules reference this extension |
| Authorization Protocol (06) | Credential-gated authorization references this extension |
| Execution Protocol (07) | Execution gate re-verifies credential status |
| Meta-Governance Protocol (13) | Trust Registry changes are governed by meta-governance |
| W3C DID Core 1.0 | External standard for Decentralized Identifiers |
| W3C Verifiable Credentials Data Model 2.0 | External standard for Verifiable Credentials |
