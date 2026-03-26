#!/usr/bin/env python3
"""
RIO Protocol — Conformance Test Runner (WS7)
=============================================
Runs all automatable conformance tests against WS3 test vectors using the
independent verifier package. Produces a summary table and exit code.

Usage:
    python tests/run_conformance.py
    python tests/run_conformance.py --level 1
    python tests/run_conformance.py --level 2
    python tests/run_conformance.py --verbose
    python tests/run_conformance.py --json

Exit codes:
    0 — All tests passed
    1 — One or more tests failed
    2 — Setup error (missing files, import failure)
"""

import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# ── Resolve paths ────────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent
VECTORS_DIR = REPO_ROOT / "tests" / "vectors"
CONFORMANCE_DIR = REPO_ROOT / "tests" / "conformance"

# Add repo root to sys.path so we can import verification/
sys.path.insert(0, str(REPO_ROOT))

try:
    from verification.receipt_verifier import verify_receipt, verify_receipt_from_file
    from verification.ledger_verifier import verify_ledger, verify_ledger_from_file
    from verification.models import (
        GENESIS_HASH, VALID_DECISIONS, SIGNED_FIELDS_19,
        ALL_REQUIRED_FIELDS, COMPUTED_FIELDS_3,
    )
    from verification.hash_utils import (
        compute_request_hash, compute_receipt_hash,
        compute_ledger_chain_hash, compute_genesis_hash,
        compute_public_key_fingerprint,
    )
    from verification.crypto_utils import load_public_key, verify_signature
    from verification.schema_validator import validate_receipt_schema, validate_ledger_entry_schema
except ImportError as e:
    print(f"SETUP ERROR: Cannot import verification package: {e}")
    print("Ensure the verification/ package is present at the repository root.")
    sys.exit(2)


# ── Helper: load JSON ────────────────────────────────────────────────────────
def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_pem(path: Path) -> str:
    return path.read_text()


# ── Test result container ────────────────────────────────────────────────────
class TestResult:
    def __init__(self, test_id: str, level: int, title: str, expected: str, actual: str, passed: bool, details: str = ""):
        self.test_id = test_id
        self.level = level
        self.title = title
        self.expected = expected
        self.actual = actual
        self.passed = passed
        self.details = details

    def to_dict(self) -> dict:
        return {
            "test_id": self.test_id,
            "level": self.level,
            "title": self.title,
            "expected": self.expected,
            "actual": self.actual,
            "result": "PASS" if self.passed else "FAIL",
            "details": self.details,
        }


