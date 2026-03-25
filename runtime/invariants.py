"""
RIO Runtime — Protocol Invariants

Implements verification checks for the eight protocol invariants (INV-01 through INV-08)
defined in /spec/protocol_invariants.md.

These invariants define safety and correctness properties that must never be violated
by any implementation of the Governed Execution Protocol.

In a production implementation, invariant violations would trigger alerts, block
execution, and generate audit records.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import (
        Authorization,
        Intent,
        LedgerEntry,
        Receipt,
        Request,
    )
    from .state import SystemState


class InvariantViolation(Exception):
    """Raised when a protocol invariant is violated."""

    def __init__(self, invariant_id: str, message: str) -> None:
        self.invariant_id = invariant_id
        super().__init__(f"[{invariant_id}] {message}")


# ---------------------------------------------------------------------------
# INV-01: Completeness
# Every action that enters the protocol must traverse all stages in order.
# No stage may be skipped.
# ---------------------------------------------------------------------------

def check_inv_01_completeness(
    request: Request,
    intent: Intent,
    authorization: Authorization,
    receipt: Receipt,
    ledger_entry: LedgerEntry,
) -> bool:
    """
    Verify that all stages produced their required artifacts.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if not request.request_id:
        raise InvariantViolation("INV-01", "Missing request_id — Intake stage incomplete")
    if not intent.intent_id:
        raise InvariantViolation("INV-01", "Missing intent_id — Structured Intent stage incomplete")
    if not authorization.authorization_id:
        raise InvariantViolation("INV-01", "Missing authorization_id — Authorization stage incomplete")
    if not receipt.receipt_id:
        raise InvariantViolation("INV-01", "Missing receipt_id — Receipt stage incomplete")
    if not ledger_entry.ledger_entry_id:
        raise InvariantViolation("INV-01", "Missing ledger_entry_id — Ledger stage incomplete")
    return True


# ---------------------------------------------------------------------------
# INV-02: Receipt Completeness
# Every action (approved, denied, or blocked) must produce a signed receipt.
# ---------------------------------------------------------------------------

def check_inv_02_receipt_completeness(receipt: Receipt) -> bool:
    """
    Verify that a receipt was generated and signed.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if not receipt.receipt_id:
        raise InvariantViolation("INV-02", "No receipt generated for action")
    if not receipt.receipt_hash:
        raise InvariantViolation("INV-02", "Receipt hash is missing")
    if not receipt.signature:
        raise InvariantViolation("INV-02", "Receipt signature is missing")
    return True


# ---------------------------------------------------------------------------
# INV-03: Ledger Completeness
# Every receipt must be appended to the audit ledger.
# ---------------------------------------------------------------------------

def check_inv_03_ledger_completeness(
    receipt: Receipt,
    ledger_entry: LedgerEntry,
) -> bool:
    """
    Verify that the receipt was recorded in the ledger.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if ledger_entry.receipt_id != receipt.receipt_id:
        raise InvariantViolation("INV-03", "Ledger entry does not reference the correct receipt")
    if not ledger_entry.ledger_hash:
        raise InvariantViolation("INV-03", "Ledger entry hash is missing")
    return True


# ---------------------------------------------------------------------------
# INV-04: Hash Chain Integrity
# Each ledger entry must be hash-linked to the previous entry.
# ---------------------------------------------------------------------------

def check_inv_04_hash_chain(
    ledger_entry: LedgerEntry,
    expected_previous_hash: str,
) -> bool:
    """
    Verify that the ledger entry's previous hash matches the expected value.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if ledger_entry.previous_ledger_hash != expected_previous_hash:
        raise InvariantViolation(
            "INV-04",
            f"Hash chain broken: expected {expected_previous_hash}, "
            f"got {ledger_entry.previous_ledger_hash}",
        )
    return True


# ---------------------------------------------------------------------------
# INV-05: Learning Separation
# The governance learning loop must not bypass runtime enforcement.
# ---------------------------------------------------------------------------

def check_inv_05_learning_separation(is_learning_context: bool, is_executing: bool) -> bool:
    """
    Verify that the learning loop is not directly executing actions.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if is_learning_context and is_executing:
        raise InvariantViolation(
            "INV-05",
            "Learning loop attempted to execute an action — "
            "learning must only produce recommendations",
        )
    return True


# ---------------------------------------------------------------------------
# INV-06: No Self-Authorization
# The requester and the authorizer must be distinct identities.
# AI agents cannot authorize their own requests.
# ---------------------------------------------------------------------------

def check_inv_06_no_self_authorization(
    intent: Intent,
    authorization: Authorization,
) -> bool:
    """
    Verify that the requester and authorizer are different identities.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if intent.requested_by == authorization.approver_id:
        raise InvariantViolation(
            "INV-06",
            f"Self-authorization detected: requester '{intent.requested_by}' "
            f"is the same as approver '{authorization.approver_id}'",
        )
    return True


# ---------------------------------------------------------------------------
# INV-07: Single-Use Authorization
# Each authorization token may be consumed exactly once.
# ---------------------------------------------------------------------------

def check_inv_07_single_use(
    authorization: Authorization,
    state: SystemState,
) -> bool:
    """
    Verify that the authorization token has not been previously consumed.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if authorization.authorization_id in state.consumed_tokens:
        raise InvariantViolation(
            "INV-07",
            f"Authorization token '{authorization.authorization_id}' has already been consumed",
        )
    return True


# ---------------------------------------------------------------------------
# INV-08: Kill Switch Override
# When the kill switch is engaged, no execution may proceed.
# ---------------------------------------------------------------------------

def check_inv_08_kill_switch(state: SystemState) -> bool:
    """
    Verify that the kill switch is not engaged before allowing execution.
    Returns True if compliant, raises InvariantViolation otherwise.
    """
    if state.kill_switch_active:
        raise InvariantViolation(
            "INV-08",
            "Kill switch (EKS-0) is engaged — all execution is halted",
        )
    return True
