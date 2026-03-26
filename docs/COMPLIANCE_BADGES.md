# RIO Protocol -- Compliance Badges

**Version:** 1.0  
**Status:** Active

This document defines the three compliance levels for the RIO Protocol, what each level means, and how to test compliance using the provided tooling.

---

## Compliance Levels

The RIO Protocol defines three progressive compliance levels. Each level builds on the previous one, forming a trust ladder from basic receipt format compliance to full protocol enforcement.

| Level | Name | What It Proves |
|-------|------|----------------|
| **Level 1** | Receipt Format Compliance | The system produces cryptographically valid receipts with correct hashes and signatures. |
| **Level 2** | Governance Attested | Level 1 + the system maintains a tamper-evident ledger and passes independent verification. |
| **Level 3** | Full Protocol Compliance | Level 2 + the system enforces the full 8-stage governance pipeline with all protocol invariants. |

---

## Level 1 -- Receipt Format Compliance

**What it means:** The implementation generates receipts that conform to the RIO receipt schema and can be independently verified for structural and cryptographic correctness.

**Required checks (all must PASS):**

| Check | Description |
|-------|-------------|
| Required Fields | All 22 required fields are present in the receipt |
| Request Hash | SHA-256 hash of canonical JSON request payload matches `request_hash` field |
| Receipt Hash | SHA-256 hash of 19 signed fields matches `receipt_hash` field |
| Signature | Ed25519 signature over `receipt_hash` verifies against the public key |
| Public Key Fingerprint | SHA-256 fingerprint of the public key matches `public_key_fingerprint` field |
| Decision Valid | `governance_decision` is one of: `allow`, `modify`, `block`, `escalate` |
| Ledger Link | `prev_ledger_hash` field is present and non-empty |

**How to test:**

```bash
python tools/check_compliance.py \
  --receipt path/to/your/receipt.json \
  --key path/to/your/public_key.pem
```

---

## Level 2 -- Governance Attested

**What it means:** The implementation not only produces valid receipts but also maintains a hash-chained ledger that can be independently verified for integrity. This proves that governance decisions are recorded in a tamper-evident sequence.

**Required checks (all Level 1 checks + the following):**

| Check | Description |
|-------|-------------|
| Chain Integrity | Every ledger entry's `current_ledger_hash` equals `SHA256(prev_ledger_hash + receipt_hash)` |
| Genesis Link | The first entry's `prev_ledger_hash` equals `SHA256(b'GENESIS')` |
| Entry Continuity | Each entry's `prev_ledger_hash` equals the previous entry's `current_ledger_hash` |
| Independent Verification | All 7 receipt checks + all 4 ledger checks pass using the independent verifier |

**How to test:**

```bash
python tools/check_compliance.py \
  --receipt path/to/your/receipt.json \
  --key path/to/your/public_key.pem \
  --ledger path/to/your/ledger.json
```

Or auto-discover from test vectors:

```bash
python tools/check_compliance.py --auto
```

---

## Level 3 -- Full Protocol Compliance

**What it means:** The implementation enforces the complete RIO governance pipeline, including all 8 protocol invariants. This is the highest level of compliance and requires attestation that the full pipeline is operational.

**Required checks (all Level 2 checks + the following):**

| Invariant | Description |
|-----------|-------------|
| INV-01 | No action executes without a signed receipt |
| INV-02 | Every receipt is recorded in the ledger |
| INV-03 | The ledger hash chain is never broken |
| INV-04 | Policy evaluation is deterministic for identical inputs |
| INV-05 | Kill switch halts all execution within the timeout window |
| INV-06 | Denied actions never execute |
| INV-07 | Learning loop never modifies policy without human approval |
| INV-08 | All receipts are independently verifiable |

**How to test:**

Level 3 compliance cannot be fully automated. The `check_compliance.py` tool checks for the presence of `invariant_results` in the receipt, but full Level 3 certification requires:

1. Automated verification of Levels 1 and 2
2. Evidence that all 8 invariants are enforced in the implementation
3. Attestation from the implementation operator

```bash
python tools/check_compliance.py \
  --receipt path/to/your/receipt.json \
  --key path/to/your/public_key.pem \
  --ledger path/to/your/ledger.json
```

---

## Badge Usage

Implementations that pass compliance testing may reference their level in documentation:

- **Level 1:** "RIO Receipt Format Compliant"
- **Level 2:** "RIO Governance Attested"
- **Level 3:** "RIO Full Protocol Compliant"

Compliance is self-assessed using the provided tooling. The compliance level applies to a specific version of the implementation and must be re-validated after significant changes.

---

## Running the Full Conformance Suite

To run all 23 conformance tests across both levels:

```bash
python tests/run_conformance.py
```

Filter by level:

```bash
python tests/run_conformance.py --level 1    # Level 1 tests only (17 tests)
python tests/run_conformance.py --level 2    # Level 1 + Level 2 tests (23 tests)
```

JSON output for CI integration:

```bash
python tests/run_conformance.py --json
```

---

## Related Documents

- [CONFORMANCE.md](CONFORMANCE.md) -- Detailed conformance level definitions and check tables
- [CERTIFICATION_CRITERIA.md](adoption/CERTIFICATION_CRITERIA.md) -- Formal certification requirements
- [QUICKSTART.md](QUICKSTART.md) -- Getting started with verification
- [VERIFICATION_OUTPUT_EXAMPLE.md](VERIFICATION_OUTPUT_EXAMPLE.md) -- What PASS/FAIL output looks like
