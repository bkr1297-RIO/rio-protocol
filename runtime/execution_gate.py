"""
RIO Runtime — Stage 6: Execution Gate

The Execution Gate is the final checkpoint before any action is executed.
It verifies four conditions before allowing execution:

1. Kill switch OFF (INV-08).
2. Decision is ALLOW.
3. Token has not been used before (INV-07: single-use).
4. Token has not expired.

If all conditions pass, the action is executed through the **Adapter
Registry** (preferred), falling back to the legacy Connector Registry
or a provided action_handler.  The result is passed to the Receipt stage.
If any condition fails, execution is blocked and a receipt is still
generated (fail-closed).

Execution priority:
1. Adapter Registry (production path) — if ``use_adapters=True``
2. Legacy action_handler callable — if provided
3. Connector Registry (legacy path) — if ``use_connectors=True``
4. Dry run — no execution

Spec reference: /spec/07_execution.md
Protocol stage: Step 6 of the 8-step Governed Execution Protocol
Related invariants: INV-01, INV-07 (Single-Use), INV-08 (Kill Switch Override)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .adapters.adapter_registry import get_adapter, get_adapter_context
from .adapters.base_adapter import AdapterResult
from .connectors.base_connector import ExecutionResult as ConnectorResult
from .connectors.connector_registry import get_connector
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
    connector_id: str = ""
    adapter_id: str = ""
    external_reference: str = ""


def execute(
    intent: Intent,
    authorization: Authorization,
    state: SystemState,
    action_handler: Optional[Callable[[Intent], dict[str, Any]]] = None,
    use_connectors: bool = True,
    use_adapters: bool = True,
) -> ExecutionResult:
    """
    Evaluate gate conditions and execute the action if all pass.

    Gate checks (in order):
    1. Kill switch OFF (INV-08)
    2. Decision is ALLOW
    3. Token not previously consumed (INV-07)
    4. Token has not expired

    Execution priority (after gate checks pass):
    1. Adapter Registry — if ``use_adapters`` is True (default)
    2. Legacy action_handler — if provided
    3. Connector Registry — if ``use_connectors`` is True
    4. Dry run — no execution

    Args:
        intent: The canonical Intent.
        authorization: The Authorization token from the Authorization stage.
        state: The current system state.
        action_handler: Optional callable that performs the actual action.
            Receives the Intent and returns a result dict.
        use_connectors: If True (default), use the connector registry
            as a fallback when no adapter or action_handler is available.
        use_adapters: If True (default), use the adapter registry as
            the primary execution path.

    Returns:
        An ExecutionResult recording the outcome.
    """
    now = int(time.time() * 1000)

    # Gate check 1: Kill switch (INV-08)
    try:
        check_inv_08_kill_switch(state)
    except InvariantViolation as e:
        logger.warning(
            "GATE BLOCKED — intent=%s reason=kill_switch_engaged",
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
            "GATE BLOCKED — intent=%s reason=decision_%s",
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
            "GATE BLOCKED — intent=%s reason=token_already_consumed token=%s",
            intent.intent_id,
            authorization.authorization_id,
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
            "GATE BLOCKED — intent=%s reason=token_expired token=%s expired_at=%d now=%d",
            intent.intent_id,
            authorization.authorization_id,
            authorization.expiration_timestamp,
            now,
        )
        return ExecutionResult(
            intent_id=intent.intent_id,
            authorization_id=authorization.authorization_id,
            execution_status=ExecutionStatus.BLOCKED,
            result_data={},
            timestamp=now,
            blocked_reason="Authorization token has expired",
        )

    # ── All gate checks passed — consume token and execute ──────────
    state.consume_token(authorization.authorization_id)
    logger.info(
        "GATE PASSED — intent=%s token=%s consumed",
        intent.intent_id,
        authorization.authorization_id,
    )

    result_data: dict[str, Any] = {}
    execution_status = ExecutionStatus.EXECUTED
    connector_id = ""
    adapter_id = ""
    external_reference = ""

    # ── Execution path 1: Adapter Registry (production) ────────────
    if use_adapters:
        adapter = get_adapter(intent.action_type)
        adapter_id = adapter.adapter_id

        # Skip default adapter (no registered adapter) — fall through
        if adapter_id != "default":
            adapter_context = get_adapter_context()
            logger.info(
                "ADAPTER RESOLVED — intent=%s action=%s adapter=%s mode=%s",
                intent.intent_id,
                intent.action_type,
                adapter_id,
                adapter_context.get("mode", "simulated"),
            )

            try:
                adapter_result: AdapterResult = adapter.execute(
                    intent, authorization, adapter_context
                )
                result_data = {
                    "execution_status": adapter_result.execution_status,
                    "result_summary": adapter_result.result_summary,
                    "raw_result": adapter_result.raw_result,
                    "adapter_id": adapter_result.adapter_id,
                    "external_reference": adapter_result.external_reference,
                    "mode": adapter_result.mode,
                    "adapter_timestamp": adapter_result.timestamp,
                }
                external_reference = adapter_result.external_reference

                if adapter_result.execution_status == "success":
                    logger.info(
                        "ADAPTER EXECUTED — intent=%s adapter=%s summary=%s ref=%s",
                        intent.intent_id,
                        adapter_id,
                        adapter_result.result_summary,
                        adapter_result.external_reference,
                    )
                else:
                    logger.warning(
                        "ADAPTER FAILED — intent=%s adapter=%s summary=%s",
                        intent.intent_id,
                        adapter_id,
                        adapter_result.result_summary,
                    )
                    execution_status = ExecutionStatus.FAILED
                    result_data["error"] = adapter_result.result_summary

            except Exception as exc:
                logger.error(
                    "ADAPTER ERROR — intent=%s adapter=%s error=%s",
                    intent.intent_id,
                    adapter_id,
                    str(exc),
                )
                execution_status = ExecutionStatus.FAILED
                result_data = {"error": str(exc), "adapter_id": adapter_id}

            return ExecutionResult(
                intent_id=intent.intent_id,
                authorization_id=authorization.authorization_id,
                execution_status=execution_status,
                result_data=result_data,
                timestamp=now,
                adapter_id=adapter_id,
                external_reference=external_reference,
            )

    # ── Execution path 2: Legacy action_handler ────────────────────
    if action_handler is not None:
        try:
            result_data = action_handler(intent)
            logger.info(
                "ACTION EXECUTED (handler) — intent=%s result_keys=%s",
                intent.intent_id,
                list(result_data.keys()),
            )
        except Exception as exc:
            logger.error(
                "ACTION FAILED (handler) — intent=%s error=%s",
                intent.intent_id,
                str(exc),
            )
            execution_status = ExecutionStatus.FAILED
            result_data = {"error": str(exc)}

    # ── Execution path 3: Legacy Connector Registry ────────────────
    elif use_connectors:
        connector = get_connector(intent.action_type)
        connector_id = connector.connector_id
        logger.info(
            "CONNECTOR RESOLVED — intent=%s action=%s connector=%s",
            intent.intent_id,
            intent.action_type,
            connector_id,
        )

        try:
            connector_result: ConnectorResult = connector.execute(intent)
            result_data = {
                "execution_status": connector_result.execution_status,
                "result_summary": connector_result.result_summary,
                "raw_result": connector_result.raw_result,
                "connector_id": connector_result.connector_id,
                "connector_timestamp": connector_result.timestamp,
            }

            if connector_result.execution_status == "success":
                logger.info(
                    "CONNECTOR EXECUTED — intent=%s connector=%s summary=%s",
                    intent.intent_id,
                    connector_id,
                    connector_result.result_summary,
                )
            else:
                logger.warning(
                    "CONNECTOR FAILED — intent=%s connector=%s summary=%s",
                    intent.intent_id,
                    connector_id,
                    connector_result.result_summary,
                )
                execution_status = ExecutionStatus.FAILED
                result_data["error"] = connector_result.result_summary

        except Exception as exc:
            logger.error(
                "CONNECTOR ERROR — intent=%s connector=%s error=%s",
                intent.intent_id,
                connector_id,
                str(exc),
            )
            execution_status = ExecutionStatus.FAILED
            result_data = {"error": str(exc), "connector_id": connector_id}

    else:
        logger.info(
            "GATE PASSED (dry run) — intent=%s no_adapter no_handler no_connector",
            intent.intent_id,
        )

    return ExecutionResult(
        intent_id=intent.intent_id,
        authorization_id=authorization.authorization_id,
        execution_status=execution_status,
        result_data=result_data,
        timestamp=now,
        connector_id=connector_id,
        adapter_id=adapter_id,
        external_reference=external_reference,
    )
