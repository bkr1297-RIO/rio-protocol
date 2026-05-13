# Connector Action Authorization Packet v0.2

Status Truth Label: draft-preserved  
Maturity: draft spec amendment after v0.1 stress test  
Date: 2026-05-13 MDT  
Scope: Documentation/spec only  
Canonical status: Not canonical until explicit source-of-truth promotion  
Repository: bkr1297-RIO/rio-protocol  
Supersedes: none — preserves v0.1 and creates a reviewable v0.2 draft beside it  
Derived from: `spec/connector-action-authorization-packet-v0.1.md` + `docs/reviews/connector-action-authorization-packet-stress-test-v0.1.md`

---

## Purpose

The **Connector Action Authorization Packet** is the explicit human permission object that converts connected tool capability into bounded, task-specific authority.

It governs how a machine-operated system may use connected services such as GitHub, Google Drive, Gmail, Notion, Linear, Outlook, Slack, calendars, databases, or other external surfaces.

Connecting a service gives possible capability. It does not grant task authority.

This v0.2 draft hardens v0.1 by adding:

- status truth label discipline;
- connector-state fields;
- connector-specific target precision requirements;
- execution binding and argument-hash checks;
- canonical RIO verdict mapping;
- minimum receipt expectations by consequence level;
- multi-connector chaining rules;
- degraded proof behavior;
- rollback limits;
- additional examples for common connector classes.

---

## One-line definition

A Connector Action Authorization Packet is a human-authored authorization object that names the connector, target surface, exact action, forbidden actions, consequence level, preview requirement, final confirmation requirement, execution-binding requirements, and receipt expectation for a single connector task or explicitly scoped connector chain.

---

## Keeper lines

> Connected is not authorized. Authorized is not executed. Executed is not receipted.

> Connectors give the machine hands. RIO decides when the hands may move.

> Drafting is preparation. Sending is consequence.

> A connector packet without target precision is not ready for consequence.

> Connector execution must hash-match the authorized packet.

> Chat receipt language is not cryptographic receipt.

---

## Non-collapse rule

A connector workflow must not collapse these states:

```text
connected
-> available_to_session
-> tool_capable
-> authorized_for_task
-> gate_validated
-> executed
-> receipted
-> verified
```

Each state must be separately checkable where consequence is possible.

---

## Connector action stack

| Layer | Meaning |
|------|---------|
| Connected | The human has signed in or authorized the service at the account level |
| Available to session | The current model/session can see or call the connector |
| Tool-capable | The connector exposes actions such as read, draft, write, send, delete, merge, create |
| Authorized for task | The human has explicitly permitted a specific connector action in scope |
| Gate validated | The exact tool call / mutation still matches the approved packet at execution time |
| Executed | The tool actually ran and returned evidence |
| Receipted | The action has a record/proof trail under the applicable receipt standard |
| Verified | The receipt or tool evidence has been independently checked under a defined verification process |

Operational form:

> Connected access is setup. Task authority is per-action. Execution requires packet fidelity.

---

## Packet template

