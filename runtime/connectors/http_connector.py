"""
HTTP Connector (Simulated)
==========================

Simulates calling external APIs via GET and POST requests.
Does **not** make real network calls — returns deterministic
simulated responses and logs the request to
``runtime/data/http_requests.log``.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from .base_connector import BaseConnector, ExecutionResult

logger = logging.getLogger("rio.connector.http")

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_HTTP_LOG = os.path.join(_DATA_DIR, "http_requests.log")


class HTTPConnector(BaseConnector):
    """Simulated HTTP request connector.

    Reads ``method``, ``url``, ``headers``, and ``body`` from
    ``intent.parameters`` and produces a simulated response.
    """

    connector_id: str = "http"

    def execute(self, intent: Any) -> ExecutionResult:
        """Simulate an HTTP request.

        Parameters
        ----------
        intent : models.Intent
            Must contain ``parameters.method`` (GET|POST) and
            ``parameters.url``.  Optional: ``parameters.headers``,
            ``parameters.body``.

        Returns
        -------
        ExecutionResult
        """
        params = intent.parameters if hasattr(intent, "parameters") else {}
        method = params.get("method", "GET").upper()
        url = params.get("url")
        headers = params.get("headers", {})
        body = params.get("body")

        if not url:
            return self._failure("Missing required parameter: url", {"error": "url_missing"})

        if method not in ("GET", "POST"):
            return self._failure(
                f"Unsupported HTTP method: {method}",
                {"error": "unsupported_method", "method": method},
            )

        # Build simulated response
        simulated_response = {
            "status_code": 200,
            "body": {
                "message": f"Simulated {method} response",
                "url": url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        }

        # Log the request
        record = {
            "intent_id": intent.intent_id if hasattr(intent, "intent_id") else "unknown",
            "method": method,
            "url": url,
            "headers": headers,
            "request_body": body,
            "response": simulated_response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            os.makedirs(_DATA_DIR, exist_ok=True)
            with open(_HTTP_LOG, "a") as fh:
                fh.write(json.dumps(record) + "\n")
            logger.info("HTTP %s %s (simulated) — 200 OK", method, url)
            return self._success(
                f"HTTP {method} {url} — 200 OK (simulated)",
                {
                    "method": method,
                    "url": url,
                    "response_status": 200,
                    "response_body": simulated_response["body"],
                },
            )
        except OSError as exc:
            logger.error("HTTP connector I/O error: %s", exc)
            return self._failure(f"I/O error writing HTTP log: {exc}", {"error": str(exc)})
