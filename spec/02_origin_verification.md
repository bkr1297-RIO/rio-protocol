## 1. Protocol Name

RIO Protocol Step 02: Origin Verification

## 2. Purpose

This protocol step verifies the identity and authenticity of the entity that submitted the action request. It ensures that the requester is a known, registered, and trusted entity with valid credentials. The primary purpose of this step is to prevent unauthorized or spoofed requests from entering the RIO decision chain. By attaching verified identity metadata, it provides a trusted foundation for all subsequent evaluation and authorization steps.

## 3. Scope

This protocol step is responsible for the verification of the requester's origin and identity. This includes, but is not limited to, checking digital signatures, validating API keys or tokens, and cross-referencing the requester's details against a trusted entity registry.

Explicitly out of scope for this protocol step is the analysis of the *content* or *intent* of the request itself. The risk, policy, and authorization evaluation of the action's parameters and purpose are handled by downstream protocol steps.

## 4. Inputs

This protocol step receives the raw, unverified action request from the Intake step.

| Field | Type | Required | Description |
|---|---|---|---|
| `request_payload` | JSON | Yes | The complete, unmodified request body as received by the intake listener. |
| `source_metadata` | JSON | Yes | Metadata about the request's origin, such as source IP address, TLS client certificate details, and HTTP headers. |
| `intake_timestamp` | ISO 8601 | Yes | The timestamp when the request was first received by the RIO system. |

## 5. Outputs

Upon successful verification, this protocol step produces a verified origin record.

| Field | Type | Description |
|---|---|---|
| `verified_origin_record_id` | UUID | A unique identifier for this verification event. |
| `request_id` | UUID | The `request_id` from the initial intake, passed through for correlation. |
| `verified_entity_id` | String | The unique identifier of the authenticated entity from the trusted registry. |
| `verification_method` | String | The method used for verification (e.g., `API_KEY_HMAC`, `MTLS`, `JWT_SIGNATURE`). |
| `verification_timestamp` | ISO 8601 | The timestamp when the origin was successfully verified. |
| `is_trusted_origin` | Boolean | A flag indicating if the origin is fully trusted. `true` if verification is successful, `false` otherwise. |
| `original_request` | JSON | The original `request_payload` is carried forward to the next step. |

## 6. Required Fields

The following fields MUST be present in the input for the Origin Verification step to proceed.

| Field | Source | Description |
|---|---|---|
| `request_payload` | Intake | The body of the request. |
| `source_metadata` | Intake | The metadata of the request's origin. |

## 7. Processing Steps

1.  The protocol receives the `request_payload` and `source_metadata` from the Intake step.
2.  It parses the `source_metadata` to determine the presented authentication method (e.g., presence of an `Authorization` header, a client certificate).
3.  Based on the method, it selects the appropriate verification routine.
4.  **For API Key/Secret:** The protocol extracts the API key and signature from the headers. It retrieves the corresponding secret from a secure vault, reconstructs the signature payload from the request body and timestamp, and compares the computed HMAC signature with the provided signature. A match verifies the request.
5.  **For mTLS:** The protocol inspects the client certificate provided during the TLS handshake. It SHALL verify that the certificate is signed by a trusted Certificate Authority and is not expired or revoked. The Subject of the certificate is used to identify the entity.
6.  **For JWT:** The protocol extracts the JSON Web Token from the `Authorization` header. It SHALL validate the signature of the token against the known public key of the issuer, check the `exp` (expiration) and `nbf` (not before) claims, and verify the `iss` (issuer) and `aud` (audience) claims against configured values.
7.  Upon successful validation, the protocol queries the internal Entity Registry using the verified identity (e.g., API key, certificate subject, or JWT `sub` claim).
8.  It confirms the entity is in an `active` state and has the necessary permissions to submit action requests.
9.  The protocol then constructs the `verified_origin_record` as specified in the Outputs section, setting `is_trusted_origin` to `true`.
10. This output record is then passed to the Canonical Request formation step.

## 8. Decision Logic

The decision logic for this step is binary: the origin is either verified or it is not.

