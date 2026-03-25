# 8-Step Governed Execution Protocol to 15 Control Protocol Mapping

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Architecture Mapping

---

## Overview

The 8-step Governed Execution Protocol defines the high-level execution flow. The existing 15 protocol specifications define the detailed control mechanisms that implement and enforce each stage of the 8-step protocol. Together, the 8-step flow and the 15 control protocols form the full RIO governance system.

---

## Stage-to-Protocol Mapping

| 8-Step Stage | Stage Name | Supporting Protocol Files |
|--------------|------------|--------------------------|
| Step 1 | Intake | `01_intake_protocol.md`, `02_origin_verification.md` |
| Step 2 | Classification | `04_risk_evaluation.md` |
| Step 3 | Structured Intent | `03_canonical_request.md` |
| Step 4 | Policy & Risk | `05_policy_constraints.md` |
| Step 5 | Authorization | `06_authorization.md`, `15_time_bound_authorization.md` |
| Step 6 | Execution Gate | `07_execution.md` |
| Step 7 | Receipt / Attestation | `08_attestation.md` |
| Step 8 | Audit Ledger | `09_audit_ledger.md` |
| Step 9 | Governance Learning | `10_learning.md` |

---

## Cross-Cutting Control Protocols

The following control protocols do not map to a single execution stage. They define structural and governance properties that are enforced across all stages of the Governed Execution Protocol.

| Protocol | Name | Cross-Cutting Role |
|----------|------|--------------------|
| `11_independence.md` | Independence | Ensures that protocol components operate independently and cannot be bypassed by other components |
| `12_role_separation.md` | Role Separation | Enforces separation of duties across all stages — no single entity may perform conflicting roles in the same decision chain |
| `13_meta_governance.md` | Meta-Governance | Governs changes to the governance system itself — policy updates, role changes, and protocol modifications must be authorized through the protocol |
| `14_orchestration.md` | Orchestration | Coordinates the sequencing and handoff between stages, ensuring the correct order of execution and proper state transitions |

---

## How to Read This Mapping

The 8-step Governed Execution Protocol (defined in `governed_execution_protocol.md`) describes **what** happens at each stage: the purpose, inputs, and outputs. The 15 control protocols describe **how** each stage is implemented: the detailed processing rules, validation logic, failure conditions, security considerations, and audit requirements.

When implementing or auditing the RIO system, use the 8-step protocol as the high-level reference and the corresponding control protocols for the detailed specification of each stage's behavior.
