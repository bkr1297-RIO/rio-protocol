# Conformance Test Suite

Machine-readable conformance test suite for any implementation of the RIO protocol. Contains 57 test definitions, 8 protocol invariants, cryptographic constants, hash computation formulas, signing payload contracts, and ledger chain formulas.

## Conformance Levels

The authoritative conformance specification is [spec/RIO_CONFORMANCE_v2.3.0.md](../../spec/RIO_CONFORMANCE_v2.3.0.md), which defines 7 levels:

| Level | Name | Scope |
|-------|------|-------|
| 1 | Receipt Generation | All required fields present, correct types |
| 2 | Receipt + Verification | Level 1 + independently verifiable hashes |
| 3 | Receipt + Ledger | Level 2 + append-only hash-chained ledger |
| 4 | Receipt + Ledger + Verification | Level 3 + chain integrity independently verifiable |
| 5 | Full Proof Pipeline | Level 4 + 3-hash proof chain (result, previous_receipt, receipt) |
| 6 | Governed Receipts | Level 5 + 5-hash chain (adds request_hash, intent_hash) |
| 7 | Signed Receipts | Level 6 + Ed25519 signatures |

The test vectors in this suite cover Levels 1–3. Higher levels require a running governance pipeline and are validated at the system level.

## Files

| File | Description |
|------|-------------|
| `rio_conformance_suite_v1.json` | Master conformance suite — all 57 test cases, invariants, constants, formulas, worked examples, reference receipt, and reference ledger chain in a single machine-readable document |
| `TEST_MATRIX.md` | Human-readable matrix mapping each test case to its level, expected decision, invariants, and required vectors |

## Test Vector Files

All test vectors are in `../vectors/`. See [tests/vectors/README.md](../vectors/README.md) for the full index.

## Interoperability Bar

An implementation claims RIO Receipt Interoperability when it satisfies all four conditions:

1. Reproduces all hashes in `hash_computation_examples.json` from the same inputs
2. Verifies all 3 signatures in `signing_payload_examples.json` with `public_key.pem`
3. All invalid vectors return FAIL; all valid vectors return PASS
4. Walks `ledger_chain_valid.json`: all entries have `chain_intact=True`

## Protocol Invariants

| ID | Invariant |
|----|-----------|
| INV-01 | Human Authority Preserved — no autonomous execution without explicit human authorization |
| INV-02 | All Decisions Logged — every governance decision produces a verifiable audit record |
| INV-03 | Policy Compliance — requests must not violate declared coherence/somatic thresholds |
| INV-04 | Scope Integrity — response scope must match stated intent; no unexpanded execution |
| INV-05 | Tool Permission Enforcement — any tool usage must be within declared agent permissions |
| INV-06 | Cryptographic Integrity — receipts must be signed; signatures must be verifiable |
| INV-07 | Ledger Append-Only — the governance ledger must form a valid hash chain from genesis |
| INV-08 | Fail-Closed Default — when evaluation fails or is ambiguous, the system must deny |
