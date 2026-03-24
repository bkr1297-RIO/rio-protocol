# RIO Protocol Role Model

## 1. Overview

The RIO Protocol is designed to provide a secure and auditable framework for AI-initiated actions. A fundamental principle of this framework is the separation of duties, which is enforced through a well-defined Role Model. Role separation is critical for AI governance as it prevents the concentration of power within a single entity, thereby mitigating the risk of unauthorized or malicious actions. By distributing responsibilities across distinct roles, the RIO Protocol ensures that every action is subject to a series of checks and balances, from its inception to its final attestation. This model is essential to establishing trust, accountability, and robust security in autonomous systems.

This document defines the roles within the RIO system, their separation, and the rules that govern their interactions. The keywords "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

## 2. Role Definitions

Each role in the RIO Protocol has a specific set of responsibilities, permissions, and restrictions. These are defined as follows:

### Requester

*   **Description:** The Requester is an AI agent or automated system that proposes an action to be taken.
*   **Responsibilities:** The Requester is responsible for creating a `canonical_request` that accurately and completely describes the proposed action.
*   **Permissions:** A Requester MAY propose actions. It MAY also hold other roles, subject to the conflict rules defined in this document.
*   **Restrictions:** A Requester MUST NOT act as the Authorizer for its own requests.

### Risk Evaluator

*   **Description:** The Risk Evaluator is a service or engine that assesses the potential risks associated with a proposed action.
*   **Responsibilities:** The Risk Evaluator is responsible for generating a `risk_evaluation` record based on the `canonical_request`.
*   **Permissions:** A Risk Evaluator MAY access the `canonical_request` and any relevant contextual data to perform its assessment.
*   **Restrictions:** The Risk Evaluator SHOULD be an independent service to ensure an unbiased assessment.

### Policy Engine

*   **Description:** The Policy Engine is a service that evaluates a proposed action against a set of organizational policies and constraints.
*   **Responsibilities:** The Policy Engine is responsible for determining whether an action complies with all applicable policies and generating a `policy_constraints` record.
*   **Permissions:** The Policy Engine MAY access the `canonical_request` and organizational policy definitions.
*   **Restrictions:** The Policy Engine MUST enforce policies as written and MUST NOT have the ability to alter them.

### Authorizer

*   **Description:** The Authorizer is a human or a delegated authority that approves or denies a proposed action.
*   **Responsibilities:** The Authorizer is responsible for reviewing the `canonical_request`, `risk_evaluation`, and `policy_constraints` to make an informed decision. The decision is recorded in an `authorization_record`.
*   **Permissions:** An Authorizer MAY approve or deny requests. An Authorizer MAY delegate their authority as per the delegation rules.
*   **Restrictions:** An Authorizer MUST NOT be the Requester for the same request. Authorization MUST be based on strong authentication methods.

### Executor

*   **Description:** The Executor is the service that performs the authorized action.
*   **Responsibilities:** The Executor is responsible for carrying out the action as specified in the `authorization_record` and generating an `execution_record`.
*   **Permissions:** The Executor MAY perform the action only after a valid `authorization_record` is produced.
*   **Restrictions:** The Executor MUST NOT be the Attestor for the same action chain. The Executor MUST perform the action exactly as authorized.

### Attestor

*   **Description:** The Attestor is a service that produces a cryptographic attestation of the entire action chain.
*   **Responsibilities:** The Attestor is responsible for verifying the integrity of the traceability chain and creating an `attestation_record`.
*   **Permissions:** The Attestor MAY access all records in the traceability chain.
*   **Restrictions:** The Attestor MUST NOT be the Executor for the same action chain. The Attestor MUST be a trusted and secure service.

### Auditor

*   **Description:** The Auditor is an entity that reviews the audit trail for compliance, security, and accuracy.
*   **Responsibilities:** The Auditor is responsible for examining the `ledger_entry` and all associated records to ensure the protocol is functioning correctly.
*   **Permissions:** An Auditor MAY have read-only access to the entire audit ledger.
*   **Restrictions:** An Auditor SHOULD be an independent entity, separate from the operational roles.

