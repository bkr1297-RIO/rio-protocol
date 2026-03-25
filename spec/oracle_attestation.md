# RIO Protocol Extension: Oracle Attestation

**Version:** 1.0.0
**Status:** Extension Specification
**Category:** Advanced Infrastructure

---

## 1. Purpose

This extension defines how external signed attestations — produced by systems, services, or authorities outside the RIO Protocol boundary — can be ingested, verified, and used as inputs to the risk evaluation and policy evaluation stages of the protocol. These external attestations are referred to as **oracle attestations** because they provide externally sourced, cryptographically verifiable claims about facts that the RIO system cannot independently determine.

Examples of oracle attestations include: compliance certification status from a regulatory body, credit risk scores from a financial data provider, identity verification results from a KYC service, vulnerability scan results from a security tool, and environmental sensor readings from an IoT platform.

This is a protocol extension. It does not modify the core 15-protocol stack. Implementations MAY adopt this extension to incorporate external evidence into risk and policy decisions.

---

## 2. Scope

This specification covers:

- The structure and schema of oracle attestation records.
- The verification procedure for oracle attestations.
- How oracle attestations are consumed by the risk evaluation engine (Protocol 04) and the policy engine (Protocol 05).
- Oracle registry management and trust establishment.
- Freshness requirements and staleness handling.
- Attestation chaining (oracle attestations that reference other attestations).

This specification does not cover:

- The internal implementation of external oracle systems.
- How external systems generate their attestations.
- Network transport or API design for fetching attestations (see `api_endpoints.md` for API patterns).

---

## 3. Terminology

| Term | Definition |
|------|-----------|
| **Oracle** | An external system or authority that produces signed attestations about facts relevant to risk or policy evaluation. |
| **Oracle Attestation** | A cryptographically signed statement from an oracle asserting one or more claims about a subject, with a defined validity period. |
| **Oracle Registry** | A governance-controlled list of trusted oracles, their public keys, the claim types they are authorized to attest, and their trust level. |
| **Claim** | A single factual assertion within an oracle attestation (e.g., "entity X has a credit score of 720"). |
| **Freshness** | The recency of an oracle attestation relative to the current time. Stale attestations may be rejected by policy. |
| **Attestation Chain** | A sequence of oracle attestations where each attestation references a prior attestation, creating a verifiable history. |

---

## 4. Oracle Attestation Record

### 4.1 Record Structure

An oracle attestation record MUST contain the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `attestation_id` | string (UUID v4) | Yes | Unique identifier for this attestation |
| `oracle_id` | string (DID or URI) | Yes | Identifier of the oracle that produced this attestation |
| `subject_id` | string | Yes | The entity or resource this attestation is about |
| `attestation_type` | string | Yes | The category of attestation (see Section 4.2) |
| `claims` | array of objects | Yes | One or more claims asserted by the oracle |
| `evidence` | object | No | Supporting evidence or methodology reference |
| `issued_at` | string (ISO 8601) | Yes | When the oracle produced this attestation |
| `valid_from` | string (ISO 8601) | Yes | Start of the attestation's validity period |
| `valid_until` | string (ISO 8601) | Yes | End of the attestation's validity period |
| `previous_attestation_id` | string (UUID v4) | No | Reference to a prior attestation in an attestation chain |
| `signature` | string (base64) | Yes | Oracle's cryptographic signature over the attestation |
| `signature_algorithm` | string | Yes | Algorithm used (e.g., `ECDSA-secp256k1`, `Ed25519`) |
| `canonical_hash` | string (hex) | Yes | SHA-256 hash of the canonicalized attestation (excluding signature fields) |

### 4.2 Attestation Types

The following attestation types are defined for use within the RIO Protocol:

| Type | Description | Typical Oracle |
|------|-------------|----------------|
| `compliance.certification` | Regulatory compliance status (e.g., SOC 2, ISO 27001, GDPR) | Compliance auditor |
| `compliance.sanctions` | Sanctions screening result | Sanctions screening service |
| `financial.credit_score` | Credit risk assessment | Credit bureau |
| `financial.fraud_score` | Fraud likelihood assessment | Fraud detection service |
| `identity.verification` | Identity verification result (KYC/KYB) | Identity verification provider |
| `security.vulnerability` | Vulnerability scan or penetration test result | Security scanning tool |
| `security.threat_intel` | Threat intelligence assessment | Threat intelligence feed |
| `operational.system_health` | System health or availability status | Monitoring platform |
| `environmental.sensor` | Environmental sensor reading (temperature, pressure, etc.) | IoT platform |
| `legal.contract_status` | Contract validity or amendment status | Legal document management system |

