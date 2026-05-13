# Connector Action Authorization Packet v0.2 — Stress Test v0.1

Status Truth Label: draft-preserved  
Maturity: demanding review / stress-test artifact  
Date: 2026-05-13 MDT  
Repository: bkr1297-RIO/rio-protocol  
Scope: Review of `spec/connector-action-authorization-packet-v0.2.md` against concrete connector workflows, proof degradation, chain behavior, and RIO verdict mapping  
Canonical status: Not canonical until explicit source-of-truth promotion  

---

## Purpose

This stress test reviews Connector Action Authorization Packet v0.2 after the v0.1 stress test and v0.2 amendment.

The goal is to determine whether v0.2 is ready to move toward a schema/conformance candidate or still needs another amendment pass before promotion consideration.

This file does not amend v0.2. It preserves review findings only.

---

## Review basis

Reviewed against:

- `spec/connector-action-authorization-packet-v0.2.md`
- `docs/reviews/connector-action-authorization-packet-stress-test-v0.1.md`
- `spec/rio-operating-spec-v0.1.md`
- `docs/failure-modes/one-rio-muss-failure-modes-v0.1.md`
- `docs/governance/status-truth-labels-v0.1.md`
- `docs/governance/promotion-queue-v0.1.md`

---

## Current finding

Connector Action Authorization Packet v0.2 passes the first demanding documentation-level stress test.

It successfully closes the major v0.1 gaps:

| v0.1 gap | v0.2 result |
|---------|-------------|
| No explicit status truth label | Added |
| No connector-state fields | Added |
| No connector-specific target precision table | Added |
| No execution binding / args-hash requirement | Added |
| Incomplete verdict mapping | Added canonical verdict mapping |
| No receipt minimums by consequence level | Added |
| No multi-connector chaining rules | Added |
| No degraded proof behavior | Added |
| No rollback limitation rules | Added |
| Limited examples | Added GitHub, Gmail, Drive, Calendar, Slack/Teams, Database examples |

The remaining work is not more concept naming. It is formalization and testability.

Recommended queue state:

```text
schema candidate + workflow stress test
```

Do not promote to canonical yet.

---

## Stress scenarios

### Scenario 1 — GitHub branch update vs merge

**Task:** Update markdown files on a branch/PR; do not merge.  
**Risk:** Branch update becomes source change / merge / source-of-truth change.  
**v0.2 controls:** target precision, access type, forbidden actions, final commit rule, source-of-truth final phrase, execution binding.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Owner/repo/branch/PR missing | CLARIFY/HOLD |
| Allowed branch update only | PASS after packet validates |
| Merge attempted without final phrase | HOLD |
| SOURCE_OF_TRUTH change outside packet | BLOCK |
| Attempt to bypass final merge confirmation | INVALID |

**Result:** PASS.

**Reason:** v0.2 explicitly separates `write_to_branch` from `merge`, requires target precision, and requires exact final commit for merge/source-of-truth changes.

---

### Scenario 2 — Gmail draft vs send

**Task:** Create a draft email; do not send.  
**Risk:** Draft/send collapse.  
**v0.2 controls:** access type, forbidden actions, final commit phrase, target precision, rollback limits.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Recipient/subject missing | CLARIFY |
| Draft-only packet validates | PASS for draft creation |
| Send requested without `Approved to send` | HOLD |
| Recipient changes after approval | HOLD/new packet |
| Send occurs but connector fails | FAILED + receipt record |

**Result:** PASS.

**Reason:** v0.2 clearly treats drafting as preparation and sending as consequence.

---

### Scenario 3 — Google Drive create vs share/publish

**Task:** Create a private document; do not share publicly.  
**Risk:** Create/share/publish/permission-change collapse.  
**v0.2 controls:** target precision, sharing scope, permission-change final commit, public publish final commit, rollback limits.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Folder or document scope missing | CLARIFY/HOLD |
| Private doc creation in scope | PASS |
| Public sharing requested without exact scope | HOLD/CLARIFY |
| Public publish attempted without final phrase | HOLD/BLOCK |
| Permission target differs from approved target | BLOCK |

**Result:** PASS.

