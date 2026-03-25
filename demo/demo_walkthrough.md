# RIO Protocol — Demo Walkthrough

This document provides a detailed technical walkthrough of the RIO Governed Execution Protocol in action. It traces a single request through all 8 stages of the pipeline, showing the exact data structures, decisions, and artifacts produced at each step.

---

## Scenario

A procurement AI agent wants to transfer $5,000 to pay an invoice. The agent does not call the payment API directly. Instead, it submits the request through RIO.

**Actor:** `procurement_agent` (role: employee)
**Action:** `transfer_funds`
**Target:** `payment_gateway`
**Amount:** $5,000 USD
**Approver:** `manager_bob` (role: manager)

---

## Step 1: Agent Submits Request

The agent calls the RIO client:

```python
result = client.submit(
    action_type="transfer_funds",
    target_resource="payment_gateway",
    parameters={
        "amount": 5000,
        "currency": "USD",
        "recipient": "Vendor Corp",
        "invoice_id": "INV-2026-0042",
        "source_account": "ACCT-7890",
    },
    justification="Invoice INV-2026-0042 due for payment",
)
```

The agent does not have access to the payment gateway. The RIO client wraps the request and submits it to the pipeline.

---

## Step 2: Pipeline Stage 1 — Intake

RIO registers the request and assigns a unique request ID.

```
Request ID:  a8b818ee-979e-42c8-a59c-c6bf84a97b3a
Actor:       procurement_agent
Timestamp:   2026-03-25T18:31:31.976Z
Source IP:   (internal)
Authenticated: True
```

The intake stage validates that the request has the minimum required fields (actor identity, action type, and authentication status). If any field is missing, the request is rejected immediately.

---

## Step 3: Pipeline Stage 2 — Classification

RIO classifies the request based on action type and target resource.

```
Action Type:     transfer_funds
Domain:          payment_gateway
Risk Category:   HIGH
```

The classification stage maps the action to a domain and assigns an initial risk category. Financial actions targeting payment systems are classified as HIGH risk by default.

---

## Step 4: Pipeline Stage 3 — Structured Intent

RIO validates the request parameters and forms a canonical intent.

```
Intent ID:       ec2f58c1-3f13-4d47-8003-ac715ab4bf50
Action Type:     transfer_funds
Target Resource: payment_gateway
Parameters:
  amount:         5000
  currency:       USD
  recipient:      Vendor Corp
  invoice_id:     INV-2026-0042
  source_account: ACCT-7890
Requested By:    procurement_agent
Justification:   Invoice INV-2026-0042 due for payment
```

The intent validation stage checks that all required parameters for `transfer_funds` are present (amount, currency, recipient, source_account). If any required parameter is missing, the request is denied at this stage — no further processing occurs.

The canonical intent is the normalized, validated representation of what the agent wants to do. It is hashed and used as the basis for all downstream decisions.

---

## Step 5: Pipeline Stage 4 — Policy and Risk Evaluation

### Risk Engine

The risk engine computes a composite risk score from four components:

| Component | Value | Explanation |
|-----------|-------|-------------|
| Base risk (action type) | 5.0 | `transfer_funds` has base risk of 5.0 |
| Role modifier | 3.0 | `employee` role adds 3.0 |
| Amount modifier | 5.0 | Amount $5,000 > $1,000 threshold adds 5.0 |
| Target modifier | 1.0 | `payment_gateway` adds 1.0 |
| **Total risk score** | **14.0** | **Risk level: HIGH** |

Risk thresholds:
- LOW: 0–4
- MEDIUM: 5–9
- HIGH: 10–15
- CRITICAL: 16+

### Policy Engine

The policy engine evaluates the intent against the active policy rules:

```
Matched Rule:  POL-001
Rule Name:     Fund transfers over 1000 require approval
Decision:      REQUIRE_APPROVAL
Reason:        Fund transfers over 1000 require approval
```

