
# Constraints vs. Policies in the RIO Protocol

## 1. Overview

In the RIO Protocol, the terms "policy" and "constraint" define two distinct but related mechanisms for governing AI-initiated actions. A clear understanding of this distinction is critical for implementers to build secure, predictable, and compliant systems. Policies serve as general rules that reflect the organization's risk appetite and operational guidelines, while constraints provide specific, one-time limitations on how an authorized action is to be executed. Misinterpreting these concepts can lead to improperly secured systems, where broad permissions are granted without sufficient fine-grained control, or where inflexible rules hinder operational agility. This document provides an authoritative explanation of these two concepts, their interaction, and best practices for their implementation within the RIO ecosystem.

## 2. Definitions

### Policy

A **Policy** is a high-level rule or set of rules defined by an organization to govern whether an AI-initiated action, or class of actions, SHOULD be allowed, denied, or escalated for human review. Policies are declarative statements that codify an organization's governance principles and risk tolerance. They are evaluated by the RIO Protocol during the `risk_evaluation` and `policy_constraints` steps of the traceability chain, before an authorization decision is made. Policies are designed to be durable and are updated through the `meta-governance` protocol, ensuring that changes to the rule set are themselves subject to authorization and audit.

**Examples:**
- "All wire transfers exceeding $50,000 MUST require explicit approval from a Chief Financial Officer (CFO) role."
- "AI agents SHALL NOT be permitted to send emails to external domains without prior review by a human operator."
- "Automated infrastructure scaling actions MUST be limited to a 25% increase in resource allocation within a 24-hour period."

### Constraint

A **Constraint** is a specific, immutable condition attached to a single `authorization_record` by a human or automated authorizer at the moment of approval. Constraints dictate the precise boundaries within which an authorized action MUST be executed. They are enforced by the `execution_gate` and are valid only for the single transaction they are associated with. Once an `authorization_record` is created and cryptographically signed, its constraints cannot be modified. This ensures that the conditions under which an action was approved are strictly honored at the time of execution.

**Examples:**
- "This wire transfer MUST be executed within the next 5 minutes."
- "The final transaction amount for this payment SHALL NOT exceed $48,250."
- "This command to provision a new server MAY only be executed between 10:00 PM and 11:00 PM UTC."

## 3. Comparison Table

| Dimension | Policy | Constraint |
| :--- | :--- | :--- |
| **Scope** | Broad, applies to a class of actions (e.g., all payments). | Narrow, applies to a single, specific action instance. |
| **Lifecycle** | Persistent and long-lived, until explicitly updated via governance. | Ephemeral and transactional, valid for one execution only. |
| **Who Sets It** | Organization's governance body or administrators. | The authorizer (human or system) at the time of approval. |
| **When Evaluated**| Before authorization, during `risk_evaluation`. | After authorization, enforced by the `execution_gate`. |
| **Where Enforced**| Policy engine during the decision-making process. | The execution environment or a dedicated `execution_gate`. |
| **Mutability** | Mutable through a formal `meta-governance` process. | Immutable once the `authorization_record` is signed. |
| **Examples** | "No deployments on Fridays." | "This specific deployment MUST be completed by 3:00 PM." |

## 4. How They Interact in the RIO Pipeline

The RIO Protocol orchestrates the evaluation of policies and the enforcement of constraints in a precise sequence to ensure security and compliance. The process is as follows:

1.  **Canonical Request**: An AI agent submits a `canonical_request` to perform an action (e.g., initiate a payment).
2.  **Policy Evaluation**: The request is evaluated against the set of active policies. The policy engine determines if the request complies with all relevant organizational rules. For instance, a request for a $60,000 payment would trigger a policy requiring CFO approval.
3.  **Authorization Decision**: Based on the policy evaluation, the request is routed for authorization. A designated human, such as CFO Sarah Mitchell, reviews the request.
4.  **Constraints Attached**: Upon approval, the authorizer attaches one or more constraints to the `authorization_record`. Sarah Mitchell might approve the $48,250 payment but add a constraint that it MUST be executed within 5 minutes and that the recipient MUST be "Meridian Industrial Supply."
5.  **Execution**: The `authorization_record`, now containing the immutable constraints, is sent to the `execution_gate`.
6.  **Constraint Enforcement**: The `execution_gate` validates the cryptographic signature of the record and then strictly enforces every constraint. If the current time is outside the 5-minute window or if the recipient account differs, the execution MUST fail. This is a fail-closed design.

This sequence ensures that broad organizational rules are satisfied before any action is even considered for approval, and that every approved action is executed under the exact conditions intended by the authorizer.

## 5. Examples

### Example 1: Financial Transaction

