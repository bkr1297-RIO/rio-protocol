# Conformance Test Suite

Machine-readable conformance test suite for any implementation of the RIO protocol. Contains 57 test definitions, 8 protocol invariants, cryptographic constants, hash computation formulas, signing payload contracts, and ledger chain formulas.

## Conformance Levels

| Level | Name | Scope |
|-------|------|-------|
| 1 | Receipt Format | Static hash, signature, and field checks — no pipeline required |
| 2 | Pipeline | Governance pipeline, gate enforcement, ledger chain |
| 3 | Full Protocol | Adapter layer, AI routing, multi-tool governance |

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
