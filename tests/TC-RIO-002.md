# Test Case: TC-RIO-002

**Title:** Denied Execution Due to Policy
**Status:** Defined
**Category:** Denial Path — Policy Block

---

## Purpose

Verify that a request denied at the Policy & Risk stage (Stage 4) does not reach Authorization (Stage 5) or Execution (Stage 6), but still produces a receipt and a ledger entry recording the denial.

---

## Protocol Steps Covered

Stages 1–5 (partial), 7–8 (Intake → Classification → Structured Intent → Policy & Risk → Receipt → Audit Ledger)

Stage 5 (Authorization) and Stage 6 (Execution Gate) are skipped because the policy denial prevents the request from reaching them.

---

## Invariants Covered

| Invariant | Assertion |
|-----------|-----------|
| INV-01 | The action traversed the required stages up to the denial point |
| INV-03 | A ledger entry was created for the denied action |
| INV-06 | The policy denial at Stage 4 prevented the request from reaching Stage 5; the request proceeded directly to Receipt and Audit Ledger with a denial record |

---

## Preconditions

1. A valid requester identity is registered and authenticated.
2. The requested action type is classified and has a matching policy rule that DENIES execution (e.g., the action exceeds a risk threshold, violates a constraint, or is explicitly prohibited).
3. The kill switch (EKS-0) is NOT engaged.

---

## Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Submit a valid request to Intake | Request ID, actor identity, timestamp, nonce, and raw input are recorded |
| 2 | Classification processes the request | Action type, domain, and preliminary risk level are assigned |
| 3 | Structured Intent converts the request | A canonical intent object is produced and schema-validated |
| 4 | Policy & Risk evaluates the intent | Policy decision is `deny`; risk score, denial reason, and constraints are recorded |
| 5 | Verify that Authorization (Stage 5) was NOT invoked | No authorization request was issued; no authorization token exists |
| 6 | Verify that Execution Gate (Stage 6) was NOT invoked | No execution token was issued; no execution occurred |
| 7 | Receipt is generated | Signed receipt contains intent hash, decision hash (denial), and timestamp; execution hash is absent or null |
| 8 | Ledger entry is created | Append-only ledger entry is written recording the denial, linked by hash chain |

---

## Pass Criteria

All of the following MUST be true:

1. The request traversed Stages 1 through 4.
2. The policy decision was `deny`.
3. Stage 5 (Authorization) was never invoked.
4. Stage 6 (Execution Gate) was never invoked.
5. A receipt was generated recording the denial.
6. A ledger entry was created recording the denial with the same fidelity as an approved action.
7. The receipt and ledger entry are hash-linked and signed.

---

## Failure Criteria

Any of the following constitutes a test failure:

1. The request reached Stage 5 (Authorization) despite a policy denial.
2. The request reached Stage 6 (Execution Gate) despite a policy denial.
3. No receipt was generated for the denied request.
4. No ledger entry was created for the denied request.
5. The denial record is missing the denial reason or risk score.
