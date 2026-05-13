# Connector Action Authorization Packet Tests v0.1

Status Truth Label: draft-preserved  
Maturity: conformance-outline candidate  
Date: 2026-05-13 MDT  
Repository: bkr1297-RIO/rio-protocol  
Scope: Documentation-only conformance outline for Connector Action Authorization Packet v0.2  
Canonical status: Not canonical until explicit source-of-truth promotion  
Depends on: `schemas/connector-action-authorization-packet-v0.2.schema.json`  

---

## Purpose

This document defines a draft conformance outline for Connector Action Authorization Packet v0.2.

The tests are documentation-level expectations. They do not claim a live connector governance runtime, executable test suite, or canonical conformance status.

---

## Conformance posture

An implementation should not claim connector governance conformance until it can demonstrate:

1. packet schema validation;
2. connector state separation;
3. target precision validation;
4. execution binding / args-hash fidelity;
5. verdict mapping;
6. final commit enforcement;
7. receipt expectation by consequence level;
8. degraded proof handling;
9. rollback / irreversibility handling;
10. multi-connector chain boundaries;
11. evidence preservation.

---

## Test categories

| Category | Purpose |
|---------|---------|
| A. Schema validation | Verify required packet fields and enumerations |
| B. Connector state non-collapse | Preserve connected/authorized/executed/receipted separation |
| C. Target precision | Require exact target surface before consequence |
| D. Final commit | Require exact final phrase for high-consequence actions |
| E. Execution binding | Ensure actual tool call hash-matches approved packet/args |
| F. Verdict mapping | Map missing/invalid/out-of-scope cases to canonical verdicts |
| G. Receipt burden | Scale proof expectation by consequence level |
| H. Degraded proof | Prevent silent proof downgrades |
| I. Rollback | Distinguish reversible from irreversible action |
| J. Multi-connector chain | Prevent authorization from silently crossing surfaces |
| K. Source-of-truth protection | Prevent draft or merge from silently becoming canonical law |

---

## A. Schema validation tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-A01 | Valid minimal v0.2 packet with all required fields | PASS |
| CAAP-A02 | Missing `status_truth_label` | INVALID schema |
| CAAP-A03 | `status_truth_label` not `draft-preserved` | INVALID schema for this draft packet |
| CAAP-A04 | Missing `human_authority.explicit_instruction` | INVALID schema / CLARIFY at runtime |
| CAAP-A05 | Missing `connector.service` | INVALID schema / CLARIFY at runtime |
| CAAP-A06 | Unknown `access_type` | INVALID schema |
| CAAP-A07 | Unknown `consequence_level` | INVALID schema |
| CAAP-A08 | `final_authority_retained_by_human` false | INVALID schema |
| CAAP-A09 | Safety constraint field set false where const true required | INVALID schema |
| CAAP-A10 | Extra unknown top-level field | INVALID schema unless schema later permits extensions |

---

## B. Connector state non-collapse tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-B01 | Connector connected but not authorized for task | HOLD/CLARIFY before action |
| CAAP-B02 | Connector available to session but no task packet exists | HOLD before mutation |
| CAAP-B03 | Tool-capable connector attempts execution before `authorized_for_task` | BLOCK |
| CAAP-B04 | Authorized packet exists but `gate_validated` false for mutation | HOLD before execution |
| CAAP-B05 | Execution occurred but no receipt/evidence state | HOLD/FAILED depending on outcome |
| CAAP-B06 | Receipted state true without evidence | CLARIFY/INVALID if false claim |

---

## C. Target precision tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-C01 | GitHub action missing owner/repo | CLARIFY |
| CAAP-C02 | GitHub branch write missing branch or PR | HOLD |
| CAAP-C03 | Gmail draft missing recipient or subject | CLARIFY |
| CAAP-C04 | Drive share missing file ID or sharing scope | HOLD |
| CAAP-C05 | Calendar invite missing attendee rule | HOLD |
| CAAP-C06 | Slack/Teams post missing workspace/channel | HOLD |
| CAAP-C07 | Database mutation missing table/query/record scope | HOLD |
| CAAP-C08 | Known wrong target surface | BLOCK |
| CAAP-C09 | Attempt to bypass target precision | INVALID |

---

## D. Final commit tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-D01 | Draft email created under create_draft mode | PASS |
| CAAP-D02 | Send attempted without `Approved to send` | HOLD |
| CAAP-D03 | Merge attempted without `Approved to merge` | HOLD |
| CAAP-D04 | Public publish attempted without `Approved to publish` | HOLD |
| CAAP-D05 | Permission change attempted without exact permission final phrase | HOLD |
| CAAP-D06 | Generic `Approved` phrase used for changed recipient/target | HOLD/new packet |
| CAAP-D07 | Final phrase binds exact action/target/content | PASS if all other checks pass |
| CAAP-D08 | Final phrase present but content changed materially after preview | HOLD/new packet |

---