Implementations MAY define additional attestation types. Custom types MUST use the namespace `custom.<domain>.<type>`.

### 4.3 Claim Structure

Each claim within an oracle attestation MUST contain:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `claim_id` | string | Yes | Unique identifier for this claim within the attestation |
| `claim_type` | string | Yes | The type of fact being asserted |
| `value` | any | Yes | The asserted value |
| `confidence` | number (0.0–1.0) | No | Oracle's confidence in the claim (1.0 = certain) |
| `methodology` | string | No | How the oracle determined this claim |

### 4.4 Example: Compliance Certification Attestation

```json
{
  "attestation_id": "f1a2b3c4-d5e6-7890-a1b2-c3d4e5f6a7b8",
  "oracle_id": "did:web:compliance-auditor.example.com",
  "subject_id": "did:web:vendor.example.com",
  "attestation_type": "compliance.certification",
  "claims": [
    {
      "claim_id": "CLM-001",
      "claim_type": "soc2_type2_status",
      "value": "certified",
      "confidence": 1.0,
      "methodology": "Annual audit completed 2026-02-15"
    },
    {
      "claim_id": "CLM-002",
      "claim_type": "soc2_type2_expiration",
      "value": "2027-02-15T00:00:00Z",
      "confidence": 1.0
    }
  ],
  "evidence": {
    "report_id": "RPT-2026-0042",
    "report_url": "https://compliance-auditor.example.com/reports/RPT-2026-0042",
    "audit_standard": "AICPA SOC 2 Type II"
  },
  "issued_at": "2026-02-20T09:00:00Z",
  "valid_from": "2026-02-15T00:00:00Z",
  "valid_until": "2027-02-15T00:00:00Z",
  "previous_attestation_id": null,
  "signature": "MEUCIQD7x8f9...",
  "signature_algorithm": "ECDSA-secp256k1",
  "canonical_hash": "a3b4c5d6e7f8..."
}
```

### 4.5 Example: Credit Score Attestation

```json
{
  "attestation_id": "b2c3d4e5-f6a7-8901-b2c3-d4e5f6a7b8c9",
  "oracle_id": "did:web:credit-bureau.example.com",
  "subject_id": "org:meridian-industrial-supply",
  "attestation_type": "financial.credit_score",
  "claims": [
    {
      "claim_id": "CLM-001",
      "claim_type": "credit_score",
      "value": 720,
      "confidence": 0.95,
      "methodology": "Composite score from payment history, credit utilization, and public records"
    },
    {
      "claim_id": "CLM-002",
      "claim_type": "credit_risk_category",
      "value": "low",
      "confidence": 0.95
    },
    {
      "claim_id": "CLM-003",
      "claim_type": "days_payable_outstanding",
      "value": 32,
      "confidence": 0.90,
      "methodology": "Based on last 12 months of reported payment data"
    }
  ],
  "issued_at": "2026-03-24T08:00:00Z",
  "valid_from": "2026-03-24T08:00:00Z",
  "valid_until": "2026-04-24T08:00:00Z",
  "signature": "MEQCIGh5j6k7...",
  "signature_algorithm": "ECDSA-secp256k1",
  "canonical_hash": "d4e5f6a7b8c9..."
}
```

---

## 5. Oracle Attestation Verification

When the RIO system receives an oracle attestation, it MUST perform the following verification procedure before the attestation can be used as input to risk or policy evaluation.

| # | Check | Condition | Failure Action |
|---|-------|-----------|----------------|
| 1 | Structure valid | Attestation contains all required fields | Reject attestation |
| 2 | Oracle registered | `oracle_id` is listed in the Oracle Registry | Reject attestation |
| 3 | Oracle authorized for type | Oracle Registry entry permits `attestation_type` | Reject attestation |
| 4 | DID resolves | `oracle_id` DID resolves to a valid DID Document | Reject attestation |
| 5 | Signature valid | `signature` verifies against the oracle's public key | Reject attestation |
| 6 | Hash valid | Recomputed canonical hash matches `canonical_hash` | Reject attestation |
| 7 | Not expired | `current_time` ≤ `valid_until` | Reject attestation (stale) |
| 8 | Valid period started | `current_time` ≥ `valid_from` | Reject attestation (not yet valid) |
| 9 | Freshness check | `issued_at` is within the freshness threshold for the attestation type | Reject or flag as stale |
| 10 | Chain integrity | If `previous_attestation_id` is set, the referenced attestation exists and is valid | Reject attestation |

