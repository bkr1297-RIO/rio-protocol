"""
Email Connector (Simulated)
===========================

Simulates sending an email by appending a structured record to
``runtime/data/sent_emails.log``.  In a production deployment this
would be replaced by an SMTP or API-based email service.

Spec reference: /spec/governed_execution_protocol.md — Stage 6
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

from .base_connector import BaseConnector, ExecutionResult

logger = logging.getLogger("rio.connector.email")

# Log file lives alongside the runtime package
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_EMAIL_LOG = os.path.join(_DATA_DIR, "sent_emails.log")


class EmailConnector(BaseConnector):
    """Simulated email connector.

    Reads ``recipient``, ``subject``, and ``body`` from
    ``intent.parameters`` and writes them to the email log file.
    """

    connector_id: str = "email"

    def execute(self, intent: Any) -> ExecutionResult:
        """Simulate sending an email.

        Parameters
        ----------
        intent : models.Intent
            Must contain ``parameters.recipient``, ``parameters.subject``,
            and ``parameters.body``.

        Returns
        -------
        ExecutionResult
        """
        params = intent.parameters if hasattr(intent, "parameters") else {}

        recipient = params.get("recipient")
        subject = params.get("subject", "(no subject)")
        body = params.get("body", "")

        if not recipient:
            logger.warning("Email connector: missing recipient")
            return self._failure(
                "Missing required parameter: recipient",
                {"error": "recipient_missing"},
            )

        record = {
            "intent_id": intent.intent_id if hasattr(intent, "intent_id") else "unknown",
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            os.makedirs(_DATA_DIR, exist_ok=True)
            with open(_EMAIL_LOG, "a") as fh:
                fh.write(json.dumps(record) + "\n")
            logger.info("Email sent (simulated) to %s — subject: %s", recipient, subject)
            return self._success(
                f"Email sent to {recipient}: {subject}",
                record,
            )
        except OSError as exc:
            logger.error("Email connector I/O error: %s", exc)
            return self._failure(
                f"I/O error writing email log: {exc}",
                {"error": str(exc)},
            )
