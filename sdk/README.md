# RIO Protocol SDK

Simple, dependency-free SDKs for verifying RIO receipts and ledgers, running conformance tests, and checking compliance level.

Available in **Python** (`sdk/python/`) and **JavaScript** (`sdk/javascript/`).

---

## What the SDK does

| Function | Description |
|---|---|
| `verify_receipt(receipt, ledger)` | Verify a RIO receipt against a ledger — 4 checks |
| `verify_ledger(ledger)` | Verify ledger chain integrity without a receipt |
| `run_conformance_tests()` | Run all Appendix C hash test vectors |
| `get_compliance_level(directory)` | Detect Level 1 / 2 / 3 compliance in a project |

All verification is done **locally** — no gateway connection, no network calls, no external dependencies.

---

## Python SDK

### Installation

```bash
cd sdk/python
pip install -e .
```

Or without installing:

```python
import sys
sys.path.insert(0, "sdk/python")
from rio_sdk import verify_receipt, verify_ledger, run_conformance_tests, get_compliance_level
```

### Verify a receipt

```python
from rio_sdk import verify_receipt

result = verify_receipt(
    "examples/example_receipt_v2.json",
    "examples/example_ledger.json",
)

print(result["overall"])          # "PASS" or "FAIL"
print(result["checks_passed"])    # 4
print(result["checks_failed"])    # 0

for check in result["checks"]:
    print(check["check_name"], "→", "PASS" if check["passed"] else "FAIL")
    print("  ", check["detail"])
```

**Output:**
```
PASS
4
0
receipt_hash_integrity → PASS
   Receipt hash matches. Execution record is intact.
execution_ledger_chain_integrity → PASS
   All 1 entries verify correctly. Chain is intact.
post_exec_ledger_hash_integrity → PASS
   All 1 hash values verify correctly.
post_exec_hmac_signatures → PASS
   All 1 HMAC signatures verify correctly.
```

### Verify a ledger only

```python
from rio_sdk import verify_ledger

result = verify_ledger("examples/example_ledger.json")
print(result["overall"])   # "PASS"
```

### Run conformance tests

```python
from rio_sdk import run_conformance_tests

result = run_conformance_tests()

print(result["overall"])   # "PASS"
print(result["passed"])    # 7
print(result["total"])     # 7

for r in result["results"]:
    status = "PASS" if r["passed"] else "FAIL"
    print(f"{r['id']:8} {r['name']:40} {status}")
```

**Output:**
```
TV-C1    intent_hash                              PASS
TV-C2    parameters_hash                          PASS
TV-C3    entry_hash (blocked)                     PASS
TV-C4    ledger_hash (post-exec)                  PASS
TV-C5    HMAC signature                           PASS
TV-C6    in-memory receipt_hash (first entry)     PASS
TV-C7    gate receipt_hash                        PASS
```

### Check compliance level

```python
from rio_sdk import get_compliance_level

result = get_compliance_level("/path/to/rio-gateway")

print(result["level"])   # 3
print(result["label"])   # "Level 3 — Full Protocol Compliance"

for check in result["checks"]:
    print(f"Level {check['level']}: {'PASS' if check['passed'] else 'FAIL'} — {check['detail']}")
```

**Level definitions:**

| Level | Name | What is verified |
|---|---|---|
| 0 | Non-Compliant | Conformance test vectors fail |
| 1 | Cryptographic Compliance | All 7 hash test vectors pass |
| 2 | Pipeline Compliance | Level 1 + `gateway.db` with intact `execution_ledger` chain |
| 3 | Full Protocol Compliance | Level 2 + `post_execution_ledger` with valid HMAC signatures |

### Using pre-loaded dicts

All functions accept either file paths or pre-loaded Python dicts:

```python
import json
receipt = json.load(open("receipt.json"))
ledger  = json.load(open("ledger.json"))
result  = verify_receipt(receipt, ledger, service_token="your-token")
```

### Service token

The HMAC check (Check 4) requires `RIO_SERVICE_TOKEN`. Priority order:

1. `service_token=` keyword argument
2. `RIO_SERVICE_TOKEN` environment variable
3. `demo_service_token` field in the ledger JSON (demo only)

---

## JavaScript SDK

### Usage (no install required)

```javascript
const rio = require("./sdk/javascript/js-sdk");
```

### Verify a receipt

```javascript
const rio = require("./sdk/javascript/js-sdk");

const result = rio.verifyReceipt(
  "examples/example_receipt_v2.json",
  "examples/example_ledger.json",
  { serviceToken: process.env.RIO_SERVICE_TOKEN }
);

console.log(result.overall);         // "PASS"
console.log(result.checks_passed);   // 4
console.log(result.checks_failed);   // 0

for (const check of result.checks) {
  console.log(check.check_name, "→", check.passed ? "PASS" : "FAIL");
  console.log(" ", check.detail);
}
```

### Verify a ledger only

```javascript
const result = rio.verifyLedger("examples/example_ledger.json");
console.log(result.overall);   // "PASS"
```

### Run conformance tests

```javascript
const result = rio.runConformanceTests();

console.log(result.overall);   // "PASS"
console.log(result.passed);    // 7
console.log(result.total);     // 7

for (const r of result.results) {
  console.log(r.id.padEnd(8), r.name.padEnd(40), r.passed ? "PASS" : "FAIL");
}
```

### Using pre-loaded objects

```javascript
const fs = require("fs");
const receipt = JSON.parse(fs.readFileSync("receipt.json", "utf8"));
const ledger  = JSON.parse(fs.readFileSync("ledger.json",  "utf8"));
const result  = rio.verifyReceipt(receipt, ledger, { serviceToken: "your-token" });
```

---

## Running the examples

```bash
# Python examples
cd sdk
python examples/python_verify_example.py
python examples/python_conformance_example.py

# JavaScript example
node examples/js_verify_example.js
```

---

## Return value reference

### `verify_receipt` / `verify_ledger`

```
{
  "overall":       "PASS" | "FAIL",
  "checks_passed": int,
  "checks_failed": int,
  "checks": [
    {
      "check_name": str,
      "passed":     bool,
      "detail":     str,
      "stored":     str,    // (receipt check only)
      "computed":   str,    // (receipt check only)
      "chain_intact": bool, // (execution ledger check only)
      "rows_checked": int,
      "row_results": [{ "row_id": int, "passed": bool }]
    }
  ]
}
```

### `run_conformance_tests`

```
{
  "overall": "PASS" | "FAIL",
  "total":   int,
  "passed":  int,
  "failed":  int,
  "results": [
    {
      "id":          str,
      "name":        str,
      "description": str,
      "passed":      bool,
      "expected":    str,
      "computed":    str,
      "error":       str | null
    }
  ]
}
```

### `get_compliance_level`

```
{
  "level":  0 | 1 | 2 | 3,
  "label":  str,
  "detail": str,
  "checks": [
    { "level": int, "name": str, "passed": bool, "detail": str }
  ]
}
```

---

## Reference

- **Protocol Specification**: `spec/RIO_Protocol_Specification_v1.0.md`
- **Conformance Guide**: `docs/CONFORMANCE.md`
- **Quickstart**: `docs/QUICKSTART.md`
- **Test vectors**: Appendix C of the spec / `tests/conformance/run_conformance_tests.py`
