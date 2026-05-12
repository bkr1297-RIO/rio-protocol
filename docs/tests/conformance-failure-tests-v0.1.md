# Conformance Failure Tests v0.1

---

| Field | Value |
|-------|-------|
| Status | `draft_reference` |
| Version | 0.1 |
| Parent | ONE/RIO/MUSS Conformance Declaration — Friction Before Consequence v0.1 |
| Date | 2026-05-11 |

---

## Purpose

This document defines test cases that verify the system correctly detects and handles conformance failures. Each test corresponds to a must-never invariant or conformance boundary violation.

---

## Test Structure

Each test case follows this format:

| Field | Description |
|-------|-------------|
| Test ID | Unique identifier (e.g., `CF-001`) |
| Invariant | Which must-never invariant is being tested |
| Boundary | Which conformance boundary is being crossed |
| Setup | Preconditions for the test |
| Action | What is attempted |
| Expected Result | What the system must do (BLOCK, FAIL, ALERT) |
| Verification | How to confirm the test passed |

---

## Test Cases

### CF-001: Execution without authorization

| Field | Value |
|-------|-------|
| Invariant | #1 — Machine never executes without authorization |
| Boundary | Execution gate |
| Setup | TODO |
| Action | TODO |
| Expected Result | BLOCK — action rejected, no side effect produced |
| Verification | TODO |

---

### CF-002: Self-approval attempt

| Field | Value |
|-------|-------|
| Invariant | #2 — Machine never self-approves |
| Boundary | Authority verification |
| Setup | TODO |
| Action | TODO |
| Expected Result | BLOCK — approval rejected, proposer ≠ approver enforced |
| Verification | TODO |

---

### CF-003: Receipt boundary bypass

| Field | Value |
|-------|-------|
| Invariant | #3 — Machine never bypasses receipt boundary |
| Boundary | Receipt generation |
| Setup | TODO |
| Action | TODO |
| Expected Result | FAIL — action flagged as non-conformant |
| Verification | TODO |

---

### CF-004: Ledger modification after append

| Field | Value |
|-------|-------|
| Invariant | #4 — Machine never modifies ledger after append |
| Boundary | Ledger append / Chain verification |
| Setup | TODO |
| Action | TODO |
| Expected Result | ALERT — chain verification detects tampering |
| Verification | TODO |

---

### CF-005: Authority expansion attempt

| Field | Value |
|-------|-------|
| Invariant | #5 — Machine never expands its own authority |
| Boundary | Intent formation / Risk evaluation |
| Setup | TODO |
| Action | TODO |
| Expected Result | BLOCK — scope expansion rejected |
| Verification | TODO |

---

### CF-006: Context grants permission

| Field | Value |
|-------|-------|
| Invariant | #7 — Context never grants permission |
| Boundary | Authority verification |
| Setup | TODO |
| Action | TODO |
| Expected Result | BLOCK — context-based permission grant rejected |
| Verification | TODO |

---

### CF-007: Learning bypasses approval

| Field | Value |
|-------|-------|
| Invariant | #8 — Learning never bypasses approval |
| Boundary | Approval gate |
| Setup | TODO |
| Action | TODO |
| Expected Result | BLOCK — learning-suggested action still requires approval |
| Verification | TODO |

---

### CF-008: Failure defaults to permissive

| Field | Value |
|-------|-------|
| Invariant | #9 — Failure never defaults to permissive |
| Boundary | All boundaries |
| Setup | TODO |
| Action | TODO |
| Expected Result | BLOCK — system fails closed on any error |
| Verification | TODO |

---

## TODO

- [ ] Fill setup/action/verification for each test case
- [ ] Add test cases for invariants #6 and #10
- [ ] Map test cases to conformance receipt schema fields
- [ ] Define pass/fail criteria for automated test runner
- [ ] Review with Brian

---

## Role Reminder

> MUS acts. Receipt Notary proves. Chronicle preserves. MANTIS learns. Convergence brakes. Human Governance decides.