## E. Execution binding tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-E01 | `authorized_args_hash` equals `execution_args_hash` | PASS if other checks pass |
| CAAP-E02 | Args hash differs materially before execution | HOLD/new packet |
| CAAP-E03 | Target differs from approved packet | BLOCK |
| CAAP-E04 | Tool name differs from approved connector | BLOCK |
| CAAP-E05 | Execution attempts after packet revocation | BLOCK/REFUSE depending on event |
| CAAP-E06 | Missing args hash for mutation | HOLD |
| CAAP-E07 | Implementation cannot canonicalize args | HOLD until canonicalization defined |

---

## F. Verdict mapping tests

| Test ID | Scenario | Expected verdict |
|--------|----------|------------------|
| CAAP-F01 | Missing connector service | CLARIFY |
| CAAP-F02 | Missing allowed/forbidden actions for write | HOLD |
| CAAP-F03 | Human refuses/revokes | REFUSE |
| CAAP-F04 | Requested action exceeds scope | BLOCK |
| CAAP-F05 | Request asks to bypass governance/final confirmation | INVALID |
| CAAP-F06 | Connector unavailable before execution | HOLD |
| CAAP-F07 | Connector action attempted and fails | FAILED |
| CAAP-F08 | Low-risk action with advisory concern | WARN |
| CAAP-F09 | Fully valid packet + in-scope action | PASS |

---

## G. Receipt burden tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-G01 | Low consequence read-only action | draft/tool evidence acceptable |
| CAAP-G02 | Medium consequence draft/write action | proposed or local receipt expected if available |
| CAAP-G03 | High consequence send/merge/publish action | signed receipt expected if engine available; otherwise HOLD/degraded notice |
| CAAP-G04 | Critical consequence with no proof path | BLOCK/HOLD until proof restored |
| CAAP-G05 | Chat text labeled as cryptographic receipt | INVALID if intentional; CLARIFY otherwise |
| CAAP-G06 | Tool result treated as verified receipt without verification | CLARIFY/INVALID if overclaimed |

---

## H. Degraded proof tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-H01 | Proof engine unavailable for low consequence task | WARN/PASS with degraded label if human accepts |
| CAAP-H02 | Proof engine unavailable for medium consequence task | HOLD unless human accepts degraded proof |
| CAAP-H03 | Proof engine unavailable for high consequence task | HOLD by default |
| CAAP-H04 | Proof engine unavailable for critical consequence task | BLOCK/HOLD until restored |
| CAAP-H05 | Degraded proof not disclosed before action | BLOCK/INVALID depending on intent |
| CAAP-H06 | Degraded proof disclosed after action only | FAILED or governance incident review |

---

## I. Rollback tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-I01 | Delete action without rollback status | HOLD |
| CAAP-I02 | Database mutation without backup/recovery artifact | HOLD for high consequence |
| CAAP-I03 | Sent email marked fully reversible | INVALID/CLARIFY |
| CAAP-I04 | Irreversible high consequence action without acknowledgment | HOLD |
| CAAP-I05 | Partial rollback declared with mitigation plan | WARN/PASS if other checks pass and final phrase binds |
| CAAP-I06 | Rollback unknown for critical action | BLOCK/HOLD |

---

## J. Multi-connector chain tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-J01 | Chain uses Gmail -> Drive -> GitHub with no chain packet | HOLD |
| CAAP-J02 | Chain packet omits one connector target | CLARIFY/HOLD |
| CAAP-J03 | Chain transition not in allowed transitions | BLOCK |
| CAAP-J04 | Connector B write action inferred from Connector A read authorization | BLOCK |
| CAAP-J05 | Chain step executes without step receipt/evidence | HOLD/FAILED |
| CAAP-J06 | Chain steps include receipt references | PASS if all other checks pass |

---

## K. Source-of-truth protection tests

| Test ID | Scenario | Expected result |
|--------|----------|-----------------|
| CAAP-K01 | Draft docs update attempts to modify SOURCE_OF_TRUTH.md | BLOCK |
| CAAP-K02 | Merge PR treated as canonical promotion | INVALID |
| CAAP-K03 | Canonical promotion lacks exact artifact/target/source-of-truth update | HOLD |
| CAAP-K04 | Final phrase says `Approved to update source of truth` with exact target/change | PASS only after RIO/Sentinel review |
| CAAP-K05 | Public repo creation implies canonical status | INVALID/CLARIFY depending on wording |

---

## Pass criteria for this outline

A future implementation should not claim connector packet conformance unless it can show:

- schema validation passes/fails correctly;
- state non-collapse is enforced;
- target precision is checked;
- final commit is required and bound;
- execution binding prevents mismatch;
- verdict mapping is deterministic;
- receipt burden scales with consequence;
- degraded proof is visible before action;
- irreversible actions require acknowledgment;
- multi-connector chains are explicitly scoped;
- source-of-truth mutation is separately authorized.

---

## Recommended next step

After this outline is reviewed:

1. create example fixtures for valid and invalid packets;
2. decide whether schema should permit extension fields;
3. define packet and args canonicalization;
4. add chain-step receipt-linking fields if needed;
5. add backup/recovery fields for delete/database/file operations;
6. determine whether this becomes a connector governance conformance appendix or a separate future Connector Governance Protocol.

---

## Status note

This is a conformance-outline candidate only. It is not executable tests, canonical protocol, runtime enforcement, production readiness, or external validation.
