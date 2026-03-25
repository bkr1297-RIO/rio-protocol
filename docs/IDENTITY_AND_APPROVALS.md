# Identity and Approvals

**RIO — Users, Roles, Permissions, and the Approval Workflow**

---

## Overview

The identity layer manages who can request actions, who can approve them, and what each role is permitted to do. It enforces the principle that no single actor can both request and authorize their own actions (INV-06: No Self-Authorization), and that approval authority is strictly bounded by role level and organizational hierarchy.

---

## Users

Users are stored in `runtime/data/users.json`. Each user record contains:

| Field | Type | Description |
|-------|------|-------------|
| `user_id` | String | Unique identifier (e.g., `user_001`) |
| `name` | String | Display name |
| `email` | String | Email address |
| `role` | String | Assigned role (intern, employee, auditor, manager, admin) |
| `active` | Boolean | Whether the user can submit requests |

The user registry is loaded at system startup by the IAM module (`runtime/iam/users.py`). The intake stage resolves the requester's identity and role from this registry before any policy evaluation occurs. Requests from unknown or inactive users are rejected at intake.

---

## Roles

Roles define a five-level hierarchy with increasing authority. Role definitions are stored in `runtime/data/roles.json` and managed by `runtime/iam/roles.py`.

| Role | Level | Description |
|------|-------|-------------|
| **Intern** | 1 | Minimal permissions. Cannot perform financial actions. Cannot approve any requests. |
| **Employee** | 2 | Standard operations. Can perform most non-financial actions. Cannot approve requests. |
| **Auditor** | 2 | Read-only audit access. Can view the ledger, receipts, and corpus. Cannot execute actions or approve requests. |
| **Manager** | 3 | Approval authority for standard operations. Can approve requests from employees and interns. Cannot approve requests from other managers or admins. |
| **Admin** | 4 | Full system access. Can approve any request. Can manage policy and risk model versions. Can engage the kill switch. |

The role hierarchy is used in two ways. First, the policy engine uses the requester's role to determine which rules apply. Second, the approval system uses the approver's role level to determine whether they have sufficient authority to approve a given request.

---

## Permissions

The permissions matrix is stored in `runtime/data/permissions.json` and managed by `runtime/iam/permissions.py`. It maps each role to a set of capabilities:

| Capability | Intern | Employee | Auditor | Manager | Admin |
|-----------|--------|----------|---------|---------|-------|
| Submit requests | Yes | Yes | No | Yes | Yes |
| Execute actions | Limited | Yes | No | Yes | Yes |
| View ledger | No | No | Yes | Yes | Yes |
| Approve requests | No | No | No | Yes | Yes |
| Manage policy | No | No | No | No | Yes |
| Manage risk model | No | No | No | No | Yes |
| Kill switch | No | No | No | No | Yes |

The permissions system is checked at multiple points in the pipeline. The intake stage verifies that the user has permission to submit requests. The policy engine checks role-specific rules. The approval manager verifies that the approver has sufficient authority. The governance API verifies admin role for policy and risk management operations.

---

## Approval Workflow

When the policy engine returns a decision of ESCALATE (REQUIRE_APPROVAL), the request enters the approval workflow managed by `runtime/approvals/approval_manager.py`.

### Workflow Steps

**Step 1: Approval Request Created.** The pipeline creates an `ApprovalRequest` object containing the full intent, policy decision, risk assessment, and requester identity. The request is added to the approval queue (`runtime/approvals/approval_queue.py`) and persisted to `runtime/data/approvals.jsonl`. The pipeline halts with status PENDING_APPROVAL.

**Step 2: Human Review.** A manager or admin reviews the pending request through the dashboard or API. The reviewer sees the full context: what action is being requested, by whom, what risk score it received, and why the policy escalated it.

**Step 3: Decision.** The reviewer either approves or denies the request.

**Approve path:** The approval manager generates an authorization token with the approver's identity, a unique nonce, and an expiration timestamp. The pipeline resumes from the execution gate. The action is dispatched to the appropriate adapter, and a receipt and ledger entry are generated.

**Deny path:** The approval manager generates a denial receipt with the denier's identity and reason. A ledger entry is created. The action is not executed.

### Approval Constraints

The approval system enforces several constraints:

**No self-approval.** The approver must be a different user than the requester. This is protocol invariant INV-06. If a manager submits a request that requires approval, only a different manager or an admin can approve it.

**Role level requirement.** The approver's role level must be sufficient for the action type. Managers can approve standard operations. Only admins can approve high-risk or governance-related actions.

**Time-bound authorization.** When an approval generates an authorization token, the token has a default expiration of 300 seconds. If the execution gate does not consume the token within that window, it expires and the request must be re-approved.

**Single-use nonce.** Each authorization token contains a unique nonce that can be consumed exactly once. This prevents replay attacks where a captured token is submitted multiple times.

### Approval Queue

The approval queue (`runtime/approvals/approval_queue.py`) maintains the list of pending requests. It provides methods to:

- List all pending requests
- Get a specific request by ID
- Record an approval decision
- Record a denial decision
- Query approval history

Approval decisions are persisted to `runtime/data/approvals.jsonl` for audit purposes.

---

## Authorization Tokens

When a request is authorized — either directly by the policy engine (ALLOW) or through human approval — an authorization token is generated by `runtime/authorization.py`.

### Token Structure

| Field | Type | Description |
|-------|------|-------------|
| `authorization_id` | UUID | Unique identifier |
| `intent_hash` | SHA-256 hex | Hash of the canonical intent (binds token to specific request) |
| `authorizer_id` | String | Identity of the authorizer (system for auto-allow, human for approval) |
| `nonce` | UUID | Single-use nonce for replay prevention |
| `issued_at` | ISO 8601 | When the token was issued |
| `expires_at` | ISO 8601 | When the token expires (default: 300 seconds after issuance) |
| `signature` | Base64 | ECDSA signature over the token content |

### Token Lifecycle

1. **Issuance.** The token is generated with all fields and signed.
2. **Presentation.** The token is passed to the execution gate.
3. **Verification.** The gate verifies the signature, checks expiration, and validates the intent hash matches.
4. **Consumption.** The gate consumes the nonce (marks it as used in the nonce registry).
5. **Execution.** The action proceeds.

A token can only be used once. After the nonce is consumed, any attempt to reuse the token is rejected.

---

## Sessions

The session manager (`runtime/iam/sessions.py`) handles user authentication state for the dashboard. Sessions are token-based and time-limited. Session management is separate from the authorization token system — sessions authenticate users to the dashboard, while authorization tokens authorize specific actions through the execution gate.

---

## References

| Specification | Location |
|--------------|----------|
| Role Model | `spec/role_model.md` |
| Authorization Protocol | `spec/06_authorization.md` |
| Time-Bound Authorization | `spec/15_time_bound_authorization.md` |
| Users Implementation | `runtime/iam/users.py` |
| Roles Implementation | `runtime/iam/roles.py` |
| Permissions Implementation | `runtime/iam/permissions.py` |
| Approval Manager | `runtime/approvals/approval_manager.py` |
| Authorization Module | `runtime/authorization.py` |
| User Data | `runtime/data/users.json` |
| Role Data | `runtime/data/roles.json` |
| Permissions Data | `runtime/data/permissions.json` |
