# Portable Constitutional Engine – Gate Simulator v0.1

**Status:** candidate reference implementation / developer preview / non-production.

This is a localized reference implementation of the RIO Membrane Gate. It demonstrates how an intent packet can be evaluated against the Four-Bit Crossing Code:

```
Authority AND Scope AND Consequence AND Return
```

It lives inside `bkr1297-RIO/rio-protocol` (not as a separate repository) so the proof trail stays unified with the rest of the packet grammar and receipt-binding work in this repo.

## 1. Overview

This package shows, in small deterministic runnable form, that no consequence-bearing packet crosses this candidate gate unless Authority, Scope, Consequence, and Return are all satisfied. It is local, standard-library-only Python with no network calls, no live tool calls, and no live adapter calls.

## 2. Project structure

```
reference/portable_constitutional_engine/
├── README.md
├── setup.sh
├── schema/
│   └── capsule_schema.json
├── core/
│   ├── gate_simulator.py
│   ├── capsule_cli.py
│   └── capsule_factory.py
├── tests/
│   └── test_harness_capsule.py
└── examples/
    └── sample_capsule.json
```

## 3. Core concepts

- **Capsule** — a small JSON record describing one intended action (who, what, scope, consequence class, and where the receipt goes).
- **Gate Simulator** — a deterministic function that evaluates a capsule against the Four-Bit Crossing Code and returns a verdict plus reasons.
- **Receipt** — a JSON record describing the verdict for a capsule; produced locally, not cryptographically signed.

## 4. Capsule definition

A candidate Capsule (see `schema/capsule_schema.json`) has these fields:

- `capsule_id` — unique candidate identifier
- `sourcepoint_id` — who/what originated the intent
- `intent` — plain-language description of the requested action
- `scope` — candidate scope label (e.g. `draft`, `read`, `send`, `delete`)
- `consequence_class` — one of `none`, `low`, `medium`, `high`, `critical`
- `return_path` — where the receipt goes, expected in the form `receipt://...`
- `authority_envelope_ref` — reference to the backing authority envelope (presence/flag check only in this reference implementation, not cryptographic verification)
- `timestamp` — UTC creation time
- `metadata` — free-form candidate metadata (register, model_office, coherence_warning, etc.)

## 5. Four-Bit Crossing Code

The Gate Simulator checks four bits before a capsule may cross:

1. **Authority** — is `authority_envelope_ref` present and not flagged revoked/expired?
2. **Scope** — is `scope` a recognized candidate scope?
3. **Consequence** — how consequential is the declared `consequence_class`, and does the scope itself carry consequence regardless of the declared class?
4. **Return** — is there a valid `receipt://` return path for the receipt?

A capsule only receives `PASS` if all four bits are satisfied and the consequence class does not independently require a hold.

## 6. Gate Simulator verdicts

- `PASS` — all four bits satisfied; capsule crosses.
- `DENY` — Authority, Scope, or Return bit failed outright.
- `HOLD` — capsule is structurally fine but held for review (medium consequence, or a consequence-bearing scope with an optimistic low/none consequence_class).
- `REST_STATE_HOLD` — high consequence class; requires an explicit human checkpoint before proceeding.
- `HARD_BLOCK` — capsule is missing required fields, uses an unrecognized `consequence_class`, or declares a critical consequence class, which this candidate gate never auto-crosses.

## 7. How to run setup

```bash
cd reference/portable_constitutional_engine
bash setup.sh
```

This creates a local virtual environment if possible (standard library only, no extra dependencies), runs the negative fixture harness, and prints the next commands.

## 8. How to generate a sample capsule

```bash
python3 -c "from core.capsule_factory import make_capsule; import json; print(json.dumps(make_capsule('Draft a note to the team'), indent=2))"
```

`capsule_factory.py` builds a capsule from plain text using deterministic keyword heuristics only. It does not call an external LLM. Any hash used to derive a candidate ID is a deterministic receipt hash, not a cryptographic authority proof.

## 9. How to evaluate a capsule

```bash
python3 core/capsule_cli.py examples/sample_capsule.json
# or
cat examples/sample_capsule.json | python3 core/capsule_cli.py -
```

This prints a receipt-style JSON object with the verdict, reasons, and boundary note.

## 10. How to run the negative fixture harness

```bash
python3 tests/test_harness_capsule.py
```

Expected output on success:

```
16 / 16 negative fixtures held as expected
ALL CAPSULE NEGATIVE FIXTURES HELD AS EXPECTED
```

This harness proves that the included negative fixtures do not cross. It does not prove that all possible attacks are impossible.

## 11. Boundary / non-claims

This is a candidate reference implementation / developer preview / non-production package only. It does not claim, prove, or imply:

- production-readiness
- certification
- live conformance
- cryptographic signing (any hash used here is a deterministic receipt hash, not a cryptographic authority proof)
- production enforcement
- deployment
- that all possible attacks are impossible — only that the included negative fixtures do not cross

## 12. Keeper

Connection gives machines reach. Constitution gives machines lawful boundary. Return keeps the human real.
