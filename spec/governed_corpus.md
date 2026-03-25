# Governed Corpus — Decision History Layer

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Data Architecture

---

## 1. Purpose

The Governed Corpus is a structured decision-history layer that records the complete lifecycle of every governed action processed by the RIO Protocol. It captures intent, classification, policy decisions, authorization outcomes, execution results, receipts, ledger references, and eventual outcomes. The corpus serves as the canonical data source for audit, simulation, risk modeling, and governance learning.

The Governed Corpus is distinct from the Audit Ledger. The Audit Ledger is an append-only, hash-linked chain optimized for tamper evidence and integrity verification. The Governed Corpus is a structured, queryable store optimized for analysis, pattern detection, and model training. Every record in the Governed Corpus references its corresponding ledger entry, and every ledger entry can be traced to its corpus record.

---

## 2. Scope

This specification covers:

- The structure and schema of Governed Corpus records.
- The relationship between corpus records and audit ledger entries.
- How the Governance Learning loop (Stage 9) consumes corpus data.
- Query patterns for audit, simulation, and risk modeling.
- Retention, access control, and integrity requirements.

This specification does not cover:

- The internal implementation of storage engines or databases.
- The Audit Ledger's hash chain mechanics (see `ledger_interoperability.md`).
- Specific machine learning algorithms used by the learning loop.

---

## 3. Terminology

| Term | Definition |
|------|-----------|
| **Corpus Record** | A single structured record in the Governed Corpus representing the full lifecycle of one governed action. |
| **Decision Chain** | The sequence of protocol outputs for a single request: intake → classification → intent → policy → authorization → execution → receipt → ledger entry. |
| **Outcome** | The eventual real-world result of an executed action, recorded asynchronously after execution completes. |
| **Corpus Query** | A structured query against the Governed Corpus for audit, simulation, or learning purposes. |

---

## 4. Corpus Record Structure

Each Governed Corpus record captures the outputs of every protocol stage for a single request. The record is assembled incrementally as the request traverses the protocol stages and is finalized when the ledger entry is written.

### 4.1 Record Fields

| Field | Type | Source Stage | Description |
|-------|------|-------------|-------------|
| `corpus_id` | string (UUID v4) | System | Unique identifier for this corpus record |
| `request_id` | string (UUID v4) | Stage 1 (Intake) | The request ID assigned at intake |
| `requester_id` | string (DID or URI) | Stage 1 (Intake) | Authenticated identity of the requester |
| `timestamp_intake` | string (ISO 8601) | Stage 1 (Intake) | When the request was registered |
| `nonce` | string | Stage 1 (Intake) | Cryptographic nonce from intake |
| `action_type` | string | Stage 2 (Classification) | Classified action type |
| `domain` | string | Stage 2 (Classification) | Risk domain |
| `preliminary_risk_level` | string | Stage 2 (Classification) | Initial risk assessment |
| `canonical_intent` | object | Stage 3 (Structured Intent) | The canonical intent object |
| `canonical_intent_hash` | string (hex) | Stage 3 (Structured Intent) | SHA-256 hash of the canonical intent |
| `policy_decision` | string | Stage 4 (Policy & Risk) | `allow`, `deny`, or `escalate` |
| `risk_score` | number | Stage 4 (Policy & Risk) | Quantified risk score |
| `risk_factors` | array | Stage 4 (Policy & Risk) | Individual risk factor assessments |
| `constraints` | array | Stage 4 (Policy & Risk) | Constraints imposed by policy |
| `authorization_decision` | string | Stage 5 (Authorization) | `approved`, `denied`, `escalated`, or `not_reached` |
| `authorizer_id` | string (DID or URI) | Stage 5 (Authorization) | Identity of the authorizer (if applicable) |
| `authorization_token_hash` | string (hex) | Stage 5 (Authorization) | Hash of the signed authorization token |
| `timestamp_authorization` | string (ISO 8601) | Stage 5 (Authorization) | When authorization was issued |
| `execution_result` | string | Stage 6 (Execution Gate) | `executed`, `blocked`, or `not_reached` |
| `execution_token_hash` | string (hex) | Stage 6 (Execution Gate) | Hash of the execution token (if issued) |
| `block_reason` | string | Stage 6 (Execution Gate) | Reason for block (if blocked) |
| `timestamp_execution` | string (ISO 8601) | Stage 6 (Execution Gate) | When execution occurred or was blocked |
| `receipt_id` | string | Stage 7 (Receipt) | Receipt identifier |
| `receipt_hash` | string (hex) | Stage 7 (Receipt) | Hash of the signed receipt |
| `ledger_entry_id` | string | Stage 8 (Audit Ledger) | Ledger entry identifier |
| `ledger_entry_hash` | string (hex) | Stage 8 (Audit Ledger) | Hash of the ledger entry |
| `outcome` | object | Asynchronous | Eventual real-world outcome (recorded after execution) |
| `outcome_recorded_at` | string (ISO 8601) | Asynchronous | When the outcome was recorded |
| `corpus_record_hash` | string (hex) | System | SHA-256 hash of the finalized corpus record |

