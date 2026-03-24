'''
## 1. Protocol Name

RIO Protocol Step 05: Policy Constraints

## 2. Purpose

This protocol step evaluates a `canonical_request` against the organization's established policy framework. Its primary purpose is to determine which policies are applicable to a given AI-initiated action, evaluate the action against the constraints defined in those policies, and produce a definitive policy decision. This decision serves as a critical input for the subsequent `authorization` step, ensuring that all actions are vetted for compliance before they can be approved or executed. It acts as an automated guardrail, enforcing organizational rules at scale.

## 3. Scope

This protocol is responsible for the lookup, interpretation, and application of predefined policies to a `canonical_request`. It covers the logic for matching request attributes to policy triggers and evaluating the request parameters against the specific constraints.

**Out of Scope:**
- The definition, creation, or management of the policies themselves. This protocol assumes policies are stored in an accessible, machine-readable format in a designated Policy Store.
- The real-time evaluation of risk. This is handled by the upstream `risk_evaluation` protocol.
- The final authorization decision. This protocol provides a policy-based recommendation, but the ultimate approval or denial is handled by the `authorization` protocol.

## 4. Inputs

This step receives the `canonical_request` record and the `risk_evaluation` record.

| Field               | Type   | Required | Description                                                                                             |
| ------------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------- |
| `request_id`        | String | Yes      | The unique identifier for the action request, used to correlate records across the decision chain.      |
| `canonical_request` | JSON   | Yes      | The full `canonical_request.json` object, containing all details of the requested action.               |
| `risk_evaluation`   | JSON   | Yes      | The full `risk_evaluation.json` object, providing the risk context and score for the request.           |

## 5. Outputs

This step produces a `policy_constraints_record`, which documents the policy evaluation process and outcome.

| Field               | Type   | Description                                                                                                                               |
| ------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `policy_record_id`  | String | A unique identifier for this policy evaluation instance.                                                                                  |
| `request_id`        | String | The ID of the `canonical_request` being evaluated.                                                                                        |
| `evaluation_timestamp` | ISO 8601 | The timestamp when the policy evaluation was performed.                                                                                   |
| `matched_policies`  | Array  | A list of policy IDs that were triggered by the request.                                                                                  |
| `policy_decision`   | Enum   | The outcome of the policy evaluation. Values: `ALLOW`, `DENY`, `REQUIRE_AUTHORIZATION`.                                                   |
| `constraints_applied` | JSON   | An object detailing the specific constraints from matched policies that were applied (e.g., velocity limits, required approvals).       |
| `policy_context`    | JSON   | The `policy_context` from the original request, now updated with the results of this evaluation.                                          |

## 6. Required Fields

The following fields from the `canonical_request` and `risk_evaluation` inputs MUST be present for the protocol to execute.

| Field           | Source              | Description                                      |
| --------------- | ------------------- | ------------------------------------------------ |
| `request_id`    | `canonical_request` | The unique identifier for the request.           |
| `action_type`   | `canonical_request` | The type of action being requested (e.g., `WIRE_TRANSFER`). |
| `parameters`    | `canonical_request` | The specific parameters of the action (e.g., amount, destination). |
| `risk_level`    | `risk_evaluation`   | The assessed risk level (e.g., `HIGH`).          |
| `risk_score`    | `risk_evaluation`   | The numerical risk score.                        |

## 7. Processing Steps

1.  The protocol SHALL receive the `canonical_request` and `risk_evaluation` records.
2.  It SHALL generate a new `policy_record_id` and set the `evaluation_timestamp`.
3.  The protocol MUST query the organization's Policy Store using attributes from the `canonical_request` (e.g., `action_type`, `target`, `parameters.amount`) and `risk_evaluation` (e.g., `risk_level`).
4.  The protocol SHALL identify all `matched_policies` whose trigger conditions are met by the request data.
5.  For each matched policy, the protocol MUST evaluate the request against the policy's `constraints`.
6.  The protocol SHALL aggregate the outcomes from all evaluated policies to determine a final `policy_decision` based on the Decision Logic (Section 8).
7.  The protocol MUST populate the `constraints_applied` field with a summary of the rules that influenced the final decision.
8.  The protocol SHALL construct the final `policy_constraints_record`.
9.  The `policy_constraints_record` MUST be passed downstream to the `authorization` protocol.

## 8. Decision Logic

The final `policy_decision` is determined by the most restrictive outcome from all matched policies.

| If any matched policy dictates... | Then the final `policy_decision` MUST be... |
| ------------------------------- | ------------------------------------------- |
| `DENY`                          | `DENY`                                      |
| `REQUIRE_AUTHORIZATION`         | `REQUIRE_AUTHORIZATION`                     |
| `ALLOW` (and no other rule applies) | `ALLOW`                                     |

**Example Policy Evaluation:**

- **Policy ID:** `POL-FIN-001` (Financial Transactions)
- **Trigger:** `action_type` == `WIRE_TRANSFER`
- **Constraint:** If `parameters.amount` > $10,000, then `REQUIRE_AUTHORIZATION`.

- **Policy ID:** `POL-SEC-004` (High Risk Actions)
- **Trigger:** `risk_level` == `HIGH`
- **Constraint:** `REQUIRE_AUTHORIZATION` by a member of the `CFO-Group`.

- **Policy ID:** `POL-VEND-007` (Vendor Management)
- **Trigger:** `target` is in `UntrustedVendorList`
- **Constraint:** `DENY`

If a request matches `POL-FIN-001` and `POL-SEC-004`, the decision will be `REQUIRE_AUTHORIZATION`. If it also matches `POL-VEND-007`, the decision will be `DENY`, as it is the most restrictive rule.

## 9. Failure Conditions

| Error Code | Trigger                                                     | Required Action                                                                                                |
| ---------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `PCE-01`   | Policy Store is unreachable or returns an error.            | The protocol MUST fail open or closed based on system configuration. Log the error and alert system administrators. |
| `PCE-02`   | A required input field is missing or malformed.             | The protocol MUST reject the request with a `DENY` decision and log a validation error.                        |
| `PCE-03`   | A matched policy contains an uninterpretable rule or format. | The protocol MUST treat this as a `DENY` decision, log the malformed policy ID, and alert policy administrators. |

## 10. Security Considerations

- **Policy Integrity:** The connection to the Policy Store MUST be over a secure and authenticated channel (e.g., mTLS). The policies themselves SHOULD be signed to prevent tampering.
- **Data Confidentiality:** The `canonical_request` may contain sensitive data. All processing within this step MUST occur in a trusted execution environment, and logs SHOULD mask sensitive fields.
- **Denial of Service:** The complexity of policy evaluation could be a vector for DoS attacks. The protocol implementation SHOULD include timeouts and resource limits for policy queries and evaluation.

## 11. Audit Requirements

To ensure transparency and non-repudiation, the following items MUST be logged as part of the audit trail:

- The complete `policy_constraints_record`, including the final `policy_decision`.
- A list of all `matched_policies` and the specific `constraints_applied`.
- The version of the policy engine and the versions of all policies evaluated.
- Any failures or errors encountered during processing, including the corresponding error codes.

## 12. Dependencies

- **Upstream:** This protocol step is dependent on the successful completion of:
    - `01_intake`
    - `02_origin_verification`
    - `03_canonical_request`
    - `04_risk_evaluation`

- **Downstream:** The output of this protocol, the `policy_constraints_record`, is a required input for:
    - `06_authorization`

## 13. Example Flow

**Scenario:** An AI finance agent requests a $48,250 wire transfer to Meridian Industrial Supply.

1.  **Input Received:** The protocol receives `request_id: "req-a9b8c7d6"` along with the `canonical_request` and the `risk_evaluation` record, which has `risk_level: "HIGH"` and `risk_score: 82`.

2.  **Policy Query:** The protocol queries the Policy Store with attributes:
    - `action_type: "WIRE_TRANSFER"`
    - `parameters.amount: 48250`
    - `risk_level: "HIGH"`

3.  **Policy Matching:** The query returns two matching policies:
    - `POL-FIN-001`: Triggered because `action_type` is `WIRE_TRANSFER` and `parameters.amount` > $10,000.
    - `POL-SEC-004`: Triggered because `risk_level` is `HIGH`.

4.  **Constraint Evaluation:**
    - `POL-FIN-001` applies the constraint: `REQUIRE_AUTHORIZATION`.
    - `POL-SEC-004` applies the constraint: `REQUIRE_AUTHORIZATION` by a member of the `CFO-Group`.

5.  **Decision Logic:** Both policies resolve to `REQUIRE_AUTHORIZATION`. The final `policy_decision` is therefore `REQUIRE_AUTHORIZATION`.

6.  **Output Generation:** The protocol generates the `policy_constraints_record`:
    - `policy_record_id: "pol-rec-e5f4g3h2"`
    - `request_id: "req-a9b8c7d6"`
    - `evaluation_timestamp: "2026-03-24T10:04:15Z"`
    - `matched_policies: ["POL-FIN-001", "POL-SEC-004"]`
    - `policy_decision: "REQUIRE_AUTHORIZATION"`
    - `constraints_applied: { "required_authorizer_group": "CFO-Group" }`
    - `policy_context: { ... }`

7.  **Downstream Handoff:** The newly created `policy_constraints_record` is passed to the `authorization` protocol to seek approval from a member of the CFO-Group.
'''