```yaml
connector_action_authorization_packet:
  version: "0.2"
  status_truth_label: "draft-preserved"

  human_authority:
    authorized_by: ""
    timestamp: ""
    explicit_instruction: ""
    final_authority_retained_by_human: true

  connector_state:
    connected: false
    available_to_session: false
    tool_capable: false
    authorized_for_task: false
    gate_validated: false
    executed: false
    receipted: false
    verified: false

  connector:
    service: "GitHub | Google Drive | Gmail | Notion | Linear | Outlook | Slack | Teams | Calendar | Database | Other"
    account_or_workspace: ""
    surface: ""
    target_url_or_id: ""
    target_precision: ""

  mode:
    access_type: "read_only | draft_only | write_to_branch | create_draft | send | delete | merge | create_repo | publish | permission_change | invite_attendees | database_mutation | multi_connector_chain"
    consequence_level: "none | low | medium | high | critical"

  purpose:
    goal: ""
    reason: ""
    success_condition: ""

  scope:
    allowed_actions: []
    forbidden_actions: []
    allowed_targets: []
    forbidden_targets: []
    max_items: ""
    timebox: ""

  target_precision_requirement:
    connector_type: ""
    required_identifiers: []
    provided_identifiers: []
    precision_status: "complete | incomplete | ambiguous"

  constraints:
    no_external_send_without_final_confirm: true
    no_delete_without_final_confirm: true
    no_merge_without_final_confirm: true
    no_public_publish_without_final_confirm: true
    no_permission_change_without_final_confirm: true
    no_attendee_invite_without_final_confirm: true
    no_database_mutation_without_final_confirm: true
    no_cross_connector_action_without_chain_packet: true

  preview_requirement:
    required_before_write: true
    required_before_external_consequence: true
    human_must_review: true
    preview_artifact_or_link: ""

  execution_binding:
    packet_hash: ""
    authorized_args_hash: ""
    execution_args_hash: ""
    committed_packet_ref: ""
    must_match_before_execution: true
    material_change_requires_new_packet: true

  verdict_mapping:
    missing_required_field: "CLARIFY | HOLD"
    outside_scope: "BLOCK"
    invariant_bypass: "INVALID"
    human_refusal: "REFUSE"
    connector_failure_after_attempt: "FAILED"

  receipt_requirement:
    minimum_receipt_status: "none | draft_receipt_language | proposed_receipt | local_receipt | signed_receipt | ledgered_receipt | verified_receipt"
    cryptographic_receipt_required_if_available: false
    degraded_mode_allowed: false
    degraded_mode_reason: ""
    record:
      - action_taken
      - connector_used
      - target
      - timestamp
      - result
      - link_or_id
      - limitations
      - packet_hash
      - authorized_args_hash
      - execution_args_hash

  multi_connector_chain:
    is_chain: false
    chain_id: ""
    connectors_involved: []
    allowed_transitions: []
    forbidden_transitions: []
    each_step_requires_packet_or_chain_scope: true

  revocation:
    stop_phrase: "hold"
    revocation_effect: "pause_future_actions | revoke_packet | revoke_chain"
    rollback_expected: false
    rollback_possible: "yes | no | partial | unknown"
    rollback_plan: ""
    irreversible_consequence_acknowledged: false

  final_commit:
    required_for:
      - send_email
      - send_message
      - merge_pr
      - create_repo
      - delete_file
      - delete_message
      - publish_publicly
      - modify_permissions
      - invite_attendees
      - database_mutation
      - spend_money
      - physical_world_action
      - source_of_truth_change
    human_final_phrase_required: "Approved to execute"
    final_phrase_must_bind_to_exact_action_target_and_surface: true
    final_phrase_timestamp: ""
```

---

## Required fields

A minimally valid packet must include:

1. status truth label;
2. human authority statement;
3. connector service;
4. account/workspace if applicable;
5. exact target surface or URL/ID;
6. access type;
7. consequence level;
8. purpose;
9. allowed actions;
10. forbidden actions;
11. target precision status;
12. preview requirement;
13. execution-binding requirement for mutations;
14. receipt requirement;
15. revocation condition;
16. final commit conditions.

If any required field is missing for a consequential connector action, the system should CLARIFY or HOLD.

If a required field is deliberately bypassed, the request should be INVALID.

---

## Connector-specific target precision

A packet is not ready for consequence unless the target is precise enough for the connector and action type.

| Connector | Minimum target precision |
|----------|---------------------------|
| GitHub | owner/repo plus branch, PR, issue, path, commit, or release target as applicable |
| Gmail / Outlook | draft/send target, recipient(s), subject, thread/message IDs where applicable, attachment scope if relevant |
| Google Drive / Docs / Sheets / Slides | file/folder/doc ID, tab/sheet/page range if applicable, sharing scope, export format if relevant |
| Calendar | calendar ID, event ID or exact proposed time window, attendee rules, recurrence scope |
| Slack / Teams | workspace, channel/DM, message/thread ID if applicable, post/edit/delete action type |
| Notion / Linear | workspace, page/database/project/issue ID, field/action scope |
| Database | database, schema, table, query/mutation scope, record IDs, write/read transaction boundary |
| Public web / publishing | URL/domain/account, public visibility scope, title/content artifact, publication target |
| Physical / robotic connector | device/unit ID, location, action envelope, safety boundary, human supervisor, emergency stop |
| Other | equivalent exact service, account, target, action, and consequence boundary |

