# RIO Protocol Specification: 11_independence

## 1. Protocol Name
RIO Protocol Step 11: Independence

## 2. Purpose
The Independence protocol is a cross-cutting architectural requirement that ensures the RIO control plane operates with complete structural and operational separation from the AI agents and systems it governs. Its purpose is to guarantee the integrity and neutrality of the governance process by preventing any entity under RIO's purview from influencing, bypassing, tampering with, or gaining privileged insight into the decision chain. This separation is fundamental to the trust and security of the entire RIO framework.

## 3. Scope
This protocol covers the mandatory architectural principles, separation boundaries, communication interfaces, and isolation requirements for all components within the RIO control plane. It defines the required logical and, where necessary, physical separation between the "Governance Plane" (RIO core services) and the "Agent Plane" (the AI agents, applications, and systems initiating actions).

What is explicitly out of scope are the specific underlying technologies used to achieve this isolation (e.g., specific container orchestration platforms, service mesh implementations, or cloud provider services). The protocol defines the required state of independence, not the implementation details for achieving it.

## 4. Inputs
This protocol is structural and does not process transactional data. Its inputs are the system's architectural configurations and runtime policies that enforce separation.

| Field | Type | Required | Description |
|---|---|---|---|
| Network Policies | Configuration | Yes | Rules defining allowed traffic flow between the Agent Plane and the Governance Plane. |
| Service Identities | Credentials | Yes | Unique, verifiable identities for every service in both planes (e.g., SPIFFE/SVID). |
| API Gateway Config | Configuration | Yes | The single, strictly defined entry point for all incoming requests from the Agent Plane. |
| IAM Policies | Configuration | Yes | Least-privilege access control policies for all system components and service accounts. |

## 5. Outputs
This protocol's output is not a data record but a continuously enforced state of operational integrity and isolation.

| Field | Type | Description |
|---|---|---|
| Enforced System State | State | A runtime condition where the Governance Plane is verifiably isolated from the Agent Plane. |
| Access Denials | Log Event | A stream of log events generated whenever an improper access attempt across the boundary is blocked. |

## 6. Required Fields
This protocol mandates required architectural properties rather than data fields in a record.

| Property | Requirement |
|---|---|
| Single Entry Point | All communication from the Agent Plane to the Governance Plane MUST pass through a single, designated API Gateway. |
| Unidirectional Initiation | Communication MUST be initiated from the Agent Plane to the Governance Plane. Direct initiation from Governance to Agent is forbidden, except for pre-defined callback patterns. |
| Separate Credentials | Service accounts and credentials for the Agent Plane MUST be distinct from those in the Governance Plane. |
| Immutable Infrastructure | Core RIO components SHOULD be deployed on immutable infrastructure to prevent configuration drift. |

## 7. Processing Steps
1.  **Boundary Definition:** The system architecture SHALL clearly define the network and logical boundary between the Agent Plane and the Governance Plane.
2.  **Ingress Enforcement:** The RIO API Gateway is deployed as the sole ingress point. All other ingress paths to the Governance Plane MUST be disabled.
3.  **Identity Verification:** Upon receiving a request at the gateway, the identity of the calling agent or service MUST be cryptographically verified (e.g., via mTLS or signed JWT).
4.  **Request Validation:** The gateway SHALL validate that the request conforms to the `canonical_request.json` schema. Any non-conforming request is immediately rejected.
5.  **Internal Routing:** Once validated, the request is passed to the RIO Intake service. All subsequent communication between RIO core services (Intake, Risk, Auth, etc.) MUST occur on a private, isolated network segment inaccessible to the Agent Plane.
6.  **Egress Control:** Communication from the Governance Plane to external systems (e.g., the final execution of a wire transfer) MUST pass through a controlled egress point that enforces its own authentication and authorization checks.
7.  **Continuous Monitoring:** The system MUST continuously monitor for and log any network traffic that violates the defined policies.

## 8. Decision Logic
The decision logic for this protocol is binary and absolute, focused on access control at the boundary.

| Condition | Action | Justification |
|---|---|---|
| Request to Governance Plane does NOT originate from the API Gateway. | **BLOCK** | All traffic must pass through the single, controlled entry point. |
| Identity of the calling agent cannot be verified. | **BLOCK** | Only trusted and authenticated agents may submit requests. |
| A service in the Governance Plane attempts to initiate a connection to a service in the Agent Plane. | **BLOCK** | Prevents internal services from being compromised and used to attack agents. |
| An agent attempts to call an internal RIO service directly (e.g., the Risk Evaluation service). | **BLOCK** | Protects the integrity and confidentiality of the internal decision-making process. |

