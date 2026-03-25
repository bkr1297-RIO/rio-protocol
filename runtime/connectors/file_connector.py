"""
File Connector
==============

Supports governed file-system operations: ``write_file``,
``read_file``, and ``append_file``.  All operations are scoped to
the ``runtime/data/`` directory to prevent arbitrary filesystem access.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import logging
import os
from typing import Any

from .base_connector import BaseConnector, ExecutionResult

logger = logging.getLogger("rio.connector.file")

# Sandbox: all file operations are confined to the data directory
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


class FileConnector(BaseConnector):
    """Governed file-system connector.

    Supported sub-actions (via ``intent.parameters["operation"]``):
    - ``write_file``  — create or overwrite a file
    - ``read_file``   — read file contents
    - ``append_file`` — append to an existing file
    """

    connector_id: str = "file"

    def execute(self, intent: Any) -> ExecutionResult:
        """Execute a file-system operation.

        Parameters
        ----------
        intent : models.Intent
            Must contain ``parameters.operation`` and ``parameters.filename``.
            For write/append, ``parameters.content`` is required.

        Returns
        -------
        ExecutionResult
        """
        params = intent.parameters if hasattr(intent, "parameters") else {}
        operation = params.get("operation", intent.action_type if hasattr(intent, "action_type") else "")
        filename = params.get("filename")

        if not filename:
            return self._failure("Missing required parameter: filename", {"error": "filename_missing"})

        # Prevent path traversal — resolve to data dir
        safe_path = os.path.join(_DATA_DIR, os.path.basename(filename))
        os.makedirs(_DATA_DIR, exist_ok=True)

        try:
            if operation in ("write_file", "write"):
                content = params.get("content", "")
                with open(safe_path, "w") as fh:
                    fh.write(content)
                logger.info("File written: %s (%d bytes)", safe_path, len(content))
                return self._success(
                    f"File written: {os.path.basename(safe_path)} ({len(content)} bytes)",
                    {"path": safe_path, "bytes_written": len(content)},
                )

            elif operation in ("read_file", "read"):
                if not os.path.exists(safe_path):
                    return self._failure(
                        f"File not found: {os.path.basename(safe_path)}",
                        {"error": "file_not_found"},
                    )
                with open(safe_path, "r") as fh:
                    content = fh.read()
                logger.info("File read: %s (%d bytes)", safe_path, len(content))
                return self._success(
                    f"File read: {os.path.basename(safe_path)} ({len(content)} bytes)",
                    {"path": safe_path, "content": content, "bytes_read": len(content)},
                )

            elif operation in ("append_file", "append"):
                content = params.get("content", "")
                with open(safe_path, "a") as fh:
                    fh.write(content)
                logger.info("File appended: %s (%d bytes)", safe_path, len(content))
                return self._success(
                    f"File appended: {os.path.basename(safe_path)} ({len(content)} bytes)",
                    {"path": safe_path, "bytes_appended": len(content)},
                )

            else:
                return self._failure(
                    f"Unsupported file operation: {operation}",
                    {"error": "unsupported_operation", "operation": operation},
                )

        except OSError as exc:
            logger.error("File connector I/O error: %s", exc)
            return self._failure(f"I/O error: {exc}", {"error": str(exc)})
