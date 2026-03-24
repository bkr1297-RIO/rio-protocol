# RIO Protocol Specification: 06_authorization

## 1. Protocol Name

RIO Protocol Step 06: Authorization

## 2. Purpose

This protocol step orchestrates the human decision-making process for an AI-initiated action. Following a comprehensive risk evaluation, the Authorization step engages a designated human or authorized entity to provide explicit approval, denial, or conditional approval for the action to proceed. Its primary purpose is to serve as a critical control point, ensuring that high-risk, sensitive, or exceptional actions are subject to human oversight and accountability before execution. This step produces a verifiable, cryptographically signed `authorization_record` that serves as immutable proof of the decision.

## 3. Scope

This protocol's scope covers the entire lifecycle of the authorization decision. This includes:

*   Receiving an authorization request, which is triggered by the outcome of the preceding Risk Evaluation and Policy Constraints steps.
*   Identifying and notifying the required authorizing party or parties.
*   Presenting the `canonical_request` and `risk_evaluation` details in a human-readable format.
*   Capturing the decision (Approve, Deny, Conditionally Approve).
*   Supporting various authorization methods, including multi-party approval, time-bound decisions, and biometric verification.
*   Generating and signing the final `authorization_record.json`.

Explicitly out of scope for this protocol step are:

*   The execution of the action itself, which is handled by the subsequent Execution step.
*   The evaluation of risk or the application of policy rules, which are upstream dependencies.
*   The long-term storage and archival of audit records, which is the responsibility of the Audit Ledger.

## 4. Inputs

This protocol step receives the `canonical_request` and the `risk_evaluation` records. These inputs provide the complete context required for an informed human decision.

| Field                 | Type          | Required | Description                                                                                             | 
| --------------------- | ------------- | -------- | ------------------------------------------------------------------------------------------------------- | 
| `request_id`          | `UUID`        | Yes      | The unique identifier from the `canonical_request` to link the entire decision chain.                   | 
| `risk_evaluation_id`  | `UUID`        | Yes      | The unique identifier from the `risk_evaluation` record.                                                | 
| `risk_level`          | `String`      | Yes      | The assessed risk level (e.g., `Low`, `Medium`, `High`, `Critical`).                                      | 
| `risk_score`          | `Integer`     | Yes      | The numerical risk score (e.g., 0-100).                                                                 | 
| `policy_flags`        | `Array`       | No       | Any policy flags that mandate human authorization (e.g., `requires_cfo_approval`).                      | 
| `recommendation`      | `String`      | Yes      | The system's recommendation based on risk and policy (e.g., `RequiresHumanAuthorization`).            | 
| `full_request_object` | `JSON`        | Yes      | The complete `canonical_request.json` object for full context review by the authorizing party.        | 

## 5. Outputs

This protocol's primary output is the `authorization_record`, which formally documents the decision and its context.

| Field                  | Type          | Description                                                                                             | 
| ---------------------- | ------------- | ------------------------------------------------------------------------------------------------------- | 
| `authorization_id`     | `UUID`        | A new unique identifier for this specific authorization event.                                          | 
| `request_id`           | `UUID`        | The identifier of the original request being authorized.                                                | 
| `risk_evaluation_id`   | `UUID`        | The identifier of the risk evaluation that triggered this authorization.                                | 
| `decision`             | `String`      | The outcome of the authorization. MUST be one of `Approved`, `Denied`, or `ConditionallyApproved`.      | 
| `authorized_by`        | `String`      | An identifier for the human or entity that made the decision (e.g., user ID, role name).              | 
| `authorization_method` | `String`      | The method used for authorization (e.g., `MobileBiometric`, `MultiParty`, `Password`).                | 
| `expires_at`           | `Timestamp`   | An optional timestamp indicating when the authorization is no longer valid.                             | 
| `conditions`           | `JSON`        | An optional object specifying constraints for a `ConditionallyApproved` decision.                       | 
| `signature`            | `String`      | A cryptographic signature over the contents of the `authorization_record` to ensure integrity.          | 

## 6. Required Fields

The following fields MUST be present in the output `authorization_record` for it to be considered valid.

| Field                | Description                                                                 | 
| -------------------- | --------------------------------------------------------------------------- | 
| `authorization_id`   | Uniquely identifies the authorization event.                                | 
| `request_id`         | Links the authorization back to the original action request.                | 
| `risk_evaluation_id` | Links the authorization to the specific risk assessment performed.          | 
| `decision`           | The definitive outcome of the authorization process.                        | 
| `authorized_by`      | Specifies who made the decision, ensuring accountability.                   | 
| `signature`          | Guarantees the authenticity and integrity of the record.                    | 

## 7. Processing Steps

1.  **Initiation**: The protocol is initiated upon receiving a valid `request_id` and `risk_evaluation_id` where the risk assessment or policy dictates human intervention.
2.  **Authority Identification**: The system identifies the required authorizing party or parties based on the `policy_context` from the `canonical_request` and internal organizational hierarchies.
3.  **Notification**: The identified authority is notified via a secure, pre-configured channel (e.g., mobile push notification, email, dedicated dashboard alert).
4.  **Context Presentation**: The system presents a clear, human-readable summary of the `canonical_request` and the key findings from the `risk_evaluation` to the authority.
5.  **Decision Capture**: The authority submits their decision (`Approved`, `Denied`, or `ConditionallyApproved`). If conditional, they MUST provide the specific constraints.
6.  **Authentication**: The authority's identity is verified using the specified `authorization_method` (e.g., prompting for a biometric scan).
7.  **Record Generation**: An `authorization_record` is created, populating all fields based on the captured decision and context.
8.  **Signing**: The generated `authorization_record` is serialized into a canonical JSON format, hashed, and cryptographically signed by the RIO system's authorization module.
9.  **Propagation**: The signed `authorization_record` is passed downstream to the Execution protocol step and upstream to the Audit Ledger.

