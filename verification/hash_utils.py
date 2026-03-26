"""
Protocol hash functions for the RIO Independent Verifier.

All hash computations follow the exact formulas defined in the
RIO Protocol Specification and Independent Verifier Spec:

- canonical_json: json.dumps(obj, sort_keys=True, separators=(',', ':'))
- request_hash: SHA256(canonical_json(request_canonical_payload))
- receipt_hash: SHA256(canonical_json({exactly the 19 signed fields}))
- model_output_hash: SHA256(model_output_string.encode('utf-8'))
- public_key_fingerprint: SHA256(raw_32_byte_ed25519_public_key_bytes)
- ledger_chain_hash: SHA256((prev_ledger_hash + receipt_hash).encode('utf-8'))
- genesis_hash: SHA256(b'GENESIS')
"""

import hashlib
import json
from typing import Any

from verification.models import SIGNED_FIELDS_19


def canonical_json(obj: Any) -> bytes:
    """
    Produce the canonical JSON byte encoding of an object.

    Rules:
    - Keys sorted recursively (sort_keys=True)
    - No whitespace (separators=(',', ':'))
    - No trailing newlines
    - Encoded as UTF-8 bytes
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Compute SHA-256 and return lowercase hex digest."""
    return hashlib.sha256(data).hexdigest()


def compute_request_hash(request_canonical_payload: dict) -> str:
    """
    SHA256(canonical_json(request_canonical_payload))
    """
    return sha256_hex(canonical_json(request_canonical_payload))


def compute_receipt_hash(receipt: dict) -> str:
    """
    SHA256(canonical_json({exactly the 19 signed fields}))

    CRITICAL: receipt_hash is NOT part of its own signed payload.
    Only the 19 signed fields are included.
    """
    signed_payload = {k: receipt[k] for k in SIGNED_FIELDS_19}
    return sha256_hex(canonical_json(signed_payload))


def compute_public_key_fingerprint(raw_public_key_bytes: bytes) -> str:
    """
    SHA256(raw_32_byte_ed25519_public_key_bytes)

    The raw key bytes are the 32-byte Ed25519 public key,
    extracted via: key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    """
    return sha256_hex(raw_public_key_bytes)


def compute_ledger_chain_hash(prev_ledger_hash: str, receipt_hash: str) -> str:
    """
    SHA256((prev_ledger_hash + receipt_hash).encode('utf-8'))

    CRITICAL: String concatenation first, then encode — NOT byte concatenation.
    """
    concatenated = prev_ledger_hash + receipt_hash
    return sha256_hex(concatenated.encode("utf-8"))


def compute_genesis_hash() -> str:
    """
    SHA256(b'GENESIS')

    Protocol constant: 901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a
    """
    return sha256_hex(b"GENESIS")
