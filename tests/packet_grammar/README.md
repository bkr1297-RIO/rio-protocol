# Packet Grammar Tests

This folder contains candidate packet-grammar tests for the ONE / RIO / MUSS orientation layer.

The first packet grammar is the Scribe-Compiler Capsule:

- Schema: `spec/scribe_compiler_capsule.schema.json`
- Fixtures: `tests/packet_grammar/scribe_compiler_capsule_fixtures_v0.1.json`
- Validator: `tests/packet_grammar/validate_scribe_compiler_capsule.py`

The first gate dataset is the Four-Bit Crossing Code truth table:

- Spec: `spec/four_bit_crossing_code.md`
- Dataset: `tests/packet_grammar/four_bit_crossing_code_truth_table_v0.1.csv`
- Validator: `tests/packet_grammar/validate_four_bit_crossing_code.py`

The first harness-negative set tests whether the truth-table validator rejects malformed datasets:

- Negative fixtures: `tests/packet_grammar/four_bit_crossing_code_harness_negatives_v0.1.json`
- Negative validator: `tests/packet_grammar/validate_four_bit_crossing_harness_negatives.py`

Gate Evidence v0.1 tests whether true gate bits carry evidence and whether allowed packets have present consent when consent is required:

- Spec: `spec/gate_evidence_v0.1.md`
- Fixtures: `tests/packet_grammar/gate_evidence_fixtures_v0.1.json`
- Validator: `tests/packet_grammar/validate_gate_evidence.py`

---

## Status

These tests are candidate, docs/test-facing, and non-runtime-enforcing.

They do not claim live conformance, production enforcement, receipt verification, or certification.

---

## Run

From the repository root:

```bash
python3 tests/packet_grammar/validate_scribe_compiler_capsule.py
python3 tests/packet_grammar/validate_four_bit_crossing_code.py
python3 tests/packet_grammar/validate_four_bit_crossing_harness_negatives.py
python3 tests/packet_grammar/validate_gate_evidence.py
```

Or run the Replit wrapper:

```bash
bash scripts/replit_run_packet_grammar_checks.sh
```

Expected output:

```text
Scribe-Compiler Capsule fixture validation passed: 2 fixtures
Four-Bit Crossing Code validation passed: 16 truth-table rows
Four-Bit Crossing Code harness-negative validation passed: 5 malformed datasets rejected
Gate Evidence validation passed: 4 fixtures
```

---

## What This Tests

The capsule validator checks required capsule structure, bit evidence presence, consentability posture, tense/status boundaries, and register-boundary protection.

The Four-Bit Crossing Code validator checks all 16 boolean combinations and verifies that only all-four-true produces `allow` and `may_cross=true`.

The harness-negative validator checks that malformed datasets fail when they contain a duplicate row, missing row, invalid bit value, incorrect verdict, or extra row.

The Gate Evidence validator checks:

1. no true bit is allowed without evidence,
2. an `allow` verdict requires all four bits true,
3. an `allow` verdict requires present consent when explicit consent is required,
4. consentability carries stakes, risks, benefits, time bound, revocability, and comprehension basis.

---

## Boundary

These validators are intentionally dependency-free. They are not full JSON Schema implementations.

Their purpose is to make the first portable constitutional grammar artifacts runnable immediately after clone.

Keeper:

Generate freely. Cross only by law. Return with proof.
