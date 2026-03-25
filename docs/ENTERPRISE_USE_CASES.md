# Enterprise Use Cases

**RIO — Real-World Governance Scenarios**

---

## Overview

RIO is designed to govern any consequential action taken by AI agents, automated workflows, or software systems on behalf of humans. The following use cases illustrate how the governed execution pipeline applies to real enterprise scenarios across finance, data management, infrastructure, identity, and multi-agent coordination.

Each use case follows the same pattern: a request enters the pipeline, policy and risk are evaluated, authorization is obtained (automatically or through human approval), the action is executed through an adapter, and a cryptographic receipt and ledger entry are produced.

---

## Use Case 1: Invoice Payment Approval

**Industry:** Finance, Accounts Payable

**Scenario:** An AI agent integrated with the accounts payable system identifies an invoice that is due for payment. The agent submits a `transfer_funds` request to RIO to initiate a wire transfer of $48,250 to the vendor's bank account.

### Pipeline Walkthrough

| Stage | What Happens |
|-------|-------------|
| **Intake** | The request is received with `user_id: ai_agent_ap`, `action: transfer_funds`, `parameters: {amount: 48250, recipient: "Vendor Corp", currency: "USD"}`. The AI agent's identity is resolved from the user registry. |
| **Classification** | The action is classified as `transfer_funds` with initial risk category HIGH (financial action above $10,000). |
| **Structured Intent** | Intent validation confirms all required fields are present: `amount`, `recipient`, `currency`. A canonical intent hash is computed. |
| **Policy** | Rule RULE-003 matches: "Transfers over $10,000 require manager or admin approval." Decision: REQUIRE_APPROVAL. |
| **Risk** | Risk score computed: base risk (5) + role risk for AI agent (2) + amount risk for $48,250 (3) = 10. Risk level: HIGH. |
| **Authorization** | The request is escalated to the approval queue. A human approver (the CFO, role: admin) reviews the request in the dashboard. The CFO sees the full context: who requested it, what amount, what risk score, why it was escalated. The CFO approves. An authorization token is issued. |
| **Execution Gate** | The token signature is verified. The nonce is consumed. The kill switch is not engaged. The request is dispatched to the HTTP adapter, which calls the payment gateway API. |
| **Receipt + Ledger** | A signed receipt is generated containing the intent hash, decision hash, and execution hash. A ledger entry is appended to the hash chain. |

### Governance Value

Without RIO, the AI agent would have initiated a $48,250 wire transfer with no human review, no audit trail, and no proof of authorization. With RIO, the transfer required explicit human approval from a sufficiently authorized individual, and the entire decision chain is cryptographically recorded.

---

## Use Case 2: Data Deletion Approval

**Industry:** Technology, Data Management, GDPR Compliance

**Scenario:** A data management system receives a GDPR "right to erasure" request from a customer. An automated workflow submits a `delete_data` request to RIO to permanently delete the customer's personal data from the production database.

### Pipeline Walkthrough

| Stage | What Happens |
|-------|-------------|
| **Intake** | Request received: `action: delete_data`, `parameters: {target: "customer_db", scope: "user_id=12345", reason: "GDPR erasure request"}`. |
| **Classification** | Classified as `delete_data` with initial risk category HIGH (irreversible data operation). |
| **Structured Intent** | Validates required fields: `target`, `scope`. Canonical intent hash computed. |
| **Policy** | Rule matches: "Data deletion requires admin approval." Decision: REQUIRE_APPROVAL. |
| **Risk** | Risk score: base risk (6) + role risk (1) + target risk for production database (3) = 10. Risk level: HIGH. |
| **Authorization** | Escalated to approval queue. The data protection officer (role: admin) reviews the request, confirms the GDPR basis, and approves. |
| **Execution Gate** | Token verified. Nonce consumed. Request dispatched to the file adapter with database deletion parameters. |
| **Receipt + Ledger** | Receipt generated. Ledger entry appended. The receipt serves as proof of compliant data deletion for GDPR audit purposes. |

### Governance Value

GDPR requires organizations to demonstrate that data deletion was performed in response to a valid request, by an authorized individual, with appropriate controls. The RIO receipt and ledger entry provide exactly this proof. If a regulator asks "How do you know this deletion was authorized?", the organization can produce the signed receipt, the approval record, and the ledger entry showing the full decision chain.

---

## Use Case 3: Deployment Approval

**Industry:** Technology, DevOps, Infrastructure

**Scenario:** A CI/CD pipeline completes a build and submits a deployment request to RIO to push the new version to the production environment. The deployment involves updating 12 microservices across three availability zones.

### Pipeline Walkthrough

| Stage | What Happens |
|-------|-------------|
| **Intake** | Request received: `action: http_request`, `parameters: {url: "https://deploy.internal/api/v1/release", method: "POST", body: {version: "2.4.1", services: 12, target: "production"}}`. |
| **Classification** | Classified as `http_request` targeting a production deployment endpoint. Risk category: HIGH. |
| **Structured Intent** | Validates required fields: `url`, `method`. Canonical intent hash computed. |
| **Policy** | Rule matches: "Production deployments require manager or admin approval." Decision: REQUIRE_APPROVAL. |
| **Risk** | Risk score: base risk (3) + target risk for production (4) + scope risk for 12 services (2) = 9. Risk level: HIGH. |
| **Authorization** | Escalated to approval queue. The engineering manager reviews the deployment manifest, confirms the build passed all tests, and approves. |
| **Execution Gate** | Token verified. Nonce consumed. Request dispatched to the HTTP adapter, which calls the deployment API. |
| **Receipt + Ledger** | Receipt generated with the deployment version, service count, and target environment. Ledger entry appended. |

