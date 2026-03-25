# Simulation and Learning

**RIO — Governed Corpus, Replay Engine, and Policy Improvement**

---

## Overview

The learning layer provides the data infrastructure and analytical tools for continuous governance improvement. It operates on a strict safety principle: **learning informs, but never modifies, live policy.** The layer collects structured decision records, enables replay of past decisions under alternate rules, and surfaces recommendations that must go through the standard governance workflow (draft, approve, activate) before taking effect.

---

## Governed Corpus

The governed corpus (`runtime/corpus/corpus_store.py`) is the system's structured decision history. Every completed pipeline run — whether the action was executed, denied, blocked, or pending — produces a corpus record that is appended to `runtime/data/governed_corpus.jsonl`.

### Corpus Record Structure

Each corpus record contains the full context of a single pipeline decision:

| Section | Fields | Purpose |
|---------|--------|---------|
| **Request** | `request_id`, `user_id`, `action`, `parameters`, `timestamp` | What was requested and by whom |
| **Intent** | `intent_hash`, `action_type`, `validated_parameters` | The canonical form of the request |
| **Policy** | `policy_decision`, `matching_rule`, `rule_id` | Which policy rule matched and what it decided |
| **Risk** | `risk_score`, `risk_level`, `score_components` | How the risk score was computed |
| **Authorization** | `authorization_id`, `authorizer_id`, `nonce`, `expires_at` | Who authorized and under what constraints |
| **Execution** | `execution_status`, `adapter_used`, `external_reference` | What happened when the action was dispatched |
| **Receipt** | `receipt_id`, `signature` | Cryptographic proof reference |
| **Ledger** | `ledger_entry_id`, `content_hash` | Audit chain reference |

### Corpus Properties

The corpus is **append-only**. Records are never modified or deleted. This ensures that the decision history is a faithful reflection of what actually happened, not a retroactive reconstruction.

The corpus is **separate from the ledger**. The ledger is the tamper-evident audit chain. The corpus is the analytical dataset. They reference the same events but serve different purposes. The ledger proves what happened. The corpus enables learning from what happened.

The corpus is **read-only with respect to the runtime**. Writing a corpus record never triggers execution, modifies system state, or affects any live pipeline. Corpus writes are the final, passive step after all active processing is complete.

---

## Replay Engine

The replay engine (`runtime/corpus/replay_engine.py`) re-evaluates past corpus records through current or alternate policy and risk settings **without executing real actions**. It is a pure evaluation engine with strict safety guarantees.

### Safety Guarantees

The replay engine enforces four invariants:

1. **Never calls adapters, connectors, or action handlers.** No real-world side effects occur during replay.
2. **Never writes execution receipts as real execution.** Replay results are clearly marked as simulated.
3. **Never appends simulated runs to the main ledger.** The audit chain is not contaminated with hypothetical data.
4. **Optionally writes simulation summaries to a separate file** (`runtime/data/simulations.jsonl`) for analysis.

### Replay Modes

The replay engine supports several modes of analysis:

**Single-record replay.** Re-evaluate a specific past decision under current policy and risk settings. This answers the question: "If this request came in today, would the outcome be different?"

**Batch replay.** Re-evaluate a range of past decisions (e.g., all decisions from the past week, all decisions involving a specific action type). This answers the question: "How would a policy change affect a class of past decisions?"

**What-if replay.** Re-evaluate past decisions under a proposed (not yet activated) policy or risk model. This answers the question: "If we activate this draft, how many past requests would have been handled differently?"

### Replay Output

Each replay produces a comparison record:

| Field | Description |
|-------|-------------|
| `original_decision` | The policy decision that was actually made |
| `replayed_decision` | The policy decision under the new rules |
| `original_risk_score` | The risk score that was actually computed |
| `replayed_risk_score` | The risk score under the new thresholds |
| `changed` | Boolean: whether the outcome would have been different |
| `change_description` | Human-readable description of the difference |

---

## Simulation API

