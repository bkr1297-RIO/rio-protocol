# RIO Protocol

**Category:** AI Control Plane and Audit Plane

RIO is a fail-closed execution governance system that requires authorization before execution and produces cryptographic receipts and tamper-evident audit logs for every action.

---

## Quick Start

```bash
git clone https://github.com/bkr1297-RIO/rio-protocol.git
cd rio-protocol
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_rio.py
python scripts/create_admin_user.py
python scripts/run_all.py
```

The dashboard opens at `http://localhost:8050`. API documentation is at `http://localhost:8050/docs`.

---

## Installation

### Prerequisites

- Python 3.10 or later
- pip (included with Python)
- Git

### Option A: Local Installation

```bash
# Clone the repository
git clone https://github.com/bkr1297-RIO/rio-protocol.git
cd rio-protocol

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize the system (creates directories, keys, seed data)
python scripts/init_rio.py

# Create the first admin user
python scripts/create_admin_user.py

# Start the server
python scripts/run_all.py
```

### Option B: Docker

```bash
git clone https://github.com/bkr1297-RIO/rio-protocol.git
cd rio-protocol
cp .env.example .env            # edit .env as needed
docker compose -f docker/docker-compose.yml up --build
```

This starts two services:

| Service | Port | Description |
|---------|------|-------------|
| `rio-dashboard` | 8050 | Dashboard + API + Admin UI |
| `rio-api` | 8000 | API-only instance |

### Option C: Makefile

```bash
make install    # Install dependencies
make init       # Initialize the system
make admin      # Create admin user
make run        # Start the server
make test       # Run 47 tests
```

---

## Configuration

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|----------|---------|-------------|
| `RIO_ENV` | `local` | Environment name |
| `RIO_DATA_DIR` | `runtime/data` | Data file directory |
| `RIO_KEYS_DIR` | `runtime/keys` | Cryptographic key directory |
| `RIO_MODE` | `simulated` | Execution mode (`simulated` or `live`) |
| `ADMIN_EMAIL` | `admin@rio.local` | Bootstrap admin email |
| `ADMIN_PASSWORD` | `change_me` | Bootstrap admin password |
| `RIO_DASHBOARD_HOST` | `0.0.0.0` | Server bind address |
| `RIO_DASHBOARD_PORT` | `8050` | Server bind port |
| `RIO_LOG_LEVEL` | `INFO` | Log verbosity |

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/init_rio.py` | Initialize directories, keys, policy files, risk files, users, roles | `python scripts/init_rio.py` |
| `scripts/create_admin_user.py` | Create or update the admin user with hashed password | `python scripts/create_admin_user.py` |
| `scripts/run_all.py` | Start the dashboard and API server | `python scripts/run_all.py` |

All scripts support `--help` for additional options.

---

## Running Tests

The test harness includes 47 test cases covering the full protocol stack:

```bash
python -m runtime.test_harness
```

| Test Suite | Count | Coverage |
|------------|-------|----------|
| TC-RIO (core protocol) | 3 | Stages 1–8, kill switch |
| TC-EXTRA (invariants) | 4 | Self-auth, replay, validation, hash chain |
| TC-POLICY / TC-RISK | 2 | Policy deny, risk scoring |
| TC-INTENT | 1 | Intent requirements matrix |
| TC-CONN (connectors) | 5 | Email, file, HTTP, kill switch |
| TC-APPR (approvals) | 4 | Queue, approve, deny, role check |
| TC-GOV (governance) | 5 | Version, activate, rollback, ledger, auth |
| TC-ADPT (adapters) | 5 | Email, calendar, file sandbox, HTTP, kill switch |
| TC-LEDG (ledger integrity) | 4 | Valid, tamper entry, delete, tamper receipt |
| TC-IAM (identity) | 5 | Role hierarchy, limits, self-approval, expiry |
| TC-CORP (corpus) | 4 | Record, replay, stricter role, same settings |
| TC-ADMIN (admin UI) | 5 | Risk draft, auth block, activate, rollback, ledger |

---

## The Problem

AI agents and automated systems can propose and execute consequential actions — payments, data deletions, code deployments, access grants — at machine speed. Without a governance layer between intent and execution, there is no mechanism to enforce authorization, verify compliance, or produce an audit trail. The result is uncontrolled execution with no accountability.

Existing approaches either block AI from acting (removing the value of automation) or allow AI to act without oversight (creating unacceptable risk). Neither is sufficient for regulated industries or high-stakes operations.

---

## The Solution

RIO interposes a control plane between any requester (AI agent, automated system, or human-initiated workflow) and any execution target (payment network, email system, database, deployment pipeline). Every action request passes through a deterministic pipeline:

1. The request is received, verified, normalized, and hashed.
2. Risk is evaluated and policies are checked.
3. A human or delegated authority makes an authorization decision.
4. The execution gate validates the authorization before releasing the action.
5. The system produces cryptographic attestation, a receipt, and a tamper-evident ledger entry.

No action executes without valid authorization. If any step fails, the system denies execution. This is the fail-closed guarantee.

---

## System Overview

```
External Requesters → RIO Control Plane → Execution Gate → Execution Systems
                                                    ↓
                                          Audit & Attestation → Ledger
