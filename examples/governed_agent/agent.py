#!/usr/bin/env python3
"""
Example Governed Agent — Procurement Bot

This script demonstrates how an AI agent uses the RIO Protocol instead of
acting directly on external systems. The agent never calls a payment API,
sends an email, or modifies a database on its own. Every action goes through
the RIO governed execution pipeline.

Flow:
    Agent → Intent → RIO → Policy/Risk → Approval → Execution → Receipt → Ledger → Result → Agent continues

Usage:
    cd rio-protocol
    python examples/governed_agent/agent.py

What this demo shows:
    1. Agent submits a low-risk action (read data) — auto-approved and executed
    2. Agent submits a high-risk action (transfer funds) — escalated for human approval
    3. Human manager approves the escalated action
    4. Agent retrieves corpus records and replays a decision under a different role
    5. Every action produces receipts and ledger entries — nothing is silent
"""

from __future__ import annotations

import logging
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from rio_client import RIOClient
from runtime.state import SystemState
from runtime import ledger
from runtime.approvals import approval_manager
from runtime.iam import permissions as iam_permissions, users as iam_users
from runtime.corpus.corpus_store import clear_corpus

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("governed_agent")


def divider(title: str) -> None:
    """Print a section divider."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def main():
    """Run the governed agent demonstration."""

    # ------------------------------------------------------------------
    # Initialize clean state
    # ------------------------------------------------------------------
    divider("GOVERNED AGENT DEMO — RIO Protocol")
    print("This demo shows an AI agent that uses RIO for every action.")
    print("The agent never acts directly — every action goes through the pipeline.")
    print()

    ledger.reset()
    approval_manager.reset()
    iam_permissions.reset()
    iam_users.reset()
    clear_corpus()

    state = SystemState()

    # Create the RIO client — this is what the agent uses
    client = RIOClient(
        agent_id="procurement_agent",
        default_approver_id="manager_bob",
        state=state,
    )

    # ------------------------------------------------------------------
    # Step 1: Low-risk action — Read data (auto-approved)
    # ------------------------------------------------------------------
    divider("STEP 1: Low-Risk Action — Read Quarterly Report")
    print("The agent wants to read a quarterly report.")
    print("This is a low-risk action — RIO will auto-approve and execute it.")
    print()

    result = client.submit(
        action_type="read_data",
        target_resource="report_server",
        parameters={
            "dataset": "quarterly_reports",
            "report_id": "RPT-2026-Q1",
        },
        justification="Agent needs Q1 revenue data for procurement analysis",
    )

    print(result)
    print()
    if result.success:
        print("✓ Action executed. Receipt and ledger entry created.")
        print(f"  Receipt: {result.receipt_id}")
        print(f"  Ledger:  {result.ledger_entry_id}")
    else:
        print(f"✗ Action failed: {result.error or result.status}")

    # ------------------------------------------------------------------
    # Step 2: High-risk action — Transfer funds (requires approval)
    # ------------------------------------------------------------------
    divider("STEP 2: High-Risk Action — Transfer $5,000 to Vendor")
    print("The agent wants to transfer funds to pay an invoice.")
    print("This is a high-risk action — RIO will escalate for human approval.")
    print()

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
        justification="Invoice INV-2026-0042 due for payment per procurement policy",
    )

    print(result)
    print()

    if result.status == "PENDING_APPROVAL":
        print("✓ Action escalated to human approver (as expected).")
        print(f"  Approval ID: {result.approval_id}")
        print(f"  Risk Score:  {result.risk_score} ({result.risk_level})")
        print()
        print("  The agent cannot proceed until a human approves this action.")
        print("  No funds have been transferred. No external system was called.")

        # ------------------------------------------------------------------
        # Step 3: Human manager approves
        # ------------------------------------------------------------------
        divider("STEP 3: Human Manager Approves the Transfer")
        print("Manager Bob reviews the request and approves it.")
        print("RIO resumes the pipeline: Authorization → Execution → Receipt → Ledger")
        print()

        approval_result = client.wait_for_approval(
            approval_id=result.approval_id,
            approver_id="manager_bob",
            approver_role="manager",
        )

        print(approval_result)
        print()
        if approval_result.success:
            print("✓ Transfer executed after human approval.")
            print(f"  Receipt: {approval_result.receipt_id}")
            print(f"  Ledger:  {approval_result.ledger_entry_id}")
        else:
            print(f"✗ Approval failed: {approval_result.error}")
    elif result.success:
        print("✓ Action auto-approved and executed (risk was below threshold).")
    else:
        print(f"✗ Action denied: {result.error or result.status}")

    # ------------------------------------------------------------------
    # Step 4: Replay — What would have happened under a different role?
    # ------------------------------------------------------------------
    divider("STEP 4: Replay Simulation — Different Role")
    print("The agent retrieves corpus records and replays the transfer decision")
    print("to see what would happen if an intern had requested it instead.")
    print()

    records = client.get_corpus_records(count=5)
    if records:
        # Use the first available corpus record for replay
        record = records[0]
        print(f"  Replaying record: action={record.action_type}, original_decision={record.policy_decision}")
        print()

        sim = client.replay(record, override_role="intern")
        print(f"  Original decision:  {sim.original_decision}")
        print(f"  Original risk:      {sim.original_risk_score} ({sim.original_risk_level})")
        print(f"  Simulated decision: {sim.simulated_decision}")
        print(f"  Simulated risk:     {sim.simulated_risk_score} ({sim.simulated_risk_level})")
        print(f"  Decision changed:   {sim.decision_changed}")
        print()
        if sim.decision_changed:
            print("✓ Policy produced a different decision for an intern.")
        else:
            print("  Policy decision would have been the same (both roles allowed for this action).")
    else:
        print("  No corpus records available for replay.")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    divider("SUMMARY")
    print("The governed agent completed its workflow:")
    print()
    print("  1. Read data      → Auto-approved → Executed → Receipt + Ledger")
    print("  2. Transfer funds  → Escalated → Human approved → Executed → Receipt + Ledger")
    print("  3. Replay          → Simulated different role → No side effects")
    print()
    print(f"  Total ledger entries: {state.ledger_length}")
    print(f"  Ledger head hash:    {state.ledger_head_hash[:32]}...")
    print()
    print("Key principle: The agent NEVER acted directly on any external system.")
    print("Every action went through RIO's governed execution pipeline.")
    print("Every decision is recorded with a cryptographic receipt and ledger entry.")


if __name__ == "__main__":
    main()
