# RIO Protocol — Execution Envelope Specification

**Version:** 1.0.0
**Status:** Normative
**Protocol Reference:** 07 — Execution Protocol

---

## 1. Overview

The execution envelope defines the bounded constraints within which an authorized action may be performed. It is the set of runtime limits that the execution gate enforces before, during, and after action execution. The envelope ensures that even after authorization, the actual execution cannot exceed the scope, duration, tools, parameters, or network boundaries that were approved.

The execution envelope is constructed from three sources:
1. **Authorization record conditions** — constraints set by the authorizer.
2. **Policy-derived constraints** — constraints imposed by the policy engine.
3. **System defaults** — baseline constraints from the system manifest.

The most restrictive constraint from any source takes precedence.

---

## 2. Envelope Fields

### 2.1 Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `envelope_id` | string (UUID v4) | Yes | Unique identifier for this envelope instance |
| `authorization_id` | string (UUID v4) | Yes | The authorization record this envelope is derived from |
| `request_id` | string (UUID v4) | Yes | The canonical request this envelope governs |
| `allowed_tools` | array of strings | Yes | List of permitted tools, APIs, or services the execution may invoke |
| `parameter_constraints` | object | Yes | Per-parameter bounds (min, max, enum, pattern) |
| `timeout_seconds` | integer | Yes | Maximum wall-clock duration for execution. MUST be > 0. |
| `max_retries` | integer | Yes | Maximum number of retry attempts on transient failure. 0 = no retries. |
| `rollback_plan` | object | Yes | Required rollback procedure if execution fails |
| `kill_switch` | object | Yes | Conditions that trigger immediate execution termination |
| `scope_boundary` | object | Yes | Systems, resources, and data the execution may access |
| `network_boundary` | object | Yes | Allowed network destinations and protocols |
| `created_at` | string (ISO 8601) | Yes | Timestamp of envelope creation |
| `expires_at` | string (ISO 8601) | Yes | MUST match or precede `authorization_record.expires_at` |

### 2.2 Allowed Tools

The `allowed_tools` field is an explicit allowlist. The execution MUST NOT invoke any tool, API, or service not listed in this array.

```json
{
  "allowed_tools": [
    "banking.wire_transfer.send",
    "banking.wire_transfer.status",
    "notification.email.send"
  ]
}
```

**Rules:**
- Tool names MUST follow the intent ontology naming convention (`<class>.<verb>.<object>`).
- Wildcard patterns are NOT permitted. Each tool MUST be explicitly listed.
- An empty `allowed_tools` array means no tools are permitted — the execution gate MUST deny execution.

### 2.3 Parameter Constraints

The `parameter_constraints` field defines per-parameter bounds that the execution MUST NOT exceed.

```json
{
  "parameter_constraints": {
    "amount": {
      "type": "number",
      "min": 0,
      "max": 48250.00,
      "currency": "USD"
    },
    "recipient_account": {
      "type": "string",
      "pattern": "^[0-9]{8,17}$",
      "exact_match": "7782019843"
    },
    "recipient_name": {
      "type": "string",
      "exact_match": "Meridian Industrial Supply LLC"
    },
    "transfer_type": {
      "type": "string",
      "enum": ["domestic_wire"]
    }
  }
}
```

**Constraint types:**

| Constraint | Applies To | Description |
|-----------|-----------|-------------|
| `min` | number | Minimum allowed value (inclusive) |
| `max` | number | Maximum allowed value (inclusive) |
| `enum` | string | List of allowed values |
| `pattern` | string | Regex pattern the value MUST match |
| `exact_match` | string, number | Value MUST equal this exactly |
| `max_length` | string | Maximum character length |
| `not_null` | any | Value MUST NOT be null or empty |

### 2.4 Timeout

```json
{
  "timeout_seconds": 120
}
```

