# Architecture

**RIO — System Architecture**

---

## Overview

The RIO system is organized into seven layers, each with a distinct responsibility. The layers communicate through well-defined interfaces, and no layer may bypass another. The architecture enforces a strict separation between specification, runtime enforcement, execution, audit, and learning.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DASHBOARD LAYER                             │
│   Audit Dashboard  ·  Policy Admin UI  ·  Risk Model Admin UI      │
├─────────────────────────────────────────────────────────────────────┤
│                           API LAYER                                 │
│   Governance API  ·  Approval API  ·  Simulation API  ·  FastAPI   │
├─────────────────────────────────────────────────────────────────────┤
│                        RUNTIME LAYER                                │
│   Pipeline  ·  Policy Engine  ·  Risk Engine  ·  Authorization      │
│   Execution Gate  ·  Kill Switch  ·  Invariant Checks               │
├─────────────────────────────────────────────────────────────────────┤
│                        ADAPTER LAYER                                │
│   Email Adapter  ·  File Adapter  ·  HTTP Adapter  ·  Calendar      │
│   Connector Registry  ·  Adapter Registry                           │
├─────────────────────────────────────────────────────────────────────┤
│                        AUDIT LAYER                                  │
│   Receipt Generator  ·  Ledger (hash chain)  ·  Verification        │
│   Governance Ledger  ·  Nonce Registry                              │
├─────────────────────────────────────────────────────────────────────┤
│                       IDENTITY LAYER                                │
│   Users  ·  Roles  ·  Permissions  ·  Sessions  ·  Approval Queue   │
├─────────────────────────────────────────────────────────────────────┤
│                       LEARNING LAYER                                │
│   Governed Corpus  ·  Replay Engine  ·  Simulation API              │
├─────────────────────────────────────────────────────────────────────┤
│                     SPECIFICATION LAYER                             │
│   15 Protocol Specs  ·  8 Invariants  ·  JSON Schemas  ·  Threat    │
│   Model  ·  Verification Tests  ·  Role Model  ·  System Manifest   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Specification Layer

The specification layer defines what the system must do without prescribing how. It contains 15 protocol specifications (intake through time-bound authorization), 8 protocol invariants, 21 system invariants, JSON schemas for all data structures, a threat model with 10 identified threats, 12 verification tests, and a system manifest.

The specification layer is implementation-independent. Any language or platform can implement RIO by satisfying the specifications and passing the verification tests.

| Component | Count | Location |
|-----------|-------|----------|
| Protocol specifications | 15 | `spec/01_intake_protocol.md` through `spec/15_time_bound_authorization.md` |
| Protocol invariants | 8 | `spec/protocol_invariants.md` |
| System invariants | 21 | `spec/system_invariants.md` |
| JSON schemas | 8 | `schemas/` |
| Core protocol schemas | 4 | `spec/*.json` |
| Threat model | 10 threats | `spec/threat_model.md` |
| Verification tests | 12 | `spec/verification_tests.md` |
| System manifest | 1 | `manifest/rio_system_manifest.json` |

---

## Runtime Layer

The runtime layer is the Python reference implementation of the specification. It implements the eight-stage Governed Execution Pipeline as a strict, sequential chain of function calls. The pipeline is defined in `runtime/pipeline.py` and orchestrates the following modules:

**Intake** (`runtime/intake.py`) receives raw action requests, validates required fields, and registers the request with a unique ID and timestamp.

**Classification** (`runtime/classification.py`) determines the action type and assigns an initial risk category based on the action and the requester's role.

**Intent Validation and Structured Intent** (`runtime/intent_validation.py`, `runtime/structured_intent.py`) validate that the request contains all fields required by the intent requirements matrix, then form a canonical intent object with a deterministic hash.

**Policy and Risk** (`runtime/policy_risk.py`) delegates to the policy engine and risk engine. The policy engine evaluates rules from `runtime/policy/policy_rules.json`. The risk engine computes a numeric score from `runtime/policy/risk_rules.json`. Together they produce a policy decision: ALLOW, DENY, or ESCALATE (require human approval).

**Authorization** (`runtime/authorization.py`) issues a time-bound, single-use authorization token when the policy decision is ALLOW. When the decision is ESCALATE, the request enters the approval queue. When the decision is DENY, a denial receipt is generated immediately.

**Execution Gate** (`runtime/execution_gate.py`) is the final checkpoint. It verifies the authorization token signature, checks the kill switch, consumes the nonce (preventing replay), and dispatches the action to the appropriate adapter.

