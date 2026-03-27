# RIO Protocol — Governance

This document defines who governs the RIO Protocol, how protocol changes are proposed and reviewed, and how backward compatibility is maintained across versions.

---

## 1. Governance Structure

The RIO Protocol is governed by the **Protocol Steward** — the individual or organization responsible for the reference implementation and canonical specification.

| Role | Responsibility |
|---|---|
| **Protocol Steward** | Final authority on protocol changes. Owns the canonical specification, test vectors, and reference implementation. |
| **Specification Maintainer** | Drafts, edits, and publishes the formal protocol specification document. |
| **Conformance Reviewer** | Reviews proposed changes for impact on conformance levels and test vector correctness. |
| **Community Contributor** | Any developer or organization that proposes protocol improvements via the change request process. |

A single person may hold multiple roles. The Protocol Steward role may be delegated but cannot be subdivided.

---

## 2. Who Can Propose Protocol Changes

Anyone may propose a protocol change. Proposals are not restricted to maintainers or certified implementors.

To be considered, a proposal must:

1. Identify a specific limitation, security issue, ambiguity, or missing capability in the current protocol.
2. Propose a concrete change to the specification, test vectors, or conformance requirements.
3. Describe the impact on existing conforming implementations (breaking vs. non-breaking).
4. Be submitted in writing with sufficient detail for independent review.

---

## 3. How Changes Are Proposed

### Step 1 — Draft a Protocol Change Request (PCR)

A PCR must include:

| Field | Description |
|---|---|
| `PCR-ID` | Sequential identifier (e.g., `PCR-0001`) |
| `Title` | Short descriptive title |
| `Status` | One of: `Draft`, `Under Review`, `Accepted`, `Rejected`, `Withdrawn` |
| `Type` | One of: `Minor`, `Major`, `Security`, `Editorial` |
| `Motivation` | Why this change is needed |
| `Proposed Change` | Exact description of what changes in the spec, test vectors, or behavior |
| `Backward Compatibility` | Whether existing conforming implementations remain conformant |
| `Test Vector Impact` | Whether new or updated test vectors are required |
| `Author` | Name or identifier of the proposer |
| `Date` | Date of submission |

### Step 2 — Submit the PCR

Submit the PCR in writing to the Specification Maintainer. The PCR is assigned a PCR-ID and its status is set to `Under Review`.

### Step 3 — Public Comment Period

All PCRs with status `Under Review` are made available for comment for a minimum of **14 calendar days** before a decision is made. Exception: Security changes may be reviewed on an expedited timeline with a 48-hour minimum review window.

---

## 4. How Changes Are Reviewed

The Conformance Reviewer evaluates each PCR against the following criteria:

| Criterion | Questions Asked |
|---|---|
| **Necessity** | Does the change address a real limitation or defect? |
| **Correctness** | Is the proposed change technically sound? |
| **Completeness** | Does the proposal fully specify the change, including edge cases? |
| **Testability** | Can conformance with the change be verified by test vectors or automated checks? |
| **Compatibility** | What is the impact on Level 1, Level 2, and Level 3 conformant implementations? |
| **Security** | Does the change introduce or close a security vulnerability? |

The Conformance Reviewer produces a written review with a recommendation of `Accept`, `Reject`, or `Revise`.

---

## 5. How Changes Are Accepted or Rejected

The Protocol Steward makes the final decision after the review period and conformance review are complete.

| Decision | Meaning |
|---|---|
| **Accepted** | The change is incorporated into the next protocol release. |
| **Accepted with Modifications** | The change is incorporated with adjustments specified by the Protocol Steward. |
| **Rejected** | The change is not incorporated. The written rejection must state the reason. |
| **Withdrawn** | The author withdraws the PCR before a decision is made. |
| **Deferred** | The change is valid but will be considered in a future release cycle. |

All decisions are recorded in the PCR log with their rationale. Rejected PCRs may be resubmitted with revisions.

---

## 6. Minor vs. Major Protocol Changes

### Minor Change

A change is **Minor** if:

- It does not alter any cryptographic algorithm, parameter, or encoding rule.
- It does not change the structure, field names, or required fields of any data structure defined in the specification.
- It does not change the behavior of any pipeline stage, gate, or invariant.
- It does not require existing conforming implementations to be modified to remain conformant.

Minor changes result in a **patch or minor version increment** (e.g., v1.0.0 → v1.0.1 or v1.0.0 → v1.1.0).

Examples of minor changes:
- Clarifying ambiguous wording in the specification.
- Adding optional fields to the intake response.
- Adding new test vectors that cover existing behavior.
- Updating documentation, examples, or conformance guides.

### Major Change

A change is **Major** if:

- It alters any cryptographic algorithm, parameter, curve, encoding format, or hash formula.
- It adds, removes, or renames required fields in any data structure.
- It changes the pipeline stage order, gate guard sequence, or invariant definitions.
- It requires existing conforming implementations to be modified to remain conformant.
- It changes the GENESIS anchor string or hash chain linkage rules.

Major changes result in a **major version increment** (e.g., v1.x.x → v2.0.0).

Major changes require:
- A migration guide describing what existing implementations must change.
- A transition period (minimum 90 days) during which both the old and new versions are supported and documented.
- New test vectors covering the changed behavior.
- An updated conformance suite.

### Security Changes

Security changes may be Minor or Major depending on their scope. They follow the same process but may use an expedited review timeline. Security changes that fix a vulnerability in the cryptographic core are always treated as Major changes.

---

## 7. Backward Compatibility

### Policy

The RIO Protocol follows **semantic versioning** (`MAJOR.MINOR.PATCH`):

- **PATCH** releases (v1.0.0 → v1.0.1): Backward compatible. Implementations conformant at the previous version remain conformant. Typically editorial or clarification-only changes.
- **MINOR** releases (v1.0.0 → v1.1.0): Backward compatible. New optional capabilities may be added. Existing conformant implementations remain conformant at their current level.
- **MAJOR** releases (v1.0.0 → v2.0.0): May be backward incompatible. Existing implementations must be reviewed and updated to achieve conformance with the new version.

### Compatibility Guarantees

| Scenario | Guarantee |
|---|---|
| A v1.0.0 conformant implementation running against a v1.x.x gateway | Fully interoperable |
| A v1.0.0 conformant implementation running against a v2.0.0 gateway | Not guaranteed; migration required |
| Receipts and ledger entries produced by a v1.x.x gateway | Verifiable by any v1.x.x verifier |
| Receipts produced by a v1.x.x gateway | Not guaranteed to be verifiable by a v2.0.0 verifier without a compatibility shim |

### Ledger Continuity

Hash chains in `execution_ledger` and `post_execution_ledger` are append-only. A protocol version upgrade does not reset or invalidate existing chains. New entries after a version upgrade must continue the chain from the last existing entry's hash. Entries produced under different protocol versions may coexist in the same chain.

---

## 8. Editorial Changes

Changes that correct typographical errors, improve clarity without altering meaning, or reorganize content without changing normative requirements are **Editorial** changes. They do not require a PCR and may be applied directly by the Specification Maintainer. Editorial changes result in a PATCH version increment.

---

## 9. Protocol Change Log

All accepted PCRs are recorded in a changelog maintained alongside the specification. Each entry includes the PCR-ID, title, type, version in which it was incorporated, and a one-sentence summary of the change.
