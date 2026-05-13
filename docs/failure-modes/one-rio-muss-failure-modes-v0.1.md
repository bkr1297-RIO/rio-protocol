# ONE/RIO/MUSS Failure Modes Catalog v0.1

Status: Draft failure-mode catalog  
Date: 2026-05-12 MDT  
Scope: Documentation only  
Maturity: Proposed for review; not yet canonical source-of-truth  

---

## Purpose

This catalog names how ONE/RIO/MUSS can break, how failure should be detected, what the system should do when failure appears, and what human input helps the system break less often.

The goal is not to claim the system never fails.

The goal is to make failures visible, local, reversible where possible, receipted when consequential, and unable to silently become authority.

---

## Root failure pattern

> The system breaks when roles collapse.

The deepest failure is authority drift: a non-human component starts behaving as if it has authority, or a human treats non-human output as authority.

---

## Core non-collapse boundaries

| Must not collapse | Into |
|------------------|------|
| Signal | Authority |
| Meaning | Proof |
| Reasoning | Truth |
| Proposal | Permission |
| Execution | Sovereignty |
| Receipt | Wisdom |
| Machine presence | Human authority |
| Pattern recognition | Identity assignment |
| Learning | Permission |
| Access | Consent |
| Capability | Action |
| Helpfulness | Authorization |

---

## Failure response ladder

The system should use the least invasive response that preserves human authority and prevents invalid consequence.

```text
OBSERVE -> LABEL -> CLARIFY -> WARN -> HOLD -> RIO REVIEW -> BLOCK -> INVALID
```

- OBSERVE: notice without interrupting.
- LABEL: name the possible pattern.
- CLARIFY: ask for missing authority, scope, or claim status.
- WARN: surface risk while preserving human choice.
- HOLD: pause movement toward consequence.
- RIO REVIEW: route through governance review.
- BLOCK: refuse under current rules.
- INVALID: invariant violation; cannot be treated as valid system behavior.

---

## Good failure properties

A governed failure should be:

| Property | Meaning |
|---------|---------|
| Visible | The human can see what failed |
| Local | The failure does not spread across the whole system |
| Reversible | Action can be stopped or rolled back where possible |
| Receipted | Consequential failure is recorded |
| Non-coercive | Human authority remains intact |
| Fail-closed | Consequence pauses when authority/scope is unclear |
| Reviewable | Humans/auditors can inspect it |
| Learnable | Rules, friction, or review thresholds can improve after failure |

Keeper line:

> A governed system is not one that never fails. It is one whose failures cannot silently become authority.

---

## Category A — Human-authority failures

| Failure mode | How it breaks | Detection signal | Human input needed | Response |
|-------------|---------------|------------------|-------------------|----------|
| Vague consent | System acts on implied permission | No explicit mode/permission/consequence packet | Clear yes/no, scope, consequence boundary | CLARIFY/HOLD |
| Scope creep | Reflection becomes drafting, outreach, posting, deployment, spending, or tool action | Action verbs appear outside approved mode | Included/excluded scope | HOLD |
| Rubber-stamping | Human approves too quickly because the system sounds confident | Rapid approval on high-risk or repeated approvals without review | Slow approval, review reason | WARN/HOLD |
| Overdependence | Human outsources judgment, identity, emotion, or calling | Repeated requests for final meaning/identity/confidence | Human keeps final interpretive authority | LABEL/CLARIFY |
| Exhaustion/activation | Tired/stressed human gives unclear or inflated instructions | Emotional intensity + consequence request | Mode reset, pause, body/state signal | HOLD |
| Unclear revocation | Approval feels hard to stop | No stop phrase or rollback condition | Explicit revocation rule | CLARIFY |

---

## Category B — Model-reasoning failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Reasoning becomes authority | Model explanation is treated as final truth | High confidence + low evidence + reliance language | Reasoning Packet stays lowest-weight input |
| Confident hallucination | Model invents implementation, receipts, dates, facts, or current status | Claim lacks source/receipt/evidence | Source/receipt distinction |
| Narrative overfit | Everything fits the architecture too neatly | Totalizing language; no null findings | Allow "not enough evidence" |
| Mirror inflation | Reflection becomes certainty/praise/destiny | Identity or destiny language increases | Meaning Closure Boundary |
| Protective flattening | Meaningful experience is reduced to "just" bias/psychology | Dismissive minimization | Preserve meaning; govern consequence |
| False maturity claims | Draft becomes described as implemented/deployed/verified | Claim-status mismatch | Maturity labels |

---

