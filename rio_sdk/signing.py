"""
RIO SDK — Cryptographic Signing

Ed25519Key, Ed25519Signer — generate / load / sign / verify
ECDSAKey, ECDSASigner     — generate / load / sign / verify (secp256k1)

All signatures are base64-encoded by default.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Optional, Union

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.asymmetric.ec import (
    ECDSA,
    SECP256K1,
    EllipticCurvePrivateKey,
    EllipticCurvePublicKey,
    generate_private_key,
)
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
    load_pem_private_key,
    load_pem_public_key,
)

from .exceptions import RIOKeyError


# ─── Ed25519 ──────────────────────────────────────────────────────────

class Ed25519Key:
    """Ed25519 key pair for intent signing and verification."""

    def __init__(self, private_key: Ed25519PrivateKey):
        self._sk = private_key
        self._pk = private_key.public_key()
        self._raw_pub = self._pk.public_bytes(Encoding.Raw, PublicFormat.Raw)

    @classmethod
    def generate(cls) -> Ed25519Key:
        """Generate a fresh Ed25519 key pair."""
        return cls(Ed25519PrivateKey.generate())

    @classmethod
    def from_pem(cls, pem_data: Union[str, bytes]) -> Ed25519Key:
        """Load from PEM-encoded private key."""
        if isinstance(pem_data, str):
            pem_data = pem_data.encode()
        try:
            sk = load_pem_private_key(pem_data, password=None)
            if not isinstance(sk, Ed25519PrivateKey):
                raise RIOKeyError("PEM does not contain an Ed25519 private key")
            return cls(sk)
        except Exception as e:
            raise RIOKeyError(f"Failed to load Ed25519 key: {e}") from e

    @classmethod
    def from_file(cls, path: str) -> Ed25519Key:
        """Load from a PEM file."""
        with open(path, "rb") as f:
            return cls.from_pem(f.read())

    def save(self, private_path: str, public_path: Optional[str] = None):
        """Save key pair to PEM files."""
        with open(private_path, "wb") as f:
            f.write(self._sk.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        if public_path:
            with open(public_path, "wb") as f:
                f.write(self._pk.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))

    @property
    def public_key_b64(self) -> str:
        return base64.b64encode(self._raw_pub).decode()

    @property
    def public_key_hex(self) -> str:
        return self._raw_pub.hex()

    @property
    def fingerprint(self) -> str:
        """SHA-256 fingerprint of the raw 32-byte public key."""
        return hashlib.sha256(self._raw_pub).hexdigest()

    @property
    def approver_id(self) -> str:
        """First 16 hex chars of the fingerprint — used as approver identifier."""
        return self.fingerprint[:16]


class Ed25519Signer:
    """Sign and verify messages with Ed25519."""

    def __init__(self, key: Ed25519Key):
        self._key = key

    def sign(self, message: Union[str, bytes]) -> str:
        """Sign a message and return base64-encoded signature."""
        if isinstance(message, str):
            message = message.encode("utf-8")
        return base64.b64encode(self._key._sk.sign(message)).decode()

    def verify(self, message: Union[str, bytes], signature_b64: str) -> bool:
        """Verify a base64-encoded signature. Returns True/False."""
        if isinstance(message, str):
            message = message.encode("utf-8")
        try:
            sig = base64.b64decode(signature_b64)
            self._key._pk.verify(sig, message)
            return True
        except Exception:
            return False

    def sign_json(self, obj: dict) -> str:
        """Sign canonical JSON representation of a dict."""
        canonical = json.dumps(obj, separators=(",", ":"), sort_keys=True)
        return self.sign(canonical)


# ─── ECDSA (secp256k1) ───────────────────────────────────────────────

class ECDSAKey:
    """ECDSA secp256k1 key pair."""

    def __init__(self, private_key: EllipticCurvePrivateKey):
        self._sk = private_key
        self._pk = private_key.public_key()

    @classmethod
    def generate(cls) -> ECDSAKey:
        """Generate a fresh ECDSA secp256k1 key pair."""
        return cls(generate_private_key(SECP256K1()))

    @classmethod
    def from_pem(cls, pem_data: Union[str, bytes]) -> ECDSAKey:
        if isinstance(pem_data, str):
            pem_data = pem_data.encode()
        try:
            sk = load_pem_private_key(pem_data, password=None)
            if not isinstance(sk, EllipticCurvePrivateKey):
                raise RIOKeyError("PEM does not contain an ECDSA private key")
            return cls(sk)
        except Exception as e:
            raise RIOKeyError(f"Failed to load ECDSA key: {e}") from e

    @classmethod
    def from_file(cls, path: str) -> ECDSAKey:
        with open(path, "rb") as f:
            return cls.from_pem(f.read())

    def save(self, private_path: str, public_path: Optional[str] = None):
        with open(private_path, "wb") as f:
            f.write(self._sk.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
        if public_path:
            with open(public_path, "wb") as f:
                f.write(self._pk.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo))

    @property
    def public_key_pem(self) -> str:
        return self._pk.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo).decode()


class ECDSASigner:
    """Sign and verify messages with ECDSA secp256k1."""

    def __init__(self, key: ECDSAKey):
        self._key = key

    def sign(self, message: Union[str, bytes]) -> str:
        if isinstance(message, str):
            message = message.encode("utf-8")
        sig = self._key._sk.sign(message, ECDSA(SHA256()))
        return base64.b64encode(sig).decode()

    def verify(self, message: Union[str, bytes], signature_b64: str) -> bool:
        if isinstance(message, str):
            message = message.encode("utf-8")
        try:
            sig = base64.b64decode(signature_b64)
            self._key._pk.verify(sig, message, ECDSA(SHA256()))
            return True
        except Exception:
            return False

    def sign_json(self, obj: dict) -> str:
        canonical = json.dumps(obj, separators=(",", ":"), sort_keys=True)
        return self.sign(canonical)
