# Connector Action Authorization Packet v0.1

Status: draft_spec  
Date: 2026-05-13 MDT  
Scope: Documentation/spec only  
Canonical status: Not canonical until Brian Commit / later source-of-truth promotion  
Repository: bkr1297-RIO/rio-protocol  

---

## Purpose

The **Connector Action Authorization Packet** is the explicit human permission object that converts connected tool capability into bounded, task-specific authority.

It governs how a machine-operated system may use connected services such as GitHub, Google Drive, Gmail, Notion, Linear, Outlook, Slack, calendars, databases, or other external surfaces.

Connecting a service gives possible capability. It does not grant task authority.

---

## One-line definition

A Connector Action Authorization Packet is a human-authored authorization object that names the connector, target surface, allowed action, forbidden action, consequence level, preview requirement, final confirmation requirement, and receipt expectation for a single connector task.

---

## Keeper lines

> Connected is not authorized. Authorized is not executed. Executed is not receipted.

> Connectors give the machine hands. RIO decides when the hands may move.

> Drafting is preparation. Sending is consequence.

---

## Why this exists

Connected tools introduce real-world consequence. A model may have access to a connector and still lack authority to use it for the current task.

This packet prevents collapse between:

- sign-in and permission;
- available tool and authorized use;
- draft and send;
- read and write;
- write and publish;
- branch update and merge;
- proposed receipt and cryptographic receipt;
- connector capability and human authority.

---

## Connector action stack

| Layer | Meaning |
|------|---------|
| Connected | The human has signed in or authorized the service at the account level |
| Available to session | The current model/session can see or call the connector |
| Tool-capable | The connector exposes actions such as read, draft, write, send, delete, merge, create |
| Authorized for task | The human has explicitly permitted a specific connector action in scope |
| Executed | The tool actually ran and returned evidence |
| Receipted | The action has a record/proof trail under the applicable receipt standard |

Non-collapse rule:

> Connected access is setup. Task authority is per-action.

---

## Relationship to Human Control Packet

The Connector Action Authorization Packet is a specialized child of the Human Control Packet.

The Human Control Packet defines mode, scope, consequence, claim status, and revocation for an interaction.

The Connector Action Authorization Packet defines exactly how those controls apply to a connected service.

---

## Relationship to future Connector Governance Protocol

This packet may later become part of a broader **Connector Governance Protocol**.

For now:

| Layer | Status |
|------|--------|
| Connector Governance Protocol | Named category / future protocol candidate |
| Connector Action Authorization Packet | Draft spec now |
| Connector Policy Packs | Future per-tool standing rules |
| Connector Receipts | Future proof/conformance layer |

This file defines the packet, not the full protocol.

---

## Packet template

```yaml
connector_action_authorization_packet:
  version: "0.1"

  human_authority:
    authorized_by: ""
    timestamp: ""
    explicit_instruction: ""

  connector:
    service: "GitHub | Google Drive | Gmail | Notion | Linear | Outlook | Slack | Calendar | Other"
    account_or_workspace: ""
    surface: ""
    target_url_or_id: ""

  mode:
    access_type: "read_only | draft_only | write_to_branch | create_draft | send | delete | merge | create_repo | publish | permission_change"
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

  constraints:
    timebox: ""
    max_items: ""
    no_external_send_without_final_confirm: true
    no_delete_without_final_confirm: true
    no_merge_without_final_confirm: true
    no_public_publish_without_final_confirm: true
    no_permission_change_without_final_confirm: true

  preview_requirement:
    required_before_write: true
    required_before_external_consequence: true
    human_must_review: true

  receipt_requirement:
    draft_receipt_required: true
    cryptographic_receipt_required_if_available: false
    record:
      - action_taken
      - connector_used
      - target
      - timestamp
      - result
      - link_or_id
      - limitations

  revocation:
    stop_phrase: "hold"
    rollback_expected: true
    rollback_plan: ""

  final_commit:
    required_for:
      - send_email
      - merge_pr
      - create_repo
      - delete_file
      - publish_publicly
      - modify_permissions
    human_final_phrase_required: "Approved to execute"
```

