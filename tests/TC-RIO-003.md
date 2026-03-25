# Test Case: TC-RIO-003

**Title:** Kill Switch Blocks Execution
**Status:** Defined
**Category:** Safety Path — EKS-0 Kill Switch

---

## Purpose

Verify that when the EKS-0 Kill Switch is engaged, the Execution Gate denies all pending and new execution requests regardless of their authorization status, and that all blocked requests still produce receipts and ledger entries.

---

## Protocol Steps Covered

Stages 5–8 (Authorization → Execution Gate → Receipt → Audit Ledger)

The test assumes the request has already passed Stages 1–4 and has a valid authorization. The kill switch is engaged before or during the Execution Gate stage.

---

## Invariants Covered

| Invariant | Assertion |
|-----------|-----------|
| INV-01 | The action traversed the required stages up to the block point |
| INV-07 | The execution gate re-verified conditions immediately before releasing execution and detected the kill switch |
| INV-08 | The kill switch overrode the valid authorization; execution was denied; a receipt and ledger entry were still produced |

---

## Preconditions

1. A valid requester identity is registered and authenticated.
2. The requested action has passed Stages 1–4 (Intake through Policy & Risk).
3. A valid authorization token has been issued (Stage 5 completed successfully).
4. The EKS-0 Kill Switch is engaged BEFORE the Execution Gate releases execution.

---

## Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Confirm that a valid authorization token exists for the request | Authorization token is present, signed, not expired, and not yet consumed |
| 2 | Engage the EKS-0 Kill Switch | Kill switch state transitions to `engaged`; engagement event is logged |
| 3 | Execution Gate processes the request | Gate detects kill switch is engaged; execution is DENIED regardless of valid authorization |
| 4 | Verify that no execution occurred | No execution record exists; no side effects were produced |
| 5 | Receipt is generated | Signed receipt records the block reason as `kill_switch_engaged`; contains intent hash, decision hash (blocked), and timestamp |
| 6 | Ledger entry is created | Append-only ledger entry records the kill switch block event, linked by hash chain |
| 7 | Submit a NEW request while kill switch is still engaged | New request is processed through Stages 1–4 but blocked at Stage 6 with the same behavior |

---

## Pass Criteria

All of the following MUST be true:

1. The Execution Gate denied execution despite a valid authorization token.
2. The denial reason is `kill_switch_engaged` (not a policy denial or authorization failure).
3. No execution occurred and no side effects were produced.
4. A receipt was generated for the blocked request.
5. A ledger entry was created for the blocked request.
6. The receipt and ledger entry correctly identify the kill switch as the blocking mechanism.
7. New requests submitted while the kill switch is engaged are also blocked at the Execution Gate.

---

## Failure Criteria

Any of the following constitutes a test failure:

1. Execution proceeded despite the kill switch being engaged.
2. No receipt was generated for the blocked request.
3. No ledger entry was created for the blocked request.
4. The receipt or ledger entry does not identify the kill switch as the blocking reason.
5. A new request was able to execute while the kill switch was engaged.

---

## Related Specification

See `/safety/EKS-0_kill_switch.md` for the full kill switch specification.
