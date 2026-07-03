#!/usr/bin/env python3
"""Validate Gate Evidence v0.1 fixtures.

Gate Evidence checks the input seam: a true bit must carry evidence, and an
allowed packet requiring explicit consent must show present consent.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "packet_grammar" / "gate_evidence_fixtures_v0.1.json"
BIT_FIELDS = ("authority", "scope", "consequence", "return")


def validate_packet(packet: dict) -> list[str]:
    failures: list[str] = []
    crossing = packet.get("crossing_code", {})
    evidence = packet.get("bit_evidence", {})
    consent = packet.get("consentability", {})

    for bit in BIT_FIELDS:
        if bit not in crossing:
            failures.append(f"missing crossing bit: {bit}")
            continue
        if not isinstance(crossing[bit], bool):
            failures.append(f"{bit} bit must be boolean")
            continue
        if bit not in evidence:
            failures.append(f"missing evidence field: {bit}")
            continue
        if not isinstance(evidence[bit], list):
            failures.append(f"bit_evidence.{bit} must be a list")
            continue
        if crossing[bit] is True and len(evidence[bit]) == 0:
            failures.append(f"{bit} true requires evidence")

    if crossing.get("verdict") == "allow":
        if not all(crossing.get(bit) is True for bit in BIT_FIELDS):
            failures.append("allow verdict requires all four bits true")
        if consent.get("explicit_consent_required") is True and consent.get("consent_state") != "present":
            failures.append("allow requires present consent")
        for required in ("stakes", "risks", "benefits", "time_bound", "revocable", "comprehension_basis"):
            if required not in consent:
                failures.append(f"consentability.{required} is required for allow")

    return failures


def main() -> int:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []

    for fixture in data["fixtures"]:
        fixture_id = fixture["id"]
        packet_failures = validate_packet(fixture["packet"])
        actual_valid = len(packet_failures) == 0
        expected_valid = fixture["expected_valid"]

        if actual_valid != expected_valid:
            failures.append(f"{fixture_id}: valid={actual_valid} expected={expected_valid}; failures={packet_failures}")
            continue

        expected_failure = fixture.get("expected_failure_contains")
        if expected_failure:
            joined = "\n".join(packet_failures)
            if expected_failure not in joined:
                failures.append(f"{fixture_id}: expected failure containing {expected_failure!r}, got {joined!r}")

    if failures:
        print("Gate Evidence validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Gate Evidence validation passed: {len(data['fixtures'])} fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