```

The system overview diagram (`reference-architecture/01_system_overview.png`) shows the four zones: External Requesters, RIO Control Plane, Execution Systems, and Audit & Attestation.

---

## Decision Traceability Chain

Every action that passes through RIO produces a chain of seven cryptographically linked records:

```
canonical_request → risk_evaluation → authorization_record → execution_record → attestation_record → receipt → ledger_entry
```

| Record | Purpose | Schema |
|--------|---------|--------|
| Canonical Request | Normalized, hashed action request | `schemas/canonical_request.json` |
| Risk Evaluation | Risk score, factors, and recommendation | `schemas/risk_evaluation.json` |
| Authorization Record | Human or delegated authority decision | `schemas/authorization_record.json` |
| Execution Record | What was actually performed | `schemas/execution_record.json` |
| Attestation Record | Cryptographic proof of the full chain | `schemas/attestation_record.json` |
| Receipt | Human-readable audit summary | `schemas/receipt.json` |
| Ledger Entry | Tamper-evident hash chain record | Defined in Spec 09 |

Each record is canonically hashed (SHA-256), cryptographically signed (ECDSA-secp256k1), and immutably linked to prior records by ID and hash reference. An auditor can verify the entire chain by recomputing hashes and validating signatures.

---

## Governed Execution Loop

The protocol implements a continuous governance loop:

```
Observe → Verify → Evaluate → Authorize → Execute → Record → Attest → Ledger → Learn → Repeat
```

The Learning stage feeds outcomes back into risk evaluation, allowing the system to improve its risk models over time without weakening governance controls. The loop diagram is available at `reference-architecture/03_governed_execution_loop.png`.

---

## The 15 Protocol Stack

The RIO Protocol consists of 15 specifications organized into five categories.

### Sequential Pipeline (Specs 01–09)

| Spec | Protocol | Purpose |
|------|----------|---------|
| 01 | Intake Protocol | Receive and validate raw action requests |
| 02 | Origin Verification Protocol | Authenticate requester identity and signature |
| 03 | Canonical Request Protocol | Normalize, hash, and create canonical form |
| 04 | Risk Evaluation Protocol | Score risk and identify risk factors |
| 05 | Policy Constraints Protocol | Evaluate organizational policies and rules |
| 06 | Authorization Protocol | Obtain human or delegated authority decision |
| 07 | Execution Protocol | Validate authorization and perform action |
| 08 | Attestation Protocol | Produce cryptographic proof of chain |
| 09 | Audit Ledger Protocol | Append tamper-evident record to hash chain |

### Feedback (Spec 10)

| Spec | Protocol | Purpose |
|------|----------|---------|
| 10 | Learning Protocol | Update risk models from outcomes |

### Structural / Cross-Cutting (Specs 11–13)

| Spec | Protocol | Purpose |
|------|----------|---------|
| 11 | Independence Protocol | Control plane isolation from agents |
| 12 | Role Separation Protocol | No self-authorization, duty separation |
| 13 | Meta-Governance Protocol | Govern changes to governance itself |

### Control Flow (Spec 14)

| Spec | Protocol | Purpose |
|------|----------|---------|
| 14 | Orchestration Protocol | Coordinate protocol execution order |

### Specialized Sub-Protocol (Spec 15)

| Spec | Protocol | Purpose |
|------|----------|---------|
| 15 | Time-Bound Authorization Protocol | Enforce expiration on all authorizations |

All specifications are in `spec/` and follow a standardized structure: Protocol Name, Purpose, Scope, Inputs, Outputs, Required Fields, Processing Steps, Decision Logic, Failure Conditions, Security Considerations, Audit Requirements, Dependencies, and Example Flow.

---

## Repository Structure

```
rio-protocol/
├── spec/                              Protocol specifications
│   ├── 01_intake_protocol.md
│   ├── 02_origin_verification.md
│   ├── 03_canonical_request.md
│   ├── 04_risk_evaluation.md
│   ├── 05_policy_constraints.md
│   ├── 06_authorization.md
│   ├── 07_execution.md
│   ├── 08_attestation.md
│   ├── 09_audit_ledger.md
│   ├── 10_learning.md
│   ├── 11_independence.md
│   ├── 12_role_separation.md
│   ├── 13_meta_governance.md
│   ├── 14_orchestration.md
│   ├── 15_time_bound_authorization.md
│   ├── governed_execution_protocol.md 8-stage runtime protocol + learning loop
│   ├── runtime_flow.md               8-step runtime flow with diagram
│   ├── protocol_invariants.md         8 protocol invariants (INV-01 through INV-08)
│   ├── system_invariants.md          21 system invariants across 6 categories
│   ├── governed_corpus.md             Decision-history layer specification
│   ├── 8_step_to_15_protocol_mapping.md  Maps 8-step flow to 15 control protocols
│   ├── system_architecture.md         4-layer system architecture
│   ├── protocol_test_matrix.md        Test-to-invariant mapping
│   ├── threat_model.md                10 threats with mitigations
│   ├── verification_tests.md          12 verification test cases
│   ├── constraint_vs_policy.md        Policy vs. constraint distinction
│   ├── role_model.md                  8 roles with separation rules
│   ├── intent_ontology.md             Standard action naming convention
│   ├── policy_language.md             Policy rule structure and priority
│   ├── receipt_spec.md                Canonical receipt fields and verification
│   ├── ledger_interoperability.md     Hash chain verification and anchoring
│   ├── governance_learning.md         Learning inputs and policy update workflow
│   ├── protocol_flow.md              Full protocol flow reference (11 steps)
│   ├── protocol_state_machine.md     Formal state transitions and terminal states
│   ├── execution_envelope.md         Bounded execution model with kill switch
│   ├── api_endpoints.md              REST API surface definition
│   ├── identity_and_credentials.md   DID, Verifiable Credentials, trust registry
│   ├── oracle_attestation.md         External signed attestations for risk/policy
│   ├── cross_domain_verification.md  Cross-system receipt and ledger verification
│   ├── content_addressing_and_lineage.md  Content hashing and provenance chains
│   ├── canonical_intent_schema.json   Core schema: canonical intent (Stage 3)
│   ├── authorization_token_schema.json Core schema: authorization token (Stage 5)
│   ├── receipt_schema.json            Core schema: receipt (Stage 7)
│   ├── ledger_entry_schema.json       Core schema: ledger entry (Stage 8)
│   ├── protocol_blueprint_template.md Standard template for all protocol stages
│   ├── reference_architecture.md      Reference architecture: components, boundaries, flow
│   ├── canonical_intent_schema.md     Canonical intent format (human-readable spec)
│   ├── receipt_protocol.md            Receipt structure, hash chain, verification
│   ├── audit_ledger_protocol.md       Append-only ledger model and audit procedures
│   ├── verification_model.md          Verification model for protocol and ledger integrity
│   ├── governance_learning_protocol.md Governance learning protocol specification
│   ├── two_loop_architecture.md       Two-loop architecture (execution + learning)
│   ├── intent_translation_layer.md    Intent translation layer (universal grammar)
│   └── master_protocol_index.md       Master index linking all specifications
│
├── architecture/                      System architecture models
│   └── 15_layer_model.md             15-layer system architecture
│
├── runtime/                           Reference runtime (Python)
│   ├── __init__.py                    Package init with execution flow docs
│   ├── models.py                      Data structures: Request, Intent, Authorization, Receipt, LedgerEntry
│   ├── invariants.py                  Protocol invariant checks (INV-01 through INV-08)
│   ├── state.py                       System state: kill switch, token registry, ledger head
│   ├── kill_switch.py                 EKS-0 kill switch engage/disengage/check
│   ├── intake.py                      Stage 1: Register and authenticate requests
│   ├── classification.py              Stage 2: Classify action type and risk
│   ├── intent_validation.py           Stage 3a: Validate required fields and schema
│   ├── structured_intent.py           Stage 3b: Form canonical intent object
│   ├── policy_risk.py                 Stage 4: Policy evaluation and risk scoring
│   ├── authorization.py               Stage 5: Authorization decisions and token issuance
│   ├── execution_gate.py              Stage 6: Final gate checks before execution
│   ├── receipt.py                     Stage 7: Receipt generation, hashing, signing
│   ├── ledger.py                      Stage 8: Append-only ledger with hash chain
│   ├── verification.py                Verification of receipts, ledger, and invariants
│   ├── governance_learning.py         Stage 9: Asynchronous learning recommendations
│   ├── test_harness.py                47-test harness (run with python -m runtime.test_harness)
│   ├── policy/                        Policy and risk engines + rules
│   ├── governance/                    Versioned policy/risk management + change logs
│   ├── approvals/                     Approval queue and manager
│   ├── connectors/                    Email, file, HTTP connectors
│   ├── adapters/                      Execution adapters
│   ├── iam/                           Identity, roles, permissions, sessions
│   ├── corpus/                        Governed corpus and replay engine
│   ├── keys/                          RSA-2048 key pair (generated by init)
│   └── data/                          Runtime data files (ledger, receipts, users)
│
├── schemas/                           JSON Schema 2020-12 definitions
│   ├── canonical_request.json
│   ├── risk_evaluation.json
│   ├── authorization_record.json
│   ├── execution_record.json
│   ├── attestation_record.json
│   ├── receipt.json
│   ├── execution_token.json
│   └── nonce_registry.json
│
├── examples/                          End-to-end example flows
│   ├── financial_transaction.md       Wire transfer requiring approval
│   ├── email_send.md                  External client email
│   ├── data_deletion.md              Production data deletion (GDPR)
│   ├── code_deploy.md                Production code deployment
│   ├── access_grant.md               System access grant
│   ├── canonical_request_example.json
│   ├── risk_evaluation_example.json
│   ├── authorization_record_example.json
│   ├── execution_record_example.json
│   ├── attestation_record_example.json
│   └── receipt_example.json
│
├── reference-architecture/            Architecture diagrams and patterns
│   ├── 01_system_overview.png
│   ├── 02_decision_traceability_chain.png
│   ├── 03_governed_execution_loop.png
│   ├── 04_protocol_stack.png
│   ├── 05_trust_boundaries.png
│   ├── *.mmd                         Mermaid source files (editable)
│   └── governed_action_pattern.md     Cross-industry pattern analysis
│
├── manifest/                          System configuration
│   └── rio_system_manifest.json       Protocol stack, crypto, governance
│
├── tests/                             Protocol test cases
│   ├── TC-RIO-001.md                  Allowed execution with receipt and ledger
│   ├── TC-RIO-002.md                  Denied execution due to policy
│   └── TC-RIO-003.md                  Kill switch blocks execution
│
├── safety/                            Safety mechanisms
│   └── EKS-0_kill_switch.md           Global execution kill switch specification
│
├── dashboard/                         Audit dashboard (FastAPI + Jinja2)
│   ├── app.py                         Main dashboard application
│   ├── admin/                         Policy & Risk Admin UI
│   │   ├── policies.py                Policy admin routes
│   │   ├── risk_models.py             Risk model admin routes
│   │   └── templates/                 Admin HTML templates
│   ├── templates/                     Dashboard HTML templates
│   └── static/                        CSS and static assets
│
├── scripts/                           Setup and run scripts
│   ├── init_rio.py                    System initialization
│   ├── create_admin_user.py           Admin user creation
│   └── run_all.py                     Server startup
│
├── docker/                            Docker configuration
│   ├── Dockerfile                     Container image definition
│   └── docker-compose.yml             Multi-service orchestration
│
├── diagrams/                          Diagram source files (reserved)
├── whitepaper/                        White paper (Markdown + PDF)
│
├── requirements.txt                   Python dependencies
├── setup.py                           Package installation script
├── pyproject.toml                     Modern Python packaging metadata
├── Makefile                           Common development targets
├── .env.example                       Environment variable template
├── .dockerignore                      Docker build exclusions
├── README.md
└── LICENSE
```

---

## Example Use Cases

The `examples/` directory contains five end-to-end flows. Each shows all seven records in the decision traceability chain with cross-referenced IDs and an explanation of what happened and why.

| Example | Scenario | Risk Level |
|---------|----------|------------|
| Financial Transaction | AI procurement agent requests wire transfer requiring human approval | High |
| Email Send | AI customer success agent sends executive apology email to client | High |
| Data Deletion | AI compliance agent processes GDPR right-to-erasure request | Critical |
| Code Deploy | AI DevOps agent deploys emergency security patch to production | High |
| Access Grant | AI IT ops agent grants temporary elevated database access | Critical |

---

## Security Model (Fail-Closed)

Every component in the RIO Protocol defaults to denying action execution when it cannot positively verify a required condition. There is no fail-open mode.

| Condition | System Response |
|-----------|----------------|
| Origin signature invalid | Request rejected |
| Risk score cannot be computed | Request held |
| Authorization signature invalid | Execution blocked |
| Nonce already consumed | Execution blocked |
| Authorization expired | Execution blocked |
| Attestation verification fails | Attestation not issued |
| Ledger append fails | Pipeline halted |

---

## Threat Model

The threat model (`spec/threat_model.md`) defines 10 threats with severity ratings, attack vectors, mitigations, and residual risks:

| ID | Threat | Severity |
|----|--------|----------|
| T-01 | Replay Attack | Critical |
| T-02 | Forged Signature | Critical |
| T-03 | Tampered Payload | Critical |
| T-04 | Expired Authorization Reuse | High |
| T-05 | Direct Execution Bypass | Critical |
| T-06 | Ledger Tampering | High |
| T-07 | Unauthorized Policy Change | High |
| T-08 | Role Collusion | High |
| T-09 | Execution Outside Authorization Scope | Critical |
| T-10 | Time Skew Attack | High |

The document also includes a consolidated mitigations table, 8 foundational assumptions, and 3 security boundary definitions with cross-boundary isolation rules.

---

## Verification Tests

The verification test suite (`spec/verification_tests.md`) defines 12 test cases that validate the security properties of any RIO implementation:

| ID | Test | Priority |
|----|------|----------|
| VT-01 | Unsigned request blocked | Critical |
| VT-02 | Tampered payload rejected | Critical |
| VT-03 | Replay attack blocked | Critical |
| VT-04 | Expired timestamp rejected | Critical |
| VT-05 | Approved request executes | Critical |
| VT-06 | Denied request blocked | Critical |
| VT-07 | Ledger hash chain integrity verified | High |
| VT-08 | Receipt signature valid | High |
| VT-09 | Forged signature rejected | Critical |
| VT-10 | Direct execution blocked without approval | Critical |
| VT-11 | Execution outside approved scope blocked | Critical |
| VT-12 | Expired authorization cannot execute | Critical |

An implementation must pass all Critical-priority tests to be considered minimally compliant.

---

## Reference Architecture

| Diagram | Description |
|---------|-------------|
| `01_system_overview.png` | High-level system overview with four zones |
| `02_decision_traceability_chain.png` | Seven-record chain with ID references |
| `03_governed_execution_loop.png` | Nine-stage governance loop with deny paths |
| `04_protocol_stack.png` | All 15 protocols organized by category |
| `05_trust_boundaries.png` | Three trust boundaries with enforcement points |
| `governed_action_pattern.md` | Cross-industry analysis of the governed action pattern across 9 industries |

All diagrams include editable Mermaid source files (`.mmd`).

---

## Cryptography

| Parameter | Value |
|-----------|-------|
| Signature Algorithm | ECDSA |
| Curve | secp256k1 |
| Hash Algorithm | SHA-256 |
| Canonicalization | Minified sorted JSON |
| Fail-Closed Default | Enabled |
| Time Skew Allowance | 300 seconds |

---

## System Architecture (15 Layers)

The RIO system is organized into 15 architectural layers that describe where each function lives. This model defines system structure, not runtime order. The 15 layers are: Intake, Interpretation, Planning, Tools, Memory, Risk, Policy, Authority, Gate, Execution, Verification, Receipt, Ledger, Audit, and Learning.

See [`architecture/15_layer_model.md`](architecture/15_layer_model.md) for the full layer definitions.

---

## Runtime Protocol (8 Steps)

The Governed Execution Protocol defines the mandatory runtime path for every request: Intake, Classification, Structured Intent, Policy & Risk Check, Authorization, Execution Gate, Receipt/Attestation, and Audit Ledger. Governance Learning operates asynchronously as a ninth step and does not bypass runtime controls.

See [`spec/runtime_flow.md`](spec/runtime_flow.md) for the runtime flow diagram and [`spec/governed_execution_protocol.md`](spec/governed_execution_protocol.md) for the full stage definitions.

---

## Protocol Invariants

Eight protocol invariants (INV-01 through INV-08) define safety and correctness properties that must never be violated by any implementation. These cover completeness (every action traverses all stages), authorization safety (valid, time-bound, single-use tokens with distinct requester/authorizer), and fail-closed behavior (denials and kill switch events follow deterministic, auditable paths).

See [`spec/protocol_invariants.md`](spec/protocol_invariants.md) for the full invariant definitions and [`spec/system_invariants.md`](spec/system_invariants.md) for the 21 system-level invariants.

---

## Safety (Kill Switch)

The EKS-0 Kill Switch is a global execution halt mechanism that overrides normal authorization and execution behavior. When engaged, no new executions may proceed regardless of policy decisions. All kill switch events and blocked requests still generate receipts and ledger entries.

See [`safety/EKS-0_kill_switch.md`](safety/EKS-0_kill_switch.md) for the specification and [`tests/TC-RIO-003.md`](tests/TC-RIO-003.md) for the test case.

---

## Test Cases

Three protocol-level test cases validate the core runtime behavior:

| Test Case | Description | Protocol Steps Covered |
|-----------|-------------|------------------------|
| [TC-RIO-001](tests/TC-RIO-001.md) | Allowed execution with receipt and ledger | Stages 1–8 |
| [TC-RIO-002](tests/TC-RIO-002.md) | Denied execution due to policy | Stages 1–5, 7–8 |
| [TC-RIO-003](tests/TC-RIO-003.md) | Kill switch blocks execution | Stages 5–8 |

See [`spec/protocol_test_matrix.md`](spec/protocol_test_matrix.md) for the test-to-invariant mapping.

---

## Governed Corpus

The Governed Corpus is a structured decision-history layer that records intent, classification, policy decisions, authorization outcomes, execution results, receipts, ledger references, and eventual outcomes. It serves as the data source for Governance Learning (Step 9) and provides the foundation for audit, simulation, and risk modeling.

See [`spec/governed_corpus.md`](spec/governed_corpus.md) for the full specification.

---

## Intent Translation Layer

RIO is designed to sit under an Intent Translation Layer that maps canonical intents to specific external systems and APIs while preserving a common governed execution model. The Intent Translation Layer translates human/agent goals into structured intents, maps those intents to system-specific actions, and normalizes execution results for receipt generation.

See [`spec/intent_translation_layer.md`](spec/intent_translation_layer.md) for the full specification and [`spec/two_loop_architecture.md`](spec/two_loop_architecture.md) for the two-loop architecture that defines the relationship between the execution loop and the learning loop.

---

## Ledger & Receipts

Every protocol decision — whether approved, denied, or blocked — produces a cryptographic receipt (Stage 7) and an append-only ledger entry (Stage 8). Receipts contain intent hash, decision hash, execution hash, timestamp, and ECDSA-secp256k1 signature. Ledger entries are hash-linked to form a tamper-evident chain. There are no silent failures and no unrecorded decisions.

See [`spec/receipt_spec.md`](spec/receipt_spec.md) for receipt fields and verification, and [`spec/ledger_interoperability.md`](spec/ledger_interoperability.md) for hash chain verification and anchoring.

---

## Status

| Component | Count | Status |
|-----------|-------|--------|
| Core Protocol Definition | 1 | Complete |
| Protocol Specifications | 15 | Complete |
| JSON Schemas (original) | 8 | Complete |
| Core Protocol Schemas | 4 | Complete |
| Protocol Blueprint Template | 1 | Complete |
| End-to-End Examples | 5 | Complete |
| Architecture Diagrams | 5 | Complete |
| Threat Model | 10 threats + 7 control mappings | Complete |
| Reference Architecture | 1 | Complete |
| Canonical Intent Schema (doc) | 1 | Complete |
| Receipt Protocol | 1 | Complete |
| Audit Ledger Protocol | 1 | Complete |
| Verification Tests | 12 tests | Complete |
| System Manifest | 1 | Complete |
| Governed Action Pattern | 1 | Complete |
| Role Model | 8 roles | Complete |
| Protocol Standardization | 5 docs | Complete |
| Core Protocol Mechanics | 5 docs | Complete |
| Infrastructure Extensions | 4 docs | Complete |
| Protocol Invariants | 8 invariants | Complete |
| Protocol Test Cases | 3 tests | Complete |
| Safety Mechanisms | 1 (EKS-0) | Complete |
| Governed Corpus | 1 | Complete |
| System Architecture (4-layer) | 1 | Complete |
| 15-Layer Architecture | 1 | Complete |
| Runtime Flow | 1 | Complete |
| 8-Step to 15-Protocol Mapping | 1 | Complete |
| Verification Model | 1 | Complete |
| Governance Learning Protocol | 1 | Complete |
| Two-Loop Architecture | 1 | Complete |
| Intent Translation Layer | 1 | Complete |
| Master Protocol Index | 1 | Complete |
| Runtime Skeleton | 15 Python modules | Complete |
| White Paper | 1 | Complete |
| Audit Dashboard | 1 (FastAPI + Jinja2) | Complete |
| Policy Admin UI | 6 routes | Complete |
| Risk Model Admin UI | 6 routes | Complete |
| IAM System | 5 roles, 9 seed users | Complete |
| Approval Workflow | 4 API endpoints | Complete |
| Connector Framework | 3 connectors (email, file, HTTP) | Complete |
| Adapter Framework | 4 adapters | Complete |
| Governed Corpus + Replay | 2 modules | Complete |
| Test Harness | 47 tests (12 suites) | Complete |
| Packaging (pip, Docker, Make) | 3 methods | Complete |

---

## Authorship and Roles

| Role | Name |
|------|------|
| System Architecture and Protocol Design | Brian K. Rasmussen |
| Technical Implementation and Documentation | Manny |

**Repository:** RIO Protocol
**Project Type:** AI Control Plane and Audit Plane / Execution Governance Protocol

---

## License

See `LICENSE` for terms.
