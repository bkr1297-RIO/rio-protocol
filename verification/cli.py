"""
RIO Independent Verifier — Command Line Interface

Usage:
    python -m verification.cli verify-receipt receipt.json --public-key key.pem
    python -m verification.cli verify-ledger ledger.json
    python -m verification.cli verify-all receipt.json ledger.json --public-key key.pem

Exit codes:
    0 — All checks passed
    1 — One or more checks failed
    2 — Input/parse/usage error

Flags:
    --json   Output structured JSON instead of human-readable text
    --quiet  Print single summary line only
"""

import argparse
import json
import sys

from verification.receipt_verifier import verify_receipt_from_file, verify_receipt
from verification.ledger_verifier import verify_ledger_from_file, verify_ledger


def _print_receipt_result(result, json_output=False, quiet=False):
    """Print receipt verification result."""
    if json_output:
        print(json.dumps({"receipt": result.to_dict()}, indent=2))
        return

    if quiet:
        status = "PASS" if result.all_passed else "FAIL"
        print(f"Receipt {result.receipt_id}: {status}")
        return

    print(f"Receipt Verification: {result.receipt_id}")
    print("=" * 60)
    for check in result.checks:
        status = "PASS" if check.passed else "FAIL"
        print(f"  [{status}] Check {check.number}: {check.check_name}")
        if check.details:
            print(f"         {check.details}")
    print("-" * 60)
    overall = "ALL CHECKS PASSED" if result.all_passed else "VERIFICATION FAILED"
    print(f"  Result: {overall}")
    print()


def _print_ledger_result(result, json_output=False, quiet=False):
    """Print ledger verification result."""
    if json_output:
        print(json.dumps({"ledger": result.to_dict()}, indent=2))
        return

    if quiet:
        status = "INTACT" if result.chain_intact else "BROKEN"
        print(f"Ledger chain: {status} ({result.entries_verified}/{result.entries_total} verified)")
        return

    print("Ledger Chain Verification")
    print("=" * 60)
    print(f"  Entries total:    {result.entries_total}")
    print(f"  Entries verified: {result.entries_verified}")
    print(f"  Chain intact:     {result.chain_intact}")
    if result.failures:
        print(f"  Failures:")
        for f in result.failures:
            print(f"    [FAIL] Index {f.entry_index}: {f.check_name}")
            print(f"           {f.details}")
    print("-" * 60)
    overall = "CHAIN INTACT" if result.chain_intact else "CHAIN BROKEN"
    print(f"  Result: {overall}")
    print()


def cmd_verify_receipt(args):
    """Handle verify-receipt command."""
    try:
        if args.receipt_file == "-":
            receipt_data = json.load(sys.stdin)
            with open(args.public_key, "r") as f:
                pem = f.read()
            result = verify_receipt(receipt_data, pem)
        else:
            result = verify_receipt_from_file(args.receipt_file, args.public_key)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    _print_receipt_result(result, json_output=args.json, quiet=args.quiet)
    sys.exit(0 if result.all_passed else 1)


def cmd_verify_ledger(args):
    """Handle verify-ledger command."""
    try:
        if args.ledger_file == "-":
            ledger_data = json.load(sys.stdin)
            result = verify_ledger(ledger_data)
        else:
            result = verify_ledger_from_file(args.ledger_file)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    _print_ledger_result(result, json_output=args.json, quiet=args.quiet)
    sys.exit(0 if result.chain_intact else 1)


def cmd_verify_all(args):
    """Handle verify-all command."""
    try:
        receipt_result = verify_receipt_from_file(args.receipt_file, args.public_key)
        ledger_result = verify_ledger_from_file(args.ledger_file)
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        combined = {
            "receipt": receipt_result.to_dict(),
            "ledger": ledger_result.to_dict(),
        }
        print(json.dumps(combined, indent=2))
    else:
        _print_receipt_result(receipt_result, quiet=args.quiet)
        _print_ledger_result(ledger_result, quiet=args.quiet)

    all_ok = receipt_result.all_passed and ledger_result.chain_intact
    sys.exit(0 if all_ok else 1)


def main():
    parser = argparse.ArgumentParser(
        prog="rio-verifier",
        description="RIO Protocol Independent Verifier v1.0",
    )
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--quiet", action="store_true", help="Print single summary line only")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # verify-receipt
    p_receipt = subparsers.add_parser("verify-receipt", help="Verify a RIO receipt")
    p_receipt.add_argument("receipt_file", help="Path to receipt JSON (or - for stdin)")
    p_receipt.add_argument("--public-key", required=True, help="Path to Ed25519 PEM public key")
    p_receipt.set_defaults(func=cmd_verify_receipt)

    # verify-ledger
    p_ledger = subparsers.add_parser("verify-ledger", help="Verify a RIO ledger chain")
    p_ledger.add_argument("ledger_file", help="Path to ledger chain JSON (or - for stdin)")
    p_ledger.set_defaults(func=cmd_verify_ledger)

    # verify-all
    p_all = subparsers.add_parser("verify-all", help="Verify receipt AND ledger chain")
    p_all.add_argument("receipt_file", help="Path to receipt JSON")
    p_all.add_argument("ledger_file", help="Path to ledger chain JSON")
    p_all.add_argument("--public-key", required=True, help="Path to Ed25519 PEM public key")
    p_all.set_defaults(func=cmd_verify_all)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
