# RIO Protocol — Release Checklist

Complete this checklist before publishing any protocol release. All items must be checked and signed off. No release may be published with unchecked items.

**Release version:** ___________________________  
**Release type:** ☐ Patch   ☐ Minor   ☐ Major   ☐ Security hotfix  
**Release manager:** ___________________________  
**Target release date:** ___________________________  

---

## 1. Pre-Release Gates

These gates must be confirmed before any release work begins.

| # | Gate | Done | Notes |
|---|---|---|---|
| G-01 | All PCRs targeted for this release have been accepted and recorded | ☐ | |
| G-02 | Feature freeze has been declared (no new PCRs accepted into this release) | ☐ | |
| G-03 | For major releases: transition period announcement has been drafted | ☐ | N/A for patch/minor |
| G-04 | For security releases: vulnerability has been confirmed and scoped | ☐ | N/A if not security |

---

## 2. Specification Updated

| # | Item | Done | Notes |
|---|---|---|---|
| S-01 | `spec/RIO_Protocol_Specification_vX.Y.md` — all accepted PCRs reflected | ☐ | |
| S-02 | Version number updated in document header (`Version: X.Y.Z`) | ☐ | |
| S-03 | Date updated in document header | ☐ | |
| S-04 | Status updated to `Active` (was `Draft` during development) | ☐ | |
| S-05 | Table of contents is accurate and all links resolve | ☐ | |
| S-06 | All normative `MUST`/`MUST NOT`/`SHOULD` statements reviewed for consistency | ☐ | |
| S-07 | Spec reviewed by at least one person other than the author | ☐ | Reviewer: ________ |
| S-08 | Previous version of spec moved to `spec/archive/` (for major releases) | ☐ | N/A for patch/minor |
| S-09 | `spec/RIO_Protocol_Specification_vX.Y.json` regenerated and validated as well-formed JSON | ☐ | |
| S-10 | JSON spec `_meta.version` matches Markdown spec version | ☐ | |

---

## 3. Test Vectors Updated

| # | Item | Done | Notes |
|---|---|---|---|
| T-01 | Appendix C of spec reviewed; all test vectors confirmed correct for this version | ☐ | |
| T-02 | For any changed formula or field: expected values recomputed by independent calculation (not copied from implementation) | ☐ | |
| T-03 | For patch/minor releases: existing test vector expected values are unchanged | ☐ | N/A if major |
| T-04 | New test vectors added for any new behavior introduced in this release | ☐ | N/A if no new behavior |
| T-05 | `spec/RIO_Protocol_Specification_vX.Y.json` `appendix_c_test_vectors` section matches Markdown Appendix C | ☐ | |
| T-06 | Test vector IDs are sequential and non-conflicting | ☐ | |

---

## 4. Conformance Tests Updated

| # | Item | Done | Notes |
|---|---|---|---|
| C-01 | `tests/conformance/run_conformance_tests.py` — all vector expected values match updated Appendix C | ☐ | |
| C-02 | `sdk/python/rio_sdk/conformance.py` — built-in vectors match updated Appendix C | ☐ | |
| C-03 | `sdk/javascript/js-sdk/conformance.js` — built-in vectors match updated Appendix C | ☐ | |
| C-04 | `run_conformance_tests.py` executed; all vectors produce `PASS`; overall result `PASS` | ☐ | Attach output |
| C-05 | SDK Python conformance runner executed; all vectors produce `PASS` | ☐ | Attach output |
| C-06 | SDK JavaScript conformance runner executed; all vectors produce `PASS` | ☐ | Attach output |
| C-07 | New conformance tests added for any new behavior | ☐ | N/A if no new behavior |

---

## 5. Verifier Updated

