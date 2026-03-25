"""
Connector Registry
==================

Maps intent ``action_type`` values to the connector instance that
can execute them.  The Execution Gate calls
``get_connector(action_type)`` to resolve the appropriate connector.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from .base_connector import BaseConnector, ExecutionResult
from .email_connector import EmailConnector
from .file_connector import FileConnector
from .http_connector import HTTPConnector

logger = logging.getLogger("rio.connector.registry")


# ── Default Connector (fallback) ────────────────────────────────────
class DefaultConnector(BaseConnector):
    """Fallback connector for action types without a registered handler.

    Returns a failure result indicating no connector is available.
    """

    connector_id: str = "default"

    def execute(self, intent) -> ExecutionResult:
        action = intent.action_type if hasattr(intent, "action_type") else "unknown"
        logger.warning("No connector registered for action_type=%s", action)
        return self._failure(
            f"No connector registered for action type: {action}",
            {"error": "no_connector", "action_type": action},
        )


# ── Registry ────────────────────────────────────────────────────────
CONNECTOR_MAP: Dict[str, BaseConnector] = {
    # Email
    "send_email": EmailConnector(),
    # File operations
    "write_file": FileConnector(),
    "read_file": FileConnector(),
    "append_file": FileConnector(),
    # HTTP
    "http_request": HTTPConnector(),
}

_default_connector = DefaultConnector()


def get_connector(action_type: str) -> BaseConnector:
    """Resolve the connector for a given action type.

    Parameters
    ----------
    action_type : str
        The ``action_type`` field from the canonical intent.

    Returns
    -------
    BaseConnector
        The registered connector, or ``DefaultConnector`` if none is
        registered.
    """
    connector = CONNECTOR_MAP.get(action_type, _default_connector)
    logger.debug("Resolved connector for %s → %s", action_type, connector.connector_id)
    return connector


def register_connector(action_type: str, connector: BaseConnector) -> None:
    """Register a new connector for an action type.

    Parameters
    ----------
    action_type : str
        The action type to map.
    connector : BaseConnector
        The connector instance to use.
    """
    CONNECTOR_MAP[action_type] = connector
    logger.info("Registered connector %s for action_type=%s", connector.connector_id, action_type)
