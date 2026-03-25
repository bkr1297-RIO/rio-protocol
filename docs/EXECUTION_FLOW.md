# Execution Flow

**RIO — Governed Execution Pipeline**

---

## Overview

Every action request in RIO traverses a mandatory eight-stage pipeline. No stage can be skipped. The pipeline is defined in `runtime/pipeline.py` and enforces all eight protocol invariants (INV-01 through INV-08) on every run.

The pipeline produces three possible terminal outcomes:

| Outcome | When It Occurs | Artifacts Produced |
|---------|---------------|-------------------|
| **Executed** | Policy allows, authorization valid, execution succeeds | Receipt + Ledger entry + Corpus record |
| **Denied** | Policy denies, or human approver denies | Denial receipt + Ledger entry + Corpus record |
| **Pending Approval** | Policy escalates to human approval | Approval request created; pipeline resumes when human acts |

A fourth outcome, **Blocked**, occurs when the kill switch is engaged. Blocked requests produce a receipt and ledger entry with the kill switch event recorded.

---

## Stage 1: Intake

**Module:** `runtime/intake.py`

The intake stage receives the raw action request and performs initial validation. It assigns a unique request ID, records the timestamp, and verifies that the request contains the minimum required fields: `user_id`, `action`, and `parameters`.

The intake stage also verifies that the requesting user exists in the IAM registry and is active. Requests from unknown or inactive users are rejected immediately.

**Input:** Raw request dictionary with `user_id`, `action`, `parameters`.

**Output:** A `Request` object with a unique ID, validated fields, and the requester's role resolved from the IAM system.

---

## Stage 2: Classification

**Module:** `runtime/classification.py`

The classification stage determines the action type and assigns an initial risk category. It maps the action string (e.g., `transfer_funds`, `send_email`, `delete_data`) to a risk category (LOW, MEDIUM, HIGH, CRITICAL) based on the action type and the requester's role.

Classification does not make policy decisions. It provides the inputs that the policy and risk engines need to make decisions.

**Input:** Validated `Request` object.

**Output:** Action type classification and initial risk category attached to the request.

---

## Stage 3: Structured Intent

**Modules:** `runtime/intent_validation.py`, `runtime/structured_intent.py`

This stage has two sub-steps. First, intent validation checks that the request contains all fields required by the intent requirements matrix (`runtime/policy/intent_requirements.py`). Different action types require different fields — for example, `transfer_funds` requires `amount`, `recipient`, and `currency`, while `send_email` requires `to`, `subject`, and `body`.

Second, the structured intent builder forms a canonical intent object. The intent object contains the action type, all validated parameters, and a deterministic SHA-256 hash of the canonicalized (minified, sorted JSON) content. This hash is used throughout the rest of the pipeline to bind all subsequent records to the original intent.

**Input:** Classified request with action type.

**Output:** `Intent` object with canonical hash, validated parameters, and action metadata.

---

## Stage 4: Policy and Risk

**Module:** `runtime/policy_risk.py`

This stage delegates to two engines:

**Policy Engine** (`runtime/policy/policy_engine.py`) evaluates the intent against the active policy rules loaded from `runtime/policy/policy_rules.json`. Rules are evaluated in priority order. Each rule specifies a role, an action, an optional condition, and a decision (ALLOW, DENY, or REQUIRE_APPROVAL). The first matching rule determines the policy decision. If no rule matches, the default decision is ALLOW.

**Risk Engine** (`runtime/policy/risk_engine.py`) computes a numeric risk score by summing four components: base risk by action type, role risk of the requester, amount risk (for financial actions), and system target risk. The score is mapped to a risk level (LOW, MEDIUM, HIGH) based on configurable thresholds.

The combined output is a policy decision and a risk assessment. If the policy decision is REQUIRE_APPROVAL and the risk level is HIGH, the request is escalated to the approval queue.

**Input:** `Intent` object with canonical hash.

**Output:** Policy decision (ALLOW, DENY, ESCALATE), risk score, risk level.

---

## Stage 5: Authorization

**Module:** `runtime/authorization.py`

The authorization stage acts on the policy decision:

**ALLOW:** An authorization token is issued. The token contains the intent hash, the authorizer identity, a unique nonce, an expiration timestamp (default: 300 seconds), and an ECDSA signature. The token is a single-use credential that the execution gate will consume.

**DENY:** No authorization token is issued. The pipeline proceeds directly to receipt generation with a denial outcome.

**ESCALATE:** The request enters the approval queue (`runtime/approvals/approval_queue.py`). The pipeline halts with a PENDING_APPROVAL status. When a human approver (manager or admin) acts on the request, the approval manager either generates an authorization token (approve) or a denial receipt (deny), and the pipeline resumes.

A critical invariant enforced at this stage is **INV-06: No Self-Authorization**. The authorizer must be a different identity than the requester. This prevents any single actor from both requesting and approving their own actions.

**Input:** Policy decision and risk assessment.

**Output:** Authorization token (for ALLOW/APPROVE), or denial status (for DENY), or pending status (for ESCALATE).

---

## Stage 6: Execution Gate