Verdict if target precision is incomplete:

| Condition | Verdict |
|----------|---------|
| Read-only and low stakes | CLARIFY or WARN depending on ambiguity |
| Draft/write action | HOLD until target is precise |
| External consequence | HOLD until exact target and final phrase exist |
| Known wrong target | BLOCK |
| Attempt to bypass target precision | INVALID |

---

## Access-type semantics

| Access type | Meaning | Final confirmation required? |
|------------|---------|------------------------------|
| read_only | Search, fetch, inspect, summarize | Usually no, unless high-stakes/private scope requires it |
| draft_only | Prepare draft without external send/publish | No send/publish allowed |
| write_to_branch | Modify an existing branch/PR surface | Required before merge/publish/canonical promotion |
| create_draft | Create draft email/doc/page/event | Required before send/share/publish/invite |
| send | Send an email/message externally | Yes |
| delete | Delete file/message/data | Yes |
| merge | Merge PR or equivalent source-surface change | Yes |
| create_repo | Create new repository | Yes |
| publish | Make content public or externally visible | Yes |
| permission_change | Add users, change sharing, alter access | Yes |
| invite_attendees | Invite people to calendar/event/workspace | Yes |
| database_mutation | Insert, update, delete, or migrate records | Yes |
| multi_connector_chain | Use two or more connectors in one workflow | Yes for each consequential step |

---

## Execution binding

Connector execution must bind to the approved packet.

Required rule:

> No connector mutation may execute unless a packet exists, required fields validate, final commit requirements are satisfied, and execution arguments hash-match the packet.

The implementation should compute or preserve:

- `packet_hash` — hash of the approved packet;
- `authorized_args_hash` — hash of approved connector arguments;
- `execution_args_hash` — hash of actual connector arguments at execution time.

If `authorized_args_hash` and `execution_args_hash` differ materially, the system must HOLD, BLOCK, or require a new packet.

This aligns connector actions with the RIO distinction between human commitment and gate validation:

```text
COMMITTED != GATE_VALIDATED
```

Human approval binds authority to a proposal packet. Gate validation confirms the exact execution request still matches at execution time.

---

## Final commit rule

Some connector actions require a final human commit even if a packet already exists.

Final commit is required for:

- sending email or messages;
- merging pull requests;
- creating repositories;
- deleting files, emails, pages, issues, messages, or records;
- publishing publicly;
- changing permissions or sharing settings;
- inviting attendees or adding people to a workspace;
- spending money;
- triggering physical-world action;
- changing canonical source-of-truth status;
- executing database mutations.

Default final phrase:

> Approved to execute.

For high-consequence actions, use a specific phrase:

- Approved to send.
- Approved to merge.
- Approved to create this repository.
- Approved to delete.
- Approved to publish.
- Approved to change permissions.
- Approved to invite attendees.
- Approved to mutate this database.
- Approved to update source of truth.

Final phrase binding rule:

> The final phrase must bind to the exact action, target, surface, and material content being executed.

A generic final phrase does not authorize a changed target, changed recipient, changed branch, changed repository, changed file, changed permission set, changed public visibility, or changed action type.

---

## Canonical verdict mapping

The connector packet should map failures to RIO's canonical verdicts.

