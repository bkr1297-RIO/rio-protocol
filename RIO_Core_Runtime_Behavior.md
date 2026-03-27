# RIO Core Runtime Behavior

**Version:** 1.0.0
**Protocol Format:** v2 (receipts and ledger entries)
**Status:** Canonical Implementation-Independent Reference
**Purpose:** This document describes the complete runtime behavior of the RIO Governed Execution Protocol. It is derived from the reference implementation but contains no code, no internal file references, and no repository-specific details. An external engineering team can implement a fully RIO-compliant system using only this document.

---

## Table of Contents

1. [Intent Envelope](#1-intent-envelope)
2. [Signature and Authentication](#2-signature-and-authentication)
3. [Governor Policy Logic](#3-governor-policy-logic)
4. [Execution Gate](#4-execution-gate)
5. [Receipt Generation](#5-receipt-generation)
6. [Ledger](#6-ledger)
7. [State Machine](#7-state-machine)
8. [Error Codes and Failure Conditions](#8-error-codes-and-failure-conditions)

---

## 1. Intent Envelope

The Intent Envelope is the canonical data structure that represents a governed action request. Every action that enters the RIO pipeline is normalized into this format before any policy evaluation, risk assessment, or authorization occurs. The envelope is the single source of truth for what was requested, by whom, and with what parameters.

### 1.1 Pipeline Context

The Intent Envelope is produced by the first three pipeline stages working in sequence:

1. **Intake** receives the raw request, assigns a `request_id`, validates the actor identity, and records the origin timestamp.
2. **Classification** examines the raw input to determine the `action_type` and preliminary `risk_category`.
3. **Structured Intent** converts the validated, classified request into the canonical Intent Envelope format.

### 1.2 Full Intent Envelope Structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | string (UUID v4) | Yes | Unique identifier assigned at intake. Links all pipeline artifacts back to the original request. |
| `requested_by` | string | Yes | Identity of the entity (human or AI agent) that initiated the request. Resolved from the actor registry at intake. |
| `requested_at` | string (ISO 8601) | Yes | UTC timestamp of when the request was received at intake. |
| `action_type` | string | Yes | Canonical action classification. Determines which policy rules, risk rules, and parameter requirements apply. |
| `target` | object | Yes | The system or resource the action targets. Contains `resource_type` (string) and `resource_id` (string). |
| `parameters` | object | Yes | Action-specific parameters. The required fields within this object depend on the `action_type` (see Section 1.4). |
| `business_reason` | object | Yes | Contains `summary` (string, required), `justification` (string, optional), and `supporting_references` (array, optional). |
| `risk_context` | object | Yes | Risk assessment metadata. Contains `risk_level` (enum: `low`, `medium`, `high`, `critical`), `risk_factors` (array of strings), `financial_impact` (object with `currency` and `amount`), and `reversibility` (enum: `reversible`, `partially_reversible`, `irreversible`). |
| `policy_context` | object | Yes | Policy evaluation metadata. Contains `applicable_policies` (array of policy references), `requires_authorization` (boolean), `authorization_type` (enum: `none`, `single_approver`, `multi_approver`, `escalation`), and `constraints` (array of constraint objects). |

### 1.3 Field Validation Rules

The following validation rules are enforced at the Intent Validation stage. If any rule fails, the request is rejected and a denial receipt is generated.

**Base field validation (all action types):**

- `action_type` MUST be present and non-empty.
- `requested_by` MUST be present and non-empty.
- `target_resource` MUST be present and non-empty.
- `parameters` MUST be present (may be an empty object for actions with no required parameters).
- `actor_id` MUST be present (resolved from the authentication layer at intake).
- The `action_type` from classification MUST be consistent with the raw input.

**Action-specific parameter validation (Intent Requirements Matrix):**

Each `action_type` has a defined set of required parameter fields. If the action type is registered in the requirements matrix, all listed fields MUST be present and non-null in the `parameters` object.

| Action Type | Required Parameters |
|-------------|-------------------|
| `send_email` | `recipient`, `subject`, `body` |
| `transfer_funds` | `amount`, `currency`, `recipient`, `source_account` |
| `create_event` | `title`, `time`, `duration` |
| `delete_data` | `dataset`, `scope`, `approval_authority` |
| `deploy_code` | `repository`, `branch`, `environment` |
| `grant_access` | `target_user`, `resource`, `permission_level` |
| `read_data` | `dataset` |
| `update_config` | `config_key`, `config_value` |

If an `action_type` is not listed in the matrix, no parameter-level validation is enforced beyond the base schema fields.

### 1.4 Canonicalization Rules for Hashing

When computing the **intent hash**, the following fields are extracted from the Intent Envelope and serialized into a canonical JSON object:

```json
{
  "intent_id": "<UUID>",
  "action_type": "<string>",
  "requested_by": "<string>",
  "target_resource": "<string>",
  "parameters": { ... }
}
```

**Canonicalization procedure:**

1. Construct a JSON object containing exactly the five fields listed above.
2. Serialize the object using **sorted keys** (alphabetical order at every nesting level).
3. Use the default JSON serialization for all value types. Non-serializable values (e.g., datetime objects) are converted to their string representation.
4. Encode the resulting JSON string as **UTF-8 bytes**.
5. Compute the **SHA-256** hash of the UTF-8 bytes.
6. The intent hash is the lowercase hexadecimal representation of the SHA-256 digest (64 characters).

**Example:**

Given intent fields:
```json
{
  "intent_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "action_type": "transfer_funds",
  "requested_by": "user_alice",
  "target_resource": "payment_system",
  "parameters": {"amount": 5000, "currency": "USD", "recipient": "vendor_corp", "source_account": "acct_001"}
}
```

Step 1: Serialize with sorted keys produces:
```
{"action_type": "transfer_funds", "intent_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890", "parameters": {"amount": 5000, "currency": "USD", "recipient": "vendor_corp", "source_account": "acct_001"}, "requested_by": "user_alice", "target_resource": "payment_system"}
```

Step 2: SHA-256 of the UTF-8 encoding of that string produces the intent hash.

### 1.5 Classification Rules

The Classification stage assigns a preliminary `risk_category` based on the `action_type`. The default classification rules are:

| Action Type | Default Risk Category |
|-------------|----------------------|
| `transfer_funds` | HIGH |
| `delete_data` | CRITICAL |
| `send_email` | MEDIUM |
| `deploy_code` | HIGH |
| `grant_access` | CRITICAL |
| `read_data` | LOW |
| `update_config` | MEDIUM |

These are default rules. A production implementation SHOULD load classification rules from a configurable policy store.

---

## 2. Signature and Authentication

RIO uses RSA-PSS digital signatures for all cryptographic attestations (receipts and ledger entries). Every receipt and every ledger entry is signed, creating a verifiable chain of custody from intent through execution to audit.

### 2.1 What Is Signed

There are four distinct signing operations in the protocol:

**Receipt Signature:**

The receipt signature covers the critical decision chain fields. The signing payload is constructed by **string concatenation (no separator)** of the following fields in this exact order:

```
intent_hash + action_hash + decision + timestamp_execution + receipt_hash + previous_hash
```

| Position | Field | Source |
|----------|-------|--------|
| 1 | `intent_hash` | SHA-256 of canonical intent JSON |
| 2 | `action_hash` | SHA-256 of canonical execution payload JSON |
| 3 | `decision` | `"approved"` or `"denied"` |
| 4 | `timestamp_execution` | ISO 8601 UTC string |
| 5 | `receipt_hash` | SHA-256 of canonical receipt fields (see Section 5) |
| 6 | `previous_hash` | Receipt hash of the preceding receipt in the chain |

**Ledger Entry Signature:**

The ledger entry signature covers the `ledger_hash` field (see Section 6.3 for how `ledger_hash` is computed). The signing payload is the `ledger_hash` string itself.

### 2.2 How Signatures Are Verified

To verify a receipt signature:

1. Reconstruct the signing payload by concatenating the six fields in the exact order specified above.
2. Encode the payload string as UTF-8 bytes.
3. Decode the `signature` field from Base64 to raw bytes.
4. Load the RSA public key (PEM format, SubjectPublicKeyInfo encoding).
5. Verify using RSA-PSS with the parameters specified in Section 2.3.
6. If verification succeeds, the signature is valid. If it throws an exception, the signature is invalid.

To verify a ledger entry signature:

1. The signing payload is the `ledger_hash` string.
2. Encode the `ledger_hash` as UTF-8 bytes.
3. Decode the `ledger_signature` field from Base64 to raw bytes.
4. Verify using RSA-PSS with the same parameters.

### 2.3 Accepted Signature Algorithm

| Parameter | Value |
|-----------|-------|
| Algorithm | RSA-PSS |
| Key Size | 2048 bits |
| Hash Function | SHA-256 |
| Mask Generation Function | MGF1 with SHA-256 |
| Salt Length | PSS maximum length (equal to hash length: 32 bytes for SHA-256) |
| Public Exponent | 65537 |
| Key Encoding | PEM (SubjectPublicKeyInfo for public key, TraditionalOpenSSL for private key) |
| Signature Encoding | Base64-encoded raw signature bytes |

### 2.4 Nonce Rules

Authorization tokens include a single-use nonce mechanism:

- Each authorization token has a unique `authorization_id` that serves as its nonce.
- The `single_use` field MUST be `true` for all authorization tokens.
- When the Execution Gate consumes a token, the `authorization_id` is added to the set of consumed tokens in the system state.
- Before allowing execution, the Execution Gate MUST check that the `authorization_id` has not been previously consumed.
- If the `authorization_id` is found in the consumed set, the execution MUST be denied with an invariant violation (INV-07: Single-Use Authorization).

### 2.5 Timestamp Rules

The protocol uses two timestamp formats depending on context:

| Context | Format | Example |
|---------|--------|---------|
| v2 Receipt timestamps | ISO 8601 UTC | `2026-03-26T14:30:00.000000+00:00` |
| Ledger entry timestamps | Unix epoch milliseconds (integer) | `1711461000000` |
| Authorization token timestamps | Unix epoch milliseconds (integer) | `1711461000000` |
| Intent timestamps | Unix epoch milliseconds (integer) | `1711461000000` |

**Authorization token expiration:**

- The `expiration_timestamp` is set to `approval_timestamp + 300000` (300 seconds / 5 minutes) by default.
- The Execution Gate MUST verify that the current time is before the `expiration_timestamp`.
- Expired tokens MUST be rejected even if they have not been consumed.

### 2.6 Replay Protection Logic

Replay protection is enforced through three mechanisms working together:

1. **Single-use nonces:** Each authorization token can be consumed exactly once. After consumption, the `authorization_id` is permanently recorded in the consumed token set.
2. **Time-bound expiration:** Authorization tokens expire after 300 seconds. Even if an attacker captures a valid token, it becomes unusable after expiration.
3. **Hash chain linkage:** Each receipt references the hash of the previous receipt (`previous_hash`). Each ledger entry references the hash of the previous ledger entry (`previous_ledger_hash`). Inserting a replayed transaction would break the hash chain.

### 2.7 Failure Conditions

| Condition | Result |
|-----------|--------|
| Signature verification fails | Receipt or ledger entry is considered tampered. Verification check returns `passed: false`. |
| Authorization token has been consumed | Execution denied. Invariant violation INV-07. |
| Authorization token has expired | Execution denied. Token rejected at Execution Gate. |
| Public key not available | Verification cannot proceed. Error reported. |
| Signature field is empty | Verification check returns `passed: false` with detail "no signature". |

### 2.8 Key Management

- A single RSA-2048 key pair is used for all signing operations (receipts and ledger entries).
- If no key pair exists at startup, the system generates an ephemeral key pair automatically.
- The private key file MUST have restricted permissions (owner read-only, mode 0600).
- The public key is distributed to any entity that needs to verify signatures.
- Key rotation: when a new key pair is generated, all subsequent receipts and ledger entries are signed with the new key. Previously signed artifacts remain verifiable with the old public key.

---

## 3. Governor Policy Logic

The Governor Policy Logic determines whether a request should be allowed, denied, or escalated to human authorization. It consists of two evaluations that run in sequence: **Risk Assessment** and **Policy Evaluation**.

### 3.1 How Risk Is Evaluated

Risk evaluation computes a numeric risk score from four additive components:

```
risk_score = base_risk + role_risk + amount_risk + system_target_risk
```

**Component 1: Base Risk (by action type)**

| Action Type | Base Risk Score |
|-------------|----------------|
| `send_email` | 1 |
| `create_event` | 1 |
| `read_data` | 1 |
| `update_config` | 3 |
| `transfer_funds` | 5 |
| `deploy_code` | 6 |
| `grant_access` | 7 |
| `delete_data` | 8 |

Default base risk for unlisted action types: 3.

**Component 2: Role Risk (by requester role)**

| Role | Role Risk Score |
|------|----------------|
| `admin` | 1 |
| `manager` | 2 |
| `employee` | 3 |
| `contractor` | 4 |
| `intern` | 6 |

Default role risk for unlisted roles: 3.

**Component 3: Amount Risk (by financial value)**

| Amount Range | Risk Addition |
|-------------|---------------|
| $0 - $99.99 | 0 |
| $100 - $999.99 | 1 |
| $1,000 - $9,999.99 | 3 |
| $10,000+ | 5 |

Amount risk is only computed when the `parameters` object contains an `amount` field. If no amount is present, amount risk is 0.

**Component 4: System Target Risk (by target resource)**

| Target Resource | Target Risk Score |
|----------------|-------------------|
| `email_system` | 1 |
| `calendar_system` | 1 |
| `config_system` | 2 |
| `payment_system` | 3 |
| `access_control` | 3 |
| `deployment_system` | 3 |
| `production_database` | 4 |

Default target risk for unlisted resources: 1.

**Risk Level Mapping:**

| Risk Level | Score Range |
|-----------|-------------|
| LOW | 0 - 4 |
| MEDIUM | 5 - 9 |
| HIGH | 10+ |

### 3.2 Policy Decision Types

After risk is computed, the policy engine evaluates the request against a set of policy rules. Each rule specifies a condition and a decision. Rules are evaluated in **priority order** (highest priority number wins).

The policy engine produces one of three decisions:

| Decision | Meaning | Pipeline Behavior |
|----------|---------|-------------------|
| `ALLOW` | The request is permitted without human approval. | Proceeds directly to the Execution Gate. An auto-authorization token is issued with `approver_id = "system_auto"`. |
| `REQUIRE_APPROVAL` | The request requires explicit human authorization before execution. | The request is placed in the approval queue. Execution is blocked until a human approver with sufficient authority issues an authorization token. |
| `DENY` | The request is prohibited by policy. | The request is immediately rejected. No authorization is sought. A denial receipt is generated and recorded in the ledger. The request does NOT proceed to the Authorization or Execution Gate stages. |

### 3.3 Policy Rule Structure

Each policy rule contains:

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique rule identifier (e.g., `POL-001`) |
| `description` | string | Human-readable description of the rule |
| `action` | string | The `action_type` this rule applies to |
| `role` | string (optional) | If present, the rule only applies to this role |
| `condition` | string (optional) | A condition expression (e.g., `amount > 1000`) |
| `decision` | string | `ALLOW`, `REQUIRE_APPROVAL`, or `DENY` |
| `priority` | integer | Higher priority rules override lower priority rules |

**Rule evaluation order:**

1. Filter rules to those matching the current `action_type`.
2. Among matching rules, filter by `role` (if the rule specifies a role, it only matches that role).
3. Among matching rules, evaluate `condition` expressions against the intent parameters.
4. The rule with the **highest priority** that matches all criteria determines the decision.
5. If no rule matches, the default decision is `DENY` (fail-closed).

### 3.4 Reference Policy Rules

| Rule ID | Action | Role | Condition | Decision | Priority |
|---------|--------|------|-----------|----------|----------|
| POL-001 | `transfer_funds` | any | `amount > 1000` | REQUIRE_APPROVAL | 10 |
| POL-002 | `delete_data` | any | none | REQUIRE_APPROVAL | 10 |
| POL-003 | `transfer_funds` | `intern` | none | DENY | 20 |
| POL-004 | `delete_data` | `intern` | none | DENY | 20 |
| POL-005 | `grant_access` | `intern` | none | DENY | 20 |
| POL-006 | `deploy_code` | any | none | REQUIRE_APPROVAL | 10 |
| POL-007 | `grant_access` | any | none | REQUIRE_APPROVAL | 10 |
| POL-008 | `transfer_funds` | any | `amount <= 1000` | ALLOW | 5 |

Note: POL-003 has priority 20 and POL-008 has priority 5. When an intern requests a transfer of any amount, POL-003 matches and wins because it has higher priority. This demonstrates the fail-closed design: restrictive rules override permissive rules.

### 3.5 Hard Stop Conditions

The following conditions cause an immediate halt in the pipeline, regardless of policy evaluation:

| Condition | Stage | Behavior |
|-----------|-------|----------|
| Kill switch (EKS-0) is engaged | Execution Gate | All execution is blocked. A receipt and ledger entry are generated recording the kill switch block. |
| Intent validation fails | Intent Validation | The request is rejected before reaching policy evaluation. A denial receipt is generated. |
| Self-authorization detected | Authorization | If the requester and approver are the same identity, the authorization is rejected (INV-06). |
| Authorization token expired | Execution Gate | The token is rejected. Execution is denied. |
| Authorization token already consumed | Execution Gate | The token is rejected. Execution is denied (INV-07). |

### 3.6 When Human Authorization Is Required

Human authorization is required when:

1. The policy engine returns `REQUIRE_APPROVAL` for the request.
2. The request is placed in the **approval queue** with all context: intent details, risk score, risk level, policy rule that triggered the escalation, and the requester's identity.
3. A human approver with sufficient authority reviews the request.
4. The approver MUST be a different identity than the requester (INV-06: No Self-Authorization).
5. The approver MUST have a role with sufficient authority for the action type and amount.

**Role-based approval authority:**

| Approver Role | Can Approve |
|---------------|-------------|
| `admin` | Any action, any amount |
| `manager` | Actions within their domain, transfers up to their authority limit |
| `employee` | Cannot approve (can only request) |
| `contractor` | Cannot approve |
| `intern` | Cannot approve |

### 3.7 Decision Output Format

The Policy & Risk evaluation produces a structured result:

```json
{
  "intent_id": "<UUID>",
  "decision": "ALLOW | REQUIRE_APPROVAL | DENY",
  "risk_score": 12.0,
  "risk_level": "HIGH",
  "policy_rule_id": "POL-001",
  "policy_ids": ["POL-001"],
  "constraints": {},
  "reason": "Fund transfers over 1000 require approval"
}
```

---

## 4. Execution Gate

The Execution Gate is the final checkpoint before any real-world action is performed. It is the enforcement point for multiple protocol invariants and the last line of defense against unauthorized execution.

### 4.1 Conditions Required Before Execution

The Execution Gate performs the following checks **in order**. If any check fails, execution is denied immediately.

| Check | Invariant | Failure Behavior |
|-------|-----------|-----------------|
| 1. Kill switch is not engaged | INV-08 | Deny execution. Generate receipt with reason `kill_switch_engaged`. |
| 2. Authorization token exists | INV-04 | Deny execution. No valid authorization. |
| 3. Authorization token signature is valid | INV-04 | Deny execution. Token may be forged. |
| 4. Authorization token has not expired | INV-04 | Deny execution. Token is stale. |
| 5. Authorization token has not been consumed | INV-07 | Deny execution. Token replay detected. |
| 6. Requester and approver are different identities | INV-06 | Deny execution. Self-authorization detected. |

### 4.2 What Is Checked Before Execution Is Allowed

After the six gate checks pass, the Execution Gate:

1. **Consumes the authorization token** by adding its `authorization_id` to the consumed token set. This is irreversible — the token can never be used again.
2. **Dispatches the action** to the appropriate execution backend (adapter, connector, or action handler).
3. **Records the execution result** including status, result data, and any external references.

### 4.3 What Causes Execution to Be Denied

| Cause | Error Type | Receipt Generated? | Ledger Entry? |
|-------|-----------|-------------------|---------------|
| Kill switch engaged | INV-08 violation | Yes (blocked) | Yes |
| No authorization token | Missing authorization | Yes (denied) | Yes |
| Invalid token signature | Token verification failure | Yes (denied) | Yes |
| Expired token | Token expired | Yes (denied) | Yes |
| Token already consumed | INV-07 violation | Yes (denied) | Yes |
| Self-authorization | INV-06 violation | Yes (denied) | Yes |
| Policy denial (upstream) | Policy DENY | Yes (denied) | Yes |
| Execution backend failure | Runtime error | Yes (failed) | Yes |

**Critical rule:** Every denial, block, and failure MUST produce a receipt and ledger entry. There is no silent failure path. This is INV-03 (Ledger Completeness).

### 4.4 Execution States and Transitions

The Execution Gate produces an execution result with one of the following statuses:

| Status | Meaning |
|--------|---------|
| `EXECUTED` | The action was successfully dispatched and completed. |
| `FAILED` | The action was dispatched but the execution backend reported a failure. |
| `BLOCKED` | The action was not dispatched because the Execution Gate denied it (kill switch, invalid token, policy denial). |

**Execution Result Structure:**

```json
{
  "intent_id": "<UUID>",
  "authorization_id": "<UUID>",
  "execution_status": "EXECUTED | FAILED | BLOCKED",
  "result_data": { ... },
  "timestamp": 1711461000000,
  "adapter_id": "<string>",
  "external_reference": "<string>"
}
```

The `result_data` object contains the output of the execution backend. For successful executions, it contains the action result. For failures, it contains an `error` field. For blocked executions, it contains the blocking reason.


---

## 5. Receipt Generation

Every governed action produces a cryptographic receipt, regardless of outcome. Approved, denied, and blocked requests all generate receipts. There is no execution path that avoids receipt generation. This is the foundation of the protocol's auditability guarantee.

### 5.1 Receipt JSON Structure (v2)

The v2 receipt contains the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `receipt_id` | string (UUID v4) | Yes | Unique identifier for this receipt. |
| `intent_id` | string (UUID v4) | Yes | Reference to the canonical intent this receipt covers. |
| `intent_hash` | string (SHA-256 hex) | Yes | SHA-256 hash of the canonical intent JSON (see Section 1.4). |
| `action` | string | Yes | The canonical action type from the intent. |
| `action_hash` | string (SHA-256 hex) | Yes | SHA-256 hash of the execution payload JSON. Empty string for denial receipts (no action executed). |
| `requested_by` | string | Yes | Identity of the entity that initiated the request. |
| `approved_by` | string | Yes | Identity of the entity that approved (or denied) the request. For auto-approved requests, this is `"system_auto"`. For validation failures, this is `"system:validation"`. |
| `decision` | string | Yes | `"approved"` or `"denied"`. |
| `timestamp_request` | string (ISO 8601) | Yes | UTC timestamp of when the original request was received. |
| `timestamp_approval` | string (ISO 8601) | Yes | UTC timestamp of when the approval/denial decision was made. |
| `timestamp_execution` | string (ISO 8601) | Conditional | UTC timestamp of when execution completed. Empty string for denial receipts. |
| `verification_status` | string | Yes | `"verified"`, `"failed"`, or `"skipped"`. Indicates whether post-execution verification was performed and its outcome. |
| `verification_hash` | string (SHA-256 hex) | Conditional | SHA-256 hash of the post-execution verification result. Empty string if verification was skipped. |
| `receipt_hash` | string (SHA-256 hex) | Yes | SHA-256 hash of the receipt itself (see Section 5.3). |
| `previous_hash` | string (SHA-256 hex) | Yes | Receipt hash of the immediately preceding receipt in the chain. Empty string for the genesis receipt. |
| `signature` | string (Base64) | Yes | RSA-PSS signature over the signing payload (see Section 5.4). |
| `request_id` | string (UUID v4) | Yes | Reference to the original request from intake. |
| `authorization_id` | string (UUID v4) | Conditional | Reference to the authorization token. Empty string for denial receipts that did not reach the authorization stage. |
| `execution_status` | string | Yes | `"EXECUTED"`, `"FAILED"`, or `"BLOCKED"`. |
| `risk_score` | number | No | Numeric risk score from the risk evaluation. |
| `risk_level` | string | No | Risk level string (`"LOW"`, `"MEDIUM"`, `"HIGH"`). |
| `policy_rule_id` | string | No | ID of the policy rule that determined the decision. |
| `policy_decision` | string | No | The raw policy decision string (e.g., `"ALLOW"`, `"DENY"`, `"APPROVED_BY_HUMAN"`). |
| `result_data` | object | No | The execution result payload or denial reason. |

### 5.2 Hash Computation Functions

**Intent Hash:**

```
Input:  { "intent_id", "action_type", "requested_by", "target_resource", "parameters" }
Method: JSON.serialize(input, sort_keys=true, default=str)
Hash:   SHA-256(UTF-8(serialized_json))
Output: Lowercase hex string (64 chars)
```

**Action Hash:**

```
Input:  The execution result payload (arbitrary JSON object)
Method: JSON.serialize(input, sort_keys=true, default=str)
Hash:   SHA-256(UTF-8(serialized_json))
Output: Lowercase hex string (64 chars)
```

**Verification Hash:**

```
Input:  The post-execution verification result (arbitrary JSON object)
Method: JSON.serialize(input, sort_keys=true, default=str)
Hash:   SHA-256(UTF-8(serialized_json))
Output: Lowercase hex string (64 chars)
```

All three hashes use the same canonicalization method: JSON serialization with sorted keys and string coercion for non-serializable types.

### 5.3 Receipt Hash Generation

The receipt hash covers the core immutable fields of the receipt (excluding the signature and extended fields):

```
Input fields (in this exact order within the JSON object):
  receipt_id, intent_id, intent_hash, action, action_hash,
  requested_by, approved_by, decision, timestamp_request,
  timestamp_approval, timestamp_execution, verification_status,
  verification_hash

Method:
  1. Construct a JSON object with exactly these 13 fields.
  2. Serialize with sorted keys: JSON.serialize(object, sort_keys=true)
  3. Concatenate the serialized JSON with the previous_hash:
     combined = serialized_json + previous_hash
  4. Compute: SHA-256(UTF-8(combined))

Output: Lowercase hex string (64 chars)
```

**Critical detail:** The `previous_hash` is concatenated AFTER the JSON serialization, not included within the JSON object. This means the receipt hash depends on both the receipt's own content and its position in the chain.

### 5.4 Receipt Signature

The receipt signature covers the critical decision chain fields. The signing payload is constructed by **direct string concatenation (no separator, no delimiter)** of these six fields in this exact order:

```
signing_payload = intent_hash + action_hash + decision + timestamp_execution + receipt_hash + previous_hash
```

| Position | Field | Example Value |
|----------|-------|---------------|
| 1 | `intent_hash` | `a3f2b1...` (64 hex chars) |
| 2 | `action_hash` | `7c9e4d...` (64 hex chars) |
| 3 | `decision` | `approved` or `denied` |
| 4 | `timestamp_execution` | `2026-03-26T14:30:00.000000+00:00` |
| 5 | `receipt_hash` | `e8b5a2...` (64 hex chars) |
| 6 | `previous_hash` | `d4c3b2...` (64 hex chars, or empty string for genesis) |

The signing payload is then signed using RSA-PSS (see Section 2.3 for algorithm parameters). The resulting signature is Base64-encoded and stored in the `signature` field.

### 5.5 When Receipts Are Created

Receipts are created at every possible pipeline exit point:

| Scenario | Receipt Type | Decision | Execution Status |
|----------|-------------|----------|-----------------|
| Action approved and executed successfully | Approval receipt | `"approved"` | `"EXECUTED"` |
| Action approved but execution failed | Approval receipt | `"approved"` | `"FAILED"` |
| Policy denied the action | Denial receipt | `"denied"` | `"BLOCKED"` |
| Intent validation failed | Denial receipt | `"denied"` | `"BLOCKED"` |
| Kill switch blocked the action | Denial receipt | `"denied"` | `"BLOCKED"` |
| Authorization token invalid/expired | Denial receipt | `"denied"` | `"BLOCKED"` |

**Denial receipts** have the following special characteristics:
- `action_hash` is empty string (no action was executed).
- `timestamp_execution` is empty string (no execution occurred).
- `verification_status` is `"skipped"` (no post-execution verification).
- `verification_hash` is empty string.
- `result_data` contains a `denial_reason` field explaining why the request was denied.

### 5.6 Post-Execution Verification

After successful execution (Stage 6) and before receipt generation (Stage 7), the protocol runs a post-execution verification step (Stage 6b). This step:

1. Verifies that the execution result is consistent with the intent.
2. Produces a verification result object.
3. Sets `verification_status` to `"verified"` (if checks pass) or `"failed"` (if checks fail).
4. Computes the `verification_hash` from the verification result.

If post-execution verification is not performed (e.g., for denied requests), `verification_status` is set to `"skipped"` and `verification_hash` is empty.

---

## 6. Ledger

The audit ledger is an append-only, hash-chained, cryptographically signed log of all governed actions. Every receipt — whether for an approved, denied, or blocked action — is recorded as a ledger entry. The ledger provides tamper-evident proof of the complete history of all decisions made by the system.

### 6.1 Ledger Entry Structure (v2)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ledger_entry_id` | string (UUID v4) | Yes | Unique identifier for this ledger entry. |
| `receipt_id` | string (UUID v4) | Yes | Reference to the receipt this entry records. |
| `receipt_hash` | string (SHA-256 hex) | Yes | Hash of the receipt, for cross-verification. |
| `intent_hash` | string (SHA-256 hex) | Yes | Copied from the receipt for direct ledger querying. |
| `action_hash` | string (SHA-256 hex) | Yes | Copied from the receipt. |
| `verification_hash` | string (SHA-256 hex) | Conditional | Copied from the receipt. Empty if verification was skipped. |
| `verification_status` | string | Yes | `"verified"`, `"failed"`, or `"skipped"`. |
| `decision` | string | Yes | `"approved"` or `"denied"`. |
| `action` | string | Yes | The canonical action type. |
| `requested_by` | string | Yes | Identity of the requester. |
| `approved_by` | string | Yes | Identity of the approver. |
| `timestamp_request` | string (ISO 8601) | Yes | When the request was received. |
| `timestamp_execution` | string (ISO 8601) | Conditional | When execution completed. Empty for denials. |
| `previous_ledger_hash` | string (SHA-256 hex) | Yes | Hash of the immediately preceding ledger entry. Empty string for the genesis entry. |
| `ledger_hash` | string (SHA-256 hex) | Yes | Hash of this ledger entry (see Section 6.3). |
| `ledger_signature` | string (Base64) | Yes | RSA-PSS signature over the `ledger_hash`. |
| `timestamp` | integer | Yes | Unix epoch milliseconds when this entry was appended. |

### 6.2 Hash Chaining Method

The ledger forms a singly-linked hash chain. Each entry's `previous_ledger_hash` field contains the `ledger_hash` of the immediately preceding entry. This creates a tamper-evident chain where modifying any entry invalidates all subsequent entries.

```
Entry 0 (Genesis):
  previous_ledger_hash = ""  (empty string)
  ledger_hash = SHA-256(entry_0_fields)

Entry 1:
  previous_ledger_hash = entry_0.ledger_hash
  ledger_hash = SHA-256(entry_1_fields)

Entry N:
  previous_ledger_hash = entry_(N-1).ledger_hash
  ledger_hash = SHA-256(entry_N_fields)
```

**Genesis entry rule:** The first entry in the ledger MUST have an empty string as its `previous_ledger_hash`. Any entry claiming to be the genesis with a non-empty `previous_ledger_hash` is invalid.

### 6.3 How the Ledger Hash Is Computed

The v2 ledger hash is computed by **direct string concatenation (no separator)** of the following fields in this exact order:

```
data = ledger_entry_id
     + receipt_id
     + receipt_hash
     + intent_hash
     + action_hash
     + verification_hash
     + verification_status
     + decision
     + action
     + requested_by
     + approved_by
     + previous_ledger_hash
     + timestamp (integer converted to string)

ledger_hash = SHA-256(UTF-8(data))
```

**Field order is critical.** The fields are concatenated in exactly the order listed above. Reordering fields will produce a different hash.

**The `timestamp` field** is the integer epoch milliseconds value, converted to its string representation (e.g., `1711461000000` becomes the string `"1711461000000"`).

### 6.4 Ledger Entry Signature

The ledger entry is signed using the same RSA-PSS algorithm as receipts (see Section 2.3). The signing payload is the `ledger_hash` string itself:

```
signing_payload = ledger_hash  (the 64-char hex string)
signature = RSA-PSS-Sign(private_key, UTF-8(signing_payload))
ledger_signature = Base64-Encode(signature)
```

### 6.5 Ledger Verification Process

To verify the integrity of the entire ledger, perform these checks on every entry in sequence:

**For each entry at index `i`:**

1. **Hash verification:** Recompute the `ledger_hash` using the formula in Section 6.3. Compare with the stored `ledger_hash`. If they differ, the entry has been tampered with.

2. **Signature verification:** Verify the `ledger_signature` against the `ledger_hash` using the RSA public key and PSS parameters from Section 2.3. If verification fails, the entry's signature is invalid.

3. **Chain link verification:**
   - If `i == 0` (genesis): `previous_ledger_hash` MUST be empty string.
   - If `i > 0`: `previous_ledger_hash` MUST equal `ledger[i-1].ledger_hash`.
   - If the chain link is broken, the ledger has been tampered with (entry inserted, deleted, or reordered).

4. **Receipt linkage verification:** The `receipt_hash` in the ledger entry MUST match the `receipt_hash` of the referenced receipt. This ensures the ledger accurately records the receipt it claims to record.

**Verification result:**

The verification produces a summary:
- `chain_intact`: boolean — true only if ALL entries pass ALL checks.
- `entries_verified`: integer — count of entries that passed all checks.
- `entries_total`: integer — total entries in the ledger.
- `failures`: list of strings — descriptions of any failures.

### 6.6 Append-Only Guarantee

The ledger is strictly append-only. The following operations are prohibited:

- **No updates:** Once an entry is appended, its fields cannot be modified.
- **No deletions:** Entries cannot be removed from the ledger.
- **No reordering:** The order of entries is fixed by the hash chain.

Any implementation MUST enforce these constraints. In the reference implementation, the ledger is an in-memory list with only an `append` operation exposed. A production implementation MUST use a durable store with equivalent guarantees (e.g., append-only database table with hash chain validation on insert).

---

## 7. State Machine

The RIO protocol defines a deterministic state machine that governs the lifecycle of every request. Each request transitions through a fixed sequence of states, with well-defined transition rules and no ambiguous states.

### 7.1 All System States

| State | Description | Produced By |
|-------|-------------|-------------|
| `submitted` | Request received at intake, assigned a `request_id`. | Stage 1: Intake |
| `classified` | Action type and risk category determined. | Stage 2: Classification |
| `validation_failed` | Intent validation found missing or invalid fields. Terminal state. | Stage 3a: Intent Validation |
| `validated` | All required fields present and consistent. | Stage 3a: Intent Validation |
| `intent_formed` | Canonical intent envelope constructed. | Stage 3b: Structured Intent |
| `policy_evaluated` | Risk score computed, policy decision rendered. | Stage 4: Policy & Risk |
| `awaiting_human_authorization` | Policy requires human approval. Pipeline halted. | Stage 4: Policy & Risk (ESCALATE) |
| `denied_by_policy` | Policy explicitly denied the request. Terminal state. | Stage 4: Policy & Risk (DENY) |
| `authorized` | Authorization token issued (auto or human). | Stage 5: Authorization |
| `authorization_failed` | Authorization check failed (self-auth, expired token, consumed token). Terminal state. | Stage 5/6: Authorization / Execution Gate |
| `executed` | Action dispatched and completed successfully. | Stage 6: Execution Gate |
| `execution_failed` | Action dispatched but execution backend reported failure. Terminal state. | Stage 6: Execution Gate |
| `kill_switch_blocked` | Kill switch (EKS-0) prevented execution. Terminal state. | Stage 6: Execution Gate |
| `verified` | Post-execution verification passed. | Stage 6b: Verification |
| `verification_failed` | Post-execution verification detected inconsistency. | Stage 6b: Verification |
| `receipted` | Cryptographic receipt generated and signed. | Stage 7: Receipt |
| `ledgered` | Receipt recorded in the audit ledger. | Stage 8: Ledger |

### 7.2 Valid State Transitions

The following diagram shows all valid state transitions. Each arrow represents a single pipeline stage transition.

```
submitted
  │
  ▼
classified
  │
  ├──► validation_failed ──► receipted ──► ledgered  [TERMINAL]
  │
  ▼
validated
  │
  ▼
intent_formed
  │
  ▼
policy_evaluated
  │
  ├──► denied_by_policy ──► receipted ──► ledgered  [TERMINAL]
  │
  ├──► awaiting_human_authorization  [PAUSED — resumes on approval]
  │       │
  │       ▼
  │     authorized  (when human approves)
  │       │
  │       ▼  (continues to execution gate below)
  │
  ▼
authorized  (auto-authorization for ALLOW decisions)
  │
  ├──► kill_switch_blocked ──► receipted ──► ledgered  [TERMINAL]
  │
  ├──► authorization_failed ──► receipted ──► ledgered  [TERMINAL]
  │
  ▼
executed  (or execution_failed)
  │
  ▼
verified  (or verification_failed, or verification skipped)
  │
  ▼
receipted
  │
  ▼
ledgered  [TERMINAL — pipeline complete]
```

### 7.3 Invalid Transitions

The following transitions are explicitly prohibited:

| From | To | Reason |
|------|----|--------|
| Any state | `submitted` | A request cannot re-enter the pipeline. |
| `denied_by_policy` | `authorized` | A denied request cannot be authorized. |
| `kill_switch_blocked` | `executed` | A kill-switch block cannot be overridden within the same pipeline run. |
| `executed` | `authorized` | Execution cannot revert to authorization. |
| `ledgered` | Any state | Once ledgered, the pipeline is complete. No further transitions. |
| `authorization_failed` | `executed` | A failed authorization cannot proceed to execution. |
| `validation_failed` | `intent_formed` | A failed validation cannot produce a valid intent. |
| Any terminal state | Any non-terminal state | Terminal states are final. The only forward transition from a terminal state is to `receipted` and then `ledgered`. |

**Key invariant:** Every request that enters the pipeline MUST eventually reach the `ledgered` state. There is no exit path that avoids receipt generation and ledger recording. This is the combined effect of INV-02 (Receipt Completeness) and INV-03 (Ledger Completeness).

### 7.4 Global System State

In addition to per-request state, the protocol maintains global system state:

| State Variable | Type | Description |
|---------------|------|-------------|
| `kill_switch_active` | boolean | Whether EKS-0 is currently engaged. |
| `kill_switch_engaged_by` | string | Identity of the actor who engaged the kill switch. |
| `kill_switch_engaged_at` | integer (epoch ms) | When the kill switch was engaged. |
| `consumed_tokens` | set of strings | Set of `authorization_id` values that have been consumed. |
| `token_registry` | map | Tracking metadata for all issued authorization tokens. |
| `ledger_head_hash` | string | Hash of the most recent ledger entry. |
| `ledger_length` | integer | Number of entries in the ledger. |
| `policy_version` | string | Version identifier for the active policy set. |
| `risk_model_version` | string | Version identifier for the active risk model. |

### 7.5 Kill Switch (EKS-0) State Machine

The kill switch has its own two-state machine:

```
DISENGAGED ──[engage(actor_id, reason)]──► ENGAGED
ENGAGED ──[disengage(actor_id, reason)]──► DISENGAGED
```

**Engage precondition:** Kill switch MUST NOT already be engaged. Attempting to engage an already-engaged kill switch raises an error.

**Disengage precondition:** Kill switch MUST be currently engaged. Attempting to disengage an already-disengaged kill switch raises an error.

**Effect of engagement:** When `kill_switch_active` is `true`, the Execution Gate MUST block ALL executions, regardless of authorization status. The block produces a receipt and ledger entry with `execution_status = "KILL_SWITCH_BLOCKED"`.

---

## 8. Error Codes and Failure Conditions

The RIO protocol defines a set of invariants that serve as the protocol's error detection and enforcement system. Each invariant has a unique identifier and defines a specific condition that must hold true at all times.

### 8.1 Protocol Invariants

| Invariant ID | Name | Description | Enforcement Point |
|-------------|------|-------------|-------------------|
| **INV-01** | Completeness | Every request that enters the pipeline must produce all required artifacts (intent, authorization decision, receipt, ledger entry). | Post-pipeline verification |
| **INV-02** | Receipt Completeness | Every governed action must produce a receipt with a valid `receipt_id`, `receipt_hash`, and `signature`. | Post-pipeline verification |
| **INV-03** | Ledger Completeness | Every receipt must be appended to the audit ledger. The ledger entry must reference the correct `receipt_id` and have a valid `ledger_hash`. | Post-pipeline verification |
| **INV-04** | Hash Chain Integrity | Each ledger entry's `previous_ledger_hash` must match the `ledger_hash` of the immediately preceding entry. | Ledger append and verification |
| **INV-05** | Learning Separation | The governance learning loop must not bypass runtime enforcement. Learning processes may only produce recommendations; they cannot directly execute actions. | Pipeline entry point |
| **INV-06** | No Self-Authorization | The requester and the authorizer must be distinct identities. An AI agent cannot authorize its own requests. | Authorization stage |
| **INV-07** | Single-Use Authorization | Each authorization token may be consumed exactly once. A consumed token must never be accepted again. | Execution Gate |
| **INV-08** | Kill Switch Override | When the kill switch (EKS-0) is engaged, no execution may proceed regardless of authorization status. | Execution Gate |

### 8.2 What Triggers Each Error

| Invariant | Trigger Condition | Detection Method |
|-----------|-------------------|-----------------|
| INV-01 | A request completes the pipeline but one or more required artifacts (intent_id, authorization_id, receipt_id, receipt_hash, receipt_signature, ledger_entry_id, ledger_hash) are missing or empty. | Check all artifact fields after pipeline completion. |
| INV-02 | A receipt is generated but its `receipt_id` is empty, its `receipt_hash` is empty, or its `signature` is empty. | Check receipt fields after receipt generation. |
| INV-03 | A receipt was generated but the corresponding ledger entry either does not exist or references a different `receipt_id`. | Compare `ledger_entry.receipt_id` with `receipt.receipt_id` after ledger append. |
| INV-04 | A ledger entry's `previous_ledger_hash` does not match the `ledger_hash` of the entry at position `index - 1` in the ledger. | Compare hashes during ledger append and during full chain verification. |
| INV-05 | A process operating in a learning/recommendation context attempts to execute an action through the pipeline. | Check the `is_learning_context` flag at pipeline entry. If true and execution is attempted, the invariant is violated. |
| INV-06 | The `intent.requested_by` field matches the `authorization.approver_id` field. | String equality check during authorization. |
| INV-07 | The `authorization.authorization_id` is found in the `consumed_tokens` set in the system state. | Set membership check at the Execution Gate before consuming the token. |
| INV-08 | The `state.kill_switch_active` flag is `true` when the Execution Gate is about to dispatch an action. | Boolean check at the Execution Gate. |

### 8.3 What the System Must Do When Each Error Occurs

| Invariant | Required System Response |
|-----------|------------------------|
| INV-01 | Log the violation. Set `result.error` to describe the missing artifacts. The pipeline result is marked as failed. The violation is recorded in the governed corpus. |
| INV-02 | Raise an `InvariantViolation` exception with code `"INV-02"` and a message identifying the missing field. The pipeline catches this and records it in the result. |
| INV-03 | Raise an `InvariantViolation` exception with code `"INV-03"` and a message identifying the mismatch. The pipeline catches this and records it in the result. |
| INV-04 | Raise an `InvariantViolation` exception with code `"INV-04"` and a message showing the expected vs. actual `previous_ledger_hash`. During full chain verification, this is reported as a chain break. |
| INV-05 | Raise an `InvariantViolation` exception with code `"INV-05"` and a message stating that the learning loop attempted to execute an action. The action is blocked. |
| INV-06 | Raise an `InvariantViolation` exception with code `"INV-06"` identifying the requester and approver. The authorization is rejected. A denial receipt is generated. |
| INV-07 | Raise an `InvariantViolation` exception with code `"INV-07"` identifying the consumed token. The execution is denied. A denial receipt is generated. In the system state, the `consumed_tokens` set already contains the token, confirming it was previously used. |
| INV-08 | Raise an `InvariantViolation` exception with code `"INV-08"` stating that the kill switch is engaged. All execution is halted. A receipt with `execution_status = "KILL_SWITCH_BLOCKED"` is generated and recorded in the ledger. |

### 8.4 Fail-Closed Design Principle

The RIO protocol operates on a **fail-closed** principle: if any check fails, if any invariant is violated, if any component is unavailable, the default behavior is to **deny execution**. There is no fail-open path.

Specific manifestations of fail-closed:

- If no policy rule matches a request, the default decision is `DENY`.
- If the kill switch state cannot be determined, execution is blocked.
- If the signature key is unavailable, receipts cannot be signed, and the pipeline halts.
- If the ledger cannot be appended to, the pipeline reports an error (the receipt still exists but the ledger completeness invariant is violated).
- If the authorization token cannot be verified, execution is denied.

### 8.5 Complete Pipeline Stage Map

For reference, the complete 8-stage pipeline with sub-stages:

| Stage | Name | Produces | Can Fail? | Failure Generates Receipt? |
|-------|------|----------|-----------|---------------------------|
| 1 | Intake | `Request` | Yes (missing actor) | No (pre-intent) |
| 2 | Classification | `ClassificationResult` | Yes (no action_type) | No (pre-intent) |
| 3a | Intent Validation | `ValidationResult` | Yes (missing fields) | Yes (denial receipt) |
| 3b | Structured Intent | `Intent` | No (always succeeds if 3a passes) | N/A |
| 4 | Policy & Risk | `PolicyRiskResult` | Yes (DENY decision) | Yes (denial receipt) |
| 4b | Approval Queue | `ApprovalRequest` | No (queue always accepts) | No (pipeline paused) |
| 5 | Authorization | `Authorization` | Yes (INV-06, INV-07) | Yes (denial receipt) |
| 6 | Execution Gate | `ExecutionResult` | Yes (INV-08, backend failure) | Yes (always) |
| 6b | Post-Execution Verification | Verification result | Yes (verification_failed) | N/A (recorded in receipt) |
| 7 | Receipt (v1 + v2) | `Receipt` / `ReceiptV2` | No (always succeeds) | N/A (this IS the receipt) |
| 8 | Ledger (v1 + v2) | `LedgerEntry` / `LedgerEntryV2` | Rare (storage failure) | N/A (this IS the ledger) |

---

## Appendix A: Complete JSON Schemas

### A.1 Canonical Intent Envelope (Request Schema)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Canonical Request",
  "type": "object",
  "required": [
    "request_id", "requested_by", "requested_at", "action_type",
    "target", "parameters", "business_reason", "risk_context", "policy_context"
  ],
  "properties": {
    "request_id": { "type": "string", "format": "uuid" },
    "requested_by": {
      "type": "object",
      "required": ["entity_id", "entity_type"],
      "properties": {
        "entity_id": { "type": "string" },
        "entity_type": { "type": "string", "enum": ["human", "ai_agent", "system"] },
        "display_name": { "type": "string" },
        "role": { "type": "string" }
      }
    },
    "requested_at": { "type": "string", "format": "date-time" },
    "action_type": { "type": "string" },
    "target": {
      "type": "object",
      "required": ["resource_type", "resource_id"],
      "properties": {
        "resource_type": { "type": "string" },
        "resource_id": { "type": "string" }
      }
    },
    "parameters": { "type": "object" },
    "business_reason": {
      "type": "object",
      "required": ["summary"],
      "properties": {
        "summary": { "type": "string" },
        "justification": { "type": "string" },
        "supporting_references": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["reference_type", "reference_id"],
            "properties": {
              "reference_type": { "type": "string" },
              "reference_id": { "type": "string" }
            }
          }
        }
      }
    },
    "risk_context": {
      "type": "object",
      "required": ["risk_level"],
      "properties": {
        "risk_level": { "type": "string", "enum": ["low", "medium", "high", "critical"] },
        "risk_factors": { "type": "array", "items": { "type": "string" } },
        "financial_impact": {
          "type": "object",
          "required": ["currency", "amount"],
          "properties": {
            "currency": { "type": "string" },
            "amount": { "type": "number" }
          }
        },
        "reversibility": { "type": "string", "enum": ["reversible", "partially_reversible", "irreversible"] }
      }
    },
    "policy_context": {
      "type": "object",
      "required": ["requires_authorization"],
      "properties": {
        "applicable_policies": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["policy_id"],
            "properties": {
              "policy_id": { "type": "string" },
              "policy_name": { "type": "string" },
              "version": { "type": "string" }
            }
          }
        },
        "requires_authorization": { "type": "boolean" },
        "authorization_type": { "type": "string", "enum": ["none", "single_approver", "multi_approver", "escalation"] },
        "constraints": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["constraint_type"],
            "properties": {
              "constraint_type": { "type": "string" },
              "description": { "type": "string" },
              "value": {}
            }
          }
        }
      }
    }
  },
  "additionalProperties": false
}
```

### A.2 Authorization Token Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Authorization Token",
  "type": "object",
  "required": [
    "authorization_id", "intent_id", "decision", "approver_id",
    "approval_timestamp", "expiration_timestamp", "single_use", "signature"
  ],
  "properties": {
    "authorization_id": { "type": "string", "format": "uuid" },
    "intent_id": { "type": "string", "format": "uuid" },
    "decision": { "type": "string", "enum": ["ALLOW", "DENY"] },
    "approver_id": { "type": "string" },
    "approval_timestamp": { "type": "integer" },
    "expiration_timestamp": { "type": "integer" },
    "single_use": { "type": "boolean" },
    "signature": { "type": "string" }
  },
  "additionalProperties": false
}
```

### A.3 v2 Receipt Schema

```json
{
  "title": "Receipt v2",
  "type": "object",
  "required": [
    "receipt_id", "intent_id", "intent_hash", "action", "decision",
    "requested_by", "approved_by", "timestamp_request", "verification_status",
    "receipt_hash", "previous_hash", "signature"
  ],
  "properties": {
    "receipt_id": { "type": "string", "format": "uuid" },
    "intent_id": { "type": "string", "format": "uuid" },
    "intent_hash": { "type": "string", "description": "SHA-256 hex" },
    "action": { "type": "string" },
    "action_hash": { "type": "string" },
    "requested_by": { "type": "string" },
    "approved_by": { "type": "string" },
    "decision": { "type": "string", "enum": ["approved", "denied"] },
    "timestamp_request": { "type": "string", "format": "date-time" },
    "timestamp_approval": { "type": "string", "format": "date-time" },
    "timestamp_execution": { "type": "string", "format": "date-time" },
    "verification_status": { "type": "string", "enum": ["verified", "failed", "skipped"] },
    "verification_hash": { "type": "string" },
    "receipt_hash": { "type": "string" },
    "previous_hash": { "type": "string" },
    "signature": { "type": "string" },
    "request_id": { "type": "string" },
    "authorization_id": { "type": "string" },
    "execution_status": { "type": "string", "enum": ["EXECUTED", "FAILED", "BLOCKED"] },
    "risk_score": { "type": "number" },
    "risk_level": { "type": "string" },
    "policy_rule_id": { "type": "string" },
    "policy_decision": { "type": "string" },
    "result_data": { "type": "object" }
  },
  "additionalProperties": false
}
```

### A.4 v2 Ledger Entry Schema

```json
{
  "title": "Ledger Entry v2",
  "type": "object",
  "required": [
    "ledger_entry_id", "receipt_id", "receipt_hash", "previous_ledger_hash",
    "ledger_hash", "ledger_signature", "timestamp"
  ],
  "properties": {
    "ledger_entry_id": { "type": "string", "format": "uuid" },
    "receipt_id": { "type": "string", "format": "uuid" },
    "receipt_hash": { "type": "string" },
    "intent_hash": { "type": "string" },
    "action_hash": { "type": "string" },
    "verification_hash": { "type": "string" },
    "verification_status": { "type": "string", "enum": ["verified", "failed", "skipped"] },
    "decision": { "type": "string", "enum": ["approved", "denied"] },
    "action": { "type": "string" },
    "requested_by": { "type": "string" },
    "approved_by": { "type": "string" },
    "timestamp_request": { "type": "string" },
    "timestamp_execution": { "type": "string" },
    "previous_ledger_hash": { "type": "string" },
    "ledger_hash": { "type": "string" },
    "ledger_signature": { "type": "string" },
    "timestamp": { "type": "integer" }
  },
  "additionalProperties": false
}
```

---

## Appendix B: Worked Example — End-to-End Pipeline Trace

This appendix traces a single request through the complete pipeline to illustrate every stage, hash computation, and data transformation.

**Scenario:** User `alice` (role: `employee`) requests to transfer $5,000 from `acct_001` to `vendor_corp`. The policy requires human approval for transfers over $1,000. Manager `bob` approves the request.

**Stage 1: Intake**

```json
{
  "request_id": "req-001",
  "actor_id": "alice",
  "raw_input": {
    "action_type": "transfer_funds",
    "target_resource": "payment_system",
    "requested_by": "alice",
    "parameters": {
      "amount": 5000,
      "currency": "USD",
      "recipient": "vendor_corp",
      "source_account": "acct_001"
    },
    "justification": "Quarterly vendor payment"
  },
  "timestamp": 1711461000000,
  "authenticated": true
}
```

**Stage 2: Classification**

- `action_type`: `"transfer_funds"`
- `risk_category`: `HIGH` (from default classification rules)

**Stage 3a: Intent Validation**

- Required parameters for `transfer_funds`: `amount`, `currency`, `recipient`, `source_account` — all present.
- Validation: PASSED.

**Stage 3b: Structured Intent**

```json
{
  "intent_id": "int-001",
  "request_id": "req-001",
  "action_type": "transfer_funds",
  "target_resource": "payment_system",
  "parameters": { "amount": 5000, "currency": "USD", "recipient": "vendor_corp", "source_account": "acct_001" },
  "requested_by": "alice",
  "justification": "Quarterly vendor payment",
  "risk_category": "HIGH"
}
```

**Stage 4: Policy & Risk**

Risk computation:
- Base risk (`transfer_funds`): 5
- Role risk (`employee`): 3
- Amount risk ($5,000 is in $1,000-$9,999 range): 3
- System target risk (`payment_system`): 3
- **Total risk score: 14 → HIGH**

Policy evaluation:
- POL-001 matches: `transfer_funds` with `amount > 1000` → `REQUIRE_APPROVAL` (priority 10)
- Decision: `REQUIRE_APPROVAL`

**Pipeline pauses — request enters approval queue.**

**Human approval:** Manager `bob` reviews and approves the request.

**Stage 5: Authorization**

```json
{
  "authorization_id": "auth-001",
  "intent_id": "int-001",
  "decision": "ALLOW",
  "approver_id": "bob",
  "approval_timestamp": 1711461300000,
  "expiration_timestamp": 1711461600000,
  "single_use": true
}
```

INV-06 check: `alice` != `bob` — PASSED.

**Stage 6: Execution Gate**

- INV-08 check: Kill switch not engaged — PASSED.
- Token not expired: current time < 1711461600000 — PASSED.
- INV-07 check: `auth-001` not in consumed tokens — PASSED.
- Token consumed: `auth-001` added to consumed set.
- Action dispatched to payment system adapter.
- Execution status: `EXECUTED`.

**Stage 6b: Post-Execution Verification**

- Verification checks pass.
- `verification_status`: `"verified"`.

**Stage 7: Receipt Generation**

- `intent_hash`: SHA-256 of canonical intent JSON.
- `action_hash`: SHA-256 of execution result JSON.
- `receipt_hash`: SHA-256 of 13-field JSON + previous_hash.
- `signing_payload`: intent_hash + action_hash + "approved" + timestamp_execution + receipt_hash + previous_hash.
- `signature`: RSA-PSS sign of signing_payload.

**Stage 8: Ledger**

- `ledger_hash`: SHA-256 of 13-field concatenation.
- `previous_ledger_hash`: hash of the prior ledger entry (or empty if genesis).
- `ledger_signature`: RSA-PSS sign of ledger_hash.
- Entry appended to ledger.

**Pipeline complete.** Result: `success = true`.
