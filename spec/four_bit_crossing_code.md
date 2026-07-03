# Four-Bit Crossing Code

**Status:** Candidate specification / non-normative until promoted  
**Register:** Packet grammar and gate semantics  
**Related schema:** `spec/scribe_compiler_capsule.schema.json`

---

## Purpose

The Four-Bit Crossing Code is the minimum predicate set for deciding whether a proposed packet may cross from formation into consequential movement.

A packet may be well-formed without being authorized.  
A packet may be authorized without being allowed to execute.  
A packet may produce a receipt without becoming settled meaning, certification, or embodied learning.

---

## Crossing Predicate

A crossing may be allowed only when all four bits are true:

```text
Authority AND Scope AND Consequence AND Return
```

If any bit is false, the packet must not proceed as a clean allowed crossing.

---

## Bit Definitions

| Bit | Question | False Means |
|---|---|---|
| Authority | Is there a valid human or organizational authority envelope for this movement? | The packet is denied. Capability does not become permission. |
| Scope | Is the proposed movement inside the authorized bounds? | The packet requires review or narrowing. Authorization does not cover drift. |
| Consequence | Have side effects and material consequences been recognized? | The packet requires clarification or review. Hidden consequence cannot cross silently. |
| Return | Is there a receipt and return path back to SourcePoint or the authorizing body? | The packet is denied. No log, no go. |

---

## Candidate Verdict Rules

| Condition | Candidate Verdict |
|---|---|
| All four bits are true | allow |
| Authority is false | deny |
| Return is false | deny |
| Scope is false | require_review |
| Consequence is false | clarify |
| Multiple non-authority bits are false | require_review unless Return is false, then deny |

These candidate rules are intentionally conservative. A future normative gate may add policy bundles, risk tiers, domain-specific constraints, or stronger denial behavior.

---

## Truth Table Requirement

The test dataset for this rule should contain all 16 possible boolean combinations of:

```text
authority, scope, consequence, return
```

Each row must include:

1. input bits,
2. expected verdict,
3. reason code,
4. whether the packet may cross.

---

## Boundary

This specification defines candidate packet-grammar behavior. It does not claim runtime enforcement, live conformance, production readiness, or certification.

---

## Keeper

Generate freely. Cross only by law. Return with proof.
