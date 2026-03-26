"""
RIO Protocol Independent Verifier v1.0

Zero-dependency verification of RIO v2 receipts and ledger chains.
This package operates independently of the reference implementation.
Only external dependency: cryptography>=41.0.0
"""

__version__ = "1.0.0"

from verification.receipt_verifier import verify_receipt, verify_receipt_from_file
from verification.ledger_verifier import verify_ledger, verify_ledger_from_file

__all__ = [
    "verify_receipt",
    "verify_receipt_from_file",
    "verify_ledger",
    "verify_ledger_from_file",
]
