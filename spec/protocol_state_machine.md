# RIO Protocol State Machine Specification

## 1. Introduction

This document specifies the formal finite state machine for a RIO Protocol decision chain. The state machine defines the lifecycle of a request, from its initial intake to its final recording in the ledger. This specification adheres to the principles of fail-closed execution governance, ensuring that any request that does not complete the entire sequence successfully is ultimately denied.

This document uses RFC 2119 keywords (MUST, SHALL, SHOULD, MAY).

## 2. States

The RIO Protocol state machine is defined by the following set of states. Each state represents a distinct stage in the processing of a governed execution request.

*   **INTAKE_RECEIVED**: The initial state. A request has been received by the protocol but has not yet been processed.
*   **ORIGIN_VERIFIED**: The origin of the request has been cryptographically verified.
*   **REQUEST_CANONICALIZED**: The request has been converted into a canonical format.
*   **RISK_EVALUATED**: The risk associated with the request has been evaluated.
*   **POLICY_CHECKED**: The request has been checked against all applicable policies.
*   **PENDING_AUTHORIZATION**: The request is awaiting authorization from a human authority.
*   **AUTHORIZED**: The request has been authorized for execution.
*   **DENIED**: The request has been denied.
*   **EXECUTION_PENDING**: The request is queued for execution.
*   **EXECUTED**: The authorized action has been successfully executed.
*   **EXECUTION_FAILED**: The execution of the authorized action failed.
*   **ATTESTED**: The execution outcome has been attested to by the execution environment.
*   **RECEIPT_GENERATED**: A cryptographic receipt for the transaction has been generated.
*   **LEDGER_RECORDED**: The transaction has been recorded in the audit ledger.
*   **EXPIRED**: The request has expired due to a timeout.
*   **FAILED**: The request has entered a failed state due to a protocol error.

## 3. State Transitions

Transitions between states are triggered by the successful completion of a protocol step. All transitions are conditional and MUST only occur when the specified trigger condition is met.

*   `INTAKE_RECEIVED` → `ORIGIN_VERIFIED`: Triggered when the cryptographic signature of the incoming request is successfully verified against the originator's public key.
*   `ORIGIN_VERIFIED` → `REQUEST_CANONICALIZED`: Triggered when the request is successfully converted into its minified, sorted JSON canonical form.
*   `REQUEST_CANONICALIZED` → `RISK_EVALUATED`: Triggered when the risk evaluation process completes and a risk score is assigned.
*   `RISK_EVALUATED` → `POLICY_CHECKED`: Triggered when the request and its associated risk score are checked against all applicable policies and constraints.
*   `POLICY_CHECKED` → `PENDING_AUTHORIZATION`: Triggered when policy checks pass and the request requires human authorization.
*   `POLICY_CHECKED` → `DENIED`: Triggered when policy checks fail.
*   `PENDING_AUTHORIZATION` → `AUTHORIZED`: Triggered when a designated human authority provides a valid authorization signature.
*   `PENDING_AUTHORIZATION` → `DENIED`: Triggered when a designated human authority explicitly denies the request.
*   `AUTHORIZED` → `EXECUTION_PENDING`: Triggered immediately upon successful authorization.
*   `EXECUTION_PENDING` → `EXECUTED`: Triggered when the authorized action is executed successfully by the target system.
*   `EXECUTION_PENDING` → `EXECUTION_FAILED`: Triggered when the execution of the authorized action fails.
*   `EXECUTED` → `ATTESTED`: Triggered when the execution environment provides a signed attestation of the execution outcome.
*   `ATTESTED` → `RECEIPT_GENERATED`: Triggered when a cryptographic receipt, including the attestation and other transaction data, is generated.
*   `RECEIPT_GENERATED` → `LEDGER_RECORDED`: Triggered when the complete transaction record is successfully written to the audit ledger.

## 4. Terminal States

Terminal states represent the final resolution of a request. Once a request enters a terminal state, it cannot transition to any other state.

*   **LEDGER_RECORDED**: The request was successfully processed, executed, and recorded. This is the sole successful terminal state.
*   **DENIED**: The request was denied, either by policy or by a human authority.
*   **EXECUTION_FAILED**: The request was authorized, but the execution failed.
*   **EXPIRED**: The request was not processed to completion within the allotted time.
*   **FAILED**: A protocol-level error prevented the request from being processed.

## 5. Timeout Transitions

To ensure liveness and prevent requests from being stuck in an indeterminate state, the RIO Protocol MUST enforce time-bound authorization. Timeouts can cause transitions to the `EXPIRED` terminal state.

*   Any state awaiting an external event (e.g., `PENDING_AUTHORIZATION`, `EXECUTION_PENDING`) MUST have a configurable timeout.
*   If a timeout is exceeded, the state machine SHALL transition the request to the `EXPIRED` state.
*   `PENDING_AUTHORIZATION` → `EXPIRED`: Triggered if a human authority does not respond within the configured authorization window.
*   `EXECUTION_PENDING` → `EXPIRED`: Triggered if the execution environment does not confirm execution within the configured execution window.

## 6. State Transition Table

The following table provides a summary of all valid state transitions.

