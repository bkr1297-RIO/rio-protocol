# RIO Protocol Specification: 03_canonical_request

## 1. Protocol Name

RIO Protocol Step 03: Canonical Request Formation

## 2. Purpose

This protocol step is responsible for transforming a verified, but potentially heterogeneous, intake request into a standardized, immutable, and verifiable `canonical_request` object. Its primary purpose is to create a single, trusted source of truth for the requested action that all subsequent steps in the RIO decision chain can rely on. By normalizing fields and computing a cryptographic hash of the contents, this step ensures data integrity and provides a stable root record, identified by a unique `request_id`, for auditing and dependency tracking.

## 3. Scope

**In Scope:**

*   Generation of a unique and unpredictable `request_id`.
*   Normalization and validation of all data received from the preceding Origin Verification step.
*   Construction of the `canonical_request` object according to the `canonical_request.json` schema.
*   Computation of a canonical hash over the object's contents to ensure immutability.
*   Persistent storage of the final `canonical_request` record.

**Out of Scope:**

*   Verification of the identity or origin of the requestor (handled by Step 02: Origin Verification).
*   Evaluation of the risk associated with the request (handled by Step 04: Risk Evaluation).
*   Enforcement of policies or authorization logic.
*   Execution of the requested action.

## 4. Inputs

This protocol step receives a data structure from the Origin Verification step containing the verified details of the action being requested.

| Field             | Type   | Required | Description                                                                                             | 
| ----------------- | ------ | -------- | ------------------------------------------------------------------------------------------------------- | 
| `verified_origin` | String | Yes      | The verified identifier of the entity making the request (e.g., AI agent ID, user ID).                  | 
| `action_type`     | String | Yes      | The classification of the action being requested (e.g., `wire_transfer`, `database_query`).             | 
| `target_resource` | String | Yes      | The specific resource the action will affect (e.g., a bank account number, a database table name).      | 
| `parameters`      | Object | Yes      | A JSON object containing the specific parameters for the action (e.g., amount, destination, query filter). | 
| `business_reason` | String | Yes      | A human-readable justification for the action, providing context for reviewers.                         | 
| `risk_context`    | Object | No       | Optional preliminary risk data provided by the origin system.                                           | 
| `policy_context`  | Object | No       | Optional preliminary policy data or hints provided by the origin system.                                | 

## 5. Outputs

This protocol step produces the final, cryptographically-hashed `canonical_request` record.

| Field                 | Type   | Description                                                                                                                                      | 
| --------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------ | 
| `request_id`          | String | A unique, unpredictable identifier (UUIDv4) for this specific request. This ID is the primary key for the entire decision chain.                     | 
| `canonical_hash`      | String | A cryptographic hash (SHA-256) of the canonical request object's contents, ensuring data integrity and preventing tampering.                     | 
| `requested_by`        | String | The normalized identifier of the requesting entity.                                                                                              | 
| `action_type`         | String | The normalized action type.                                                                                                                      | 
| `target`              | String | The normalized target resource.                                                                                                                  | 
| `parameters`          | Object | The normalized and structured parameters for the action.                                                                                         | 
| `business_reason`     | String | The normalized business reason.                                                                                                                  | 
| `risk_context`        | Object | The normalized risk context, merged with any system-defaults if applicable.                                                                      | 
| `policy_context`      | Object | The normalized policy context, merged with any system-defaults if applicable.                                                                    | 

## 6. Required Fields

For a canonical request to be successfully formed, the following input fields MUST be present and valid. The absence of any of these fields SHALL result in a failure condition.

| Field             | Type   | 
| ----------------- | ------ | 
| `verified_origin` | String | 
| `action_type`     | String | 
| `target_resource` | String | 
| `parameters`      | Object | 
| `business_reason` | String | 

## 7. Processing Steps

1.  **Receive Verified Intake:** The protocol step receives the data payload from the successful completion of the Origin Verification step.
2.  **Validate Required Fields:** The system MUST check for the presence and basic validity of all fields listed in Section 6. If any field is missing or malformed, the process MUST terminate and trigger the `MissingRequiredField` failure condition.
3.  **Generate Request ID:** The system SHALL generate a new, unique `request_id` using the UUIDv4 algorithm.
4.  **Normalize Fields:** All string fields (e.g., `verified_origin`, `action_type`, `target_resource`, `business_reason`) MUST be normalized by trimming leading/trailing whitespace and converting to a consistent case (e.g., lowercase) where appropriate for the field type. The `parameters` object keys and values SHOULD also be normalized.
5.  **Construct Request Object:** The system SHALL assemble the `canonical_request` object by mapping the normalized input fields to their corresponding fields in the `canonical_request.json` schema (`verified_origin` maps to `requested_by`, `target_resource` maps to `target`).
6.  **Compute Canonical Hash:** The system MUST serialize the constructed `canonical_request` object (excluding the `canonical_hash` field itself) into a deterministic, canonical JSON string (e.g., keys sorted alphabetically, no insignificant whitespace). A SHA-256 hash of this string SHALL then be computed. This hash value is assigned to the `canonical_hash` field.
7.  **Persist Record:** The complete `canonical_request` object, including the `request_id` and `canonical_hash`, MUST be written to the RIO system's persistent data store.
8.  **Propagate Request ID:** The `request_id` is passed to the next protocol step (Risk Evaluation) to initiate the subsequent phase of the decision chain.