The policy engine returns `REQUIRE_APPROVAL`, which the pipeline maps to `ESCALATE`. The pipeline halts.

---

## Step 6: Pipeline Halts — Approval Required

RIO creates an approval request and stores the pipeline context:

```
Approval ID:     APR-28FDB6A9
Status:          PENDING
Action:          transfer_funds
Requester:       procurement_agent
Risk Score:      14.0
Risk Level:      HIGH
Policy Rule:     POL-001
```

The agent receives a `PENDING_APPROVAL` result. No execution has occurred. No external system has been contacted. The pipeline is suspended until a human acts.

**What the agent sees:**

```
GovernedResult(status=PENDING_APPROVAL)
  success:         False
  policy_decision: ESCALATE
  approval_id:     APR-28FDB6A9
```

---

## Step 7: Human Manager Approves

Manager Bob reviews the pending approval. The approval interface shows:

- What action is being requested
- Who requested it
- The risk score and level
- The policy rule that triggered escalation
- The justification provided by the agent

Manager Bob approves the request:

```python
approval_result = approval_manager.approve(
    approval_id="APR-28FDB6A9",
    approver_id="manager_bob",
    approver_role="manager",
)
```

RIO verifies:
1. Manager Bob has the `manager` role (authorized to approve)
2. Manager Bob is not the same person as the requester (INV-06: no self-authorization)
3. The amount ($5,000) is within the manager's approval limit ($10,000)
4. The approval request is still PENDING (not already resolved)

All checks pass. The pipeline resumes.

---

## Step 8: Pipeline Stage 5 — Authorization

RIO issues a single-use authorization token:

```
Authorization ID:  AUTH-7a3b2c1d
Intent ID:         ec2f58c1-3f13-4d47-8003-ac715ab4bf50
Approver:          manager_bob
Decision:          ALLOW
Nonce:             (unique, single-use)
Expires:           2026-03-25T18:36:31Z (5 minutes)
```

The authorization token is consumed immediately. It cannot be reused (INV-07: single-use tokens). If the same approval is submitted again, it will be rejected.

---

## Step 9: Pipeline Stage 6 — Execution Gate

The execution gate verifies all preconditions before dispatching the action:

```
Kill switch active:  No
Authorization valid: Yes
Token consumed:      Yes (first use)
Decision:            ALLOW
```

The gate opens. The action is dispatched to the payment adapter.

---

## Step 10: Execution — Payment Adapter

The payment adapter receives the authorized intent and executes the transfer:

```
Adapter:    payment_gateway
Action:     transfer_funds
Amount:     $5,000 USD
Recipient:  Vendor Corp
Invoice:    INV-2026-0042
Status:     completed
```

In the demo, this is a simulated adapter. In production, this would call the actual payment API with the authorized parameters.

---

## Step 11: Pipeline Stage 7 — Receipt Generation

RIO generates a cryptographic receipt containing all decision artifacts:

```
Receipt ID:       f00f63f8-4072-4bdf-980f-71e0487ca2d0
Request ID:       a8b818ee-979e-42c8-a59c-c6bf84a97b3a
Intent ID:        ec2f58c1-3f13-4d47-8003-ac715ab4bf50
Authorization ID: AUTH-7a3b2c1d
Decision:         ALLOW
Execution Status: EXECUTED
Risk Score:       14.0
Risk Level:       HIGH
Policy Rule:      POL-001
Intent Hash:      SHA-256(canonical intent)
Decision Hash:    SHA-256(decision artifacts)
Execution Hash:   SHA-256(execution result)
Receipt Hash:     SHA-256(all fields above)
Signature:        ECDSA-secp256k1(receipt_hash, private_key)
Timestamp:        2026-03-25T18:31:31.979Z
```

The receipt is a self-contained proof of what was requested, what was decided, and what happened. It can be independently verified using the public key.

---

## Step 12: Pipeline Stage 8 — Ledger Entry

RIO appends a ledger entry to the hash chain:

