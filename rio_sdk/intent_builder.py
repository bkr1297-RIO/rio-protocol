"""
RIO SDK — Fluent IntentBuilder

    intent = (
        IntentBuilder("Summarise the Q3 financial report")
        .with_context(user_id="u-42", environment="staging")
        .with_metadata(priority="high")
        .build()
    )
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional

from .models import Intent
from .signing import Ed25519Key, Ed25519Signer
from .exceptions import RIOConfigError


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


class IntentBuilder:
    """Fluent builder for constructing signed RIO intents."""

    def __init__(self, intent_text: str, key: Optional[Ed25519Key] = None):
        self._intent_text = intent_text
        self._key = key
        self._source = "sdk"
        self._model = "claude"
        self._context: dict = {}
        self._metadata: dict = {}
        self._timestamp: Optional[str] = None
        self._disengaged = False

    def with_key(self, key: Ed25519Key) -> IntentBuilder:
        """Set the signing key."""
        self._key = key
        return self

    def with_source(self, source: str) -> IntentBuilder:
        """Set the intent source identifier."""
        self._source = source
        return self

    def with_model(self, model: str) -> IntentBuilder:
        """Set the target model."""
        self._model = model
        return self

    def with_context(self, **kwargs) -> IntentBuilder:
        """Add context fields (user_id, environment, session_id, etc.)."""
        self._context.update(kwargs)
        return self

    def with_metadata(self, **kwargs) -> IntentBuilder:
        """Add metadata fields (priority, tags, etc.)."""
        self._metadata.update(kwargs)
        return self

    def with_timestamp(self, ts: str) -> IntentBuilder:
        """Override the timestamp (ISO 8601 UTC)."""
        self._timestamp = ts
        return self

    def disengage(self) -> IntentBuilder:
        """Mark intent as disengaged (bypass governance — testing only)."""
        self._disengaged = True
        return self

    def build(self) -> Intent:
        """Build and sign the intent. Requires a key unless disengaged."""
        if not self._key and not self._disengaged:
            raise RIOConfigError("IntentBuilder requires an Ed25519Key. Call .with_key() or .disengage().")

        ts = self._timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        canonical = f"{self._intent_text}|{self._source}|{ts}"
        intent_id = _sha256(canonical.encode("utf-8"))

        params_hash = _sha256(_canonical_json({
            "intent": self._intent_text,
            "source": self._source,
            "model": self._model,
            "timestamp": ts,
            "intent_id": intent_id,
        }))

        if self._key:
            signer = Ed25519Signer(self._key)
            signature = signer.sign(canonical)
            nonce = os.urandom(16).hex()
            exec_token = signer.sign(f"{intent_id}|{nonce}")
            pub_b64 = self._key.public_key_b64
            pub_hex = self._key.public_key_hex
        else:
            # Disengaged mode — no real signatures
            signature = ""
            nonce = os.urandom(16).hex()
            exec_token = ""
            pub_b64 = ""
            pub_hex = ""

        return Intent(
            intent=self._intent_text,
            source=self._source,
            timestamp=ts,
            intent_id=intent_id,
            signature=signature,
            execution_token=exec_token,
            model=self._model,
            nonce=nonce,
            public_key_b64=pub_b64,
            public_key_hex=pub_hex,
            parameters_hash=params_hash,
            context=self._context.copy(),
            metadata=self._metadata.copy(),
        )
