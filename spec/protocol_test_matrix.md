# RIO Protocol: Test Matrix

**Version:** 1.0.0
**Status:** Core Specification
**Category:** Verification

---

## Purpose

This document maps protocol test cases to the Governed Execution Protocol stages and protocol invariants they verify. Each test case is defined in full in the `/tests/` directory.

---

## Test Matrix

| Test Case | Description | Protocol Steps Covered | Invariants Covered |
|-----------|-------------|-------------------------|-------------------|
| TC-RIO-001 | Allowed execution with receipt and ledger | 1–8 | INV-01, INV-02, INV-03, INV-04, INV-07 |
| TC-RIO-002 | Denied execution due to policy | 1–5, 7–8 | INV-01, INV-03, INV-06 |
| TC-RIO-003 | Kill switch blocks execution | 5–8 | INV-01, INV-07, INV-08 |