---

## Required fields

A minimally valid packet must include:

1. human authority statement;
2. connector service;
3. target surface or URL/ID;
4. access type;
5. purpose;
6. allowed actions;
7. forbidden actions;
8. consequence level;
9. preview requirement;
10. receipt requirement;
11. revocation condition;
12. final commit conditions.

If any required field is missing for a consequential connector action, the system should HOLD or CLARIFY.

---

## Access-type semantics

| Access type | Meaning | Final confirmation required? |
|------------|---------|------------------------------|
| read_only | Search, fetch, inspect, summarize | Usually no, unless high-stakes/private scope requires it |
| draft_only | Prepare draft without external send/publish | No send/publish allowed |
| write_to_branch | Modify an existing branch/PR surface | Required before merge/publish |
| create_draft | Create draft email/doc/page | Required before send/share/publish |
| send | Send an email/message externally | Yes |
| delete | Delete file/message/data | Yes |
| merge | Merge PR or equivalent source-surface change | Yes |
| create_repo | Create new repository | Yes |
| publish | Make content public or externally visible | Yes |
| permission_change | Add users, change sharing, alter access | Yes |

---

## Final commit rule

Some connector actions require a final human commit even if a packet already exists.

Final commit is required for:

- sending email or messages;
- merging pull requests;
- creating repositories;
- deleting files, emails, pages, issues, or records;
- publishing publicly;
- changing permissions or sharing settings;
- spending money;
- triggering physical-world action;
- contacting third parties;
- changing canonical source-of-truth status.

Default final phrase:

> Approved to execute.

For high-consequence actions, use a specific phrase:

- Approved to send.
- Approved to merge.
- Approved to create this repository.
- Approved to delete.
- Approved to publish.
- Approved to change permissions.

---

## Connector policy packs

A Connector Policy Pack is a standing rule set for one connector.

Examples:

| Connector | Standing rule example |
|----------|-----------------------|
| Gmail | May draft but not send without final confirmation |
| GitHub | May write to draft PR branches when explicitly scoped; may not merge without final confirmation |
| Google Drive | May create docs when explicitly scoped; may not share publicly without final confirmation |
| Notion | May draft pages; may not publish or change permissions without final confirmation |
| Calendar | May propose events; may not invite attendees without final confirmation |

Connector Policy Packs do not replace task-specific authorization. They set defaults.

---

## Example: GitHub draft PR update

```yaml
connector_action_authorization_packet:
  version: "0.1"

  human_authority:
    authorized_by: "Brian Kent Rasmussen"
    explicit_instruction: "Update draft PR #17 with the approved amendment language."

  connector:
    service: "GitHub"
    account_or_workspace: "bkr1297-RIO"
    surface: "rio-protocol"
    target_url_or_id: "PR #17 / branch docs/precision-by-friction-v0.1"

  mode:
    access_type: "write_to_branch"
    consequence_level: "medium"

  purpose:
    goal: "Add approved amendment docs to PR #17."
    success_condition: "PR remains draft, docs-only, non-canonical, no merge."

  scope:
    allowed_actions:
      - "Create or update markdown files on the existing PR branch"
      - "Update PR body if explicitly included"
      - "Add review comment if explicitly included"
    forbidden_actions:
      - "Merge PR"
      - "Create new repo"
      - "Change SOURCE_OF_TRUTH.md"
      - "Change runtime code"
      - "Change schemas unless draft-only"
      - "Delete files"

  receipt_requirement:
    draft_receipt_required: true
    record:
      - changed_files
      - PR link
      - commit SHA
      - scope limits

  final_commit:
    required_for:
      - "merge_pr"
      - "create_repo"
      - "delete_file"
      - "modify_permissions"
    human_final_phrase_required: "Approved to execute"
```

---

## Example: Gmail draft

