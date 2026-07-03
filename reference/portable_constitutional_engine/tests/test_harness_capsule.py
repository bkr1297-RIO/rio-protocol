#!/usr/bin/env python3
"""
Portable Constitutional Engine - Negative Fixture Harness v0.1
Candidate reference implementation / developer preview / non-production.

This harness proves only that the negative fixtures listed below do not
cross (do not receive a PASS verdict) when evaluated by
core.gate_simulator.evaluate(). It does not prove that all possible
attacks are impossible, and it performs no live tool calls, live adapter
calls, or network requests.
"""
import sys
from pathlib import Path

CORE_DIR = Path(__file__).resolve().parents[1] / "core"
sys.path.insert(0, str(CORE_DIR))

from gate_simulator import evaluate, VERDICT_PASS  # noqa: E402


def _base_capsule():
    return {
        "capsule_id": "caps-negative-base",
        "sourcepoint_id": "sourcepoint-harness",
        "intent": "Draft a kind response to the client's email.",
        "scope": "draft",
        "consequence_class": "low",
        "return_path": "receipt://mus/ledger/harness",
        "authority_envelope_ref": "env-harness-valid",
        "timestamp": "2026-07-03T00:00:00Z",
        "metadata": {
            "register": "developer_preview",
            "model_office": "Scribe-Compiler",
            "coherence_warning": "",
        },
    }


def _without(field):
    capsule = _base_capsule()
    capsule.pop(field, None)
    return capsule


NEGATIVE_FIXTURES = [
    ("missing_capsule_id", _without("capsule_id"), "HARD_BLOCK"),
    ("missing_sourcepoint_id", _without("sourcepoint_id"), "HARD_BLOCK"),
    ("missing_timestamp", _without("timestamp"), "HARD_BLOCK"),
    ("missing_scope", _without("scope"), "HARD_BLOCK"),
    ("missing_return_path", _without("return_path"), "HARD_BLOCK"),
    ("missing_authority_envelope_ref", _without("authority_envelope_ref"), "HARD_BLOCK"),
    ("empty_authority_envelope_ref", {**_base_capsule(), "authority_envelope_ref": ""}, "HARD_BLOCK"),
    ("revoked_authority", {**_base_capsule(), "authority_envelope_ref": "env-revoked-2026"}, "DENY"),
    ("expired_authority", {**_base_capsule(), "authority_envelope_ref": "env-expired-2025"}, "DENY"),
    ("malformed_return_path", {**_base_capsule(), "return_path": "http://not-a-receipt"}, "DENY"),
    ("unknown_scope", {**_base_capsule(), "scope": "detonate"}, "DENY"),
    ("unrecognized_consequence_class", {**_base_capsule(), "consequence_class": "extreme"}, "HARD_BLOCK"),
    ("critical_consequence", {**_base_capsule(), "consequence_class": "critical", "scope": "delete"}, "HARD_BLOCK"),
    ("high_consequence", {**_base_capsule(), "consequence_class": "high", "scope": "transfer"}, "REST_STATE_HOLD"),
    ("medium_consequence", {**_base_capsule(), "consequence_class": "medium"}, "HOLD"),
    (
        "consequence_bearing_scope_declared_low",
        {**_base_capsule(), "scope": "send", "consequence_class": "low"},
        "HOLD",
    ),
]


def main():
    failures = []
    for name, capsule, expected_verdict in NEGATIVE_FIXTURES:
        result = evaluate(capsule)
        verdict = result["verdict"]
        if verdict == VERDICT_PASS:
            failures.append(
                (name, verdict, expected_verdict, "fixture crossed the gate (PASS) when it should have been held")
            )
        elif verdict != expected_verdict:
            failures.append((name, verdict, expected_verdict, "fixture was held but with an unexpected verdict"))

    total = len(NEGATIVE_FIXTURES)
    held = total - len(failures)

    print(f"{held} / {total} negative fixtures held as expected")

    if failures:
        print("")
        print("FAILURES:")
        for name, got, expected, note in failures:
            print(f"  - {name}: got {got}, expected {expected} ({note})")
        return 1

    print("ALL CAPSULE NEGATIVE FIXTURES HELD AS EXPECTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
