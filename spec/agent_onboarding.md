# RIO Protocol: Agent Onboarding Specification

**Version:** 1.0.0
**Status:** Specification
**Category:** Operational Infrastructure

---

## 1. Purpose

This specification defines how new agents (LLM sessions, AI services, or automated systems) are onboarded into a RIO governed workflow. Onboarding ensures that every agent begins with the correct role assignment, understands the system constraints, and is registered in the principal registry before performing any work.

This specification bridges two layers:
- **Prompt layer:** The bootstrap prompt pack (`prompts/bootstrap-v1.md`) sets the agent's behavioral expectations.
- **Enforcement layer:** The principal registry (`gateway/security/principals.mjs`) and policy engine (`gateway/governance/policy-engine.mjs`) enforce the constraints structurally.

The prompt layer is necessary but not sufficient. An agent may drift from its prompt. The enforcement layer catches drift and fails closed.

---

## 2. Onboarding Flow

### 2.1 Manual Onboarding (Current — Phase 0)

The human authority (I-1) onboards agents manually:

1. **Register principal.** Add the agent to the principal registry with a `principal_id`, `actor_type`, `primary_role`, and `secondary_roles`. This is done via the `principals.mjs` seed list or the `/principals` API endpoint.

2. **Deliver bootstrap prompt.** Paste the Master Prompt from `prompts/bootstrap-v1.md` to the agent. Then paste the appropriate Role Prompt based on the agent's `primary_role`.

3. **Confirm comprehension.** The agent must acknowledge the constraint before receiving any task. If the agent does not acknowledge, do not assign work.

4. **Assign work.** Deliver the task, spec, or directive. The agent operates within its lane.

### 2.2 Automated Onboarding (Future — Phase 2+)

When the Notion Decision Log and inter-agent communication are operational:

1. **Register principal.** Same as manual, but triggered by a governed action (intent → approval → execution → receipt).

2. **Serve bootstrap prompt.** The system generates the Master Prompt + Role Prompt from the prompt pack, parameterized by the agent's registered role. The prompt is delivered as the first message in the agent's context.

3. **Bind to Notion.** The agent's first Decision Log row is created automatically, showing its registration, role assignment, and the prompt version it received.

4. **Drift detection.** The learning loop compares the agent's outputs against the expectations set by its Role Prompt. Deviations are logged as governance events.

---

## 3. Principal Registry Binding

When a new agent is onboarded, the following fields MUST be set in the principal registry:

| Field | Required | Description |
|-------|----------|-------------|
| `principal_id` | YES | Unique identifier (e.g., `bondi`, `manny`, `observer`) |
| `actor_type` | YES | One of: `human`, `ai_agent`, `service`, `executor`, `auditor`, `meta_governor` |
| `display_name` | YES | Human-readable name and role description |
| `primary_role` | YES | One of: `proposer`, `approver`, `executor`, `auditor`, `meta_governor`, `root_authority` |
| `secondary_roles` | YES | Array of additional roles (subject to `PROHIBITED_ROLE_COMBINATIONS`) |
| `registered_by` | YES | The principal who authorized the registration (must be `root_authority` or `meta_governor`) |
| `prompt_version` | RECOMMENDED | The version of the bootstrap prompt pack delivered to the agent |

### 3.1 Prompt Version Tracking

The `metadata` JSONB field on the principal record SHOULD include:

```json
{
  "bootstrap_prompt_version": "1.0.0",
  "bootstrap_prompt_hash": "<sha256 of prompts/bootstrap-v1.md>",
  "onboarded_at": "2026-04-14T00:00:00.000Z",
  "onboarded_by": "I-1"
}
```

This creates a verifiable link between the agent's identity and the expectations that were set for it.

---

## 4. Role-to-Prompt Mapping

The system MUST serve the correct Role Prompt based on the agent's `primary_role`:

| Primary Role | Role Prompt | Handoff Signal |
|-------------|-------------|----------------|
| `proposer` (architect) | Section 2: Architect | `Ready for Builder handoff.` |
| `proposer` (builder) | Section 3: Builder | `Ready for Auditor review.` |
| `auditor` | Section 4: Auditor | `Ready for Human Approval.` |
| `proposer` (operator) | Section 5: Operator | `Ready for Human Decision.` |

Note: The `proposer` role has sub-types (architect, builder, operator) that are distinguished by the agent's `display_name` or `metadata.sub_role` field, not by the `primary_role` enum. This is because all three sub-types share the same enforcement constraint: they can propose but not execute.

---

## 5. Drift Detection Baseline

The bootstrap prompt pack serves as the drift detection baseline. The learning loop (when implemented) SHOULD:

1. **Record the prompt version** delivered to each agent at onboarding time.
2. **Compare agent outputs** against the expectations defined in the Role Prompt:
   - Does the agent stay within its declared lane?
   - Does the agent produce the correct handoff signal?
   - Does the agent attempt actions outside its role?
3. **Log deviations** as governance events with the following schema:

```json
{
  "event_type": "AGENT_DRIFT",
  "principal_id": "<agent_id>",
  "expected_role": "<role from prompt>",
  "observed_behavior": "<description of deviation>",
  "prompt_version": "1.0.0",
  "severity": "LOW | MEDIUM | HIGH",
  "timestamp": "<ISO8601>"
}
```

4. **Surface deviations** in the Notion Decision Log for human review.
5. **Never auto-correct.** Drift detection observes and reports. The human authority decides the response.

---

## 6. Invariants

1. No agent may be onboarded without a principal registry entry.
2. No agent may receive work before acknowledging the Master Prompt.
3. The bootstrap prompt version MUST be recorded on the principal record.
4. Drift detection MUST NOT auto-correct agent behavior.
5. Changes to the prompt pack are governed actions requiring `root_authority` approval.