| Condition | Result |
|---|---|
| Authentication credentials are valid (e.g., signature matches, certificate is valid, JWT is verified). | **Proceed** |
| AND the authenticated entity exists in the registry and is `active`. | |
| Authentication credentials are invalid (e.g., signature mismatch, expired certificate, invalid JWT). | **Fail** |
| OR the authenticated entity is not found in the registry, is `inactive`, or lacks submission permissions. | **Fail** |

## 9. Failure Conditions

If the origin cannot be verified, the request MUST NOT proceed. The system SHALL generate a failure record and MAY notify the originating system.

| Error Code | Trigger | Required Action |
|---|---|---|
| `OV-001` | Invalid Signature | The computed signature does not match the signature provided in the request. | Log the failure, reject the request with a `401 Unauthorized` status, and increment a counter for the source IP/entity. |
| `OV-002` | Expired Credentials | The provided token, certificate, or key has expired. | Log the failure, reject the request with a `401 Unauthorized` status. |
| `OV-003` | Unknown Entity | The credentials are valid, but the entity is not found in the registry. | Log the failure, reject the request with a `403 Forbidden` status. |
| `OV-004` | Inactive Entity | The entity is found but is marked as inactive or disabled. | Log the failure, reject the request with a `403 Forbidden` status. |

## 10. Security Considerations

-   All secrets, such as API secret keys and private keys for signing JWTs, MUST be stored in a secure, encrypted, and access-controlled vault.
-   Transport-level security (TLS 1.2 or higher) MUST be enforced for all incoming requests to protect data in transit.
-   To mitigate replay attacks, requests SHOULD include a timestamp or a nonce that is validated by the server. Signatures SHOULD include this value to bind it to the request.
-   Rate limiting SHOULD be applied to source IP addresses and/or entities to prevent brute-force attacks on authentication endpoints.
-   The comparison of signatures or other cryptographic material MUST be done using constant-time comparison functions to prevent timing attacks.

## 11. Audit Requirements

-   A log entry MUST be created for every verification attempt, both successful and failed.
-   For successful verifications, the log MUST include the `verified_entity_id`, `verification_method`, and `verification_timestamp`.
-   For failed verifications, the log MUST include the reason for failure (e.g., `invalid_signature`), the source IP address, and any available (but unverified) identity information.
-   These logs form part of the immutable audit trail and are referenced in the final `attestation_record`.

## 12. Dependencies

-   **Upstream:** This protocol step depends on the **01_Intake** step to receive the raw request.
-   **Downstream:** The **03_Canonical_Request_Formation** step depends on the successful output of this protocol. Without a `verified_origin_record`, the canonical request cannot be formed.

## 13. Example Flow

**Scenario:** An AI finance agent requests a $48,250 wire transfer.

1.  **Input:** The RIO intake listener receives a request at `2026-03-12T10:00:05Z`. The request includes an `Authorization` header: `HMAC-SHA256 ApiKey=FINANCE-AI-001, Signature=abc123def456...`.
2.  **Processing:**
    *   The Origin Verification step identifies the `HMAC-SHA256` authentication scheme.
    *   It extracts the `ApiKey`: `FINANCE-AI-001`.
    *   It retrieves the corresponding shared secret for `FINANCE-AI-001` from the secure vault.
    *   It reconstructs the message to be signed using the request body and timestamp.
    *   It computes its own HMAC-SHA256 signature and compares it to the provided `Signature`. The signatures match.
    *   It looks up `FINANCE-AI-001` in the Entity Registry and confirms its status is `active`.
3.  **Decision:** The origin is successfully verified.
4.  **Output:** The protocol generates the following record:
    *   `verified_origin_record_id`: `f47ac10b-58cc-4372-a567-0e02b2c3d479`
    *   `request_id`: `a1b2c3d4-e5f6-7890-1234-567890abcdef` (from Intake)
    *   `verified_entity_id`: `FINANCE-AI-001`
    *   `verification_method`: `API_KEY_HMAC`
    *   `verification_timestamp`: `2026-03-12T10:00:06Z`
    *   `is_trusted_origin`: `true`
    *   `original_request`: `{ "action_type": "wire_transfer", ... }`
5.  **Next Step:** This verified record is passed to the Canonical Request Formation step to be processed further.
