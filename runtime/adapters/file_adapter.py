"""
RIO Runtime — File Adapter
============================

Production-style adapter for file operations: ``read_file``,
``write_file``, and ``append_file``.

All file operations are constrained to a safe sandbox directory
(``runtime/data/sandbox/`` by default) to prevent path traversal
attacks or writes to arbitrary locations.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

from .base_adapter import BaseAdapter, AdapterResult

logger = logging.getLogger("rio.adapter.file")


class FileAdapter(BaseAdapter):
    """Adapter for governed file operations within a sandboxed directory."""

    adapter_id: str = "file"

    def execute(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
    ) -> AdapterResult:
        """Execute a file operation (read_file, write_file, append_file).

        Parameters
        ----------
        intent : models.Intent
            action_type determines the operation.
            parameters must include: filename (and content for write/append).
        authorization : models.Authorization
            The authorization token (verified by execution gate).
        context : dict
            Runtime context with sandbox_path, mode, etc.

        Returns
        -------
        AdapterResult
        """
        mode = context.get("mode", "simulated")
        sandbox_path = context.get("sandbox_path", "")
        params = intent.parameters if hasattr(intent, "parameters") else {}
        action = intent.action_type if hasattr(intent, "action_type") else params.get("operation", "")

        filename = params.get("filename", "")
        if not filename:
            return self._failure(
                "Missing required parameter: filename",
                {"error": "missing_filename"},
                mode=mode,
            )

        # ── Sandbox enforcement ────────────────────────────────────
        if not sandbox_path:
            return self._failure(
                "Sandbox path not configured",
                {"error": "no_sandbox_path"},
                mode=mode,
            )

        # Resolve and validate path is within sandbox
        target_path = os.path.normpath(os.path.join(sandbox_path, filename))
        sandbox_abs = os.path.normpath(sandbox_path)

        if not target_path.startswith(sandbox_abs + os.sep) and target_path != sandbox_abs:
            logger.warning(
                "FILE ADAPTER BLOCKED — path traversal attempt: filename=%s resolved=%s sandbox=%s",
                filename,
                target_path,
                sandbox_abs,
            )
            return self._failure(
                f"Path traversal blocked: file must be within sandbox ({sandbox_abs})",
                {
                    "error": "path_traversal",
                    "filename": filename,
                    "resolved_path": target_path,
                    "sandbox_path": sandbox_abs,
                },
                mode=mode,
            )

        # Ensure sandbox directory exists
        os.makedirs(sandbox_path, exist_ok=True)

        try:
            if action in ("write_file", "write"):
                return self._write_file(intent, authorization, context, target_path, params)
            elif action in ("read_file", "read"):
                return self._read_file(intent, authorization, context, target_path, params)
            elif action in ("append_file", "append"):
                return self._append_file(intent, authorization, context, target_path, params)
            else:
                return self._failure(
                    f"Unknown file operation: {action}",
                    {"error": "unknown_operation", "action": action},
                    mode=mode,
                )
        except Exception as exc:
            logger.error(
                "FILE ADAPTER ERROR — intent=%s action=%s error=%s",
                intent.intent_id,
                action,
                str(exc),
            )
            return self._failure(
                f"File adapter error: {str(exc)}",
                {"error": str(exc), "action": action, "filename": filename},
                mode=mode,
            )

    def _write_file(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        target_path: str,
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Write content to a file (creates or overwrites)."""
        content = params.get("content", "")

        # Ensure parent directory exists
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        with open(target_path, "w") as f:
            f.write(content)

        logger.info(
            "FILE WRITTEN — intent=%s path=%s bytes=%d",
            intent.intent_id,
            target_path,
            len(content),
        )

        return self._success(
            f"File written: {os.path.basename(target_path)} ({len(content)} bytes)",
            raw={
                "operation": "write_file",
                "path": target_path,
                "filename": os.path.basename(target_path),
                "bytes_written": len(content),
                "intent_id": intent.intent_id,
                "authorization_id": authorization.authorization_id,
            },
            external_reference=target_path,
            mode=context.get("mode", "simulated"),
        )

    def _read_file(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        target_path: str,
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Read content from a file."""
        if not os.path.exists(target_path):
            return self._failure(
                f"File not found: {os.path.basename(target_path)}",
                {"error": "file_not_found", "path": target_path},
                mode=context.get("mode", "simulated"),
            )

        with open(target_path, "r") as f:
            content = f.read()

        logger.info(
            "FILE READ — intent=%s path=%s bytes=%d",
            intent.intent_id,
            target_path,
            len(content),
        )

        return self._success(
            f"File read: {os.path.basename(target_path)} ({len(content)} bytes)",
            raw={
                "operation": "read_file",
                "path": target_path,
                "filename": os.path.basename(target_path),
                "content": content,
                "bytes_read": len(content),
                "intent_id": intent.intent_id,
                "authorization_id": authorization.authorization_id,
            },
            external_reference=target_path,
            mode=context.get("mode", "simulated"),
        )

    def _append_file(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        target_path: str,
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Append content to a file (creates if not exists)."""
        content = params.get("content", "")

        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        with open(target_path, "a") as f:
            f.write(content)

        logger.info(
            "FILE APPENDED — intent=%s path=%s bytes=%d",
            intent.intent_id,
            target_path,
            len(content),
        )

        return self._success(
            f"File appended: {os.path.basename(target_path)} ({len(content)} bytes)",
            raw={
                "operation": "append_file",
                "path": target_path,
                "filename": os.path.basename(target_path),
                "bytes_appended": len(content),
                "intent_id": intent.intent_id,
                "authorization_id": authorization.authorization_id,
            },
            external_reference=target_path,
            mode=context.get("mode", "simulated"),
        )
