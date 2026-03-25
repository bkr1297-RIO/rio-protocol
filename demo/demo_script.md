# RIO Protocol — Demo Script

This script is designed for a 5–7 minute demonstration of the RIO Governed Execution Protocol. It walks through the complete lifecycle of a governed action: from request submission through policy evaluation, risk scoring, human approval, execution, receipt generation, ledger recording, and replay simulation.

The demo uses the built-in test harness and governed agent example. No external services are required.

---

## Prerequisites

Before recording or presenting, ensure the system is initialized:

```bash
cd rio-protocol
python scripts/init_rio.py
```

---

## Scene 1: Introduction (30 seconds)

**Narrator:**

> "This is RIO — the Runtime Intelligence Orchestration protocol. RIO sits between AI agents and the actions they want to perform. No action happens without policy evaluation, risk scoring, authorization, and a cryptographic audit trail. Let me show you how it works."

**Screen:** Show the README architecture diagram or the system overview page.

---

## Scene 2: Submit a Request (60 seconds)

**Narrator:**

> "An AI procurement agent wants to read a quarterly report. It doesn't access the report server directly — it submits a request through RIO."

**Action:** Run the governed agent example.

```bash
python examples/governed_agent/agent.py
```

**Screen:** Show the terminal output for Step 1.

**Narrator:**

> "RIO evaluates the request through its 8-stage pipeline. The policy engine classifies this as a low-risk read operation. Risk score: 5.0 out of 20. The policy allows it. RIO authorizes and executes the action, then generates a cryptographic receipt and appends a ledger entry. The agent gets its data — and there's a complete audit trail."

**Highlight in output:**
- `policy_decision: ALLOW`
- `risk_score: 5.0 (MEDIUM)`
- `receipt_id: ...`
- `ledger_entry_id: ...`

---

## Scene 3: High-Risk Action — Escalation (60 seconds)

**Narrator:**

> "Now the agent wants to transfer $5,000 to a vendor. This is a financial action — RIO treats it differently."

**Screen:** Show Step 2 output.

**Narrator:**

> "The policy engine matches rule POL-001: fund transfers over $1,000 require human approval. RIO halts the pipeline and creates an approval request. No money has moved. No external system was called. The agent is waiting."

**Highlight in output:**
- `status: PENDING_APPROVAL`
- `policy_decision: ESCALATE`
- `approval_id: APR-...`

**Key point to emphasize:**

> "This is the core principle: the agent cannot bypass governance. The protocol enforces it structurally — not through a prompt, not through a guideline, but through the execution pipeline itself."

---

## Scene 4: Human Approval (60 seconds)

**Narrator:**

> "A human manager reviews the request. They see the action type, the amount, the risk score, and the justification. They approve it."

**Screen:** Show Step 3 output.

**Narrator:**

> "RIO resumes the pipeline from where it paused. It authorizes the action, executes it through the payment adapter, generates a receipt, and appends a ledger entry. The transfer is complete — and every step is recorded."

**Highlight in output:**
- `status: APPROVED`
- `receipt_id: ...`
- `ledger_entry_id: ...`

---

## Scene 5: Replay Simulation (60 seconds)

**Narrator:**

> "Now the agent replays a past decision through the simulation engine. What would have happened if an intern had submitted this request instead of a regular employee?"

**Screen:** Show Step 4 output.

**Narrator:**

> "The simulation re-evaluates the same action under a different role. The risk score changes — interns carry higher role risk. The policy engine may produce a different decision. This is how organizations test policy changes before deploying them."

**Highlight in output:**
- `Original decision: ALLOW`
- `Simulated decision: ALLOW` (or different)
- `Original risk: 5.0`
- `Simulated risk: 8.0`

**Key point:**

> "The simulation never touches any real system. It only re-evaluates the policy and risk decision. No receipts, no ledger entries, no side effects."

---

## Scene 6: Ledger Verification (60 seconds)

**Narrator:**

> "Every action in RIO produces a cryptographic receipt and a ledger entry. The ledger is a hash chain — each entry links to the previous one. If anyone modifies a past entry, the chain breaks."

**Action:** Run the ledger verification tool.

```bash
python -m runtime.verify_ledger
```

**Screen:** Show the verification output.

**Narrator:**

> "The verifier walks the entire chain, checking hashes, signatures, and timestamps. If any entry has been tampered with, the verification fails and identifies exactly which entry was modified."

**Highlight:**
- `Ledger verification: PASS`
- Chain length
- Hash chain integrity

---

## Scene 7: Dashboard (60 seconds)

**Narrator:**

> "The dashboard provides a real-time view of the system. You can see the pipeline status, recent requests, approval queue, ledger entries, and risk distribution."

**Action:** Start the dashboard.

```bash
python scripts/run_all.py
```

**Screen:** Open browser to `http://localhost:8050`.

**Show:**
1. Pipeline overview — recent requests with status (EXECUTED, DENIED, PENDING)
2. Approval queue — pending requests awaiting human action
3. Ledger view — hash chain with receipt references
4. Risk distribution — chart showing risk scores across actions

---

## Scene 8: Summary (30 seconds)

**Narrator:**

> "That's RIO. Every AI action goes through an 8-stage governed pipeline. Policy and risk are evaluated before execution. High-risk actions require human approval. Every decision produces a cryptographic receipt and a tamper-evident ledger entry. Past decisions can be replayed through simulation to test policy changes. The system is open source, runnable locally, and designed for enterprise governance of AI agents."

**Screen:** Show the summary output from the governed agent.

---

## Total Runtime

| Scene | Duration |
|-------|----------|
| Introduction | 30s |
| Submit Request | 60s |
| Escalation | 60s |
| Human Approval | 60s |
| Replay Simulation | 60s |
| Ledger Verification | 60s |
| Dashboard | 60s |
| Summary | 30s |
| **Total** | **~7 minutes** |

---

## Commands Used

```bash
# Initialize the system
python scripts/init_rio.py

# Run the governed agent demo
python examples/governed_agent/agent.py

# Verify the ledger
python -m runtime.verify_ledger

# Start the dashboard
python scripts/run_all.py

# Run the full test suite
python -m runtime.test_harness
```

---

## Notes for Recording

- Run each command in a clean terminal with a dark background and readable font size (16pt+).
- Pause briefly after each command to let the output render before narrating.
- The governed agent example produces both log-level output and user-facing output. For the video, consider piping through a filter to show only the user-facing lines, or use the full output to show the pipeline stages in real time.
- The dashboard requires the system to be running. Start it before switching to the browser.
- All data is local. No external APIs are called. The demo works entirely offline after initialization.
