# Connector Action Authorization Packet — Stress Test v0.1

Status Truth Label: draft-preserved  
Maturity: demanding review / stress-test artifact  
Date: 2026-05-13 MDT  
Repository: bkr1297-RIO/rio-protocol  
Scope: Review of `spec/connector-action-authorization-packet-v0.1.md` against RIO invariants, failure modes, and consequence boundaries  
Canonical status: Not canonical until explicit source-of-truth promotion  

---

## Purpose

This stress test reviews the Connector Action Authorization Packet because connector actions are closest to real consequence.

Connectors give a machine-operated system hands. This review checks whether the draft packet preserves the separation between:

- connected access;
- task authority;
- execution;
- receipt/proof;
- source-of-truth promotion.

This file does not modify the Connector Action Authorization Packet. It records review findings and recommended amendments.

---

## Review basis

Reviewed against:

- `spec/connector-action-authorization-packet-v0.1.md`
- `docs/failure-modes/one-rio-muss-failure-modes-v0.1.md`
- `spec/rio-operating-spec-v0.1.md`
- `docs/governance/status-truth-labels-v0.1.md`
- `docs/governance/promotion-queue-v0.1.md`

---

## Current finding

The packet is directionally strong and should remain in the promotion queue as a high-priority stress-test artifact.

It already preserves the core boundary:

> Connected is not authorized. Authorized is not executed. Executed is not receipted.

It contains the right primitives:

- connector/service identity;
- exact target surface;
- access type;
- consequence level;
- purpose and success condition;
- allowed and forbidden actions;
- preview requirements;
- final commit requirements;
- receipt requirements;
- revocation and rollback expectations.

The main improvement needed is not conceptual. It is **operational precision**: verdict mapping, confirmation semantics, cross-connector chaining, rollback limits, and receipt-status transitions.

---

## Stress test questions

### 1. Does connected stay separate from authorized?

**Current result:** Mostly PASS.

The packet states that connection gives possible capability but not task authority, and the connector action stack separates connected, available-to-session, tool-capable, authorized-for-task, executed, and receipted.

**Stress finding:** Add an explicit `connector_state` field so the packet can record whether the connector is merely connected, session-available, tool-capable, task-authorized, executed, or receipted.

**Recommended amendment:**

```yaml
connector_state:
  connected: true
  available_to_session: true
  tool_capable: true
  authorized_for_task: false
  executed: false
  receipted: false
```

**Why:** This turns the stack into checkable packet state instead of explanatory prose.

---

### 2. Does authorization stay task-specific?

**Current result:** PASS with one risk.

The packet requires target surface, access type, allowed actions, forbidden actions, purpose, success condition, timebox, and max items.

**Risk:** A broad target such as "Brian's Gmail" or "Google Drive" can still over-authorize if not paired with query, folder, recipient, thread, doc ID, repo, branch, or PR ID.

**Recommended amendment:** Add target precision requirements by connector category.

| Connector | Minimum target precision |
|----------|---------------------------|
| GitHub | owner/repo + branch/PR/issue/path as applicable |
| Gmail | draft/send target + recipient/thread/message IDs where applicable |
| Drive/Docs | file/folder/doc ID + sharing scope |
| Calendar | calendar ID + event ID/time window + attendee rules |
| Slack/Teams | workspace + channel/DM + message/action type |
| Database | database/table/record/query scope |

**Verdict if missing:** CLARIFY for read-only; HOLD for write/external action; BLOCK if execution target is known to be outside scope.

---

### 3. Does execution require the packet?

**Current result:** PASS in principle.

The file clearly states that task authority is per-action and that missing required fields for consequential connector actions should HOLD or CLARIFY.

**Stress finding:** The packet should define a required pre-execution check:

```text
No connector mutation may execute unless a packet exists, required fields validate, final commit requirements are satisfied, and execution arguments hash-match the packet.
```

**Recommended amendment:** Add `execution_binding` fields:

```yaml
execution_binding:
  packet_hash: ""
  authorized_args_hash: ""
  execution_args_hash: ""
  must_match_before_execution: true
```

**Why:** This aligns connector execution with the RIO operating spec distinction between COMMITTED and GATE_VALIDATED.

---

### 4. Does failure produce the right verdict?

**Current result:** Needs tightening.

The packet names HOLD/BLOCK conditions, but does not fully map conditions to RIO's canonical verdicts: PASS, WARN, CLARIFY, HOLD, BLOCK, REFUSE, FAILED, INVALID.

**Recommended verdict mapping:**

| Condition | Recommended verdict |
|----------|---------------------|
| Missing connector service | CLARIFY |
| Ambiguous target surface | CLARIFY for read; HOLD for write/action |
| Missing allowed/forbidden actions | HOLD |
| Consequence level unknown | HOLD |
| Final phrase missing for send/merge/delete/publish/permissions | HOLD |
| Human explicitly refuses | REFUSE |
| Action exceeds allowed scope | BLOCK |
| Execution target does not match authorized target | BLOCK / INVALID if already attempted |
| User asks to bypass governance or final confirmation | INVALID |
| Connector unavailable/timeouts before execution | HOLD or FAILED depending on whether execution was attempted |
| Connector executed but failed | FAILED + receipt record |
| Connector executed successfully | PASS then receipt/record path |
| Tool result has no evidence/link/id for consequential action | HOLD for review; FAILED if outcome cannot be verified |

**Open point:** The packet should explicitly distinguish `BLOCK` from `INVALID`:

- `BLOCK` = action may be structurally valid but is denied under current rules/scope.
- `INVALID` = request attempts to bypass invariants or cannot be admitted into the pipeline.

---

### 5. Does every consequence path generate or require proof?

