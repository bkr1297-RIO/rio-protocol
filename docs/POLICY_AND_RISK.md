# Policy and Risk

**RIO — Policy Engine, Risk Engine, and Governance Versioning**

---

## Overview

The policy and risk layer is the decision-making core of RIO. It determines whether a given action should be allowed, denied, or escalated to a human approver. The layer consists of two engines — the **policy engine** and the **risk engine** — that operate independently but produce a combined decision. Both engines are configurable through versioned rule files, and all changes to those rules follow a governed workflow with full audit trail.

---

## Policy Engine

The policy engine (`runtime/policy/policy_engine.py`) evaluates a canonical intent against a set of organizational rules. Rules are loaded from `runtime/policy/policy_rules.json` and evaluated in priority order.

### Rule Structure

Each policy rule contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | String | Unique rule identifier (e.g., `RULE-001`) |
| `action` | String | The action type this rule applies to (e.g., `transfer_funds`, `*` for all) |
| `role` | String | The role this rule applies to (e.g., `intern`, `employee`, `*` for all) |
| `decision` | String | ALLOW, DENY, or REQUIRE_APPROVAL |
| `condition` | Object | Optional condition evaluated against intent parameters |
| `priority` | Integer | Lower numbers are evaluated first |
| `description` | String | Human-readable explanation of the rule |

### Evaluation Logic

The engine evaluates rules in ascending priority order. For each rule, it checks whether the action type and role match the intent. If a condition is specified, it is evaluated against the intent parameters (e.g., `amount > 10000`). The first matching rule determines the policy decision. If no rule matches, the default decision is ALLOW.

### Example Rules

> **RULE-001:** Interns are denied all financial actions.
> Matches: `action=transfer_funds`, `role=intern`. Decision: DENY.

> **RULE-003:** Transfers over $10,000 require manager or admin approval.
> Matches: `action=transfer_funds`, `role=*`, condition: `amount > 10000`. Decision: REQUIRE_APPROVAL.

> **RULE-005:** Admins may perform any action.
> Matches: `action=*`, `role=admin`. Decision: ALLOW.

---

## Risk Engine

The risk engine (`runtime/policy/risk_engine.py`) computes a numeric risk score for each canonical intent. The score is a sum of four components, each derived from configurable rules loaded from `runtime/policy/risk_rules.json`.

### Risk Score Components

| Component | Source | Description |
|-----------|--------|-------------|
| **Base risk** | Action type | Each action type has a base risk value (e.g., `transfer_funds: 5`, `send_email: 2`) |
| **Role risk** | Requester's role | Each role has a risk modifier (e.g., `intern: 3`, `admin: 0`) |
| **Amount risk** | Financial parameters | Scaled by transaction amount when applicable |
| **Target risk** | System target | Risk modifier based on the target system or resource |

The total risk score is the sum of all applicable components.

### Risk Thresholds

The risk score is mapped to a risk level using configurable thresholds:

| Risk Level | Default Threshold | Meaning |
|------------|------------------|---------|
| **LOW** | Score 0–4 | Standard processing, no additional controls |
| **MEDIUM** | Score 5–7 | Enhanced logging, may trigger additional review |
| **HIGH** | Score 8+ | Escalation to human approval required |

When the risk level is HIGH and the policy decision is REQUIRE_APPROVAL, the request is escalated to the approval queue. The risk score and level are included in the approval request so the human approver has full context.

### Intent Requirements

The intent requirements matrix (`runtime/policy/intent_requirements.py`) defines which fields are mandatory for each action type. This ensures that the policy and risk engines always have the data they need to make informed decisions.

| Action Type | Required Fields |
|-------------|----------------|
| `transfer_funds` | `amount`, `recipient`, `currency` |
| `send_email` | `to`, `subject`, `body` |
| `delete_data` | `target`, `scope` |
| `create_event` | `title`, `start_time`, `attendees` |
| `http_request` | `url`, `method` |