## 8. Decision Logic

The primary logic in this step is procedural and transformational, not decisional. The main conditional path is the validation of inputs.

| Condition                               | Action                                                                | 
| --------------------------------------- | --------------------------------------------------------------------- | 
| Any field from Section 6 is null or empty | Trigger `MissingRequiredField` failure condition. HALT processing.    | 
| Input data types do not match spec      | Trigger `InvalidDataFormat` failure condition. HALT processing.       | 
| All required fields are present and valid | Proceed with Processing Steps 3 through 8.                            | 

## 9. Failure Conditions

| Error Code           | Trigger                                                                                                | Required Action                                                                                                                                 | 
| -------------------- | ------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- | 
| `MissingRequiredField` | An input field listed in Section 6 is not present in the data received from the Origin Verification step. | The request MUST be rejected. A log entry detailing the missing field(s) SHALL be created. An error notification SHOULD be sent to the origin system. | 
| `InvalidDataFormat`  | An input field's data is not in the expected format (e.g., `parameters` is not a valid JSON object).     | The request MUST be rejected. A log entry detailing the malformed field(s) SHALL be created. An error notification SHOULD be sent to the origin system. | 
| `DuplicateRequestID` | The generated `request_id` already exists in the persistent data store (a highly improbable collision).    | The system MUST attempt to re-generate the `request_id` up to a maximum of 3 times. If it still fails, the request is rejected and a critical system error is logged. | 

## 10. Security Considerations

*   **Integrity:** The `canonical_hash` is the most critical security control in this step. It provides a strong guarantee that the request data has not been altered after its creation. Any downstream component MUST validate the integrity of the record by re-computing the hash and comparing it to the stored value.
*   **Uniqueness and Non-Repudiation:** The use of a UUIDv4 for the `request_id` ensures that each request is globally unique, preventing replay attacks where an old, valid request could be maliciously re-submitted. This unique ID is fundamental to the non-repudiation of the entire action chain.
*   **Input Validation:** All incoming data MUST be treated as untrusted. The normalization and validation process is a critical defense against injection attacks and other data-driven exploits. The system SHOULD NOT pass any raw input directly into the canonical record without sanitization.
*   **Hashing Algorithm:** The SHA-256 algorithm is the specified standard for computing the `canonical_hash`. Use of weaker algorithms is NOT permitted.

## 11. Audit Requirements

*   The full, final `canonical_request` object, including the `request_id` and `canonical_hash`, MUST be logged and stored in a way that is immutable and durable.
*   Any failure conditions encountered during this step, particularly `MissingRequiredField` or `InvalidDataFormat`, MUST be logged with the complete, problematic input data for forensic analysis.
*   The timestamp of the canonical request's creation SHALL be recorded.

## 12. Dependencies

*   **Upstream:** This protocol step is directly dependent on the successful completion of **Step 02: Origin Verification**. It cannot begin until it receives a verified data payload from that step.
*   **Downstream:** The successful creation of the canonical request is a prerequisite for **Step 04: Risk Evaluation**. The `request_id` generated in this step is the key that links all subsequent downstream steps (Risk Evaluation, Authorization, Execution, etc.) back to this original, verified request.

## 13. Example Flow

**Scenario:** An AI finance agent requests a $48,250 wire transfer to Meridian Industrial Supply for Invoice #INV-2026-03-1147.

1.  **Receive Verified Intake:** The Canonical Request Formation step receives the following verified data:
    *   `verified_origin`: `ai_agent:fin_ops_agent_007`
    *   `action_type`: `wire_transfer`
    *   `target_resource`: `account:meridian_industrial_supply`
    *   `parameters`: `{"amount": 48250, "currency": "USD", "destination_account": "987654321", "reference": "Invoice #INV-2026-03-1147"}`
    *   `business_reason`: `Payment for approved invoice #INV-2026-03-1147 for industrial supplies.`

2.  **Validate Required Fields:** All required fields are present and correctly formatted. Validation passes.

3.  **Generate Request ID:** The system generates a unique ID: `request_id: 2f1c4a9c-3b7e-4d8a-9c1f-8a7b6c5d4e3f`

4.  **Normalize Fields:** Fields are trimmed and normalized (no changes in this specific example, but the process runs regardless).

5.  **Construct Request Object:** The system assembles the pre-hash object:
    ```json
    {
      "request_id": "2f1c4a9c-3b7e-4d8a-9c1f-8a7b6c5d4e3f",
      "requested_by": "ai_agent:fin_ops_agent_007",
      "action_type": "wire_transfer",
      "target": "account:meridian_industrial_supply",
      "parameters": {
        "amount": 48250,
        "currency": "USD",
        "destination_account": "987654321",
        "reference": "Invoice #INV-2026-03-1147"
      },
      "business_reason": "Payment for approved invoice #INV-2026-03-1147 for industrial supplies.",
      "risk_context": {},
      "policy_context": {}
    }
    ```

6.  **Compute Canonical Hash:** The object is serialized deterministically and hashed using SHA-256, producing the hash: `canonical_hash: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (example hash).

7.  **Persist Record:** The final `canonical_request` object, now including the `canonical_hash`, is written to the database at `2026-03-24T10:02:15Z`.

8.  **Propagate Request ID:** The `request_id` `2f1c4a9c-3b7e-4d8a-9c1f-8a7b6c5d4e3f` is passed to the Risk Evaluation service to begin the next step.
