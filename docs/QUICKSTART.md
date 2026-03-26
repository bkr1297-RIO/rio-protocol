# RIO Protocol — Quickstart Guide

**Go from clone to verified receipt in 10 minutes.**

---

## What Is RIO?

RIO (Runtime Intelligence Orchestration) is an open protocol that governs AI agent execution through cryptographic accountability. Every action an AI agent takes — whether approved, modified, or denied — passes through a governance pipeline that evaluates intent, enforces policy, gates execution, and produces a signed receipt. These receipts are chained into a tamper-evident ledger that any third party can independently verify. RIO ensures that AI systems operate under human authority, that every decision is auditable, and that no action can execute without passing through the governance pipeline. The protocol is designed so that compliance is not self-declared but cryptographically provable.

---

## Prerequisites

| Requirement | Details |
|-------------|---------|
| Python | 3.9 or later |
| pip | For installing the `cryptography` package |
| Git | For cloning the repository |

No API keys, accounts, or external services are required.

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/bkr1297-RIO/rio-protocol.git
cd rio-protocol
```

---

## Step 2: Install the Verifier Dependency

The independent verifier has a single dependency:

```bash
pip install cryptography>=41.0.0
```

---

## Step 3: Locate the Example Files

The repository includes real, cryptographically valid example files in `examples/quickstart/`:

| File | What It Is |
|------|------------|
| `example_intent.json` | The original intent submitted to the governance pipeline |
| `example_receipt_v2.json` | The signed receipt produced after governance evaluation |
| `example_ledger.json` | The hash-chain ledger entry linking this receipt to the chain |
| `example_verification_result.json` | The expected output when the verifier confirms the receipt |

The public key used to sign these examples is at `tests/vectors/public_key.pem`.

---

## Step 4: Verify the Example Receipt

Run the independent verifier against the example receipt:

```bash
python -m verification.cli verify-receipt \
  examples/quickstart/example_receipt_v2.json \
  --public-key tests/vectors/public_key.pem
```

**Expected output (PASS):**

```
RIO Receipt Verification
========================
Receipt: a1b2c3d4-0001-0001-0001-aabbccddeeff

Check 1 [required_fields]       PASS
Check 2 [request_hash]          PASS
Check 3 [receipt_hash]          PASS
Check 4 [signature]             PASS
Check 5 [public_key_fingerprint] PASS
Check 6 [decision_valid]        PASS
Check 7 [ledger_link]           PASS

Result: ALL CHECKS PASSED
```

The exit code is `0`, meaning the receipt is valid.

---

## Step 5: Verify the Example Ledger

Run the verifier against the example ledger:

```bash
python -m verification.cli verify-ledger \
  examples/quickstart/example_ledger.json
```

**Expected output (PASS):**

```
RIO Ledger Verification
=======================
Entries: 1

Entry 0  PASS  (genesis → ...)

Chain intact: YES
Entries verified: 1/1
```

---

## Step 6: Verify Both Together

Run the full verification (receipt + ledger) in one command:

```bash
python -m verification.cli verify-all \
  examples/quickstart/example_receipt_v2.json \
  examples/quickstart/example_ledger.json \
  --public-key tests/vectors/public_key.pem
```

Both the receipt and ledger checks must pass. Exit code `0` means everything is valid.

---

## What a FAIL Looks Like

If a receipt has been tampered with, the verifier will report which check failed:

```bash
python -m verification.cli verify-receipt \
  tests/vectors/receipt_invalid_signature.json \
  --public-key tests/vectors/public_key.pem
```

**Expected output (FAIL):**

```
Check 4 [signature]             FAIL  Ed25519 signature verification failed

Result: VERIFICATION FAILED (1 of 7 checks failed)
```

The exit code is `1`, meaning the receipt is invalid. A FAIL on any check means the receipt cannot be trusted. The `details` field explains what specifically failed.

---

## JSON Output Mode

For programmatic use, add the `--json` flag to get structured JSON output:

```bash
python -m verification.cli --json verify-receipt \
  examples/quickstart/example_receipt_v2.json \
  --public-key tests/vectors/public_key.pem
```

Compare the output against `examples/quickstart/example_verification_result.json` to confirm your verifier produces the same results.

---

## What to Read Next

| Document | Location | Purpose |
|----------|----------|---------|
| Conformance Definition | `docs/CONFORMANCE.md` | Understand what Level 1, 2, and 3 compliance mean |
| Canonical Protocol Specification | `spec/RIO_Protocol_Specification_v1.0.json` | Full protocol standard |
| Independent Verifier Spec | `spec/Independent_Verifier_Spec.json` | How verification works |
| Conformance Test Vectors | `tests/conformance/` | Test your own implementation |
| Implementation Guide | `docs/adoption/IMPLEMENTATION_GUIDE.md` | Step-by-step adoption for organizations |

---

## Exit Codes Reference

| Code | Meaning |
|------|---------|
| `0` | All checks passed — the receipt/ledger is valid |
| `1` | One or more checks failed — the receipt/ledger cannot be trusted |
| `2` | Input error — file not found, invalid JSON, or missing arguments |