## 9. Failure Conditions
Failures in this protocol represent a critical security breach.

| Error Code | Trigger | Required Action |
|---|---|---|
| `INDEPENDENCE_BREACH_01` | A network packet from the Agent Plane is detected on the internal Governance Plane network. | **HALT & ALERT.** Immediately halt processing on the affected node. Generate a P0 security alert. Isolate the source agent. |
| `INDEPENDENCE_BREACH_02` | A core RIO service's configuration is modified by an unauthorized process. | **HALT & ALERT.** Revert the change from the source of truth. Trigger a P1 security alert. Initiate a full audit of the component. |
| `INDEPENDENCE_BREACH_03` | An agent successfully bypasses the API Gateway and calls an internal service. | **HALT & ALERT.** Immediately terminate the connection. Generate a P0 security alert. The compromised internal service MUST be shut down and re-provisioned. |

## 10. Security Considerations
- **Mutual TLS (mTLS):** All service-to-service communication within the Governance Plane and at the API Gateway boundary MUST be secured with mTLS to ensure authenticated, encrypted transport.
- **Principle of Least Privilege:** Service accounts for RIO components MUST have the minimum permissions required for their function. They SHALL NOT have broad administrative access.
- **Network Segmentation:** The Agent Plane and Governance Plane MUST reside in separate, non-overlapping network segments (e.g., different VPCs or subnets with strict firewall rules).
- **Immutable Deployments:** Core RIO services SHOULD be deployed as immutable artifacts (e.g., container images). Any changes MUST result in a new deployment, not a modification of a running instance.
- **Configuration as Code:** All network policies, IAM roles, and gateway configurations MUST be managed as code in a version-controlled repository with mandatory peer review for changes.

## 11. Audit Requirements
- All accepted and rejected connection attempts at the API Gateway MUST be logged with their source, destination, identity, and timestamp.
- Any change to a network policy, firewall rule, or IAM role governing the RIO planes MUST be logged, attributed to a specific user or process, and stored in an immutable log store.
- The system SHALL periodically (e.g., every 24 hours) run an automated verification process that confirms the integrity of the separation boundaries and logs a signed attestation of the current state.

## 12. Dependencies
- **Upstream:** This protocol is foundational. It depends on the underlying infrastructure (cloud provider, container orchestrator) providing the necessary tools for network and identity management.
- **Downstream:** All other RIO protocol steps (1-10) are critically dependent on the guarantees provided by the Independence protocol. A failure in Independence invalidates the entire decision chain.

## 13. Example Flow
In the $48,250 wire transfer scenario, the principle of Independence is demonstrated as follows:

1.  **Agent Action:** The AI finance agent, running in the Agent Plane, constructs a `canonical_request.json` object for the wire transfer. It does **not** have access to the bank's API or any internal RIO services.
    - `request_id`: `d8f2a3b1-4e7c-4b8a-9f0d-3e5c6a7b8d9e`
    - `action_type`: `WIRE_TRANSFER`
    - `target`: `urn:bank:api:v1:transfer`
2.  **Boundary Crossing:** The agent makes a single, authenticated HTTPS call to the RIO API Gateway's public endpoint (e.g., `https://rio.api.acmecorp.com/v1/actions`). Its identity is verified by the gateway via a client certificate or signed JWT.
3.  **Isolation:** The gateway forwards the request to the Intake service. From this point on, the entire process is opaque to the agent. The agent has no network path or credentials to access the Risk Evaluation, Authorization, or Execution services, which are running in a private subnet.
4.  **Internal Processing:** The RIO services communicate over an internal, mTLS-secured service mesh. The Risk Evaluation service determines the high risk, and the Authorization service manages the workflow to get CFO Sarah Mitchell's approval. The agent cannot observe or interfere with this internal traffic.
5.  **Controlled Egress:** After receiving the signed `authorization_record.json`, the RIO Execution service, which resides in a secure egress segment, is the only component with the credentials to call the bank's payment API. It executes the wire transfer.
6.  **No Bypass:** If the AI finance agent had attempted to call the bank's API directly, the request would have been blocked by a network firewall, as the agent's service account is not authorized for that egress path. If it had attempted to call the RIO Risk Evaluation service directly, the call would have been rejected at the network level before it could even be processed.