All 10 checks MUST pass. If any check fails, the attestation MUST be rejected and MUST NOT influence risk or policy evaluation.

---

## 6. Integration with Risk Evaluation (Protocol 04)

### 6.1 Attestation as Risk Input

Oracle attestations provide external evidence that the risk evaluation engine can incorporate into its risk scoring. The risk engine MUST treat oracle attestations as advisory inputs, not as overrides of its own assessment.

**Integration points:**

| Risk Factor | Oracle Attestation Type | Effect on Risk Score |
|------------|------------------------|---------------------|
| Counterparty risk | `financial.credit_score` | Low credit score increases risk; high score decreases risk |
| Compliance risk | `compliance.certification` | Missing or expired certification increases risk |
| Fraud risk | `financial.fraud_score` | High fraud score increases risk |
| Identity risk | `identity.verification` | Failed or incomplete verification increases risk |
| System risk | `security.vulnerability` | Unpatched critical vulnerabilities increase risk |
| Sanctions risk | `compliance.sanctions` | Positive sanctions match sets risk to critical |

### 6.2 Risk Score Adjustment

The risk engine MUST record which oracle attestations were considered and how they influenced the risk score. This information is captured in the `risk_evaluation.risk_factors` array:

```json
{
  "risk_factors": [
    {
      "factor": "counterparty_credit_risk",
      "source": "oracle_attestation",
      "oracle_attestation_id": "b2c3d4e5-f6a7-8901-b2c3-d4e5f6a7b8c9",
      "oracle_id": "did:web:credit-bureau.example.com",
      "claim_type": "credit_score",
      "claim_value": 720,
      "risk_adjustment": -15,
      "rationale": "Credit score 720 indicates low counterparty risk"
    }
  ]
}
```

### 6.3 Missing Attestation Handling

If a policy requires an oracle attestation for a specific risk factor and the attestation is not available (oracle unreachable, attestation expired, no attestation on file), the risk engine MUST apply the **fail-closed default**: treat the missing attestation as the worst-case scenario for that risk factor.

---

## 7. Integration with Policy Evaluation (Protocol 05)

### 7.1 Attestation-Based Policy Rules

The policy engine MAY define rules that require specific oracle attestations as preconditions for authorization.

**Example policy rule:**

```json
{
  "rule_id": "POL-VENDOR-001",
  "description": "Payments to vendors over $10,000 require a valid compliance certification and credit score attestation",
  "condition": {
    "action_type": "transact.send_payment.*",
    "amount_gt": 10000.00,
    "target_type": "vendor"
  },
  "required_attestations": [
    {
      "attestation_type": "compliance.certification",
      "subject": "${request.target_id}",
      "claims": {
        "soc2_type2_status": { "equals": "certified" }
      },
      "max_age_hours": 8760
    },
    {
      "attestation_type": "financial.credit_score",
      "subject": "${request.target_id}",
      "claims": {
        "credit_score": { "gte": 600 }
      },
      "max_age_hours": 720
    }
  ]
}
```

### 7.2 Policy Evaluation Outcome

When the policy engine evaluates attestation-based rules, it MUST record the evaluation result:

| Outcome | Description | Effect |
|---------|-------------|--------|
| `attestation_satisfied` | All required attestations are present, valid, and claims meet thresholds | Policy rule passes |
| `attestation_missing` | A required attestation is not available | Policy rule fails (deny) |
| `attestation_expired` | A required attestation has expired | Policy rule fails (deny) |
| `attestation_stale` | A required attestation is older than `max_age_hours` | Policy rule fails (deny) |
| `claim_unsatisfied` | A required claim does not meet the threshold | Policy rule fails (deny) |

---

## 8. Oracle Registry

### 8.1 Purpose

The Oracle Registry is a governance-controlled list of external systems that are trusted to provide attestations within the RIO Protocol deployment. It prevents arbitrary external systems from influencing risk and policy decisions.

### 8.2 Registry Entry Structure