| Current State          | Trigger Condition                     | Next State              |
|------------------------|---------------------------------------|-------------------------|
| INTAKE_RECEIVED        | Origin signature verified             | ORIGIN_VERIFIED         |
| ORIGIN_VERIFIED        | Request canonicalized                 | REQUEST_CANONICALIZED   |
| REQUEST_CANONICALIZED  | Risk evaluation complete              | RISK_EVALUATED          |
| RISK_EVALUATED         | Policy checks complete (pass)         | POLICY_CHECKED          |
| POLICY_CHECKED         | Requires human authorization          | PENDING_AUTHORIZATION   |
| POLICY_CHECKED         | Policy check fails                    | DENIED                  |
| PENDING_AUTHORIZATION  | Human authorizes                      | AUTHORIZED              |
| PENDING_AUTHORIZATION  | Human denies                          | DENIED                  |
| PENDING_AUTHORIZATION  | Timeout                               | EXPIRED                 |
| AUTHORIZED             | -                                     | EXECUTION_PENDING       |
| EXECUTION_PENDING      | Execution successful                  | EXECUTED                |
| EXECUTION_PENDING      | Execution fails                       | EXECUTION_FAILED        |
| EXECUTION_PENDING      | Timeout                               | EXPIRED                 |
| EXECUTED               | Attestation received                  | ATTESTED                |
| ATTESTED               | Receipt generated                     | RECEIPT_GENERATED       |
| RECEIPT_GENERATED      | Record written to ledger              | LEDGER_RECORDED         |
| (Any)                  | Protocol error                        | FAILED                  |

## 7. State Diagram

The following diagram illustrates the state transitions of the RIO Protocol.

```
                      +-------------------+
                      | INTAKE_RECEIVED   |
                      +-------------------+
                              |
                              v
                      +-------------------+
                      | ORIGIN_VERIFIED   |
                      +-------------------+
                              |
                              v
                      +-----------------------+
                      | REQUEST_CANONICALIZED |
                      +-----------------------+
                              |
                              v
                      +-------------------+
                      | RISK_EVALUATED    |
                      +-------------------+
                              |
                              v
                      +-------------------+
                      | POLICY_CHECKED    |
                      +-------------------+
                              | 
            +-----------------+-----------------+
            |                                   |
            v                                   v
+-------------------------+                   +--------+
| PENDING_AUTHORIZATION   |                   | DENIED |
+-------------------------+                   +--------+
            |                                   ^
+-----------+-----------+                       |
|           |           |                       |
|           v           v                       |
|      +----------+  +---------+                |
|      |EXPIRED   |  |AUTHORIZED|                |
|      +----------+  +---------+                |
|                        |                      |
|                        v                      |
|           +--------------------+              |
|           | EXECUTION_PENDING  |              |
|           +--------------------+              |
|                        |                      |
|           +------------+-----------+          |
|           |            |           |          |
|           v            v           v          |
|  +----------------+ +---------+ +---------+   |
|  |EXECUTION_FAILED| | EXPIRED | | EXECUTED|   |
|  +----------------+ +---------+ +---------+   |
|           ^                        |           |
|           |                        v           |
|           |                 +----------+       |
|           |                 | ATTESTED |       |
|           |                 +----------+       |
|           |                        |           |
|           |                        v           |
|           |            +-------------------+   |
|           |            | RECEIPT_GENERATED |   |
|           |            +-------------------+   |
|           |                        |           |
|           |                        v           |
|           |            +-----------------+   |
|           |            | LEDGER_RECORDED |   |
|           |            +-----------------+   |
|           |                                    |
+-----------+------------------------------------+-----------------+
            |                                                      |
            v                                                      v
      +---------+                                              +------+
      | FAILED  |                                              | .... |
      +---------+                                              +------+

```

## 8. Invariants

The following invariants MUST hold true throughout the entire lifecycle of a request:

*   **Forward-Only Progression**: The state machine MUST NOT transition to a previous state in the standard execution path. For example, a transition from `RISK_EVALUATED` to `REQUEST_CANONICALIZED` is forbidden.
*   **No Skipped States**: Each state in the primary success path MUST be visited in sequence. A transition from `ORIGIN_VERIFIED` to `RISK_EVALUATED`, for instance, is not permitted as it skips the `REQUEST_CANONICALIZED` state.
*   **Immutable History**: Once a state is passed, the data generated in that state (e.g., the canonical request, the risk score) MUST NOT be altered in subsequent states.
*   **Authorization is Final**: Once a request is `AUTHORIZED`, it cannot be unauthorized. The only path forward is to `EXECUTION_PENDING`.
*   **Terminal States are Final**: Once a request enters a terminal state (`LEDGER_RECORDED`, `DENIED`, `EXECUTION_FAILED`, `EXPIRED`, `FAILED`), no further transitions are possible.

## 9. Error States and Recovery

Errors can occur at any point in the protocol. The `FAILED` state is a designated terminal state for capturing unrecoverable protocol errors.

*   Any state MAY transition to the `FAILED` state if a protocol-level error is detected (e.g., cryptographic verification failure, malformed data, database connection error).
*   The `FAILED` state indicates that the request could not be processed due to a system or protocol failure, not a user-level denial.
*   Recovery from a `FAILED` state is not possible for the given request. The system SHOULD log detailed diagnostic information to aid in debugging the root cause of the failure. The originator of the request MAY be notified of the failure and MAY choose to resubmit the request.