```
Ledger Entry ID:      5ad02f54-48d4-4419-baaa-66b956564c59
Receipt ID:           f00f63f8-4072-4bdf-980f-71e0487ca2d0
Receipt Hash:         fdd37de862f57dae...
Previous Ledger Hash: 4cfbd42413f7842f...  (from entry #1)
Ledger Hash:          ba5ed9b3d406df69...
Chain Length:         2
Timestamp:            2026-03-25T18:31:31.982Z
```

The ledger entry links to the previous entry via `previous_ledger_hash`, forming a tamper-evident chain. If any past entry is modified, all subsequent hashes become invalid.

---

## Step 13: Corpus Record

RIO writes a governed corpus record for future replay and learning:

```
Corpus ID:        CORP-A1B2C3D4
Request ID:       a8b818ee-979e-42c8-a59c-c6bf84a97b3a
Action Type:      transfer_funds
Target Resource:  payment_gateway
Policy Decision:  ALLOW (after approval)
Risk Score:       14.0
Risk Level:       HIGH
Execution Status: EXECUTED
Policy Rule:      POL-001
Policy Version:   1.0.0
```

The corpus record captures the complete decision context. It can be replayed through the simulation engine to test how different policies or roles would have affected the outcome.

---

## Step 14: Replay Simulation

The agent replays the decision under a different role:

```python
sim = client.replay(record, override_role="intern")
```

The simulation engine re-evaluates the same action as if an intern had submitted it:

```
Original:
  Decision:  ALLOW
  Risk:      5.0 (MEDIUM)
  Role:      employee

Simulated:
  Decision:  ALLOW (or DENY, depending on policy)
  Risk:      8.0 (MEDIUM)
  Role:      intern
```

The simulation does not execute any action, generate any receipt, or modify the ledger. It only re-evaluates the policy and risk decision. This is how organizations test policy changes before deploying them to production.

---

## Complete Flow Diagram

```
procurement_agent
       │
       ▼
┌─────────────┐
│   RIO       │
│   Client    │
└──────┬──────┘
       │ submit()
       ▼
┌─────────────────────────────────────────────────────┐
│                  RIO PIPELINE                       │
│                                                     │
│  Stage 1: Intake ──────────────► Request registered │
│  Stage 2: Classification ──────► HIGH risk          │
│  Stage 3: Structured Intent ───► Canonical intent   │
│  Stage 4: Policy & Risk ──────► ESCALATE (POL-001)  │
│                                                     │
│  ── PIPELINE HALTED ── Approval Required ──         │
│                                                     │
│  [Human Manager Approves]                           │
│                                                     │
│  Stage 5: Authorization ──────► Token issued        │
│  Stage 6: Execution Gate ─────► Gate opens          │
│  Stage 7: Receipt ────────────► Signed receipt      │
│  Stage 8: Ledger ─────────────► Hash chain entry    │
│                                                     │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐     ┌──────────┐
│  Payment    │     │   Governed   │     │  Ledger  │
│  Adapter    │     │   Corpus     │     │  (chain) │
│  (execute)  │     │  (learning)  │     │  (audit) │
└─────────────┘     └──────────────┘     └──────────┘
```

---

## Verification

After the demo, verify the ledger integrity:

```bash
python -m runtime.verify_ledger
```

Expected output:

```
Ledger verification: PASS
Entries verified: 2
Chain integrity: VALID
```

---

## What This Proves

1. **No direct action.** The agent never called the payment API directly. Every action went through the governed pipeline.

2. **Policy enforcement.** The policy engine correctly identified the transfer as requiring approval and halted the pipeline.

3. **Human-in-the-loop.** A human manager reviewed and approved the action before execution could proceed.

4. **Cryptographic audit.** Every decision produced a signed receipt and a hash-chained ledger entry.

5. **Replay without side effects.** Past decisions can be replayed under different conditions without affecting any real system.

6. **Tamper evidence.** The ledger can be independently verified. Any modification to past entries breaks the hash chain.
