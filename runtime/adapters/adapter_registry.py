"""
RIO Runtime — Adapter Registry
===============================

Maps intent ``action_type`` values to the adapter instance that can
execute them.  The Execution Gate calls ``get_adapter(action_type)``
to resolve the appropriate adapter and ``get_adapter_context()`` to
obtain the runtime configuration.

The registry loads config.json at import time and exposes a context
dict that adapters use to determine execution mode, sandbox paths,
whitelisted domains, etc.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

from .base_adapter import BaseAdapter, AdapterResult

logger = logging.getLogger("rio.adapter.registry")


# ── Load Configuration ─────────────────────────────────────────────
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def _load_config() -> Dict[str, Any]:
    """Load adapter configuration from config.json."""
    try:
        with open(_CONFIG_PATH, "r") as f:
            config = json.load(f)
        logger.info(
            "Adapter config loaded: mode=%s, allowed_actions=%d, whitelisted_domains=%d",
            config.get("mode", "simulated"),
            len(config.get("allowed_actions", [])),
            len(config.get("whitelisted_domains", [])),
        )
        return config
    except FileNotFoundError:
        logger.warning("Adapter config not found at %s — using defaults", _CONFIG_PATH)
        return {
            "mode": "simulated",
            "allowed_actions": [],
            "whitelisted_domains": [],
            "sandbox_path": "runtime/data/sandbox",
        }


_config: Dict[str, Any] = _load_config()


def get_adapter_config() -> Dict[str, Any]:
    """Return the current adapter configuration."""
    return dict(_config)


def get_adapter_context() -> Dict[str, Any]:
    """Build the runtime context dict passed to adapters during execution.

    This includes mode, sandbox path, whitelisted domains, and any
    adapter-specific configuration sections.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sandbox_rel = _config.get("sandbox_path", "runtime/data/sandbox")
    sandbox_abs = os.path.join(project_root, sandbox_rel)

    return {
        "mode": _config.get("mode", "simulated"),
        "allowed_actions": _config.get("allowed_actions", []),
        "whitelisted_domains": _config.get("whitelisted_domains", []),
        "sandbox_path": sandbox_abs,
        "project_root": project_root,
        "email": _config.get("email", {}),
        "calendar": _config.get("calendar", {}),
        "http": _config.get("http", {}),
    }


def reload_config() -> None:
    """Reload configuration from disk (useful after config changes)."""
    global _config
    _config = _load_config()
    logger.info("Adapter config reloaded")


# ── Default Adapter (fallback) ─────────────────────────────────────
class DefaultAdapter(BaseAdapter):
    """Fallback adapter for action types without a registered handler.

    Returns a failure result indicating no adapter is available.
    """

    adapter_id: str = "default"

    def execute(self, intent, authorization, context) -> AdapterResult:
        action = intent.action_type if hasattr(intent, "action_type") else "unknown"
        logger.warning("No adapter registered for action_type=%s", action)
        return self._failure(
            f"No adapter registered for action type: {action}",
            {"error": "no_adapter", "action_type": action},
        )


# ── Lazy imports to avoid circular dependencies ────────────────────
def _build_registry() -> Dict[str, BaseAdapter]:
    """Build the adapter registry with lazy imports."""
    from .email_adapter import EmailAdapter
    from .calendar_adapter import CalendarAdapter
    from .file_adapter import FileAdapter
    from .http_adapter import HTTPAdapter

    return {
        # Email
        "send_email": EmailAdapter(),
        # Calendar
        "create_event": CalendarAdapter(),
        # File operations
        "write_file": FileAdapter(),
        "read_file": FileAdapter(),
        "append_file": FileAdapter(),
        # HTTP
        "http_request": HTTPAdapter(),
    }


_adapter_map: Optional[Dict[str, BaseAdapter]] = None
_default_adapter = DefaultAdapter()


def _get_registry() -> Dict[str, BaseAdapter]:
    """Get or lazily initialise the adapter registry."""
    global _adapter_map
    if _adapter_map is None:
        _adapter_map = _build_registry()
        logger.info(
            "Adapter registry initialised: %d action types registered",
            len(_adapter_map),
        )
    return _adapter_map


def get_adapter(action_type: str) -> BaseAdapter:
    """Resolve the adapter for a given action type.

    Parameters
    ----------
    action_type : str
        The ``action_type`` field from the canonical intent.

    Returns
    -------
    BaseAdapter
        The registered adapter, or ``DefaultAdapter`` if none is registered.
    """
    registry = _get_registry()
    adapter = registry.get(action_type, _default_adapter)
    logger.debug("Resolved adapter for %s → %s", action_type, adapter.adapter_id)
    return adapter


def register_adapter(action_type: str, adapter: BaseAdapter) -> None:
    """Register a new adapter for an action type.

    Parameters
    ----------
    action_type : str
        The action type to map.
    adapter : BaseAdapter
        The adapter instance to use.
    """
    registry = _get_registry()
    registry[action_type] = adapter
    logger.info(
        "Registered adapter %s for action_type=%s",
        adapter.adapter_id,
        action_type,
    )
