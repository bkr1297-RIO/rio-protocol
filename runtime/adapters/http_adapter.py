"""
RIO Runtime — HTTP Adapter
============================

Production-style adapter for the ``http_request`` action type.

Supports two execution modes:
- **simulated**: Validates the request, checks domain whitelist, and
  writes a structured JSON record to ``http_requests.log`` with a
  simulated 200 response (default; safe for testing and demos).
- **live_stub**: Structured placeholder for real HTTP calls.
  Validates domain whitelist but does not actually make the request.

Domain whitelisting is enforced in all modes — requests to
non-whitelisted domains are blocked with a failure result.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import urlparse

from .base_adapter import BaseAdapter, AdapterResult

logger = logging.getLogger("rio.adapter.http")


class HTTPAdapter(BaseAdapter):
    """Adapter for governed HTTP requests with domain whitelisting."""

    adapter_id: str = "http"

    def execute(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
    ) -> AdapterResult:
        """Execute an http_request action.

        Parameters
        ----------
        intent : models.Intent
            parameters must include: url, method (GET/POST).
            Optional: headers, body.
        authorization : models.Authorization
            The authorization token (verified by execution gate).
        context : dict
            Runtime context with whitelisted_domains, mode, http config, etc.

        Returns
        -------
        AdapterResult
        """
        mode = context.get("mode", "simulated")
        params = intent.parameters if hasattr(intent, "parameters") else {}

        url = params.get("url", "")
        method = params.get("method", "GET").upper()

        if not url:
            return self._failure(
                "Missing required parameter: url",
                {"error": "missing_url"},
                mode=mode,
            )

        if method not in ("GET", "POST"):
            return self._failure(
                f"Unsupported HTTP method: {method} (only GET and POST allowed)",
                {"error": "unsupported_method", "method": method},
                mode=mode,
            )

        # ── Domain whitelist enforcement ───────────────────────────
        whitelisted = context.get("whitelisted_domains", [])
        domain_check = self._check_domain_whitelist(url, whitelisted)
        if not domain_check["allowed"]:
            logger.warning(
                "HTTP ADAPTER BLOCKED — non-whitelisted domain: url=%s domain=%s",
                url,
                domain_check["domain"],
            )
            return self._failure(
                f"Domain not whitelisted: {domain_check['domain']}",
                {
                    "error": "domain_not_whitelisted",
                    "url": url,
                    "domain": domain_check["domain"],
                    "whitelisted_domains": whitelisted,
                },
                mode=mode,
            )

        try:
            if mode == "live_stub":
                return self._execute_live_stub(intent, authorization, context, params)
            else:
                return self._execute_simulated(intent, authorization, context, params)
        except Exception as exc:
            logger.error(
                "HTTP ADAPTER ERROR — intent=%s error=%s",
                intent.intent_id,
                str(exc),
            )
            return self._failure(
                f"HTTP adapter error: {str(exc)}",
                {"error": str(exc)},
                mode=mode,
            )

    def _check_domain_whitelist(
        self,
        url: str,
        whitelisted_domains: List[str],
    ) -> Dict[str, Any]:
        """Check if the URL's domain is in the whitelist.

        Returns
        -------
        dict
            ``{"allowed": bool, "domain": str}``
        """
        try:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
        except Exception:
            return {"allowed": False, "domain": "invalid_url"}

        if not domain:
            return {"allowed": False, "domain": "empty_domain"}

        # Check exact match or subdomain match
        for allowed in whitelisted_domains:
            if domain == allowed or domain.endswith("." + allowed):
                return {"allowed": True, "domain": domain}

        return {"allowed": False, "domain": domain}

    def _execute_simulated(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Simulated mode: write to http_requests.log with simulated response."""
        project_root = context.get("project_root", "")
        http_config = context.get("http", {})
        log_rel = http_config.get("simulated_log", "runtime/data/http_requests.log")
        log_path = os.path.join(project_root, log_rel)

        request_id = f"HTTP-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "request_id": request_id,
            "intent_id": intent.intent_id,
            "authorization_id": authorization.authorization_id,
            "method": params.get("method", "GET").upper(),
            "url": params.get("url", ""),
            "headers": params.get("headers", {}),
            "body": params.get("body", {}),
            "mode": "simulated",
            "timestamp": now,
            "response": {
                "status_code": 200,
                "body": {"status": "ok", "simulated": True, "request_id": request_id},
                "headers": {"Content-Type": "application/json"},
            },
        }

        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        logger.info(
            "HTTP REQUEST (simulated) — intent=%s method=%s url=%s request_id=%s",
            intent.intent_id,
            params.get("method", "GET"),
            params.get("url"),
            request_id,
        )

        return self._success(
            f"HTTP {params.get('method', 'GET')} {params.get('url')} → 200 OK (simulated)",
            raw=record,
            external_reference=request_id,
            mode="simulated",
        )

    def _execute_live_stub(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Live stub mode: structured placeholder for real HTTP calls.

        In production, this method would:
        1. Make the actual HTTP request using requests/httpx
        2. Apply timeout and retry policies from config
        3. Return the real response

        Currently returns a stub response for integration testing.
        """
        http_config = context.get("http", {})
        request_id = f"STUB-HTTP-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        stub_response = {
            "request_id": request_id,
            "intent_id": intent.intent_id,
            "authorization_id": authorization.authorization_id,
            "method": params.get("method", "GET").upper(),
            "url": params.get("url", ""),
            "mode": "live_stub",
            "timeout": http_config.get("timeout_seconds", 30),
            "max_retries": http_config.get("max_retries", 3),
            "status": "pending",
            "timestamp": now,
            "note": "Live stub — request not actually sent. Enable live mode for real HTTP calls.",
        }

        logger.info(
            "HTTP REQUEST QUEUED (live_stub) — intent=%s method=%s url=%s request_id=%s",
            intent.intent_id,
            params.get("method", "GET"),
            params.get("url"),
            request_id,
        )

        return self._success(
            f"HTTP {params.get('method', 'GET')} {params.get('url')} queued (live_stub)",
            raw=stub_response,
            external_reference=request_id,
            mode="live_stub",
        )
