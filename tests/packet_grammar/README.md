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
```

Expected output:

```text
Scribe-Compiler Capsule fixture validation passed: 2 fixtures
Four-Bit Crossing Code validation passed: 16 truth-table rows
Four-Bit Crossing Code harness-negative validation passed: 5 malformed datasets rejected
```

---

## What This Tests

The capsule validator checks:

1. required capsule fields,
2. UUID shape,
3. timestamp shape,
4. SHA-256 hash shape,
5. enum constraints,
6. Four-Bit Crossing Code coherence,
7. bit evidence presence for true bits,
8. consentability posture for allowed crossings,
9. basic tense/status overclaim protection,
10. register-boundary protection.

The Four-Bit Crossing Code validator checks:

1. all 16 boolean combinations are present exactly once,
2. Authority failure denies crossing,
3. Return failure denies crossing,
4. Scope failure requires review,
5. Consequence failure clarifies the packet,
6. only all-four-true produces `allow` and `may_cross=true`.

The harness-negative validator checks that malformed datasets fail when they contain:

1. a duplicate row,
2. a missing row,
3. an invalid bit value,
4. an incorrect verdict,
5. an extra row.

---

## Boundary

These validators are intentionally dependency-free. They are not full JSON Schema implementations.

Their purpose is to make the first portable constitutional grammar artifacts runnable immediately after clone.

Keeper:

Generate freely. Cross only by law. Return with proof.
