# RIO Protocol

**The governed execution protocol for AI systems.**

RIO sits between AI systems and real-world actions. It makes sure AI cannot execute important actions without authorization, policy checks, verification, and proof.

> "RIO governs consequence. Receipts prove what happened."

---

## Governed Model Exchange

RIO Protocol sits in the emerging gap between model/tool context protocols and agent-to-agent coordination.

- **MCP** gives models tools.
- **A2A** lets agents communicate.
- **RIO** governs what an exchange may become under human or organizational authority.

RIO defines authority, permission, reliance, proof, receipts, and conformance boundaries for governed intelligence systems. It is complementary to MCP and A2A — not a replacement for either.

---

## Non-Collapse Conformance

This repository includes the Non-Collapse Conformance Bundle v0.1.3, a docs/tests-only synthetic baseline for testing whether governed intelligence systems preserve category boundaries.

It tests whether systems avoid collapsing:

- memory into consent
- access into authority
- confidence into truth
- learning into permission
- capability into action
- observation into judgment
- proof into meaning
- key possession into current conformance
- model agreement into proof
- helpfulness into permission

**Accepted proof posture:**

| Claim | Status |
|-------|--------|
| proof_status_label | negative_run_validated |
| runtime_status | not_enforced |
| live_conformance_status | not_claimed |
| receipt_verified | not_claimed |

This bundle does not claim live conformance, runtime enforcement, receipt verification, or production readiness.

---

## What RIO Is

RIO is a governed execution layer for AI systems. It sits between intelligent systems and real-world actions, ensuring that important actions cannot execute without authorization, policy checks, verification, and proof. Different repositories implement different parts of the system, including governance, receipts, observation, and interface layers.

**How it works:**

1. AI proposes an action.
2. The system evaluates risk and checks policy.
3. Humans approve when required.
4. RIO gates execution — nothing runs without authorization.
5. Receipts prove what happened.

---

## What This Repository Contains

This is the **canonical protocol specification** — the authoritative definition of what a RIO-compliant system must do. It contains specifications, JSON schemas, conformance test vectors, governance documents, and reference artifacts. Everything an external team needs to implement a RIO-compliant gateway is here.

Where any implementation conflicts with the protocol specification in this repository, the protocol specification governs.

**Version:** v1.0.0
**Error Vocabulary Version:** v1.0 (locked April 21, 2026, 01:00)

---

## How This Repo Fits Into the Larger System

| Repository | Role |
|------------|------|
| **[rio-protocol](https://github.com/bkr1297-RIO/rio-protocol)** (this repo) | Canonical protocol specification |
| [rio-receipt-protocol](https://github.com/bkr1297-RIO/rio-receipt-protocol) | Proof layer — local receipt engine |
| [rio-system](https://github.com/bkr1297-RIO/rio-system) | Observation and monitoring layer |
| [language-intake-mvp](https://github.com/bkr1297-RIO/language-intake-mvp) | Language governance — crossing detection |

---

## Verify Immediately

```bash
git clone https://github.com/bkr1297-RIO/rio-protocol.git
cd rio-protocol
pip install pynacl
```

Then follow the 5-step verification in [VERIFY_THIS_SYSTEM.md](VERIFY_THIS_SYSTEM.md). All test vectors, schemas, and verification instructions are in this repository. No external repos required.

---

## Standard and Verification

| Document | Location | Role |
|----------|----------|------|
| RIO Standard | [spec/RIO_STANDARD_v1.0.md](spec/RIO_STANDARD_v1.0.md) | Authoritative specification |
| Conformance Spec | [spec/RIO_CONFORMANCE_v2.3.0.md](spec/RIO_CONFORMANCE_v2.3.0.md) | How compliance is verified (7 levels) |
| Error Vocabulary | [spec/error_vocabulary.v1.json](spec/error_vocabulary.v1.json) | Canonical error codes (immutable) |
| Error Vocabulary Spec | [spec/error_vocabulary.md](spec/error_vocabulary.md) | Versioning and immutability rules |
| Verification Guide | [VERIFY_THIS_SYSTEM.md](VERIFY_THIS_SYSTEM.md) | Clone → run → break → verify in under 5 minutes |

`RIO_STANDARD_v1.0.md` is the authoritative specification. `RIO_CONFORMANCE_v2.3.0.md` defines how compliance is verified (7 conformance levels).

---

## Normative Boundary

This repository contains the protocol specification and reference verification implementation used to validate receipts and ledger integrity.

### Normative artifacts

The protocol contract is defined by:

1. `spec/receipt_schema.json`
2. `spec/receipt_protocol.md`
3. `spec/RIO_CONFORMANCE_v2.3.0.md`

These define protocol conformance.

### Reference implementation

Code in this repository is a reference implementation, not the protocol itself.

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

A RIO Receipt proves that a system produced a record and that it has not been altered. It does not independently prove that the action occurred in the external world.

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

## Conformance Levels

The authoritative conformance specification defines 7 levels in [spec/RIO_CONFORMANCE_v2.3.0.md](spec/RIO_CONFORMANCE_v2.3.0.md):

| Level | Name | Scope |
|-------|------|-------|
| 1 | Receipt Generation | All required fields present, correct types |
| 2 | Receipt + Verification | Level 1 + independently verifiable hashes |
| 3 | Receipt + Ledger | Level 2 + append-only hash-chained ledger |
| 4 | Receipt + Ledger + Verification | Level 3 + chain integrity independently verifiable |
| 5 | Full Proof Pipeline | Level 4 + 3-hash proof chain (result, previous_receipt, receipt) |
| 6 | Governed Receipts | Level 5 + 5-hash chain (adds request_hash, intent_hash) |
| 7 | Signed Receipts | Level 6 + Ed25519 signatures |

See [spec/RIO_CONFORMANCE_v2.3.0.md](spec/RIO_CONFORMANCE_v2.3.0.md) for complete definitions and [tests/conformance/](tests/conformance/) for the test suite.

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
├── canonical_request.json               Canonical request structure
├── receipt.json                         Cryptographic receipt
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
└── three_loop_architecture.png          Architecture diagram

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

## Certification

Organizations can certify their RIO implementations at three levels: Structural, Cryptographic, and Full Protocol. See [docs/CERTIFICATION.md](docs/CERTIFICATION.md) for the process and [docs/CERTIFICATION_CHECKLIST.md](docs/CERTIFICATION_CHECKLIST.md) for the submission checklist.

---

## Protocol Governance

Changes to the protocol follow the Protocol Change Proposal (PCP) process defined in [docs/GOVERNANCE.md](docs/GOVERNANCE.md). The versioning policy follows SemVer 2.0.0 as defined in [docs/VERSIONING.md](docs/VERSIONING.md).

---

See [SYSTEM-LAYERS.md](SYSTEM-LAYERS.md) for system structure.

---

## Status

This repository defines the RIO protocol and provides a reference verification implementation.

It is not a production system.

## Implementation Notes

Implementations intending to align with RIO v1.0 should at minimum:
- enforce authorization before execution
- bind actions to exact intent
- produce verifiable receipts

See the specification and verification materials for conformance requirements.

See Bondi specifications for orchestration, authority boundaries, and runtime behavior.

---

## License

All Rights Reserved (Apache 2.0 license pending) — see [LICENSE](LICENSE).
