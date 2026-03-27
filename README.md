# RIO Protocol

**Runtime Governance and Execution Control Plane for AI Systems**

RIO is a governed execution system that sits between AI, humans, and real-world actions. It translates goals into structured intent, evaluates risk and policy, requires approval when necessary, controls execution, verifies outcomes, and generates cryptographically signed receipts recorded in a tamper-evident ledger. **The system enforces the rules, not the AI.** Built on a three-loop architecture — Intake (goal → intent), Governance (policy → approval → execution → verification), and Learning (ledger → policy improvement) — RIO creates a closed-loop system where every action is authorized, executed, verified, recorded, and used to improve future decisions.

> **This repository is the canonical protocol specification.** It contains everything an external team needs to implement a RIO-compliant gateway: specifications, JSON schemas, conformance test vectors, governance documents, and reference artifacts. It contains no executable implementation code.

---

## Related Repositories

| Repository | Purpose |
|------------|---------|
| [rio-reference-impl](https://github.com/bkr1297-RIO/rio-reference-impl) | Working reference implementation — runtime engine, audit dashboard, policy engine, Docker deployment |
| [rio-tools](https://github.com/bkr1297-RIO/rio-tools) | Developer tools — SDKs (Python + JavaScript), protocol simulator, independent verifier CLI, compliance checker |

---

## Getting Started

### For Implementers

Read the protocol specification and implement against the schemas:

1. Start with [RIO_Core_Runtime_Behavior.md](RIO_Core_Runtime_Behavior.md) for the implementation-independent behavior reference
2. Read the [canonical specification](spec/RIO_Protocol_Specification_v1.0.md) for the complete 8-stage pipeline
3. Validate your implementation against the [JSON schemas](schemas/) and [conformance test vectors](tests/vectors/)
4. Check your conformance level using the [conformance definitions](docs/CONFORMANCE.md)

### For Evaluators

Review the protocol design and governance:

1. [System Overview](docs/SYSTEM_OVERVIEW.md) — What RIO is and why it exists
2. [Architecture](docs/ARCHITECTURE.md) — Component architecture
3. [Enterprise Use Cases](docs/ENTERPRISE_USE_CASES.md) — Real-world governance scenarios
4. [Regulatory Mapping](docs/adoption/REGULATORY_MAPPING.md) — EU AI Act, NIST AI RMF, SOC 2 alignment

### For Contributors

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [docs/GOVERNANCE.md](docs/GOVERNANCE.md) for the protocol change process.

---

## Protocol Overview

### The 8-Stage Governed Execution Pipeline

| Stage | Name | Description |
|-------|------|-------------|
| 1 | Intake | Goal reception and origin verification |
| 2 | Canonical Intent | Structured intent construction with identity binding |
| 3 | Risk Evaluation | Multi-dimensional risk scoring |
| 4 | Policy Constraints | Policy rule evaluation and constraint enforcement |
| 5 | Authorization | Human approval for high-risk actions, automatic approval for low-risk |
| 6 | Execution | Controlled execution with kill switch capability |
| 7 | Attestation | Cryptographic receipt generation with hash-chain ledger recording |
| 8 | Verification | Post-execution verification and learning loop feedback |

### Three-Loop Architecture

![Three-Loop Architecture](docs/three_loop_architecture.png)

1. **Intake Loop** — Goal → Intent → Canonical Request
2. **Governance Loop** — Risk → Policy → Approval → Execution → Receipt → Ledger → Verification
3. **Learning Loop** — Corpus → Replay → Simulation → Policy Improvement

### Cryptographic Guarantees

The protocol provides tamper-evident execution records through:

- **v2 Receipts** — Ed25519/ECDSA signed receipts with `intent_hash`, `action_hash`, `verification_hash`, `verification_status`, ISO 8601 timestamps, and identity fields
- **Hash-Chain Ledger** — Each entry contains `previous_ledger_hash` for chain integrity, independently verifiable
- **Denial Receipts** — Blocked actions generate full receipts with `decision=denied` and `execution_status=BLOCKED`
- **Post-Execution Verification** — Stage 6b verification produces `verification_status` embedded in receipts

---

## Repository Structure

```
spec/                                  Canonical protocol specifications
├── RIO_Protocol_Specification_v1.0.md   Master specification (101K characters)
├── RIO_Protocol_Specification_v1.0.json Structured JSON specification
├── rio_gateway_protocol_v1.0.json       Gateway protocol specification
├── Independent_Verifier_Spec.json       Verifier requirements
├── 01_intake_protocol.md                Stage 1: Intake
├── 02_origin_verification.md            Stage 2: Origin verification
├── 03_canonical_request.md              Stage 3: Canonical request
├── 04_risk_evaluation.md                Stage 4: Risk evaluation
├── 05_policy_constraints.md             Stage 5: Policy constraints
├── 06_authorization.md                  Stage 6: Authorization
├── 07_execution.md                      Stage 7: Execution
├── 08_attestation.md                    Stage 8: Attestation
├── 09_audit_ledger.md                   Stage 9: Audit ledger
├── 10_learning.md                       Stage 10: Learning
├── 11_independence.md                   Independence specification
├── 12_role_separation.md                Role separation
├── 13_meta_governance.md                Meta governance
├── 14_orchestration.md                  Orchestration
├── 15_time_bound_authorization.md       Time-bound authorization
├── *.md                                 Design documents and architecture specs
└── *.json                               Schema definitions (in-spec)

schemas/                               JSON Schema 2020-12 definitions
├── canonical_intent.json                Canonical request structure
├── receipt.json                         Cryptographic receipt
├── ledger_entry.json                    Ledger entry
├── auth_token.json                      Authorization token
├── risk_evaluation.json                 Risk evaluation record
├── authorization_record.json            Authorization record
├── execution_record.json                Execution record
└── attestation_record.json              Attestation record

examples/                              Reference artifacts and use cases
├── full_cycle/                          Complete end-to-end reference (live capture)
│   ├── README.md                        Full cycle walkthrough
│   ├── example_intent_signed.json       Signed intent (ECDSA secp256k1)
│   ├── example_execution_result.json    4-step execution trace
│   ├── example_receipt_v2.json          Cryptographic receipt (v2)
│   ├── example_ledger_entry.json        Single ledger entry
│   ├── example_ledger_chain.json        Complete hash-chain ledger
│   ├── example_verification_result.json Independent verification (PASS)
│   ├── example_audit_log.json           Governance enforcement evidence
│   ├── example_debug_test_flow.json     5-test diagnostic pipeline
│   └── example_nonce_stats.json         Replay protection statistics
├── gateway/                             Gateway example artifacts
├── quickstart/                          Quickstart example artifacts
├── *.md                                 Use case narratives (5 scenarios)
├── *_example.json                       Schema example instances
└── engine_manifest.json                 Live engine manifest

tests/                                 Conformance test materials
├── vectors/                             Deterministic test vectors
│   ├── public_key.pem                   Ed25519 test public key
│   ├── receipt_valid_approved.json      Valid approved receipt
│   ├── receipt_valid_denied.json        Valid denied receipt
│   ├── receipt_invalid_*.json           Invalid receipt variants
│   ├── hash_computation_examples.json   7 worked hash examples
│   ├── signing_payload_examples.json    3 signing/verification examples
│   ├── ledger_chain_valid.json          Valid hash chain
│   ├── ledger_chain_tampered.json       Tampered hash chain
│   └── README.md                        Vector index and constants
├── conformance/                         Conformance suite
│   ├── rio_conformance_suite_v1.json    Master suite (57 tests)
│   ├── TEST_MATRIX.md                   Test case matrix
│   ├── README.md                        Conformance documentation
│   └── *.json                           Conformance test vectors
└── TC-RIO-*.md                          Protocol test case definitions

docs/                                  Protocol documentation
├── SYSTEM_OVERVIEW.md                   What RIO is and why it exists
├── ARCHITECTURE.md                      Component architecture
├── EXECUTION_FLOW.md                    Pipeline walkthrough
├── LEDGER_AND_RECEIPTS.md               Cryptographic audit system
├── POLICY_AND_RISK.md                   Policy/risk specification
├── IDENTITY_AND_APPROVALS.md            Identity specification
├── SIMULATION_AND_LEARNING.md           Learning specification
├── THREAT_MODEL_SUMMARY.md              Threat model
├── ENTERPRISE_USE_CASES.md              Enterprise use cases
├── GLOSSARY.md                          Key terms and definitions
├── GOVERNANCE.md                        Protocol governance structure
├── CERTIFICATION.md                     Certification levels and process
├── CERTIFICATION_CHECKLIST.md           Certification submission checklist
├── RELEASE_CHECKLIST.md                 Pre-publish release checklist
├── RELEASE_PROCESS.md                   Version numbering and release workflow
├── CONFORMANCE.md                       Conformance level definitions
├── COMPLIANCE_BADGES.md                 Badge definitions and usage
├── VERSIONING.md                        Protocol versioning policy (SemVer 2.0.0)
├── PROTOCOL_CHANGE_TEMPLATE.md          Protocol Change Proposal template
├── VERIFICATION_OUTPUT_EXAMPLE.md       Verification output examples
├── QUICKSTART.md                        Protocol quickstart guide
├── three_loop_architecture.png          Architecture diagram
└── adoption/                            Regulatory and adoption docs
    ├── REGULATORY_MAPPING.md            EU AI Act, NIST AI RMF, SOC 2
    ├── CERTIFICATION_CRITERIA.md        Conformance certification criteria
    ├── IMPLEMENTATION_GUIDE.md          Step-by-step adoption guide
    └── QUICKSTART.md                    Minimal viable deployment

reference-architecture/                Architecture diagrams
├── 01_system_overview.mmd + .png
├── 02_decision_traceability_chain.mmd + .png
├── 03_governed_execution_loop.mmd + .png
├── 04_protocol_stack.mmd + .png
├── 05_trust_boundaries.mmd + .png
└── governed_action_pattern.md

whitepaper/                            Protocol white paper
├── rio_protocol_whitepaper.md + .pdf
└── rio_protocol_whitepaper_v2.md + .pdf

architecture/15_layer_model.md         15-layer architecture model
diagrams/                              Diagram source files
manifest/rio_system_manifest.json      System manifest
safety/EKS-0_kill_switch.md            Kill switch specification
security/README.md                     Security documentation
ledger/README.md                       Ledger protocol documentation

RIO_Core_Runtime_Behavior.md           Implementation-independent behavior reference
README.md                              This file
LICENSE                                Apache License 2.0
CONTRIBUTING.md                        Contribution guidelines
CHANGELOG.md                           Release history
```

---

## Conformance Levels

Implementations are assessed at three conformance levels:

| Level | Name | Requirements |
|-------|------|-------------|
| L1 | Structural | Correct receipt and ledger entry structure, all required fields present |
| L2 | Cryptographic | L1 + valid signatures, correct hash computation, chain integrity |
| L3 | Full Protocol | L2 + complete 8-stage pipeline, denial receipts, post-execution verification, learning loop |

See [docs/CONFORMANCE.md](docs/CONFORMANCE.md) for complete definitions and [tests/conformance/](tests/conformance/) for the test suite.

---

## Example Use Cases

The `examples/` directory contains five end-to-end flows. Each shows all seven records in the decision traceability chain with cross-referenced IDs.

| Example | Scenario | Risk Level |
|---------|----------|------------|
| Financial Transaction | AI procurement agent requests wire transfer requiring human approval | High |
| Email Send | AI customer success agent sends executive apology email to client | High |
| Data Deletion | AI compliance agent processes GDPR right-to-erasure request | Critical |
| Code Deploy | AI DevOps agent deploys emergency security patch to production | High |
| Access Grant | AI IT ops agent grants temporary elevated database access | Critical |

---

## Certification

Organizations can certify their RIO implementations at three levels: Structural, Cryptographic, and Full Protocol. See [docs/CERTIFICATION.md](docs/CERTIFICATION.md) for the process and [docs/CERTIFICATION_CHECKLIST.md](docs/CERTIFICATION_CHECKLIST.md) for the submission checklist.

---

## Protocol Governance

Changes to the protocol follow the Protocol Change Proposal (PCP) process defined in [docs/GOVERNANCE.md](docs/GOVERNANCE.md). The versioning policy follows SemVer 2.0.0 as defined in [docs/VERSIONING.md](docs/VERSIONING.md).

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).