```json
{
  "oracle_id": "did:web:credit-bureau.example.com",
  "name": "Example Credit Bureau",
  "attestation_types": [
    "financial.credit_score",
    "financial.fraud_score"
  ],
  "trust_level": "verified",
  "verification_method": "did:web:credit-bureau.example.com#signing-key-1",
  "signature_algorithm": "ECDSA-secp256k1",
  "freshness_requirements": {
    "financial.credit_score": {
      "max_age_hours": 720,
      "refresh_interval_hours": 168
    },
    "financial.fraud_score": {
      "max_age_hours": 24,
      "refresh_interval_hours": 6
    }
  },
  "valid_from": "2026-01-01T00:00:00Z",
  "valid_until": "2027-01-01T00:00:00Z",
  "added_by": "did:web:governance.example.com",
  "added_at": "2026-01-01T00:00:00Z",
  "ledger_entry_id": "le-a1b2c3d4"
}
```

### 8.3 Trust Levels

| Trust Level | Description | Governance Requirement |
|-------------|-------------|----------------------|
| `root` | Governance authority itself | N/A (bootstrap) |
| `verified` | Oracle identity and capabilities independently verified | Governance authorization + independent audit |
| `registered` | Oracle identity verified, capabilities self-declared | Governance authorization |
| `provisional` | Temporary trust, pending full verification | Governance authorization with expiration ≤ 90 days |

### 8.4 Registry Governance

Changes to the Oracle Registry (adding, modifying, or removing oracles) MUST be processed through the RIO Protocol's meta-governance mechanism (Protocol 13). This ensures that changes to the set of trusted external inputs are themselves governed, authorized, and recorded in the ledger.

---

## 9. Freshness and Staleness

### 9.1 Freshness Thresholds

Each attestation type has a freshness threshold defined in the Oracle Registry. The freshness threshold specifies the maximum age of an attestation before it is considered stale.

| Attestation Type | Typical Freshness Threshold | Rationale |
|-----------------|---------------------------|-----------|
| `compliance.sanctions` | 24 hours | Sanctions lists change frequently |
| `financial.fraud_score` | 24 hours | Fraud indicators are time-sensitive |
| `financial.credit_score` | 30 days | Credit scores change slowly |
| `compliance.certification` | 365 days | Certifications are typically annual |
| `security.vulnerability` | 7 days | Vulnerability landscape changes weekly |
| `identity.verification` | 365 days | Identity verification is typically annual |

### 9.2 Staleness Handling

When an attestation exceeds its freshness threshold:

1. The attestation MUST be flagged as stale in the risk evaluation.
2. The risk engine MUST apply a staleness penalty to the risk score.
3. If the policy requires a fresh attestation and only a stale one is available, the policy rule MUST fail.
4. The system SHOULD attempt to request a fresh attestation from the oracle if an automated refresh mechanism is configured.

---

## 10. Attestation Chaining

Oracle attestations MAY reference prior attestations via the `previous_attestation_id` field. This creates a verifiable history of attestations for a given subject, enabling trend analysis and anomaly detection.

**Use cases for attestation chaining:**

- Tracking credit score changes over time for a vendor.
- Monitoring compliance certification renewals.
- Detecting sudden changes in fraud scores that may indicate compromise.

**Chain verification:** When verifying a chained attestation, the system MUST verify the entire chain back to the first attestation (or to a configurable chain depth limit). Each link in the chain MUST pass the standard verification procedure (Section 5).

---

## 11. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Oracle compromise | Oracle Registry entries have expiration dates. Compromised oracles MUST be removed immediately. All attestations from a compromised oracle MUST be invalidated. |
| Attestation forgery | All attestations are cryptographically signed. Signature verification is mandatory. |
| Stale data exploitation | Freshness thresholds prevent old attestations from influencing current decisions. |
| Oracle collusion | Multiple independent oracles SHOULD be required for critical risk factors. Policy rules MAY require attestations from N-of-M oracles. |
| Replay of old attestations | Each attestation has a unique `attestation_id` and a `valid_until` timestamp. Expired attestations are rejected. |
| Man-in-the-middle | Oracle attestations are signed at the source. Transport-layer interception cannot modify the attestation without invalidating the signature. |

---

## 12. Dependencies

| Document | Relationship |
|----------|-------------|
| Risk Evaluation Protocol (04) | Oracle attestations are consumed as risk inputs |
| Policy Constraints Protocol (05) | Attestation-based policy rules reference this extension |
| Meta-Governance Protocol (13) | Oracle Registry changes are governed by meta-governance |
| Identity and Credentials Extension | Oracle identity uses the DID-based identity model |
| System Invariants | Oracle attestation verification upholds fail-closed invariants |
