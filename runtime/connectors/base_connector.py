"""
Base Connector
==============

Defines the abstract interface that every execution connector must
implement.  The Execution Gate calls ``connector.execute(intent)``
and receives a standardised ``ExecutionResult``.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

logger = logging.getLogger("rio.connector.base")


# ── Execution Result ────────────────────────────────────────────────
@dataclass
class ExecutionResult:
    """Standardised return value from every connector.

    Fields
    ------
    execution_status : str
        ``"success"`` or ``"failure"``.
    result_summary : str
        Human-readable one-line summary of what happened.
    raw_result : dict
        Connector-specific detail payload.
    connector_id : str
        Identifier of the connector that produced this result.
    timestamp : str
        ISO-8601 UTC timestamp of execution completion.
    """

    execution_status: str  # "success" | "failure"
    result_summary: str
    raw_result: Dict[str, Any] = field(default_factory=dict)
    connector_id: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


# ── Base Connector ──────────────────────────────────────────────────
class BaseConnector(ABC):
    """Abstract base class for all RIO execution connectors.

    Every connector must:
    1. Inherit from ``BaseConnector``.
    2. Implement ``execute(intent) -> ExecutionResult``.
    3. Return a valid ``ExecutionResult`` for both success and failure.
    4. Never raise unhandled exceptions — catch and wrap in a failure result.
    """

    connector_id: str = "base"

    @abstractmethod
    def execute(self, intent: Any) -> ExecutionResult:
        """Execute an action based on the canonical intent.

        Parameters
        ----------
        intent : models.Intent
            The canonical intent object produced by Stage 3.

        Returns
        -------
        ExecutionResult
            Standardised result containing status, summary, and raw detail.
        """
        ...

    def _success(self, summary: str, raw: Dict[str, Any] | None = None) -> ExecutionResult:
        """Helper to build a success result."""
        return ExecutionResult(
            execution_status="success",
            result_summary=summary,
            raw_result=raw or {},
            connector_id=self.connector_id,
        )

    def _failure(self, summary: str, raw: Dict[str, Any] | None = None) -> ExecutionResult:
        """Helper to build a failure result."""
        return ExecutionResult(
            execution_status="failure",
            result_summary=summary,
            raw_result=raw or {},
            connector_id=self.connector_id,
        )
