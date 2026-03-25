"""
RIO Runtime — Base Adapter
==========================

Defines the abstract interface that every production-style execution
adapter must implement.  The Execution Gate resolves an adapter from
the Adapter Registry and calls ``adapter.execute(intent, authorization, context)``.

Unlike the simpler Connector layer, adapters:
- Receive the full authorization token for verification
- Accept a context dict with runtime config (mode, sandbox path, etc.)
- Return an ``AdapterResult`` that includes an ``external_reference``
  field for tracking real-system identifiers (ticket IDs, message IDs, etc.)

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("rio.adapter.base")


# ── Adapter Result ─────────────────────────────────────────────────
@dataclass
class AdapterResult:
    """Standardised return value from every adapter.

    Fields
    ------
    execution_status : str
        ``"success"`` or ``"failure"``.
    result_summary : str
        Human-readable one-line summary of what happened.
    raw_result : dict
        Adapter-specific detail payload.
    adapter_id : str
        Identifier of the adapter that produced this result.
    external_reference : str
        External system reference (message ID, ticket ID, event ID, etc.).
        Empty string if not applicable or in simulated mode.
    mode : str
        Execution mode used: ``"simulated"`` or ``"live_stub"``.
    timestamp : str
        ISO-8601 UTC timestamp of execution completion.
    """

    execution_status: str  # "success" | "failure"
    result_summary: str
    raw_result: Dict[str, Any] = field(default_factory=dict)
    adapter_id: str = ""
    external_reference: str = ""
    mode: str = "simulated"
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


# ── Base Adapter ───────────────────────────────────────────────────
class BaseAdapter(ABC):
    """Abstract base class for all RIO execution adapters.

    Every adapter must:
    1. Inherit from ``BaseAdapter``.
    2. Implement ``execute(intent, authorization, context) -> AdapterResult``.
    3. Return a valid ``AdapterResult`` for both success and failure.
    4. Never raise unhandled exceptions — catch and wrap in a failure result.
    5. Respect the ``mode`` field in context (simulated vs live_stub).
    """

    adapter_id: str = "base"

    @abstractmethod
    def execute(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
    ) -> AdapterResult:
        """Execute an action based on the canonical intent.

        Parameters
        ----------
        intent : models.Intent
            The canonical intent object produced by Stage 3.
        authorization : models.Authorization
            The authorization token from Stage 5.
        context : dict
            Runtime context including mode, sandbox_path, allowed_domains, etc.

        Returns
        -------
        AdapterResult
            Standardised result containing status, summary, raw detail,
            and external reference.
        """
        ...

    def _success(
        self,
        summary: str,
        raw: Dict[str, Any] | None = None,
        external_reference: str = "",
        mode: str = "simulated",
    ) -> AdapterResult:
        """Helper to build a success result."""
        return AdapterResult(
            execution_status="success",
            result_summary=summary,
            raw_result=raw or {},
            adapter_id=self.adapter_id,
            external_reference=external_reference,
            mode=mode,
        )

    def _failure(
        self,
        summary: str,
        raw: Dict[str, Any] | None = None,
        mode: str = "simulated",
    ) -> AdapterResult:
        """Helper to build a failure result."""
        return AdapterResult(
            execution_status="failure",
            result_summary=summary,
            raw_result=raw or {},
            adapter_id=self.adapter_id,
            mode=mode,
        )