**Module:** `runtime/execution_gate.py`

The execution gate is the final checkpoint before real-world action. It performs four checks in sequence:

1. **Kill switch check.** If the global kill switch is engaged, the request is blocked regardless of authorization status. The blocked event is recorded.

2. **Authorization verification.** The gate verifies the authorization token's ECDSA signature to ensure it has not been tampered with.

3. **Nonce consumption.** The gate checks the nonce registry. If the nonce has already been consumed, the request is rejected (replay prevention). If the nonce is fresh, it is marked as consumed.

4. **Expiration check.** The gate verifies that the authorization token has not expired.

If all checks pass, the gate resolves the appropriate adapter from the adapter registry and dispatches the intent for execution.

**Input:** Authorization token and canonical intent.

**Output:** `ExecutionResult` containing the adapter's response, external references, and execution status.

---

## Stage 7: Receipt

**Module:** `runtime/receipt.py`

The receipt stage generates a cryptographic proof of the pipeline outcome. Every outcome — executed, denied, blocked, or errored — produces a receipt.

Each receipt contains:

| Field | Description |
|-------|-------------|
| `receipt_id` | Unique identifier |
| `intent_hash` | SHA-256 hash of the canonical intent |
| `decision_hash` | SHA-256 hash of the policy decision |
| `execution_hash` | SHA-256 hash of the execution result (or denial/block reason) |
| `timestamp` | ISO 8601 timestamp |
| `signature` | ECDSA-secp256k1 signature over the receipt content |
| `policy_decision` | The policy engine's decision (ALLOW, DENY, ESCALATE) |
| `risk_level` | The risk engine's assessment (LOW, MEDIUM, HIGH) |

The receipt is signed with the system's RSA-2048 private key stored at `runtime/keys/private_key.pem`.

**Input:** Pipeline outcome (intent, decision, execution result or denial reason).

**Output:** Signed `Receipt` object.

---

## Stage 8: Ledger

**Module:** `runtime/ledger.py`

The ledger stage appends a hash-linked entry to the tamper-evident audit ledger at `runtime/data/ledger.jsonl`.

Each ledger entry contains:

| Field | Description |
|-------|-------------|
| `entry_id` | Unique identifier |
| `receipt_id` | Reference to the associated receipt |
| `content_hash` | SHA-256 hash of the entry's own content |
| `previous_hash` | Hash of the previous ledger entry (forms the chain) |
| `timestamp` | ISO 8601 timestamp |
| `event_type` | Type of event (EXECUTION, DENIAL, KILL_SWITCH, GOVERNANCE_CHANGE) |
| `actor_id` | The user who initiated the action |

The hash chain ensures that any modification or deletion of a ledger entry is detectable. The verification system (`runtime/verify_ledger.py`) can validate the entire chain at any time.

**Input:** Signed receipt.

**Output:** `LedgerEntry` appended to the chain.

---

## Stage 9: Governance Learning (Asynchronous)

**Module:** `runtime/governance_learning.py`

After the pipeline completes, a corpus record is written to `runtime/data/governed_corpus.jsonl` containing the full decision context. Governance learning operates asynchronously — it reads the corpus to identify patterns, anomalies, and potential policy improvements, but it never modifies live policy directly. Any recommended changes must go through the standard governance workflow (draft, approve, activate).

---

## Invariant Verification

At the end of every pipeline run, the system verifies four protocol invariants:

| Invariant | Check |
|-----------|-------|
| **INV-01: Completeness** | Every request has traversed all required stages |
| **INV-02: Receipt Completeness** | A receipt exists for every completed request |
| **INV-03: Ledger Completeness** | A ledger entry exists for every receipt |
| **INV-04: Hash Chain** | The ledger hash chain is unbroken |

If any invariant is violated, the violation is logged and the pipeline result is flagged. Invariant violations do not silently pass.

---

## Pipeline Diagram

```
Request ──▶ Intake ──▶ Classify ──▶ Intent ──▶ Policy/Risk
                                                    │
                                          ┌─────────┼─────────┐
                                          ▼         ▼         ▼
                                        ALLOW    ESCALATE    DENY
                                          │         │         │
                                          │    Approval Queue  │
                                          │    ┌────┴────┐     │
                                          │    ▼         ▼     │
                                          │  Approve    Deny───┤
                                          │    │               │
                                          ▼    ▼               ▼
                                      Exec Gate          Denial Path
                                          │                    │
                                          ▼                    │
                                       Adapter                 │
                                          │                    │
                                          ▼                    ▼
                                       Receipt ◀──────── Receipt
                                          │                    │
                                          ▼                    ▼
                                       Ledger ◀──────── Ledger
                                          │                    │
                                          ▼                    ▼
                                       Corpus ◀──────── Corpus
```

---

## References

| Specification | Location |
|--------------|----------|
| Governed Execution Protocol | `spec/governed_execution_protocol.md` |
| Runtime Flow | `spec/runtime_flow.md` |
| Protocol Invariants | `spec/protocol_invariants.md` |
| System Invariants | `spec/system_invariants.md` |
| Pipeline Implementation | `runtime/pipeline.py` |
