# RIO Protocol — Conformance Definition

**Version:** 1.0
**Status:** Normative

---

## What "RIO Compliant" Means

A system is **RIO Compliant** when it produces cryptographic receipts and maintains an audit ledger that can be independently verified by any third party using only the public key and the RIO Independent Verifier. Compliance is not self-declared; it is demonstrated by passing the conformance test vectors published in this repository.

RIO compliance is defined at three levels. Each level builds on the previous one. An implementation must satisfy all requirements of a given level before claiming that level of compliance.

---

## Level 1 — Receipt Format Compliance

Level 1 establishes that an implementation produces receipts in the correct format with valid cryptographic properties. This is the minimum bar for interoperability.

**Requirements:**

An implementation claiming Level 1 compliance must produce receipts that pass all 7 checks of the RIO Independent Verifier:

| Check | Name | Requirement |
|-------|------|-------------|
| 1 | `required_fields` | All 22 required fields are present with correct types |
| 2 | `request_hash` | `request_hash` equals SHA-256 of the canonical JSON of `request_canonical_payload` |
| 3 | `receipt_hash` | `receipt_hash` equals SHA-256 of the canonical JSON of the 19 signed fields |
| 4 | `signature` | Ed25519 signature over the canonical JSON of the 19 signed fields is valid |
| 5 | `public_key_fingerprint` | `public_key_fingerprint` equals SHA-256 of the raw 32-byte Ed25519 public key |
| 6 | `decision_valid` | `decision` is one of: `allow`, `modify`, `block`, `escalate` |
| 7 | `ledger_link` | `prev_ledger_hash` is a well-formed 64-character hex digest |

**How to test:** Run the verifier against every receipt your system produces. All 7 checks must pass.

```bash
python -m verification.cli verify-receipt your_receipt.json --public-key your_key.pem
```

**Pass criteria:** Exit code 0, all checks report `PASS`.

---

## Level 2 — Ledger and Verification Compliance

Level 2 establishes that an implementation maintains a tamper-evident hash-chain ledger and that the ledger can be independently verified. Level 2 requires Level 1.

**Requirements (in addition to Level 1):**

An implementation claiming Level 2 compliance must produce a ledger that passes all 4 checks of the RIO Independent Verifier:

| Check | Name | Requirement |
|-------|------|-------------|
| 1 | `entry_hash` | For every entry, `current_ledger_hash` equals SHA-256 of (`prev_ledger_hash` + `receipt_hash`) concatenated as UTF-8 strings |
| 2 | `genesis_link` | The first entry's `prev_ledger_hash` equals `SHA-256(b'GENESIS')` = `901131d8...1416a` |
| 3 | `chain_link` | Each entry's `prev_ledger_hash` equals the previous entry's `current_ledger_hash` |
| 4 | `full_chain` | The entire chain is intact — no gaps, no reordering, no deletions |

**Additional Level 2 requirements:**

Every receipt produced by the system must have a corresponding ledger entry. The `receipt_hash` in the ledger entry must match the `receipt_hash` in the receipt. There must be no orphaned receipts (receipts without ledger entries) and no orphaned ledger entries (entries without corresponding receipts).

**How to test:** Run the verifier against your ledger file. All checks must pass.

```bash
python -m verification.cli verify-ledger your_ledger.json
```

**Full verification (receipt + ledger together):**

```bash
python -m verification.cli verify-all your_receipt.json your_ledger.json --public-key your_key.pem
```

**Pass criteria:** Exit code 0, all receipt checks and all ledger checks report `PASS`.

---

## Level 3 — Full Pipeline Compliance

Level 3 establishes that an implementation follows the complete RIO governance pipeline, including policy evaluation, approval routing, execution gating, and post-execution verification. Level 3 requires Level 2.

**Requirements (in addition to Level 2):**

An implementation claiming Level 3 compliance must enforce the following protocol invariants:

| Invariant | ID | Requirement |
|-----------|----|-------------|
| Human authority preserved | INV-01 | A human can override, halt, or reverse any AI-initiated action at any point in the pipeline |
| Every action is logged | INV-02 | Every action (approved, denied, or failed) produces a signed receipt and a ledger entry |
| Policy compliance | INV-03 | No action executes without passing the policy engine evaluation |
| Scope integrity | INV-04 | The executed action matches the original user intent — no scope creep |
| Tool permission check | INV-05 | The system verifies that the requested tool/action is within the agent's permitted scope |
| Fail-closed execution | INV-06 | If any gate fails, the system denies the action and produces a denial receipt |
| Denial receipts | INV-07 | Denied actions produce full receipts with `decision=block` and `execution_status=BLOCKED` |
| Ledger immutability | INV-08 | Once a ledger entry is written, it cannot be modified or deleted |

**Additional Level 3 requirements:**

The implementation must include a kill switch mechanism that can halt all AI execution within a bounded time. The implementation must enforce approval timeouts — if human approval is required and not received within the configured window, the action is denied. The implementation must separate the learning/adaptation loop from the execution path — model updates cannot bypass the governance pipeline.

**How to test:** Level 3 compliance requires running the full conformance test suite:

```bash
python -m pytest tests/ -v
```

Additionally, the implementation must demonstrate:

1. A denied action produces a valid receipt with `decision=block`
2. A tampered ledger is detected by the verifier (exit code 1)
3. The kill switch halts execution when triggered
4. An expired approval results in denial

---

## Conformance Test Vectors

The following test vectors are provided in `tests/conformance/` for external implementers to validate their implementations:

| File | Purpose | Expected Verifier Result |
|------|---------|--------------------------|
| `valid_receipt.json` | A correctly formed, signed receipt | All 7 checks PASS |
| `valid_ledger.json` | A correctly formed hash-chain ledger | All 4 checks PASS |
| `tampered_receipt.json` | Receipt with corrupted signature | Check 4 (signature) FAIL |
| `tampered_ledger.json` | Ledger with modified entry hash | Check 1 (entry_hash) FAIL |
| `missing_fields_receipt.json` | Receipt with required fields removed | Check 1 (required_fields) FAIL |
| `invalid_signature_receipt.json` | Receipt with invalid signature bytes | Check 4 (signature) FAIL |

The public key for all test vectors is located at `tests/vectors/public_key.pem`.

---

## Claiming Compliance

To claim RIO compliance at any level, an implementation must:

1. Pass all verification checks for that level using the RIO Independent Verifier
2. Pass all applicable conformance test vectors
3. Document the compliance level claimed and the test results

There is no self-certification. Compliance is binary: either the verifier reports PASS on all checks, or the implementation is not compliant at that level.

---

## Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Canonical Protocol Specification | `spec/RIO_Protocol_Specification_v1.0.json` | Defines the protocol standard |
| Independent Verifier Specification | `spec/Independent_Verifier_Spec.json` | Defines verification checks |
| Independent Verifier Implementation | `verification/` | Reference verifier package |
| Conformance Test Suite | `tests/conformance/rio_conformance_suite_v1.json` | Machine-readable test definitions |
| Test Vectors | `tests/vectors/` | Cryptographic test data |
| Quickstart Guide | `docs/QUICKSTART.md` | Clone-to-verify walkthrough |
