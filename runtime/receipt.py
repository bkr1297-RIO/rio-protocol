"""
RIO Runtime — Stage 8: Receipt / Attestation

Generates a cryptographic receipt after every execution decision (allow, deny,
or block). The receipt includes hashes of the intent, authorization, and
execution result, forming a hash chain with the previous receipt.

Every action — whether executed, denied, or blocked — must produce a receipt.
This enforces INV-02 (Receipt Completeness).

Receipts are signed with an RSA-2048 private key stored at
``runtime/keys/private_key.pem``.  The corresponding public key
(``runtime/keys/public_key.pem``) is used by the verification CLI to
validate receipt authenticity.

Spec reference: /spec/receipt_protocol.md, /spec/08_attestation.md
Protocol stage: Step 7 of the 8-step Governed Execution Protocol
Related invariants: INV-02 (Receipt Completeness), INV-04 (Hash Chain Integrity)
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import os
import time
import uuid
from typing import Any

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .models import Authorization, Decision, ExecutionStatus, Intent, Receipt

logger = logging.getLogger("rio.receipt")

# ---------------------------------------------------------------------------
# Key management
# ---------------------------------------------------------------------------

_KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
_PRIVATE_KEY_PATH = os.path.join(_KEYS_DIR, "private_key.pem")
_PUBLIC_KEY_PATH = os.path.join(_KEYS_DIR, "public_key.pem")

_private_key = None
_public_key = None


def _load_private_key():
    """Load the RSA private key from disk (lazy, cached)."""
    global _private_key
    if _private_key is not None:
        return _private_key

    if not os.path.exists(_PRIVATE_KEY_PATH):
        logger.warning("Private key not found at %s — generating ephemeral key pair", _PRIVATE_KEY_PATH)
        _generate_key_pair()

    with open(_PRIVATE_KEY_PATH, "rb") as fh:
        _private_key = serialization.load_pem_private_key(fh.read(), password=None)

    return _private_key


def _load_public_key():
    """Load the RSA public key from disk (lazy, cached)."""
    global _public_key
    if _public_key is not None:
        return _public_key

    if not os.path.exists(_PUBLIC_KEY_PATH):
        logger.warning("Public key not found at %s — generating ephemeral key pair", _PUBLIC_KEY_PATH)
        _generate_key_pair()

    with open(_PUBLIC_KEY_PATH, "rb") as fh:
        _public_key = serialization.load_pem_public_key(fh.read())

    return _public_key


def _generate_key_pair():
    """Generate a new RSA-2048 key pair and write to disk."""
    global _private_key, _public_key

    os.makedirs(_KEYS_DIR, exist_ok=True)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Write private key
    with open(_PRIVATE_KEY_PATH, "wb") as fh:
        fh.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    os.chmod(_PRIVATE_KEY_PATH, 0o600)

    # Write public key
    with open(_PUBLIC_KEY_PATH, "wb") as fh:
        fh.write(
            key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

    _private_key = key
    _public_key = key.public_key()

    logger.info("Generated new RSA-2048 key pair at %s", _KEYS_DIR)


def get_public_key():
    """Return the loaded public key (for external verification)."""
    return _load_public_key()


# ---------------------------------------------------------------------------
# Receipt generation
# ---------------------------------------------------------------------------

def generate_receipt(
    intent: Intent,
    authorization: Authorization,
    execution_status: ExecutionStatus,
    result_data: dict[str, Any],
    previous_receipt_hash: str,
) -> Receipt:
    """
    Generate a signed receipt for the governed action.

    The receipt captures the full decision chain: what was requested (intent),
    what was decided (authorization), and what happened (execution result).
    It is hash-linked to the previous receipt to form a tamper-evident chain.

    Args:
        intent: The canonical Intent.
        authorization: The Authorization decision.
        execution_status: The outcome of the Execution Gate.
        result_data: The result of the executed action (or empty if blocked).
        previous_receipt_hash: Hash of the preceding receipt (empty for genesis).

    Returns:
        A signed Receipt ready for the Ledger stage.
    """
    now = int(time.time() * 1000)

    # Compute result hash
    result_hash = _compute_hash(json.dumps(result_data, sort_keys=True))

    # Build receipt
    receipt = Receipt(
        receipt_id=str(uuid.uuid4()),
        request_id=intent.request_id,
        intent_id=intent.intent_id,
        authorization_id=authorization.authorization_id,
        decision=authorization.decision,
        action_type=intent.action_type,
        execution_status=execution_status,
        execution_timestamp=now,
        result_hash=result_hash,
        previous_receipt_hash=previous_receipt_hash,
    )

    # Compute receipt hash (canonical JSON + previous_receipt_hash)
    receipt.receipt_hash = _compute_receipt_hash(receipt)

    # Sign receipt with RSA private key
    receipt.signature = _sign_receipt(receipt)

    logger.info(
        "Receipt %s generated for intent %s — decision=%s, status=%s, hash=%s",
        receipt.receipt_id,
        receipt.intent_id,
        receipt.decision.value,
        receipt.execution_status.value,
        receipt.receipt_hash[:16] + "...",
    )

    return receipt


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def _compute_hash(data: str) -> str:
    """Compute SHA-256 hash of a string."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _compute_receipt_hash(receipt: Receipt) -> str:
    """
    Compute the receipt hash using canonical JSON serialization.

    Formula: SHA-256(canonical_json(receipt_fields) + previous_receipt_hash)
    """
    canonical = json.dumps(
        {
            "receipt_id": receipt.receipt_id,
            "request_id": receipt.request_id,
            "intent_id": receipt.intent_id,
            "authorization_id": receipt.authorization_id,
            "decision": receipt.decision.value,
            "action_type": receipt.action_type,
            "execution_status": receipt.execution_status.value,
            "execution_timestamp": receipt.execution_timestamp,
            "result_hash": receipt.result_hash,
        },
        sort_keys=True,
    )
    combined = canonical + receipt.previous_receipt_hash
    return _compute_hash(combined)


# ---------------------------------------------------------------------------
# RSA Signing & Verification
# ---------------------------------------------------------------------------

def _sign_receipt(receipt: Receipt) -> str:
    """
    Sign the receipt hash with the RSA-2048 private key.

    Returns a base64-encoded RSA-PSS signature of the receipt_hash.
    """
    private_key = _load_private_key()
    signature_bytes = private_key.sign(
        receipt.receipt_hash.encode("utf-8"),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature_bytes).decode("utf-8")


def verify_receipt_signature(receipt: Receipt) -> bool:
    """
    Verify the RSA-PSS signature on a receipt using the public key.

    Args:
        receipt: The receipt whose signature to verify.

    Returns:
        True if the signature is valid, False otherwise.
    """
    if not receipt.signature:
        return False

    public_key = _load_public_key()
    try:
        signature_bytes = base64.b64decode(receipt.signature)
        public_key.verify(
            signature_bytes,
            receipt.receipt_hash.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Rehash (for post-generation field updates)
# ---------------------------------------------------------------------------

def rehash_receipt(receipt: Receipt) -> Receipt:
    """
    Recompute the receipt hash and signature after field updates.

    Used when additional fields (risk_score, risk_level, policy_rule_id,
    policy_decision) are populated after initial receipt generation.

    Args:
        receipt: The Receipt with updated fields.

    Returns:
        The same Receipt with recomputed hash and signature.
    """
    receipt.receipt_hash = _compute_receipt_hash(receipt)
    receipt.signature = _sign_receipt(receipt)

    logger.info(
        "Receipt %s rehashed — new hash=%s",
        receipt.receipt_id,
        receipt.receipt_hash[:16] + "...",
    )

    return receipt