| Condition | Recommended verdict |
|----------|---------------------|
| Missing connector service | CLARIFY |
| Missing account/workspace where required | CLARIFY |
| Ambiguous target surface | CLARIFY for read; HOLD for write/action |
| Missing allowed/forbidden actions | HOLD |
| Consequence level unknown | HOLD |
| Preview required but not shown | HOLD |
| Final phrase missing for send/merge/delete/publish/permission/invite/database/source-of-truth action | HOLD |
| Human explicitly refuses or revokes | REFUSE |
| Action exceeds allowed scope | BLOCK |
| Action targets forbidden surface | BLOCK |
| Execution target does not match authorized target | BLOCK, or INVALID if bypass was attempted |
| User asks to bypass governance, final confirmation, or receipt labeling | INVALID |
| Connector unavailable/timeouts before execution | HOLD |
| Connector action attempted and connector fails | FAILED |
| Connector executed but returned no evidence/link/id for consequential action | HOLD for review; FAILED if outcome cannot be verified |
| Low-risk action can proceed with advisory concern | WARN |
| Packet validates and action is within scope | PASS |

BLOCK vs INVALID:

- `BLOCK` = action may be structurally valid but is denied under current rules, policy, or scope.
- `INVALID` = request attempts to bypass invariants or cannot be admitted into the pipeline.

---

## Receipt expectation by consequence level

Receipt burden should scale with consequence.

| Consequence level | Minimum receipt expectation |
|-------------------|----------------------------|
| none | no receipt or draft_receipt_language, depending on task |
| low | draft_receipt_language plus tool result/link/id if any action occurred |
| medium | proposed_receipt or local_receipt if receipt engine is available |
| high | signed_receipt if receipt engine is available; otherwise HOLD or degraded-mode note |
| critical | signed + ledgered + verified, or BLOCK/HOLD until proof path exists |

Receipt status labels:

| Label | Meaning |
|------|---------|
| draft_receipt_language | Structured text in chat/doc; not cryptographic proof |
| proposed_receipt | Ready to be written to a receipt system |
| local_receipt | Written by a local receipt engine |
| signed_receipt | Cryptographically signed |
| ledgered_receipt | Preserved in inspectable append-only ledger |
| verified_receipt | Independently checked under defined verification process |

Keeper boundary:

> Chat receipt language is not a cryptographic receipt.

---

## Degraded proof behavior

If the connector action can run but the expected proof path is unavailable, the system must not silently downgrade proof.

Degraded proof requires:

1. explicit notice to the human;
2. consequence level review;
3. minimum fallback record;
4. clear label that proof is degraded;
5. human decision to proceed, hold, or cancel;
6. no claim of signed/ledgered/verified receipt unless true.

Default behavior:

| Consequence level | Proof unavailable behavior |
|-------------------|----------------------------|
| none | proceed if no receipt required |
| low | proceed with draft status if human accepts |
| medium | HOLD unless human accepts degraded proof |
| high | HOLD by default |
| critical | BLOCK or HOLD until proof is restored |

---

## Rollback limits

Rollback may be expected but is not always possible.

The packet must distinguish:

| Rollback status | Meaning |
|----------------|---------|
| yes | action can be fully reversed |
| partial | some but not all effects can be reversed |
| no | action is effectively irreversible |
| unknown | rollback not confirmed |

Irreversible or partially reversible examples:

- sent email/message;
- public publication indexed by third parties;
- merged PR with downstream pulls;
- permission change already used by a third party;
- deleted data without backup;
- invited attendee notification already delivered;
- database mutation without transaction/backup;
- physical-world action.

If rollback is `no`, `partial`, or `unknown`, final confirmation must explicitly acknowledge irreversibility for high or critical consequence actions.

---

## Multi-connector chaining

A multi-connector chain occurs when one task uses two or more connector surfaces.

Examples:

- read Gmail attachment -> save to Drive -> open GitHub PR;
- fetch Drive doc -> email it to a third party;
- search calendar -> invite attendees -> send Slack notice;
- query database -> update spreadsheet -> publish report.

Rules:

1. Each connector step requires its own packet or a chain packet that explicitly names all connectors, targets, transitions, and consequence levels.
2. Authorization on connector A does not authorize connector B.
3. Read permission on connector A does not imply write permission on connector B.
4. Chain steps must not silently add recipients, repositories, folders, channels, databases, or public surfaces.
5. Each consequential step requires preview, final commit if applicable, and receipt/proof according to consequence level.

Chain keeper line:

> Cross-surface movement is consequence.

---

## Connector policy packs

A Connector Policy Pack is a standing rule set for one connector.

