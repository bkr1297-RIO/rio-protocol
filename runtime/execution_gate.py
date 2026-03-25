"""
RIO Runtime — Stage 7: Execution Gate

The Execution Gate is the final checkpoint before any action is executed.
It verifies four conditions before allowing execution:

1. Valid authorization token (signature and expiration).
2. Token has not been used before (INV-07: single-use).
3. Kill switch is OFF (INV-08).
4. Decision is ALLOW.

If all conditions pass, the action is executed and the result is passed
to the Receipt stage. If any condition fails, execution is blocked.

Spec reference: /spec/07_execution.md
Protocol stage: Step 6 of the 8-step Governed Execution Protocol
Related invariants: INV-01, INV-07 (Single-Use), INV-08 (Kill Switch Override)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .invariants import InvariantViolation, check_inv_07_single_use, check_inv_08_kill_switch
from .models import Authorization, Decision, ExecutionStatus, Intent
from .state import SystemState

logger = logging.getLogger("rio.execution_gate")


@dataclass
class ExecutionResult:
    """Result of the execution gate evaluation and (optional) action execution."""
    intent_id: str
    authorization_id: str
    execution_status: ExecutionStatus
    result_data: dict[str, Any]
    timestamp: int
    blocked_reason: str = ""


def execute(
    intent: Intent,
    authorization: Authorization,
    state: SystemState,
    action_handler: Optional[Callable[[Intent], dict[str, Any]]] = None,
) -> ExecutionResult:
    """
    Evaluate gate conditions and execute the action if all pass.

    Gate checks (in order):
    1. Kill switch OFF (INV-08)
    2. Decision is ALLOW
    3. Token not previously consumed (INV-07)
    4. Token has not expired

    If all checks pass and an action_handler is provided, the action is executed.
    The authorization token is consumed (marked as used) upon successful execution.

    Args:
        intent: The canonical Intent.
        authorization: The Authorization token from the Authorization stage.
        state: The current system state.
        action_handler: Optional callable that performs the actual action.
            Receives the Intent and returns a result dict.

    Returns:
        An ExecutionResult recording the outcome.
    """
    now = int(time.time() * 1000)

    # Gate check 1: Kill switch (INV-08)
    try:
        check_inv_08_kill_switch(state)
    except InvariantViolation as e:
        logger.warning(
            "Execution BLOCKED for intent %s — kill switch engaged",
            intent.intent_id,
        )
        return ExecutionResult(
            intent_id=intent.intent_id,
            authorization_id=authorization.authorization_id,
            execution_status=ExecutionStatus.KILL_SWITCH_BLOCKED,
            result_data={},
            timestamp=now,
            blocked_reason=str(e),
        )

    # Gate check 2: Decision must be ALLOW
    if authorization.decision != Decision.ALLOW:
        logger.info(
            "Execution BLOCKED for intent %s — decision is %s",
            intent.intent_id,
            authorization.decision.value,
        )
        return ExecutionResult(
            intent_id=intent.intent_id,
            authorization_id=authorization.authorization_id,
            execution_status=ExecutionStatus.BLOCKED,
            result_data={},
            timestamp=now,
            blocked_reason=f"Authorization decision is {authorization.decision.value}",
        )

    # Gate check 3: Single-use token (INV-07)
    try:
        check_inv_07_single_use(authorization, state)
    except InvariantViolation as e:
        logger.warning(
            "Execution BLOCKED for intent %s — token already consumed",
            intent.intent_id,
        )
        return ExecutionResult(
            intent_id=intent.intent_id,
            authorization_id=authorization.authorization_id,
            execution_status=ExecutionStatus.BLOCKED,
            result_data={},
            timestamp=now,
            blocked_reason=str(e),
        )

    # Gate check 4: Token expiration
    if authorization.expiration_timestamp > 0 and now > authorization.expiration_timestamp:
        logger.warning(
            "Execution BLOCKED for intent %s — authorization token expired",
            intent.intent_id,
        )
        return ExecutionResult(
            intent_id=intent.intent_id,
            authorization_id=authorization.authorization_id,
            execution_status=ExecutionStatus.BLOCKED,
            result_data={},
            timestamp=now,
            blocked_reason="Authorization token has expired",
        )

    # All gate checks passed — consume token and execute
    state.consume_token(authorization.authorization_id)

    result_data: dict[str, Any] = {}
    execution_status = ExecutionStatus.EXECUTED

    if action_handler is not None:
        try:
            result_data = action_handler(intent)
            logger.info(
                "Action executed for intent %s — result keys: %s",
                intent.intent_id,
                list(result_data.keys()),
            )
        except Exception as exc:
            logger.error(
                "Action FAILED for intent %s — %s",
                intent.intent_id,
                str(exc),
            )
            execution_status = ExecutionStatus.FAILED
            result_data = {"error": str(exc)}
    else:
        logger.info(
            "Execution gate passed for intent %s — no action handler provided (dry run)",
            intent.intent_id,
        )

    return ExecutionResult(
        intent_id=intent.intent_id,
        authorization_id=authorization.authorization_id,
        execution_status=execution_status,
        result_data=result_data,
        timestamp=now,
    )
