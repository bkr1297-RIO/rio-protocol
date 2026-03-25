# Test Case: TC-RIO-001

**Title:** Allowed Execution with Receipt and Ledger
**Status:** Defined
**Category:** Happy Path — Full Protocol Traversal

---

## Purpose

Verify that a request that passes all protocol stages results in successful execution, a signed receipt, and an immutable ledger entry.

---

## Protocol Steps Covered

Stages 1–8 (Intake → Classification → Structured Intent → Policy & Risk → Authorization → Execution Gate → Receipt → Audit Ledger)

---

## Invariants Covered

| Invariant | Assertion |
|-----------|-----------|
| INV-01 | The action traversed all preceding stages before execution |
| INV-02 | A signed receipt was produced containing intent hash, decision hash, execution hash, and timestamp |
| INV-03 | A ledger entry was created for the approved action |
| INV-04 | The execution gate verified a valid, time-bound, single-use authorization token |
| INV-07 | The execution gate re-verified authorization validity immediately before releasing execution |

---

## Preconditions

1. A valid requester identity is registered and authenticated.
2. The requested action type is classified and has a matching policy rule that permits execution.
3. A qualified authorizer (distinct from the requester) is available to approve the request.
4. The kill switch (EKS-0) is NOT engaged.

---

## Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Submit a valid request to Intake | Request ID, actor identity, timestamp, nonce, and raw input are recorded |
| 2 | Classification processes the request | Action type, domain, and preliminary risk level are assigned |
| 3 | Structured Intent converts the request | A canonical intent object is produced and schema-validated |
| 4 | Policy & Risk evaluates the intent | Policy decision is `allow`; risk score and constraints are recorded |
| 5 | Authorization is requested from a qualified authorizer | Authorization decision is `approved`; a signed authorization token is issued |
| 6 | Execution Gate verifies the authorization token | Token signature, expiration, and single-use status are verified; execution token is released |
| 7 | Action is executed | Execution completes successfully; execution record is produced |
| 8 | Receipt is generated | Signed receipt contains intent hash, decision hash, execution hash, and timestamp |
| 9 | Ledger entry is created | Append-only ledger entry is written, linked by hash chain to the previous entry |

---

## Pass Criteria

All of the following MUST be true:

1. The request traversed Stages 1 through 8 in order.
2. The receipt exists and contains valid intent hash, decision hash, execution hash, and timestamp.
3. The receipt signature verifies against the issuer's public key.
4. The ledger entry exists and is hash-linked to the previous entry.
5. The authorization token was single-use and has been consumed.
6. The authorizer identity is distinct from the requester identity.

---

## Failure Criteria

Any of the following constitutes a test failure:

1. Execution occurred without traversing all preceding stages.
2. No receipt was generated after execution.
3. The receipt is missing any required hash or timestamp.
4. No ledger entry was created.
5. The authorization token was reusable or expired at the time of execution.
