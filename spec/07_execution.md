
## 1. Protocol Name
RIO Protocol Step 07: Execution

## 2. Purpose
The Execution step is responsible for performing the requested action after a valid, unexpired, and unused authorization has been confirmed. Its primary purpose is to translate an approved request into a real-world action, record the precise details of what was performed, and verify that the executed action aligns with the granted authorization. This step acts as the bridge between the digital decision chain and the tangible execution of an operation.

## 3. Scope
This protocol step covers the validation of the `authorization_record`, the execution of the specified action, the creation of the `execution_record`, and the comparison between the authorized and executed actions. It is explicitly out of scope for this step to perform risk evaluation, policy checks, or the initial authorization decision, as these are handled by upstream components. It is also out of scope to handle the final cryptographic attestation or the generation of a human-readable receipt, which are downstream responsibilities.

## 4. Inputs
This step primarily consumes the `authorization_record` to validate that the action is approved for execution.

| Field | Type | Required | Description |
|---|---|---|---|
| `authorization_id` | String | Yes | The unique identifier of the authorization record to be validated. |
| `request_id` | String | Yes | The identifier of the original canonical request. |
| `risk_evaluation_id` | String | Yes | The identifier of the associated risk evaluation. |
| `decision` | String | Yes | The outcome of the authorization decision (must be 'approved'). |
| `expires_at` | Timestamp | Yes | The timestamp indicating when the authorization is no longer valid. |

## 5. Outputs
This step produces a detailed `execution_record` that documents the action taken.

| Field | Type | Description |
|---|---|---|
| `execution_id` | String | A unique identifier for this execution event. |
| `request_id` | String | The identifier of the original canonical request. |
| `authorization_id` | String | The identifier of the authorization record that permitted this execution. |
| `execution_status` | String | The status of the execution (e.g., 'success', 'failure', 'partial_success'). |
| `action_performed` | Object | A detailed record of the action that was actually executed. |
| `result_summary` | String | A human-readable summary of the execution outcome. |
| `authorization_match` | Boolean | A flag indicating whether the executed action matched the authorized action. |
| `signature` | String | A digital signature from the execution environment to ensure integrity. |

## 6. Required Fields
The following fields from the `authorization_record` MUST be present and valid for the execution step to proceed.

| Field | Condition |
|---|---|
| `authorization_id` | MUST be a valid, non-null string. |
| `decision` | MUST be equal to the string 'approved'. |
| `expires_at` | MUST be a valid timestamp in the future. |

## 7. Processing Steps
The execution of a request follows a strict, sequential process:

1.  **Receive Execution Trigger**: The process initiates upon receiving a request to execute an action, referencing a specific `authorization_id`.
2.  **Fetch Authorization Record**: The system SHALL retrieve the full `authorization_record` from the data store using the provided `authorization_id`.
3.  **Validate Authorization Status**: The system MUST verify that the `decision` field in the `authorization_record` is 'approved'. If not, the process terminates with a failure condition.
4.  **Check Expiration**: The system MUST check that the `expires_at` timestamp is in the future. If the timestamp is in the past, the authorization is considered expired, and the process terminates.
5.  **Verify Authorization Uniqueness**: The system MUST verify that the `authorization_id` has not been previously used for an execution. This prevents replay attacks.
6.  **Execute Action**: The system SHALL now perform the action as specified in the `canonical_request` associated with the authorization. The execution environment (e.g., a payment gateway, an API client) performs the real-world operation.
7.  **Record Action Performed**: The execution environment MUST produce a detailed record of the action that was actually performed. This becomes the `action_performed` field in the `execution_record`.
8.  **Compare Authorization and Execution**: The system SHALL perform a deep comparison between the `action_performed` object and the `parameters` from the original `canonical_request`. The result of this comparison sets the `authorization_match` boolean flag.
9.  **Generate Execution Record**: The system SHALL create a new `execution_record.json` object, populating it with the `execution_id`, `request_id`, `authorization_id`, `execution_status`, `action_performed`, `result_summary`, and `authorization_match` fields.
10. **Sign and Store Record**: The execution environment MUST sign the newly created `execution_record` and store it securely. The signature provides a non-repudiable guarantee of the execution's integrity.

## 8. Decision Logic
The primary decision logic in the Execution step is a series of binary checks to validate the authorization before proceeding. The logic follows a fail-fast approach.

