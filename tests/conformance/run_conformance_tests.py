#!/usr/bin/env python3
"""
RIO Protocol — Conformance Test Runner
========================================
Runs the protocol test vectors (Appendix C of the RIO Protocol Specification)
and prints a summary table showing test name, expected result, actual result,
and PASS/FAIL status.

Usage:
    python run_conformance_tests.py

No external dependencies. Uses Python standard library only (hashlib, hmac).
"""

import hashlib
import hmac as hmac_module
import sys


# ── Cryptographic helpers ─────────────────────────────────────────────────────

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def hmac_sha256(key: str, msg: str) -> str:
    return hmac_module.new(
        key.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# ── Test vector definitions ───────────────────────────────────────────────────
#
# Each vector is a dict with:
#   id          : test vector ID matching Appendix C of the spec
#   name        : human-readable name
#   description : what is being tested
#   compute     : callable() -> str   (the actual computed value)
#   expected    : the expected hash value

INTENT = "Summarise the key properties of the secp256k1 elliptic curve in three bullet points."
SOURCE = "manus"
TIMESTAMP = "2026-03-26T14:00:00.000000Z"
APPROVER = "a1b2c3d4e5f6a7b8"
AGENT_STR = "claude-sonnet-4-6"
MODEL = "claude"
GATE_TS = "2026-03-26T14:00:00.512344Z"
POST_TS = "2026-03-26T14:00:03.901234Z"
RESPONSE_TS = "2026-03-26T14:00:03.847221Z"
SERVICE_TOKEN = "demo-service-token-for-testing-only"

AI_RESPONSE = (
    "The secp256k1 elliptic curve has three key properties:\n\n"
    "\u2022 Prime field: Defined over a 256-bit prime field, giving approximately 128-bit security.\n"
    "\u2022 Cofactor h=1: Every non-identity point generates the full group, which is important for cryptographic correctness.\n"
    "\u2022 Efficient endomorphism: Supports a Frobenius endomorphism that enables a roughly 30% speedup in scalar multiplication, "
    "which is why it was chosen for Bitcoin and Ethereum."
)


def tv_c1_intent_hash():
    """TV-C1: SHA-256(UTF-8_encode(intent)) — spec Section 5.5"""
    return sha256(INTENT)


def tv_c2_parameters_hash():
    """TV-C2: SHA-256(UTF-8_encode(intent + '|' + source + '|' + timestamp)) — spec Section 5.5"""
    canonical = f"{INTENT}|{SOURCE}|{TIMESTAMP}"
    return sha256(canonical)


def tv_c3_entry_hash_blocked():
    """
    TV-C3: entry_hash for a blocked execution_ledger row — spec Section 5.6.
    agent = '' and receipt_hash = '' — produces two consecutive || in seal_data.
    Field order: action|agent|approver|executed_by|intent_id|parameters_hash|
                 result|reason|receipt_hash|prev_hash|timestamp
    """
    intent_id       = tv_c1_intent_hash()
    parameters_hash = tv_c2_parameters_hash()
    fields = [
        "check_gate",            # action
        "",                      # agent (empty — blocked before model resolution)
        APPROVER,                # approver
        "manus",                 # executed_by
        intent_id,               # intent_id
        parameters_hash,         # parameters_hash
        "blocked",               # result
        "missing_token",         # reason
        "",                      # receipt_hash (empty — gate did not pass)
        "GENESIS",               # prev_hash (first entry)
        "2026-03-26T14:00:01.000000Z",  # timestamp
    ]
    seal = "|".join(fields)
    return sha256(seal)


def tv_c4_ledger_hash():
    """TV-C4: ledger_hash for a post_execution_ledger row — spec Section 5.7"""
    parameters_hash = tv_c2_parameters_hash()
    result_hash     = sha256(AI_RESPONSE)
    seal = (
        f"{POST_TS}"
        f"|{APPROVER}"
        f"|{AGENT_STR}"
        f"|manus"
        f"|success"
        f"|{parameters_hash}"
        f"|{result_hash}"
        f"|GENESIS"
    )
    return sha256(seal)


def tv_c5_hmac_signature():
    """TV-C5: HMAC-SHA256(ledger_hash, RIO_SERVICE_TOKEN) — spec Section 5.7"""
    ledger_hash = tv_c4_ledger_hash()
    return hmac_sha256(SERVICE_TOKEN, ledger_hash)


def tv_c6_in_memory_receipt_hash():
    """
    TV-C6: in-memory receipt_hash (first entry, prev_hash=GENESIS) — spec Section 5.8.
    Only the first 500 chars of ai_response are included.
    """
    response_500 = AI_RESPONSE[:500]
    data = f"GENESIS|{SOURCE}|{INTENT}|{MODEL}|{response_500}|{RESPONSE_TS}"
    return sha256(data)


def tv_c7_gate_receipt_hash():
    """TV-C7: gate receipt_hash = SHA-256('GATE_PASSED|intent_id|source|ts') — spec Section 5.5"""
    intent_id = tv_c1_intent_hash()
    data = f"GATE_PASSED|{intent_id}|{SOURCE}|{GATE_TS}"
    return sha256(data)


TEST_VECTORS = [
    {
        "id":          "TV-C1",
        "name":        "intent_hash",
        "description": "SHA-256(UTF-8_encode(intent))",
        "compute":     tv_c1_intent_hash,
        "expected":    "62ddf2d783eb52aa5f0d5aa671485a2239d5c2db01a324902dc282307301ee3a",
    },
    {
        "id":          "TV-C2",
        "name":        "parameters_hash",
        "description": "SHA-256(UTF-8_encode(intent + '|' + source + '|' + timestamp))",
        "compute":     tv_c2_parameters_hash,
        "expected":    "3becab543471433b50570a1bb0041ed79db2492e1522b4c3fe8c258543a9e356",
    },
    {
        "id":          "TV-C3",
        "name":        "entry_hash (blocked — empty agent + empty receipt_hash)",
        "description": "SHA-256 of seal_data with empty agent and empty receipt_hash (double ||)",
        "compute":     tv_c3_entry_hash_blocked,
        "expected":    "e44cced653ebcc9376c9ee741906b17b31762b60ba7bb83d6e2fdbf0efca1d29",
    },
    {
        "id":          "TV-C4",
        "name":        "ledger_hash (post-exec)",
        "description": "SHA-256(ts + '|' + approver + '|' + agent + '|' + executed_by + '|' + policy_result + '|' + parameters_hash + '|' + result_hash + '|' + prev_ledger_hash)",
        "compute":     tv_c4_ledger_hash,
        "expected":    "71032422115b7424d6d2b5fd25c12dd66534ac7510f312a88a5c3f89d5afecec",
    },
    {
        "id":          "TV-C5",
        "name":        "HMAC signature (post-exec)",
        "description": "HMAC-SHA256(key=UTF-8_encode(RIO_SERVICE_TOKEN), msg=UTF-8_encode(ledger_hash))",
        "compute":     tv_c5_hmac_signature,
        "expected":    "52fd81e93bb7318814ba7f7092a430ee35b9de3de5b04e715ecf03fb485a8263",
    },
    {
        "id":          "TV-C6",
        "name":        "in-memory receipt_hash (first entry)",
        "description": "SHA-256 with prev_hash=GENESIS and ai_response[:500]",
        "compute":     tv_c6_in_memory_receipt_hash,
        "expected":    "228cd0b0abfdf4d1cfcc6efa83abe8bc8d9b65f518153722a43cc91998498907",
    },
    {
        "id":          "TV-C7",
        "name":        "gate receipt_hash",
        "description": "SHA-256(UTF-8_encode('GATE_PASSED|' + intent_id + '|' + source + '|' + ts))",
        "compute":     tv_c7_gate_receipt_hash,
        "expected":    "272dd6571870b29bb7f8434fe4aca3f8af0a527b9ca5b8b4ccbdaf9a929bff0f",
    },
]


# ── Runner ────────────────────────────────────────────────────────────────────

def run_tests():
    col_id    = 6
    col_name  = 46
    col_stat  = 6

    header = (
        f"{'ID':<{col_id}}  {'Test Name':<{col_name}}  {'Result':<{col_stat}}"
    )
    divider = "-" * len(header)

    print()
    print("=" * len(header))
    print(" RIO Protocol — Conformance Test Runner (Appendix C)")
    print("=" * len(header))
    print()
    print(header)
    print(divider)

    results = []
    failures = []

    for tv in TEST_VECTORS:
        try:
            computed = tv["compute"]()
            passed   = computed == tv["expected"]
        except Exception as e:
            computed = f"ERROR: {e}"
            passed   = False

        status = "PASS" if passed else "FAIL"
        results.append(passed)

        name_display = tv["name"][:col_name]
        print(f"{tv['id']:<{col_id}}  {name_display:<{col_name}}  {status:<{col_stat}}")

        if not passed:
            failures.append({
                "id": tv["id"],
                "name": tv["name"],
                "expected": tv["expected"],
                "computed": computed,
                "description": tv["description"],
            })

    print(divider)

    n_pass = sum(results)
    n_fail = len(results) - n_pass
    overall = "PASS" if n_fail == 0 else "FAIL"

    print(f"\nResult: {n_pass}/{len(results)} vectors passed — Overall: {overall}")

    if failures:
        print()
        print("─" * len(header))
        print(" FAILURE DETAILS")
        print("─" * len(header))
        for f in failures:
            print(f"\n[{f['id']}] {f['name']}")
            print(f"  Description : {f['description']}")
            print(f"  Expected    : {f['expected']}")
            print(f"  Computed    : {f['computed']}")
            print()
            print("  This means your implementation of the formula above produces")
            print("  a different result. Check field order, separator character,")
            print("  UTF-8 encoding, and lowercase hex output.")

    print()
    return overall == "PASS"


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
