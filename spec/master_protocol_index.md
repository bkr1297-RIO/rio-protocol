# RIO Master Protocol Index

This document provides a structured index of all RIO protocol specifications, architecture documents, safety controls, and verification models.

RIO is a governed execution architecture that converts goals and intents into authorized, executed, attested, and permanently recorded actions, with a learning loop that improves governance over time.

---

## 1. System Overview

The RIO system operates across the following high-level flow:

```
Goal → Intent Formation → Intent Validation → Governed Execution Protocol → Receipt → Ledger → Audit → Learning
```

RIO operates as a two-loop system:

- **Execution Loop** — controls and records actions in real time
- **Learning Loop** — improves policy, risk, and governance over time

See:
- `/spec/two_loop_architecture.md`
- `/spec/reference_architecture.md`

---

## 2. Pre-Runtime Protocols (Goal → Valid Intent)

| Protocol | File |
|----------|------|
| Goal Clarification | `/spec/intent_formation_and_validation_protocol.md` |
| Intent Formation | `/spec/intent_formation_and_validation_protocol.md` |
| Intent Validation | `/spec/intent_formation_and_validation_protocol.md` |
| Canonical Intent Schema | `/spec/canonical_intent_schema.md` |
| Intent Translation Layer | `/spec/intent_translation_layer.md` |

These protocols convert goals into structured, validated intents that can enter the governed execution runtime.

---

## 3. Governed Execution Protocol (Runtime Control)

| Step | Protocol | File |
|------|----------|------|
| 1 | Intake | `/spec/01_intake_protocol.md` |
| 2 | Classification | `/spec/04_risk_evaluation.md` |
| 3 | Structured Intent | `/spec/03_canonical_request.md` |
| 4 | Policy & Risk | `/spec/05_policy_constraints.md` |
| 5 | Authorization | `/spec/06_authorization.md` |
| 6 | Execution Gate | `/spec/07_execution.md` |
| 7 | Receipt | `/spec/receipt_protocol.md` |
| 8 | Audit Ledger | `/spec/audit_ledger_protocol.md` |
| 9 | Governance Learning | `/spec/governance_learning_protocol.md` |

These protocols enforce runtime control over all actions.

See `/spec/8_step_to_15_protocol_mapping.md` for the full mapping between the 8-step runtime and the 15 control protocols.

---

## 4. Safety and Security

| Component | File |
|-----------|------|
| Protocol Invariants | `/spec/protocol_invariants.md` |
| System Invariants | `/spec/system_invariants.md` |
| EKS-0 Kill Switch | `/safety/EKS-0_kill_switch.md` |
| Threat Model | `/spec/threat_model.md` |
| Verification Model | `/spec/verification_model.md` |

These components ensure the system is safe, secure, and auditable.

---

## 5. Data, Proof, and History

| Component | File |
|-----------|------|
| Canonical Intent Schema | `/spec/canonical_intent_schema.md` |
| Canonical Intent JSON Schema | `/spec/canonical_intent_schema.json` |
| Authorization Token Schema | `/spec/authorization_token_schema.json` |
| Receipt Protocol | `/spec/receipt_protocol.md` |
| Receipt JSON Schema | `/spec/receipt_schema.json` |
| Audit Ledger Protocol | `/spec/audit_ledger_protocol.md` |
| Ledger Entry JSON Schema | `/spec/ledger_entry_schema.json` |
| Governed Corpus | `/spec/governed_corpus.md` |

These components define how the system records, proves, and learns from decisions and actions.

---

## 6. Architecture

| Document | File |
|----------|------|
| Reference Architecture | `/spec/reference_architecture.md` |
| Two-Loop Architecture | `/spec/two_loop_architecture.md` |
| Intent Translation Layer | `/spec/intent_translation_layer.md` |
| System Architecture (4-Layer) | `/spec/system_architecture.md` |
| 15-Layer Architecture | `/architecture/15_layer_model.md` |
| 8-Step to 15-Protocol Mapping | `/spec/8_step_to_15_protocol_mapping.md` |

These documents define the system architecture and orchestration model.

---

## 7. Testing and Validation

| Test | File |
|------|------|
| TC-RIO-001 — Allowed execution | `/tests/TC-RIO-001.md` |
| TC-RIO-002 — Denied execution | `/tests/TC-RIO-002.md` |
| TC-RIO-003 — Kill switch blocks | `/tests/TC-RIO-003.md` |
| Protocol Test Matrix | `/spec/protocol_test_matrix.md` |
| Verification Tests (12 cases) | `/spec/verification_tests.md` |

These tests verify that the protocol enforces authorization, denial, and kill-switch behavior.

---

## 8. Summary

RIO is composed of:

- Goal and Intent Protocols
- Governed Execution Protocol
- Receipt and Ledger Protocols
- Verification and Audit Model
- Safety and Security Controls
- Learning and Governance Loop
- Intent Translation Layer
- Reference Architecture

Together, these components form a governed execution system for AI and software-driven actions.

---

## Note on Pre-Runtime Protocol

The file `/spec/intent_formation_and_validation_protocol.md` referenced in Section 2 is planned but not yet created. It will define the Goal Clarification, Intent Formation, and Intent Validation stages that precede the Governed Execution Protocol runtime.
