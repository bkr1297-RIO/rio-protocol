
# RIO Protocol Specification: 14. Orchestration

## 1. Protocol Name
RIO Protocol Step 14: Orchestration

## 2. Purpose
This protocol defines the master control flow for the Runtime Intelligence Orchestration (RIO) decision chain. Its primary purpose is to coordinate the sequential and conditional execution of all other RIO Protocol steps, from intake to feedback. It acts as a state machine, managing the lifecycle of an AI-initiated action request, ensuring each step is executed in the correct order, handling state transitions, managing timeouts, and guaranteeing that the entire process either completes successfully or fails in a clean, predictable, and auditable manner.

## 3. Scope
**In Scope:**
-   Management of the state machine for a single `request_id`.
-   Sequential invocation of RIO Protocol steps 1 through 13.
-   Handling of success, failure, and timeout conditions for each step.
-   Passing of data records (e.g., `canonical_request`, `risk_evaluation`) between protocol steps.
-   Ensuring the integrity and order of the decision chain.

**Out of Scope:**
-   The internal logic or processing of any individual protocol step (e.g., how risk is calculated in Step 4).
-   The underlying transport mechanism for data records.
-   Long-term storage of audit logs or records, which is the responsibility of the Audit Ledger (Step 9).
-   The execution of the action itself, which is handled by the Execution protocol (Step 7).

## 4. Inputs
The Orchestration protocol is initiated by the Intake protocol and subsequently receives inputs from each protocol step it invokes.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `request_id` | String | Yes | The unique identifier for the action request, received from the Intake protocol. |
| `protocol_step_output` | JSON | Yes | The complete output record from the previously executed protocol step. |
| `protocol_step_status` | Enum | Yes | The status of the previous step (`SUCCESS`, `FAILURE`, `PENDING_AUTHORIZATION`). |

## 5. Outputs
The Orchestration protocol produces a final state for the request and ensures all generated records are routed to the Audit Ledger.

| Field | Type | Description |
| :--- | :--- | :--- |
| `final_request_status` | Enum | The terminal state of the request (`COMPLETED`, `FAILED`, `REJECTED`). |
| `full_decision_chain` | Array | An ordered collection of all records generated during the process (e.g., `canonical_request`, `risk_evaluation`, `authorization_record`). |

## 6. Required Fields
For the Orchestration protocol to proceed from one step to the next, it MUST receive a valid status and the corresponding output record from the currently executing step.

| Field | Required For | Description |
| :--- | :--- | :--- |
| `request_id` | Initialization | Must be present to start the orchestration flow. |
| `protocol_step_status` | State Transition | Must be present to determine the next state in the machine. |

## 7. Processing Steps
1.  **Initiation:** The Orchestration protocol is initiated upon the successful completion of the Intake protocol (Step 1), which provides the `request_id` and the initial `canonical_request` object.
2.  **State Initialization:** The orchestrator initializes a state machine for the `request_id`, setting the initial state to `PENDING_ORIGIN_VERIFICATION`.
3.  **Sequential Invocation:** The orchestrator proceeds to invoke each protocol step in the defined sequence (2 through 13).
4.  **State Transition:** After each step, the orchestrator receives the `protocol_step_status` and `protocol_step_output`.
    -   If the status is `SUCCESS`, the orchestrator transitions the state machine to the next step in the sequence and passes the required inputs.
    -   If the status is `FAILURE`, the orchestrator immediately transitions the state to `FAILED`, halts further processing, and proceeds to Step 6.
    -   If the status is `PENDING_AUTHORIZATION` (from Step 5), the orchestrator enters a waiting state until the Authorization protocol (Step 6) provides a definitive `authorization_record`.
5.  **Timeout Management:** The orchestrator MUST implement a timeout for each step. If a step does not return a status within the configured timeout period, it is treated as a `FAILURE`.
6.  **Finalization:** Upon reaching a terminal state (`COMPLETED`, `FAILED`, `REJECTED`), the orchestrator assembles the `full_decision_chain` by collecting all generated records.
7.  **Hand-off to Ledger:** The orchestrator passes the `full_decision_chain` and `final_request_status` to the Audit Ledger protocol (Step 9) and the Learning Feedback protocol (Step 10).
8.  **Termination:** The orchestration for the `request_id` is now complete.

## 8. Decision Logic
The core logic is a finite state machine. The primary decision is based on the `protocol_step_status` returned by each invoked step.

