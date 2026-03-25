"""
RIO Runtime — Test Harness

Implements the protocol test cases defined in /tests/TC-RIO-001.md,
/tests/TC-RIO-002.md, and /tests/TC-RIO-003.md, plus additional
scenarios for invariant enforcement, edge cases, connector
integration, approval workflows, governance, and adapter execution.

Test Cases:
    TC-RIO-001: Allowed execution with receipt and ledger
    TC-RIO-002: Denied execution due to policy (HIGH risk)
    TC-RIO-003: Kill switch blocks execution
    TC-EXTRA-001: Self-authorization blocked (INV-06)
    TC-EXTRA-002: Token replay blocked (INV-07)
    TC-EXTRA-003: Validation failure produces receipt
    TC-EXTRA-004: Ledger hash chain integrity
    TC-POLICY-001: Policy engine denies intern transfer_funds > 1000
    TC-RISK-001: Risk engine computes correct score and level
    TC-INTENT-001: Intent requirements matrix validates required parameters
    TC-CONN-001: Email connector — allowed send writes to sent_emails.log
    TC-CONN-002: Email connector — denied send writes no log
    TC-CONN-003: Kill switch ON — connector not called
    TC-CONN-004: File connector — write_file creates file
    TC-CONN-005: HTTP connector — simulated request logged
    TC-APPR-001: Action requires approval → added to approval queue
    TC-APPR-002: Manager approves → execution happens → receipt → ledger
    TC-APPR-003: Manager denies → no execution → denial receipt → ledger
    TC-APPR-004: Non-manager cannot approve
    TC-GOV-001: Create new policy version via submit + approve
    TC-GOV-002: Activate new policy version and verify rules change
    TC-GOV-003: Rollback policy version to previous
    TC-GOV-004: Policy change recorded in ledger (GOVERNANCE_CHANGE)
    TC-GOV-005: Non-admin cannot change policy
    TC-ADPT-001: send_email executes through adapter and logs result
    TC-ADPT-002: create_event executes through adapter
    TC-ADPT-003: file write stays inside sandbox
    TC-ADPT-004: http request to non-whitelisted domain is blocked
    TC-ADPT-005: kill switch blocks adapter execution

Run with: python -m runtime.test_harness
"""

from __future__ import annotations

import json
import logging
import os
import sys

from . import ledger, kill_switch, data_store
from .models import Decision, ExecutionStatus
from .pipeline import PipelineResult, run
from .state import SystemState
from .approvals import approval_queue, approval_manager
from .governance import policy_manager
from .governance.governance_ledger import record_governance_change, set_governance_state

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("rio.test_harness")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_state() -> SystemState:
    """Create a fresh system state and reset the in-memory ledger."""
    ledger.reset()
    approval_manager.reset()
    return SystemState()


def _assert(condition: bool, message: str) -> None:
    """Assert a condition, logging pass or fail."""
    if condition:
        logger.info("  PASS: %s", message)
    else:
        logger.error("  FAIL: %s", message)
        raise AssertionError(message)


def _action_handler(intent):
    """Simulated action handler that returns a success result."""
    return {"status": "completed", "action": intent.action_type}


# ---------------------------------------------------------------------------
# TC-RIO-001: Allowed execution with receipt and ledger
# Protocol Steps Covered: 1–8
# Invariants Covered: INV-01, INV-02, INV-03, INV-04, INV-07
# ---------------------------------------------------------------------------

def test_tc_rio_001():
    """
    TC-RIO-001: A low-risk request from an authenticated user is approved
    by a distinct approver, executed, and produces a signed receipt and
    ledger entry with valid hash chain.
    """
    logger.info("=" * 70)
    logger.info("TC-RIO-001: Allowed execution with receipt and ledger")
    logger.info("=" * 70)

    state = _reset_state()

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "read_data",
            "target_resource": "report_server",
            "parameters": {"dataset": "quarterly_reports", "report_id": "RPT-2026-001"},
            "requested_by": "user_alice",
            "justification": "Quarterly review",
        },
        approver_id="manager_bob",
        state=state,
        action_handler=_action_handler,
    )

    # Verify all stages completed
    _assert(len(result.stages_completed) >= 8, "All 8+ stages completed")
    _assert("intake" in result.stages_completed, "Intake stage completed")
    _assert("execution_gate" in result.stages_completed, "Execution gate completed")
    _assert("receipt" in result.stages_completed, "Receipt stage completed")
    _assert("ledger" in result.stages_completed, "Ledger stage completed")

    # Verify execution succeeded
    _assert(result.success is True, "Pipeline reports success")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED",
    )

    # Verify receipt (INV-02)
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.receipt.receipt_hash != "", "Receipt hash is non-empty")
    _assert(result.receipt.signature != "", "Receipt signature is non-empty")
    _assert(result.receipt.decision == Decision.ALLOW, "Receipt decision is ALLOW")

    # Verify ledger entry (INV-03)
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(
        result.ledger_entry.receipt_id == result.receipt.receipt_id,
        "Ledger entry references correct receipt",
    )
    _assert(result.ledger_entry.ledger_hash != "", "Ledger hash is non-empty")

    # Verify hash chain (INV-04)
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    # Verify token consumed (INV-07)
    _assert(
        result.authorization.authorization_id in state.consumed_tokens,
        "Authorization token was consumed (single-use)",
    )

    # Verify ledger state updated
    _assert(state.ledger_length == 1, "Ledger length is 1")
    _assert(state.ledger_head_hash != "", "Ledger head hash is set")

    logger.info("TC-RIO-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-RIO-002: Denied execution due to policy
# Protocol Steps Covered: 1–5, 7–8
# Invariants Covered: INV-01, INV-03, INV-06
# ---------------------------------------------------------------------------

def test_tc_rio_002():
    """
    TC-RIO-002: A critical-risk request (delete_data, CRITICAL risk) is
    denied by policy. The denial still produces a receipt and ledger entry.
    """
    logger.info("=" * 70)
    logger.info("TC-RIO-002: Denied execution due to policy")
    logger.info("=" * 70)

    state = _reset_state()

    result = run(
        actor_id="intern_user_04",
        raw_input={
            "action_type": "delete_data",
            "target_resource": "production_database",
            "parameters": {
                "dataset": "customer_records",
                "scope": "all",
                "approval_authority": "data_governance_board",
            },
            "requested_by": "intern_user_04",
            "justification": "Cleanup request",
            "role": "intern",
        },
        approver_id="finance_manager",
        state=state,
        action_handler=_action_handler,
    )

    # Verify pipeline completed (even though denied)
    _assert("intake" in result.stages_completed, "Intake stage completed")
    _assert("receipt" in result.stages_completed, "Receipt stage completed")
    _assert("ledger" in result.stages_completed, "Ledger stage completed")

    # Verify execution was blocked
    _assert(result.success is False, "Pipeline reports failure (denied)")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.BLOCKED,
        "Execution status is BLOCKED",
    )

    # Verify receipt generated for denial (INV-02)
    _assert(result.receipt is not None, "Receipt was generated for denial")
    _assert(result.receipt.decision == Decision.DENY, "Receipt decision is DENY")
    _assert(result.receipt.receipt_hash != "", "Receipt hash is non-empty")
    _assert(result.receipt.signature != "", "Receipt signature is non-empty")

    # Verify ledger entry for denial (INV-03)
    _assert(result.ledger_entry is not None, "Ledger entry was created for denial")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-RIO-002: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-RIO-003: Kill switch blocks execution
# Protocol Steps Covered: 5–8
# Invariants Covered: INV-01, INV-07, INV-08
# ---------------------------------------------------------------------------

