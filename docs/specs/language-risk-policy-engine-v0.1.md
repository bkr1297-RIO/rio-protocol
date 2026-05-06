# Language Risk Policy Engine — v0.1

**Status:** Draft — Advisory / scanner mode only  
**Layer:** Scribe / Language Governance (Enforcement Runtime)  
**Cross-links:** Personal AI Grammar Packet v0.1, RIO Operating Spec, ONE Answer Check  

---

## §1 Purpose

The Language Risk Policy Engine is the enforcement runtime that evaluates messages against the Personal AI Grammar Packet and produces verdicts. It is the mechanism by which grammar rules become enforceable boundaries.

The Grammar Packet defines what is admissible. The Policy Engine evaluates whether a specific message is admissible. The distinction is constitutional: the packet is law, the engine is court.

---

## §2 Keeper Line

> Grammar defines the crossing. Policy evaluates the risk. RIO governs the boundary. Receipts prove what happened.

---

## §3 Layer Boundary

This section defines what the Policy Engine may and may not do. These boundaries are constitutional.

**Policy** evaluates risk and recommends routing. Policy may assign risk tier, suggest CLARIFY/WARN/HOLD/BLOCK/INVALID, and identify receipt requirements. Policy may not become final authority or override the human.

**Policy is not Grammar.** Policy does not define admissible crossings — it evaluates messages against them.

**Policy is not RIO.** Policy does not govern consequence — it recommends routing to RIO when consequence is detected.

**Policy is not the Human.** Policy does not settle meaning, override Commit, revoke consent, or make final accountable decisions.

**Policy is not Receipts.** Policy produces evaluation receipts, but receipts do not prove wisdom, morality, legality, truth, destiny, or ultimate meaning.

---

## §4 Verdicts

The Policy Engine produces exactly one of five verdicts for any evaluated message.

| Verdict | Definition | Consequence |
|---------|-----------|-------------|
| PASS | Language is inside approved grammar | Message proceeds without intervention |
| WARN | Possible drift or ambiguity detected | User can proceed with awareness; warning recorded |
| HOLD | Crossing requires clarification, revision, approval, or review | Message is paused until resolved |
| BLOCK | Language violates policy or attempts unsafe/unauthorized crossing | Message is refused; violation recorded |
| INVALID | Violates root invariant; cannot be treated as valid system behavior | System rejects entirely; integrity alert raised |

---

## §5 Verdict Semantics

### §5.1 PASS

The message does not trigger any active grammar rule. It remains within the boundaries defined by the Grammar Packet. No intervention is required. The system may optionally log the evaluation for audit purposes but takes no visible action.

### §5.2 WARN

The message triggers a rule at advisory level. The system detects possible drift, ambiguity, or proximity to a boundary but the crossing has not occurred. The user is informed and may proceed. The warning is recorded in the evaluation receipt.

**Examples:** Unacknowledged reliance shift, language approaching but not crossing identity boundary, ambiguous authority framing.

### §5.3 HOLD

The message triggers a rule that requires human resolution before the message can proceed. The system pauses delivery, execution, or routing until the human clarifies, revises, approves, or routes the message appropriately.

**Examples:** Implied action without explicit commitment, language that may transfer authority without delegation, public claim without evidence routing.

### §5.4 BLOCK

The message violates an active grammar rule. The system refuses to deliver, execute, or route the message. The violation is recorded. A safe revision may be suggested.

**Examples:** Machine settles human meaning, identity assignment, action taken without authorization, scope extension beyond grant.

### §5.5 INVALID

The message violates a root invariant of the system. It cannot be treated as valid system behavior. This verdict indicates a fundamental violation — not merely a policy breach but an attempt to operate outside the constitutional boundaries of the system.

**Examples:** Attempt to override human root authority, attempt to disable governance, attempt to forge receipts or bypass verification.

---

## §6 Least Restrictive Intervention Rule

Use the least restrictive route that preserves human authority and prevents unauthorized consequence.

**Escalation ladder:**

```
OBSERVE → LABEL → CLARIFY → WARN → HOLD → RIO REVIEW → BLOCK
```