| Current State | Input Status | Next State | Action |
| :--- | :--- | :--- | :--- |
| Any | `SUCCESS` | `PENDING_<NEXT_STEP>` | Invoke the next protocol step in the sequence. |
| Any | `FAILURE` | `FAILED` | Halt execution, proceed to Finalization. |
| `PENDING_POLICY` | `PENDING_AUTHORIZATION` | `AWAITING_AUTHORIZATION` | Wait for output from Authorization protocol (Step 6). |
| `AWAITING_AUTHORIZATION` | `SUCCESS` (Approved) | `PENDING_EXECUTION` | Invoke Execution protocol (Step 7). |
| `AWAITING_AUTHORIZATION` | `FAILURE` (Rejected) | `REJECTED` | Halt execution, proceed to Finalization. |

## 9. Failure Conditions

| Error Code | Trigger | Required Action |
| :--- | :--- | :--- |
| `ORCH-F-01` | A protocol step returns a `FAILURE` status. | Halt all further processing. Set `final_request_status` to `FAILED`. Log the failure source and reason. |
| `ORCH-F-02` | A protocol step invocation times out. | Halt all further processing. Set `final_request_status` to `FAILED`. Log the timeout event and the timed-out step. |
| `ORCH-F-03` | An invalid or unexpected state transition is attempted. | Halt all further processing. Set `final_request_status` to `FAILED`. This indicates a critical internal error that requires investigation. |

## 10. Security Considerations
-   The orchestrator itself MUST be a highly privileged and isolated component, as it governs the entire decision flow.
-   State transition logic MUST be protected from tampering. Any unauthorized change to the state machine could bypass critical security checks like risk evaluation or authorization.
-   The orchestrator SHALL NOT modify any of the data records it passes between steps. It acts as a router, not a data manipulator.
-   Communication channels between the orchestrator and the individual protocol step endpoints MUST be mutually authenticated and encrypted to prevent man-in-the-middle attacks.

## 11. Audit Requirements
-   Every state transition for a given `request_id` MUST be logged with a timestamp.
-   The start and end of each protocol step invocation MUST be logged.
-   All timeout events and failures, including the specific step that failed, MUST be logged in detail.
-   The final, ordered `full_decision_chain` is the ultimate audit artifact produced by the orchestration and MUST be delivered to the Audit Ledger.

## 12. Dependencies
-   **Upstream:** The Orchestration protocol depends on the **Intake** protocol (Step 1) to initiate a request.
-   **Downstream:** All other protocols (Steps 2-13) are downstream dependencies, as the orchestrator invokes them. The **Audit Ledger** (Step 9) and **Learning Feedback** (Step 10) are the final downstream consumers of the completed orchestration flow.

## 13. Example Flow
**Scenario:** AI agent requests a $48,250 wire transfer to Meridian Industrial Supply.

1.  **Initiation:** The Intake protocol provides the orchestrator with `request_id: "8a7d6f5e-4b3c-2a1b-9d8e-7f6a5b4c3d2e"` and the `canonical_request.json` object.
2.  **State Transition:** Orchestrator sets state to `PENDING_ORIGIN_VERIFICATION` and invokes Protocol Step 2.
3.  **Sequential Execution:** Steps 2 (Origin Verification) and 3 (Canonical Request) execute and return `SUCCESS`.
4.  **Risk Evaluation:** Step 4 (Risk Evaluation) runs and returns `SUCCESS`, along with the `risk_evaluation.json` record showing `risk_level: "HIGH"` and `risk_score: 82`.
5.  **Policy Constraints & Authorization:** Step 5 (Policy Constraints) evaluates the high-risk score and returns `PENDING_AUTHORIZATION`. The orchestrator transitions the state to `AWAITING_AUTHORIZATION`.
6.  **Wait State:** The orchestrator invokes Step 6 (Authorization) and waits. CFO Sarah Mitchell approves. Step 6 returns `SUCCESS` with the `authorization_record.json` where `decision: "APPROVED"`.
7.  **State Transition:** The orchestrator receives the approval, transitions the state to `PENDING_EXECUTION`, and invokes Step 7 (Execution).
8.  **Execution & Attestation:** Step 7 (Execution) performs the wire transfer and returns `SUCCESS`. Step 8 (Attestation) cryptographically seals the records and returns `SUCCESS`.
9.  **Finalization:** The orchestrator has now completed the main flow. It invokes Step 9 (Audit Ledger), passing the complete chain of records. It then invokes Step 10 (Learning Feedback).
10. **Termination:** The orchestrator sets `final_request_status: "COMPLETED"` for request `8a7d6f5e-4b3c-2a1b-9d8e-7f6a5b4c3d2e` and terminates the process. The entire flow from intake to completion took 1.8 seconds. The timeout for the human authorization step was set to 5 minutes, but was completed in 45 seconds.