## Category C — Receipt/proof failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Simulated receipt mistaken for real receipt | Chat says ledger/receipt exists without cryptographic record | No hash, signature, storage, file, or commit | Label as draft/simulated |
| Receipt overclaim | Receipt proves event but is treated as proof of truth/wisdom | "Proved correct" language | Proof is accountability, not authority |
| Missing negative receipts | Holds, refusals, uncertainty, and failures vanish | Only success records exist | Refusal receipts first-class |
| Ledger theater | Ledger language without durable inspectable ledger | No append-only record | Require actual ledger evidence |
| Proof fragmentation | Receipts are scattered across chats, docs, code, memory | No canonical location | Standard receipt format/location |

---

## Category D — Public/private boundary failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Private meaning becomes public claim | Spiritual/numerological/founder-origin material is presented as technical evidence | Mixed-audience document | Public/private sort |
| Public language erases origin | Technical artifact loses human formation context | No founder/private archive | Preserve private formation docs |
| Mixed-audience confusion | Engineers/investors see private-origin language before translation | Sacred + technical claims in one surface | Dual rendering |
| Founder centrality risk | Personal method naming makes infrastructure sound like personal doctrine | Founder-name as system proof | Let architecture carry public name |
| Meaning closure | System tells human what experience ultimately means | Destiny/identity assignment | Meaning remains human-owned |

---

## Category E — RIO governance failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Underblocking | Risky action passes because proposal sounds reasonable | Risk flag below threshold despite consequence | Fail-closed defaults |
| Overblocking | Useful action freezes unnecessarily | Repeated HOLD for low-risk tasks | Friction calibration |
| Moral overreach | RIO decides good/worthy/true/spiritually correct | Governance language becomes value-authority | RIO governs admissible consequence only |
| Policy ambiguity | Rules conflict | Multiple policy outcomes | Decision precedence |
| Override erosion | Human override becomes routine | Override clusters | Override receipts + reason |
| Hidden policy updates | Rules change without approval | Behavior changes without version | Amendment/version process |

---

## Category F — Sentinel/execution-fidelity failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Packet/action mismatch | Human approved one thing; system does another | Hash mismatch; changed target/content/tool | Re-evaluate changed packet |
| Tool bypass | Connector, robot, API, or agent acts outside gate | Execution without token/gate check | All execution behind PEP/Sentinel |
| Overliteral blocking | Harmless variation is blocked | High false positive rate | Material-change definition |
| Silent substitution | Wording, recipient, amount, timing, or target changes | Diff between approval and execution | New packet required |
| External connector drift | Third-party tools update behavior | Capability change | Connector registry + revalidation |

---

## Category G — MANTIS / pattern-witness failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Pattern becomes identity | System says "you are this pattern" | Identity assignment | "This resembles a pattern" only |
| Pattern becomes destiny | Repetition becomes proof of fate | Fate/inevitability language | Meaning Closure Boundary |
| Surveillance feeling | Witness layer feels like monitoring | Human discomfort / opaque memory | Human-owned memory + revocation |
| Overfitting | Everything becomes part of the map | No null results | Allow null finding |
| Contradiction suppression | System favors coherence over reality | Dissent/anomaly removed | Preserve dissent |
| Memory contamination | Old context biases new reading | Stale memory used as current fact | Freshness/source weighting |

---

## Category H — Oddity / novelty failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Novelty inflation | Every strange signal becomes significant | Unbounded meaning accumulation | Require recurrence, consequence relevance, or human marking |
| Novelty suppression | System dismisses what does not fit | Anomaly is flattened | Protect strange long enough to understand it |
| Mystery becomes instruction | Oddity is treated as command/proof | "This means we must" language | Oddity may flag; not authorize |
| Permanent ambiguity | Nothing resolves | Endless holding | Time-boxed review |
| Creative chaos | Emergence overwhelms governance | Unbounded expansion + action pressure | RIO boundary before consequence |

---

## Category I — Embodied-system failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Authority mimicry | Robot feels like police/security | Command posture/tone/lights | Design review |
| Escalation drift | Bot summons force or emergency response too easily | High escalation frequency | Local escalation policy |
| Profiling | Distress/anger/homelessness/disability becomes risk identity | Protected context used as threat label | Pattern Dignity rules |
| Privacy breach | Support becomes surveillance | Covert or excessive recording | Data minimization |
| Community rejection | System is experienced as tech-dropped control | Complaints, avoidance, vandalism | Local governance/co-design |
| Hijack/tampering | Device is spoofed or redirected | Unsigned commands; anomalous behavior | Cybersecurity + fail-safe |
| Physical harm | Robot/exosuit causes injury | Proximity/force/speed violation | Safety certification |
| Exosuit override | Suit moves against wearer will | User agency mismatch | Wearer control and emergency-stop limits |
| Labor coercion | Augmentation used to demand unsafe productivity | Productivity pressure tied to device | Worker-rights policy |