# ── Test definitions ─────────────────────────────────────────────────────────
def run_all_tests(verbose: bool = False) -> list[TestResult]:
    results: list[TestResult] = []

    # Load shared resources
    try:
        pub_key_pem = load_pem(VECTORS_DIR / "public_key.pem")
        receipt_valid = load_json(VECTORS_DIR / "receipt_valid_approved.json")
        receipt_denied = load_json(VECTORS_DIR / "receipt_valid_denied.json")
        receipt_invalid_sig = load_json(VECTORS_DIR / "receipt_invalid_signature.json")
        receipt_invalid_hash = load_json(VECTORS_DIR / "receipt_invalid_hash.json")
        receipt_invalid_intent = load_json(VECTORS_DIR / "receipt_invalid_intent_hash.json")
        receipt_missing = load_json(VECTORS_DIR / "receipt_missing_fields.json")
        ledger_valid = load_json(VECTORS_DIR / "ledger_chain_valid.json")
        ledger_tampered = load_json(VECTORS_DIR / "ledger_chain_tampered.json")
        ledger_deleted = load_json(VECTORS_DIR / "ledger_chain_deleted_entry.json")
        hash_examples = load_json(VECTORS_DIR / "hash_computation_examples.json")
        signing_examples = load_json(VECTORS_DIR / "signing_payload_examples.json")
    except FileNotFoundError as e:
        print(f"SETUP ERROR: Missing test vector file: {e}")
        sys.exit(2)

    # ── LEVEL 1: Receipt Format Compliance (16 tests) ────────────────────

    # TC-V2-001: Valid receipt — all 22 fields present
    r = verify_receipt(receipt_valid, pub_key_pem)
    schema_check = next((c for c in r.checks if c.check_name == "required_fields"), None)
    results.append(TestResult(
        "TC-V2-001", 1, "Valid receipt: all 22 required fields present",
        "PASS", "PASS" if (schema_check and schema_check.passed) else "FAIL",
        schema_check.passed if schema_check else False,
    ))

    # TC-V2-002: Valid receipt — request_hash matches
    hash_check = next((c for c in r.checks if c.check_name == "request_hash"), None)
    results.append(TestResult(
        "TC-V2-002", 1, "Valid receipt: request_hash matches canonical payload",
        "PASS", "PASS" if (hash_check and hash_check.passed) else "FAIL",
        hash_check.passed if hash_check else False,
    ))

    # TC-V2-002b: Invalid intent hash receipt — request_hash mismatch detected
    r_intent = verify_receipt(receipt_invalid_intent, pub_key_pem)
    hash_check_bad = next((c for c in r_intent.checks if c.check_name == "request_hash"), None)
    results.append(TestResult(
        "TC-V2-002b", 1, "Invalid intent hash: request_hash mismatch detected",
        "FAIL", "FAIL" if (hash_check_bad and not hash_check_bad.passed) else "PASS",
        (hash_check_bad is not None and not hash_check_bad.passed),
    ))

    # TC-V2-003: Valid receipt — receipt_hash matches signed payload
    receipt_hash_check = next((c for c in r.checks if c.check_name == "receipt_hash"), None)
    results.append(TestResult(
        "TC-V2-003", 1, "Valid receipt: receipt_hash matches 19-field signed payload",
        "PASS", "PASS" if (receipt_hash_check and receipt_hash_check.passed) else "FAIL",
        receipt_hash_check.passed if receipt_hash_check else False,
    ))

    # TC-V2-003b: Invalid hash receipt — receipt_hash mismatch detected
    r_bad_hash = verify_receipt(receipt_invalid_hash, pub_key_pem)
    rh_check_bad = next((c for c in r_bad_hash.checks if c.check_name == "receipt_hash"), None)
    results.append(TestResult(
        "TC-V2-003b", 1, "Invalid hash: receipt_hash mismatch detected",
        "FAIL", "FAIL" if (rh_check_bad and not rh_check_bad.passed) else "PASS",
        (rh_check_bad is not None and not rh_check_bad.passed),
    ))

    # TC-V2-005: Valid receipt — Ed25519 signature valid
    sig_check = next((c for c in r.checks if c.check_name == "signature"), None)
    results.append(TestResult(
        "TC-V2-005", 1, "Valid receipt: Ed25519 signature verification passes",
        "PASS", "PASS" if (sig_check and sig_check.passed) else "FAIL",
        sig_check.passed if sig_check else False,
    ))

    # TC-V2-005b: Invalid signature receipt — signature verification fails
    r_bad_sig = verify_receipt(receipt_invalid_sig, pub_key_pem)
    sig_check_bad = next((c for c in r_bad_sig.checks if c.check_name == "signature"), None)
    results.append(TestResult(
        "TC-V2-005b", 1, "Invalid signature: Ed25519 signature verification fails",
        "FAIL", "FAIL" if (sig_check_bad and not sig_check_bad.passed) else "PASS",
        (sig_check_bad is not None and not sig_check_bad.passed),
    ))

    # TC-V2-006: Valid receipt — public key fingerprint matches
    fp_check = next((c for c in r.checks if c.check_name == "public_key_fingerprint"), None)
    results.append(TestResult(
        "TC-V2-006", 1, "Valid receipt: public key fingerprint matches",
        "PASS", "PASS" if (fp_check and fp_check.passed) else "FAIL",
        fp_check.passed if fp_check else False,
    ))

    # TC-V2-007: Valid receipt — decision is valid enum value
    dec_check = next((c for c in r.checks if c.check_name == "decision_valid"), None)
    results.append(TestResult(
        "TC-V2-007", 1, "Valid receipt: decision is valid enum (allow/modify/block/escalate)",
        "PASS", "PASS" if (dec_check and dec_check.passed) else "FAIL",
        dec_check.passed if dec_check else False,
    ))

    # TC-V2-008: Valid denied receipt — all checks pass
    r_denied = verify_receipt(receipt_denied, pub_key_pem)
    results.append(TestResult(
        "TC-V2-008", 1, "Valid denied receipt: all 7 checks pass (decision=block)",
        "PASS", "PASS" if r_denied.all_passed else "FAIL",
        r_denied.all_passed,
    ))

    # TC-V2-009: Missing fields receipt — schema validation fails
    r_missing = verify_receipt(receipt_missing, pub_key_pem)
    missing_schema = next((c for c in r_missing.checks if c.check_name == "required_fields"), None)
    results.append(TestResult(
        "TC-V2-009", 1, "Missing fields: schema validation detects missing required fields",
        "FAIL", "FAIL" if (missing_schema and not missing_schema.passed) else "PASS",
        (missing_schema is not None and not missing_schema.passed),
    ))

    # TC-V2-010: Full valid receipt — all 7 checks pass
    results.append(TestResult(
        "TC-V2-010", 1, "Full valid receipt: all 7 verification checks pass",
        "PASS", "PASS" if r.all_passed else "FAIL",
        r.all_passed,
    ))

    # TC-GOV-001: Valid receipt has governance_decision field
    receipt_data = receipt_valid.get("receipt", receipt_valid)
    has_gov = "governance_decision" in receipt_data or "decision" in receipt_data
    results.append(TestResult(
        "TC-GOV-001", 1, "Governance: receipt contains decision field",
        "PASS", "PASS" if has_gov else "FAIL",
        has_gov,
    ))

    # TC-GOV-002: Decision value is from valid enum
    decision_val = receipt_data.get("governance_decision", receipt_data.get("decision", ""))
    is_valid_dec = decision_val in VALID_DECISIONS
    results.append(TestResult(
        "TC-GOV-002", 1, "Governance: decision value is from valid enum set",
        "PASS", "PASS" if is_valid_dec else "FAIL",
        is_valid_dec,
    ))

    # TC-GOV-003: Receipt contains timestamp
    has_ts = "timestamp" in receipt_data
    results.append(TestResult(
        "TC-GOV-003", 1, "Governance: receipt contains timestamp field",
        "PASS", "PASS" if has_ts else "FAIL",
        has_ts,
    ))

    # TC-POLICY-001: Receipt contains risk assessment field
    has_risk = any(k in receipt_data for k in ("risk_score", "risk_level", "risk_category", "threshold_results"))
    results.append(TestResult(
        "TC-POLICY-001", 1, "Policy: receipt contains risk assessment field",
        "PASS", "PASS" if has_risk else "FAIL",
        has_risk,
    ))

    # TC-INTENT-001: Receipt contains intent_type or request_type field
    has_intent = any(k in receipt_data for k in ("intent_type", "request_type", "request_canonical_payload"))
    results.append(TestResult(
        "TC-INTENT-001", 1, "Intent: receipt contains intent/request classification",
        "PASS", "PASS" if has_intent else "FAIL",
        has_intent,
    ))

    # ── LEVEL 2: Ledger + Verification Compliance (6 tests) ─────────────

    # TC-LEDG-001: Valid ledger chain — all entries verify
    lr = verify_ledger(ledger_valid)
    results.append(TestResult(
        "TC-LEDG-001", 2, "Valid ledger: hash chain integrity verified",
        "PASS", "PASS" if lr.chain_intact else "FAIL",
        lr.chain_intact,
    ))

    # TC-LEDG-002: Tampered ledger — chain integrity failure detected
    lr_tampered = verify_ledger(ledger_tampered)
    results.append(TestResult(
        "TC-LEDG-002", 2, "Tampered ledger: chain integrity failure detected",
        "FAIL", "FAIL" if not lr_tampered.chain_intact else "PASS",
        not lr_tampered.chain_intact,
    ))

    # TC-LEDG-003: Deleted entry ledger — chain integrity failure detected
    lr_deleted = verify_ledger(ledger_deleted)
    results.append(TestResult(
        "TC-LEDG-003", 2, "Deleted entry: chain integrity failure detected",
        "FAIL", "FAIL" if not lr_deleted.chain_intact else "PASS",
        not lr_deleted.chain_intact,
    ))

    # TC-LEDG-004a: Genesis hash matches SHA256(b'GENESIS')
    computed_genesis = compute_genesis_hash()
    results.append(TestResult(
        "TC-LEDG-004a", 2, "Genesis: computed genesis hash matches protocol constant",
        "PASS", "PASS" if computed_genesis == GENESIS_HASH else "FAIL",
        computed_genesis == GENESIS_HASH,
    ))

    # TC-LEDG-004b: First ledger entry prev_ledger_hash == GENESIS_HASH
    chain_data = ledger_valid if isinstance(ledger_valid, list) else ledger_valid.get("chain", ledger_valid.get("entries", []))
    # Handle dict-with-entry_N-keys format (e.g. {"genesis_hash": ..., "entry_0": {...}, "entry_1": {...}})
    if isinstance(chain_data, dict):
        entry_keys = sorted([k for k in chain_data if k.startswith("entry_")], key=lambda k: int(k.split("_")[1]))
        if entry_keys:
            chain_data = [chain_data[k] for k in entry_keys]
        else:
            chain_data = chain_data.get("chain", chain_data.get("entries", []))
    first_prev = chain_data[0].get("prev_ledger_hash", "") if chain_data else ""
    genesis_match = first_prev == GENESIS_HASH
    results.append(TestResult(
        "TC-LEDG-004b", 2, "Genesis: first entry prev_ledger_hash equals GENESIS_HASH",
        "PASS", "PASS" if genesis_match else "FAIL",
        genesis_match,
    ))

    # TC-LEDG-005 (bonus): Full independent verification passes on valid receipt
    results.append(TestResult(
        "TC-V2-010b", 2, "Full independent verification: receipt + ledger both pass",
        "PASS", "PASS" if (r.all_passed and lr.chain_intact) else "FAIL",
        r.all_passed and lr.chain_intact,
    ))

    return results


