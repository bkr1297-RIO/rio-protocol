# RIO Protocol

**Runtime Governance and Execution Control Plane for AI Systems**

RIO is a governed execution system that sits between AI, humans, and real-world actions. It translates goals into structured intent, evaluates risk and policy, requires approval when necessary, controls execution, verifies outcomes, and generates cryptographically signed receipts recorded in a tamper-evident ledger. **The system enforces the rules, not the AI.**

> **This repository is the canonical protocol specification.** It contains everything an external team needs to implement a RIO-compliant gateway: specifications, JSON schemas, conformance test vectors, governance documents, and reference artifacts. It contains no executable implementation code.

**Version:** v1.0.0

---

## What RIO Guarantees

These are not features. They are properties enforced by the protocol's cryptographic and architectural mechanisms. Each is independently testable.

| Guarantee | Mechanism | How to Verify |
|-----------|-----------|---------------|
| **No action executes without authorization** | Fail-closed execution gate; no valid token = no execution | Submit any request without a token → gate rejects |
| **Past records cannot be altered without detection** | Hash-chained ledger: `Hn = SHA256(En.data + H(n-1))` | Recompute chain hashes; any mismatch = tampering |
| **Approvals cannot be forged** | Ed25519/ECDSA signatures on receipts and tokens | Verify signature against public key; forgery fails |
| **Tokens cannot be replayed** | Single-use nonce registry | Submit a used nonce → system rejects |
| **Stale authorizations expire** | TTL-bound tokens (default 300s) | Submit expired token → gate rejects |
| **Denied actions are auditable** | Denial receipts recorded in ledger | Query ledger for `decision=denied` entries |
| **Intent is bound to outcome** | Three-hash binding: `intent_hash`, `action_hash`, `verification_hash` | Compare hashes; mismatch = drift or tampering |

---

## How to Verify (No Access to RIO Required)

An independent party can audit the system using only the public key and the ledger:

1. **Recompute the hash chain:** `Hn = SHA256(En.data + H(n-1))` for every entry. Any mismatch proves tampering.
2. **Verify receipt signatures:** Check Ed25519/ECDSA signatures against the public key. Invalid signature = forgery.
3. **Check the three-hash binding:** Compare `intent_hash` (what was authorized), `action_hash` (what was executed), `verification_hash` (what was observed). Mismatch = drift.
4. **Test replay protection:** Submit a used nonce. The system must reject it.
5. **Test TTL enforcement:** Submit an expired token. The gate must reject it.
6. **Test fail-closed behavior:** Attempt execution without a token. The gate must remain locked.

Test vectors for all six checks are in [`tests/vectors/`](tests/vectors/).

---

## Three-Loop Architecture

![Three-Loop Architecture](docs/three_loop_architecture.png)

1. **Intake Loop** — Goal → Intent → Canonical Request
2. **Governance Loop** — Risk → Policy → Approval → Execution → Receipt → Ledger → Verification
3. **Learning Loop** — Corpus → Replay → Simulation → Policy Improvement

The Learning Loop analyzes the audit trail and proposes policy updates. It cannot bypass governance or execute actions directly.

---

## The 8-Stage Governed Execution Pipeline

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

1. [Architecture](docs/Architecture.md) — Pipeline, receipts, ledger, verification, threat model, trust model
2. [Threat Model](docs/Threat_Model.md) — 10 threat categories and mitigations
3. [Trust Model](docs/Trust_Model.md) — What you must trust and what you do not
4. [EGI Technical Assessment](docs/EGI_Technical_Assessment.pdf) — Regulatory alignment analysis (EU AI Act, NIST AI RMF, ISO 42001)
5. [Enterprise Use Cases](docs/ENTERPRISE_USE_CASES.md) — Real-world governance scenarios

### For Contributors

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines and [docs/GOVERNANCE.md](docs/GOVERNANCE.md) for the protocol change process.

---

## Regulatory Alignment

RIO provides infrastructure for a specific, demonstrable regulatory requirement: a verifiable, cryptographic record that a specific action was authorized by a specific human, executed under a specific policy, verified against its stated intent, and recorded in a tamper-evident ledger that any independent party can audit.

