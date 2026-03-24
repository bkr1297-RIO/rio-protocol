# RIO Protocol Specification: 15_time_bound_authorization

## 1. Protocol Name
RIO Protocol Step 15: Time-Bound Authorization

## 2. Purpose
This protocol defines the rules and mechanisms for creating and enforcing time-bound authorizations within the RIO decision chain. Its primary purpose is to mitigate the risks associated with indefinitely valid approvals by ensuring that an authorization, once granted, is only valid for a specific, predefined time window. This step is critical for time-sensitive actions where the context or risk profile may change rapidly, ensuring that execution can only occur when the approval is recent and relevant.

## 3. Scope
**In Scope:**
*   The specification of an `expires_at` timestamp within an `authorization_record.json`.
*   The logic for validating the timeliness of an authorization at the execution gate.
*   The cryptographic enforcement of time-bound constraints.
*   The rejection of execution requests that reference an expired `authorization_record.json`.

**Out of Scope:**
*   The mechanism for determining the duration of the time window itself. This is considered a policy decision set during the policy definition phase.
*   The user interface or methods for displaying the remaining validity period to the authorizer or operator.
*   The process of re-authorizing a request after a previous authorization has expired.

## 4. Inputs
This protocol step primarily receives the `authorization_record.json` after it has been created.

| Field             | Type      | Required | Description                                                                 |
| ----------------- | --------- | -------- | --------------------------------------------------------------------------- |
| `authorization_record.json` | JSON      | Yes      | The complete authorization record, which MUST contain the `expires_at` field. |

## 5. Outputs
This protocol does not produce a new record. It provides a validation result to the execution step.

| Field             | Type      | Description                                                                 |
| ----------------- | --------- | --------------------------------------------------------------------------- |
| Validation Result | Boolean   | `true` if the authorization is valid, `false` if it has expired.              |

## 6. Required Fields
The following fields MUST be present in the `authorization_record.json` for this protocol to be enforced:

| Field        | Type      | Description                                      |
| ------------ | --------- | ------------------------------------------------ |
| `expires_at` | Timestamp | The timestamp when the authorization becomes invalid. |

## 7. Processing Steps
1.  The Execution step receives a request to perform an action, referencing an `authorization_id`.
2.  The Execution step retrieves the corresponding `authorization_record.json`.
3.  The system MUST read the `expires_at` timestamp from the `authorization_record.json`.
4.  The system MUST compare the `expires_at` timestamp with the current system time.
5.  If the current time is after the `expires_at` time, the authorization is considered expired.
6.  The Execution step MUST reject the execution request if the authorization has expired.

## 8. Decision Logic
| Condition                                       | Action                                         |
| ----------------------------------------------- | ---------------------------------------------- |
| Current Time <= `expires_at`                    | Proceed with execution.                        |
| Current Time > `expires_at`                     | Reject execution and trigger a failure condition. |

## 9. Failure Conditions
| Error Code | Trigger                                 | Required Action                                                               |
| ---------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| 403.1      | Authorization has expired.              | Reject the execution request and log the failure.                             |

## 10. Security Considerations
*   The `expires_at` timestamp MUST be cryptographically signed as part of the `authorization_record.json` to prevent tampering.
*   The system time used for comparison MUST be synchronized with a reliable time source to prevent timing attacks.
*   The time-bound authorization mechanism helps prevent replay attacks by ensuring that an authorization cannot be used after its validity period.

## 11. Audit Requirements
*   The `expires_at` timestamp MUST be included in the audit ledger.
*   Any failed execution attempts due to an expired authorization MUST be logged for security and compliance reviews.

## 12. Dependencies
*   **Upstream:** This protocol depends on the **Authorization** step to create the `authorization_record.json` with the `expires_at` field.
*   **Downstream:** The **Execution** step depends on this protocol to validate the timeliness of the authorization before performing the action.

## 13. Example Flow
An AI finance agent requests a $48,250 wire transfer. The RIO system evaluates it as high risk and requires human authorization. CFO Sarah Mitchell approves the request via her mobile device.

*   **Authorization Record Creation:**
    *   `authorization_id`: `auth-cfo-98765`
    *   `request_id`: `req-fin-12345`
    *   `decision`: `approved`
    *   `authorized_by`: `sarah.mitchell@example.com`
    *   `authorization_method`: `mobile_biometric`
    *   `expires_at`: `2026-03-24T14:05:00Z` (5 minutes after approval at 14:00:00Z)

*   **Execution Attempt 1 (within the time window):**
    *   **Time:** `2026-03-24T14:03:00Z`
    *   The Execution step retrieves the `authorization_record.json`.
    *   The system compares the current time (`14:03:00Z`) with the `expires_at` time (`14:05:00Z`).
    *   The authorization is valid, and the wire transfer is executed successfully.

*   **Execution Attempt 2 (outside the time window):**
    *   **Time:** `2026-03-24T14:06:00Z`
    *   The Execution step retrieves the `authorization_record.json`.
    *   The system compares the current time (`14:06:00Z`) with the `expires_at` time (`14:05:00Z`).
    *   The authorization has expired.
    *   The Execution step rejects the request, logs a failure condition (Error Code 403.1), and does not proceed with the wire transfer.