## 8. Decision Logic

The core decision is made by the human authority. The system's logic is focused on routing and enforcing the outcome.

| Decision                 | Condition                                                                                             | System Action                                                                                                                              | 
| ------------------------ | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | 
| `Approved`               | The authority explicitly approves the request.                                                        | The protocol concludes successfully. The `authorization_record` with `decision: "Approved"` is passed to the Execution step.               | 
| `Denied`                 | The authority explicitly denies the request.                                                          | The protocol concludes. The `authorization_record` with `decision: "Denied"` is logged, and the action is terminated. No execution occurs. | 
| `ConditionallyApproved`  | The authority approves the request subject to specific, machine-readable constraints (e.g., time limits). | The protocol concludes successfully. The `authorization_record` with `decision: "ConditionallyApproved"` and populated `conditions` is passed to the Execution step, which MUST enforce the conditions. | 

## 9. Failure Conditions

| Error Code          | Trigger                                                                                                  | Required Action                                                                                                                            | 
| ------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | 
| `AUTH_TIMEOUT`      | The designated authority fails to respond within the configured time window.                             | The request is automatically denied. An `authorization_record` is generated with `decision: "Denied"` and `authorized_by: "System"`. | 
| `AUTH_INVALID_SIG`  | The signature provided by the authority's authentication method fails verification.                      | The authorization attempt is rejected. The authority MAY be prompted to try again, up to a configured limit.                             | 
| `AUTH_REJECTED`     | The authority actively rejects the authentication challenge (e.g., cancels a biometric prompt).          | The authorization attempt is rejected. The request remains in a pending state until it times out.                                        | 
| `AUTH_NO_AUTHORITY` | The system cannot identify a valid, available authority to handle the request based on policy.         | The request is automatically denied. An `authorization_record` is generated with `decision: "Denied"` and `authorized_by: "System"`. | 

## 10. Security Considerations

*   **Authentication Strength**: The `authorization_method` SHOULD be commensurate with the risk level of the action. High-risk actions MUST require strong authentication, such as multi-factor or biometric verification.
*   **Signature Integrity**: The final `authorization_record` MUST be signed using a strong, industry-standard asymmetric cryptographic algorithm (e.g., ECDSA with P-256). The signature ensures the record cannot be tampered with after the decision is made.
*   **Secure Communication**: All communications with the authorizing authority, including notifications and decision capture, MUST occur over encrypted channels (e.g., TLS 1.3).
*   **Replay Prevention**: The `authorization_id` and associated timestamps help prevent replay attacks. An authorization record, once used for execution, SHALL NOT be usable for a second execution.
*   **Time-Bound Authorization**: The `expires_at` field MUST be used for high-risk transactions to limit the window of opportunity for an approved action to be executed, mitigating risks from stale approvals.

## 11. Audit Requirements

To ensure full traceability and non-repudiation, the following MUST be logged:

*   The complete, signed `authorization_record.json` MUST be stored in the Audit Ledger.
*   A log of all notification attempts (successful and failed) to the designated authorities.
*   The specific timing of when the request was presented to the authority and when the decision was rendered.
*   Any metadata associated with the authentication process, such as the type of biometric factor used, without exposing the raw biometric data itself.

## 12. Dependencies

*   **Upstream**: This protocol step is dependent on the **Policy Constraints** step. It is triggered only if policy rules determine that human authorization is required for the given `request_id` and `risk_evaluation_id`.
*   **Downstream**: The **Execution** step is dependent on this protocol. It SHALL NOT proceed with performing an action unless it receives a valid, signed `authorization_record` with a decision of `Approved` or `ConditionallyApproved`.

## 13. Example Flow

**Scenario**: An AI finance agent requests a $48,250 wire transfer to Meridian Industrial Supply. The risk evaluation scores it 82/100 (High) and flags it for mandatory CFO approval.

1.  **Initiation**: The Authorization protocol receives `request_id: "uuid-request-123"` and `risk_evaluation_id: "uuid-risk-456"`. The risk score of 82 triggers the process.
2.  **Authority Identification**: Policy rules identify the `CFO` role as the required authority. The system maps this to user `smitchell` (Sarah Mitchell).
3.  **Notification**: A push notification is sent to Sarah Mitchell's registered mobile device: "Authorization Required: Wire Transfer of $48,250 to Meridian Industrial Supply. Risk: High (82/100)."
4.  **Context Presentation**: Sarah opens the notification and is shown the full request details: amount, recipient, invoice number, and business reason. She also sees the key risk factors identified.
5.  **Decision Capture**: Sarah assesses the request and decides to approve it, but wants to ensure it is executed quickly. She chooses `ConditionallyApproved`.
6.  **Authentication**: The system prompts for biometric confirmation. Sarah uses her phone's Face ID. The authentication is successful.
7.  **Record Generation**: The system generates the `authorization_record` with the following key values:
    *   `authorization_id`: `"uuid-auth-789"`
    *   `request_id`: `"uuid-request-123"`
    *   `risk_evaluation_id`: `"uuid-risk-456"`
    *   `decision`: `"ConditionallyApproved"`
    *   `authorized_by`: `"smitchell"`
    *   `authorization_method`: `"MobileBiometric"`
    *   `expires_at`: `"2026-03-24T14:05:00Z"` (5 minutes from approval time)
    *   `conditions`: `{ "max_execution_delay_seconds": 300 }`
8.  **Signing**: The RIO authorization service signs the complete JSON object of the record, producing a signature string.
9.  **Propagation**: The signed `authorization_record` is sent to the Execution module to proceed with the wire transfer, which must now be completed within 5 minutes.
