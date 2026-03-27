# RIO Protocol — Release Process

This document defines how a new version of the RIO Protocol is released, what version numbering rules apply, and what must be updated for every release.

---

## 1. Version Numbering

The RIO Protocol uses **semantic versioning**: `MAJOR.MINOR.PATCH`

| Component | When it increments | Example |
|---|---|---|
| `MAJOR` | A breaking or incompatible protocol change is introduced | v1.x.x → v2.0.0 |
| `MINOR` | New backward-compatible capability is added | v1.0.x → v1.1.0 |
| `PATCH` | Editorial correction or clarification only; no behavioral change | v1.0.0 → v1.0.1 |

### Rules

- All three components are non-negative integers.
- When `MAJOR` increments, `MINOR` and `PATCH` reset to `0`.
- When `MINOR` increments, `PATCH` resets to `0`.
- Pre-release versions may be denoted with a suffix: `v2.0.0-rc.1`, `v2.0.0-beta.1`.
- The current stable release is always the highest non-pre-release version.
- Version `v1.0.0` is the baseline. All prior development versions are `v0.x.x`.

---

## 2. Release Types

| Type | Trigger | Backward Compatible | Migration Required |
|---|---|---|---|
| **Patch release** | Editorial or clarification change | Yes | No |
| **Minor release** | New optional feature or capability | Yes | No |
| **Major release** | Breaking change to crypto, schema, or pipeline | No | Yes |
| **Security release** | Vulnerability fix | Depends on scope | Depends on scope |

---

## 3. What Must Be Updated for Every Release

All releases — patch, minor, or major — require the following artifacts to be reviewed and updated where applicable before the release is published.

### 3.1 Specification

- [ ] `spec/RIO_Protocol_Specification_vX.Y.md` — The canonical Markdown specification must reflect all accepted PCRs included in this release.
- [ ] `spec/RIO_Protocol_Specification_vX.Y.json` — The machine-readable JSON version must be regenerated or updated to match the Markdown specification exactly.
- [ ] Version number updated in the document header (`Version`, `Date`, `Status`).
- [ ] Table of contents is accurate.
- [ ] All normative `MUST`/`MUST NOT`/`SHOULD` statements are consistent with the implementation.

### 3.2 Test Vectors

- [ ] `spec/RIO_Protocol_Specification_vX.Y.md` Appendix C — All test vectors verified as correct for this version.
- [ ] `spec/RIO_Protocol_Specification_vX.Y.json` `appendix_c_test_vectors` section updated.
- [ ] New test vectors added for any new behavior introduced in this release.
- [ ] Existing test vectors confirmed unmodified for patch/minor releases (any modification constitutes a major change).
- [ ] All test vector expected values verified by independent computation (not copied from the implementation).

### 3.3 Conformance Tests

- [ ] `tests/conformance/run_conformance_tests.py` updated to reflect any new or changed test vectors.
- [ ] All built-in vectors produce PASS against the new expected values.
- [ ] SDK conformance modules (`sdk/python/rio_sdk/conformance.py`, `sdk/javascript/js-sdk/conformance.js`) updated to match.
- [ ] Conformance test runner executed; all vectors must pass before release.

### 3.4 Verification Tools

- [ ] `demo/demo_verify.py` — reviewed for compatibility with the new version. Updated if any formula or field has changed.
- [ ] `sdk/python/rio_sdk/verifier.py` — reviewed and updated.
- [ ] `sdk/javascript/js-sdk/verifier.js` — reviewed and updated.
- [ ] `sdk/python/rio_sdk/compliance.py` — reviewed and updated.
- [ ] All verification tools execute against example data and produce PASS.

### 3.5 Examples

- [ ] `examples/example_intent.json` — updated if the intake request schema changed.
- [ ] `examples/example_receipt_v2.json` — updated if the receipt format changed.
- [ ] `examples/example_ledger.json` — updated if any ledger hash formula changed; all hash values recomputed.
- [ ] `examples/example_verification_result.json` — regenerated from the updated ledger data.
- [ ] Demo scripts (`demo/demo_verify.py`, SDK examples) run against updated examples and produce PASS.

### 3.6 Version Number

- [ ] Version string updated in `spec/RIO_Protocol_Specification_vX.Y.md` header.
- [ ] Version string updated in `spec/RIO_Protocol_Specification_vX.Y.json` `_meta.version`.
- [ ] SDK version strings updated (`sdk/python/rio_sdk/__init__.py` `__version__`, `sdk/javascript/package.json` `version`).
- [ ] File names of spec artifacts updated to reflect new version (e.g., `v1.0.md` → `v1.1.md`).

### 3.7 Release Notes

- [ ] A release notes document is written before the release is published.
- [ ] Release notes include: version number, release date, summary of changes, list of accepted PCRs, backward compatibility statement, and migration instructions (for major releases).

---

## 4. Release Stages

Every release follows four stages in sequence. A release must not advance to the next stage until the current stage is complete.

### Stage 1 — Feature Freeze

All PCRs targeted for this release have been accepted. No new PCRs are accepted into the release after feature freeze.

- Duration: Minimum 7 days for minor releases; minimum 30 days for major releases.
- Output: A finalized list of changes for this release.

### Stage 2 — Specification Draft

The specification is updated to reflect all accepted PCRs. The draft is reviewed for internal consistency, completeness, and normative correctness.

- Output: A draft specification with version number marked as `DRAFT`.
- Review: At least one independent review of the draft specification is required before advancing.

### Stage 3 — Candidate Release (RC)

A release candidate is published with version suffix `-rc.N` (e.g., `v1.1.0-rc.1`). All required artifacts are updated as described in Section 3. Conformance tests and verification tools are run against the RC.

- Duration: Minimum 14 days for minor releases; minimum 30 days for major releases.
- If defects are found: A new RC is issued (`-rc.2`, etc.). The timer resets.
- Output: All checklist items (Section 5) pass.

### Stage 4 — Final Release

The RC is promoted to a final release. The `-rc.N` suffix is removed. The release is tagged, published, and announced.

- Output: Tagged release with all artifacts finalized. Status in spec changed to `Active`.

---

## 5. Release Checklist

See `docs/RELEASE_CHECKLIST.md` for the complete release checklist, which must be completed and signed off before any release is published.

---

## 6. Major Release Migration

For every major release (MAJOR increment), the following additional steps are required:

- [ ] A **Migration Guide** is published explaining exactly what existing implementations must change to achieve conformance with the new version.
- [ ] A **compatibility shim** or translation layer specification is published if existing receipts and ledger entries must remain verifiable under the new version.
- [ ] Both the old and new versions of the specification are kept available (old version moved to `spec/archive/`).
- [ ] A **transition period** of minimum 90 days is announced during which both versions are supported.
- [ ] The conformance test suite for the old version remains available for the duration of the transition period.

---

## 7. Hotfix Releases

A hotfix release may be issued outside the normal release cycle when a critical security vulnerability or correctness defect is found. Hotfix releases:

- Are always PATCH releases if they do not change normative behavior, or MINOR/MAJOR if they do.
- Skip Stage 1 (Feature Freeze) but must complete Stages 2, 3, and 4.
- Have a minimum RC period of 48 hours for critical security issues.
- Are announced immediately upon publication with a security advisory if applicable.