**Kill Switch** (`runtime/kill_switch.py`) is a global halt mechanism. When engaged, no new executions proceed regardless of authorization status. Kill switch events are themselves recorded in the ledger.

**Invariant Checks** (`runtime/invariants.py`) verify protocol invariants INV-01 through INV-08 at the end of every pipeline run, ensuring completeness, receipt integrity, ledger integrity, and hash chain consistency.

---

## Adapter Layer

The adapter layer translates authorized intents into real-world actions. Each adapter implements a common interface defined in `runtime/adapters/base_adapter.py` and is registered in the adapter registry.

| Adapter | Action Types | Description |
|---------|-------------|-------------|
| Email Adapter | `send_email` | Sends email via configured transport (simulated in local mode) |
| File Adapter | `write_file`, `read_file`, `delete_data` | File system operations within a sandboxed directory |
| HTTP Adapter | `http_request` | Outbound HTTP calls to whitelisted domains |
| Calendar Adapter | `create_event` | Calendar event creation |

The adapter layer also includes a **connector** sub-layer (`runtime/connectors/`) that provides lower-level transport abstractions. Adapters use connectors for actual I/O, while adding authorization verification and context handling.

The adapter registry (`runtime/adapters/adapter_registry.py`) loads configuration from `runtime/adapters/config.json`, which defines the execution mode (simulated or live), allowed action types, and domain whitelists.

---

## Audit Layer

The audit layer produces and stores the cryptographic proof of every decision.

**Receipt Generator** (`runtime/receipt.py`) creates a signed receipt for every pipeline outcome. Each receipt contains the intent hash, decision hash, execution hash, a timestamp, and an ECDSA-secp256k1 signature using the system's RSA-2048 private key. Receipts are the atomic unit of proof in the system.

**Ledger** (`runtime/ledger.py`) maintains an append-only, hash-linked chain of entries. Each entry contains a reference to its receipt, a content hash, and the hash of the previous entry. The ledger is stored in `runtime/data/ledger.jsonl`.

**Governance Ledger** (`runtime/governance/governance_ledger.py`) extends the audit layer to cover policy and risk model changes. Every governance action — policy activation, rollback, risk model update — produces its own receipt and ledger entry with event type `GOVERNANCE_CHANGE`.

**Verification** (`runtime/verification.py`, `runtime/verify_ledger.py`) provides tools to verify individual receipts, validate the full ledger hash chain, and detect tampering.

**Nonce Registry** (managed by `runtime/state.py`) tracks consumed authorization nonces to prevent replay attacks. Each nonce can be used exactly once.

---

## Identity Layer

The identity layer manages users, roles, permissions, and the human approval workflow.

**Users** (`runtime/iam/users.py`) are stored in `runtime/data/users.json`. Each user has a unique ID, name, email, role, and active status.

**Roles** (`runtime/iam/roles.py`) define a five-level hierarchy: intern (level 1), employee (level 2), auditor (level 2), manager (level 3), and admin (level 4). Role definitions are stored in `runtime/data/roles.json`.

**Permissions** (`runtime/iam/permissions.py`) map roles to allowed actions, approval authority, ledger visibility, and approval limits. The permissions matrix is stored in `runtime/data/permissions.json`.

**Approval Workflow** (`runtime/approvals/`) handles the ESCALATE path. When policy requires human approval, the request enters the approval queue. A manager or admin can approve or deny the request. Approval generates an authorization token and resumes the pipeline. Denial generates a denial receipt. Self-approval is prohibited.

---

## Learning Layer

The learning layer provides the data and tools for governance improvement without ever modifying live policy directly.

**Governed Corpus** (`runtime/corpus/corpus_store.py`) records a structured decision-history entry for every completed pipeline run. Each corpus record contains the full context: request, intent, policy decision, risk score, authorization outcome, execution result, receipt reference, and ledger reference.

**Replay Engine** (`runtime/corpus/replay_engine.py`) re-evaluates past corpus records through current or alternate policy and risk settings without executing real actions. It answers questions like "What would happen if we changed the risk threshold?" or "How many past requests would be blocked under the proposed policy?"

**Simulation API** (`runtime/corpus/simulation_api.py`) exposes replay functionality through the dashboard, allowing administrators to test policy changes before activating them.

---

## Dashboard Layer

The dashboard layer provides the human interface to the system.

