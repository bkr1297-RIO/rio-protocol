# SBAM-Baseline Gate Interface
# Coordinated Human-Side Authorization and Machine-Side Runtime Governance

### Purpose

This document defines the interface and handoff between two distinct but paired governance layers:

- **Baseline Gate** — The human-side sovereignty checkpoint (Return-to-Baseline Protocol)
- **SBAM Runtime Harness** — The machine-side governance engine

The goal is to create a clean, enforceable boundary so that raw human signal does **not** become machine execution authority without passing through regulated human authorization first.

### Core Principle

**Capability does not create authority.**

**Authorization does not bypass runtime governance.**

Baseline Gate protects human sovereignty *before* authorization is granted.

SBAM protects system integrity *after* authorization is granted.

These are paired but non-substitutable functions.

### The Handoff Object: Human Baseline Authorization (HBA)

This is the formal bridge between the two layers.

Once a human completes Baseline Gate, the system produces a **Human Baseline Authorization** object. This is the *only* object that should enter the SBAM Runtime Harness from the human side.

**Human Baseline Authorization (v0.1.3)**

| Field | Description | Required |
|---|---|---|
| `authorization_id` | Unique identifier (e.g. `HBA-0001`) | Yes |
| `issued_by` | `human_operator` | Yes |
| `issued_at` | Timestamp when the authorization was created. | Yes |
| `status` | `granted` / `conditional` / `denied` / `revoked` | Yes |
| `authorization_type` | `single_action` / `session_limited` / `conditional_envelope` / `standing_rule_reference` | Yes |
| `scope` | action_type, permitted_operations, prohibited_operations | Yes |
| `register_separation` | private_meaning, personal_protocol, public_proof, runtime_evidence | Yes |
| `declared_human_state` | baseline_check, charge_level, urgency_level, reversibility, state_basis | Optional |
| `authority_statement` | Human-authored declaration of what is being authorized | Yes |
| `validity` | expires_at, renewal_required, revocation_path, reentry_required_on_expiry | Yes |
| `sbam_requirements` | triadic_closure_required, phase_state_evaluation_required | Yes |
| `machine_permissions` | Granular permissions for machine actions | Yes |
| `receipt_required` | Must be true | Yes |

**Key Rule:**

SBAM must never receive raw human signal or intent. It only receives a bounded `Human Baseline Authorization` object.

### SBAM's Role After Receiving HBA

Once SBAM receives a valid HBA, it performs the following in strict order:

1. **Triadic Closure Check** (Authority x Clarity x Containment)
2. **Phase-State Selection** via the SBAM Phase-State Controller
3. **Routing Decision** based on HBA scope + current system state

#### Recommended Phase States (in context of Baseline Gate)

| SBAM Phase | Trigger Condition | Allowed Behavior | Human Re-entry |
|---|---|---|---|
| **Open / Fluid** | Low charge, narrow scope, high reversibility | Proceed within HBA permissions | No |
| **Bounded** | Moderate charge or broader scope | Operate strictly inside HBA scope | Optional |
| **Reflective** | High symbolic/personal charge | Mirror + simulate only. No final output | Required |
| **Closed / Hold** | Scope violation or failed closure | Halt. Generate review packet | Required |
| **Escalated** | High consequence or ambiguous authority | Generate review packet only | Required |

### Critical Boundaries

| Question | Answered By | Notes |
|---|---|---|
| What does this signal mean to the human? | Baseline Gate | Human meaning stays human |
| Has the human authorized action from a regulated state? | Baseline Gate | Produces HBA |
| Does this action have standing? | Triadic Closure | Inside SBAM |
| What machine posture is permitted? | SBAM Phase-State | Based on current stress + HBA scope |
| What actually happened? | MUS Receipt | Proof layer |
| What pattern is emerging? | MANTIS | Advisory only |

**Core Boundary Rule:**

Baseline Gate regulates **authorization**.

SBAM regulates **execution**.

Neither may substitute for the other.

### Failure Modes at the Seam

| Failure Mode | Description | Required Response |
|---|---|---|
| **Baseline Bypass** | Signal moves directly to machine execution | Force Baseline Gate before any SBAM evaluation |
| **Authorization Inflation** | Human authorized "draft" but machine attempts to publish/execute | SBAM detects scope violation -> Close or narrow phase |
| **Category Collapse** | Private meaning treated as public proof | Hold. Force register separation |
| **Runtime Override** | Clean HBA treated as sufficient to bypass closure | Triadic Closure remains mandatory |
| **Infinite Reflection** | Baseline Gate becomes paralysis | Define low-risk thresholds for bounded progression |

### Keeper Principles

- **Return before release.**
  The human must return to baseline before granting authorization.

- **Close before execution.**
  Triadic Closure (Authority x Clarity x Containment) must be satisfied before any action proceeds.

- **Receipt after motion.**
  Every authorized action must produce a receipt.

- **Human authority is not transferable.**
  Even with a valid HBA, the human remains the root source of authority and consequence.

- **Telemetry may constrict the membrane. It may not create permission.**

### Recommended Next Artifacts

Once this interface is stable, the logical sequence is:

1. `baseline_gate_protocol.md` — Full human-side protocol spec (future)
2. Formal schemas for HBA, AAP, and Baseline Receipt (delivered in v0.1.3)

**Core Keeper:**

Baseline Gate returns the human before machine consequence. HBA carries bounded authority. AAP carries the request. SBAM routes crossing behavior. RIO decides admissibility. Sentinel enforces. MUS receipts. MUSS preserves sovereignty. The system records authority; it does not become authority.