Examples:

| Connector | Standing rule example |
|----------|-----------------------|
| Gmail | May draft but not send without final confirmation |
| GitHub | May write to scoped PR branches; may not merge without final confirmation |
| Google Drive | May create docs when scoped; may not share publicly without final confirmation |
| Notion | May draft pages; may not publish or change permissions without final confirmation |
| Calendar | May propose events; may not invite attendees without final confirmation |
| Slack/Teams | May draft messages; may not post without final confirmation |
| Database | May read scoped records; may not mutate without final confirmation and proof path |

Connector Policy Packs do not replace task-specific authorization. They set defaults.

---

## Examples

### Example A — GitHub draft PR update

```yaml
connector_action_authorization_packet:
  version: "0.2"
  status_truth_label: "draft-preserved"

  human_authority:
    authorized_by: "Brian Kent Rasmussen"
    explicit_instruction: "Update draft PR #17 with the approved amendment language."

  connector_state:
    connected: true
    available_to_session: true
    tool_capable: true
    authorized_for_task: true
    gate_validated: false
    executed: false
    receipted: false
    verified: false

  connector:
    service: "GitHub"
    account_or_workspace: "bkr1297-RIO"
    surface: "rio-protocol"
    target_url_or_id: "PR #17 / branch docs/precision-by-friction-v0.1"
    target_precision: "owner/repo + PR number + branch"

  mode:
    access_type: "write_to_branch"
    consequence_level: "medium"

  purpose:
    goal: "Add approved amendment docs to PR #17."
    success_condition: "PR remains draft, docs-only, non-canonical, no merge."

  scope:
    allowed_actions:
      - "Create or update markdown files on the existing PR branch"
    forbidden_actions:
      - "Merge PR"
      - "Create new repo"
      - "Change SOURCE_OF_TRUTH.md"
      - "Change runtime code"
      - "Delete files"

  execution_binding:
    packet_hash: ""
    authorized_args_hash: ""
    execution_args_hash: ""
    must_match_before_execution: true

  final_commit:
    required_for:
      - "merge_pr"
    human_final_phrase_required: "Approved to merge"
```

---

### Example B — Gmail draft only

```yaml
connector_action_authorization_packet:
  version: "0.2"
  status_truth_label: "draft-preserved"

  connector:
    service: "Gmail"
    target_url_or_id: "new draft only"
    target_precision: "recipient + subject + draft mode"

  mode:
    access_type: "create_draft"
    consequence_level: "medium"

  purpose:
    goal: "Draft an email for human review."
    success_condition: "Draft created only. Nothing sent."

  scope:
    allowed_actions:
      - "Create draft email"
    forbidden_actions:
      - "Send email"
      - "Forward email"
      - "Delete email"
      - "Archive email"
      - "Label messages unless separately approved"

  final_commit:
    required_for:
      - "send_email"
    human_final_phrase_required: "Approved to send"
```

---

### Example C — Google Drive create but do not share publicly

```yaml
connector_action_authorization_packet:
  version: "0.2"
  status_truth_label: "draft-preserved"

  connector:
    service: "Google Drive"
    account_or_workspace: "Brian's Drive"
    surface: "Google Docs"
    target_url_or_id: "new private document"
    target_precision: "document title + folder + sharing scope"

  mode:
    access_type: "create_draft"
    consequence_level: "medium"

  purpose:
    goal: "Create a private working document."
    success_condition: "Doc exists privately; no public sharing."

  scope:
    allowed_actions:
      - "Create Google Doc"
      - "Insert approved content"
    forbidden_actions:
      - "Share publicly"
      - "Add collaborators"
      - "Change permissions"
      - "Publish to web"

  final_commit:
    required_for:
      - "modify_permissions"
      - "publish_publicly"
    human_final_phrase_required: "Approved to change permissions"
```

---

### Example D — Calendar proposal without attendee invite

