#!/usr/bin/env python3
"""
RIO Protocol SDK — Python Verify Example
==========================================
Demonstrates how to verify a RIO receipt and ledger using the SDK.

Run from the sdk/ directory:
    python examples/python_verify_example.py
"""

import json
import sys
from pathlib import Path

# Add the python SDK to the path (not needed after pip install)
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from rio_sdk import verify_receipt, verify_ledger

# ── Paths to example files ────────────────────────────────────────────────────
EXAMPLES = Path(__file__).parent.parent.parent / "examples"
RECEIPT  = EXAMPLES / "example_receipt_v2.json"
LEDGER   = EXAMPLES / "example_ledger.json"


def main():
    print("=" * 60)
    print(" RIO Protocol SDK — Receipt + Ledger Verification Example")
    print("=" * 60)

    # Read the demo service token from the ledger file
    # (In production use: pass your real RIO_SERVICE_TOKEN here or set the env var)
    ledger_data   = json.loads(LEDGER.read_text())
    demo_token    = ledger_data.get("demo_service_token", "")

    # ── Example 1: verify_receipt ─────────────────────────────────────────────
    print("\n[1] Verifying receipt + ledger together...")
    result = verify_receipt(RECEIPT, LEDGER, service_token=demo_token)

    print(f"    Overall: {result['overall']}")
    print(f"    Passed:  {result['checks_passed']} / {len(result['checks'])}")
    for check in result["checks"]:
        icon = "✓" if check["passed"] else "✗"
        print(f"      {icon} {check['check_name']}: {check['detail']}")

    # ── Example 2: verify_ledger (without a receipt) ──────────────────────────
    print("\n[2] Verifying ledger only (no receipt)...")
    ledger_result = verify_ledger(LEDGER, service_token=demo_token)

    print(f"    Overall: {ledger_result['overall']}")
    print(f"    Passed:  {ledger_result['checks_passed']} / {len(ledger_result['checks'])}")

    # ── Example 3: using pre-loaded dicts ─────────────────────────────────────
    print("\n[3] Using pre-loaded dicts instead of file paths...")
    receipt_data = json.loads(RECEIPT.read_text())

    dict_result = verify_receipt(receipt_data, ledger_data, service_token=demo_token)
    print(f"    Overall: {dict_result['overall']}")

    # ── Example 4: what FAIL looks like ──────────────────────────────────────
    print("\n[4] Simulating a tampered receipt (what FAIL looks like)...")
    tampered = json.loads(RECEIPT.read_text())
    tampered["receipt_hash"] = "0" * 64   # corrupt the hash

    fail_result = verify_receipt(tampered, ledger_data)
    print(f"    Overall: {fail_result['overall']}")
    for check in fail_result["checks"]:
        if not check["passed"]:
            print(f"      ✗ {check['check_name']}: {check['detail']}")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    overall = "PASS" if result["overall"] == "PASS" else "FAIL"
    print(f" Demo result: {overall}")
    print("=" * 60)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
