# Receipt Binding v0.1

**Status:** Candidate specification / non-normative until promoted  
**Register:** Packet grammar and receipt proof  
**Related receipts:**

- `tests/packet_grammar/RUN-RECEIPT-001.md`
- `tests/packet_grammar/RUN-RECEIPT-002.md`

---

## Purpose

Receipt Binding v0.1 defines the minimum structure for tying a verification claim to the evidence that supports it.

A receipt should not merely say that a check passed. It should bind together:

1. the exact commit tested,
2. the runtime surface used,
3. the command that ran,
4. the observed output,
5. the artifacts being verified,
6. the boundary of what the result does and does not prove.

---

## Core Rule

A verification receipt is only well-bound when it can answer:

| Question | Required Binding |
|---|---|
| What was tested? | artifact paths or test names |
| Where was it tested? | runtime surface |
| Which version was tested? | full commit SHA and short SHA |
| What command ran? | command string or script path |
| What happened? | observed output and exit code |
| What is not proven? | explicit boundary claims |

---

## Candidate Boundary Claims

A candidate receipt must not silently imply:

- live conformance,
- production enforcement,
- receipt-protocol verification,
- deployment,
- production readiness,
- certification.

If those are not proven, they must remain false or explicitly not claimed.

---

## Boundary

This candidate layer verifies receipt shape and binding completeness. It does not prove the external truth of the execution environment or independently re-run the tests.

External attestation and cryptographic receipt verification are later layers.

---

## Keeper

A receipt is not proof because it sounds official. A receipt is proof only to the extent that it binds claim, run, artifact, output, and boundary.