**Rules:**
- The execution gate MUST terminate execution if `timeout_seconds` is exceeded.
- The timeout clock starts when the execution gate releases the action.
- Timeout MUST be ≤ the remaining time in the authorization window (`expires_at - current_time`).
- If the authorization has 60 seconds remaining, `timeout_seconds` MUST NOT exceed 60.

### 2.5 Max Retries

```json
{
  "max_retries": 1
}
```

**Rules:**
- Retries are only permitted for transient failures (network timeout, temporary service unavailability).
- Retries MUST NOT be attempted for authorization failures, parameter violations, or business logic errors.
- Each retry uses the same `execution_id` and `authorization_id`.
- The retry count MUST be recorded in the execution record.
- Total execution time across all retries MUST NOT exceed `timeout_seconds`.

### 2.6 Rollback Plan

The rollback plan defines the procedure to reverse or compensate for a failed execution.

```json
{
  "rollback_plan": {
    "rollback_type": "compensating_action",
    "rollback_tool": "banking.wire_transfer.cancel",
    "rollback_parameters": {
      "original_confirmation_id": "${execution.result.confirmation_id}"
    },
    "rollback_timeout_seconds": 60,
    "rollback_requires_authorization": false,
    "manual_fallback": "Contact treasury operations at +1-555-0142 to manually reverse the wire transfer."
  }
}
```

**Rollback types:**

| Type | Description |
|------|-------------|
| `compensating_action` | Execute a reverse action (e.g., cancel wire, revoke access) |
| `idempotent_retry` | Re-execute the same action (safe for idempotent operations) |
| `manual_intervention` | Human must perform the rollback manually |
| `no_rollback` | Action is irreversible; flag for incident review |

**Rules:**
- Every execution envelope MUST include a rollback plan.
- If `rollback_type` is `no_rollback`, the `manual_fallback` field MUST be populated.
- Rollback execution is itself recorded in the ledger as a separate decision chain.

### 2.7 Kill Switch

The kill switch defines conditions that trigger immediate, unconditional termination of execution.

```json
{
  "kill_switch": {
    "conditions": [
      {
        "condition_id": "KS-001",
        "trigger": "parameter_deviation",
        "description": "Execution attempts to send amount different from authorized amount",
        "threshold": "amount != 48250.00"
      },
      {
        "condition_id": "KS-002",
        "trigger": "unauthorized_tool_invocation",
        "description": "Execution attempts to invoke a tool not in allowed_tools",
        "threshold": "tool NOT IN allowed_tools"
      },
      {
        "condition_id": "KS-003",
        "trigger": "timeout_exceeded",
        "description": "Execution exceeds timeout_seconds",
        "threshold": "elapsed_time > 120"
      },
      {
        "condition_id": "KS-004",
        "trigger": "scope_violation",
        "description": "Execution attempts to access a system outside scope_boundary",
        "threshold": "target_system NOT IN scope_boundary.allowed_systems"
      },
      {
        "condition_id": "KS-005",
        "trigger": "network_violation",
        "description": "Execution attempts to reach a network destination outside network_boundary",
        "threshold": "destination NOT IN network_boundary.allowed_destinations"
      }
    ],
    "termination_behavior": "immediate_halt",
    "post_termination": [
      "Record execution_status as 'cancelled'",
      "Record kill_switch condition that triggered",
      "Execute rollback_plan if applicable",
      "Generate incident record",
      "Write ledger entry"
    ]
  }
}
```

**Rules:**
- Kill switch evaluation is continuous during execution, not just at start.
- Kill switch termination is immediate — no grace period.
- Kill switch activation MUST be recorded in the execution record with the triggering condition.

### 2.8 Scope Boundary

```json
{
  "scope_boundary": {
    "allowed_systems": [
      "core-banking-api.internal",
      "notification-service.internal"
    ],
    "allowed_databases": [],
    "allowed_file_paths": [],
    "allowed_resources": [
      "account:7782019843",
      "account:sender-operating-001"
    ],
    "denied_systems": [
      "hr-system.internal",
      "admin-console.internal"
    ]
  }
}
```