The simulation API (`runtime/corpus/simulation_api.py`) exposes replay functionality through REST endpoints, making it accessible from the dashboard and external tools.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/simulation/replay` | POST | Replay a single corpus record under specified rules |
| `/api/simulation/batch` | POST | Replay a batch of records with filtering criteria |
| `/api/simulation/what-if` | POST | Replay against a proposed (draft) policy version |
| `/api/simulation/summary` | GET | Retrieve simulation history and summaries |

The simulation API is available to managers and admins. It does not require the same approval workflow as policy activation because simulations have no effect on the live system.

---

## Policy Improvement Loop

The governance learning module (`runtime/governance_learning.py`) analyzes the governed corpus to identify patterns and recommend policy adjustments. The improvement loop follows a structured process:

### Step 1: Pattern Detection

The learning module scans the corpus for patterns that may indicate policy gaps or inefficiencies:

**Frequent escalations.** If a specific action type is consistently escalated to human approval but always approved, the policy may be overly conservative for that action. A rule change could auto-allow it under certain conditions.

**Frequent denials followed by re-requests.** If users repeatedly submit requests that are denied and then re-submit with minor modifications, the denial rule may need refinement or the users may need clearer guidance.

**Risk score clustering.** If many requests cluster just below or just above a risk threshold, the threshold may need adjustment to better separate routine from exceptional requests.

**Role-action mismatches.** If a role frequently requests actions that are always denied for that role, the role's permissions may need review.

### Step 2: Recommendation Generation

Based on detected patterns, the learning module generates structured recommendations:

| Recommendation Type | Example |
|--------------------|---------|
| **Threshold adjustment** | "Reduce HIGH risk threshold from 8 to 7 for `delete_data` actions — 12 of 15 recent escalations were approved" |
| **Rule addition** | "Add auto-allow rule for `send_email` by employees to internal domains — 100% approval rate over 30 days" |
| **Rule modification** | "Increase amount threshold for `transfer_funds` REQUIRE_APPROVAL from $10,000 to $25,000 — all transfers between $10K-$25K were approved" |
| **Role review** | "Intern role has 47 denied `transfer_funds` requests — consider explicit guidance or role reassignment" |

### Step 3: Human Review

Recommendations are surfaced through the dashboard. They are **never automatically applied**. An admin must review each recommendation, decide whether to act on it, and if so, create a policy or risk model draft through the standard governance workflow.

### Step 4: Governed Change

If the admin decides to act on a recommendation, the change follows the full governance workflow: propose draft, approve, activate, with receipt and ledger entry at each step. The recommendation ID is included in the change record for traceability.

---

## Safety Architecture

The learning layer's safety architecture is designed around a single principle: **observation must never become action without human governance.**

```
Governed Corpus ──▶ Replay Engine ──▶ Recommendations
       │                                      │
       │                                      ▼
       │                              Dashboard Display
       │                                      │
       │                              Human Admin Review
       │                                      │
       │                              ┌───────┴───────┐
       │                              ▼               ▼
       │                           Accept          Reject
       │                              │
       │                              ▼
       │                     Governance Workflow
       │                    (Draft → Approve → Activate)
       │                              │
       │                              ▼
       │                     Ledger + Receipt
       │                              │
       └──────────────────────────────┘
                  (New decisions feed back into corpus)
```

The corpus feeds the replay engine. The replay engine produces recommendations. Recommendations are displayed to humans. Humans decide whether to act. Actions follow the governance workflow. The governance workflow produces ledger entries. New decisions feed back into the corpus. The loop is closed, but every transition from observation to action passes through human governance.

---

## References

| Specification | Location |
|--------------|----------|
| Governed Execution Protocol | `spec/governed_execution_protocol.md` |
| Corpus Store Implementation | `runtime/corpus/corpus_store.py` |
| Replay Engine Implementation | `runtime/corpus/replay_engine.py` |
| Simulation API | `runtime/corpus/simulation_api.py` |
| Governance Learning | `runtime/governance_learning.py` |
| Corpus Data | `runtime/data/governed_corpus.jsonl` |
| Simulation Data | `runtime/data/simulations.jsonl` |
