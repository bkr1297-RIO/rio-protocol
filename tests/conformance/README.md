# Conformance Test Suite

This directory will contain the full conformance test documentation for the RIO protocol, produced by the Workstream 3 (Conformance Test) agent.

## Expected Contents

Each conformance test document follows a structured format with preconditions, steps, expected outcomes, and the invariants it validates.

### Test Categories

| Category | Test ID Range | Description |
|----------|---------------|-------------|
| Cryptographic Integrity | TC-CRYPTO-001 through TC-CRYPTO-015 | Hash computation, signing, verification |
| Policy Enforcement | TC-POLICY-001 through TC-POLICY-010 | Risk scoring, threshold decisions, escalation |
| State Machine | TC-STATE-001 through TC-STATE-010 | State transitions, terminal states, invalid transitions |
| Ledger Integrity | TC-LEDGER-001 through TC-LEDGER-010 | Hash chain, genesis block, tamper detection |
| Kill Switch | TC-KILL-001 through TC-KILL-005 | Fail-closed behavior, kill switch activation |
| Authorization | TC-AUTH-001 through TC-AUTH-007 | Token validation, expiry, scope enforcement |

## Relationship to Existing Tests

The three existing test case documents (`TC-RIO-001.md`, `TC-RIO-002.md`, `TC-RIO-003.md`) in the parent `tests/` directory are end-to-end scenario tests. The conformance tests in this directory are granular, testing individual protocol operations in isolation.

## Status

Pending — awaiting WS3 agent output.