**BLOCK requires one of:**

- Clear invariant violation
- Explicit unauthorized consequence
- Credential, money, or safety risk
- Identity impersonation
- Legal, medical, or financial high-stakes action without authority
- Tool/API execution without valid Commit
- External communication with unresolved high-risk crossing

The engine must not over-block. Over-blocking is a governance failure equivalent to under-blocking: it removes human authority by preventing legitimate action.

---

## §7 Evaluation Flow

The Policy Engine evaluates messages through the following sequence:

```
Message received
  → Parse message content and context
  → Load active Grammar Packet rules
  → Evaluate against each active rule
  → Determine highest-severity trigger
  → Apply Least Restrictive Intervention Rule
  → Produce verdict
  → If PASS: proceed
  → If WARN: annotate and proceed
  → If HOLD: pause and request resolution
  → If BLOCK: refuse and record
  → If INVALID: reject and alert
  → Generate evaluation receipt
```

---

## §8 RIO Handoff Rule

The trigger for RIO handoff is not risky language alone. The trigger is **risk + reliance or consequence**.

**RIO handoff triggers:**

- External communication
- Public claim
- Money movement
- Credential sharing
- Legal reliance
- Medical reliance
- Financial reliance
- Identity representation
- Delegated action
- Tool/API execution
- Commitment to another person
- Record creation with consequence
- Override after warning/hold/block

**RIO Handoff Contract:**

Each handoff must include:

```json
{
  "trigger": "why this is consequence-relevant",
  "risk_type": "language | identity | financial | relational | legal | medical | tool_action | public_claim | credential | external_communication",
  "requested_action": "what may happen next",
  "human_authority_required": true,
  "receipt_required": true,
  "proof_status": "Prompt Run | Human Recorded | Structured Packet | Receipt Created | Ledger Verified"
}
```

---

## §9 Receipt Trigger Table

Receipt or draft receipt required for:

| Event | Receipt Required |
|-------|-----------------|
| CLARIFY verdict | Yes |
| WARN verdict | Yes |
| HOLD verdict | Yes |
| BLOCK verdict | Yes |
| INVALID verdict | Yes |
| Human Commit | Yes |
| Human override | Yes |
| RIO handoff | Yes |
| Policy version used | Yes |
| Risk label assigned | Yes |
| Tool execution attempted | Yes |
| Tool execution refused | Yes |
| Meaning-closure warning | Yes |
| Protective-flattening warning | Yes |
| Handoff to another AI, human, or system | Yes |

---

## §10 Evaluation Receipt

Every evaluation produces a receipt regardless of verdict. The receipt records what was checked, what triggered, and what verdict was produced.

**Receipt fields:**

| Field | Description |
|-------|-------------|
| evaluation_id | Unique identifier for this evaluation |
| timestamp | ISO 8601 UTC timestamp |
| message_hash | SHA-256 hash of the evaluated message |
| packet_id | Grammar Packet used for evaluation |
| packet_version | Version of the Grammar Packet |
| rules_evaluated | List of rule IDs checked |
| triggers_fired | List of rule IDs that triggered |
| verdict | PASS, WARN, HOLD, BLOCK, or INVALID |
| highest_trigger_rule | Rule ID of the highest-severity trigger |
| safe_revision | Suggested safe revision (if applicable) |
| route | Recommended routing (if applicable) |
| context | Evaluation context (private_meaning, public_claim, action_authority, etc.) |

---

## §11 Rule Evaluation Logic

Each rule in the Grammar Packet is evaluated independently. The engine applies the following logic per rule:

1. **Match trigger:** Does the message match the rule's trigger conditions?
2. **Determine context:** What reliance context applies (exploration, private_meaning, public_claim, action_authority, delegated_authority)?
3. **Apply verdict map:** Given the trigger and context, what verdict does the rule produce?
4. **Apply Least Restrictive Intervention:** Is this the minimum intervention that preserves authority and prevents consequence?
5. **Record trigger:** Log the rule ID and verdict in the evaluation receipt.