**Rules:**
- `allowed_systems` is an explicit allowlist. Any system not listed is denied.
- `denied_systems` takes precedence over `allowed_systems` if both match (defense in depth).
- An empty `allowed_systems` array means no systems are accessible — execution gate MUST deny.

### 2.9 Network Boundary

```json
{
  "network_boundary": {
    "allowed_destinations": [
      "core-banking-api.internal:443",
      "notification-service.internal:443"
    ],
    "allowed_protocols": ["https"],
    "denied_destinations": [
      "*.external.com",
      "0.0.0.0/0"
    ],
    "egress_allowed": false
  }
}
```

**Rules:**
- `egress_allowed: false` means no outbound internet traffic is permitted.
- `allowed_destinations` is an explicit allowlist for internal network targets.
- `denied_destinations` takes precedence over `allowed_destinations`.

---

## 3. Envelope Validation

The execution gate MUST perform the following validation checks before releasing execution:

| # | Check | Condition | Failure Action |
|---|-------|-----------|----------------|
| 1 | Authorization valid | `authorization_record.decision` is `approve` or `approve_with_conditions` | Deny execution |
| 2 | Authorization not expired | `current_time < authorization_record.expires_at` | Deny execution |
| 3 | Envelope not expired | `current_time < envelope.expires_at` | Deny execution |
| 4 | Single use | `authorization_id` has not been used for a prior execution | Deny execution |
| 5 | Signature valid | `authorization_record.signature` verifies | Deny execution |
| 6 | Tools populated | `allowed_tools` is non-empty | Deny execution |
| 7 | Timeout valid | `timeout_seconds > 0` AND `timeout_seconds ≤ remaining_authorization_time` | Deny execution |
| 8 | Rollback plan present | `rollback_plan` is non-null and valid | Deny execution |
| 9 | Kill switch defined | `kill_switch.conditions` is non-empty | Deny execution |
| 10 | Parameter constraints match | All execution parameters satisfy `parameter_constraints` | Deny execution |

All 10 checks MUST pass. If any check fails, the execution gate MUST deny execution and record the failure.

---

## 4. Envelope Violations

When execution violates the envelope at runtime:

### 4.1 Violation Types

| Violation | Trigger | Severity |
|-----------|---------|----------|
| Parameter deviation | Execution attempts to use a parameter value outside constraints | Critical |
| Tool violation | Execution invokes a tool not in `allowed_tools` | Critical |
| Timeout exceeded | Execution exceeds `timeout_seconds` | High |
| Scope violation | Execution accesses a system outside `scope_boundary` | Critical |
| Network violation | Execution reaches a destination outside `network_boundary` | Critical |
| Retry exceeded | Execution exceeds `max_retries` | Medium |

### 4.2 Violation Response

1. **Immediate termination.** The execution gate MUST halt execution immediately upon detecting a violation.
2. **Incident record.** An incident record MUST be created containing the violation type, triggering condition, execution state at time of violation, and the envelope that was violated.
3. **Rollback.** If the rollback plan is applicable and the violation is recoverable, execute the rollback procedure.
4. **Ledger entry.** A ledger entry MUST be created recording the violation, the terminated execution, and the incident.
5. **Notification.** The system SHOULD notify the authorization owner and system operators of the violation.

---

