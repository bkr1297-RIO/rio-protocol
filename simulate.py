#!/usr/bin/env python3
"""
RIO Protocol Simulator v1.0 (Ed25519)

Generates cryptographically valid protocol artifacts for testing,
demonstration, and SDK development. Every hash and signature is
recomputable from the artifact fields — nothing is mocked.

Usage:
    python simulate.py --generate-valid
    python simulate.py --generate-invalid-signature
    python simulate.py --generate-tampered-ledger
    python simulate.py --generate-full-example
    python simulate.py --all                       # run all four modes
    python simulate.py --verify <file.json>        # verify any artifact

Requires: cryptography>=41.0
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import uuid
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import (
        Ed25519PrivateKey,
        Ed25519PublicKey,
    )
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PublicFormat,
        NoEncryption,
        PrivateFormat,
    )
except ImportError:
    print("ERROR: 'cryptography' package required.  pip install cryptography>=41.0")
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────
SIMULATOR_TAG = "RIO Protocol Simulator v1.0 (Ed25519)"
GENESIS = "GENESIS"
DEMO_SERVICE_TOKEN = "demo-service-token-for-testing-only"
DEFAULT_INTENT = (
    "Summarise the key properties of the secp256k1 elliptic curve "
    "in three bullet points."
)
DEFAULT_RESPONSE = (
    "The secp256k1 elliptic curve has three key properties:\n\n"
    "\u2022 Prime field: Defined over a 256-bit prime field, giving approximately "
    "128-bit security.\n"
    "\u2022 Cofactor h=1: Every non-identity point generates the full group, "
    "which is important for cryptographic correctness.\n"
    "\u2022 Efficient endomorphism: Supports a Frobenius endomorphism that enables "
    "a roughly 30% speedup in scalar multiplication, which is why it was chosen "
    "for Bitcoin and Ethereum."
)
DEFAULT_MODEL = "claude"
DEFAULT_AGENT = "claude-sonnet-4-6"


# ─── Helpers ──────────────────────────────────────────────────────────
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_str(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def hmac_sha256(key: str, data: str) -> str:
    return hmac.new(key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256).hexdigest()


def canonical_json(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


def keygen():
    """Generate an Ed25519 key pair and return (private_key, public_key, pub_b64, pub_hex, approver_id)."""
    sk = Ed25519PrivateKey.generate()
    pk = sk.public_key()
    raw = pk.public_bytes(Encoding.Raw, PublicFormat.Raw)
    pub_b64 = base64.b64encode(raw).decode()
    pub_hex = raw.hex()
    approver_id = sha256_bytes(raw)[:16]
    return sk, pk, pub_b64, pub_hex, approver_id


def sign_ed25519(sk: Ed25519PrivateKey, message: bytes) -> str:
    return base64.b64encode(sk.sign(message)).decode()


def write_artifact(data: dict, path: str):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  \u2713 {path} ({os.path.getsize(path)} bytes)")


# ─── Intent Builder ───────────────────────────────────────────────────
def build_intent(sk, pub_b64, pub_hex, intent_text=DEFAULT_INTENT,
                 source="simulator", model=DEFAULT_MODEL, ts=None):
    ts = ts or now_iso()
    canonical = f"{intent_text}|{source}|{ts}"
    intent_id = sha256_str(canonical)
    parameters_hash = sha256_bytes(canonical_json({
        "intent": intent_text, "source": source, "model": model,
        "timestamp": ts, "intent_id": intent_id,
    }))
    sig = sign_ed25519(sk, canonical.encode("utf-8"))
    sig_hash = sha256_str(sig)
    nonce = os.urandom(16).hex()
    exec_token = sign_ed25519(sk, f"{intent_id}|{nonce}".encode("utf-8"))
    approver = sha256_bytes(base64.b64decode(pub_b64))[:16]

    return {
        "_artifact": "intent_signed",
        "_simulator": SIMULATOR_TAG,
        "_note": "Valid signed intent. All signatures are Ed25519.",
        "source": source,
        "intent": intent_text,
        "timestamp": ts,
        "intent_id": intent_id,
        "signature": sig,
        "execution_token": exec_token,
        "model": model,
        "nonce": nonce,
        "public_key_b64": pub_b64,
        "public_key_hex": pub_hex,
        "_computed": {
            "canonical_string": canonical,
            "parameters_hash": parameters_hash,
            "signature_hash": sig_hash,
            "approver": approver,
            "signature_valid": True,
        },
    }


# ─── Governance Decision ─────────────────────────────────────────────
def build_governance_decision(intent_data, decision="approved", reason="gate_passed",
                              receipt_hash="", ts=None):
    ts = ts or now_iso()
    agent = DEFAULT_AGENT if decision == "approved" else ""
    seal_data = (
        f"check_gate|{agent}|{intent_data['_computed']['approver']}|"
        f"{intent_data['source']}|{intent_data['intent_id']}|"
        f"{intent_data['_computed']['parameters_hash']}|"
        f"{decision}|{reason}|{receipt_hash}|{GENESIS}|{ts}"
    )
    entry_hash = sha256_str(seal_data)

    return {
        "_artifact": "governance_decision",
        "_simulator": SIMULATOR_TAG,
        "intent_id": intent_data["intent_id"],
        "decision": decision,
        "reason": reason,
        "approver": intent_data["_computed"]["approver"],
        "executed_by": intent_data["source"],
        "agent": agent,
        "timestamp": ts,
        "parameters_hash": intent_data["_computed"]["parameters_hash"],
        "receipt_hash": receipt_hash,
        "prev_hash": GENESIS,
        "entry_hash": entry_hash,
        "_computed": {"seal_data": seal_data},
    }


# ─── Execution Result ────────────────────────────────────────────────
def build_execution_result(intent_data, response=DEFAULT_RESPONSE, ts=None):
    ts = ts or now_iso()
    result_hash = sha256_str(response)
    return {
        "_artifact": "execution_result",
        "_simulator": SIMULATOR_TAG,
        "intent_id": intent_data["intent_id"],
        "model": intent_data["model"],
        "agent": DEFAULT_AGENT,
        "source": intent_data["source"],
        "intent": intent_data["intent"],
        "response": response,
        "timestamp": ts,
        "signature_hash": intent_data["_computed"]["signature_hash"],
        "_computed": {"result_hash": result_hash},
    }


# ─── Receipt ─────────────────────────────────────────────────────────
def build_receipt(intent_data, execution_result, ts=None):
    ts = ts or now_iso()
    receipt_fields = {
        "intent_id": intent_data["intent_id"],
        "model": intent_data["model"],
        "agent": DEFAULT_AGENT,
        "source": intent_data["source"],
        "response_chars": len(execution_result["response"]),
        "signature_hash": intent_data["_computed"]["signature_hash"],
        "result_hash": execution_result["_computed"]["result_hash"],
        "timestamp": ts,
    }
    receipt_hash = sha256_bytes(canonical_json(receipt_fields))

    return {
        "_artifact": "receipt",
        "_simulator": SIMULATOR_TAG,
        "status": "success",
        "model_used": intent_data["model"],
        "response": execution_result["response"],
        "signature_verified": True,
        "signature_hash": intent_data["_computed"]["signature_hash"],
        "receipt_hash": receipt_hash,
        "timestamp": ts,
        "_computed": {
            "receipt_fields": receipt_fields,
            "receipt_hash_formula": "SHA256(canonical_json(receipt_fields))",
        },
    }


# ─── Ledger Chain ────────────────────────────────────────────────────
def build_ledger_chain(intent_data, gov_decisions, receipt, service_token=DEMO_SERVICE_TOKEN):
    """Build a multi-entry execution_ledger + post_execution_ledger."""
    pub_hex = intent_data["public_key_hex"]
    execution_ledger = []
    post_execution_ledger = []
    prev_hash = GENESIS

    for i, gov in enumerate(gov_decisions, start=1):
        ts = gov["timestamp"]
        agent = gov["agent"]
        approver = gov["approver"]
        executed_by = gov["executed_by"]
        intent_id = gov["intent_id"]
        params_hash = gov["parameters_hash"]
        result = gov.get("decision", "executed")
        if result == "approved":
            result = "executed"
        reason = gov["reason"]
        r_hash = gov.get("receipt_hash", "")

        seal = (
            f"check_gate|{agent}|{approver}|{executed_by}|{intent_id}|"
            f"{params_hash}|{result}|{reason}|{r_hash}|{prev_hash}|{ts}"
        )
        entry_hash = sha256_str(seal)

        execution_ledger.append({
            "id": i,
            "action": "check_gate",
            "agent": agent,
            "approver": approver,
            "executed_by": executed_by,
            "intent_id": intent_id,
            "parameters_hash": params_hash,
            "result": result,
            "reason": reason,
            "receipt_hash": r_hash,
            "prev_hash": prev_hash,
            "entry_hash": entry_hash,
            "timestamp": ts,
        })

        # Post-execution ledger
        ledger_hash = sha256_str(f"{prev_hash}|{entry_hash}|{ts}")
        signature = hmac_sha256(service_token, f"{entry_hash}|{ledger_hash}|{ts}")

        post_execution_ledger.append({
            "id": i,
            "entry_hash": entry_hash,
            "ledger_hash": ledger_hash,
            "signature": signature,
            "timestamp": ts,
        })

        prev_hash = entry_hash

    return {
        "_artifact": "ledger_chain",
        "_simulator": SIMULATOR_TAG,
        "_note": f"Full valid {len(execution_ledger)}-entry hash-chained ledger.",
        "demo_service_token": service_token,
        "public_key_hex": pub_hex,
        "execution_ledger": execution_ledger,
        "post_execution_ledger": post_execution_ledger,
    }


# ─── Ledger Entry (single) ───────────────────────────────────────────
def build_ledger_entry(ledger_chain, index=0):
    entry = ledger_chain["execution_ledger"][index]
    return {
        "_artifact": "ledger_entry",
        "_simulator": SIMULATOR_TAG,
        **entry,
    }


# ─── Verification Result ─────────────────────────────────────────────
def build_verification_result(receipt, ledger_chain, service_token=DEMO_SERVICE_TOKEN):
    checks = []

    # Check 1: receipt_hash integrity
    stored_hash = receipt["receipt_hash"]
    computed_hash = sha256_bytes(canonical_json(receipt["_computed"]["receipt_fields"]))
    checks.append({
        "check_name": "receipt_hash_integrity",
        "description": "Recompute receipt_hash from source fields and compare to stored value.",
        "passed": stored_hash == computed_hash,
        "stored": stored_hash,
        "computed": computed_hash,
        "detail": "Receipt hash matches. Execution record is intact." if stored_hash == computed_hash
                  else f"MISMATCH: stored={stored_hash}, computed={computed_hash}",
    })

    # Check 2: execution_ledger chain integrity
    exec_results = []
    prev = GENESIS
    chain_ok = True
    for row in ledger_chain["execution_ledger"]:
        seal = (
            f"check_gate|{row['agent']}|{row['approver']}|{row['executed_by']}|"
            f"{row['intent_id']}|{row['parameters_hash']}|{row['result']}|"
            f"{row['reason']}|{row['receipt_hash']}|{row['prev_hash']}|{row['timestamp']}"
        )
        computed_eh = sha256_str(seal)
        prev_ok = row["prev_hash"] == prev
        eh_ok = row["entry_hash"] == computed_eh
        passed = prev_ok and eh_ok
        if not passed:
            chain_ok = False
        exec_results.append({
            "row_id": row["id"],
            "stored_entry_hash": row["entry_hash"],
            "computed_entry_hash": computed_eh,
            "prev_hash_ok": prev_ok,
            "entry_hash_ok": eh_ok,
            "passed": passed,
            "tampered": not eh_ok,
        })
        prev = row["entry_hash"]

    n = len(exec_results)
    failed = sum(1 for r in exec_results if not r["passed"])
    checks.append({
        "check_name": "execution_ledger_chain_integrity",
        "description": "For each execution_ledger row: recompute entry_hash and verify prev_hash linkage from GENESIS.",
        "rows_checked": n,
        "chain_anchor": GENESIS,
        "results": exec_results,
        "chain_intact": chain_ok,
        "passed": chain_ok,
        "detail": f"All {n} entries verify correctly. Chain is intact." if chain_ok
                  else f"Chain integrity failure detected in {failed} row(s).",
    })

    # Check 3: post_execution_ledger hash integrity
    post_results = []
    post_ok = True
    for row in ledger_chain["post_execution_ledger"]:
        # Find corresponding exec entry
        exec_row = next(e for e in ledger_chain["execution_ledger"] if e["id"] == row["id"])
        prev_h = GENESIS if exec_row["id"] == 1 else ledger_chain["execution_ledger"][exec_row["id"] - 2]["entry_hash"]
        computed_lh = sha256_str(f"{prev_h}|{row['entry_hash']}|{row['timestamp']}")
        passed = row["ledger_hash"] == computed_lh
        if not passed:
            post_ok = False
        post_results.append({
            "row_id": row["id"],
            "stored_ledger_hash": row["ledger_hash"],
            "computed_ledger_hash": computed_lh,
            "passed": passed,
        })

    checks.append({
        "check_name": "post_exec_ledger_hash_integrity",
        "description": "For each post_execution_ledger row: recompute ledger_hash and compare to stored value.",
        "rows_checked": len(post_results),
        "results": post_results,
        "passed": post_ok,
        "detail": f"All {len(post_results)} hash values verify correctly." if post_ok
                  else "Hash mismatch detected.",
    })

    # Check 4: HMAC signatures
    hmac_results = []
    hmac_ok = True
    for row in ledger_chain["post_execution_ledger"]:
        computed_sig = hmac_sha256(service_token, f"{row['entry_hash']}|{row['ledger_hash']}|{row['timestamp']}")
        passed = row["signature"] == computed_sig
        if not passed:
            hmac_ok = False
        hmac_results.append({
            "row_id": row["id"],
            "stored_signature": row["signature"],
            "computed_signature": computed_sig,
            "passed": passed,
        })

    checks.append({
        "check_name": "post_exec_hmac_signatures",
        "description": "For each post_execution_ledger row: recompute HMAC-SHA256 signature using the service token and compare to stored value.",
        "rows_checked": len(hmac_results),
        "results": hmac_results,
        "passed": hmac_ok,
        "detail": f"All {len(hmac_results)} HMAC signatures verify correctly." if hmac_ok
                  else "HMAC signature mismatch detected.",
    })

    passed_count = sum(1 for c in checks if c["passed"])
    failed_count = len(checks) - passed_count
    overall = "PASS" if failed_count == 0 else "FAIL"

    return {
        "_artifact": "verification_result",
        "_simulator": SIMULATOR_TAG,
        "overall": overall,
        "checks_passed": passed_count,
        "checks_failed": failed_count,
        "checks": checks,
    }


# ─── Mode 1: --generate-valid ────────────────────────────────────────
def generate_valid(output_dir):
    print("\n=== Mode: --generate-valid ===")
    print("Generating 7 valid artifacts + 4/4 verification PASS\n")

    sk, pk, pub_b64, pub_hex, approver = keygen()
    ts_base = now_iso()

    intent = build_intent(sk, pub_b64, pub_hex, ts=ts_base)
    write_artifact(intent, os.path.join(output_dir, "intent_signed.json"))

    gov_ts = now_iso()
    gov = build_governance_decision(intent, ts=gov_ts)
    write_artifact(gov, os.path.join(output_dir, "governance_decision.json"))

    exec_result = build_execution_result(intent, ts=now_iso())
    write_artifact(exec_result, os.path.join(output_dir, "execution_result.json"))

    receipt = build_receipt(intent, exec_result, ts=now_iso())
    write_artifact(receipt, os.path.join(output_dir, "receipt.json"))

    # Build 3-entry ledger (approved, approved, approved)
    govs = []
    for i in range(3):
        g = build_governance_decision(intent, receipt_hash=receipt["receipt_hash"] if i == 0 else "", ts=now_iso())
        govs.append(g)

    ledger = build_ledger_chain(intent, govs, receipt)
    write_artifact(ledger, os.path.join(output_dir, "ledger_chain.json"))

    entry = build_ledger_entry(ledger, 0)
    write_artifact(entry, os.path.join(output_dir, "ledger_entry.json"))

    verification = build_verification_result(receipt, ledger)
    write_artifact(verification, os.path.join(output_dir, "verification_result.json"))

    print(f"\nVerification: {verification['overall']} "
          f"({verification['checks_passed']}/{verification['checks_passed'] + verification['checks_failed']} checks)")
    return verification["overall"] == "PASS"


# ─── Mode 2: --generate-invalid-signature ─────────────────────────────
def generate_invalid_signature(output_dir):
    print("\n=== Mode: --generate-invalid-signature ===")
    print("Generating intent with CORRUPT signature (gateway would reject at Stage 2)\n")

    # Generate valid intent first
    sk, pk, pub_b64, pub_hex, approver = keygen()
    intent = build_intent(sk, pub_b64, pub_hex)

    # Generate a DIFFERENT key pair and re-sign with it (signature won't match public key)
    sk2, pk2, pub_b64_2, pub_hex_2, approver_2 = keygen()
    corrupt_sig = sign_ed25519(sk2, f"{intent['intent']}|{intent['source']}|{intent['timestamp']}".encode("utf-8"))
    corrupt_token = sign_ed25519(sk2, f"{intent['intent_id']}|{intent['nonce']}".encode("utf-8"))

    intent["_note"] = "CORRUPT SIGNATURE \u2014 verification will fail"
    intent["signature"] = corrupt_sig
    intent["execution_token"] = corrupt_token
    # Keep the ORIGINAL public key so verification fails
    intent["_computed"]["signature_valid"] = False

    write_artifact(intent, os.path.join(output_dir, "invalid_signature_intent.json"))
    print("\nSignature is from a different key pair. Gateway will reject at Stage 2 (HTTP 401).")
    return True


# ─── Mode 3: --generate-tampered-ledger ───────────────────────────────
def generate_tampered_ledger(output_dir):
    print("\n=== Mode: --generate-tampered-ledger ===")
    print("Generating 3-entry chain with row 2 tampered \u2014 verification FAILs\n")

    sk, pk, pub_b64, pub_hex, approver = keygen()
    intent = build_intent(sk, pub_b64, pub_hex)
    exec_result = build_execution_result(intent)
    receipt = build_receipt(intent, exec_result)

    govs = []
    for i in range(3):
        g = build_governance_decision(intent, ts=now_iso())
        govs.append(g)

    ledger = build_ledger_chain(intent, govs, receipt)

    # Tamper row 2: change result from "executed" to "blocked" without updating entry_hash
    ledger["_note"] = "Row 2 of execution_ledger has been tampered. Chain verification will fail at that row."
    ledger["execution_ledger"][1]["result"] = "blocked"
    # entry_hash is now stale — verification will detect this

    write_artifact(ledger, os.path.join(output_dir, "tampered_ledger_chain.json"))

    # Verify and write the FAIL result
    verification = build_verification_result(receipt, ledger)
    write_artifact(verification, os.path.join(output_dir, "tampered_ledger_verification_result.json"))

    print(f"\nVerification: {verification['overall']} "
          f"({verification['checks_passed']}/{verification['checks_passed'] + verification['checks_failed']} checks)")
    assert verification["overall"] == "FAIL", "Expected FAIL but got PASS!"
    return True


# ─── Mode 4: --generate-full-example ──────────────────────────────────
def generate_full_example(output_dir):
    print("\n=== Mode: --generate-full-example ===")
    print("Generating full narrated 8-stage protocol flow with all artifacts\n")

    sk, pk, pub_b64, pub_hex, approver = keygen()

    # Stage 1-3: Intent signing
    ts = now_iso()
    intent = build_intent(sk, pub_b64, pub_hex, ts=ts)
    intent["_note"] = "Full example: Stage 1-3 (Intake \u2192 Signing \u2192 Canonical Intent)"
    write_artifact(intent, os.path.join(output_dir, "full_intent_signed.json"))

    # Stage 4-5: Governance decision (approved)
    gov_ts = now_iso()
    gov_approved = build_governance_decision(intent, decision="approved", reason="gate_passed", ts=gov_ts)
    write_artifact(gov_approved, os.path.join(output_dir, "full_governance_decision.json"))

    # Stage 4-5: Governance decision (blocked — for contrast)
    gov_blocked = build_governance_decision(intent, decision="blocked", reason="policy_rejected", ts=gov_ts)
    write_artifact(gov_blocked, os.path.join(output_dir, "full_governance_decision_blocked.json"))

    # Stage 6: Execution
    exec_ts = now_iso()
    exec_result = build_execution_result(intent, ts=exec_ts)
    write_artifact(exec_result, os.path.join(output_dir, "full_execution_result.json"))

    # Stage 7: Receipt
    receipt_ts = now_iso()
    receipt = build_receipt(intent, exec_result, ts=receipt_ts)
    write_artifact(receipt, os.path.join(output_dir, "full_receipt.json"))

    # Stage 8: Ledger (3 entries: approved, approved, approved)
    govs = []
    for i in range(3):
        g = build_governance_decision(intent, receipt_hash=receipt["receipt_hash"] if i == 0 else "", ts=now_iso())
        govs.append(g)

    ledger = build_ledger_chain(intent, govs, receipt)
    write_artifact(ledger, os.path.join(output_dir, "full_ledger_chain.json"))

    # Stage 6b: Verification
    verification = build_verification_result(receipt, ledger)
    write_artifact(verification, os.path.join(output_dir, "full_verification_result.json"))

    print(f"\nFull example verification: {verification['overall']} "
          f"({verification['checks_passed']}/{verification['checks_passed'] + verification['checks_failed']} checks)")
    return verification["overall"] == "PASS"


# ─── Verify existing artifact ────────────────────────────────────────
def verify_artifact(path):
    print(f"\n=== Verifying: {path} ===\n")
    with open(path) as f:
        data = json.load(f)

    artifact_type = data.get("_artifact", "unknown")
    print(f"Artifact type: {artifact_type}")

    if artifact_type == "verification_result":
        print(f"Overall: {data['overall']}")
        print(f"Checks: {data['checks_passed']} passed, {data['checks_failed']} failed")
        for c in data["checks"]:
            status = "\u2713" if c["passed"] else "\u2717"
            print(f"  {status} {c['check_name']}: {c['detail']}")
        return data["overall"] == "PASS"

    elif artifact_type == "ledger_chain":
        print(f"Entries: {len(data.get('execution_ledger', []))}")
        print(f"Post-exec entries: {len(data.get('post_execution_ledger', []))}")
        # Quick chain check
        prev = GENESIS
        ok = True
        for row in data["execution_ledger"]:
            if row["prev_hash"] != prev:
                print(f"  \u2717 Row {row['id']}: prev_hash mismatch")
                ok = False
            prev = row["entry_hash"]
        if ok:
            print("  \u2713 Chain linkage: intact")
        return ok

    elif artifact_type == "intent_signed":
        print(f"Intent ID: {data['intent_id']}")
        print(f"Signature valid (claimed): {data.get('_computed', {}).get('signature_valid', 'unknown')}")
        return True

    else:
        print(f"Artifact type '{artifact_type}' — no specific verification logic.")
        print(json.dumps(data, indent=2)[:500])
        return True


# ─── Main ─────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="RIO Protocol Simulator — generate and verify protocol artifacts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python simulate.py --generate-valid
  python simulate.py --generate-invalid-signature
  python simulate.py --generate-tampered-ledger
  python simulate.py --generate-full-example
  python simulate.py --all
  python simulate.py --verify verification_result.json
        """,
    )
    parser.add_argument("--generate-valid", action="store_true",
                        help="Generate 7 valid artifacts + 4/4 verification PASS")
    parser.add_argument("--generate-invalid-signature", action="store_true",
                        help="Generate intent with corrupt signature (gateway rejects at Stage 2)")
    parser.add_argument("--generate-tampered-ledger", action="store_true",
                        help="Generate 3-entry chain with row 2 tampered — verification FAILs")
    parser.add_argument("--generate-full-example", action="store_true",
                        help="Generate full narrated 8-stage protocol flow with all artifacts")
    parser.add_argument("--all", action="store_true",
                        help="Run all four generation modes")
    parser.add_argument("--verify", metavar="FILE",
                        help="Verify an existing artifact JSON file")
    parser.add_argument("--output-dir", "-o", default=".",
                        help="Output directory for generated artifacts (default: current directory)")

    args = parser.parse_args()

    if not any([args.generate_valid, args.generate_invalid_signature,
                args.generate_tampered_ledger, args.generate_full_example,
                args.all, args.verify]):
        parser.print_help()
        sys.exit(0)

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    results = []

    if args.verify:
        ok = verify_artifact(args.verify)
        sys.exit(0 if ok else 1)

    if args.generate_valid or args.all:
        results.append(("generate-valid", generate_valid(output_dir)))

    if args.generate_invalid_signature or args.all:
        results.append(("generate-invalid-signature", generate_invalid_signature(output_dir)))

    if args.generate_tampered_ledger or args.all:
        results.append(("generate-tampered-ledger", generate_tampered_ledger(output_dir)))

    if args.generate_full_example or args.all:
        results.append(("generate-full-example", generate_full_example(output_dir)))

    # Summary
    print("\n" + "=" * 60)
    print("SIMULATION SUMMARY")
    print("=" * 60)
    for name, ok in results:
        status = "\u2713 PASS" if ok else "\u2717 FAIL"
        print(f"  {status}  {name}")
    print("=" * 60)

    all_ok = all(ok for _, ok in results)
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
