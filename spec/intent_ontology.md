# RIO Protocol — Intent Ontology and Action Naming Convention

**Version:** 1.0.0
**Status:** Normative
**Protocol Reference:** 03 — Canonical Request Protocol

---

## 1. Overview

Every canonical request in the RIO Protocol includes an `action_type` field that identifies the operation being requested. A standardized naming convention for action types is essential for three reasons:

1. **Policy matching.** Policies reference action types to determine which rules apply. Without consistent naming, policies cannot reliably match requests.
2. **Risk evaluation.** The risk engine uses action type classes to select appropriate risk models and thresholds.
3. **Audit and reporting.** Auditors query the ledger by action type to analyze patterns, generate compliance reports, and detect anomalies.

This specification defines the canonical action naming format, the standard intent classes, and the rules for constructing valid action names within the RIO Protocol.

---

## 2. Naming Format

Action names MUST use the following hierarchical dot-notation format:

```
<class>.<verb>[.<object>][.<scope>]
```

| Segment | Required | Description | Example |
|---------|----------|-------------|---------|
| `class` | Yes | Top-level intent category from the standard class list | `transact` |
| `verb` | Yes | The specific operation being performed | `send` |
| `object` | No | The target resource type | `payment` |
| `scope` | No | Boundary qualifier (internal, external, cross-region) | `external` |

**Full example:** `transact.send.payment.external`

This name reads as: a financial transaction (`transact`) to send (`send`) a payment (`payment`) to an external party (`external`).

---

## 3. Standard Intent Classes

The RIO Protocol defines 10 standard intent classes. Implementations MUST support all 10 classes. Organizations MAY add custom classes following the extensibility rules in Section 7.

| Class | Description | Risk Baseline | Example Actions |
|-------|-------------|---------------|-----------------|
| `read` | Data retrieval and query operations | Low | `read.query.database`, `read.export.report` |
| `write` | Data creation, modification, or deletion | Medium | `write.update.record`, `write.delete.table` |
| `communicate` | Messaging, email, and notification operations | Medium | `communicate.send.email.external`, `communicate.post.message` |
| `execute` | Code execution, deployments, and system commands | High | `execute.deploy.service.production`, `execute.run.script` |
| `transact` | Financial operations including payments and transfers | High | `transact.send.payment.external`, `transact.refund.credit` |
| `control` | System configuration and access control changes | High | `control.modify.firewall`, `control.update.config` |
| `approve` | Authorization and decision-making operations | Medium | `approve.authorize.request`, `approve.sign.document` |
| `delegate` | Permission delegation and role assignment | High | `delegate.grant.access`, `delegate.assign.role` |
| `monitor` | Observability, alerting, and surveillance operations | Low | `monitor.create.alert`, `monitor.subscribe.event` |
| `learn` | Model updates, policy changes, and system learning | Critical | `learn.update.policy`, `learn.retrain.model` |

### 3.1 Risk Baseline

Each class carries a default risk baseline that the risk evaluation engine uses as a starting point. The actual risk score is computed from the full request context, but the class baseline establishes the floor.

- **Low:** Typically does not require authorization for standard operations.
- **Medium:** May require authorization depending on scope and parameters.
- **High:** Typically requires explicit human authorization.
- **Critical:** MUST always require human authorization. No exceptions.

---

## 4. Action Name Registry

The following table provides the standard action name registry. Implementations SHOULD use these names for common operations to ensure cross-system consistency.

| Action Name | Class | Verb | Object | Scope | Description |
|-------------|-------|------|--------|-------|-------------|
| `read.query.database` | read | query | database | — | Query a database table or view |
| `read.export.report` | read | export | report | — | Export a report to file |
| `read.fetch.document` | read | fetch | document | — | Retrieve a document from storage |
| `write.create.record` | write | create | record | — | Create a new data record |
| `write.update.record` | write | update | record | — | Modify an existing record |
| `write.delete.record` | write | delete | record | — | Delete a data record |
| `write.delete.table.production` | write | delete | table | production | Delete a production database table |
| `communicate.send.email.external` | communicate | send | email | external | Send email to external recipient |
| `communicate.send.email.internal` | communicate | send | email | internal | Send email to internal recipient |
| `communicate.post.message` | communicate | post | message | — | Post a message to a channel |
| `communicate.send.notification` | communicate | send | notification | — | Send a system notification |
| `execute.deploy.service.production` | execute | deploy | service | production | Deploy a service to production |
| `execute.deploy.service.staging` | execute | deploy | service | staging | Deploy a service to staging |
| `execute.run.script` | execute | run | script | — | Execute a script or command |
| `execute.run.migration` | execute | run | migration | — | Run a database migration |
| `transact.send.payment.external` | transact | send | payment | external | Send payment to external party |
| `transact.send.payment.internal` | transact | send | payment | internal | Internal fund transfer |
| `transact.refund.credit` | transact | refund | credit | — | Issue a refund or credit |
| `transact.approve.invoice` | transact | approve | invoice | — | Approve an invoice for payment |
| `control.modify.firewall` | control | modify | firewall | — | Change firewall rules |
| `control.update.config` | control | update | config | — | Update system configuration |
| `control.rotate.credentials` | control | rotate | credentials | — | Rotate API keys or passwords |
| `approve.authorize.request` | approve | authorize | request | — | Authorize a pending request |
| `delegate.grant.access` | delegate | grant | access | — | Grant access to a resource |
| `delegate.assign.role` | delegate | assign | role | — | Assign a role to a user |
| `delegate.revoke.access` | delegate | revoke | access | — | Revoke access from a user |
| `monitor.create.alert` | monitor | create | alert | — | Create a monitoring alert |
| `monitor.subscribe.event` | monitor | subscribe | event | — | Subscribe to system events |
| `learn.update.policy` | learn | update | policy | — | Update a governance policy |
| `learn.retrain.model` | learn | retrain | model | — | Retrain a risk or ML model |

