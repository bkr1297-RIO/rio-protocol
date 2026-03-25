# RIO Protocol: Protocol Invariants

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Safety and Correctness

---

## 1. Purpose

This document defines the protocol invariants for the Governed Execution Protocol. These are safety and correctness properties that MUST never be violated by any implementation. They apply across all runtime stages and are enforced by the runtime, authorization system, and execution gate.

Protocol invariants are distinct from system invariants (see `system_invariants.md`). System invariants define properties of the underlying infrastructure (cryptographic integrity, ledger immutability, hash chain correctness). Protocol invariants define properties of the governed execution flow itself — the rules that ensure every action traverses the correct stages in the correct order with the correct outcomes.

---

## 2. Invariant Definitions

| ID | Statement | Applies To | Enforcement Point |
|----|-----------|-----------|-------------------|
| INV-01 | Every action that reaches execution MUST have traversed all preceding protocol stages in order: Intake → Classification → Structured Intent → Policy & Risk → Authorization → Execution Gate. | Stages 1–6 | Execution Gate (Stage 6) |
| INV-02 | Every executed action MUST produce a signed receipt containing the intent hash, decision hash, execution hash, and timestamp. | Stage 7 | Receipt / Attestation (Stage 7) |
| INV-03 | Every protocol decision — whether approved, denied, or blocked — MUST produce a ledger entry. Denied and blocked actions are recorded with the same fidelity as approved actions. | Stage 8 | Audit Ledger (Stage 8) |
| INV-04 | No action SHALL be executed without a valid, time-bound, single-use authorization token. | Stage 6 | Execution Gate (Stage 6) |
| INV-05 | The requester and the authorizer MUST be distinct entities. No entity may authorize its own request. | Stage 5 | Authorization (Stage 5) |
| INV-06 | A policy denial at Stage 4 MUST prevent the request from reaching Stage 5 (Authorization). The request MUST proceed directly to Stage 7 (Receipt) and Stage 8 (Audit Ledger) with a denial record. | Stage 4 | Policy & Risk Check (Stage 4) |
| INV-07 | The Execution Gate MUST re-verify authorization validity (signature, expiration, single-use status) immediately before releasing execution. Stale or revoked authorizations MUST be rejected even if they were valid at the time of issuance. | Stage 6 | Execution Gate (Stage 6) |
| INV-08 | When the kill switch (EKS-0) is engaged, the Execution Gate MUST deny all pending and new execution requests regardless of their authorization status. Kill switch events MUST still produce receipts and ledger entries. | Stages 5–8 | Execution Gate (Stage 6), Receipt (Stage 7), Audit Ledger (Stage 8) |

---

## 3. Invariant Categories

| Category | Invariants | Description |
|----------|-----------|-------------|
| Completeness | INV-01, INV-02, INV-03 | Every action traverses all required stages; every outcome is recorded |
| Authorization Safety | INV-04, INV-05, INV-07 | Authorization is valid, time-bound, single-use, and independently verified |
| Fail-Closed Behavior | INV-06, INV-08 | Denials and kill switch events follow deterministic, auditable paths |

---

## 4. Relationship to System Invariants

The protocol invariants defined here operate at the protocol flow level. They depend on the system invariants defined in `system_invariants.md` for their underlying guarantees:

| Protocol Invariant | Depends On | Reason |
|-------------------|-----------|--------|
| INV-01 | ORD-001, ORD-003 | Stage ordering depends on ordering invariants |
| INV-02 | CRYP-001, AUD-001 | Receipt signing depends on cryptographic and audit invariants |
| INV-03 | AUD-002, AUD-003, AUD-004 | Ledger recording depends on audit invariants |
| INV-04 | AUTH-001, AUTH-003, AUTH-004 | Authorization token validity depends on authorization invariants |
| INV-05 | AUTH-002, GOV-002 | Role separation depends on authorization and governance invariants |
| INV-07 | CRYP-001, FC-001 | Re-verification depends on cryptographic and fail-closed invariants |
| INV-08 | FC-001, AUD-002 | Kill switch behavior depends on fail-closed and audit invariants |

---

## 5. Verification

Each protocol invariant is tested by one or more test cases in the `/tests/` directory. See `/spec/protocol_test_matrix.md` for the mapping between test cases and invariants.