| Condition | Rule | Action if False |
|---|---|---|
| `authorization_record.decision == 'approved'` | The authorization must be explicitly approved. | Terminate with `failure_authorization_not_approved`. |
| `now() < authorization_record.expires_at` | The current time must be before the expiration time. | Terminate with `failure_authorization_expired`. |
| `is_authorization_unused(authorization_id)` | The authorization must not have been used in a prior execution. | Terminate with `failure_authorization_already_used`. |

## 9. Failure Conditions
Failures at this stage are critical as they prevent unauthorized or invalid actions from being performed.

| Error Code | Trigger | Required Action |
|---|---|---|
| `failure_authorization_not_found` | The provided `authorization_id` does not correspond to any existing record. | Log the event. Do not proceed with execution. |
| `failure_authorization_not_approved` | The `decision` field of the fetched `authorization_record` is not 'approved'. | Log the event. Do not proceed with execution. |
| `failure_authorization_expired` | The `expires_at` timestamp on the `authorization_record` is in the past. | Log the event. Do not proceed with execution. |
| `failure_authorization_already_used` | The `authorization_id` has already been associated with a previous `execution_record`. | Trigger a high-priority security alert for a potential replay attack. Log the event. Do not proceed with execution. |
| `failure_execution_error` | The execution environment (e.g., payment gateway) returns an error during the action. | Log the detailed error from the execution environment. Create an `execution_record` with `execution_status` set to 'failure'. |

## 10. Security Considerations
- **Replay Prevention**: The check to ensure an `authorization_id` is used only once is a critical defense against replay attacks. This MUST be enforced by a unique constraint in the data store.
- **Integrity of Execution Environment**: The execution environment MUST be a trusted and secure component. It is responsible for accurately performing the action and providing a truthful `action_performed` record.
- **Signature**: The `execution_record` MUST be digitally signed by the execution environment. This signature ensures the integrity and non-repudiation of the execution details.
- **Separation of Duties**: The entity performing the execution SHOULD be distinct from the entity that requested the action and the entity that authorized it.

## 11. Audit Requirements
- A complete `execution_record` MUST be created for every execution attempt, whether successful or failed.
- The log MUST include the precise timestamp of the execution attempt.
- The comparison result (`authorization_match`) MUST be logged to provide a clear audit trail of any discrepancies between what was authorized and what was executed.
- All failure conditions encountered during this step MUST be logged with their corresponding error codes and relevant identifiers (`request_id`, `authorization_id`).

## 12. Dependencies
- **Upstream**: This step is critically dependent on a valid `authorization_record` produced by the **Authorization** step (Step 06). It also implicitly depends on the `canonical_request` (Step 03) to define the action to be performed.
- **Downstream**: The **Attestation** step (Step 08) depends on the successful creation of the `execution_record` to include it in the final cryptographic chain of evidence.

## 13. Example Flow
The AI finance agent has requested a $48,250 wire transfer, which has been approved by the CFO, Sarah Mitchell.

1.  **Receive Execution Trigger**: The RIO system receives a trigger to execute the action associated with `authorization_id: auth-cfo-987654`.
2.  **Fetch Authorization Record**: The system retrieves the `authorization_record` for `auth-cfo-987654`.
3.  **Validate Authorization**: The system confirms `decision: "approved"`.
4.  **Check Expiration**: The system checks `expires_at: "2026-03-24T14:05:00Z"` against the current time of `2026-03-24T14:01:15Z`. The authorization is valid.
5.  **Verify Uniqueness**: The system confirms that `auth-cfo-987654` has not been used before.
6.  **Execute Action**: The RIO system instructs the integrated payment gateway to execute the wire transfer.
7.  **Record Action Performed**: The payment gateway confirms the transfer and returns the following `action_performed` object:
    ```json
    {
      "type": "wire_transfer",
      "amount": 48250.00,
      "currency": "USD",
      "beneficiary": "Meridian Industrial Supply",
      "beneficiary_account": "FR7630004000031234567890185",
      "reference": "Invoice #INV-2026-03-1147",
      "transaction_id": "pg-tx-a1b2c3d4e5"
    }
    ```
8.  **Compare Authorization and Execution**: The system compares this object to the `parameters` in the original `canonical_request`. They match perfectly. The `authorization_match` flag is set to `true`.
9.  **Generate Execution Record**: A new `execution_record` is created with `execution_id: exec-abcdef-123456`.
    - `request_id`: `req-xyz-12345`
    - `authorization_id`: `auth-cfo-987654`
    - `execution_status`: `"success"`
    - `result_summary`: `"Successfully executed wire transfer of $48,250.00 to Meridian Industrial Supply."`
    - `authorization_match`: `true`
10. **Sign and Store**: The payment gateway signs the `execution_record`, and it is stored in the audit ledger.
