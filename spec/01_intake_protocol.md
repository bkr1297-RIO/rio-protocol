# RIO Protocol Specification: 01 - Intake

## 1. Protocol Name

RIO Protocol Step 01: Intake Protocol

## 2. Purpose

The Intake Protocol serves as the formal entry point for all action requests submitted to the RIO (Runtime Intelligence Orchestration) system. Its primary function is to receive raw action requests from diverse sources—such as AI agents, automated services, or human-delegated processes—and to perform initial, non-substantive validation. This protocol standardizes incoming data by validating its basic structure, assigning a unique and immutable tracking identifier (`request_id`), and formally constructing the `canonical_request` object. This ensures that every action is properly registered and prepared for secure and sequential processing through the RIO decision chain, beginning with the Origin Verification protocol.

## 3. Scope

This protocol's responsibilities are strictly limited to the initial capture and structural validation of an action request. The scope includes:

- **Receiving Requests:** Accepting action requests through a secure, defined API endpoint.
- **Structural Validation:** Verifying the presence and correct data types of mandatory fields in the raw request.
- **Identifier Assignment:** Generating a cryptographically secure, unique `request_id` that will follow the request through its entire lifecycle.
- **Object Creation:** Assembling the validated data into the formal `canonical_request.json` data structure.
- **Hand-off:** Passing the newly created `canonical_request` object to the next step in the chain, the Origin Verification Protocol.

Explicitly out of scope for the Intake Protocol are:

- Verifying the identity or authenticity of the requester (`Origin Verification`).
- Analyzing the potential risk of the action (`Risk Evaluation`).
- Applying business rules or organizational policies (`Policy Constraints`).
- Granting or denying permission for the action (`Authorization`).
- Performing the requested action (`Execution`).
- Creating cryptographic proof of the process (`Attestation`).

## 4. Inputs

The protocol receives a raw action request, typically transmitted as a JSON payload over a secure (TLS) connection. The structure of this payload is detailed below.

| Field           | Type   | Required | Description                                                                                                 |
|:----------------|:-------|:---------|:------------------------------------------------------------------------------------------------------------|
| `action_type`   | String | Yes      | A standardized string identifying the class of action (e.g., `WIRE_TRANSFER`, `API_CALL`, `FILE_DELETE`).       |
| `target`        | Object | Yes      | An object defining the resource upon which the action is to be performed (e.g., a bank account, a server).    |
| `parameters`    | Object | Yes      | A key-value map of the specific arguments required to execute the action (e.g., amount, destination, query). |
| `requested_by`  | String | Yes      | An identifier for the principal (AI agent, system, user) initiating the request.                            |
| `business_reason`| String | Yes      | A human-readable justification for the action, intended for audit and review.                               |
| `risk_context`  | Object | No       | Optional, requester-provided data that may inform the downstream risk evaluation process.                   |
| `policy_context`| Object | No       | Optional, requester-provided data that may inform the downstream policy evaluation process.                 |

## 5. Outputs

The sole output of this protocol is the `canonical_request` object, which conforms to the `canonical_request.json` schema.

| Field               | Type        | Description                                                                                                                                 |
|:--------------------|:------------|:--------------------------------------------------------------------------------------------------------------------------------------------|
| `canonical_request` | JSON Object | The structured, validated, and identified request object that serves as the foundational record for all subsequent protocol steps. |

## 6. Required Fields

For a raw request to pass validation and be accepted into the RIO system, it MUST contain the following fields with non-null values. Failure to meet this requirement SHALL result in the immediate rejection of the request.

| Field           | Type   | Constraint      |
|:----------------|:-------|:----------------|
| `action_type`   | String | Must not be empty |
| `target`        | Object | Must not be empty |
| `parameters`    | Object | Must not be empty |
| `requested_by`  | String | Must not be empty |
| `business_reason`| String | Must not be empty |

## 7. Processing Steps

The Intake Protocol MUST be executed in the following sequence:

1.  **Receive Request:** The protocol listener accepts an incoming request on its designated endpoint.
2.  **Log Raw Request:** The full, unaltered body of the incoming request is logged for audit purposes before any processing occurs.
3.  **Validate Structure:** The request is checked for the presence and basic data type of all fields listed in Section 6. The validation is structural, not semantic (e.g., it checks that `amount` is a number, not that the number is within a valid range).
4.  **Generate Request ID:** Upon successful validation, a new, unique `request_id` is generated. This identifier SHOULD be a Version 4 UUID to ensure uniqueness and non-predictability.
5.  **Construct Canonical Request:** A new JSON object is created that conforms to the `canonical_request.json` schema. It is populated with the validated data from the raw request and the newly generated `request_id`.
6.  **Log Canonical Request:** The complete `canonical_request` object is logged for audit and traceability.
7.  **Forward to Origin Verification:** The `canonical_request` object is passed to the Origin Verification protocol for the next stage of processing.