**Reason:** v0.2 names sharing/publication as separate consequential actions requiring specific confirmation.

---

### Scenario 4 — Calendar propose vs invite attendees

**Task:** Propose an event window; do not invite attendees.  
**Risk:** Proposal/invite collapse; third parties contacted without final approval.  
**v0.2 controls:** calendar target precision, attendee rules, `invite_attendees` final commit.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Time window missing | CLARIFY |
| Attendee rule missing | HOLD for external invite |
| Proposed event details only | PASS |
| Invite attendees without final phrase | HOLD |
| Changed attendee list after final phrase | HOLD/new packet |

**Result:** PASS.

**Reason:** v0.2 correctly treats attendee invitation as external consequence.

---

### Scenario 5 — Slack/Teams draft vs post

**Task:** Draft a Slack/Teams message; do not post.  
**Risk:** Draft/post/tag collapse; accidental public/internal distribution.  
**v0.2 controls:** workspace/channel/DM precision, post/edit/delete action type, final commit.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Workspace/channel ambiguous | CLARIFY/HOLD |
| Draft only | PASS |
| Post without final phrase | HOLD |
| Tag users/channels without approval | HOLD/BLOCK |
| Edit/delete existing message outside scope | BLOCK |

**Result:** PASS.

**Reason:** v0.2 covers draft-only messaging and posting as separate actions.

---

### Scenario 6 — Database read vs mutation

**Task:** Read scoped database records; do not mutate.  
**Risk:** Read/write/schema/export collapse.  
**v0.2 controls:** database/table/query scope, mutation final phrase, forbidden actions, receipt expectations.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Database/table/query scope missing | CLARIFY/HOLD |
| Read-only query in scope | PASS |
| Mutation without final phrase | HOLD |
| Schema change requested | HOLD/BLOCK depending on scope |
| Export beyond approved scope | BLOCK |

**Result:** PASS with note.

**Note:** Database mutation should eventually require transaction/backup/rollback fields if this moves closer to runtime conformance.

---

### Scenario 7 — Multi-connector chain

**Task:** Read Gmail attachment -> save to Drive -> open GitHub PR.  
**Risk:** Authorization on one connector silently expands to another connector.  
**v0.2 controls:** multi-connector chain section, allowed transitions, each step requires packet or chain scope.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Chain not declared | HOLD |
| Connector B target missing | CLARIFY/HOLD |
| Transition not allowed | BLOCK |
| External send/publish step appears | HOLD/final phrase required |
| Each step scoped and proof expectations set | PASS step-by-step |

**Result:** PASS with amendment candidate.

**Amendment candidate:** Add a `chain_step_id` and `previous_step_receipt_ref` field in future v0.3 or schema version so each step can be receipt-linked.

---

### Scenario 8 — Degraded proof mode

**Task:** Execute medium/high connector action when receipt engine is unavailable.  
**Risk:** Proof silently downgrades; chat/status note is treated as cryptographic receipt.  
**v0.2 controls:** degraded proof behavior, receipt expectation by consequence level, explicit notice, human decision, no false receipt claim.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Low consequence, human accepts draft proof | WARN/PASS with degraded label |
| Medium consequence, proof unavailable | HOLD unless human accepts degraded proof |
| High consequence, proof unavailable | HOLD by default |
| Critical consequence, proof unavailable | BLOCK/HOLD until proof restored |
| User asks to label degraded proof as verified | INVALID |

**Result:** PASS.

**Reason:** v0.2 preserves proof-status truth and prevents silent proof downgrade.

---

### Scenario 9 — Rollback and irreversibility

**Task:** Delete file, send email, merge PR, invite attendee, publish publicly, or mutate database.  
**Risk:** System assumes rollback is possible when it is not.  
**v0.2 controls:** rollback status table, irreversibility acknowledgment, final confirmation.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Rollback unknown on high consequence | HOLD |
| Rollback not possible and final phrase lacks acknowledgment | HOLD |
| Irreversibility acknowledged and action otherwise valid | PASS after RIO/Sentinel checks |
| Rollback falsely claimed as full | INVALID if intentional; CLARIFY if uncertain |