## 5. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://rio-protocol.org/schemas/execution_envelope.json",
  "title": "RIO Protocol Execution Envelope",
  "type": "object",
  "required": [
    "envelope_id",
    "authorization_id",
    "request_id",
    "allowed_tools",
    "parameter_constraints",
    "timeout_seconds",
    "max_retries",
    "rollback_plan",
    "kill_switch",
    "scope_boundary",
    "network_boundary",
    "created_at",
    "expires_at"
  ],
  "additionalProperties": false,
  "properties": {
    "envelope_id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier for this execution envelope"
    },
    "authorization_id": {
      "type": "string",
      "format": "uuid",
      "description": "The authorization record this envelope is derived from"
    },
    "request_id": {
      "type": "string",
      "format": "uuid",
      "description": "The canonical request this envelope governs"
    },
    "allowed_tools": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1,
      "description": "Explicit allowlist of tools the execution may invoke"
    },
    "parameter_constraints": {
      "type": "object",
      "description": "Per-parameter bounds for execution"
    },
    "timeout_seconds": {
      "type": "integer",
      "minimum": 1,
      "description": "Maximum wall-clock duration for execution"
    },
    "max_retries": {
      "type": "integer",
      "minimum": 0,
      "description": "Maximum retry attempts on transient failure"
    },
    "rollback_plan": {
      "type": "object",
      "required": ["rollback_type"],
      "properties": {
        "rollback_type": {
          "type": "string",
          "enum": ["compensating_action", "idempotent_retry", "manual_intervention", "no_rollback"]
        },
        "rollback_tool": { "type": "string" },
        "rollback_parameters": { "type": "object" },
        "rollback_timeout_seconds": { "type": "integer", "minimum": 1 },
        "rollback_requires_authorization": { "type": "boolean" },
        "manual_fallback": { "type": "string" }
      },
      "description": "Procedure to reverse or compensate for failed execution"
    },
    "kill_switch": {
      "type": "object",
      "required": ["conditions", "termination_behavior"],
      "properties": {
        "conditions": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["condition_id", "trigger", "description"],
            "properties": {
              "condition_id": { "type": "string" },
              "trigger": { "type": "string" },
              "description": { "type": "string" },
              "threshold": { "type": "string" }
            }
          },
          "minItems": 1
        },
        "termination_behavior": {
          "type": "string",
          "enum": ["immediate_halt", "graceful_shutdown"]
        },
        "post_termination": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "description": "Conditions that trigger immediate execution termination"
    },
    "scope_boundary": {
      "type": "object",
      "properties": {
        "allowed_systems": { "type": "array", "items": { "type": "string" } },
        "allowed_databases": { "type": "array", "items": { "type": "string" } },
        "allowed_file_paths": { "type": "array", "items": { "type": "string" } },
        "allowed_resources": { "type": "array", "items": { "type": "string" } },
        "denied_systems": { "type": "array", "items": { "type": "string" } }
      },
      "description": "Systems and resources the execution may access"
    },
    "network_boundary": {
      "type": "object",
      "properties": {
        "allowed_destinations": { "type": "array", "items": { "type": "string" } },
        "allowed_protocols": { "type": "array", "items": { "type": "string" } },
        "denied_destinations": { "type": "array", "items": { "type": "string" } },
        "egress_allowed": { "type": "boolean" }
      },
      "description": "Allowed network destinations and protocols"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp of envelope creation"
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "Envelope expiration — must match or precede authorization expiration"
    }
  }
}
```

---

## 6. Example: $48,250 Wire Transfer Execution Envelope

```json
{
  "envelope_id": "e1a2b3c4-d5e6-7f89-0a1b-c2d3e4f5a6b7",
  "authorization_id": "b2c3d4e5-f6a7-8901-b2c3-d4e5f6a7b8c9",
  "request_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f6a7b8",
  "allowed_tools": [
    "transact.send_payment.wire.domestic",
    "transact.check_status.wire",
    "communicate.send.email.internal"
  ],
  "parameter_constraints": {
    "amount": {
      "type": "number",
      "min": 48250.00,
      "max": 48250.00,
      "currency": "USD"
    },
    "recipient_account": {
      "type": "string",
      "exact_match": "7782019843"
    },
    "recipient_name": {
      "type": "string",
      "exact_match": "Meridian Industrial Supply LLC"
    },
    "transfer_type": {
      "type": "string",
      "enum": ["domestic_wire"]
    }
  },
  "timeout_seconds": 120,
  "max_retries": 1,
  "rollback_plan": {
    "rollback_type": "compensating_action",
    "rollback_tool": "transact.cancel_payment.wire",
    "rollback_parameters": {
      "original_confirmation_id": "${execution.result.confirmation_id}"
    },
    "rollback_timeout_seconds": 60,
    "rollback_requires_authorization": false,
    "manual_fallback": "Contact treasury operations at +1-555-0142 to manually reverse the wire transfer within the Fed reversal window."
  },
  "kill_switch": {
    "conditions": [
      {
        "condition_id": "KS-001",
        "trigger": "parameter_deviation",
        "description": "Amount differs from authorized $48,250.00",
        "threshold": "amount != 48250.00"
      },
      {
        "condition_id": "KS-002",
        "trigger": "recipient_mismatch",
        "description": "Recipient account differs from authorized account",
        "threshold": "recipient_account != '7782019843'"
      },
      {
        "condition_id": "KS-003",
        "trigger": "unauthorized_tool",
        "description": "Execution invokes a tool not in allowed_tools",
        "threshold": "tool NOT IN allowed_tools"
      },
      {
        "condition_id": "KS-004",
        "trigger": "timeout",
        "description": "Execution exceeds 120 seconds",
        "threshold": "elapsed_time > 120"
      },
      {
        "condition_id": "KS-005",
        "trigger": "scope_violation",
        "description": "Execution accesses a system outside scope_boundary",
        "threshold": "target NOT IN scope_boundary.allowed_systems"
      }
    ],
    "termination_behavior": "immediate_halt",
    "post_termination": [
      "Set execution_status to 'cancelled'",
      "Record triggering kill_switch condition",
      "Attempt rollback via transact.cancel_payment.wire",
      "Generate incident record",
      "Write ledger entry",
      "Notify CFO and treasury operations"
    ]
  },
  "scope_boundary": {
    "allowed_systems": [
      "core-banking-api.internal",
      "notification-service.internal"
    ],
    "allowed_databases": [],
    "allowed_file_paths": [],
    "allowed_resources": [
      "account:7782019843",
      "account:operating-001"
    ],
    "denied_systems": [
      "hr-system.internal",
      "admin-console.internal",
      "customer-data.internal"
    ]
  },
  "network_boundary": {
    "allowed_destinations": [
      "core-banking-api.internal:443",
      "notification-service.internal:443"
    ],
    "allowed_protocols": ["https"],
    "denied_destinations": ["0.0.0.0/0"],
    "egress_allowed": false
  },
  "created_at": "2026-03-24T14:33:42Z",
  "expires_at": "2026-03-24T14:38:42Z"
}
```

---

## 7. Relationship to Authorization Record Conditions

The execution envelope is derived from, but not identical to, the `authorization_record.conditions` array. The relationship is:

| Authorization Condition | Envelope Field |
|------------------------|----------------|
| `amount_cap` | `parameter_constraints.amount.max` |
| `time_restriction` | `expires_at` |
| `parameter_override` | `parameter_constraints.<field>.exact_match` |
| `scope_limitation` | `scope_boundary` |
| `tool_restriction` | `allowed_tools` |
| `network_restriction` | `network_boundary` |

**Construction rules:**
1. Start with system defaults from the manifest.
2. Apply policy-derived constraints (narrowing only — policies cannot widen system defaults).
3. Apply authorization conditions (narrowing only — authorizer cannot widen policy constraints).
4. The resulting envelope is the intersection of all three constraint sources.

The execution gate MUST verify that the constructed envelope is consistent (no contradictions) and non-empty (at least one tool is allowed, timeout is positive, etc.) before releasing execution.

---

## 8. Dependencies

| Document | Relationship |
|----------|-------------|
| Authorization Protocol (06) | Source of authorization conditions |
| Policy Constraints Protocol (05) | Source of policy-derived constraints |
| System Manifest | Source of system defaults |
| Execution Protocol (07) | Consumer of the execution envelope |
| Protocol State Machine | Envelope validation occurs during EXECUTION_PENDING → EXECUTED transition |
| System Invariants | Envelope enforcement upholds authorization and fail-closed invariants |
