"""
RIO Runtime — EKS-0 Kill Switch

Implements the global execution kill switch as defined in /safety/EKS-0_kill_switch.md.

When the kill switch is engaged:
- No new executions may proceed regardless of policy decisions.
- All blocked requests must still generate receipts and ledger entries.
- The kill switch event itself is recorded in the audit ledger.

The kill switch can only be engaged or disengaged by authorized governance actors.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import SystemState

logger = logging.getLogger("rio.kill_switch")


@dataclass
class KillSwitchEvent:
    """Record of a kill switch engagement or disengagement."""
    event_type: str  # "ENGAGE" or "DISENGAGE"
    actor_id: str
    timestamp: int
    reason: str


def engage(state: SystemState, actor_id: str, reason: str = "") -> KillSwitchEvent:
    """
    Engage the EKS-0 global execution kill switch.

    When engaged, the Execution Gate (Stage 7) must block all new executions.
    This function updates the system state and returns an event record that
    must be passed to the Receipt and Ledger stages.

    Args:
        state: The current system state.
        actor_id: Identity of the actor engaging the kill switch.
        reason: Human-readable reason for engagement.

    Returns:
        KillSwitchEvent recording the engagement.

    Raises:
        RuntimeError: If the kill switch is already engaged.
    """
    if state.kill_switch_active:
        raise RuntimeError("Kill switch is already engaged")

    state.engage_kill_switch(actor_id)

    event = KillSwitchEvent(
        event_type="ENGAGE",
        actor_id=actor_id,
        timestamp=int(time.time() * 1000),
        reason=reason,
    )

    logger.warning(
        "EKS-0 ENGAGED by %s at %d — reason: %s",
        actor_id,
        event.timestamp,
        reason,
    )

    return event


def disengage(state: SystemState, actor_id: str, reason: str = "") -> KillSwitchEvent:
    """
    Disengage the EKS-0 global execution kill switch.

    Requires authorized governance action. The disengagement event must be
    recorded in the audit ledger before normal execution can resume.

    Args:
        state: The current system state.
        actor_id: Identity of the actor disengaging the kill switch.
        reason: Human-readable reason for disengagement.

    Returns:
        KillSwitchEvent recording the disengagement.

    Raises:
        RuntimeError: If the kill switch is not currently engaged.
    """
    if not state.kill_switch_active:
        raise RuntimeError("Kill switch is not currently engaged")

    state.disengage_kill_switch(actor_id)

    event = KillSwitchEvent(
        event_type="DISENGAGE",
        actor_id=actor_id,
        timestamp=int(time.time() * 1000),
        reason=reason,
    )

    logger.info(
        "EKS-0 DISENGAGED by %s at %d — reason: %s",
        actor_id,
        event.timestamp,
        reason,
    )

    return event


def is_active(state: SystemState) -> bool:
    """
    Check whether the kill switch is currently engaged.

    This function is called by the Execution Gate before allowing any action
    to proceed. If True, the gate must block execution and generate a
    KILL_SWITCH_BLOCKED receipt.

    Args:
        state: The current system state.

    Returns:
        True if the kill switch is engaged, False otherwise.
    """
    return state.kill_switch_active
