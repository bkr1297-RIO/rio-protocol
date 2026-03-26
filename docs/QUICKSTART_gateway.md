# RIO Protocol — Quickstart Guide

This guide explains how the RIO Protocol works and walks you through verifying a receipt end-to-end using the included demo tools.

---

## What is RIO?

RIO is a **governed execution system** that sits between AI models, human principals, and real-world actions.  It ensures that:

- Every AI invocation is **cryptographically authorized** by the system owner (via ECDSA secp256k1 signatures).
- Every execution is **single-use** — replaying a request is detected and blocked.
- Every outcome is **tamper-evidently recorded** in a hash-chained audit ledger.
- Any third party can **independently verify** past executions using only the public key and the ledger — no access to the running gateway is required.

The system enforces the rules. The AI does not.

---

## Key Concepts

### Receipt

A **receipt** is a cryptographic proof of a single governed execution. It is returned in the HTTP response immediately after the AI model runs. It contains:

| Field | Meaning |
|---|---|
| `receipt_hash` | SHA-256 seal of the in-memory ledger entry for this execution |
| `ledger_index` | Sequential position of this entry in the in-memory ledger |
| `signature_hash` | SHA-256 of the raw signature bytes — proves the specific signature was consumed |
| `model_used` | Which AI model handled this request (`claude`, `chatgpt`, or `gemini`) |
| `signature_verified` | Always `true` on a successful (HTTP 200) response |
| `timestamp` | When the response was produced |

A receipt alone proves that _an_ execution happened. Cross-referenced with the audit ledger, it proves _exactly what_ was authorized and executed.

### The Ledger

The **audit ledger** is a tamper-evident record of every gate decision (in `execution_ledger`) and every completed execution (in `post_execution_ledger`). It has two layers:

**`execution_ledger`** — one row per gate decision (pass or block):
- Contains `entry_hash`: SHA-256 of all fields in that row, including `prev_hash` from the previous row.
- This forms a hash chain: modifying any row breaks the chain for every row after it.
- Every blocked attempt is also recorded here with `result = "blocked"`.

**`post_execution_ledger`** — one row per successful AI execution:
- Contains `ledger_hash`: SHA-256 of all fields in that row.
- Contains `signature`: HMAC-SHA256 of the `ledger_hash` using `RIO_SERVICE_TOKEN`.
- Linked to `execution_ledger` via `parameters_hash`.

### The Independent Verifier

The **independent verifier** is a standalone tool (no gateway connection needed) that:

1. Recomputes every `entry_hash` in `execution_ledger` from raw fields.
2. Checks that each row's `prev_hash` equals the previous row's `entry_hash`.
3. Recomputes every `ledger_hash` in `post_execution_ledger` from raw fields.
4. Recomputes and verifies every HMAC `signature` in `post_execution_ledger`.
5. Verifies cross-table linkage via `parameters_hash`.

It requires only: the ledger data (exported from `gateway.db`) and `RIO_SERVICE_TOKEN`.

---

## How to Verify a Receipt

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

No additional packages are required for the verifier. It uses only Python's standard library (`hashlib`, `hmac`, `json`).

### Step 2 — Run the demo verifier

```bash
cd demo
python demo_verify.py
```

This loads `../examples/gateway/example_receipt_v2.json` and `../examples/gateway/example_ledger.json`, runs the independent verification logic, and prints the result.

### Expected PASS output

```
============================================================
 RIO Protocol — Independent Verifier
============================================================
 Receipt file  : ../examples/gateway/example_receipt_v2.json
 Ledger file   : ../examples/gateway/example_ledger.json
============================================================

[1/4] Receipt hash integrity ... PASS
[2/4] Execution ledger chain integrity ... PASS
[3/4] Post-execution ledger hash integrity ... PASS
[4/4] Post-execution ledger HMAC signatures ... PASS

============================================================
 Overall result: PASS
 All 4 checks passed.
============================================================
```

### Example FAIL output (tampered ledger)

```
[1/4] Receipt hash integrity ... PASS
[2/4] Execution ledger chain integrity ... FAIL
       Row id=1: entry_hash mismatch
         stored   : 0eaa56cc5107c2246a64d0492f46ca41cc0f4a89c5bc1a41a81ac64d7ef14652
         computed : 7f3a1b2c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1
       (First failure at row 1; subsequent rows may also be broken)
[3/4] Post-execution ledger hash integrity ... PASS
[4/4] Post-execution ledger HMAC signatures ... PASS

============================================================
 Overall result: FAIL
 1 of 4 checks failed.
============================================================
```

---

## How to Verify a Single Receipt Hash Manually

The in-memory ledger receipt hash formula (Section 5.8 of the protocol spec) is:

```
receipt_hash = SHA-256( prev_hash + "|" + source + "|" + intent + "|"
                       + model_used + "|" + ai_response[:500] + "|" + timestamp )
```

For the first entry: `prev_hash = "GENESIS"`.

Using Python:

```python
import hashlib

data = (
    "GENESIS"
    + "|" + "manus"
    + "|" + "Summarise the key properties of the secp256k1 elliptic curve in three bullet points."
    + "|" + "claude"
    + "|" + ai_response[:500]
    + "|" + "2026-03-26T14:00:03.847221Z"
)
receipt_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
print(receipt_hash)
# 228cd0b0abfdf4d1cfcc6efa83abe8bc8d9b65f518153722a43cc91998498907
```

---

## Reference

- **Protocol Specification**: `spec/RIO_Protocol_Specification_v1.0.md` — authoritative definition of all algorithms, schemas, and invariants.
- **JSON Spec**: `spec/RIO_Protocol_Specification_v1.0.json` — machine-readable version of the spec, suitable for code generation and tooling.
- **Conformance Guide**: `docs/CONFORMANCE.md` — how to implement and test a compliant RIO system.
- **Test Vectors**: Appendix C of the protocol spec and `tests/conformance/run_conformance_tests.py`.
