"""
RIO Runtime — Governed Execution Protocol v2: Receipts Package

Provides v2 receipt generation, signing, and verification.
"""

from .receipt_generator import (
    ReceiptV2,
    compute_action_hash,
    compute_intent_hash,
    compute_receipt_hash,
    compute_verification_hash,
    generate_denial_receipt,
    generate_receipt_v2,
)
from .receipt_signer import sign_receipt
from .receipt_verifier import verify_receipt_full

__all__ = [
    "ReceiptV2",
    "compute_action_hash",
    "compute_intent_hash",
    "compute_receipt_hash",
    "compute_verification_hash",
    "generate_denial_receipt",
    "generate_receipt_v2",
    "sign_receipt",
    "verify_receipt_full",
]
