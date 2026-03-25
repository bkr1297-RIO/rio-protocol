# Governed Agent Example

This example demonstrates how an AI agent uses the RIO Protocol instead of acting directly on external systems. The agent submits every action through the governed execution pipeline, which evaluates policy, computes risk, obtains authorization, and produces cryptographic receipts.

## What This Shows

The example runs a simulated procurement agent that performs four operations:

1. **Low-risk action (read data)** — The agent requests quarterly report data. RIO evaluates the action as low-risk, auto-approves it, executes it, and generates a receipt and ledger entry.

2. **High-risk action (transfer funds)** — The agent requests a $48,250 payment to a vendor. RIO evaluates the action as high-risk and escalates it for human approval. No funds are transferred until a human approves.

3. **Human approval** — A manager reviews and approves the transfer. RIO resumes the pipeline: authorization, execution, receipt, and ledger entry are all completed.

4. **Replay simulation** — The agent retrieves the transfer decision from the governed corpus and replays it under a different role (intern) to see how policy would have responded differently.

## Files

| File | Purpose |
|------|---------|
| `agent.py` | The governed agent — demonstrates the full workflow |
| `rio_client.py` | RIO client library — wraps the pipeline for agent use |
| `README.md` | This file |

## Running the Example

From the project root:

```bash
python examples/governed_agent/agent.py
```

Expected output shows each step with status, receipt IDs, risk scores, and ledger references.

## Architecture

```
┌──────────────┐     ┌──────────────────────────────────────┐
│  AI Agent    │     │  RIO Governed Execution Pipeline     │
│              │     │                                      │
│  agent.py    │────>│  Intake → Classification → Intent    │
│              │     │  → Policy/Risk → Authorization       │
│              │     │  → Execution Gate → Receipt → Ledger │
│              │<────│                                      │
└──────────────┘     └──────────────────────────────────────┘
       │                          │
       │                          ▼
       │              ┌──────────────────────┐
       │              │  External Systems    │
       │              │  (Payment, Email,    │
       │              │   Database, etc.)    │
       │              └──────────────────────┘
       │
       ▼
┌──────────────┐
│  Corpus &    │
│  Replay      │
│  (Learning)  │
└──────────────┘
```

The agent communicates only with RIO. RIO communicates with external systems through governed adapters. The agent never has direct access to payment APIs, databases, or other external resources.

## Key Principles

**No direct action.** The agent never calls external APIs or modifies external systems directly. Every action goes through `client.submit()`.

**Automatic escalation.** High-risk actions are automatically escalated for human approval. The agent cannot bypass this — it is enforced at the protocol level.

**Full audit trail.** Every action, whether approved, denied, or escalated, produces a cryptographic receipt and a tamper-evident ledger entry.

**Replay without side effects.** The agent can replay past decisions through the simulation engine to understand how policy changes would affect outcomes, without triggering any real execution.

## Integrating Your Own Agent

To use RIO in your own agent:

```python
from rio_client import RIOClient

client = RIOClient(
    agent_id="your_agent_name",
    default_approver_id="manager_id",
)

# Submit an action through RIO
result = client.submit(
    action_type="send_email",
    parameters={"to": "user@example.com", "subject": "Report", "body": "..."},
    justification="Automated weekly report delivery",
)

# Check the result
if result.status == "PENDING_APPROVAL":
    # Wait for human approval
    result = client.wait_for_approval(result.approval_id)
elif result.success:
    print(f"Executed. Receipt: {result.receipt_id}")
else:
    print(f"Denied: {result.error}")
```

The `RIOClient` handles all pipeline interaction. Your agent code stays clean and focused on its domain logic.