```yaml
connector_action_authorization_packet:
  version: "0.2"
  status_truth_label: "draft-preserved"

  connector:
    service: "Calendar"
    target_url_or_id: "primary calendar / proposed event window"
    target_precision: "calendar ID + date/time window + attendee rule"

  mode:
    access_type: "create_draft"
    consequence_level: "medium"

  purpose:
    goal: "Propose a calendar event for human review."
    success_condition: "Draft/proposed event details prepared; no attendee invitations sent."

  scope:
    allowed_actions:
      - "Search availability"
      - "Prepare proposed event details"
    forbidden_actions:
      - "Invite attendees"
      - "Send updates"
      - "Change existing events"

  final_commit:
    required_for:
      - "invite_attendees"
    human_final_phrase_required: "Approved to invite attendees"
```

---

### Example E — Slack/Teams draft message

```yaml
connector_action_authorization_packet:
  version: "0.2"
  status_truth_label: "draft-preserved"

  connector:
    service: "Slack | Teams"
    account_or_workspace: ""
    surface: "channel or DM"
    target_url_or_id: ""
    target_precision: "workspace + channel/DM + post/edit/delete action"

  mode:
    access_type: "draft_only"
    consequence_level: "medium"

  purpose:
    goal: "Draft a message for human review."
    success_condition: "Message drafted; not posted."

  scope:
    allowed_actions:
      - "Draft message text"
    forbidden_actions:
      - "Post message"
      - "Edit existing message"
      - "Delete message"
      - "Tag users or channels unless approved"

  final_commit:
    required_for:
      - "send_message"
    human_final_phrase_required: "Approved to post"
```

---

### Example F — Database read vs mutation

```yaml
connector_action_authorization_packet:
  version: "0.2"
  status_truth_label: "draft-preserved"

  connector:
    service: "Database"
    account_or_workspace: ""
    surface: ""
    target_url_or_id: "database/table/query scope"
    target_precision: "database + schema/table + query/mutation + record IDs if applicable"

  mode:
    access_type: "read_only"
    consequence_level: "medium"

  purpose:
    goal: "Inspect scoped records and summarize findings."
    success_condition: "Read-only summary generated; no data mutation."

  scope:
    allowed_actions:
      - "Run read-only query"
      - "Summarize returned rows"
    forbidden_actions:
      - "Insert rows"
      - "Update rows"
      - "Delete rows"
      - "Change schema"
      - "Export beyond approved scope"

  final_commit:
    required_for:
      - "database_mutation"
    human_final_phrase_required: "Approved to mutate this database"
```

---

## HOLD / BLOCK / INVALID examples

| Scenario | Expected response |
|---------|-------------------|
| "Send this when ready" with draft-only packet | HOLD before send |
| "Merge if it looks fine" after branch update packet | HOLD before merge |
| "Share the doc with everyone" without exact sharing scope | HOLD / CLARIFY |
| Gmail -> Drive -> GitHub chain without chain packet | HOLD until chain is packetized |
| Update source-of-truth when packet only authorized draft docs | BLOCK |
| Claim cryptographic receipt in chat without signed/hash-bound receipt | CLARIFY or INVALID if asked to mislabel |
| Create public repo without license/visibility/source-of-truth relation | HOLD |
| Delete data without final phrase and rollback plan | HOLD / BLOCK |

---

## Relationship to RIO / Sentinel / MUS / Ledger / MANTIS

```text
Connector available
-> Connector Action Authorization Packet
-> RIO authority/scope/consequence check
-> Sentinel target/action fidelity check
-> Connector action
-> MUS receipt or draft receipt record
-> Ledger/Chronicle if implemented
-> MANTIS observation and calibration
```

RIO determines admissibility. Sentinel verifies execution fidelity. MUS records what happened. The connector does not become authority.

---

## v0.2 status note

This is a draft spec. It does not create a live connector governance runtime, change connector permissions, authorize any connector action, establish conformance, amend source-of-truth, or promote itself to canonical protocol.

Recommended next review:

- stress-test v0.2 against GitHub, Gmail, Drive, Calendar, Slack/Teams, and database workflows;
- decide whether to convert packet fields into JSON Schema;
- decide whether connector governance belongs inside RIO canonical conformance or remains a separate draft protocol surface.