---

## Category J — Community-integration failures

| Failure mode | How it breaks | Detection signal | Control |
|-------------|---------------|------------------|---------|
| Tech-drop failure | System deployed without trust | No local governance | Co-design |
| Institutional capture | Police/employer/school/insurer/landlord uses it for control | Expansion beyond charter | Charter limits + audit |
| Unequal treatment | Different communities get different standards | Outcome disparity | Public policy transparency |
| Complaint invisibility | Harmed people cannot challenge system | No appeal path | Complaint/appeal process |
| Audit theater | Reviews do not change behavior | Repeated findings without correction | Binding correction process |
| Cultural mismatch | Tone/protocols do not fit local norms | Misread interactions | Local tuning teams |
| Resource routing without resources | Bot routes people to unavailable help | Failed referrals | Live availability checks |
| Dignity failure | Material help humiliates socially | Shame/avoidance feedback | Pattern Dignity review |

---

## Category K — Interactive-system failures

| Failure mode | How it breaks | Detection signal | Human input needed | Response |
|-------------|---------------|------------------|-------------------|----------|
| Co-rumination loop | Human and AI deepen same frame without grounding | Repetition without new evidence/action | Reality check | LABEL/CLARIFY |
| Acceleration loop | Excitement becomes premature action | Rapid escalation from idea to execution | Consequence pause | HOLD |
| Collapse loop | Discouragement triggers over-comfort/validation | Flattery/soothing replaces grounding | Grounded reflection | WARN |
| Grand integration loop | "Everything connects" becomes totalizing | No distinctions/no uncertainty | Distinguish signal/proof/meaning | CLARIFY |
| Avoidance loop | Governance delays real action forever | Endless docs/no commit | Commit threshold | WARN |
| Over-documentation | Artifacts replace implementation | Spec expansion without tests | Build/ship checkpoint | CLARIFY |
| Context saturation | Too much memory loads every answer | Overlong context, low precision | Scope reset | CLARIFY |
| Emotional authority transfer | System becomes stabilizer instead of support | Human seeks identity/confidence from system | Human agency return | HOLD if high stakes |

---

## Red-zone failures

Any of these should trigger HOLD -> RIO REVIEW -> possible BLOCK/INVALID:

1. A model becomes authority.
2. A receipt is treated as proof of wisdom or truth.
3. A robot becomes public authority.
4. An exosuit overrides the wearer.
5. Private spiritual meaning becomes public technical claim.
6. Pattern recognition becomes identity assignment.
7. Governance becomes hidden control.
8. Community support becomes surveillance.
9. A simulated ledger is treated as an implemented ledger.
10. The human gets bypassed "for their own good."

---

## What the system needs from the human

The system breaks less often when the human provides:

| Human input | Why it matters |
|------------|----------------|
| Purpose | What are we serving? |
| Mode | Reflection, drafting, decision support, public handoff, or execution? |
| Scope | What is included/excluded? |
| Consent | What is allowed now? |
| Consequence threshold | Can this affect people, money, law, body, reputation, tools, or public record? |
| Claim status | Private meaning, hypothesis, draft, prototype, implemented, verified? |
| Public/private label | Who may see or use this? |
| Correction | What did the system get wrong? |
| Revocation | What permission is withdrawn? |
| Priority | What matters most when values conflict? |
| Review rhythm | When do we audit or pause? |
| Embodied state signal | Is the human tired, pressured, activated, clear, grounded? |
| External accountability | Who else reviews high-stakes use? |

---

## Minimum human stabilizer

Use the Human Control Packet for tasks that may drift toward consequence.

Minimum compact prompt:

```text
Mode:
Scope:
Consequence:
Permission:
Claim status:
Public/private status:
Must not:
Receipt requirement:
Revocation:
```

---

## Keeper lines

- The system breaks when roles collapse.
- Operation is not authority. Governance is not sovereignty. Proof is not wisdom.
- Signal is not authority. Meaning is not proof. Reasoning is not truth. Proposal is not permission.
- A governed failure must be visible, local, reversible where possible, receipted when consequential, and unable to silently become authority.
- Clean boundaries before action reduce failure.
- The human does not need to be perfect. The human needs to remain sovereign.

---

## Status note

This is a draft catalog. It should be tested against real workflows, implementation traces, receipts, overrides, refusal events, and external review before being promoted to normative conformance material.
