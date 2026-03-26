#!/usr/bin/env python3
"""
RIO Protocol -- Compliance Level Validator (WS7)
================================================
Determines the conformance level (Level 1, 2, or 3) of a given set of
artifacts by running the independent verifier against them.

Levels:
    Level 1 -- Receipt Format Compliance
        Valid receipt format + valid receipt hash + valid receipt signature
    Level 2 -- Governance Attested
        Level 1 + valid ledger hash chain + independent verification PASS
    Level 3 -- Full Protocol Compliance
        Level 2 + full pipeline + protocol invariants enforced

Usage:
    python tools/check_compliance.py --receipt <path> --key <path>
    python tools/check_compliance.py --receipt <path> --key <path> --ledger <path>
    python tools/check_compliance.py --auto
    python tools/check_compliance.py --auto --json

Exit codes:
    0 -- Assessment completed (check output for level)
    1 -- Assessment failed (invalid inputs or setup error)
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Resolve paths
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
VECTORS_DIR = REPO_ROOT / "tests" / "vectors"

sys.path.insert(0, str(REPO_ROOT))

try:
    from verification.receipt_verifier import verify_receipt
    from verification.ledger_verifier import verify_ledger
    from verification.models import GENESIS_HASH, VALID_DECISIONS, SIGNED_FIELDS_19
except ImportError as e:
    print(f"SETUP ERROR: Cannot import verification package: {e}")
    sys.exit(1)


def assess_level_1(receipt_data, public_key_pem):
    """Level 1 -- Receipt Format Compliance."""
    result = verify_receipt(receipt_data, public_key_pem)
    checks = {}
    for c in result.checks:
        checks[c.check_name] = {"passed": c.passed, "details": c.details}

    required_checks = ["required_fields", "receipt_hash", "signature"]
    level1_passed = all(
        checks.get(name, {}).get("passed", False) for name in required_checks
    )

    return {
        "level": 1,
        "name": "Receipt Format Compliance",
        "passed": level1_passed,
        "checks": checks,
        "receipt_id": result.receipt_id,
        "all_7_passed": result.all_passed,
    }


def assess_level_2(receipt_data, public_key_pem, ledger_data):
    """Level 2 -- Governance Attested."""
    l1 = assess_level_1(receipt_data, public_key_pem)
    if not l1["passed"]:
        return {
            "level": 2,
            "name": "Governance Attested",
            "passed": False,
            "reason": "Level 1 requirements not met",
            "level_1": l1,
            "ledger_checks": {},
        }

    lr = verify_ledger(ledger_data)
    ledger_checks = {
        "chain_intact": lr.chain_intact,
        "entries_verified": lr.entries_verified,
        "entries_total": lr.entries_total,
        "failures": [f.__dict__ for f in lr.failures] if lr.failures else [],
    }

    level2_passed = l1["passed"] and lr.chain_intact and l1["all_7_passed"]

    return {
        "level": 2,
        "name": "Governance Attested",
        "passed": level2_passed,
        "level_1": l1,
        "ledger_checks": ledger_checks,
    }


def assess_level_3(receipt_data, public_key_pem, ledger_data, invariants=None):
    """Level 3 -- Full Protocol Compliance."""
    l2 = assess_level_2(receipt_data, public_key_pem, ledger_data)

    receipt = receipt_data.get("receipt", receipt_data)
    invariant_results = receipt.get("invariant_results", {})

    invariant_checks = {}
    protocol_invariants = [
        "INV-01", "INV-02", "INV-03", "INV-04",
        "INV-05", "INV-06", "INV-07", "INV-08",
    ]

    for inv_id in protocol_invariants:
        if inv_id in invariant_results:
            val = invariant_results[inv_id]
            invariant_checks[inv_id] = {
                "present": True,
                "passed": val.get("passed", False) if isinstance(val, dict) else bool(val),
            }
        elif invariants and inv_id in invariants:
            invariant_checks[inv_id] = {
                "present": True,
                "passed": invariants[inv_id],
            }
        else:
            invariant_checks[inv_id] = {"present": False, "passed": False}

    all_present = all(v["present"] for v in invariant_checks.values())
    all_passed = all(v["passed"] for v in invariant_checks.values())

    level3_passed = l2["passed"] and all_present and all_passed

    return {
        "level": 3,
        "name": "Full Protocol Compliance",
        "passed": level3_passed,
        "level_2": l2,
        "invariant_checks": invariant_checks,
        "all_invariants_present": all_present,
        "all_invariants_passed": all_passed,
        "note": "Level 3 requires pipeline invariant attestation in receipt." if not all_present else "",
    }


def determine_compliance_level(receipt_data, public_key_pem, ledger_data=None):
    """Determine the highest compliance level achieved."""
    timestamp = datetime.now(timezone.utc).isoformat()

    l1 = assess_level_1(receipt_data, public_key_pem)
    if not l1["passed"]:
        return {
            "timestamp": timestamp,
            "compliance_level": 0,
            "compliance_name": "Non-Compliant",
            "summary": "Receipt does not meet Level 1 requirements",
            "details": l1,
        }

    if ledger_data is None:
        return {
            "timestamp": timestamp,
            "compliance_level": 1,
            "compliance_name": "Receipt Format Compliance",
            "summary": "Level 1 achieved. Provide ledger data to assess Level 2.",
            "details": l1,
        }

    l2 = assess_level_2(receipt_data, public_key_pem, ledger_data)
    if not l2["passed"]:
        return {
            "timestamp": timestamp,
            "compliance_level": 1,
            "compliance_name": "Receipt Format Compliance",
            "summary": "Level 1 achieved but Level 2 requirements not met",
            "details": l2,
        }

    l3 = assess_level_3(receipt_data, public_key_pem, ledger_data)
    if l3["passed"]:
        return {
            "timestamp": timestamp,
            "compliance_level": 3,
            "compliance_name": "Full Protocol Compliance",
            "summary": "Level 3 achieved -- full pipeline with protocol invariants enforced",
            "details": l3,
        }

    return {
        "timestamp": timestamp,
        "compliance_level": 2,
        "compliance_name": "Governance Attested",
        "summary": "Level 2 achieved -- receipt and ledger verified independently",
        "details": l2,
    }


def print_human(result):
    level = result["compliance_level"]

    print()
    print("=" * 60)
    print(" RIO Protocol -- Compliance Assessment")
    print(f" Timestamp: {result['timestamp']}")
    print("=" * 60)
    print()

    details = result.get("details", {})

    # Level 1 checks
    checks = details.get("checks", {})
    if checks:
        print("Receipt Verification Checks:")
        for check_name, check_info in checks.items():
            status = "PASS" if check_info.get("passed") else "FAIL"
            print(f"  [{status}] {check_name.replace('_', ' ').title()}")
        print()

    # Level 1 from level_2 details
    l1_in_l2 = details.get("level_1", {})
    if l1_in_l2 and not checks:
        l1_checks = l1_in_l2.get("checks", {})
        if l1_checks:
            print("Receipt Verification Checks:")
            for check_name, check_info in l1_checks.items():
                status = "PASS" if check_info.get("passed") else "FAIL"
                print(f"  [{status}] {check_name.replace('_', ' ').title()}")
            print()

    # Level 2 ledger checks
    ledger = details.get("ledger_checks", {})
    if ledger:
        chain_status = "PASS" if ledger.get("chain_intact") else "FAIL"
        ev = ledger.get("entries_verified", 0)
        et = ledger.get("entries_total", 0)
        print("Ledger Verification:")
        print(f"  [{chain_status}] Chain Integrity ({ev}/{et} entries)")
        print()

    # Level 3 invariant checks
    invariants = details.get("invariant_checks", {})
    if invariants:
        print("Protocol Invariants:")
        for inv_id, inv_info in invariants.items():
            if inv_info.get("present"):
                status = "PASS" if inv_info.get("passed") else "FAIL"
            else:
                status = "N/A "
            print(f"  [{status}] {inv_id}")
        print()

    level_labels = {
        0: "Non-Compliant",
        1: "Level 1 -- Receipt Format Compliance",
        2: "Level 2 -- Governance Attested",
        3: "Level 3 -- Full Protocol Compliance",
    }
    print(f"Compliance: {level_labels.get(level, 'Unknown')}")
    print(f"Summary:    {result['summary']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="RIO Protocol Compliance Level Validator (WS7)",
    )
    parser.add_argument("--receipt", type=str, help="Path to receipt JSON file")
    parser.add_argument("--key", type=str, help="Path to public key PEM file")
    parser.add_argument("--ledger", type=str, help="Path to ledger chain JSON file")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-discover artifacts from tests/vectors/")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    args = parser.parse_args()

    if args.auto:
        receipt_path = VECTORS_DIR / "receipt_valid_approved.json"
        key_path = VECTORS_DIR / "public_key.pem"
        ledger_path = VECTORS_DIR / "ledger_chain_valid.json"
        if not receipt_path.exists() or not key_path.exists():
            print("ERROR: Cannot auto-discover -- test vectors not found.")
            sys.exit(1)
    elif args.receipt and args.key:
        receipt_path = Path(args.receipt)
        key_path = Path(args.key)
        ledger_path = Path(args.ledger) if args.ledger else None
    else:
        parser.error("Provide --receipt and --key, or use --auto")

    # Load artifacts
    try:
        with open(receipt_path) as f:
            receipt_data = json.load(f)
        public_key_pem = key_path.read_text()
        ledger_data = None
        if ledger_path and ledger_path.exists():
            with open(ledger_path) as f:
                ledger_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to load artifacts: {e}")
        sys.exit(1)

    result = determine_compliance_level(receipt_data, public_key_pem, ledger_data)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_human(result)

    sys.exit(0)


if __name__ == "__main__":
    main()