### 4.2 Terminal States

Not every request traverses all stages. The corpus record captures where the request terminated:

| Terminal State | Stages Completed | Fields Populated |
|---------------|-----------------|-----------------|
| Policy denial | 1–4, 7–8 | Authorization fields set to `not_reached`; execution fields set to `not_reached` |
| Authorization denial | 1–5, 7–8 | Execution fields set to `not_reached` |
| Kill switch block | 1–6, 7–8 | `block_reason` set to `kill_switch_engaged` |
| Successful execution | 1–8 | All fields populated |

---

## 5. Outcome Recording

### 5.1 Purpose

The outcome field captures the eventual real-world result of an executed action. Outcomes are recorded asynchronously — they may arrive minutes, hours, or days after execution. Outcomes are essential for the Governance Learning loop because they provide the ground truth against which risk models and policies are evaluated.

### 5.2 Outcome Structure

| Field | Type | Description |
|-------|------|-------------|
| `outcome_type` | string | `success`, `partial_success`, `failure`, `reverted`, `disputed`, `unknown` |
| `outcome_description` | string | Human-readable description of what happened |
| `outcome_metrics` | object | Quantitative outcome data (e.g., actual amount transferred, time to completion) |
| `outcome_reported_by` | string (DID or URI) | Identity of the entity reporting the outcome |
| `outcome_evidence` | array | References to supporting evidence (receipts, confirmations, error logs) |

### 5.3 Example Outcome

```json
{
  "outcome_type": "success",
  "outcome_description": "Wire transfer of $48,250.00 completed successfully. Funds received by Meridian Industrial Supply LLC.",
  "outcome_metrics": {
    "amount_transferred": 48250.00,
    "currency": "USD",
    "settlement_time_hours": 2.3
  },
  "outcome_reported_by": "did:web:treasury-system.example.com",
  "outcome_evidence": [
    {
      "type": "bank_confirmation",
      "reference": "CONF-2026-03-24-8847",
      "timestamp": "2026-03-24T16:53:00Z"
    }
  ]
}
```

---

## 6. Relationship to Audit Ledger

The Governed Corpus and the Audit Ledger are complementary but distinct:

| Property | Audit Ledger | Governed Corpus |
|----------|-------------|-----------------|
| **Primary purpose** | Tamper-evident integrity proof | Structured analysis and learning |
| **Data model** | Append-only hash-linked chain | Structured records with queryable fields |
| **Mutability** | Immutable (append-only) | Record is assembled incrementally; outcome is appended asynchronously |
| **Query optimization** | Sequential traversal, hash verification | Indexed queries by action type, risk level, outcome, time range |
| **Retention** | Permanent | Configurable (minimum retention defined by governance) |
| **Integrity guarantee** | Hash chain + external anchors | Each record references its ledger entry hash; corpus record hash is verifiable |

Every corpus record MUST contain a `ledger_entry_id` and `ledger_entry_hash` that reference the corresponding audit ledger entry. This linkage ensures that any corpus record can be verified against the tamper-evident ledger.

---

## 7. Governance Learning Integration

### 7.1 Learning Inputs

The Governance Learning loop (Stage 9 of the Governed Execution Protocol) consumes corpus data to update risk models and policies. The following corpus fields are primary learning inputs:

