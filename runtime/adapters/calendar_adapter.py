"""
RIO Runtime — Calendar Adapter
================================

Production-style adapter for the ``create_event`` action type.

Supports two execution modes:
- **simulated**: Writes a structured JSON record to ``calendar_events.log``
  (default; safe for testing and demos).
- **live_stub**: Structured placeholder for Google Calendar / Microsoft
  Graph API integration.  Logs the full event payload and returns a
  stub external reference without actually creating an event.

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

logger = logging.getLogger("rio.adapter.calendar")


class CalendarAdapter(BaseAdapter):
    """Adapter for creating calendar events through the governed execution system."""

    adapter_id: str = "calendar"

    def execute(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
    ) -> AdapterResult:
        """Execute a create_event action.

        Parameters
        ----------
        intent : models.Intent
            Must contain parameters: title, time, duration.
        authorization : models.Authorization
            The authorization token (verified by execution gate).
        context : dict
            Runtime context with mode, calendar config, project_root, etc.

        Returns
        -------
        AdapterResult
        """
        mode = context.get("mode", "simulated")
        params = intent.parameters if hasattr(intent, "parameters") else {}

        title = params.get("title", "")
        event_time = params.get("time", "")
        duration = params.get("duration", "")

        if not title or not event_time:
            return self._failure(
                "Missing required calendar parameters (title, time)",
                {"error": "missing_params", "title": title, "time": event_time},
                mode=mode,
            )

        try:
            if mode == "live_stub":
                return self._execute_live_stub(intent, authorization, context, params)
            else:
                return self._execute_simulated(intent, authorization, context, params)
        except Exception as exc:
            logger.error(
                "CALENDAR ADAPTER ERROR — intent=%s error=%s",
                intent.intent_id,
                str(exc),
            )
            return self._failure(
                f"Calendar adapter error: {str(exc)}",
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
        """Simulated mode: write to calendar_events.log."""
        project_root = context.get("project_root", "")
        cal_config = context.get("calendar", {})
        log_rel = cal_config.get("simulated_log", "runtime/data/calendar_events.log")
        log_path = os.path.join(project_root, log_rel)

        event_id = f"EVT-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "event_id": event_id,
            "intent_id": intent.intent_id,
            "authorization_id": authorization.authorization_id,
            "title": params.get("title", ""),
            "time": params.get("time", ""),
            "duration": params.get("duration", ""),
            "location": params.get("location", ""),
            "attendees": params.get("attendees", []),
            "description": params.get("description", ""),
            "organizer": intent.requested_by,
            "mode": "simulated",
            "timestamp": now,
        }

        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        with open(log_path, "a") as f:
            f.write(json.dumps(record) + "\n")

        logger.info(
            "EVENT CREATED (simulated) — intent=%s title=%s time=%s event_id=%s",
            intent.intent_id,
            params.get("title"),
            params.get("time"),
            event_id,
        )

        return self._success(
            f"Calendar event created (simulated): {params.get('title')} at {params.get('time')}",
            raw=record,
            external_reference=event_id,
            mode="simulated",
        )

    def _execute_live_stub(
        self,
        intent: Any,
        authorization: Any,
        context: Dict[str, Any],
        params: Dict[str, Any],
    ) -> AdapterResult:
        """Live stub mode: structured placeholder for Google/Microsoft Calendar API.

        In production, this method would:
        1. Authenticate with Google Calendar / Microsoft Graph API
        2. Create the calendar event
        3. Return the real event ID as external_reference

        Currently returns a stub response for integration testing.
        """
        cal_config = context.get("calendar", {}).get("live_stub", {})
        event_id = f"STUB-EVT-{uuid.uuid4().hex[:12].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        stub_response = {
            "event_id": event_id,
            "intent_id": intent.intent_id,
            "authorization_id": authorization.authorization_id,
            "provider": cal_config.get("provider", "google"),
            "calendar_id": cal_config.get("calendar_id", "primary"),
            "title": params.get("title", ""),
            "time": params.get("time", ""),
            "duration": params.get("duration", ""),
            "mode": "live_stub",
            "status": "pending",
            "timestamp": now,
            "note": "Live stub — event not actually created. Configure API credentials for real integration.",
        }

        logger.info(
            "EVENT QUEUED (live_stub) — intent=%s title=%s provider=%s event_id=%s",
            intent.intent_id,
            params.get("title"),
            cal_config.get("provider", "google"),
            event_id,
        )

        return self._success(
            f"Calendar event queued (live_stub): {params.get('title')} via {cal_config.get('provider', 'google')}",
            raw=stub_response,
            external_reference=event_id,
            mode="live_stub",
        )
