# Canonical Intent Schema

**Version:** 2.0.0
**Status:** Core Specification
**Category:** Data Structure

---

## 1. Purpose

The Canonical Intent Schema defines the standard structured format that all intents must conform to before entering the Governed Execution Protocol. This ensures that all requests are machine-readable, policy-evaluable, and auditable.

Every intent — regardless of whether it originates from an AI agent, an automated system, or a human-initiated workflow — must be normalized into this canonical format during Intent Formation and validated against it during Intent Validation. Only intents that conform to this schema are accepted into the Governed Execution Protocol at Stage 1 (Intake).

---

## 2. Canonical Intent Structure

Each intent is represented as a structured object with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `intent_id` | string | Yes | Unique identifier for the intent |
| `request_id` | string | Yes | Link to intake request |
| `action_type` | string | Yes | Type of action requested (e.g., `transfer_funds`, `deploy_code`, `delete_data`, `grant_access`, `send_email`) |
| `target_resource` | string | Yes | System or resource being acted on (e.g., `payment_system`, `production_cluster`, `customer_database`) |
| `parameters` | object | Yes | Action-specific parameters (contents vary by action type) |
| `requested_by` | string | Yes | Identity of requester (verified at Intake, not self-reported) |
| `justification` | string | Yes | Reason for the action (used by policy evaluation and human authorizers) |
| `risk_category` | string (enum) | Yes | Risk level: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `required_approvals` | array of strings | Yes | List of required approvers or roles that must authorize this intent |
| `timestamp` | string (ISO 8601) | Yes | Time intent was created |
| `status` | string (enum) | Yes | Current state: `pending`, `validated`, `denied`, `approved`, `executed` |

---

## 3. Example Intent Object

The following example shows a canonical intent for a fund transfer request:

```json
{
  "intent_id": "INT-001",
  "request_id": "REQ-001",
  "action_type": "transfer_funds",
  "target_resource": "payment_system",
  "parameters": {
    "amount": 5000,
    "currency": "EUR",
    "recipient": "Vendor_X",
    "source_account": "Berlin_Office_Account"
  },
  "requested_by": "Intern_User_04",
  "justification": "Office supplies invoice",
  "risk_category": "HIGH",
  "required_approvals": ["Finance_Manager"],
  "timestamp": "2026-01-10T10:32:00Z",
  "status": "pending"
}
```

In this example, the intent requests a 5,000 EUR transfer from the Berlin Office Account to Vendor_X. The risk category is `HIGH` because the action involves financial transfer. The `required_approvals` field specifies that a Finance Manager must authorize the intent before it can proceed to the Execution Gate. The `status` is `pending` because the intent has been formed but not yet validated or authorized.

---

## 4. Status Lifecycle

The `status` field tracks the intent through the protocol stages:

| Status | Meaning | Set By |
|--------|---------|--------|
| `pending` | Intent has been formed but not yet validated | Intent Formation |
| `validated` | Intent has passed schema and business rule validation | Intent Validation |
| `denied` | Intent was denied by policy, risk evaluation, or authorization | Policy & Risk Check or Authorization |
| `approved` | Intent has been authorized and is eligible for execution | Authorization (Stage 5) |
| `executed` | Intent has been executed and a receipt has been generated | Execution Gate (Stage 6) / Receipt (Stage 7) |

Status transitions are unidirectional. An intent cannot move from `denied` back to `pending`, or from `executed` back to `approved`. Every status change is recorded in the audit trail.

---

## 5. Relationship to Other Specifications

| Document | Relationship |
|----------|-------------|
| `/spec/canonical_intent_schema.json` | Machine-readable JSON Schema for automated validation |
| `/spec/intent_ontology.md` | Defines the standard `action_type` vocabulary |
| `/spec/governed_execution_protocol.md` | Defines the protocol stages that consume the canonical intent |
| `/spec/reference_architecture.md` | Places the canonical intent in the system data flow |
| `/spec/protocol_invariants.md` | Invariants that apply to intent processing |
