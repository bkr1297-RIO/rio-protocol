# RIO Protocol

**Category:** AI Control Plane and Audit Plane

RIO is a fail-closed execution governance system that requires authorization before execution and produces cryptographic receipts and tamper-evident audit logs for every action.

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
│   ├── threat_model.md                10 threats with mitigations
│   ├── verification_tests.md          12 verification test cases
│   ├── constraint_vs_policy.md        Policy vs. constraint distinction
│   └── role_model.md                  8 roles with separation rules
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
├── whitepaper/                        White paper (pending)
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

## Status

| Component | Count | Status |
|-----------|-------|--------|
| Protocol Specifications | 15 | Complete |
| JSON Schemas | 8 | Complete |
| End-to-End Examples | 5 | Complete |
| Architecture Diagrams | 5 | Complete |
| Threat Model | 10 threats | Complete |
| Verification Tests | 12 tests | Complete |
| System Manifest | 1 | Complete |
| Governed Action Pattern | 1 | Complete |
| Role Model | 8 roles | Complete |
| White Paper | — | Pending |

---

## License

See `LICENSE` for terms.
