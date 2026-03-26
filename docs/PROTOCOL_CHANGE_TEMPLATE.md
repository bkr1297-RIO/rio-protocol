# Protocol Change Proposal (PCP) Template

**PCP Number:** PCP-XXXX  
**Title:** [Descriptive title of the proposed change]  
**Author:** [Name and contact]  
**Status:** Draft | Review | Accepted | Rejected | Withdrawn  
**Type:** MAJOR | MINOR | PATCH  
**Created:** [YYYY-MM-DD]  
**Target Version:** [e.g., 1.1.0 or 2.0.0]

---

## Abstract

A concise summary of the proposed change in 2-3 sentences. What is being changed and why?

---

## Motivation

Describe the problem or limitation that this change addresses. Why is the current protocol insufficient? Include specific use cases, failure modes, or regulatory requirements that motivate this change.

---

## Specification

Provide the complete technical specification of the proposed change. This section must be precise enough that an independent implementer can apply the change without ambiguity.

### Current Behavior

Describe how the protocol currently works in the area being changed. Reference specific sections of the canonical specification.

### Proposed Behavior

Describe the new behavior after the change is applied. Include:

- Modified data structures (with field names, types, and constraints)
- Modified algorithms (with pseudocode or formulas)
- Modified invariants (with formal definitions)
- Modified verification checks (with expected outcomes)

### Migration Path

For MAJOR changes: describe how existing implementations should migrate. For MINOR changes: describe how the change is backward-compatible.

---

## Backward Compatibility

Analyze the impact on existing implementations:

- **Receipt format:** Are existing receipts still valid after this change?
- **Verification:** Can existing verifiers still verify receipts produced before this change?
- **Ledger:** Are existing ledger chains still valid?
- **Test vectors:** Do existing test vectors need updating?

If the change is breaking, justify why a MAJOR version increment is necessary.

---

## Test Vectors

Provide new test vectors that exercise the proposed change. Each test vector must include:

- Input data (receipt JSON, ledger JSON, or both)
- Expected verification result (PASS or FAIL)
- Explanation of what the test vector validates

---

## Security Considerations

Analyze the security implications of the proposed change:

- Does this change affect the cryptographic guarantees of the protocol?
- Does this change affect the tamper-evidence of the ledger?
- Does this change introduce new attack surfaces?
- Does this change affect any of the 8 protocol invariants?

---

## Conformance Impact

Describe how this change affects conformance testing:

- Which conformance level(s) are affected?
- Are new conformance checks required?
- Do existing conformance checks need modification?

---

## Implementation Notes

Optional section for implementation guidance:

- Suggested implementation approach
- Performance considerations
- Known edge cases
- Reference implementation changes required

---

## References

List any external documents, standards, or prior art referenced in this proposal.

---

## Review History

| Date | Reviewer | Decision | Notes |
|------|----------|----------|-------|
| | | | |
