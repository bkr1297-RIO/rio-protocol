# Packet Bit Evidence

**Status:** Candidate specification / non-normative until promoted  
**Register:** Packet grammar  
**Related schema:** `spec/scribe_compiler_capsule.schema.json`

---

## Purpose

The Four-Bit Crossing Code proves gate math only after the bits have been set.

This note addresses the input seam: a packet must not merely assert that a bit is true. It must carry evidence references explaining why the bit was set.

---

## Rule

Each true bit in `crossing_code` must have at least one corresponding evidence item in `bit_evidence`.

| Bit | Evidence Should Show |
|---|---|
| Authority | Authorization artifact, human statement, delegated role, policy reference, or signature reference. |
| Scope | Scope constraint, allowed domain, prohibited domain, or review note. |
| Consequence | Side effect, risk, impact, or consequence assessment. |
| Return | Receipt plan, return channel, ledger requirement, or evidence requirement. |

False bits may have evidence explaining why they failed, but false-bit evidence is not required.

---

## Boundary

This candidate layer does not prove that the evidence is true in the external world. It prevents silent self-assertion by requiring the packet to carry the evidence references needed for later verification.

---

## Keeper

A bit is not true merely because the packet says it is true. A true bit must carry its evidence route.