### Governance Value

Production deployments are among the highest-risk operations in any technology organization. A failed deployment can cause outages, data loss, or security vulnerabilities. RIO ensures that every production deployment is explicitly authorized by a human with sufficient authority, and that the full context — what was deployed, who approved it, when it happened — is permanently recorded.

---

## Use Case 4: Access Provisioning

**Industry:** Enterprise IT, Identity and Access Management

**Scenario:** An HR onboarding system submits a request to provision a new employee's access to internal systems: email, Slack, the code repository, and the production database (read-only).

### Pipeline Walkthrough

| Stage | What Happens |
|-------|-------------|
| **Intake** | Request received: `action: http_request`, `parameters: {url: "https://iam.internal/api/provision", method: "POST", body: {employee_id: "emp_789", systems: ["email", "slack", "github", "prod_db_readonly"]}}`. |
| **Classification** | Classified as `http_request` targeting the IAM provisioning endpoint. Risk category: MEDIUM (standard onboarding). |
| **Structured Intent** | Validates required fields. Canonical intent hash computed. |
| **Policy** | Two rules evaluated. Rule for standard systems (email, Slack, GitHub): ALLOW. Rule for production database access: REQUIRE_APPROVAL. The most restrictive rule applies. Decision: REQUIRE_APPROVAL. |
| **Risk** | Risk score: base risk (3) + target risk for prod_db (3) = 6. Risk level: MEDIUM. |
| **Authorization** | Escalated to approval queue. The IT manager reviews the access request, confirms the employee's role justifies production database access, and approves. |
| **Execution Gate** | Token verified. Nonce consumed. Request dispatched to the HTTP adapter, which calls the IAM provisioning API. |
| **Receipt + Ledger** | Receipt generated listing all provisioned systems. Ledger entry appended. |

### Governance Value

Access provisioning is a common vector for privilege escalation. An automated system that provisions access without oversight could grant excessive permissions. RIO ensures that access to sensitive systems (production databases, admin panels, financial systems) requires explicit human approval, while routine access (email, messaging) can be auto-approved by policy.

---

## Use Case 5: Agent-to-Agent Control

**Industry:** AI Operations, Multi-Agent Systems

**Scenario:** A planning agent determines that a task requires delegating a sub-task to a specialized execution agent. The planning agent submits a request to RIO to authorize the execution agent to perform a specific action on its behalf.

### Pipeline Walkthrough

| Stage | What Happens |
|-------|-------------|
| **Intake** | Request received from `planning_agent_01`: `action: http_request`, `parameters: {url: "https://agent-hub.internal/api/delegate", method: "POST", body: {delegate_to: "execution_agent_03", task: "generate_financial_report", data_access: ["revenue_db", "expense_db"]}}`. |
| **Classification** | Classified as `http_request` involving agent delegation with data access. Risk category: HIGH (cross-agent delegation with database access). |
| **Structured Intent** | Validates required fields. Canonical intent hash computed. |
| **Policy** | Rule matches: "Agent-to-agent delegation with database access requires admin approval." Decision: REQUIRE_APPROVAL. |
| **Risk** | Risk score: base risk (3) + delegation risk (3) + data access risk (3) = 9. Risk level: HIGH. |
| **Authorization** | Escalated to approval queue. The operations admin reviews the delegation request, confirms that `execution_agent_03` is authorized for financial data, and approves. |
| **Execution Gate** | Token verified. Nonce consumed. Request dispatched to the HTTP adapter, which calls the agent hub's delegation API. |
| **Receipt + Ledger** | Receipt generated recording the delegation chain: which agent requested, which agent was delegated to, what data access was granted. Ledger entry appended. |

### Governance Value

As multi-agent systems become more common, the risk of uncontrolled agent-to-agent delegation grows. Without governance, a planning agent could delegate sensitive tasks to execution agents without human oversight, creating chains of automated decisions that no human reviewed. RIO ensures that every delegation is visible, authorized, and auditable, preventing the emergence of uncontrolled agent networks.

---

## Summary

| Use Case | Action Type | Risk Level | Approval Required | Governance Outcome |
|----------|------------|------------|-------------------|-------------------|
| Invoice Payment | `transfer_funds` | HIGH | Yes (CFO) | Financial action authorized, receipt proves compliance |
| Data Deletion | `delete_data` | HIGH | Yes (DPO) | GDPR-compliant deletion with audit proof |
| Deployment | `http_request` | HIGH | Yes (Eng Manager) | Production change authorized with full context |
| Access Provisioning | `http_request` | MEDIUM | Yes (IT Manager) | Sensitive access gated, routine access auto-approved |
| Agent Delegation | `http_request` | HIGH | Yes (Ops Admin) | Cross-agent delegation visible and controlled |

In every case, the pattern is the same: the action enters the pipeline, policy and risk are evaluated, authorization is obtained, the action is executed, and a cryptographic receipt and ledger entry are produced. The specific rules, thresholds, and approval requirements are configurable through the policy and risk versioning system, allowing each organization to adapt RIO to its own governance requirements.
