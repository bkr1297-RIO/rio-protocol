# Canonical Intent Schema

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Data Structure

---

## Overview

The Canonical Intent Schema defines the structured format used to represent a normalized, validated action request within the Governed Execution Protocol. The canonical intent is produced by Stage 3 (Structured Intent) and consumed by Stage 4 (Policy & Risk Check), Stage 5 (Authorization), and Stage 6 (Execution Gate). It is the single authoritative representation of what is being requested, by whom, against which resource, and under what justification.

The canonical intent is distinct from the raw request received at Intake. Raw requests may arrive in varied formats from different requester types (AI agents, APIs, human-initiated workflows). The Structured Intent stage normalizes all requests into this canonical format before any policy, risk, or authorization evaluation occurs.

---

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `intent_id` | string (UUID v4) | Yes | Unique identifier for this canonical intent |
| `action_type` | string | Yes | Canonical action type from the intent ontology (e.g., `WIRE_TRANSFER`, `DATA_DELETE`, `CODE_DEPLOY`, `ACCESS_GRANT`, `EMAIL_SEND`) |
| `target_resource` | string | Yes | Identifier of the resource upon which the action is to be performed (e.g., account ID, database name, deployment target, recipient address) |
| `parameters` | object | Yes | Action-specific parameters normalized to standard formats. Contents vary by action type but must conform to the parameter schema defined for that action type in the intent ontology |
| `requested_by` | string | Yes | Verified identity of the requesting entity (DID URI or system identifier). This value is set by the Intake stage based on authenticated identity, not self-reported by the requester |
| `justification` | string | Yes | Human-readable explanation of why this action is being requested. Used by Policy & Risk Check and by human authorizers to evaluate the request in context |
| `risk_category` | string (enum) | Yes | Preliminary risk level assigned by the Classification stage. Values: `low`, `medium`, `high`, `critical` |
| `required_approvals` | integer | Yes | Number of independent approvals required before authorization is granted. Determined by the Policy & Risk Check stage based on action type, risk category, and organizational policy |
| `timestamp` | integer | Yes | UTC Unix timestamp in milliseconds when the canonical intent was formed at Stage 3 |

---

## Additional Context Fields

The following fields are carried through the protocol for traceability but are not part of the authorization decision:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string (UUID v4) | Yes | Reference to the original request registered at Stage 1 (Intake) |
| `nonce` | string | Yes | Cryptographic nonce (minimum 128 bits) generated at Intake to prevent replay attacks |
| `origin_type` | string (enum) | Yes | Type of requester: `ai_agent`, `automated_system`, `human_initiated` |
| `session_id` | string | No | Session or conversation identifier, if applicable |

---

## Canonical Hashing

The canonical intent is hashed using SHA-256 over its minified, sorted JSON representation (excluding any fields added after formation). This hash serves as the `intent_hash` referenced in authorization tokens, receipts, and ledger entries. Any modification to the canonical intent after formation invalidates all downstream records that reference its hash.

---

## Validation Rules

The following validation rules apply at Stage 3 (Structured Intent) before the canonical intent is accepted into the protocol:

1. All required fields must be present and non-empty.
2. `intent_id` must be a valid UUID v4.
3. `action_type` must match a recognized entry in the intent ontology (`/spec/intent_ontology.md`).
4. `target_resource` must conform to the resource identifier format defined for the action type.
5. `parameters` must validate against the parameter schema defined for the action type.
6. `requested_by` must match the authenticated identity established at Intake.
7. `risk_category` must be one of: `low`, `medium`, `high`, `critical`.
8. `required_approvals` must be a positive integer (minimum 1).
9. `timestamp` must be within the allowed time skew window (300 seconds) of the current server time.
10. `nonce` must not appear in the nonce registry (replay check).

If any validation rule fails, the canonical intent is rejected and a denial receipt is generated.

---

## Relationship to JSON Schema

The machine-readable JSON Schema for the canonical intent is defined in `/spec/canonical_intent_schema.json`. This document provides the human-readable specification and validation rules. The JSON Schema provides the machine-enforceable structure.

---

## References

| Document | Path |
|----------|------|
| Canonical Intent JSON Schema | `/spec/canonical_intent_schema.json` |
| Intent Ontology | `/spec/intent_ontology.md` |
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Protocol Invariants | `/spec/protocol_invariants.md` |