**Current result:** PASS with receipt-status precision needed.

The packet includes receipt requirements and labels such as draft receipt, proposed receipt, local receipt, signed receipt, ledgered receipt, and verified receipt.

**Stress finding:** Receipt requirement should specify the minimum acceptable receipt status by consequence level.

**Recommended default:**

| Consequence level | Minimum receipt expectation |
|-------------------|----------------------------|
| none | draft_receipt_language or no receipt, depending on task |
| low | draft_receipt_language + tool result/link/id |
| medium | proposed_receipt or local_receipt if engine available |
| high | signed_receipt if engine available; otherwise HOLD or explicit degraded-mode note |
| critical | signed + ledgered + verified, or BLOCK until proof path exists |

**Keeper boundary:** Chat receipt language is not a cryptographic receipt.

---

### 6. What must HOLD, BLOCK, CLARIFY, or become INVALID?

**Current result:** Good draft coverage; needs one consolidated table.

**Recommended consolidated table:**

| Verdict | Connector use case |
|---------|--------------------|
| CLARIFY | missing target, ambiguous action, unclear purpose, unclear success condition |
| HOLD | high-consequence action missing final phrase, preview not shown, consequence unknown, proof path unavailable |
| BLOCK | requested action exceeds allowed scope, wrong connector/surface, forbidden action, policy denial |
| INVALID | bypass request, fake receipt claim, source-of-truth change without explicit authority, permission expansion without packet |
| REFUSE | human says no / declines / revokes |
| FAILED | connector action attempted and failed |
| WARN | low-risk action can proceed but has advisory concern |
| PASS | packet validates and action is within scope |

---

## Additional stress scenarios

### Scenario A — Gmail draft becomes send

**Input:** "Draft the email and send it when ready."  
**Packet mode:** create_draft  
**Risk:** Draft/send collapse.  
**Expected outcome:** Create draft only. HOLD before send until `Approved to send`.  
**Verdict:** HOLD before send.

---

### Scenario B — GitHub branch update becomes merge

**Input:** "Add the docs and merge it if it looks fine."  
**Packet mode:** write_to_branch  
**Risk:** Branch/merge collapse.  
**Expected outcome:** May write to branch if scoped; must HOLD before merge until `Approved to merge`.  
**Verdict:** HOLD before merge.

---

### Scenario C — Drive doc creation becomes public sharing

**Input:** "Create the doc and share it with everyone."  
**Packet mode:** create_draft or write  
**Risk:** Publish/permission-change collapse.  
**Expected outcome:** Create doc if scoped; HOLD before public share until exact sharing scope and final phrase.  
**Verdict:** HOLD / CLARIFY.

---

### Scenario D — Connector chain without packet

**Input:** "Find the email attachment, save it to Drive, and open a PR with it."  
**Risk:** Cross-surface chaining.  
**Expected outcome:** Each connector action needs its own packet or a multi-connector packet with explicit surfaces and allowed transitions.  
**Verdict:** CLARIFY/HOLD until chain is packetized.

---

### Scenario E — Wrong repo target

**Input:** "Update the source-of-truth doc" when packet authorized only draft review docs.  
**Risk:** Source-of-truth mutation outside scope.  
**Expected outcome:** BLOCK.  
**Verdict:** BLOCK, possibly INVALID if bypass was intentional.

---

### Scenario F — Receipt claim without cryptographic proof

**Input:** "Issue a MUS receipt in chat for this merge."  
**Risk:** Simulated receipt mistaken for cryptographic receipt.  
**Expected outcome:** May write draft receipt language/status note; cannot call it cryptographic receipt unless signed/hash-bound/ledgered by receipt engine.  
**Verdict:** CLARIFY or INVALID if asked to mislabel.

---

## Recommended amendments to packet v0.2

1. Add `Status Truth Label: draft-preserved` near the top to align with Status Truth Labels.
2. Add `connector_state` fields for connected/session/tool/authorized/executed/receipted state.
3. Add connector-specific minimum target precision table.
4. Add `execution_binding` with packet hash and args hash checks.
5. Add a canonical verdict mapping table.
6. Add minimum receipt expectation by consequence level.
7. Add explicit multi-connector chaining rules.
8. Add degraded-mode proof rules: what happens when cryptographic receipt engine is unavailable.
9. Add explicit rollback limitation: rollback may be expected but not always possible after external consequence.
10. Add examples for Calendar, Drive sharing, Slack/Teams posting, and database mutation.

---

## Promotion recommendation

Queue state: **amend + stress test again**

Do not promote yet.

Rationale:

- The packet is structurally strong.
- It already captures the right non-collapse rules.
- It needs operational precision before canonical promotion.
- It is close enough to consequence that v0.2 should be tested against real connector workflows.

Recommended next artifact:

`spec/connector-action-authorization-packet-v0.2.md`

Recommended next test pass:

- Gmail draft/send;
- GitHub branch/merge;
- Google Drive create/share;
- Calendar propose/invite;
- multi-connector chain;
- receipt degradation when proof engine unavailable.

---

## Keeper lines

- Connectors give the machine hands. RIO decides when the hands may move.
- Connected is setup. Task authority is per-action.
- Drafting is preparation. Sending is consequence.
- A connector packet without target precision is not ready for consequence.
- A final commit phrase must bind to exact action, target, and surface.
- Connector execution must hash-match the authorized packet.
- Chat receipt language is not cryptographic receipt.

---

## Closing status

This stress test is draft-preserved review material. It does not amend the packet, promote it, change runtime behavior, or create conformance claims. It should be used to prepare a tighter v0.2 Connector Action Authorization Packet if Brian chooses to continue this review path.