**Audit Dashboard** (`dashboard/app.py`) displays the ledger, receipts, request history, approval queue, system state, and kill switch controls. It is built with FastAPI and Jinja2 templates.

**Policy Admin UI** (`dashboard/admin/policies.py`) provides pages for viewing, drafting, approving, activating, and rolling back policy versions.

**Risk Model Admin UI** (`dashboard/admin/risk_models.py`) provides the same lifecycle management for risk model versions.

**API Layer** The dashboard application also serves the Governance API (`runtime/governance/governance_api.py`), Approval API (`runtime/approvals/approval_api.py`), and Simulation API (`runtime/corpus/simulation_api.py`) as FastAPI sub-applications.

---

## API Layer

All programmatic access to RIO is through REST endpoints served by the FastAPI application:

| Endpoint Group | Base Path | Purpose |
|---------------|-----------|---------|
| Governance API | `/api/governance/` | Policy and risk model management |
| Approval API | `/api/approvals/` | Approval queue operations |
| Simulation API | `/api/simulation/` | Replay and what-if analysis |
| Dashboard | `/` | HTML dashboard and admin UI |
| OpenAPI Docs | `/docs` | Auto-generated API documentation |

---

## Data Flow

The following diagram shows the flow of data through the system for a single request:

```
  AI Agent / User
        │
        ▼
  ┌─────────────┐
  │   Intake     │──── Request registered, ID assigned
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │ Classify     │──── Action type + initial risk category
  └──────┬──────┘
         ▼
  ┌─────────────┐
  │ Intent       │──── Canonical intent object + hash
  └──────┬──────┘
         ▼
  ┌─────────────┐     ┌──────────────┐
  │ Policy/Risk  │────▶│ Policy Rules │
  └──────┬──────┘     │ Risk Rules   │
         │            └──────────────┘
         ▼
    ┌────┴────┐
    │ Decision │
    └────┬────┘
         │
    ┌────┼────────────────┐
    ▼    ▼                ▼
  ALLOW  ESCALATE       DENY
    │    │                │
    │    ▼                │
    │  ┌──────────┐       │
    │  │ Approval │       │
    │  │ Queue    │       │
    │  └────┬─────┘       │
    │       ▼             │
    │  Human Approver     │
    │    │      │         │
    │  Approve  Deny──────┤
    │    │                │
    ▼    ▼                ▼
  ┌─────────────┐   ┌──────────┐
  │ Exec Gate   │   │ Denial   │
  │ (nonce,     │   │ Receipt  │
  │  kill sw,   │   └────┬─────┘
  │  signature) │        │
  └──────┬──────┘        │
         ▼               │
  ┌─────────────┐        │
  │ Adapter      │        │
  │ (execute)    │        │
  └──────┬──────┘        │
         ▼               ▼
  ┌─────────────┐   ┌──────────┐
  │ Receipt      │   │ Receipt  │
  │ (signed)     │   │ (signed) │
  └──────┬──────┘   └────┬─────┘
         ▼               ▼
  ┌─────────────────────────────┐
  │         Ledger              │
  │   (hash-linked chain)       │
  └──────────────┬──────────────┘
                 ▼
  ┌─────────────────────────────┐
  │      Governed Corpus        │
  │   (decision history)        │
  └─────────────────────────────┘
```

---

## File Organization

```
rio-protocol/
├── spec/                  Specification layer (15 protocols, schemas, threat model)
├── schemas/               JSON Schema definitions
├── architecture/          Architecture models (15-layer)
├── runtime/               Runtime layer (Python reference implementation)
│   ├── pipeline.py        Governed Execution Pipeline orchestrator
│   ├── policy/            Policy engine + risk engine + rules
│   ├── governance/        Policy/risk versioning + governance ledger
│   ├── adapters/          Execution adapters (email, file, HTTP, calendar)
│   ├── connectors/        Transport-level connectors
│   ├── approvals/         Approval queue and manager
│   ├── iam/               Identity, roles, permissions, sessions
│   ├── corpus/            Governed corpus + replay engine + simulation
│   ├── keys/              RSA-2048 key pair
│   └── data/              Runtime data files
├── dashboard/             Dashboard + Admin UI (FastAPI + Jinja2)
├── scripts/               Setup and run scripts
├── docker/                Docker configuration
├── examples/              End-to-end example flows
├── manifest/              System manifest
├── tests/                 Protocol test cases
├── safety/                Kill switch specification
├── whitepaper/            White paper
└── docs/                  This documentation
```
