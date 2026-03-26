"""
RIO Runtime — Governed Execution Protocol v2: Receipt Signer

Signs v2 receipts using RSA-2048 PSS signatures. The signed fields are:

    intent_hash + action_hash + decision + timestamp_execution +
    receipt_hash + previous_hash

The signature covers the critical decision chain, ensuring that any
modification to the intent, action, decision, timing, or chain linkage
is detectable.

Spec reference: /spec/receipt_protocol.md
"""

from __future__ import annotations

import base64
import logging
import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .receipt_generator import ReceiptV2

logger = logging.getLogger("rio.receipts.signer")

# ---------------------------------------------------------------------------
# Key management (reuses the same key pair as receipt.py)
# ---------------------------------------------------------------------------

_KEYS_DIR = os.path.join(os.path.dirname(__file__), "..", "keys")
_PRIVATE_KEY_PATH = os.path.join(_KEYS_DIR, "private_key.pem")
_PUBLIC_KEY_PATH = os.path.join(_KEYS_DIR, "public_key.pem")

_private_key = None


def _load_private_key():
    """Load the RSA private key from disk (lazy, cached)."""
    global _private_key
    if _private_key is not None:
        return _private_key

    if not os.path.exists(_PRIVATE_KEY_PATH):
        logger.warning("Private key not found — generating ephemeral key pair")
        _generate_key_pair()

    with open(_PRIVATE_KEY_PATH, "rb") as fh:
        _private_key = serialization.load_pem_private_key(fh.read(), password=None)

    return _private_key


def _generate_key_pair():
    """Generate a new RSA-2048 key pair and write to disk."""
    global _private_key

    os.makedirs(_KEYS_DIR, exist_ok=True)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with open(_PRIVATE_KEY_PATH, "wb") as fh:
        fh.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    os.chmod(_PRIVATE_KEY_PATH, 0o600)

    with open(_PUBLIC_KEY_PATH, "wb") as fh:
        fh.write(
            key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    _private_key = key
    logger.info("Generated new RSA-2048 key pair at %s", _KEYS_DIR)


# ---------------------------------------------------------------------------
# Signing
# ---------------------------------------------------------------------------

def _build_signing_payload(receipt: ReceiptV2) -> str:
    """
    Build the signing payload from the v2 receipt's critical fields.

    Signed fields:
        intent_hash + action_hash + decision + timestamp_execution +
        receipt_hash + previous_hash
    """
    return (
        f"{receipt.intent_hash}"
        f"{receipt.action_hash}"
        f"{receipt.decision}"
        f"{receipt.timestamp_execution}"
        f"{receipt.receipt_hash}"
        f"{receipt.previous_hash}"
    )


def sign_receipt(receipt: ReceiptV2) -> ReceiptV2:
    """
    Sign a v2 receipt with the RSA-2048 private key.

    The signature covers the critical decision chain fields. The receipt
    is modified in place and returned.

    Args:
        receipt: The ReceiptV2 to sign (must have receipt_hash computed).

    Returns:
        The same ReceiptV2 with the signature field populated.
    """
    private_key = _load_private_key()
    payload = _build_signing_payload(receipt)

    signature_bytes = private_key.sign(
        payload.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    receipt.signature = base64.b64encode(signature_bytes).decode("utf-8")

    logger.info(
        "v2 Receipt %s signed — hash=%s",
        receipt.receipt_id,
        receipt.receipt_hash[:16] + "...",
    )

    return receipt


def get_signing_payload(receipt: ReceiptV2) -> str:
    """
    Return the signing payload for external verification.

    This is the exact string that was signed, allowing independent
    signature verification.
    """
    return _build_signing_payload(receipt)