After all rules are evaluated, the engine selects the **highest-severity verdict** as the final verdict. Severity order: INVALID > BLOCK > HOLD > WARN > PASS.

---

## §12 Context Detection

The Policy Engine must determine the reliance context of a message before applying verdict maps. Context detection uses the following signals:

| Signal | Indicates |
|--------|-----------|
| Exploratory language ("I wonder", "what if", "I'm thinking") | Exploration |
| Self-attribution ("I feel", "I experience", "to me this means") | Private meaning |
| Factual assertion ("this is true", "research shows", "it's proven") | Public claim |
| Action language ("send", "publish", "commit", "pay", "approve") | Action authority |
| Delegation language ("you decide", "handle this", "act on my behalf") | Delegated authority |

Context detection is advisory. When ambiguous, the engine defaults to the **more restrictive** context (fail-safe).

---

## §13 Safe Revision

When a message receives HOLD or BLOCK, the engine may suggest a safe revision. A safe revision is a reformulation of the message that would receive PASS or WARN under the same Grammar Packet.

Safe revisions are suggestions, not mandates. The human retains authority to revise differently, escalate, or override (with appropriate governance routing).

**Safe revision principles:**

- Preserve the human's intent
- Remove the boundary violation
- Maintain openness where meaning was being closed
- Route consequence where action was being leaked
- Reflect rather than settle where identity was being assigned

---

## §14 Integration Points

| System | Integration |
|--------|-------------|
| Personal AI Grammar Packet | Source of rules; engine evaluates against packet |
| RIO Operating Spec | HOLD/BLOCK verdicts on action_authority context trigger RIO handoff |
| ONE Answer Check | WARN/HOLD verdicts on public_claim context route to Answer Check |
| Handoff Receipt Protocol | When evaluation triggers RIO handoff, a handoff receipt is generated |
| Verification Stack | Evaluation receipts follow the verification stack (receipt → attestation → verification → ledger) |
| MANTIS | Pattern observation layer may consume evaluation receipts for drift detection |

---

## §15 Fail-Safe Behavior

The Policy Engine operates fail-safe (fail-closed for consequence, fail-open for exploration):

| Failure Mode | Behavior |
|-------------|----------|
| Grammar Packet unavailable | HOLD all messages until packet is loaded |
| Rule evaluation error | HOLD the message; do not default to PASS |
| Context detection ambiguous | Use more restrictive context |
| Multiple rules trigger at same severity | Report all triggers; use most specific rule for safe revision |
| Engine unavailable | No messages proceed; system enters safe mode |

---

## §16 Relationship to RIO

The Language Risk Policy Engine is **not** RIO. It is a pre-consequence evaluation layer.

| Layer | Function |
|-------|----------|
| Grammar Packet | Defines admissible crossings |
| Policy Engine | Evaluates messages against grammar |
| RIO | Governs consequence when language crosses into action |

The Policy Engine may produce a verdict that triggers a RIO handoff, but it does not itself govern consequence. It evaluates language risk. RIO governs action risk.

---

## §17 Non-Goals (v0.1)

This specification does not:

- Define how the engine is implemented (language, framework, deployment)
- Specify real-time performance requirements
- Define multi-user or multi-packet evaluation
- Specify how overrides or escalations are handled beyond routing to RIO
- Define machine learning or adaptive rule generation
- Build UI
- Build production enforcement
- Create autonomous blocking
- Collapse grammar, policy, RIO, receipts, or human authority into one layer

---

## §18 Readiness Classification

| Component | Readiness Level |
|-----------|----------------|
| Architecture | Controlled local testing ready |
| Policy engine | Advisory / scanner mode only |
| Blocking | Not production-ready |
| Outbound enforcement | Requires RIO handoff, receipt triggers, override rules, and proof-status labels |

---

## §19 Version History

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-05-05 | Initial draft — 5 verdicts, evaluation flow, receipt structure, integration points |
| v0.1.1 | 2026-05-05 | Red-team revision — added Layer Boundary, Least Restrictive Intervention Rule, RIO Handoff Rule/Contract, Receipt Trigger Table, Readiness Classification, Non-goals expanded |