---

## 5. Naming Rules

The following rules MUST be enforced when constructing or validating action names:

1. **Lowercase only.** All segments MUST be lowercase ASCII letters. No uppercase, no Unicode.
2. **Dot-separated.** Segments MUST be separated by a single period (`.`). No spaces, underscores, or hyphens within the action name.
3. **Minimum depth: 2.** Every action name MUST have at least a class and a verb: `<class>.<verb>`.
4. **Maximum depth: 4.** Action names MUST NOT exceed 4 segments: `<class>.<verb>.<object>.<scope>`.
5. **Standard class required.** The first segment MUST be one of the 10 standard classes or a registered custom class.
6. **No reserved words.** The following words MUST NOT be used as verbs or objects: `all`, `any`, `none`, `null`, `undefined`, `wildcard`.
7. **Immutable once recorded.** Once an action name appears in a ledger entry, its meaning MUST NOT be changed. New semantics require a new action name.

### 5.1 Validation Regex

```
^(read|write|communicate|execute|transact|control|approve|delegate|monitor|learn)\.[a-z]+(\.[a-z]+){0,2}$
```

Implementations with custom classes MUST extend this regex to include registered custom class names.

---

## 6. Policy Matching

Policies reference action types using exact matches or wildcard patterns. The RIO Protocol supports the following matching modes:

| Pattern | Matches | Example |
|---------|---------|---------|
| Exact | Only the specified action | `transact.send.payment.external` |
| Class wildcard | All actions in a class | `transact.*` |
| Verb wildcard | All actions with a specific class and verb | `transact.send.*` |
| Object wildcard | All scopes of a specific action | `transact.send.payment.*` |

### 6.1 Matching Rules

1. Wildcards MUST only appear as the last segment, represented by `*`.
2. A policy with pattern `transact.*` matches `transact.send`, `transact.send.payment`, and `transact.send.payment.external`.
3. More specific patterns take precedence over less specific patterns during policy evaluation.
4. If multiple policies match at the same specificity level, the priority order defined in the Policy Language Specification applies: DENY > ESCALATE > ALLOW_WITH_CONSTRAINTS > ALLOW.

### 6.2 Matching Algorithm

```
function matchesPolicy(actionName, policyPattern):
    if policyPattern does not contain '*':
        return actionName == policyPattern
    
    prefix = policyPattern.removeSuffix('.*')
    return actionName == prefix OR actionName.startsWith(prefix + '.')
```

---

## 7. Extensibility

Organizations MAY define custom intent classes to support domain-specific operations. Custom classes MUST follow these rules:

1. **Registration required.** Custom classes MUST be registered in the organization's RIO configuration before use.
2. **No collision.** Custom class names MUST NOT conflict with the 10 standard classes.
3. **Prefix recommended.** Organizations SHOULD prefix custom classes with an organization identifier to prevent cross-organization collisions (e.g., `acme_logistics.route.optimize`).
4. **Documentation required.** Each custom class MUST include a description, risk baseline, and at least one example action.
5. **Policy updates required.** Adding a custom class MUST be accompanied by at least one policy rule that governs actions in that class. Unmatched action types default to DENY under the fail-closed model.

### 7.1 Custom Class Registration

Custom classes are registered in the system manifest under `custom_intent_classes`:

```json
{
  "custom_intent_classes": [
    {
      "class": "logistics",
      "description": "Supply chain and logistics operations",
      "risk_baseline": "medium",
      "registered_by": "admin-001",
      "registered_at": "2026-03-01T00:00:00Z"
    }
  ]
}
```

---

## 8. Anti-Patterns

The following are common mistakes that implementations MUST avoid:

| Anti-Pattern | Problem | Correct Approach |
|-------------|---------|------------------|
| Using free-text action types | `"Send money to vendor"` cannot be matched by policies | Use `transact.send.payment.external` |
| Overloading a single action name | Using `execute.run` for both scripts and deployments | Use `execute.run.script` and `execute.deploy.service` |
| Mixing case | `Transact.Send.Payment` breaks validation | Use `transact.send.payment` |
| Exceeding depth | `transact.send.wire.payment.external.urgent` | Limit to 4 segments; use `parameters` for additional context |
| Using scope as risk indicator | `transact.send.payment.high_risk` | Scope describes boundary, not risk; use `risk_context` in the canonical request |
| Changing meaning of existing names | Redefining `write.delete.record` to mean "archive" | Create `write.archive.record` instead |
| Skipping class registration | Using unregistered custom classes | Register in manifest before use; unregistered classes are rejected |

---

## 9. Dependencies

| Dependency | Relationship |
|-----------|-------------|
| Canonical Request Protocol (03) | Action names populate the `action_type` field |
| Risk Evaluation Protocol (04) | Risk engine uses class baseline for initial scoring |
| Policy Constraints Protocol (05) | Policies match against action name patterns |
| Audit Ledger Protocol (09) | Ledger entries are queryable by action type |
| Learning Protocol (10) | Learning engine analyzes action type frequency and outcomes |