---

## Policy Versioning

Policy rules are versioned through the policy manager (`runtime/governance/policy_manager.py`). The version registry is stored in `runtime/governance/policy_versions.json`, and each version's rules are preserved as a snapshot file (e.g., `policy_rules_v1_0.json`, `policy_rules_v1_1.json`).

### Version Lifecycle

Every policy change follows a governed workflow with five states:

| State | Description |
|-------|-------------|
| **PROPOSED** | A draft has been submitted with proposed rule changes |
| **APPROVED** | An admin has approved the draft for activation |
| **ACTIVATED** | The draft is now the live policy; prior version becomes INACTIVE |
| **INACTIVE** | A previously active version that has been superseded |
| **ROLLED_BACK** | A version that was active but has been rolled back to a prior version |

### Workflow

1. **Propose.** An admin submits a draft with new or modified rules. The draft is stored with status PROPOSED. The live policy is not affected.

2. **Approve.** A different admin reviews and approves the draft. Self-approval is prohibited. The draft status changes to APPROVED.

3. **Activate.** An admin activates the approved draft. The draft's rules are copied to `runtime/policy/policy_rules.json`, the version status changes to ACTIVATED, and the prior active version becomes INACTIVE. A governance change record, receipt, and ledger entry are created.

4. **Rollback.** If a problem is discovered, an admin can roll back to any previously active version. The rollback restores the prior version's rules to the live policy file, creates a new version entry with status ROLLED_BACK, and records the event in the governance ledger.

### Access Control

| Action | Required Role |
|--------|--------------|
| Propose a draft | Admin |
| Approve a draft | Admin (different from proposer) |
| Activate a version | Admin |
| Roll back a version | Admin |
| View policy versions | Manager, Admin |

---

## Risk Model Versioning

Risk model rules follow the same versioning workflow through the risk manager (`runtime/governance/risk_manager.py`). The version registry is stored in `runtime/governance/risk_versions.json`, and each version's rules are preserved as a snapshot file (e.g., `risk_rules_v1_0_0.json`).

The risk model versioning workflow is identical to policy versioning: propose, approve, activate, with optional rollback. All changes produce governance change records, receipts, and ledger entries.

### Risk Model Structure

A risk model version contains three sections:

**Base risk values** define the inherent risk of each action type:
```json
{
  "transfer_funds": 5,
  "send_email": 2,
  "delete_data": 6,
  "create_event": 1,
  "http_request": 3
}
```

**Role risk modifiers** define the additional risk based on the requester's role:
```json
{
  "intern": 3,
  "employee": 1,
  "auditor": 0,
  "manager": 0,
  "admin": 0
}
```

**Thresholds** define the boundaries between risk levels:
```json
{
  "low_max": 4,
  "medium_max": 7
}
```

---

## Safety Guarantees

The policy and risk versioning system enforces two critical safety properties:

**Drafts never affect live runtime.** A proposed or approved draft exists only in the governance directory. The live policy and risk files (`runtime/policy/policy_rules.json` and `runtime/policy/risk_rules.json`) are only modified during the activation step.

**Every change is auditable.** Every activation and rollback creates a governance change record in the change log, a cryptographic receipt, and a tamper-evident ledger entry. The full history of who proposed what, who approved it, and when it was activated is permanently recorded.

---

## References

| Specification | Location |
|--------------|----------|
| Policy Constraints | `spec/05_policy_constraints.md` |
| Risk Evaluation | `spec/04_risk_evaluation.md` |
| Policy Engine Implementation | `runtime/policy/policy_engine.py` |
| Risk Engine Implementation | `runtime/policy/risk_engine.py` |
| Policy Manager | `runtime/governance/policy_manager.py` |
| Risk Manager | `runtime/governance/risk_manager.py` |
| Active Policy Rules | `runtime/policy/policy_rules.json` |
| Active Risk Rules | `runtime/policy/risk_rules.json` |