*   **Scenario**: An AI-powered financial management agent requests to pay an invoice of $48,250 to a new vendor, "Meridian Industrial Supply."
*   **Policy**: "All payments to new vendors MUST be approved by a Level 2 manager. All payments over $25,000 MUST be approved by a CFO."
*   **Interaction**: The policy engine first identifies that the vendor is new and the amount exceeds the CFO threshold, escalating the request to CFO Sarah Mitchell. Sarah reviews the invoice and approves the payment.
*   **Constraints**: During authorization, Sarah attaches the following constraints: `{"max_amount": "48250.00", "currency": "USD", "recipient_account": "Meridian Industrial Supply", "expires_at": "2026-03-24T18:05:00Z"}`. The execution gate will only proceed if the payment is for the exact amount (or less), to the correct recipient, and occurs before the expiration timestamp.

### Example 2: External Communication

*   **Scenario**: A customer support AI agent drafts an email to a user containing a password reset link.
*   **Policy**: "AI agents SHALL NOT send emails containing sensitive links or attachments to external users without human review."
*   **Interaction**: The policy engine flags the email content as sensitive and routes it to a human support supervisor for review.
*   **Constraints**: The supervisor approves the email but adds a constraint: `{"valid_for_clicks": 1, "link_expires_at": "2026-03-24T19:00:00Z"}`. The email system, acting as the execution gate, would be responsible for generating a single-use link that expires at the specified time.

### Example 3: Cloud Infrastructure Scaling

*   **Scenario**: An automated monitoring system detects a surge in web traffic and requests to scale up the number of web servers from 10 to 15.
*   **Policy**: "Automated resource scaling SHALL NOT exceed a 50% increase in capacity without manual approval from a Site Reliability Engineer (SRE)." "No scaling operations are permitted during a code freeze."
*   **Interaction**: The request is for a 50% increase, which is at the boundary of the policy. Assuming no code freeze is active, the policy allows the action to proceed to an SRE for approval.
*   **Constraints**: The on-call SRE approves the scaling action but adds a constraint to prevent runaway costs: `{"max_instances": 15, "monitor_duration_minutes": 60}`. The infrastructure-as-code execution gate will provision the 5 new instances but is also instructed to trigger a new evaluation after 60 minutes, preventing the new capacity from becoming permanent without further review.

## 6. Implementation Guidance

Implementers of the RIO Protocol SHOULD adhere to the following guidance to ensure correct and secure handling of policies and constraints.

### Implementing Policies

*   **Declarative Rules**: Policies SHOULD be stored in a declarative format such as JSON, YAML, or a dedicated policy language (e.g., Rego). This separates policy logic from application code, making policies easier to manage, audit, and update.
*   **Version Control**: Policy files MUST be stored in a version control system. Changes to policies MUST be managed through the `meta-governance` protocol, which creates an auditable trail of all modifications.
*   **Policy Engine**: A centralized policy engine SHOULD be used to evaluate requests against the policy set. This ensures consistent application of rules across the system.

### Implementing Constraints

*   **Embed in Authorization**: Constraints MUST be embedded directly within the `authorization_record` data structure before it is cryptographically signed by the authorizer. This makes them an immutable part of the authorization itself.
*   **Strict Enforcement**: The `execution_gate` MUST be designed to parse and strictly enforce every constraint in the `authorization_record`. Any failure to meet a constraint MUST result in a failed execution (fail-closed).
*   **Standardized Schema**: It is highly recommended to use a standardized JSON Schema for common constraints (e.g., `expires_at`, `max_amount`). This promotes interoperability between different components in the RIO ecosystem.

## 7. Common Mistakes

When implementing RIO, developers and architects SHOULD avoid these common anti-patterns:

*   **Confusing Policies and Constraints**: Do not use policies to enforce transactional, one-time conditions. For example, using a policy to limit a payment to a specific dollar amount is incorrect; this is the role of a constraint.
*   **Hardcoding Policies in Code**: Embedding policy logic directly into the source code of services is a significant anti-pattern. This makes policies difficult to change, audit, or reason about, defeating the purpose of a decoupled governance layer.
*   **Ignoring Constraint Enforcement**: An `execution_gate` that validates the signature of an `authorization_record` but does not enforce the constraints within it is critically flawed. The gate MUST treat constraints as mandatory conditions for execution.
*   **Mutable Constraints**: Allowing constraints to be modified after an `authorization_record` has been signed breaks the cryptographic guarantees of the protocol. Constraints MUST be immutable post-authorization.
*   **Vague Definitions**: Using vague or ambiguous language in policies or constraints can lead to unpredictable behavior. Definitions SHOULD be precise and machine-readable where possible.