**Result:** PASS with amendment candidate.

**Amendment candidate:** Add `backup_or_recovery_artifact` field for delete/database/file operations.

---

### Scenario 10 — Source-of-truth mutation

**Task:** Modify `SOURCE_OF_TRUTH.md` or promote a draft artifact to canonical.  
**Risk:** Draft promotion becomes hidden source-of-truth change.  
**v0.2 controls:** source-of-truth change final commit, exact target/action/material binding, forbidden actions, final phrase.  
**Expected verdicts:**

| Condition | Verdict |
|----------|---------|
| Source-of-truth update not explicitly authorized | BLOCK |
| Human says “approve” but not exact source-of-truth target/change | HOLD |
| Exact final phrase + target + content + source-of-truth relation present | PASS only after RIO/Sentinel check |
| Attempt to treat merge as source-of-truth promotion | INVALID |

**Result:** PASS.

**Reason:** v0.2 aligns with Promotion Queue rule that promotion requires explicit source-of-truth action.

---

## Cross-scenario findings

### Strengths

1. v0.2 preserves connector state separation.
2. v0.2 introduces target precision as a precondition for consequence.
3. v0.2 binds execution to packet/args hashes.
4. v0.2 maps failure states to canonical verdicts.
5. v0.2 scales receipt burden by consequence level.
6. v0.2 prevents silent multi-connector expansion.
7. v0.2 handles degraded proof without overclaiming.
8. v0.2 acknowledges rollback limitations.
9. v0.2 adds enough examples to make the packet reviewable by connector class.

### Remaining gaps

These are not blockers for draft preservation, but they block canonical promotion:

1. No JSON Schema yet.
2. No conformance tests yet.
3. No live runtime enforcement claim.
4. No formal connector registry.
5. No exact hash canonicalization rules for packet/arguments.
6. No chain-step receipt-linking fields.
7. No backup/recovery artifact field for high-risk delete/database/file operations.
8. No connector-specific policy packs yet.
9. No source-of-truth promotion procedure integrated into canonical RIO docs.

---

## Recommended queue state

```text
promote candidate after schema + conformance outline
```

Do not promote now.

Rationale:

- v0.2 passes documentation-level workflow stress testing.
- v0.2 is materially stronger than v0.1.
- v0.2 is close enough to become a schema/conformance candidate.
- It still lacks machine-checkable schema, canonicalization rules, conformance tests, and runtime enforcement evidence.

---

## Recommended next artifacts

1. `schemas/connector-action-authorization-packet-v0.2.schema.json`  
   Machine-checkable schema for v0.2 packet fields.

2. `tests/connector-action-authorization-packet-tests-v0.1.md`  
   Conformance-style test outline for connector actions.

3. `docs/architecture/connector-governance-protocol-roadmap-v0.1.md`  
   Boundary note: packet vs full protocol vs connector policy packs vs runtime implementation.

4. `docs/reviews/connector-action-authorization-packet-v0.2-red-team-v0.1.md`  
   Adversarial review pass focused on bypass, ambiguous instruction, and connector-chaining attempts.

---

## Possible v0.3 amendments

If a v0.3 draft is created later, consider adding:

```yaml
chain_step:
  chain_step_id: ""
  previous_step_receipt_ref: ""
  next_allowed_step_ids: []

recovery:
  backup_or_recovery_artifact: ""
  recovery_verified: false

canonicalization:
  packet_canonicalization_method: ""
  args_canonicalization_method: ""
  hash_algorithm: "SHA-256"
```

These are not required for v0.2 review preservation but may be needed for runtime conformance.

---

## Keeper lines

- v0.2 passes documentation-level stress testing, not runtime conformance.
- Target precision is the difference between tool availability and governed action.
- Execution binding is the bridge from connector packet to Sentinel fidelity.
- Degraded proof must be named before action, not explained after action.
- Cross-surface movement is consequence.
- No connector chain should outrun its receipts.

---

## Closing status

This stress test is draft-preserved review material. It does not promote v0.2, change runtime behavior, create schemas, authorize connector use, or claim live connector governance.

It supports a next step toward schema and conformance outline work if Brian chooses to continue this promotion path.
