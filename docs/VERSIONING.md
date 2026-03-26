# RIO Protocol -- Versioning Policy

**Version:** 1.0  
**Status:** Active

This document defines the versioning scheme for the RIO Protocol, rules for version increments, backward compatibility guarantees, and the process for proposing changes.

---

## Versioning Scheme

The RIO Protocol uses **Semantic Versioning 2.0.0** (SemVer) with the format:

```
MAJOR.MINOR.PATCH
```

| Component | When to Increment | Example |
|-----------|-------------------|---------|
| **MAJOR** | Breaking changes to the protocol that require all implementations to update | Changing the hash algorithm from SHA-256, modifying the receipt schema in a non-backward-compatible way, changing the signing algorithm |
| **MINOR** | Backward-compatible additions to the protocol | Adding optional fields to the receipt schema, adding new conformance checks, adding new invariants |
| **PATCH** | Corrections to the specification that do not change protocol behavior | Fixing typos in the spec, clarifying ambiguous language, correcting test vector documentation |

---

## Current Version

The current protocol version is **1.0.0**, tagged in the repository as `v1.0.0`.

---

## What Constitutes a Breaking Change (MAJOR)

A change is breaking if any existing conformant implementation would fail verification after the change is applied. Specifically:

**Breaking changes include:**

- Changing the hash algorithm (e.g., SHA-256 to SHA-3)
- Changing the signing algorithm (e.g., Ed25519 to ECDSA)
- Removing or renaming required receipt fields
- Changing the receipt hash computation formula (the 19 signed fields or their order)
- Changing the ledger chain hash computation formula
- Changing the genesis hash value
- Changing the canonical JSON serialization rules
- Removing or redefining existing protocol invariants (INV-01 through INV-08)

**Non-breaking changes include:**

- Adding new optional fields to the receipt schema
- Adding new protocol invariants (INV-09+)
- Adding new conformance checks
- Adding new test vectors
- Clarifying specification language without changing behavior
- Adding new tools or documentation

---

## Backward Compatibility Guarantees

Within a MAJOR version (e.g., all 1.x.y releases):

1. **Receipt format stability.** All 22 required fields in the v1.0 receipt schema will remain required with the same names, types, and semantics. New optional fields may be added.

2. **Hash computation stability.** The SHA-256 hash formulas for `request_hash`, `receipt_hash`, and `current_ledger_hash` will not change. The 19 signed fields and their canonical order will remain fixed.

3. **Signature algorithm stability.** Ed25519 signing and verification will remain the required algorithm for the reference implementation path.

4. **Genesis hash stability.** The genesis hash `SHA256(b'GENESIS')` will remain the defined starting point for all ledger chains.

5. **Test vector validity.** All test vectors published in a MINOR release will remain valid in subsequent MINOR and PATCH releases within the same MAJOR version.

6. **Invariant stability.** Existing invariants (INV-01 through INV-08) will not be removed or weakened. New invariants may be added.

---

## Version Lifecycle

Each protocol version follows this lifecycle:

| Stage | Description |
|-------|-------------|
| **Draft** | Proposed changes under review. Not yet part of the protocol. |
| **Release Candidate** | Changes finalized, test vectors updated, awaiting final review. Tagged as `vX.Y.Z-rc.N`. |
| **Released** | Official protocol version. Tagged as `vX.Y.Z`. |
| **Deprecated** | Superseded by a newer MAJOR version. Implementations should migrate. |
| **Retired** | No longer supported. Conformance testing may not be available. |

---

## Deprecation Policy

When a new MAJOR version is released:

1. The previous MAJOR version enters **Deprecated** status.
2. Deprecated versions remain documented and their test vectors remain available for at least **12 months** after deprecation.
3. After 12 months, deprecated versions may be moved to **Retired** status.
4. Retired versions are archived but no longer actively maintained.

---

## Proposing Changes

All changes to the protocol must follow the Protocol Change Proposal (PCP) process:

1. **Open an issue** in the repository describing the proposed change.
2. **Submit a PCP** using the template in [PROTOCOL_CHANGE_TEMPLATE.md](PROTOCOL_CHANGE_TEMPLATE.md).
3. **Review period:** Minimum 14 days for MINOR changes, 30 days for MAJOR changes.
4. **Approval:** MAJOR changes require explicit approval from the protocol maintainers. MINOR and PATCH changes require at least one maintainer review.
5. **Implementation:** Update the specification, test vectors, and verification tooling.
6. **Release:** Tag the new version and update the CHANGELOG.

---

## Version History

| Version | Date | Type | Summary |
|---------|------|------|---------|
| 1.0.0 | 2025-03-23 | Initial | First stable release of the RIO Protocol |

---

## Related Documents

- [CHANGELOG.md](../CHANGELOG.md) -- Detailed change history
- [CONTRIBUTING.md](../CONTRIBUTING.md) -- How to contribute to the protocol
- [PROTOCOL_CHANGE_TEMPLATE.md](PROTOCOL_CHANGE_TEMPLATE.md) -- Template for proposing changes