| Regulation | Requirement | RIO Mechanism |
|------------|-------------|---------------|
| **EU AI Act, Art. 12** | Automatic logging of high-risk AI system events | Signed receipts + hash-chained ledger |
| **EU AI Act, Art. 14** | Human oversight with ability to intervene | Fail-closed gate + human approval for high-risk |
| **EU AI Act, Art. 9** | Risk management system | 4-component risk scoring + policy engine |
| **NIST AI RMF** | Govern / Map / Measure / Manage | Policy engine / Intake loop / Risk scoring / Approval gate |
| **ISO 42001, A.6.2.8** | Event logging for AI management | Automatic signed receipts per action |

For the full analysis, see [docs/EGI_Technical_Assessment.pdf](docs/EGI_Technical_Assessment.pdf).

---

## Repository Structure

```
spec/                                  Canonical protocol specifications
├── RIO_Protocol_Specification_v1.0.md   Master specification
├── RIO_Protocol_Specification_v1.0.json Structured JSON specification
├── rio_gateway_protocol_v1.0.json       Gateway protocol specification
├── Independent_Verifier_Spec.json       Verifier requirements
├── 01–15_*.md                           Stage specifications
└── *.md / *.json                        Design documents and schema defs

schemas/                               JSON Schema 2020-12 definitions
├── canonical_intent.json                Canonical request structure
├── receipt.json                         Cryptographic receipt
├── ledger_entry.json                    Ledger entry
├── authorization_record.json            Authorization record
├── execution_record.json                Execution record
├── risk_evaluation.json                 Risk evaluation record
├── execution_token.json                 Execution token
├── nonce_registry.json                  Nonce registry
└── attestation_record.json              Attestation record

examples/                              Reference artifacts and use cases
├── full_cycle/                          Complete end-to-end reference (live capture)
├── gateway/                             Gateway example artifacts
├── quickstart/                          Quickstart example artifacts
├── *.md                                 Use case narratives (5 scenarios)
├── *_example.json                       Schema example instances
└── engine_manifest.json                 Live engine manifest

tests/                                 Conformance test materials
├── vectors/                             Deterministic test vectors
├── conformance/                         Conformance suite (57 tests)
└── TC-RIO-*.md                          Protocol test case definitions

docs/                                  Protocol documentation
├── Architecture.md                      Pipeline, receipts, ledger, verification
├── Threat_Model.md                      10 threat categories and mitigations
├── Trust_Model.md                       Trust assumptions and boundaries
├── EGI_Technical_Assessment.pdf         Regulatory alignment analysis
├── SYSTEM_OVERVIEW.md                   What RIO is and why it exists
├── EXECUTION_FLOW.md                    Pipeline walkthrough
├── LEDGER_AND_RECEIPTS.md               Cryptographic audit system
├── POLICY_AND_RISK.md                   Policy/risk specification
├── IDENTITY_AND_APPROVALS.md            Identity specification
├── SIMULATION_AND_LEARNING.md           Learning specification
├── THREAT_MODEL_SUMMARY.md              Threat model summary
├── ENTERPRISE_USE_CASES.md              Enterprise use cases
├── GLOSSARY.md                          Key terms and definitions
├── GOVERNANCE.md                        Protocol governance structure
├── CERTIFICATION.md                     Certification levels and process
├── CONFORMANCE.md                       Conformance level definitions
├── VERSIONING.md                        Protocol versioning policy
└── adoption/                            Regulatory and adoption docs

reference-architecture/                Architecture diagrams (Mermaid + PNG)
whitepaper/                            Protocol white paper (v1 + v2)
architecture/15_layer_model.md         15-layer architecture model
diagrams/                              Diagram source files
manifest/rio_system_manifest.json      System manifest
safety/EKS-0_kill_switch.md            Kill switch specification
security/README.md                     Security documentation
ledger/README.md                       Ledger protocol documentation

RIO_Core_Runtime_Behavior.md           Implementation-independent behavior reference
VERSION                                Protocol version (v1.0.0)
README.md                              This file
LICENSE                                All Rights Reserved (Apache 2.0 pending)
CONTRIBUTING.md                        Contribution guidelines
CHANGELOG.md                           Release history
NOTICE                                 Attribution notice
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

All Rights Reserved (Apache 2.0 license pending) — see [LICENSE](LICENSE).
