"""
RIO Protocol SDK — Python
=========================
Simple functions for verifying RIO receipts and ledgers, running conformance
tests, and checking compliance level.

Quick start:
    from rio_sdk import verify_receipt, verify_ledger, run_conformance_tests, get_compliance_level

    result = verify_receipt("receipt.json", "ledger.json", service_token="your-token")
    print(result["overall"])  # "PASS" or "FAIL"
"""

from .verifier import verify_receipt, verify_ledger
from .conformance import run_conformance_tests
from .compliance import get_compliance_level

__version__ = "1.0.0"
__all__ = [
    "verify_receipt",
    "verify_ledger",
    "run_conformance_tests",
    "get_compliance_level",
]