| # | Item | Done | Notes |
|---|---|---|---|
| V-01 | `demo/demo_verify.py` — reviewed and updated for any changed formula or field | ☐ | |
| V-02 | `sdk/python/rio_sdk/verifier.py` — reviewed and updated | ☐ | |
| V-03 | `sdk/javascript/js-sdk/verifier.js` — reviewed and updated | ☐ | |
| V-04 | `sdk/python/rio_sdk/compliance.py` — reviewed and updated | ☐ | |
| V-05 | `demo/demo_verify.py` executed against updated example data; all 4 checks `PASS`; overall `PASS` | ☐ | Attach output |
| V-06 | `sdk/examples/python_verify_example.py` executed; overall `PASS` | ☐ | Attach output |
| V-07 | `sdk/examples/js_verify_example.js` executed; overall `PASS` | ☐ | Attach output |
| V-08 | `sdk/examples/python_conformance_example.py` executed; conformance `PASS`, compliance level as expected | ☐ | Attach output |

---

## 6. Version Number Updated

| # | Item | Done | Notes |
|---|---|---|---|
| N-01 | `spec/RIO_Protocol_Specification_vX.Y.md` — version in filename matches release version | ☐ | |
| N-02 | `spec/RIO_Protocol_Specification_vX.Y.json` — version in filename matches release version | ☐ | |
| N-03 | `spec/RIO_Protocol_Specification_vX.Y.json` `_meta.version` = `"X.Y.Z"` | ☐ | |
| N-04 | `sdk/python/rio_sdk/__init__.py` `__version__` = `"X.Y.Z"` | ☐ | |
| N-05 | `sdk/javascript/package.json` `version` = `"X.Y.Z"` | ☐ | |
| N-06 | No other files contain hardcoded version strings referencing the previous version | ☐ | Search for old version |

---

## 7. Examples Updated

| # | Item | Done | Notes |
|---|---|---|---|
| E-01 | `examples/example_intent.json` — updated if intake request schema changed | ☐ | |
| E-02 | `examples/example_receipt_v2.json` — updated if receipt format changed; `receipt_hash` recomputed | ☐ | |
| E-03 | `examples/example_ledger.json` — all hash values recomputed if any formula changed | ☐ | |
| E-04 | `examples/example_verification_result.json` — regenerated from updated example data | ☐ | |
| E-05 | All example hash values verified by independent computation | ☐ | |
| E-06 | Independent verifier produces `PASS` against updated example ledger and receipt | ☐ | Attach output |

---

## 8. Release Notes Written

| # | Item | Done | Notes |
|---|---|---|---|
| R-01 | Release notes document created | ☐ | |
| R-02 | Release notes include: version number, release date | ☐ | |
| R-03 | Release notes include: summary of all changes | ☐ | |
| R-04 | Release notes include: list of accepted PCRs with IDs and titles | ☐ | |
| R-05 | Release notes include: backward compatibility statement | ☐ | |
| R-06 | Release notes include: migration instructions (major releases only) | ☐ | N/A for patch/minor |
| R-07 | Release notes include: security advisory (security releases only) | ☐ | N/A if not security |

---

## 9. Candidate Release (RC) Validation

| # | Item | Done | Notes |
|---|---|---|---|
| RC-01 | RC published with version suffix `-rc.1` (or `-rc.N`) | ☐ | |
| RC-02 | Minimum RC period observed: 14 days (minor), 30 days (major), 48 hours (security hotfix) | ☐ | RC start date: ______ |
| RC-03 | No defects found during RC period; or all defects resolved and a new RC issued | ☐ | |
| RC-04 | All checklist items above completed against the RC | ☐ | |

---

## 10. Final Release Sign-Off

| # | Item | Done | Notes |
|---|---|---|---|
| F-01 | All items in Sections 1–9 are checked | ☐ | |
| F-02 | Release tagged in version control | ☐ | Tag: `vX.Y.Z` |
| F-03 | Spec status updated from `Draft` to `Active` in the final published document | ☐ | |
| F-04 | Release announced | ☐ | |
| F-05 | For major releases: old version archived in `spec/archive/` | ☐ | N/A for patch/minor |
| F-06 | For major releases: transition period start date announced | ☐ | N/A for patch/minor |
| F-07 | Certification registry updated to note the new protocol version is available for certification | ☐ | |

---

## Sign-Off

**Release manager:** ___________________________  
**Date all items completed:** ___________________________  
**Final release published:** ___________________________  

---

*See `docs/RELEASE_PROCESS.md` for the full release process description and stage requirements.*