## 8. Decision Logic

The decision logic of the Intake Protocol is binary and based solely on structural validation.

| Condition                                     | Result                                      |
|:----------------------------------------------|:--------------------------------------------|
| All fields in Section 6 are present and valid | **ACCEPT:** Proceed to Step 4 (Generate ID) |
| Any field in Section 6 is missing or invalid  | **REJECT:** Fail with error code `400-InvalidRequest` |

## 9. Failure Conditions

This protocol step can fail under the following conditions. Each failure MUST be logged with its corresponding error code.

| Error Code          | Trigger                                                              | Required Action                                                                                              |
|:--------------------|:---------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------|
| `400-InvalidRequest`| The incoming request is missing one or more required fields, or the fields are of an incorrect data type. | The request is immediately rejected. A failure notice is logged. No `request_id` is generated. No further processing occurs. |
| `500-InternalError` | The protocol fails to generate a `request_id` or encounters an unexpected internal processing error. | The request is rejected. A high-priority alert is raised for system administrators. The raw request is preserved for diagnostics. |

## 10. Security Considerations

- **Transport Security:** All endpoints for this protocol MUST be protected with strong, current Transport Layer Security (TLS 1.2 or higher) to ensure confidentiality and integrity of the incoming request data.
- **Identifier Security:** The `request_id` MUST be generated using a cryptographically secure random number generator to prevent prediction or collision. It is an identifier, not a secret, but its integrity is paramount.
- **Input Sanitization:** While this protocol's validation is structural, the receiving endpoint SHOULD perform basic input sanitization to mitigate common injection-style attacks before parsing the JSON payload.
- **Denial of Service:** The intake endpoint should be monitored for anomalous traffic patterns and be protected by rate limiting to mitigate Denial of Service (DoS) attacks.

## 11. Audit Requirements

To ensure full traceability, the following information MUST be logged at this stage:

- The complete, raw, and unmodified incoming request payload.
- The precise timestamp (UTC with millisecond precision) of request receipt.
- The outcome of the validation check (ACCEPT or REJECT).
- If rejected, the specific reason and error code for the failure.
- If accepted, the generated `request_id` and the full `canonical_request` object that was created.

## 12. Dependencies

- **Upstream:** This protocol has no upstream dependencies within the RIO chain, as it is the designated entry point.
- **Downstream:** This protocol is a direct dependency for the **02_origin_verification_protocol**. The Origin Verification step cannot begin until the Intake Protocol has successfully completed and produced a valid `canonical_request` object.

## 13. Example Flow

This example follows the scenario of an AI finance agent requesting a $48,250 wire transfer.

1.  **Request Received:** At `2026-03-24T10:00:00.123Z`, the RIO Intake endpoint receives the following JSON payload:

    ```json
    {
      "action_type": "WIRE_TRANSFER",
      "target": {
        "type": "BENEFICIARY_ACCOUNT",
        "identifier": "ACCT_6021-MERIDIAN"
      },
      "parameters": {
        "amount": 48250.00,
        "currency": "USD",
        "destination_name": "Meridian Industrial Supply",
        "reference": "Invoice #INV-2026-03-1147"
      },
      "requested_by": "agent:finance-automator-v3.1",
      "business_reason": "Payment for approved Q1 industrial equipment invoice."
    }
    ```

2.  **Validation:** The protocol verifies that `action_type`, `target`, `parameters`, `requested_by`, and `business_reason` are all present and correctly formatted. The validation passes.

3.  **ID Generation:** A unique `request_id` is generated: `req_a7b3c8d9-e1f2-4a5b-8c6d-7e8f9a0b1c2d`.

4.  **Canonical Request Construction:** The system constructs the `canonical_request` object:

    ```json
    {
      "request_id": "req_a7b3c8d9-e1f2-4a5b-8c6d-7e8f9a0b1c2d",
      "requested_by": "agent:finance-automator-v3.1",
      "action_type": "WIRE_TRANSFER",
      "target": {
        "type": "BENEFICIARY_ACCOUNT",
        "identifier": "ACCT_6021-MERIDIAN"
      },
      "parameters": {
        "amount": 48250.00,
        "currency": "USD",
        "destination_name": "Meridian Industrial Supply",
        "reference": "Invoice #INV-2026-03-1147"
      },
      "business_reason": "Payment for approved Q1 industrial equipment invoice.",
      "risk_context": {},
      "policy_context": {}
    }
    ```

5.  **Hand-off:** At `2026-03-24T10:00:00.250Z`, this `canonical_request` object is passed to the Origin Verification protocol, and the Intake step is complete.