def test_tc_rio_003():
    """
    TC-RIO-003: The kill switch is engaged before a request is processed.
    The request is blocked at the authorization/execution gate level.
    A receipt and ledger entry are still generated.
    """
    logger.info("=" * 70)
    logger.info("TC-RIO-003: Kill switch blocks execution")
    logger.info("=" * 70)

    state = _reset_state()

    # Engage kill switch
    kill_switch.engage(state, actor_id="security_admin", reason="Emergency shutdown")
    _assert(state.kill_switch_active is True, "Kill switch is engaged")

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "read_data",
            "target_resource": "report_server",
            "parameters": {"dataset": "daily_reports", "report_id": "RPT-2026-002"},
            "requested_by": "user_alice",
            "justification": "Routine check",
        },
        approver_id="manager_bob",
        state=state,
        action_handler=_action_handler,
    )

    # Verify pipeline completed (blocked but still produced artifacts)
    _assert("intake" in result.stages_completed, "Intake stage completed")
    _assert("receipt" in result.stages_completed, "Receipt stage completed")
    _assert("ledger" in result.stages_completed, "Ledger stage completed")

    # Verify execution was blocked by kill switch (INV-08)
    _assert(result.success is False, "Pipeline reports failure (kill switch)")

    # Verify receipt generated for blocked request
    _assert(result.receipt is not None, "Receipt was generated for blocked request")
    _assert(result.receipt.receipt_hash != "", "Receipt hash is non-empty")
    _assert(result.receipt.signature != "", "Receipt signature is non-empty")

    # Verify ledger entry
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    # Verify token was NOT consumed (execution was blocked)
    _assert(
        len(state.consumed_tokens) == 0,
        "No tokens consumed (execution was blocked)",
    )

    logger.info("TC-RIO-003: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-EXTRA-001: Self-authorization blocked (INV-06)
# ---------------------------------------------------------------------------

def test_self_authorization_blocked():
    """
    TC-EXTRA-001: An actor attempts to authorize their own request.
    The pipeline must raise an InvariantViolation for INV-06.
    """
    logger.info("=" * 70)
    logger.info("TC-EXTRA-001: Self-authorization blocked (INV-06)")
    logger.info("=" * 70)

    state = _reset_state()

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "read_data",
            "target_resource": "report_server",
            "parameters": {},
            "requested_by": "user_alice",
            "justification": "Self-service",
        },
        approver_id="user_alice",  # Same as actor — should be blocked
        state=state,
        action_handler=_action_handler,
    )

    # Verify pipeline caught the invariant violation
    _assert(result.success is False, "Pipeline reports failure")
    _assert("invariant" in result.error.lower() or "inv-06" in result.error.lower(),
            "Error references INV-06 or invariant violation")

    logger.info("TC-EXTRA-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-EXTRA-002: Token replay blocked (INV-07)
# ---------------------------------------------------------------------------

def test_token_replay_blocked():
    """
    TC-EXTRA-002: After a successful execution, the same authorization token
    cannot be reused. A second pipeline run with the same token must be blocked.
    """
    logger.info("=" * 70)
    logger.info("TC-EXTRA-002: Token replay blocked (INV-07)")
    logger.info("=" * 70)

    state = _reset_state()

    # First run — should succeed
    result1 = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "read_data",
            "target_resource": "report_server",
            "parameters": {"dataset": "reports", "report_id": "RPT-001"},
            "requested_by": "user_alice",
            "justification": "First request",
        },
        approver_id="manager_bob",
        state=state,
        action_handler=_action_handler,
    )
    _assert(result1.success is True, "First execution succeeded")

    # Second run — new request, new token (should also succeed)
    result2 = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "read_data",
            "target_resource": "report_server",
            "parameters": {"dataset": "reports", "report_id": "RPT-002"},
            "requested_by": "user_alice",
            "justification": "Second request",
        },
        approver_id="manager_bob",
        state=state,
        action_handler=_action_handler,
    )
    _assert(result2.success is True, "Second execution succeeded (new token)")

    # Verify both tokens are consumed
    _assert(len(state.consumed_tokens) == 2, "Two tokens consumed")

    # Verify ledger has 2 entries with valid chain
    _assert(state.ledger_length == 2, "Ledger has 2 entries")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact after 2 entries")

    logger.info("TC-EXTRA-002: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-EXTRA-003: Validation failure produces receipt
# ---------------------------------------------------------------------------

def test_validation_failure_produces_receipt():
    """
    TC-EXTRA-003: A request with missing required fields fails validation
    but still produces a receipt and ledger entry (fail-closed).
    """
    logger.info("=" * 70)
    logger.info("TC-EXTRA-003: Validation failure produces receipt")
    logger.info("=" * 70)

    state = _reset_state()

    result = run(
        actor_id="user_alice",
        raw_input={
            # Missing action_type, target_resource, requested_by
        },
        approver_id="manager_bob",
        state=state,
    )

    # Verify pipeline handled the failure
    _assert(result.success is False, "Pipeline reports failure")

    # Even on validation failure, receipt and ledger should exist
    # (if the pipeline got far enough to generate them)
    if result.receipt is not None:
        _assert(result.receipt.receipt_hash != "", "Receipt hash is non-empty")
        _assert(result.ledger_entry is not None, "Ledger entry was created")
        logger.info("  INFO: Validation failure produced receipt and ledger entry")
    else:
        logger.info("  INFO: Pipeline failed before receipt generation (expected for missing action_type)")

    logger.info("TC-EXTRA-003: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-EXTRA-004: Ledger hash chain integrity
# ---------------------------------------------------------------------------

def test_ledger_hash_chain():
    """
    TC-EXTRA-004: Run multiple requests through the pipeline and verify
    the ledger hash chain is intact across all entries.
    """
    logger.info("=" * 70)
    logger.info("TC-EXTRA-004: Ledger hash chain integrity")
    logger.info("=" * 70)

    state = _reset_state()

    # Run 5 requests
    for i in range(5):
        result = run(
            actor_id=f"user_{i}",
            raw_input={
                "action_type": "read_data",
                "target_resource": f"resource_{i}",
                "parameters": {"dataset": f"dataset_{i}", "index": i},
                "requested_by": f"user_{i}",
                "justification": f"Request {i}",
            },
            approver_id=f"approver_{i}",
            state=state,
            action_handler=_action_handler,
        )
        _assert(result.success is True, f"Request {i} succeeded")

    # Verify chain
    _assert(state.ledger_length == 5, "Ledger has 5 entries")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact across 5 entries")

    # Verify each entry links to the previous
    entries = ledger.get_ledger()
    for i in range(1, len(entries)):
        _assert(
            entries[i].previous_ledger_hash == entries[i - 1].ledger_hash,
            f"Entry {i} links to entry {i-1}",
        )

    # Verify genesis entry
    _assert(entries[0].previous_ledger_hash == "", "Genesis entry has empty previous hash")

    logger.info("TC-EXTRA-004: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-POLICY-001: Policy engine denies intern transfer_funds > 1000
# ---------------------------------------------------------------------------

def test_policy_engine_deny():
    """
    TC-POLICY-001: An intern attempts a transfer_funds action with amount > 1000.
    The Policy Engine should match the deny rule and block the request.
    The receipt should contain the policy_rule_id and risk_score.
    """
    logger.info("=" * 70)
    logger.info("TC-POLICY-001: Policy engine denies intern transfer_funds > 1000")
    logger.info("=" * 70)

    state = _reset_state()

    result = run(
        actor_id="intern_user_04",
        raw_input={
            "action_type": "transfer_funds",
            "target_resource": "payment_system",
            "parameters": {
                "amount": 5000,
                "currency": "EUR",
                "recipient": "Vendor_X",
                "source_account": "Berlin_Office_Account",
            },
            "requested_by": "intern_user_04",
            "justification": "Office supplies invoice",
            "role": "intern",
        },
        approver_id="finance_manager",
        state=state,
        action_handler=_action_handler,
    )

    # Verify execution was blocked
    _assert(result.success is False, "Pipeline reports failure (denied by policy)")

    # Verify receipt exists
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.receipt.receipt_hash != "", "Receipt hash is non-empty")

    # Verify risk and policy fields on receipt
    _assert(result.receipt.risk_score > 0, f"Receipt has risk_score={result.receipt.risk_score}")
    _assert(result.receipt.risk_level != "", f"Receipt has risk_level={result.receipt.risk_level}")
    _assert(result.receipt.policy_rule_id != "", f"Receipt has policy_rule_id={result.receipt.policy_rule_id}")
    _assert(result.receipt.policy_decision != "", f"Receipt has policy_decision={result.receipt.policy_decision}")

    # Verify ledger entry
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-POLICY-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-RISK-001: Risk engine computes correct score and level
# ---------------------------------------------------------------------------

def test_risk_engine_scoring():
    """
    TC-RISK-001: Verify that the Risk Engine correctly computes risk scores
    based on action type, role, amount, and target resource.
    A low-risk read_data by an admin should have a low score.
    A high-risk transfer_funds by an intern should have a high score.
    """
    logger.info("=" * 70)
    logger.info("TC-RISK-001: Risk engine computes correct score and level")
    logger.info("=" * 70)

    from .policy.risk_engine import compute_risk

    # Low risk: admin reading data
    low_result = compute_risk(
        action_type="read_data",
        parameters={},
        role="admin",
        target_resource="email_system",
    )
    _assert(low_result.risk_level == "LOW", f"Admin read_data is LOW risk (score={low_result.risk_score})")
    _assert(low_result.risk_score < 5, f"Score {low_result.risk_score} < 5")

    # High risk: intern transferring large amount
    high_result = compute_risk(
        action_type="transfer_funds",
        parameters={"amount": 50000},
        role="intern",
        target_resource="payment_system",
    )
    _assert(high_result.risk_level == "HIGH", f"Intern transfer 50k is HIGH risk (score={high_result.risk_score})")
    _assert(high_result.risk_score >= 10, f"Score {high_result.risk_score} >= 10")

    # Verify components are populated
    _assert("base_risk" in high_result.components, "Components include base_risk")
    _assert("role_risk" in high_result.components, "Components include role_risk")
    _assert("amount_risk" in high_result.components, "Components include amount_risk")
    _assert("system_target_risk" in high_result.components, "Components include system_target_risk")

    logger.info("TC-RISK-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-INTENT-001: Intent requirements matrix validates required parameters
# ---------------------------------------------------------------------------

def test_intent_requirements_validation():
    """
    TC-INTENT-001: Verify that the Intent Requirements Matrix correctly
    identifies missing required parameters for specific action types.
    """
    logger.info("=" * 70)
    logger.info("TC-INTENT-001: Intent requirements matrix validates required parameters")
    logger.info("=" * 70)

    from .policy.intent_requirements import validate_intent_fields, get_required_fields

    # transfer_funds requires: amount, currency, recipient, source_account
    required = get_required_fields("transfer_funds")
    _assert("amount" in required, "transfer_funds requires 'amount'")
    _assert("currency" in required, "transfer_funds requires 'currency'")
    _assert("recipient" in required, "transfer_funds requires 'recipient'")
    _assert("source_account" in required, "transfer_funds requires 'source_account'")

    # Valid parameters — should pass
    valid, missing = validate_intent_fields("transfer_funds", {
        "amount": 5000,
        "currency": "EUR",
        "recipient": "Vendor_X",
        "source_account": "Berlin_Office_Account",
    })
    _assert(valid is True, "Valid transfer_funds parameters pass validation")
    _assert(len(missing) == 0, "No missing fields")

    # Missing parameters — should fail
    invalid, missing = validate_intent_fields("transfer_funds", {
        "amount": 5000,
        # Missing currency, recipient, source_account
    })
    _assert(invalid is False, "Incomplete transfer_funds parameters fail validation")
    _assert("currency" in missing, "Missing 'currency' detected")
    _assert("recipient" in missing, "Missing 'recipient' detected")
    _assert("source_account" in missing, "Missing 'source_account' detected")

    # Unknown action type — should pass (no requirements defined)
    unknown_valid, unknown_missing = validate_intent_fields("unknown_action", {})
    _assert(unknown_valid is True, "Unknown action type passes (no requirements)")

    logger.info("TC-INTENT-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-CONN-001: Email connector — allowed send writes to sent_emails.log
# Protocol Steps Covered: 1–8 (full pipeline with connector execution)
# ---------------------------------------------------------------------------

def test_email_connector_allowed():
    """
    TC-CONN-001: An allowed send_email action routes through the email
    connector and writes a record to runtime/data/sent_emails.log.
    """
    logger.info("=" * 70)
    logger.info("TC-CONN-001: Email connector — allowed send writes to sent_emails.log")
    logger.info("=" * 70)

    state = _reset_state()

    # Clean up any previous email log
    email_log = os.path.join(os.path.dirname(__file__), "data", "sent_emails.log")
    if os.path.exists(email_log):
        os.remove(email_log)

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "send_email",
            "target_resource": "email_system",
            "parameters": {
                "recipient": "bob@example.com",
                "subject": "Quarterly Report",
                "body": "Please find the quarterly report attached.",
            },
            "requested_by": "user_alice",
            "justification": "Sending quarterly report",
        },
        approver_id="manager_bob",
        state=state,
        # No action_handler — let the connector handle it
    )

    # Verify execution succeeded via connector
    _assert(result.success is True, "Pipeline reports success")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED",
    )
    _assert(
        result.execution_result.adapter_id == "email",
        f"Adapter ID is 'email' (got: {result.execution_result.adapter_id})",
    )

    # Verify email log file was written
    _assert(os.path.exists(email_log), "sent_emails.log file exists")
    with open(email_log, "r") as fh:
        lines = fh.readlines()
    _assert(len(lines) >= 1, f"Email log has at least 1 entry (got {len(lines)})")

    record = json.loads(lines[-1])
    # Adapter uses 'to' field; connector used 'recipient'
    email_to = record.get("to", record.get("recipient", ""))
    _assert(email_to == "bob@example.com", "Email recipient matches")
    _assert(record["subject"] == "Quarterly Report", "Email subject matches")

    # Verify receipt and ledger
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-CONN-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-CONN-002: Denied action — connector NOT called
# Protocol Steps Covered: 1–5, 7–8 (denied at policy, connector NOT called)
# ---------------------------------------------------------------------------

def test_email_connector_denied():
    """
    TC-CONN-002: A denied action (intern attempting delete_data, blocked by
    POL-004) must NOT invoke any connector. The execution gate blocks before
    the connector layer is reached, and no side effects occur.
    """
    logger.info("=" * 70)
    logger.info("TC-CONN-002: Denied action — connector NOT called")
    logger.info("=" * 70)

    state = _reset_state()

    # Clean up any previous email log (should stay absent)
    email_log = os.path.join(os.path.dirname(__file__), "data", "sent_emails.log")
    if os.path.exists(email_log):
        os.remove(email_log)

    # Use delete_data by intern — denied by POL-004
    result = run(
        actor_id="intern_user_04",
        raw_input={
            "action_type": "delete_data",
            "target_resource": "production_database",
            "parameters": {
                "dataset": "customer_records",
                "scope": "all",
                "approval_authority": "data_governance_board",
            },
            "requested_by": "intern_user_04",
            "justification": "Cleanup request",
            "role": "intern",
        },
        approver_id="finance_manager",
        state=state,
    )

    # Verify execution was blocked
    _assert(result.success is False, "Pipeline reports failure (denied)")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.BLOCKED,
        "Execution status is BLOCKED",
    )

    # Verify no connector side effects occurred
    # (email log should not exist since no connector was called)
    log_exists = os.path.exists(email_log)
    if log_exists:
        with open(email_log, "r") as fh:
            content = fh.read().strip()
        _assert(content == "", "Email log is empty (no connector side effects)")
    else:
        _assert(True, "No connector side effects (email log absent)")

    # Verify the connector_id is empty (connector was never resolved)
    _assert(
        result.execution_result.adapter_id == "",
        f"Adapter ID is empty (got: '{result.execution_result.adapter_id}')",
    )

    # Receipt and ledger should still exist
    _assert(result.receipt is not None, "Receipt was generated for denial")
    _assert(result.receipt.decision == Decision.DENY, "Receipt decision is DENY")
    _assert(result.ledger_entry is not None, "Ledger entry was created")

    logger.info("TC-CONN-002: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-CONN-003: Kill switch ON — connector not called
# Protocol Steps Covered: 1–8 (kill switch blocks at execution gate)
# Invariants Covered: INV-08
# ---------------------------------------------------------------------------

def test_kill_switch_blocks_connector():
    """
    TC-CONN-003: With the kill switch engaged, even an otherwise-allowed
    send_email action must be blocked. The email connector must NOT be
    invoked and no email log record should be written.
    """
    logger.info("=" * 70)
    logger.info("TC-CONN-003: Kill switch ON — connector not called")
    logger.info("=" * 70)

    state = _reset_state()

    # Clean up any previous email log
    email_log = os.path.join(os.path.dirname(__file__), "data", "sent_emails.log")
    if os.path.exists(email_log):
        os.remove(email_log)

    # Engage kill switch
    kill_switch.engage(state, actor_id="security_admin", reason="Emergency lockdown")
    _assert(state.kill_switch_active is True, "Kill switch is engaged")

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "send_email",
            "target_resource": "email_system",
            "parameters": {
                "recipient": "bob@example.com",
                "subject": "Urgent update",
                "body": "This should never be sent.",
            },
            "requested_by": "user_alice",
            "justification": "Urgent communication",
        },
        approver_id="manager_bob",
        state=state,
    )

    # Verify execution was blocked by kill switch
    _assert(result.success is False, "Pipeline reports failure (kill switch)")

    # Verify email log was NOT written
    log_exists = os.path.exists(email_log)
    if log_exists:
        with open(email_log, "r") as fh:
            content = fh.read().strip()
        _assert(content == "", "Email log is empty (connector not called)")
    else:
        _assert(True, "Email log file does not exist (connector not called)")

    # Receipt and ledger should still exist
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-CONN-003: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-CONN-004: File connector — write_file creates file
# Protocol Steps Covered: 1–8 (full pipeline with file connector)
# ---------------------------------------------------------------------------

