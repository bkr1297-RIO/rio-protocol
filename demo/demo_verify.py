#!/usr/bin/env python3
"""
RIO Protocol — Independent Verifier Demo
=========================================
Loads example_receipt_v2.json and example_ledger.json, runs the four
independent verification checks defined in the RIO Protocol Specification
(Section 6), and prints PASS or FAIL.

Usage:
    python demo_verify.py [--receipt PATH] [--ledger PATH] [--token TOKEN]

Defaults:
    --receipt  ../examples/gateway/example_receipt_v2.json
    --ledger   ../examples/gateway/example_ledger.json
    --token    read from ledger file's demo_service_token field

This script has NO dependency on the gateway runtime. It uses only
Python standard library modules (hashlib, hmac, json, sys, argparse).
"""

import argparse
import hashlib
import hmac as hmac_module
import json
import sys
from pathlib import Path


# ── Cryptographic helpers ─────────────────────────────────────────────────────

def sha256(s: str) -> str:
    """SHA-256 of a UTF-8-encoded string. Returns lowercase hex."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hmac_sha256(key: str, msg: str) -> str:
    """HMAC-SHA256 with UTF-8-encoded key and message. Returns lowercase hex."""
    return hmac_module.new(
        key.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# ── Verifier checks ───────────────────────────────────────────────────────────

def check_receipt_hash(receipt: dict) -> tuple[bool, str]:
    """
    Check 1: Re-derive the in-memory ledger receipt_hash and compare.

    Formula (spec Section 5.8):
        SHA-256(prev_hash + "|" + source + "|" + intent + "|"
                + model_used + "|" + ai_response[:500] + "|" + timestamp)
    """
    vi = receipt.get("_verification_inputs", {})
    prev_hash    = vi.get("prev_hash", "")
    source       = vi.get("source", "")
    intent       = vi.get("intent", "")
    model_used   = vi.get("model_used", "")
    ai_response  = vi.get("ai_response_first_500_chars", receipt.get("response", ""))[:500]
    timestamp    = vi.get("timestamp", receipt.get("timestamp", ""))
    stored       = receipt.get("receipt_hash", "")

    data = f"{prev_hash}|{source}|{intent}|{model_used}|{ai_response}|{timestamp}"
    computed = sha256(data)

    if computed == stored:
        return True, "Receipt hash matches. Execution record is intact."
    return False, (
        f"Receipt hash MISMATCH\n"
        f"  stored   : {stored}\n"
        f"  computed : {computed}"
    )


def check_execution_ledger_chain(ledger: dict) -> tuple[bool, str]:
    """
    Check 2: Re-derive entry_hash for each execution_ledger row and verify
    the hash chain.

    Formula (spec Section 5.6):
        SHA-256(action + "|" + agent + "|" + approver + "|" + executed_by + "|"
                + intent_id + "|" + parameters_hash + "|" + result + "|"
                + reason + "|" + receipt_hash + "|" + prev_hash + "|" + timestamp)
    """
    rows = ledger.get("execution_ledger", [])
    if not rows:
        return True, "No execution_ledger entries to check."

    expected_prev = "GENESIS"
    failures = []

    for row in rows:
        rid = row.get("id", "?")
        fields = [
            row.get("action", ""),
            row.get("agent", ""),
            row.get("approver", ""),
            row.get("executed_by", ""),
            row.get("intent_id", ""),
            row.get("parameters_hash", ""),
            row.get("result", ""),
            row.get("reason", ""),
            row.get("receipt_hash", ""),
            row.get("prev_hash", ""),
            row.get("timestamp", ""),
        ]
        seal_data = "|".join(fields)
        computed_entry_hash = sha256(seal_data)
        stored_entry_hash   = row.get("entry_hash", "")
        stored_prev_hash    = row.get("prev_hash", "")

        if stored_prev_hash != expected_prev:
            failures.append(
                f"Row id={rid}: prev_hash mismatch\n"
                f"  expected : {expected_prev}\n"
                f"  stored   : {stored_prev_hash}"
            )
        if computed_entry_hash != stored_entry_hash:
            failures.append(
                f"Row id={rid}: entry_hash mismatch\n"
                f"  stored   : {stored_entry_hash}\n"
                f"  computed : {computed_entry_hash}"
            )

        expected_prev = stored_entry_hash  # advance chain pointer

    if failures:
        detail = "\n       ".join(failures[:3])
        if len(failures) > 3:
            detail += f"\n       ... ({len(failures) - 3} more failure(s) not shown)"
        return False, f"Chain BROKEN at first error:\n       {detail}"

    return True, f"All {len(rows)} execution_ledger entries verify correctly. Chain is intact."


def check_post_exec_ledger_hashes(ledger: dict) -> tuple[bool, str]:
    """
    Check 3: Re-derive ledger_hash for each post_execution_ledger row.

    Formula (spec Section 5.7):
        SHA-256(timestamp + "|" + approver + "|" + agent + "|" + executed_by + "|"
                + policy_result + "|" + parameters_hash + "|" + result_hash + "|"
                + prev_ledger_hash)
    """
    rows = ledger.get("post_execution_ledger", [])
    if not rows:
        return True, "No post_execution_ledger entries to check."

    expected_prev = "GENESIS"
    failures = []

    for row in rows:
        rid = row.get("id", "?")
        seal_data = "|".join([
            row.get("timestamp", ""),
            row.get("approver", ""),
            row.get("agent", ""),
            row.get("executed_by", ""),
            row.get("policy_result", ""),
            row.get("parameters_hash", ""),
            row.get("result_hash", ""),
            expected_prev,
        ])
        computed = sha256(seal_data)
        stored   = row.get("ledger_hash", "")

        if computed != stored:
            failures.append(
                f"Row id={rid}: ledger_hash mismatch\n"
                f"  stored   : {stored}\n"
                f"  computed : {computed}"
            )

        expected_prev = stored  # advance chain pointer

    if failures:
        detail = "\n       ".join(failures[:3])
        return False, f"Hash mismatch:\n       {detail}"

    return True, f"All {len(rows)} post_execution_ledger hash values verify correctly."


def check_post_exec_hmac_signatures(ledger: dict, service_token: str) -> tuple[bool, str]:
    """
    Check 4: Re-derive HMAC-SHA256 signature for each post_execution_ledger row.

    Formula (spec Section 5.7):
        HMAC-SHA256(key=UTF-8_encode(RIO_SERVICE_TOKEN), msg=UTF-8_encode(ledger_hash))
    """
    rows = ledger.get("post_execution_ledger", [])
    if not rows:
        return True, "No post_execution_ledger entries to check."

    failures = []
    for row in rows:
        rid    = row.get("id", "?")
        lhash  = row.get("ledger_hash", "")
        stored = row.get("signature", "")

        if stored == "key_unavailable":
            failures.append(f"Row id={rid}: signature is 'key_unavailable' (token was not set at write time).")
            continue

        computed = hmac_sha256(service_token, lhash)
        if computed != stored:
            failures.append(
                f"Row id={rid}: HMAC mismatch\n"
                f"  stored   : {stored}\n"
                f"  computed : {computed}"
            )

    if failures:
        detail = "\n       ".join(failures[:3])
        return False, f"HMAC verification failed:\n       {detail}"

    return True, f"All {len(rows)} HMAC signatures verify correctly with the provided service token."


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="RIO Protocol Independent Verifier Demo")
    script_dir = Path(__file__).parent
    examples_dir = script_dir.parent / "examples" / "gateway"

    parser.add_argument(
        "--receipt",
        default=str(examples_dir / "example_receipt_v2.json"),
        help="Path to the receipt JSON file",
    )
    parser.add_argument(
        "--ledger",
        default=str(examples_dir / "example_ledger.json"),
        help="Path to the ledger JSON file",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="RIO_SERVICE_TOKEN (overrides ledger file's demo_service_token field)",
    )
    args = parser.parse_args()

    # Load files
    try:
        with open(args.receipt) as f:
            receipt = json.load(f)
    except Exception as e:
        print(f"ERROR: Cannot load receipt file: {e}")
        sys.exit(1)

    try:
        with open(args.ledger) as f:
            ledger = json.load(f)
    except Exception as e:
        print(f"ERROR: Cannot load ledger file: {e}")
        sys.exit(1)

    service_token = args.token or ledger.get("demo_service_token", "")
    if not service_token:
        print("ERROR: No service token provided. Pass --token or include demo_service_token in the ledger file.")
        sys.exit(1)

    # Print header
    print()
    print("=" * 60)
    print(" RIO Protocol — Independent Verifier")
    print("=" * 60)
    print(f" Receipt file  : {args.receipt}")
    print(f" Ledger file   : {args.ledger}")
    print("=" * 60)
    print()

    # Run checks
    checks = [
        ("Receipt hash integrity",                  lambda: check_receipt_hash(receipt)),
        ("Execution ledger chain integrity",         lambda: check_execution_ledger_chain(ledger)),
        ("Post-execution ledger hash integrity",     lambda: check_post_exec_ledger_hashes(ledger)),
        ("Post-execution ledger HMAC signatures",    lambda: check_post_exec_hmac_signatures(ledger, service_token)),
    ]

    results = []
    for i, (name, fn) in enumerate(checks, 1):
        passed, detail = fn()
        results.append(passed)
        status = "PASS" if passed else "FAIL"
        print(f"[{i}/{len(checks)}] {name} ... {status}")
        if not passed:
            for line in detail.split("\n"):
                print(f"       {line}")
        print()

    # Summary
    n_pass = sum(results)
    n_fail = len(results) - n_pass
    overall = "PASS" if n_fail == 0 else "FAIL"

    print("=" * 60)
    print(f" Overall result: {overall}")
    if n_fail == 0:
        print(f" All {n_pass} checks passed.")
    else:
        print(f" {n_fail} of {len(results)} checks FAILED.")
    print("=" * 60)
    print()

    sys.exit(0 if overall == "PASS" else 1)


if __name__ == "__main__":
    main()
