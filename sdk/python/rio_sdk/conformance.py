"""
RIO Protocol SDK — Conformance Test Runner
===========================================
Runs the Appendix C test vectors from the RIO Protocol Specification v1.0
and returns a structured pass/fail summary.

Usage:
    from rio_sdk import run_conformance_tests
    result = run_conformance_tests()
    print(result["overall"])  # "PASS" or "FAIL"
"""

import hashlib
import hmac as hmac_module
from pathlib import Path
from typing import Optional


# ── Crypto helpers ────────────────────────────────────────────────────────────

def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hmac_sha256(key: str, msg: str) -> str:
    return hmac_module.new(
        key.encode("utf-8"),
        msg.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


# ── Built-in test vectors (Appendix C of the protocol spec) ──────────────────

_INTENT    = "Summarise the key properties of the secp256k1 elliptic curve in three bullet points."
_SOURCE    = "manus"
_TIMESTAMP = "2026-03-26T14:00:00.000000Z"
_APPROVER  = "a1b2c3d4e5f6a7b8"
_AGENT     = "claude-sonnet-4-6"
_MODEL     = "claude"
_GATE_TS   = "2026-03-26T14:00:00.512344Z"
_POST_TS   = "2026-03-26T14:00:03.901234Z"
_RESP_TS   = "2026-03-26T14:00:03.847221Z"
_TOKEN     = "demo-service-token-for-testing-only"
_AI_RESP   = (
    "The secp256k1 elliptic curve has three key properties:\n\n"
    "\u2022 Prime field: Defined over a 256-bit prime field, giving approximately 128-bit security.\n"
    "\u2022 Cofactor h=1: Every non-identity point generates the full group, "
    "which is important for cryptographic correctness.\n"
    "\u2022 Efficient endomorphism: Supports a Frobenius endomorphism that enables "
    "a roughly 30% speedup in scalar multiplication, which is why it was chosen "
    "for Bitcoin and Ethereum."
)


def _tv_c1():
    return _sha256(_INTENT)

def _tv_c2():
    return _sha256(f"{_INTENT}|{_SOURCE}|{_TIMESTAMP}")

def _tv_c3():
    intent_id       = _tv_c1()
    parameters_hash = _tv_c2()
    fields = [
        "check_gate", "", _APPROVER, "manus",
        intent_id, parameters_hash,
        "blocked", "missing_token", "",
        "GENESIS", "2026-03-26T14:00:01.000000Z",
    ]
    return _sha256("|".join(fields))

def _tv_c4():
    parameters_hash = _tv_c2()
    result_hash     = _sha256(_AI_RESP)
    seal = "|".join([_POST_TS, _APPROVER, _AGENT, "manus",
                     "success", parameters_hash, result_hash, "GENESIS"])
    return _sha256(seal)

def _tv_c5():
    return _hmac_sha256(_TOKEN, _tv_c4())

def _tv_c6():
    resp_500 = _AI_RESP[:500]
    data = f"GENESIS|{_SOURCE}|{_INTENT}|{_MODEL}|{resp_500}|{_RESP_TS}"
    return _sha256(data)

def _tv_c7():
    intent_id = _tv_c1()
    return _sha256(f"GATE_PASSED|{intent_id}|{_SOURCE}|{_GATE_TS}")


_BUILTIN_VECTORS = [
    {
        "id": "TV-C1", "name": "intent_hash",
        "description": "SHA-256(UTF-8_encode(intent))",
        "compute": _tv_c1,
        "expected": "62ddf2d783eb52aa5f0d5aa671485a2239d5c2db01a324902dc282307301ee3a",
    },
    {
        "id": "TV-C2", "name": "parameters_hash",
        "description": "SHA-256(UTF-8_encode(intent + '|' + source + '|' + timestamp))",
        "compute": _tv_c2,
        "expected": "3becab543471433b50570a1bb0041ed79db2492e1522b4c3fe8c258543a9e356",
    },
    {
        "id": "TV-C3", "name": "entry_hash (blocked)",
        "description": "entry_hash with empty agent and empty receipt_hash (double ||)",
        "compute": _tv_c3,
        "expected": "e44cced653ebcc9376c9ee741906b17b31762b60ba7bb83d6e2fdbf0efca1d29",
    },
    {
        "id": "TV-C4", "name": "ledger_hash (post-exec)",
        "description": "SHA-256 of pipe-delimited post-execution seal fields",
        "compute": _tv_c4,
        "expected": "71032422115b7424d6d2b5fd25c12dd66534ac7510f312a88a5c3f89d5afecec",
    },
    {
        "id": "TV-C5", "name": "HMAC signature",
        "description": "HMAC-SHA256(key=service_token, msg=ledger_hash)",
        "compute": _tv_c5,
        "expected": "52fd81e93bb7318814ba7f7092a430ee35b9de3de5b04e715ecf03fb485a8263",
    },
    {
        "id": "TV-C6", "name": "in-memory receipt_hash",
        "description": "SHA-256 with GENESIS prev_hash and ai_response[:500]",
        "compute": _tv_c6,
        "expected": "228cd0b0abfdf4d1cfcc6efa83abe8bc8d9b65f518153722a43cc91998498907",
    },
    {
        "id": "TV-C7", "name": "gate receipt_hash",
        "description": "SHA-256(UTF-8_encode('GATE_PASSED|intent_id|source|ts'))",
        "compute": _tv_c7,
        "expected": "272dd6571870b29bb7f8434fe4aca3f8af0a527b9ca5b8b4ccbdaf9a929bff0f",
    },
]


# ── Public API ────────────────────────────────────────────────────────────────

def run_conformance_tests(test_directory: Optional[str] = None) -> dict:
    """
    Run the RIO Protocol Appendix C test vectors.

    Args:
        test_directory: Optional path to a directory containing custom test
                        vector JSON files. If None, the built-in Appendix C
                        vectors are used.

                        Custom vector files must be JSON with the structure:
                        {
                          "id": "CUSTOM-01",
                          "name": "my test",
                          "description": "what it tests",
                          "input_string": "the string to hash",
                          "formula": "sha256",
                          "expected": "abc123..."
                        }

    Returns:
        dict with keys:
            overall         "PASS" or "FAIL"
            total           int — number of vectors run
            passed          int
            failed          int
            results         list of per-vector result dicts, each with:
                              id, name, description, passed, expected, computed, error
    """
    vectors = list(_BUILTIN_VECTORS)

    # Load custom vectors if a directory was provided
    if test_directory:
        p = Path(test_directory)
        for f in sorted(p.glob("*.json")):
            try:
                import json
                with open(f) as fh:
                    tv = json.load(fh)
                # Build a simple callable that hashes input_string
                input_str = tv.get("input_string", "")
                formula   = tv.get("formula", "sha256").lower()
                if formula == "sha256":
                    fn = lambda s=input_str: _sha256(s)
                else:
                    fn = lambda s=input_str: f"unsupported_formula:{formula}"
                vectors.append({
                    "id":          tv.get("id", f.stem),
                    "name":        tv.get("name", f.stem),
                    "description": tv.get("description", ""),
                    "compute":     fn,
                    "expected":    tv.get("expected", ""),
                })
            except Exception as e:
                vectors.append({
                    "id": f.stem, "name": str(f),
                    "description": "custom vector",
                    "compute": lambda e=e: (_ for _ in ()).throw(e),
                    "expected": "",
                })

    results = []
    for tv in vectors:
        try:
            computed = tv["compute"]()
            passed   = computed == tv["expected"]
            error    = None
        except Exception as exc:
            computed = ""
            passed   = False
            error    = str(exc)

        results.append({
            "id":          tv["id"],
            "name":        tv["name"],
            "description": tv["description"],
            "passed":      passed,
            "expected":    tv["expected"],
            "computed":    computed,
            "error":       error,
        })

    n_pass = sum(1 for r in results if r["passed"])
    n_fail = len(results) - n_pass

    return {
        "overall": "PASS" if n_fail == 0 else "FAIL",
        "total":   len(results),
        "passed":  n_pass,
        "failed":  n_fail,
        "results": results,
    }
