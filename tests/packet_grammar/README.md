# Packet Grammar Tests

This folder contains candidate packet-grammar tests for the ONE / RIO / MUSS orientation layer.

The first packet grammar is the Scribe-Compiler Capsule:

- Schema: `spec/scribe_compiler_capsule.schema.json`
- Fixtures: `tests/packet_grammar/scribe_compiler_capsule_fixtures_v0.1.json`
- Validator: `tests/packet_grammar/validate_scribe_compiler_capsule.py`

---

## Status

These tests are candidate, docs/test-facing, and non-runtime-enforcing.

They do not claim live conformance, production enforcement, receipt verification, or certification.

---

## Run

From the repository root:

```bash
python3 tests/packet_grammar/validate_scribe_compiler_capsule.py
```

Expected output:

```text
Scribe-Compiler Capsule fixture validation passed: 5 fixtures
```

---

## What This Tests

The validator checks:

1. required capsule fields,
2. UUID shape,
3. timestamp shape,
4. SHA-256 hash shape,
5. enum constraints,
6. Four-Bit Crossing Code coherence,
7. basic tense/status overclaim protection,
8. register-boundary protection.

---

## Boundary

This validator is intentionally dependency-free. It is not a full JSON Schema implementation.

Its purpose is to make the first portable constitutional grammar artifact runnable immediately after clone.

Keeper:

Generate freely. Cross only by law. Return with proof.
