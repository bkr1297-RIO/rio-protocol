"""
RIO SDK — Python SDK for the RIO Governance Protocol

    from rio_sdk import RIOClient, IntentBuilder, ReceiptVerifier

Quick start:

    client = RIOClient("http://localhost:5000")

    intent = (
        IntentBuilder("Summarise the Q3 financial report")
        .with_context(user_id="u-42", environment="staging")
        .build()
    )

    result = client.evaluate(intent)
    print(result.receipt.decision)  # 'allow'

    verifier = ReceiptVerifier(client.public_key_pem())
    verifier.assert_valid(result.receipt)
    print(verifier.verify(result.receipt).summary)  # '7/7 checks passed'
"""

__version__ = "0.1.0"

from .gateway_client import RIOClient
from .intent_builder import IntentBuilder
from .receipt_verifier import ReceiptVerifier, LedgerVerifier
from .ledger_client import LedgerClient
from .signing import Ed25519Key, Ed25519Signer, ECDSAKey, ECDSASigner
from .models import (
    Intent,
    Receipt,
    EvaluateResult,
    GovernorSubmission,
    LedgerEntry,
    GateExecuteResult,
    VerificationResult,
    VerificationCheck,
)
from .exceptions import (
    RIOError,
    RIOConnectionError,
    RIOHTTPError,
    RIOIntentBlockedError,
    RIOVerificationError,
    RIOLedgerError,
    RIOApprovalError,
    RIOKeyError,
    RIOConfigError,
)

__all__ = [
    # Core classes
    "RIOClient",
    "IntentBuilder",
    "ReceiptVerifier",
    "LedgerVerifier",
    "LedgerClient",
    # Signing
    "Ed25519Key",
    "Ed25519Signer",
    "ECDSAKey",
    "ECDSASigner",
    # Models
    "Intent",
    "Receipt",
    "EvaluateResult",
    "GovernorSubmission",
    "LedgerEntry",
    "GateExecuteResult",
    "VerificationResult",
    "VerificationCheck",
    # Exceptions
    "RIOError",
    "RIOConnectionError",
    "RIOHTTPError",
    "RIOIntentBlockedError",
    "RIOVerificationError",
    "RIOLedgerError",
    "RIOApprovalError",
    "RIOKeyError",
    "RIOConfigError",
]
