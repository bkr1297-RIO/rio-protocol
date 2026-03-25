"""
RIO Runtime — Email Adapter
============================

Production-style adapter for the ``send_email`` action type.

Supports two execution modes:
- **simulated**: Writes a structured JSON record to ``sent_emails.log``
  (default; safe for testing and demos).
- **live_stub**: Structured placeholder for real SMTP/API integration.
  Logs the full email payload and returns a stub external reference
  without actually sending.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from .base_adapter import BaseAdapter, AdapterResult

logger = logging.getLogger("rio.adapter.email")


class EmailAdapter(BaseAdapter):
    """Adapter for sending emails through the governed execution system."""

    adapter_id: str = "email"

    def execute(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
    ) -> AdapterResult:
        """Execute a send_email action.

        Parameters
        ----------
        intent : models.Intent
            Must contain parameters: recipient, subject, body.
        authorization : models.Authorization
            The authorization token (verified by execution gate).
        context : dict
            Runtime context with mode, email config, project_root, etc.

        Returns
        -------
        AdapterResult
        """
        mode = context.get("mode", "simulated")
        params = intent.parameters if hasattr(intent, "parameters") else {}

        recipient = params.get("recipient", "")
        subject = params.get("subject", "")
        body = params.get("body", "")

        if not recipient or not subject:
            return self._failure(
                "Missing required email parameters (recipient, subject)",
                {"error": "missing_params", "recipient": recipient, "subject": subject},
                mode=mode,
            )

        try:
            if mode == "live_stub":
                return self._execute_live_stub(intent, authorization, context, params)
            else:
                return self._execute_simulated(intent, authorization, context, params)
        except Exception as exc:
            logger.error(
                "EMAIL ADAPTER ERROR — intent=%s error=%s",
                intent.intent_id,
                str(exc),
            )
            return self._failure(
                f"Email adapter error: {str(exc)}",
                {"error": str(exc)},
                mode=mode,
            )

    def _execute_simulated(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Simulated mode: write to sent_emails.log."""
        project_root = context.get("project_root", "")
        email_config = context.get("email", {})
        log_rel = email_config.get("simulated_log", "runtime/data/sent_emails.log")
        log_path = os.path.join(project_root, log_rel)

        # Build structured email record
        message_id = f"SIM-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "message_id": message_id,
            "intent_id": intent.intent_id,
            "authorization_id": authorization.authorization_id,
            "from": email_config.get("live_stub", {}).get("from_address", "rio@example.com"),
            "to": params.get("recipient", ""),
            "subject": params.get("subject", ""),
            "body": params.get("body", ""),
            "cc": params.get("cc", []),
            "bcc": params.get("bcc", []),
            "mode": "simulated",
            "timestamp": now,
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        logger.info(
            "EMAIL SENT (simulated) — intent=%s to=%s subject=%s message_id=%s",
            intent.intent_id,
            params.get("recipient"),
            params.get("subject"),
            message_id,
        )

        return self._success(
            f"Email sent (simulated) to {params.get('recipient')} — {params.get('subject')}",
            raw=record,
            external_reference=message_id,
            mode="simulated",
        )

    def _execute_live_stub(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Live stub mode: structured placeholder for real SMTP/API integration.

        In production, this method would:
        1. Connect to SMTP server or email API (SendGrid, SES, etc.)
        2. Authenticate with credentials from config
        3. Send the email
        4. Return the real message ID as external_reference

        Currently returns a stub response for integration testing.
        """
        email_config = context.get("email", {}).get("live_stub", {})
        message_id = f"STUB-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        stub_response = {
            "message_id": message_id,
            "intent_id": intent.intent_id,
            "authorization_id": authorization.authorization_id,
            "provider": email_config.get("provider", "smtp"),
            "host": email_config.get("host", ""),
            "from": email_config.get("from_address", "rio@example.com"),
            "to": params.get("recipient", ""),
            "subject": params.get("subject", ""),
            "mode": "live_stub",
            "status": "queued",
            "timestamp": now,
            "note": "Live stub — email not actually sent. Configure SMTP/API credentials for real delivery.",
        }

        logger.info(
            "EMAIL QUEUED (live_stub) — intent=%s to=%s provider=%s message_id=%s",
            intent.intent_id,
            params.get("recipient"),
            email_config.get("provider", "smtp"),
            message_id,
        )

        return self._success(
            f"Email queued (live_stub) to {params.get('recipient')} via {email_config.get('provider', 'smtp')}",
            raw=stub_response,
            external_reference=message_id,
            mode="live_stub",
        )
