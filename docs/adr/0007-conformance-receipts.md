# ADR-0007: Conformance Receipts

---

| Field | Value |
|-------|-------|
| Status | `draft_reference` |
| Date | 2026-05-11 |
| Deciders | Brian Rassier (pending) |
| Parent | ONE/RIO/MUSS Conformance Declaration v0.1 |

---

## Context

The base receipt protocol (see `rio-receipt-protocol`) proves that governed events occurred. However, it does not prove that the system was conformant at the time of the event. A separate receipt type is needed to prove that conformance boundaries were checked.

---

## Decision

Introduce conformance receipts as a distinct receipt type that:
- Records which conformance boundary was checked.
- Records the result (CONFORMANT / NON_CONFORMANT / PARTIAL).
- Records which must-never invariants were verified.
- Is signed and hash-chained like base receipts.
- Can be independently verified.

---

## Relationship to Base Receipts

| Receipt Type | Proves |
|-------------|--------|
| Base receipt | A governed event occurred and was recorded. |
| Conformance receipt | A conformance boundary was checked and the result was recorded. |
| Accountability determination receipt | Who is accountable was determined and the evidence chain was recorded. |

---

## Consequences

- Conformance becomes provable, not just claimed.
- Conformance failures become detectable and auditable.
- The system can prove it checked before it acted — not just that it acted.
- Receipts prove events. Conformance receipts prove boundaries.

---

## TODO

- [ ] Finalize conformance receipt schema (see `docs/specs/conformance-receipt.schema.yaml`)
- [ ] Define relationship between conformance receipt and base receipt (linked or embedded?)
- [ ] Define when conformance receipts are generated (every action? periodic audit? on-demand?)
- [ ] Define storage: same ledger or separate conformance ledger?
- [ ] Review and promote with Brian

---

## Role Reminder

> MUS acts. Receipt Notary proves. Chronicle preserves. MANTIS learns. Convergence brakes. Human Governance decides.