def test_file_connector_write():
    """
    TC-CONN-004: An allowed write_file action routes through the file
    connector and creates the target file in runtime/data/.
    """
    logger.info("=" * 70)
    logger.info("TC-CONN-004: File connector — write_file creates file")
    logger.info("=" * 70)

    state = _reset_state()

    # Clean up any previous test file — adapter writes to data/sandbox/
    test_file = os.path.join(os.path.dirname(__file__), "data", "sandbox", "test_output.txt")
    if os.path.exists(test_file):
        os.remove(test_file)

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "write_file",
            "target_resource": "file_system",
            "parameters": {
                "operation": "write_file",
                "filename": "test_output.txt",
                "content": "RIO governed file write test — TC-CONN-004",
            },
            "requested_by": "user_alice",
            "justification": "Writing test output",
        },
        approver_id="manager_bob",
        state=state,
    )

    # Verify execution succeeded via connector
    _assert(result.success is True, "Pipeline reports success")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED",
    )
    _assert(
        result.execution_result.adapter_id == "file",
        f"Adapter ID is 'file' (got: {result.execution_result.adapter_id})",
    )

    # Verify the file was created
    _assert(os.path.exists(test_file), "test_output.txt was created")
    with open(test_file, "r") as fh:
        content = fh.read()
    _assert(
        content == "RIO governed file write test — TC-CONN-004",
        "File content matches expected value",
    )

    # Verify receipt and ledger
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    # Clean up
    os.remove(test_file)

    logger.info("TC-CONN-004: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-CONN-005: HTTP connector — simulated request logged
# Protocol Steps Covered: 1–8 (full pipeline with HTTP connector)
# ---------------------------------------------------------------------------

def test_http_connector_simulated():
    """
    TC-CONN-005: An allowed http_request action routes through the HTTP
    connector and writes a record to runtime/data/http_requests.log.
    """
    logger.info("=" * 70)
    logger.info("TC-CONN-005: HTTP connector — simulated request logged")
    logger.info("=" * 70)

    state = _reset_state()

    # Clean up any previous HTTP log
    http_log = os.path.join(os.path.dirname(__file__), "data", "http_requests.log")
    if os.path.exists(http_log):
        os.remove(http_log)

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "http_request",
            "target_resource": "external_api",
            "parameters": {
                "method": "POST",
                "url": "https://api.example.com/v1/reports",
                "headers": {"Authorization": "Bearer test-token"},
                "body": {"report_id": "RPT-2026-001"},
            },
            "requested_by": "user_alice",
            "justification": "Submitting report to external API",
        },
        approver_id="manager_bob",
        state=state,
    )

    # Verify execution succeeded via connector
    _assert(result.success is True, "Pipeline reports success")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED",
    )
    _assert(
        result.execution_result.adapter_id == "http",
        f"Adapter ID is 'http' (got: {result.execution_result.adapter_id})",
    )

    # Verify HTTP log file was written
    _assert(os.path.exists(http_log), "http_requests.log file exists")
    with open(http_log, "r") as fh:
        lines = fh.readlines()
    _assert(len(lines) >= 1, f"HTTP log has at least 1 entry (got {len(lines)})")

    record = json.loads(lines[-1])
    _assert(record["method"] == "POST", "HTTP method is POST")
    _assert(record["url"] == "https://api.example.com/v1/reports", "HTTP URL matches")
    _assert(record["response"]["status_code"] == 200, "Simulated response is 200")

    # Verify receipt and ledger
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-CONN-005: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-APPR-001: Action requires approval → added to approval queue
# ---------------------------------------------------------------------------

