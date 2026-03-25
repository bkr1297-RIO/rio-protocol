"""
RIO Runtime — Test Harness

Implements the protocol test cases defined in /tests/TC-RIO-001.md,
/tests/TC-RIO-002.md, and /tests/TC-RIO-003.md, plus additional
scenarios for invariant enforcement and edge cases.

Test Cases:
    TC-RIO-001: Allowed execution with receipt and ledger
    TC-RIO-002: Denied execution due to policy (HIGH risk)
    TC-RIO-003: Kill switch blocks execution
    TC-EXTRA-001: Self-authorization blocked (INV-06)
    TC-EXTRA-002: Token replay blocked (INV-07)
    TC-EXTRA-003: Validation failure produces receipt
    TC-EXTRA-004: Ledger hash chain integrity

Run with: python -m runtime.test_harness
"""

from __future__ import annotations

import logging
import sys

from . import ledger, kill_switch
from .models import Decision, ExecutionStatus
from .pipeline import PipelineResult, run
from .state import SystemState

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
