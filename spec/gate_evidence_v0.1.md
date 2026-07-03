# Gate Evidence v0.1

**Status:** Candidate specification / non-normative until promoted  
**Register:** Packet grammar and gate evidence  
**Related specs:**

- `spec/four_bit_crossing_code.md`
- `spec/packet_bit_evidence.md`
- `spec/scribe_compiler_capsule.schema.json`

---

## Purpose

Gate Evidence v0.1 defines the first evidence rule for packet movement:

> No true gate bit may stand as a naked assertion.

The Four-Bit Crossing Code decides whether a packet may move only after the bits have been set. Gate Evidence v0.1 checks whether each true bit carries an evidence route.

---

## Core Rule

For each bit in the Four-Bit Crossing Code:

```text
Authority AND Scope AND Consequence AND Return
```

if the bit is `true`, the packet must contain at least one matching evidence reference.

| True Bit | Required Evidence Route |
|---|---|
| Authority | authorization artifact, human statement, delegated role, policy reference, or signature reference |
| Scope | allowed domain, prohibited domain, scope constraint, or review note |
| Consequence | side-effect acknowledgement, risk note, consequence assessment, or impact note |
| Return | receipt plan, return channel, ledger requirement, or evidence requirement |

False bits may carry evidence explaining why they failed, but false-bit evidence is not required.

---

## Candidate Verdict Relationship

Gate Evidence v0.1 does not replace the Four-Bit Crossing Code.

It adds a prior check:

1. Are the bits present?
2. Are true bits supported by evidence?
3. Does the truth table produce the expected verdict?

A packet with all four bits set to true but missing evidence is not a clean allow. It must fail evidence validation before crossing.

---

## Consentability Relationship

When explicit consent is required, consent evidence must also be present and understandable:

- stakes,
- risks,
- benefits,
- time bound,
- revocability,
- comprehension basis.

A packet cannot rely on ceremonial approval alone. It must carry enough structure to show what the approving party was consenting to.

---

## Boundary

This candidate layer does not prove the external truth of the evidence. It only proves that the packet carries the evidence route needed for later verification.

External evidence verification is a later layer.

---

## Keeper

No naked yes. Every true bit needs a trail.
