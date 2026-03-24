## 1. Protocol Name
RIO Protocol Step 12: Role Separation

## 2. Purpose
This protocol step ensures the integrity of the RIO decision chain by enforcing the principle of separation of duties. It defines the distinct roles within the RIO system and ensures that no single entity can perform multiple conflicting roles in the same decision chain. The purpose is to prevent unauthorized actions, fraud, and errors by requiring multiple independent actors to be involved in high-risk decisions.

## 3. Scope
This protocol covers the validation of role separation for all actors involved in a single RIO decision chain, including the requester, evaluator, authorizer, executor, and attestor. It defines the conflict rules between these roles.

This protocol is explicitly out of scope of:
*   The underlying Identity and Access Management (IAM) system used to manage and authenticate entities.
*   The specific mechanisms for assigning roles to entities.
*   The enforcement of role separation outside of a single RIO decision chain.

## 4. Inputs
This protocol step receives the identities of all actors involved in the decision chain so far.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request_id` | String | Yes | The unique identifier of the request. |
| `requester_identity` | String | Yes | The identity of the entity that initiated the request, from `canonical_request.json`. |
| `evaluator_identity` | String | Yes | The identity of the entity that performed the risk evaluation, from `risk_evaluation.json`. |
| `authorizer_identity` | String | Yes | The identity of the entity that authorized the request, from `authorization_record.json`. |
| `executor_identity` | String | Yes | The identity of the entity that executed the action, from `execution_record.json`. |
| `attestor_identity` | String | Yes | The identity of the entity that will attest to the record, from `attestation_record.json`. |

## 5. Outputs
This protocol step produces a validation status indicating whether the role separation principle has been upheld.

| Field | Type | Description |
| :--- | :--- | :--- |
| `role_separation_check_status` | String | The result of the role separation check. MUST be either `success` or `failure`. |
| `conflicting_roles` | Array of Strings | If the check fails, this field contains a list of roles that are in conflict. |

## 6. Required Fields
For this protocol step to proceed, the following fields MUST be present:

| Field |
| :--- |
| `request_id` |
| `requester_identity` |
| `evaluator_identity` |
| `authorizer_identity` |
| `executor_identity` |
| `attestor_identity` |

## 7. Processing Steps
1.  The protocol receives the identities of the requester, evaluator, authorizer, executor, and attestor for a given `request_id`.
2.  A set of unique identities is created from the received identity fields.
3.  The protocol SHALL compare the number of unique identities in the set with the number of roles being evaluated (which is 5).
4.  If the number of unique identities is less than 5, a role conflict is detected. The protocol MUST identify which identities are associated with multiple roles.
5.  The `role_separation_check_status` SHALL be set to `failure`.
6.  The `conflicting_roles` field SHALL be populated with the names of the roles that are in conflict.
7.  If the number of unique identities is equal to 5, no role conflict is detected. The `role_separation_check_status` SHALL be set to `success`.

## 8. Decision Logic
The core decision logic is based on a conflict matrix that defines which roles are not permitted to be performed by the same entity within the same decision chain. A conflict exists if any two roles are held by the same identity.

| Role A | Role B | Conflict? |
| :--- | :--- | :--- |
| Requester | Evaluator | Yes |
| Requester | Authorizer | Yes |
| Requester | Executor | Yes |
| Requester | Attestor | Yes |
| Evaluator | Authorizer | Yes |
| Evaluator | Executor | Yes |
| Evaluator | Attestor | Yes |
| Authorizer | Executor | Yes |
| Authorizer | Attestor | Yes |
| Executor | Attestor | Yes |

## 9. Failure Conditions
| Error Code | Trigger | Required Action |
| :--- | :--- | :--- |
| `ROLE_CONFLICT` | A single entity is found to be performing more than one role in the decision chain. | The RIO process MUST be halted. The request MUST be rejected. An alert SHOULD be generated and sent to a security or compliance team. |
| `MISSING_IDENTITY` | One or more of the required identity fields are not provided. | The RIO process MUST be halted. The request MUST be rejected. An error SHOULD be logged indicating which identity was missing. |

## 10. Security Considerations
*   The identities of all actors MUST be securely managed and authenticated through a robust IAM system.
*   The transmission of identity information between protocol steps MUST be over a secure and encrypted channel.
*   Any failure in the role separation check MUST be treated as a potential security incident and logged accordingly.
*   The role separation logic itself SHOULD be protected from tampering.

## 11. Audit Requirements
*   A record of every role separation check MUST be logged, including the `request_id`, the identities of all actors, and the outcome of the check (`success` or `failure`).
*   In case of a failure, the specific conflicting roles MUST be logged.
*   These audit logs MUST be immutable and stored securely for a defined retention period.

## 12. Dependencies
*   **Upstream:** This protocol step depends on the successful completion of the preceding steps that generate the `canonical_request.json`, `risk_evaluation.json`, `authorization_record.json`, and `execution_record.json` as they provide the identities of the actors.
*   **Downstream:** The `attestation_record.json` and `receipt.json` steps depend on the successful completion of this role separation check. A failure in this step will prevent the attestation and the generation of the final receipt.

## 13. Example Flow
In the $48,250 wire transfer scenario, the role separation check is performed as follows:

*   **Inputs:**
    *   `request_id`: `4a4f4e43-4b4f-4d4f-8f8f-4e4f4f4f4f4f`
    *   `requester_identity`: `ai-finance-agent-prod-01`
    *   `evaluator_identity`: `rio-risk-eval-engine-prod-us-east-1`
    *   `authorizer_identity`: `sarah.mitchell@examplecorp.com`
    *   `executor_identity`: `fedwire-integration-svc-acct`
    *   `attestor_identity`: `rio-attestation-service-prod-us-east-1`

*   **Processing:**
    1.  The protocol receives the five identities listed above.
    2.  A set of unique identities is created: `{'ai-finance-agent-prod-01', 'rio-risk-eval-engine-prod-us-east-1', 'sarah.mitchell@examplecorp.com', 'fedwire-integration-svc-acct', 'rio-attestation-service-prod-us-east-1'}`.
    3.  The number of unique identities (5) is compared to the number of roles (5).
    4.  Since the numbers are equal, no conflict is detected.

*   **Outputs:**
    *   `role_separation_check_status`: `success`
    *   `conflicting_roles`: `[]`

The protocol step completes successfully, and the RIO decision chain proceeds to the next step.
