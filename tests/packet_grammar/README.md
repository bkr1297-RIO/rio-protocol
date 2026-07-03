# Packet Grammar Tests

Candidate packet-grammar tests for the ONE / RIO / MUSS orientation layer.

## Validators

- `tests/packet_grammar/validate_scribe_compiler_capsule.py`
- `tests/packet_grammar/validate_four_bit_crossing_code.py`
- `tests/packet_grammar/validate_four_bit_crossing_harness_negatives.py`
- `tests/packet_grammar/validate_gate_evidence.py`
- `tests/packet_grammar/validate_receipt_binding.py`

## Related Specs and Fixtures

- `spec/scribe_compiler_capsule.schema.json`
- `spec/four_bit_crossing_code.md`
- `spec/gate_evidence_v0.1.md`
- `spec/receipt_binding_v0.1.md`
- `tests/packet_grammar/scribe_compiler_capsule_fixtures_v0.1.json`
- `tests/packet_grammar/four_bit_crossing_code_truth_table_v0.1.csv`
- `tests/packet_grammar/four_bit_crossing_code_harness_negatives_v0.1.json`
- `tests/packet_grammar/gate_evidence_fixtures_v0.1.json`
- `tests/packet_grammar/receipt_binding_fixtures_v0.1.json`

---

## Run

Canonical verification command from the repository root:

```bash
bash scripts/rio_verify.sh
```

The older Replit wrapper remains available and delegates to the canonical runner:

```bash
bash scripts/replit_run_packet_grammar_checks.sh
```

Expected output includes:

```text
Scribe-Compiler Capsule fixture validation passed: 2 fixtures
Four-Bit Crossing Code validation passed: 16 truth-table rows
Four-Bit Crossing Code harness-negative validation passed: 5 malformed datasets rejected
Gate Evidence validation passed: 4 fixtures
Receipt Binding validation passed: 5 fixtures
RIO verification complete
Exit code: 0
```

---

## What This Tests

- Capsule structure and consentability posture.
- Four-Bit Crossing truth-table behavior.
- Harness rejection of malformed truth tables.
- Gate Evidence: no true bit without evidence.
- Receipt Binding: no verification receipt without commit, command, output, artifacts, and boundary claims.

---

## Boundary

These checks are candidate, docs/test-facing, and non-runtime-enforcing.

They do not claim live conformance, production enforcement, receipt verification, deployment, production readiness, or certification.

Keeper:

Generate freely. Cross only by law. Return with proof.