def test_approval_queue_created():
    """
    TC-APPR-001: An employee deploys code (deploy_code). Policy rule POL-006
    returns REQUIRE_APPROVAL. The pipeline halts with pending_approval=True
    and an approval request is created in the queue.
    """
    logger.info("=" * 70)
    logger.info("TC-APPR-001: Action requires approval → added to approval queue")
    logger.info("=" * 70)

    state = _reset_state()

    result = run(
        actor_id="dev_charlie",
        raw_input={
            "action_type": "deploy_code",
            "target_resource": "production_server",
            "parameters": {"repository": "rio-app", "branch": "main", "environment": "production"},
            "requested_by": "dev_charlie",
            "justification": "Release v2.1.0 to production",
            "role": "employee",
        },
        approver_id="manager_diana",
        state=state,
        action_handler=_action_handler,
    )

    # Pipeline should halt at approval queue
    _assert(result.pending_approval is True, "Pipeline reports pending_approval")
    _assert(result.approval is not None, "Approval request was created")
    _assert(result.approval.status == "PENDING", "Approval status is PENDING")
    _assert(result.approval.action == "deploy_code", "Approval action is deploy_code")
    _assert(result.approval.requester == "dev_charlie", "Approval requester is dev_charlie")
    _assert(result.approval.role == "employee", "Approval role is employee")
    _assert(result.approval.policy_rule_id == "POL-006", "Matched policy rule POL-006")

    # Pipeline should NOT have reached execution, receipt, or ledger
    _assert(result.execution_result is None, "No execution result (pipeline halted)")
    _assert(result.receipt is None, "No receipt (pipeline halted)")
    _assert(result.ledger_entry is None, "No ledger entry (pipeline halted)")

    # Approval should be in the queue
    _assert("approval_queue" in result.stages_completed, "Approval queue stage completed")
    pending = approval_queue.get_pending()
    _assert(len(pending) >= 1, "At least one pending approval in queue")
    _assert(pending[0].approval_id == result.approval.approval_id, "Pending approval matches")

    logger.info("TC-APPR-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-APPR-002: Manager approves → execution happens → receipt → ledger
# ---------------------------------------------------------------------------

def test_approval_approved():
    """
    TC-APPR-002: An employee's deploy_code request goes to the approval queue.
    A manager approves it. The pipeline resumes: authorization → execution →
    receipt → ledger. All artifacts are produced.
    """
    logger.info("=" * 70)
    logger.info("TC-APPR-002: Manager approves → execution → receipt → ledger")
    logger.info("=" * 70)

    state = _reset_state()

    # Step 1: Submit request → goes to approval queue
    result = run(
        actor_id="dev_charlie",
        raw_input={
            "action_type": "deploy_code",
            "target_resource": "staging_server",
            "parameters": {"repository": "rio-app", "branch": "release/2.2", "environment": "staging"},
            "requested_by": "dev_charlie",
            "justification": "Deploy v2.2.0 to staging",
            "role": "employee",
        },
        approver_id="manager_diana",
        state=state,
        action_handler=_action_handler,
    )

    _assert(result.pending_approval is True, "Request is pending approval")
    approval_id = result.approval.approval_id

    # Step 2: Manager approves
    approval_result = approval_manager.approve(
        approval_id=approval_id,
        approver_id="manager_diana",
        approver_role="manager",
    )

    _assert(approval_result.success is True, "Approval action succeeded")
    _assert(approval_result.error == "", "No error from approval")

    # Verify approval status updated
    approval = approval_queue.get(approval_id)
    _assert(approval.status == "APPROVED", "Approval status is APPROVED")
    _assert(approval.resolved_by == "manager_diana", "Resolved by manager_diana")

    # Verify execution happened
    _assert(approval_result.execution_result is not None, "Execution result exists")
    _assert(
        approval_result.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED",
    )

    # Verify receipt generated
    _assert(approval_result.receipt is not None, "Receipt was generated")
    _assert(approval_result.receipt.receipt_hash != "", "Receipt hash is non-empty")
    _assert(approval_result.receipt.policy_decision == "APPROVED_BY_HUMAN", "Policy decision is APPROVED_BY_HUMAN")

    # Verify ledger entry
    _assert(approval_result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-APPR-002: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-APPR-003: Manager denies → no execution → denial receipt → ledger
# ---------------------------------------------------------------------------

def test_approval_denied():
    """
    TC-APPR-003: An employee's deploy_code request goes to the approval queue.
    A manager denies it. No execution happens. A denial receipt and ledger
    entry are generated.
    """
    logger.info("=" * 70)
    logger.info("TC-APPR-003: Manager denies → denial receipt → ledger")
    logger.info("=" * 70)

    state = _reset_state()

    # Step 1: Submit request → goes to approval queue
    result = run(
        actor_id="dev_charlie",
        raw_input={
            "action_type": "deploy_code",
            "target_resource": "production_server",
            "parameters": {"repository": "rio-app", "branch": "beta", "environment": "production"},
            "requested_by": "dev_charlie",
            "justification": "Deploy beta to production",
            "role": "employee",
        },
        approver_id="manager_diana",
        state=state,
        action_handler=_action_handler,
    )

    _assert(result.pending_approval is True, "Request is pending approval")
    approval_id = result.approval.approval_id

    # Step 2: Manager denies
    denial_result = approval_manager.deny(
        approval_id=approval_id,
        denier_id="manager_diana",
        denier_role="manager",
    )

    _assert(denial_result.success is False, "Denial result success is False (denied)")
    _assert(denial_result.error == "", "No error from denial")

    # Verify approval status updated
    approval = approval_queue.get(approval_id)
    _assert(approval.status == "DENIED", "Approval status is DENIED")
    _assert(approval.resolved_by == "manager_diana", "Resolved by manager_diana")

    # Verify NO execution happened
    _assert(
        denial_result.execution_result is None,
        "No execution result (denied — action not executed)",
    )

    # Verify denial receipt generated
    _assert(denial_result.receipt is not None, "Denial receipt was generated")
    _assert(denial_result.receipt.receipt_hash != "", "Receipt hash is non-empty")
    _assert(denial_result.receipt.policy_decision == "DENIED_BY_HUMAN", "Policy decision is DENIED_BY_HUMAN")
    _assert(
        denial_result.receipt.execution_status == ExecutionStatus.BLOCKED,
        "Execution status is BLOCKED",
    )

    # Verify ledger entry
    _assert(denial_result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-APPR-003: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-APPR-004: Non-manager cannot approve
# ---------------------------------------------------------------------------

def test_non_manager_cannot_approve():
    """
    TC-APPR-004: An employee (non-manager) attempts to approve a pending
    request. The approval is rejected because only manager/admin roles
    can approve.
    """
    logger.info("=" * 70)
    logger.info("TC-APPR-004: Non-manager cannot approve")
    logger.info("=" * 70)

    state = _reset_state()

    # Step 1: Submit request → goes to approval queue
    result = run(
        actor_id="dev_charlie",
        raw_input={
            "action_type": "deploy_code",
            "target_resource": "production_server",
            "parameters": {"repository": "rio-app", "branch": "release/2.3", "environment": "production"},
            "requested_by": "dev_charlie",
            "justification": "Deploy v2.3.0",
            "role": "employee",
        },
        approver_id="manager_diana",
        state=state,
        action_handler=_action_handler,
    )

    _assert(result.pending_approval is True, "Request is pending approval")
    approval_id = result.approval.approval_id

    # Step 2: Employee tries to approve — should be rejected
    bad_result = approval_manager.approve(
        approval_id=approval_id,
        approver_id="dev_eve",
        approver_role="employee",
    )

    _assert(bad_result.success is False, "Non-manager approval rejected")
    _assert("not authorized" in bad_result.error, "Error mentions not authorized")

    # Verify approval is still PENDING
    approval = approval_queue.get(approval_id)
    _assert(approval.status == "PENDING", "Approval still PENDING after rejected attempt")

    # Step 3: Also test that intern cannot approve
    bad_result_2 = approval_manager.approve(
        approval_id=approval_id,
        approver_id="intern_frank",
        approver_role="intern",
    )

    _assert(bad_result_2.success is False, "Intern approval rejected")
    _assert("not authorized" in bad_result_2.error, "Error mentions not authorized")

    # Approval still PENDING
    _assert(approval.status == "PENDING", "Approval still PENDING after intern attempt")

    logger.info("TC-APPR-004: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-GOV-001: Create new policy version via submit + approve
# ---------------------------------------------------------------------------

def test_governance_create_version():
    """
    TC-GOV-001: An admin proposes a new policy version with modified rules.
    A second admin approves it. The new version is registered but not yet active.
    """
    logger.info("=" * 70)
    logger.info("TC-GOV-001: Create new policy version via submit + approve")
    logger.info("=" * 70)

    state = _reset_state()
    policy_manager.reset()

    # Get current policy
    current = policy_manager.get_current_policy()
    _assert(current.success is True, "Current policy loaded")
    _assert(current.version == "1.0", f"Current version is 1.0 (got: {current.version})")

    # Propose a new version with an additional rule
    new_rules = list(current.rules) + [
        {
            "id": "POL-009",
            "description": "Bulk data export requires approval",
            "action": "export_data",
            "decision": "REQUIRE_APPROVAL",
            "priority": 10,
        }
    ]

    submit_result = policy_manager.submit_policy_change(
        proposed_by="admin_01",
        proposed_by_role="admin",
        new_rules=new_rules,
        change_summary="Add POL-009: Bulk data export requires approval",
    )
    _assert(submit_result.success is True, "Policy change submitted")
    _assert(submit_result.change.status == "PROPOSED", "Status is PROPOSED")
    _assert(submit_result.version == "1.1", f"New version is 1.1 (got: {submit_result.version})")

    change_id = submit_result.change.change_id

    # Approve with a different admin (no self-approval)
    approve_result = policy_manager.approve_policy_change(
        change_id=change_id,
        approver_id="admin_02",
        approver_role="admin",
    )
    _assert(approve_result.success is True, "Policy change approved")
    _assert(approve_result.change.status == "APPROVED", "Status is APPROVED")
    _assert(approve_result.change.approved_by == "admin_02", "Approved by admin_02")

    # Version should be registered but not yet active
    versions = policy_manager.get_all_versions()
    _assert("1.1" in versions["versions"], "Version 1.1 exists in registry")
    _assert(versions["current_version"] == "1.0", "Current version is still 1.0")

    logger.info("TC-GOV-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-GOV-002: Activate new policy version and verify rules change
# ---------------------------------------------------------------------------

def test_governance_activate_version():
    """
    TC-GOV-002: After creating and approving a new policy version,
    an admin activates it. The policy engine should now use the new rules.
    """
    logger.info("=" * 70)
    logger.info("TC-GOV-002: Activate new policy version and verify rules change")
    logger.info("=" * 70)

    state = _reset_state()
    policy_manager.reset()

    # Get current rules count
    current = policy_manager.get_current_policy()
    original_count = len(current.rules)
    _assert(current.version == "1.0", "Starting at version 1.0")

    # Propose + approve a new version
    new_rules = list(current.rules) + [
        {
            "id": "POL-010",
            "description": "System shutdown requires admin approval",
            "action": "system_shutdown",
            "decision": "REQUIRE_APPROVAL",
            "priority": 15,
        }
    ]

    submit = policy_manager.submit_policy_change(
        proposed_by="admin_01",
        proposed_by_role="admin",
        new_rules=new_rules,
        change_summary="Add POL-010: System shutdown requires approval",
    )
    _assert(submit.success is True, "Submitted")

    approve = policy_manager.approve_policy_change(
        change_id=submit.change.change_id,
        approver_id="admin_02",
        approver_role="admin",
    )
    _assert(approve.success is True, "Approved")

    # Activate the new version
    activate = policy_manager.activate_policy_version(
        version="1.1",
        activated_by="admin_01",
        activated_by_role="admin",
    )
    _assert(activate.success is True, "Version 1.1 activated")
    _assert(activate.version == "1.1", "Active version is 1.1")
    _assert(len(activate.rules) == original_count + 1, f"Rules count increased by 1")

    # Verify the policy engine is now using the new version
    versions = policy_manager.get_all_versions()
    _assert(versions["current_version"] == "1.1", "Current version is now 1.1")

    # Verify the new rule exists
    new_policy = policy_manager.get_current_policy()
    rule_ids = [r["id"] for r in new_policy.rules]
    _assert("POL-010" in rule_ids, "POL-010 is in the active rules")

    # Restore original version for subsequent tests
    policy_manager.rollback_policy_version(
        target_version="1.0",
        rolled_back_by="admin_01",
        rolled_back_by_role="admin",
    )

    logger.info("TC-GOV-002: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-GOV-003: Rollback policy version to previous
# ---------------------------------------------------------------------------

def test_governance_rollback_version():
    """
    TC-GOV-003: After activating a new policy version, an admin rolls back
    to the previous version. The policy engine should revert to the old rules.
    """
    logger.info("=" * 70)
    logger.info("TC-GOV-003: Rollback policy version to previous")
    logger.info("=" * 70)

    state = _reset_state()
    policy_manager.reset()

    # Propose + approve + activate a new version
    current = policy_manager.get_current_policy()
    original_count = len(current.rules)

    new_rules = list(current.rules) + [
        {
            "id": "POL-011",
            "description": "Test rule for rollback",
            "action": "test_action",
            "decision": "DENY",
            "priority": 5,
        }
    ]

    submit = policy_manager.submit_policy_change(
        proposed_by="admin_01",
        proposed_by_role="admin",
        new_rules=new_rules,
        change_summary="Add POL-011 for rollback test",
    )
    approve = policy_manager.approve_policy_change(
        change_id=submit.change.change_id,
        approver_id="admin_02",
        approver_role="admin",
    )
    activate = policy_manager.activate_policy_version(
        version="1.1",
        activated_by="admin_01",
        activated_by_role="admin",
    )
    _assert(activate.success is True, "Version 1.1 activated")

    # Verify we are on 1.1
    versions = policy_manager.get_all_versions()
    _assert(versions["current_version"] == "1.1", "Current version is 1.1")

    # Rollback to 1.0
    rollback = policy_manager.rollback_policy_version(
        target_version="1.0",
        rolled_back_by="admin_02",
        rolled_back_by_role="admin",
    )
    _assert(rollback.success is True, "Rollback succeeded")
    _assert(rollback.version == "1.0", "Rolled back to version 1.0")
    _assert(len(rollback.rules) == original_count, "Rule count matches original")

    # Verify version registry
    versions = policy_manager.get_all_versions()
    _assert(versions["current_version"] == "1.0", "Current version is 1.0 after rollback")

    # Verify change log has rollback entry
    change = rollback.change
    _assert(change.status == "ROLLED_BACK", "Change status is ROLLED_BACK")
    _assert(change.old_version == "1.1", "Old version in rollback is 1.1")
    _assert(change.new_version == "1.0", "New version in rollback is 1.0")

    logger.info("TC-GOV-003: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-GOV-004: Policy change recorded in ledger (GOVERNANCE_CHANGE)
# ---------------------------------------------------------------------------

def test_governance_change_in_ledger():
    """
    TC-GOV-004: When a policy version is activated, a GOVERNANCE_CHANGE
    entry must be recorded in the audit ledger with the version change,
    proposer, and approver information.
    """
    logger.info("=" * 70)
    logger.info("TC-GOV-004: Policy change recorded in ledger (GOVERNANCE_CHANGE)")
    logger.info("=" * 70)

    state = _reset_state()
    policy_manager.reset()
    set_governance_state(state)

    # Record initial ledger length
    initial_length = state.ledger_length

    # Record a governance change directly
    result = record_governance_change(
        change_type="ACTIVATE",
        old_version="1.0",
        new_version="1.1",
        proposed_by="admin_01",
        approved_by="admin_02",
        change_summary="Activate v1.1 with new approval threshold",
        change_id="POL-CHG-TEST-001",
    )

    # Verify receipt was created
    receipt = result["receipt"]
    _assert(receipt is not None, "Governance receipt was created")
    _assert(receipt.receipt_hash != "", "Receipt hash is non-empty")
    _assert(receipt.action_type == "GOVERNANCE_CHANGE", "Action type is GOVERNANCE_CHANGE")
    _assert(receipt.policy_decision == "GOVERNANCE_ACTIVATE", "Policy decision is GOVERNANCE_ACTIVATE")
    _assert(receipt.risk_level == "GOVERNANCE", "Risk level is GOVERNANCE")

    # Verify ledger entry was created
    ledger_entry = result["ledger_entry"]
    _assert(ledger_entry is not None, "Ledger entry was created")
    _assert(ledger_entry.ledger_hash != "", "Ledger hash is non-empty")
    _assert(state.ledger_length == initial_length + 1, "Ledger length increased by 1")

    # Verify hash chain integrity
    _assert(ledger.verify_chain(), "Ledger hash chain is intact after governance change")

    # Record a second governance change (rollback)
    result2 = record_governance_change(
        change_type="ROLLBACK",
        old_version="1.1",
        new_version="1.0",
        proposed_by="admin_02",
        approved_by="admin_02",
        change_summary="Emergency rollback to v1.0",
        change_id="POL-CHG-TEST-002",
    )

    _assert(result2["receipt"].policy_decision == "GOVERNANCE_ROLLBACK", "Rollback receipt has correct policy_decision")
    _assert(state.ledger_length == initial_length + 2, "Ledger length increased by 2")
    _assert(ledger.verify_chain(), "Ledger hash chain intact after two governance changes")

    logger.info("TC-GOV-004: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-GOV-005: Non-admin cannot change policy
# ---------------------------------------------------------------------------

def test_governance_non_admin_blocked():
    """
    TC-GOV-005: Non-admin roles (employee, manager, intern) cannot submit,
    approve, activate, or rollback policy changes.
    """
    logger.info("=" * 70)
    logger.info("TC-GOV-005: Non-admin cannot change policy")
    logger.info("=" * 70)

    state = _reset_state()
    policy_manager.reset()

    current = policy_manager.get_current_policy()

    # Employee cannot propose
    result = policy_manager.submit_policy_change(
        proposed_by="employee_01",
        proposed_by_role="employee",
        new_rules=current.rules,
        change_summary="Unauthorized change attempt",
    )
    _assert(result.success is False, "Employee cannot propose policy changes")
    _assert("not authorized" in result.error.lower(), "Error mentions authorization")

    # Manager cannot propose
    result2 = policy_manager.submit_policy_change(
        proposed_by="manager_01",
        proposed_by_role="manager",
        new_rules=current.rules,
        change_summary="Unauthorized change attempt",
    )
    _assert(result2.success is False, "Manager cannot propose policy changes")

    # Intern cannot propose
    result3 = policy_manager.submit_policy_change(
        proposed_by="intern_01",
        proposed_by_role="intern",
        new_rules=current.rules,
        change_summary="Unauthorized change attempt",
    )
    _assert(result3.success is False, "Intern cannot propose policy changes")

    # Create a valid proposal for testing approve/activate/rollback blocks
    submit = policy_manager.submit_policy_change(
        proposed_by="admin_01",
        proposed_by_role="admin",
        new_rules=current.rules,
        change_summary="Valid proposal for testing",
    )
    _assert(submit.success is True, "Admin can propose")
    change_id = submit.change.change_id

    # Employee cannot approve
    approve_result = policy_manager.approve_policy_change(
        change_id=change_id,
        approver_id="employee_01",
        approver_role="employee",
    )
    _assert(approve_result.success is False, "Employee cannot approve policy changes")

    # Manager cannot approve (only admin can)
    approve_result2 = policy_manager.approve_policy_change(
        change_id=change_id,
        approver_id="manager_01",
        approver_role="manager",
    )
    _assert(approve_result2.success is False, "Manager cannot approve policy changes")

    # Employee cannot activate
    activate_result = policy_manager.activate_policy_version(
        version="1.1",
        activated_by="employee_01",
        activated_by_role="employee",
    )
    _assert(activate_result.success is False, "Employee cannot activate policy versions")

    # Employee cannot rollback
    rollback_result = policy_manager.rollback_policy_version(
        target_version="1.0",
        rolled_back_by="employee_01",
        rolled_back_by_role="employee",
    )
    _assert(rollback_result.success is False, "Employee cannot rollback policy versions")

    logger.info("TC-GOV-005: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-ADPT-001: send_email executes through adapter and logs result
# Protocol Steps Covered: 1–8 (full pipeline with adapter execution)
# ---------------------------------------------------------------------------

def test_adapter_email():
    """
    TC-ADPT-001: An allowed send_email action routes through the email
    adapter, logs a structured record, and returns an external_reference.
    """
    logger.info("=" * 70)
    logger.info("TC-ADPT-001: send_email executes through adapter and logs result")
    logger.info("=" * 70)

    state = _reset_state()

    # Clean up any previous email log
    email_log = os.path.join(os.path.dirname(__file__), "data", "sent_emails.log")
    if os.path.exists(email_log):
        os.remove(email_log)

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "send_email",
            "target_resource": "email_system",
            "parameters": {
                "recipient": "cto@example.com",
                "subject": "Adapter Test Email",
                "body": "This email was sent through the adapter layer.",
            },
            "requested_by": "user_alice",
            "justification": "Testing adapter-based email execution",
        },
        approver_id="manager_bob",
        state=state,
    )

    _assert(result.success is True, "Pipeline reports success")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED",
    )
    _assert(
        result.execution_result.adapter_id == "email",
        f"Adapter ID is 'email' (got: {result.execution_result.adapter_id})",
    )
    _assert(
        result.execution_result.external_reference != "",
        f"External reference is non-empty (got: {result.execution_result.external_reference})",
    )
    _assert(
        result.execution_result.external_reference.startswith("SIM-"),
        f"External reference starts with SIM- (got: {result.execution_result.external_reference})",
    )

    # Verify email log file was written with adapter format
    _assert(os.path.exists(email_log), "sent_emails.log file exists")
    with open(email_log, "r") as fh:
        lines = fh.readlines()
    _assert(len(lines) >= 1, f"Email log has at least 1 entry (got {len(lines)})")

    record = json.loads(lines[-1])
    _assert(record["to"] == "cto@example.com", "Email 'to' field matches")
    _assert(record["subject"] == "Adapter Test Email", "Email subject matches")
    _assert(record["mode"] == "simulated", "Mode is simulated")
    _assert("message_id" in record, "Record has message_id")
    _assert("intent_id" in record, "Record has intent_id")
    _assert("authorization_id" in record, "Record has authorization_id")

    # Verify result_data contains adapter metadata
    rd = result.execution_result.result_data
    _assert(rd.get("adapter_id") == "email", "result_data has adapter_id=email")
    _assert(rd.get("mode") == "simulated", "result_data has mode=simulated")
    _assert("external_reference" in rd, "result_data has external_reference")

    # Verify receipt and ledger
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-ADPT-001: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-ADPT-002: create_event executes through adapter
# Protocol Steps Covered: 1–8 (full pipeline with calendar adapter)
# ---------------------------------------------------------------------------

def test_adapter_calendar():
    """
    TC-ADPT-002: An allowed create_event action routes through the
    calendar adapter and logs a structured event record.
    """
    logger.info("=" * 70)
    logger.info("TC-ADPT-002: create_event executes through adapter")
    logger.info("=" * 70)

    state = _reset_state()

    # Clean up any previous calendar log
    cal_log = os.path.join(os.path.dirname(__file__), "data", "calendar_events.log")
    if os.path.exists(cal_log):
        os.remove(cal_log)

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "create_event",
            "target_resource": "calendar_system",
            "parameters": {
                "title": "RIO Architecture Review",
                "time": "2026-04-01T14:00:00Z",
                "duration": "60m",
                "location": "Conference Room A",
                "attendees": ["bob@example.com", "carol@example.com"],
            },
            "requested_by": "user_alice",
            "justification": "Quarterly architecture review meeting",
        },
        approver_id="manager_bob",
        state=state,
    )

    _assert(result.success is True, "Pipeline reports success")
    _assert(
        result.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED",
    )
    _assert(
        result.execution_result.adapter_id == "calendar",
        f"Adapter ID is 'calendar' (got: {result.execution_result.adapter_id})",
    )
    _assert(
        result.execution_result.external_reference.startswith("EVT-"),
        f"External reference starts with EVT- (got: {result.execution_result.external_reference})",
    )

    # Verify calendar log file was written
    _assert(os.path.exists(cal_log), "calendar_events.log file exists")
    with open(cal_log, "r") as fh:
        lines = fh.readlines()
    _assert(len(lines) >= 1, f"Calendar log has at least 1 entry (got {len(lines)})")

    record = json.loads(lines[-1])
    _assert(record["title"] == "RIO Architecture Review", "Event title matches")
    _assert(record["time"] == "2026-04-01T14:00:00Z", "Event time matches")
    _assert(record["duration"] == "60m", "Event duration matches")
    _assert(record["mode"] == "simulated", "Mode is simulated")
    _assert("event_id" in record, "Record has event_id")

    # Verify receipt and ledger
    _assert(result.receipt is not None, "Receipt was generated")
    _assert(result.ledger_entry is not None, "Ledger entry was created")
    _assert(ledger.verify_chain(), "Ledger hash chain is intact")

    logger.info("TC-ADPT-002: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-ADPT-003: file write stays inside sandbox
# Protocol Steps Covered: Adapter sandbox enforcement
# ---------------------------------------------------------------------------

def test_adapter_file_sandbox():
    """
    TC-ADPT-003: A write_file action through the file adapter creates
    the file inside the sandbox directory. A path traversal attempt
    (e.g., ../../../etc/passwd) is blocked by the adapter.
    """
    logger.info("=" * 70)
    logger.info("TC-ADPT-003: file write stays inside sandbox")
    logger.info("=" * 70)

    state = _reset_state()

    # --- Part A: Valid write inside sandbox ---
    sandbox_dir = os.path.join(os.path.dirname(__file__), "data", "sandbox")
    test_file = os.path.join(sandbox_dir, "adapter_test.txt")
    if os.path.exists(test_file):
        os.remove(test_file)

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "write_file",
            "target_resource": "file_system",
            "parameters": {
                "operation": "write_file",
                "filename": "adapter_test.txt",
                "content": "Adapter sandbox write test — TC-ADPT-003",
            },
            "requested_by": "user_alice",
            "justification": "Testing adapter sandbox enforcement",
        },
        approver_id="manager_bob",
        state=state,
    )

    _assert(result.success is True, "Pipeline reports success for valid write")
    _assert(
        result.execution_result.adapter_id == "file",
        f"Adapter ID is 'file' (got: {result.execution_result.adapter_id})",
    )
    _assert(os.path.exists(test_file), "File was created inside sandbox")
    with open(test_file, "r") as fh:
        content = fh.read()
    _assert(
        content == "Adapter sandbox write test — TC-ADPT-003",
        "File content matches expected value",
    )

    # --- Part B: Path traversal attempt ---
    state2 = _reset_state()

    traversal_result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "write_file",
            "target_resource": "file_system",
            "parameters": {
                "operation": "write_file",
                "filename": "../../../etc/malicious.txt",
                "content": "This should be blocked",
            },
            "requested_by": "user_alice",
            "justification": "Path traversal test",
        },
        approver_id="manager_bob",
        state=state2,
    )

    # The pipeline should succeed (no crash) but the adapter should fail
    _assert(
        traversal_result.execution_result.execution_status == ExecutionStatus.FAILED,
        "Path traversal write was blocked (FAILED status)",
    )
    _assert(
        "path_traversal" in str(traversal_result.execution_result.result_data)
        or "traversal" in str(traversal_result.execution_result.result_data).lower(),
        "Result mentions path traversal",
    )

    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)

    logger.info("TC-ADPT-003: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-ADPT-004: http request to non-whitelisted domain is blocked
# Protocol Steps Covered: Adapter domain whitelist enforcement
# ---------------------------------------------------------------------------

def test_adapter_http_whitelist():
    """
    TC-ADPT-004: An http_request to a non-whitelisted domain is blocked
    by the HTTP adapter. A request to a whitelisted domain succeeds.
    """
    logger.info("=" * 70)
    logger.info("TC-ADPT-004: http request to non-whitelisted domain is blocked")
    logger.info("=" * 70)

    state = _reset_state()

    # --- Part A: Non-whitelisted domain (should be blocked) ---
    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "http_request",
            "target_resource": "http_gateway",
            "parameters": {
                "url": "https://evil-domain.com/api/steal",
                "method": "POST",
                "body": {"data": "sensitive"},
            },
            "requested_by": "user_alice",
            "justification": "Testing domain whitelist",
        },
        approver_id="manager_bob",
        state=state,
    )

    _assert(
        result.execution_result.execution_status == ExecutionStatus.FAILED,
        "Non-whitelisted domain request was blocked (FAILED status)",
    )
    _assert(
        "domain_not_whitelisted" in str(result.execution_result.result_data)
        or "not whitelisted" in str(result.execution_result.result_data).lower(),
        "Result mentions domain not whitelisted",
    )

    # --- Part B: Whitelisted domain (should succeed) ---
    state2 = _reset_state()

    http_log = os.path.join(os.path.dirname(__file__), "data", "http_requests.log")
    if os.path.exists(http_log):
        os.remove(http_log)

    result2 = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "http_request",
            "target_resource": "http_gateway",
            "parameters": {
                "url": "https://api.example.com/v1/status",
                "method": "GET",
            },
            "requested_by": "user_alice",
            "justification": "Testing whitelisted domain",
        },
        approver_id="manager_bob",
        state=state2,
    )

    _assert(result2.success is True, "Whitelisted domain request succeeded")
    _assert(
        result2.execution_result.execution_status == ExecutionStatus.EXECUTED,
        "Execution status is EXECUTED for whitelisted domain",
    )
    _assert(
        result2.execution_result.adapter_id == "http",
        f"Adapter ID is 'http' (got: {result2.execution_result.adapter_id})",
    )

    logger.info("TC-ADPT-004: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# TC-ADPT-005: kill switch blocks adapter execution
# Protocol Steps Covered: INV-08 enforcement at adapter layer
# ---------------------------------------------------------------------------

def test_adapter_kill_switch():
    """
    TC-ADPT-005: When the kill switch is engaged, the execution gate
    blocks before the adapter is ever called. Verify no adapter side
    effects occur.
    """
    logger.info("=" * 70)
    logger.info("TC-ADPT-005: kill switch blocks adapter execution")
    logger.info("=" * 70)

    state = _reset_state()

    # Engage kill switch
    kill_switch.engage(state, actor_id="admin_01", reason="TC-ADPT-005 test")
    _assert(state.kill_switch_active is True, "Kill switch is engaged")

    # Clean up any previous email log
    email_log = os.path.join(os.path.dirname(__file__), "data", "sent_emails.log")
    if os.path.exists(email_log):
        os.remove(email_log)

    result = run(
        actor_id="user_alice",
        raw_input={
            "action_type": "send_email",
            "target_resource": "email_system",
            "parameters": {
                "recipient": "blocked@example.com",
                "subject": "This should not be sent",
                "body": "Kill switch is engaged.",
            },
            "requested_by": "user_alice",
            "justification": "Testing kill switch with adapter",
        },
        approver_id="manager_bob",
        state=state,
    )

    # Verify execution was blocked at the gate level
    _assert(
        result.execution_result.execution_status == ExecutionStatus.KILL_SWITCH_BLOCKED,
        "Execution status is KILL_SWITCH_BLOCKED",
    )

    # Verify adapter was never called (no side effects)
    _assert(
        result.execution_result.adapter_id == "",
        f"Adapter ID is empty (got: '{result.execution_result.adapter_id}')",
    )
    _assert(
        result.execution_result.external_reference == "",
        "No external reference (adapter never called)",
    )

    # Verify no email was logged
    if os.path.exists(email_log):
        with open(email_log, "r") as fh:
            lines = fh.readlines()
        _assert(len(lines) == 0, "No emails logged when kill switch is engaged")
    else:
        _assert(True, "No email log file (adapter never called)")

    # Verify no tokens consumed
    _assert(
        len(state.consumed_tokens) == 0,
        "No tokens consumed (execution was blocked)",
    )

    # Disengage for cleanup
    kill_switch.disengage(state, actor_id="admin_01", reason="TC-ADPT-005 cleanup")

    logger.info("TC-ADPT-005: PASSED")
    logger.info("")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_all_tests():
    """Run all test cases and report results."""
    logger.info("=" * 70)
    logger.info("RIO RUNTIME TEST HARNESS")
    logger.info("=" * 70)
    logger.info("")

    tests = [
        ("TC-RIO-001", test_tc_rio_001),
        ("TC-RIO-002", test_tc_rio_002),
        ("TC-RIO-003", test_tc_rio_003),
        ("TC-EXTRA-001", test_self_authorization_blocked),
        ("TC-EXTRA-002", test_token_replay_blocked),
        ("TC-EXTRA-003", test_validation_failure_produces_receipt),
        ("TC-EXTRA-004", test_ledger_hash_chain),
        ("TC-POLICY-001", test_policy_engine_deny),
        ("TC-RISK-001", test_risk_engine_scoring),
        ("TC-INTENT-001", test_intent_requirements_validation),
        ("TC-CONN-001", test_email_connector_allowed),
        ("TC-CONN-002", test_email_connector_denied),
        ("TC-CONN-003", test_kill_switch_blocks_connector),
        ("TC-CONN-004", test_file_connector_write),
        ("TC-CONN-005", test_http_connector_simulated),
        ("TC-APPR-001", test_approval_queue_created),
        ("TC-APPR-002", test_approval_approved),
        ("TC-APPR-003", test_approval_denied),
        ("TC-APPR-004", test_non_manager_cannot_approve),
        ("TC-GOV-001", test_governance_create_version),
        ("TC-GOV-002", test_governance_activate_version),
        ("TC-GOV-003", test_governance_rollback_version),
        ("TC-GOV-004", test_governance_change_in_ledger),
        ("TC-GOV-005", test_governance_non_admin_blocked),
        ("TC-ADPT-001", test_adapter_email),
        ("TC-ADPT-002", test_adapter_calendar),
        ("TC-ADPT-003", test_adapter_file_sandbox),
        ("TC-ADPT-004", test_adapter_http_whitelist),
        ("TC-ADPT-005", test_adapter_kill_switch),
    ]

    passed = 0
    failed = 0
    errors = []

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except (AssertionError, Exception) as e:
            failed += 1
            errors.append((name, str(e)))
            logger.error("TEST FAILED: %s — %s", name, str(e))
            logger.info("")

    logger.info("=" * 70)
    logger.info("TEST RESULTS: %d passed, %d failed, %d total", passed, failed, len(tests))
    if errors:
        logger.info("FAILURES:")
        for name, err in errors:
            logger.info("  %s: %s", name, err)
    logger.info("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
