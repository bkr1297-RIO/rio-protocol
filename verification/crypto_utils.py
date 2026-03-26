"""
Cryptographic utilities for the RIO Independent Verifier.

Uses ONLY the 'cryptography' library for Ed25519 operations.
Zero imports from the reference implementation.
"""

import base64

from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
    load_pem_public_key,
)
from cryptography.exceptions import InvalidSignature


def load_public_key(pem_text: str):
    """
    Load an Ed25519 public key from PEM text.

    Expected format:
        -----BEGIN PUBLIC KEY-----
        MCowBQYDK2VwAyEA...
        -----END PUBLIC KEY-----

    Returns the public key object.
    Raises ValueError if the PEM is invalid or not an Ed25519 key.
    """
    try:
        key = load_pem_public_key(pem_text.encode("utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to load PEM public key: {e}") from e
    return key


def get_raw_public_key_bytes(public_key) -> bytes:
    """
    Extract the raw 32-byte Ed25519 public key bytes.

    Uses: key.public_bytes(Encoding.Raw, PublicFormat.Raw)
    """
    return public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)


def verify_signature(public_key, message_bytes: bytes, signature_b64: str) -> bool:
    """
    Verify an Ed25519 signature.

    Args:
        public_key: Ed25519 public key object
        message_bytes: The exact bytes that were signed
        signature_b64: Base64-encoded 64-byte Ed25519 signature

    Returns:
        True if signature is valid, False otherwise.
    """
    try:
        sig_bytes = base64.b64decode(signature_b64)
    except Exception:
        return False

    if len(sig_bytes) != 64:
        return False

    try:
        public_key.verify(sig_bytes, message_bytes)
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False