| Learning Input | Corpus Fields Used | Learning Purpose |
|---------------|-------------------|-----------------|
| Risk calibration | `risk_score`, `risk_factors`, `outcome` | Compare predicted risk to actual outcome; recalibrate risk models |
| Policy effectiveness | `policy_decision`, `constraints`, `outcome` | Evaluate whether policy decisions led to good outcomes |
| Authorization patterns | `authorizer_id`, `authorization_decision`, `outcome` | Detect authorizer bias, fatigue, or anomalous approval patterns |
| Action type trends | `action_type`, `domain`, `risk_score`, `outcome` | Identify emerging risk patterns by action type |
| Execution failures | `execution_result`, `block_reason`, `outcome` | Analyze why executions fail and whether blocks were justified |

### 7.2 Learning Constraints

The learning loop operates under the following constraints:

1. Learning processes have **read-only** access to the Governed Corpus. They cannot modify corpus records.
2. Learning outputs (proposed policy changes, updated risk models) MUST be submitted as canonical requests through the Governed Execution Protocol itself. They require authorization before deployment.
3. Learning processes MUST NOT bypass runtime enforcement. Updated policies take effect only after they are authorized and deployed through the governed change process.

---

## 8. Query Patterns

### 8.1 Audit Queries

Audit queries retrieve corpus records for compliance review and investigation:

| Query Pattern | Description | Example |
|--------------|-------------|---------|
| By request ID | Retrieve the full decision chain for a specific request | "Show me everything that happened for request `a1b2c3d4`" |
| By requester | Retrieve all requests from a specific entity | "Show all requests from `did:web:procurement-agent.example.com` in the last 30 days" |
| By action type | Retrieve all requests of a specific type | "Show all `transact.send_payment.wire.*` requests in Q1 2026" |
| By outcome | Retrieve requests with a specific outcome type | "Show all requests where `outcome_type` is `failure` or `reverted`" |
| By risk level | Retrieve requests above a risk threshold | "Show all requests where `risk_score` exceeded 80" |

### 8.2 Simulation Queries

Simulation queries support "what-if" analysis by replaying historical corpus records against proposed policy changes:

| Query Pattern | Description |
|--------------|-------------|
| Policy replay | "If we had applied policy rule POL-NEW-001, how many of the last 1,000 requests would have been denied that were previously allowed?" |
| Risk threshold analysis | "If we lowered the auto-approve risk threshold from 30 to 20, how many additional requests would have required human authorization?" |
| Kill switch impact | "If the kill switch had been engaged at timestamp T, how many in-flight requests would have been blocked?" |

---

## 9. Access Control

| Role | Access Level | Permitted Operations |
|------|-------------|---------------------|
| Auditor | Read-only | Query corpus records; verify against ledger |
| Risk Analyst | Read-only | Query corpus records; run simulation queries |
| Learning System | Read-only | Consume corpus data for model training; output proposed changes as canonical requests |
| Governance Authority | Read + outcome write | Query corpus records; record outcomes |
| System Administrator | No direct access | Corpus access is through defined roles only; no administrative override |

---

## 10. Retention

Corpus records MUST be retained for a minimum period defined by the governance authority. The default minimum retention period is 7 years, consistent with common regulatory requirements for financial and compliance records. Records beyond the retention period MAY be archived but MUST NOT be deleted if their corresponding ledger entries still exist.

---

## 11. Integrity

Each finalized corpus record MUST have a `corpus_record_hash` computed as the SHA-256 hash of the canonicalized record (excluding the `corpus_record_hash` field itself). This hash enables independent verification that the corpus record has not been modified after finalization.

The `ledger_entry_hash` field in each corpus record MUST match the hash of the corresponding audit ledger entry. This cross-reference ensures that corpus records are consistent with the tamper-evident ledger.

---

## 12. Dependencies

| Document | Relationship |
|----------|-------------|
| Governed Execution Protocol | The corpus records outputs from all 8 protocol stages |
| Audit Ledger Protocol (09) | Every corpus record references a ledger entry |
| Governance Learning (governance_learning.md) | The learning loop consumes corpus data |
| Risk Evaluation Protocol (04) | Risk scores and factors are recorded in the corpus |
| Policy Constraints Protocol (05) | Policy decisions and constraints are recorded in the corpus |
| Receipt Specification (receipt_spec.md) | Receipt hashes are recorded in the corpus |