# ── Output formatting ────────────────────────────────────────────────────────
def print_table(results: list[TestResult], verbose: bool = False):
    header = f"{'Test ID':<14} {'Level':<6} {'Expected':<10} {'Actual':<10} {'Result':<8} {'Title'}"
    separator = "-" * len(header)
    print(separator)
    print(header)
    print(separator)
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"{r.test_id:<14} L{r.level:<5} {r.expected:<10} {r.actual:<10} {status:<8} {r.title}")
        if verbose and r.details:
            print(f"{'':>14} Detail: {r.details}")
    print(separator)


def print_json(results: list[TestResult]):
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runner_version": "1.0.0",
        "total_tests": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "results": [r.to_dict() for r in results],
    }
    print(json.dumps(output, indent=2))


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="RIO Protocol Conformance Test Runner (WS7)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--level", type=int, choices=[1, 2, 3],
                        help="Run only tests up to this conformance level (default: all)")
    parser.add_argument("--verbose", action="store_true",
                        help="Show detailed check information for each test")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON instead of table")
    args = parser.parse_args()

    results = run_all_tests(verbose=args.verbose)

    # Filter by level if requested
    if args.level:
        results = [r for r in results if r.level <= args.level]

    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    level_str = f" (Level 1-{args.level})" if args.level else ""

    if args.json_output:
        print_json(results)
    else:
        print()
        print("=" * 66)
        print(" RIO Protocol \u2014 Conformance Test Runner v1.0")
        print(f" Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
        print(f" Vectors:   {VECTORS_DIR}")
        print("=" * 66)
        print()
        print_table(results, verbose=args.verbose)

    print()
    print(f"Result: {passed}/{total} tests passed{level_str} \u2014 Overall: {'PASS' if failed == 0 else 'FAIL'}")
    print()

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
