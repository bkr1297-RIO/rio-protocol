# RIO Protocol — Policy Language Specification

## 1. Overview

This document specifies the structure, evaluation, and lifecycle of policies within the RIO Protocol. RIO policies are declarative, machine-readable rules that govern the execution of actions within a system. The Policy Engine, a core component of the RIO Protocol, evaluates these policies during the risk evaluation and authorization phases of the decision traceability chain. Policies are designed to be unambiguous and auditable, ensuring that all actions are explicitly authorized and compliant with established governance criteria. All policy changes MUST be authorized through the RIO Protocol itself, a concept known as meta-governance.

## 2. Policy Rule Structure

A RIO policy is a JSON object composed of the following fields:

| Field | Type | Description |
| :--- | :--- | :--- |
| `policy_id` | String | A unique identifier for the policy. |
| `policy_name` | String | A human-readable name for the policy. |
| `version` | Integer | The version number of the policy. |
| `priority` | Integer | A number indicating the policy's evaluation priority. Lower numbers are evaluated first. |
| `conditions` | Array | An array of predicate objects that MUST all evaluate to true for the policy to match. |
| `action` | String | The action to be taken if the conditions are met. MUST be one of: `DENY`, `ESCALATE`, `ALLOW_WITH_CONSTRAINTS`, `ALLOW`. |
| `constraints` | Object | An optional object defining constraints to be applied if the action is `ALLOW_WITH_CONSTRAINTS`. |
| `effective_from` | String | The ISO 8601 timestamp from which the policy is effective. |
| `effective_until` | String | The ISO 8601 timestamp until which the policy is effective. |
| `created_by` | String | The identifier of the user or system that created the policy. |
| `approved_by` | String | The identifier of the user or system that approved the policy. |

## 3. Priority Order

Policies are evaluated in a specific order to ensure deterministic outcomes. The primary sorting key is the `action` field, followed by the `priority` field. The order of actions is as follows:

1.  **DENY:** Policies that explicitly deny an action.
2.  **ESCALATE:** Policies that require a higher level of authorization.
3.  **ALLOW_WITH_CONSTRAINTS:** Policies that allow an action with specific limitations.
4.  **ALLOW:** Policies that explicitly allow an action.

Within each action category, policies are sorted by their `priority` value in ascending order (lower numbers have higher priority). The first matching `DENY` policy will always win, immediately stopping further evaluation. If no `DENY` policy matches, the first matching `ESCALATE` policy is applied. If no `DENY` or `ESCALATE` policies match, the first matching `ALLOW_WITH_CONSTRAINTS` or `ALLOW` policy is applied. If multiple `ALLOW_WITH_CONSTRAINTS` or `ALLOW` policies match, the one with the lowest `priority` value is chosen.

## 4. Condition Predicates

Condition predicates are used to evaluate the `canonical_request` against the policy's rules. The following predicates are supported:

| Predicate | Description |
| :--- | :--- |
| `equals` | Checks if a field in the request is equal to a specified value. |
| `greater_than` | Checks if a numeric field in the request is greater than a specified value. |
| `less_than` | Checks if a numeric field in the request is less than a specified value. |
| `in_set` | Checks if a field in the request is present in a specified set of values. |
| `not_in_set` | Checks if a field in the request is not present in a specified set of values. |
| `matches_pattern` | Checks if a string field in the request matches a specified regular expression. |
| `time_within` | Checks if a timestamp field in the request is within a specified time range. |
| `role_is` | Checks if the requesting user has a specific role. |
| `action_type_matches` | Checks if the requested action type matches a specified type. |

## 5. Constraint Types

Constraints are applied when a policy with the `ALLOW_WITH_CONSTRAINTS` action is matched. The following constraint types are supported:

| Constraint | Description |
| :--- | :--- |
| `amount_cap` | Sets a maximum value for a numeric parameter in the request. |
| `time_restriction` | Restricts the execution of the action to a specific time window. |
| `parameter_override` | Overrides a parameter in the request with a specified value. |
| `require_co_authorization` | Requires an additional signature from a user with a specific role. |
| `notification_required` | Requires a notification to be sent to a specified recipient upon execution. |
| `rate_limit` | Limits the number of times the action can be executed within a specified time period. |

## 6. Human-Readable Policy Example

Here is an example of a policy expressed in natural language:

> 'Wire transfers over $25,000 to external accounts require CFO approval within business hours.'

## 7. JSON Policy Example

Here is the same policy expressed as a RIO policy JSON object:

```json
{
  "policy_id": "policy-wire-transfer-cfo-approval",
  "policy_name": "Wire Transfer CFO Approval",
  "version": 1,
  "priority": 100,
  "conditions": [
    {
      "field": "action_type",
      "predicate": "equals",
      "value": "wire_transfer"
    },
    {
      "field": "amount",
      "predicate": "greater_than",
      "value": 25000
    },
    {
      "field": "destination_account_type",
      "predicate": "equals",
      "value": "external"
    },
    {
      "field": "request_time",
      "predicate": "time_within",
      "value": {
        "start": "T09:00:00Z",
        "end": "T17:00:00Z",
        "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]
      }
    }
  ],
  "action": "ESCALATE",
  "constraints": {
    "require_co_authorization": {
      "role": "CFO"
    }
  },
  "effective_from": "2023-01-01T00:00:00Z",
  "effective_until": "2024-01-01T00:00:00Z",
  "created_by": "system",
  "approved_by": "admin"
}
```

## 8. Policy Lifecycle

The lifecycle of a policy is managed through the RIO Protocol itself. This ensures that all changes to the governance rules are themselves governed. The lifecycle consists of the following stages:

1.  **Creation:** A new policy is created as a JSON object. It is not yet active.
2.  **Versioning:** Any change to a policy MUST result in a new version of that policy.
3.  **Activation:** A policy becomes active when it is approved through the RIO Protocol. This involves a `canonical_request` to approve the policy, which is itself evaluated by the Policy Engine.
4.  **Deactivation:** A policy can be deactivated by setting its `effective_until` timestamp to a time in the past.
5.  **Retirement:** A policy is retired when it is no longer needed. Retired policies are archived for auditing purposes.

## 9. Evaluation Algorithm

The Policy Engine evaluates policies against a `canonical_request` using the following algorithm:

1.  Fetch all active policies.
2.  Filter policies based on `effective_from` and `effective_until` timestamps.
3.  Group policies by their `action` type.
4.  For each `action` type, sort the policies by their `priority` in ascending order.
5.  Evaluate policies in the order of `DENY`, `ESCALATE`, `ALLOW_WITH_CONSTRAINTS`, `ALLOW`.
6.  For each policy, evaluate all `conditions`. If all conditions in a policy are met, the policy is considered a match.
7.  If a matching `DENY` policy is found, the evaluation stops and the action is denied.
8.  If no matching `DENY` policy is found, the first matching `ESCALATE` policy is applied.
9.  If no matching `DENY` or `ESCALATE` policies are found, the first matching `ALLOW_WITH_CONSTRAINTS` or `ALLOW` policy is applied.
10. If no policies match, the default action is `DENY`.

## 10. Anti-Patterns

When creating policies, it is important to avoid common mistakes that can lead to unintended consequences. Here are some anti-patterns to avoid:

*   **Overly broad conditions:** Policies with conditions that are too general can inadvertently deny or allow actions that they shouldn't.
*   **Conflicting policies:** Creating multiple policies that can match the same request with conflicting actions can lead to unpredictable behavior.
*   **Ignoring priority:** Not considering the priority of policies can result in the wrong policy being applied.
*   **Complex regular expressions:** Using overly complex regular expressions can make policies difficult to understand and maintain.
*   **Not testing policies:** Failing to test policies before activating them can lead to production issues.
