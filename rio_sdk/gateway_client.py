"""
RIO SDK — Gateway HTTP Client

RIOClient — HTTP client for all gateway endpoints.

    client = RIOClient("http://localhost:5000")
    result = client.evaluate(intent)
    print(result.receipt.decision)
"""

from __future__ import annotations

from typing import Optional

import requests

from .models import (
    EvaluateResult,
    GateExecuteResult,
    GovernorSubmission,
    Intent,
    LedgerEntry,
)
from .exceptions import (
    RIOConnectionError,
    RIOHTTPError,
    RIOIntentBlockedError,
)


DEFAULT_TIMEOUT = 30


class RIOClient:
    """HTTP client for the RIO governance gateway."""

    def __init__(self, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def _request(self, method: str, path: str, **kwargs) -> dict:
        kwargs.setdefault("timeout", self._timeout)
        try:
            resp = self._session.request(method, self._url(path), **kwargs)
        except requests.ConnectionError as e:
            raise RIOConnectionError(f"Cannot reach gateway at {self._base_url}: {e}") from e
        except requests.Timeout as e:
            raise RIOConnectionError(f"Gateway timeout: {e}") from e

        if resp.status_code >= 400:
            raise RIOHTTPError(resp.status_code, resp.text)

        try:
            return resp.json()
        except ValueError:
            return {"_raw": resp.text}

    # ─── Governance Endpoints ─────────────────────────────────────

    def evaluate(self, intent: Intent) -> EvaluateResult:
        """POST /v1/governance/evaluate — Submit intent for governance evaluation."""
        data = self._request("POST", "/v1/governance/evaluate", json=intent.to_dict())
        result = EvaluateResult.from_dict(data)
        if result.decision == "block":
            raise RIOIntentBlockedError(data)
        return result

    def submit(self, intent: Intent) -> GovernorSubmission:
        """POST /v1/governor/submit — Submit for human approval (AWAITING_HUMAN_SIGNATURE)."""
        data = self._request("POST", "/v1/governor/submit", json=intent.to_dict())
        return GovernorSubmission.from_dict(data)

    def public_key_pem(self) -> str:
        """GET /v1/governance/public-key — Retrieve the gateway's Ed25519 public key (PEM)."""
        data = self._request("GET", "/v1/governance/public-key")
        return data.get("public_key", data.get("pem", ""))

    def ledger_latest(self) -> LedgerEntry:
        """GET /v1/governance/ledger/latest — Get the latest ledger entry."""
        data = self._request("GET", "/v1/governance/ledger/latest")
        return LedgerEntry.from_dict(data)

    def get_receipt(self, receipt_id: str) -> bytes:
        """GET /v1/governance/receipt/<id>/download — Download receipt as ZIP."""
        resp = self._session.get(
            self._url(f"/v1/governance/receipt/{receipt_id}/download"),
            timeout=self._timeout,
        )
        if resp.status_code >= 400:
            raise RIOHTTPError(resp.status_code, resp.text)
        return resp.content

    # ─── Gate Endpoints ───────────────────────────────────────────

    def gate_execute(self, tool: str, payload: dict,
                     intent_id: Optional[str] = None,
                     signature: Optional[str] = None,
                     nonce: Optional[str] = None) -> GateExecuteResult:
        """POST /api/gate/execute — Execute a tool through the governance gate."""
        body = {"tool": tool, "payload": payload}
        if intent_id:
            body["intent_id"] = intent_id
        if signature:
            body["signature"] = signature
        if nonce:
            body["nonce"] = nonce
        data = self._request("POST", "/api/gate/execute", json=body)
        return GateExecuteResult.from_dict(data)

    def gate_approve(self, approval_id: str) -> dict:
        """POST /api/gate/approve — Approve a pending action."""
        return self._request("POST", "/api/gate/approve", json={"approval_id": approval_id})

    def gate_reject(self, approval_id: str, reason: str = "") -> dict:
        """POST /api/gate/reject — Reject a pending action."""
        return self._request("POST", "/api/gate/reject", json={
            "approval_id": approval_id,
            "reason": reason,
        })

    def gate_pending(self) -> list:
        """GET /api/gate/pending — List pending approval requests."""
        data = self._request("GET", "/api/gate/pending")
        return data if isinstance(data, list) else data.get("pending", [])

    def gate_audit_log(self) -> list:
        """GET /api/gate/audit-log — Get the gate audit log."""
        data = self._request("GET", "/api/gate/audit-log")
        return data if isinstance(data, list) else data.get("audit_log", [])

    def gate_config(self) -> dict:
        """GET /api/gate/config — Get gate configuration."""
        return self._request("GET", "/api/gate/config")

    # ─── Audit & Policy ──────────────────────────────────────────

    def ledger_full(self) -> list[LedgerEntry]:
        """GET /api/audit-trail — Get full in-memory session ledger."""
        data = self._request("GET", "/api/audit-trail")
        entries = data if isinstance(data, list) else data.get("entries", [])
        return [LedgerEntry.from_dict(e) for e in entries]

    def public_policy(self) -> dict:
        """GET /api/policy/public — Get the public policy configuration."""
        return self._request("GET", "/api/policy/public")