### Meta-Governor

*   **Description:** The Meta-Governor is the entity that has the authority to modify the rules and policies of the RIO Protocol itself.
*   **Responsibilities:** The Meta-Governor is responsible for the `meta-governance` protocol, including updates to the policy engine's rules, role definitions, and other core components.
*   **Permissions:** The Meta-Governor MAY modify the protocol's governance rules.
*   **Restrictions:** Changes made by the Meta-Governor MUST be subject to their own authorization process, ensuring that no single entity can unilaterally alter the system's foundations.

## 3. Role Separation Matrix

To enforce the separation of duties, the following matrix defines which roles can be held by the same entity. A 'No' indicates that two roles MUST NOT be held by the same entity for the same action chain.

| Role            | Requester | Risk Evaluator | Policy Engine | Authorizer | Executor | Attestor | Auditor | Meta-Governor |
|-----------------|-----------|----------------|---------------|------------|----------|----------|---------|---------------|
| **Requester**   | -         | Yes            | Yes           | No         | Yes      | Yes      | Yes     | Yes           |
| **Risk Evaluator**| Yes       | -              | Yes           | Yes        | Yes      | Yes      | Yes     | Yes           |
| **Policy Engine** | Yes       | Yes            | -             | Yes        | Yes      | Yes      | Yes     | Yes           |
| **Authorizer**  | No        | Yes            | Yes           | -          | Yes      | Yes      | No      | Yes           |
| **Executor**    | Yes       | Yes            | Yes           | Yes        | -        | No       | Yes     | Yes           |
| **Attestor**    | Yes       | Yes            | Yes           | Yes        | No       | -        | Yes     | Yes           |
| **Auditor**     | Yes       | Yes            | Yes           | No         | Yes      | Yes      | -       | No            |
| **Meta-Governor**| Yes       | Yes            | Yes           | Yes        | Yes      | Yes      | No      | -             |

## 4. Conflict Rules

The following specific conflict rules MUST be enforced:

*   A Requester MUST NOT be the Authorizer for the same request. This is a critical control to prevent self-approval of actions.
*   An Executor MUST NOT be the Attestor for the same action chain. This ensures that the entity performing the action is not the same one that verifies its integrity.
*   An Auditor SHOULD NOT hold any other role in an operational capacity to maintain independence.
*   A Meta-Governor SHOULD NOT be an Auditor to avoid conflicts of interest in overseeing the system they can change.

## 5. Role Assignment

Roles are assigned to entities (users, services, or systems) through a secure administrative process. Each role assignment MUST be cryptographically signed and recorded in the audit ledger. Role verification SHALL be performed at each step of the traceability chain. Roles SHOULD be reviewed periodically, and rotation of roles is RECOMMENDED for sensitive positions to reduce the risk of collusion or compromise.

## 6. Delegation Rules

An Authorizer MAY delegate their authority to another entity. Any delegation of authority MUST be time-bound and specific to a certain type or class of action. The delegation itself MUST be an authorized action and recorded in the audit ledger. The delegate acts on behalf of the original Authorizer, and the original Authorizer remains ultimately responsible. The `authorization_record` MUST clearly indicate if the authorization was performed by a delegate.

## 7. Example: Role Assignment in the Wire Transfer Scenario

In the example of a $48,250 wire transfer, the roles would be assigned as follows:

*   **Requester:** The AI finance agent that initiated the wire transfer request.
*   **Risk Evaluator:** A dedicated risk management service that analyzes the transaction for signs of fraud or anomaly.
*   **Policy Engine:** The corporate expense policy service that checks if the payment amount and recipient are within the defined policy rules.
*   **Authorizer:** The CFO, Sarah Mitchell, who provides approval via Face ID.
*   **Executor:** The bank's API service that executes the wire transfer.
*   **Attestor:** A dedicated RIO Protocol service that cryptographically signs the entire transaction record.
*   **Auditor:** The company's internal audit team or an external regulatory body.
*   **Meta-Governor:** The RIO Protocol governance board responsible for updating the protocol's rules.
