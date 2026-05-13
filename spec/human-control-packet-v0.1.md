# Human Control Packet v0.1

Status: Draft specification  
Date: 2026-05-12 MDT  
Scope: Documentation/spec only  
Maturity: Proposed for review; not yet canonical source-of-truth  

---

## Purpose

The **Human Control Packet** is the minimal structured input that helps ONE/RIO/MUSS preserve human authority in an interactive system.

It tells the machine what kind of help is allowed, what must stay bounded, what consequence level is present, and what proof or revocation conditions apply.

---

## One-line definition

A Human Control Packet is a human-authored boundary object that defines purpose, mode, scope, consequence, permission, claim status, prohibited actions, receipt requirements, and revocation conditions for an interaction or task.

---

## Why this exists

Interactive AI systems drift when the human's intended mode is implicit.

The Human Control Packet reduces drift by making the human's control signals explicit before the system moves toward action.

---

## Minimal packet fields

```yaml
human_control_packet:
  version: "0.1"
  purpose: ""
  mode: "reflection | private_journal | drafting | analysis | decision_support | proposal | public_handoff | execution_request"
  scope:
    included: []
    excluded: []
  consequence:
    external_effect: false
    affects_people: false
    affects_money: false
    affects_legal_or_medical: false
    affects_reputation_or_public_record: false
    affects_body_or_physical_world: false
    uses_external_tools: false
  permission:
    may_reflect: true
    may_draft: false
    may_prepare_packet: false
    may_decide: false
    may_execute: false
    may_contact_others: false
    may_use_tools: false
  claim_status: "private_meaning | hypothesis | draft | prototype | implemented | verified"
  public_private_status: "private | internal | public_candidate | public"
  boundaries:
    must_not: []
  receipt_requirement:
    required: false
    receipt_type: "none | draft_receipt | local_receipt | signed_receipt | ledger_entry"
  revocation:
    stop_phrase: "hold"
    rollback_expected: false
    notes: ""
```

---

## Field definitions

| Field | Meaning |
|------|---------|
| purpose | What the human is trying to do or understand |
| mode | The interaction mode; determines allowable machine behavior |
| scope.included | What the task may cover |
| scope.excluded | What must be kept outside the task |
| consequence | Flags indicating whether the task can affect the world outside the conversation |
| permission | What the machine may and may not do |
| claim_status | Maturity level of claims used or produced |
| public_private_status | Audience and disclosure boundary |
| boundaries.must_not | Explicit prohibitions |
| receipt_requirement | What proof must exist if consequence occurs |
| revocation | How the human can stop, undo, or limit the task |

---

## Mode semantics

| Mode | Allowed behavior | Forbidden behavior |
|------|------------------|--------------------|
| reflection | Mirror, map, clarify, ask questions | Execute, contact, publicize, decide |
| private_journal | Preserve meaning, name patterns, mark private | Convert private meaning into public claim |
| drafting | Produce text or artifacts for review | Treat draft as approved or sent |
| analysis | Inspect, compare, stress-test | Decide for human |
| decision_support | Present options, risks, tradeoffs | Make final decision |
| proposal | Prepare a governed packet for review | Execute packet |
| public_handoff | Translate into public-safe language | Include private-origin material without permission |
| execution_request | Prepare for RIO authorization and gate validation | Execute without approval and receipt |

---

## Required default behavior

If no Human Control Packet exists, the system should default to:

```yaml
mode: reflection
permission:
  may_reflect: true
  may_draft: true only when clearly requested
  may_prepare_packet: false unless requested
  may_decide: false
  may_execute: false
  may_contact_others: false
  may_use_tools: false unless explicitly requested or required for the user's direct task
claim_status: draft
public_private_status: private
receipt_requirement:
  required: false unless consequence is requested
```

---

## Consequence escalation

The system should increase friction when any consequence flag is true.

| Consequence flag | Minimum response |
|-----------------|------------------|
| affects_people | Clarify recipient/impact/scope before action |
| affects_money | Require explicit approval and receipt |
| affects_legal_or_medical | Require high-stakes disclaimer, grounding, and human/professional authority |
| affects_reputation_or_public_record | Require public/private and claim-status review |
| affects_body_or_physical_world | Require safety, physical-world, and liability review |
| uses_external_tools | Route through authorization and receipt rules |

---

## Failure modes reduced

The Human Control Packet reduces:

- vague consent;
- mode confusion;
- scope creep;
- public/private collapse;
- execution without authorization;
- claim-status inflation;
- simulated proof treated as real proof;
- hidden tool use;
- overhelpfulness;
- authority transfer;
- failure to honor revocation.

---

## Failure modes not solved by the packet alone

The packet does not solve:

- malicious human intent;
- coercive third-party pressure;
- downstream platform misuse;
- unverified external facts;
- runtime bypass;
- cryptographic failure;
- unsafe physical execution;
- legal/regulatory noncompliance;
- human rubber-stamping.

Those require RIO, Sentinel, MUS, Ledger, external governance, safety review, and human responsibility.

---

## Human-friendly prompt

When needed, the system may ask for this compact version:

```text
What mode are we in?
Reflection, drafting, decision support, public handoff, or execution?

What is included and excluded?

Can this affect another person, money, law/medicine, reputation, public record, tools, or the physical world?

May I only reflect, may I draft, may I prepare a packet, or may I move toward action?

Is this private meaning, a hypothesis, a draft, a prototype, implemented, or verified?

What must not happen?
```

---

## Keeper lines

- The system does not need a perfect human. It needs a sovereign human who can say what is allowed, what is not allowed, what is real, what is private, what is public, and what must stop.
- Clean boundaries before action reduce failure.
- Human control is not a vibe. It is a packet.

---

## Status note

This is a draft packet format. It should be tested against live workflows before being promoted to a normative schema.