```yaml
connector_action_authorization_packet:
  version: "0.1"

  connector:
    service: "Gmail"
    target_url_or_id: "Brian's Gmail"

  mode:
    access_type: "create_draft"
    consequence_level: "medium"

  purpose:
    goal: "Draft an email for Brian to review."
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

## Example: repository creation

```yaml
connector_action_authorization_packet:
  version: "0.1"

  connector:
    service: "GitHub"
    account_or_workspace: "bkr1297-RIO"

  mode:
    access_type: "create_repo"
    consequence_level: "high"

  purpose:
    goal: "Create a new repository for ONE protocol work."
    success_condition: "Repo created with exact approved name, visibility, license posture, and README boundary."

  required_preflight:
    repo_name: ""
    visibility: "private | public"
    license: "none | MIT | Apache-2.0 | All Rights Reserved | TBD"
    canonical_status: "draft | canonical | reference | prototype"
    source_of_truth_relationship: ""
    why_not_existing_repo: ""

  scope:
    allowed_actions:
      - "Create repository only after final confirmation"
      - "Set visibility exactly as approved"
      - "Add initial README if approved"
      - "Add LICENSE only if approved"
    forbidden_actions:
      - "Create multiple repos"
      - "Make public if private was approved"
      - "Choose license automatically"
      - "Invite collaborators"
      - "Publish claims of implementation"
      - "Move canonical status from rio-protocol"

  final_commit:
    required_for:
      - "create_repo"
    human_final_phrase_required: "Approved to create this repository"
```

---

## Failure modes reduced

| Failure mode | Description | Control |
|-------------|-------------|---------|
| Connected-access drift | Signed-in connector is treated as task permission | Require action packet |
| Draft/send collapse | Drafting is confused with sending | Final send confirmation |
| Read/write collapse | Reading drifts into editing or publishing | Access-type semantics |
| Preview bypass | External action occurs before human review | Preview requirement |
| Silent connector action | Tool acts without visible evidence | Tool result + receipt record |
| Surface confusion | Action happens in wrong repo, doc, folder, inbox, workspace | Target URL/ID required |
| Permission inflation | One approved connector action expands into broader tool use | Allowed/forbidden actions |
| Merge/publish collapse | Branch or draft update becomes public/canonical | Final commit rule |
| Permission-change drift | Sharing/collaborator settings change without explicit approval | Permission-change final confirmation |
| Receipt overclaim | Draft receipt language is treated as cryptographic proof | Receipt status labels |

---

## HOLD / BLOCK conditions

The system should HOLD when:

- connector service is not named;
- target surface is ambiguous;
- action type is ambiguous;
- allowed and forbidden actions are missing;
- consequence level is unknown;
- final commit status is unclear;
- human asks for a high-consequence action without exact target;
- connector action could affect third parties;
- deletion, sending, publishing, merging, repo creation, or permission change is requested without final phrase.

The system should BLOCK or INVALID when:

- the requested action violates a core invariant;
- the user asks the system to bypass governance;
- the action exceeds connector policy;
- execution target does not match authorization;
- final confirmation is missing for required action;
- tool output shows the action would affect an unapproved surface.

---

## Receipt status labels

| Label | Meaning |
|------|---------|
| draft_receipt_language | Structured text in chat/doc; not cryptographic proof |
| proposed_receipt | Ready to be written to a receipt system |
| local_receipt | Written by a local receipt engine |
| signed_receipt | Cryptographically signed |
| ledgered_receipt | Preserved in inspectable append-only ledger |
| verified_receipt | Independently checked under defined verification process |

Keeper line:

> Chat receipt language is not a cryptographic receipt.

---

## Minimal human prompt

```text
Connector:
Target:
Action:
Mode: read-only / draft / write / send / merge / create / delete / publish / permission-change
Allowed:
Forbidden:
Consequence:
Preview before action: yes/no
Receipt required: yes/no
Final confirmation phrase:
```

---

## Relationship to RIO/Sentinel/MUS

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

## Status note

This is a draft spec. It does not create a live connector governance runtime, change connector permissions, authorize any connector action, or establish a canonical protocol. It should be tested against GitHub, Drive, Gmail, Notion, and other connector workflows before canonical promotion.
