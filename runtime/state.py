"""
RIO Runtime — System State

Manages the mutable runtime state of the governed execution system, including
the kill switch, consumed token registry, ledger head hash, and version tracking
for policies and risk models.

In a production implementation, this state would be persisted to a durable store
with transactional guarantees. This reference skeleton uses in-memory state.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class SystemState:
    """
    Global runtime state for the Governed Execution Protocol.

    Attributes:
        kill_switch_active: Whether EKS-0 is currently engaged.
        kill_switch_engaged_by: Identity of the actor who engaged the kill switch.
        kill_switch_engaged_at: Timestamp when the kill switch was engaged.
        consumed_tokens: Set of authorization_ids that have been consumed (INV-07).
        ledger_head_hash: Hash of the most recent ledger entry (hash chain head).
        ledger_length: Number of entries in the ledger.
        policy_version: Current version identifier for the active policy set.
        risk_model_version: Current version identifier for the active risk model.
    """

    # Kill switch state
    kill_switch_active: bool = False
    kill_switch_engaged_by: str = ""
    kill_switch_engaged_at: int = 0

    # Token registry (INV-07: single-use enforcement)
    consumed_tokens: set[str] = field(default_factory=set)

    # Ledger state
    ledger_head_hash: str = ""
    ledger_length: int = 0

    # Governance versioning
    policy_version: str = "1.0.0"
    risk_model_version: str = "1.0.0"

    def engage_kill_switch(self, actor_id: str) -> None:
        """
        Engage the EKS-0 global execution kill switch.

        When engaged, no new executions may proceed regardless of policy decisions.
        All kill switch events must still generate receipts and ledger entries.

        Args:
            actor_id: Identity of the actor engaging the kill switch.
        """
        self.kill_switch_active = True
        self.kill_switch_engaged_by = actor_id
        self.kill_switch_engaged_at = int(time.time() * 1000)

    def disengage_kill_switch(self, actor_id: str) -> None:
        """
        Disengage the EKS-0 global execution kill switch.

        Requires authorized governance action. Disengagement must be recorded
        in the audit ledger.

        Args:
            actor_id: Identity of the actor disengaging the kill switch.
        """
        self.kill_switch_active = False
        self.kill_switch_engaged_by = ""
        self.kill_switch_engaged_at = 0

    def consume_token(self, authorization_id: str) -> None:
        """
        Mark an authorization token as consumed (single-use enforcement).

        Args:
            authorization_id: The authorization token ID to consume.

        Raises:
            ValueError: If the token has already been consumed.
        """
        if authorization_id in self.consumed_tokens:
            raise ValueError(
                f"Authorization token '{authorization_id}' has already been consumed"
            )
        self.consumed_tokens.add(authorization_id)

    def update_ledger_head(self, ledger_hash: str) -> None:
        """
        Update the ledger head hash after a successful append.

        Args:
            ledger_hash: Hash of the newly appended ledger entry.
        """
        self.ledger_head_hash = ledger_hash
        self.ledger_length += 1
