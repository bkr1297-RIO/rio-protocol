#!/usr/bin/env python3
"""Validate Receipt Binding v0.1 fixtures.

Receipt Binding checks whether a verification receipt binds the claim to a commit,
command, runtime surface, observed output, verified artifacts, and explicit boundary.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "packet_grammar" / "receipt_binding_fixtures_v0.1.json"
SHA_RE = re.compile(r"^[a-f0-9]{40}$")

BOUNDARY_FALSE_FIELDS = (
    "live_conformance",
    "production_enforcement",
    "receipt_protocol_verification",
    "deployment",
    "production_readiness",
    "certification",
)


def nonempty_string(value: object) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def validate_receipt(receipt: dict) -> list[str]:
    failures: list[str] = []

    if not nonempty_string(receipt.get("receipt_id")):
        failures.append("receipt_id is required")
    if not nonempty_string(receipt.get("receipt_path")):
        failures.append("receipt_path is required")

    verified_commit = receipt.get("verified_commit")
    if not nonempty_string(verified_commit):
        failures.append("verified_commit is required")
    elif not SHA_RE.match(verified_commit):
        failures.append("verified_commit must be a full 40-character lowercase hex SHA")

    short_sha = receipt.get("short_sha")
    if not nonempty_string(short_sha):
        failures.append("short_sha is required")
    elif nonempty_string(verified_commit) and not str(verified_commit).startswith(str(short_sha)):
        failures.append("short_sha must prefix verified_commit")

    if not nonempty_string(receipt.get("runtime_surface")):
        failures.append("runtime_surface is required")
    if not nonempty_string(receipt.get("command")):
        failures.append("command is required")
    if receipt.get("exit_code") != 0:
        failures.append("exit_code must be 0 for a passing verification receipt")

    artifacts = receipt.get("artifacts_verified")
    if not isinstance(artifacts, list) or len(artifacts) == 0:
        failures.append("artifacts_verified is required")
    elif any(not nonempty_string(item) for item in artifacts):
        failures.append("artifacts_verified entries must be nonempty strings")

    outputs = receipt.get("observed_outputs")
    if not isinstance(outputs, list) or len(outputs) == 0:
        failures.append("observed_outputs is required")
    elif any(not nonempty_string(item) for item in outputs):
        failures.append("observed_outputs entries must be nonempty strings")

    boundary_claims = receipt.get("boundary_claims")
    if not isinstance(boundary_claims, dict):
        failures.append("boundary_claims is required")
    else:
        for field in BOUNDARY_FALSE_FIELDS:
            if field not in boundary_claims:
                failures.append(f"boundary claim {field} is required")
            elif boundary_claims[field] is not False:
                failures.append(f"boundary claim {field} must be false")

    return failures


def main() -> int:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []

    for fixture in data["fixtures"]:
        fixture_id = fixture["id"]
        receipt_failures = validate_receipt(fixture["receipt"])
        actual_valid = len(receipt_failures) == 0
        expected_valid = fixture["expected_valid"]

        if actual_valid != expected_valid:
            failures.append(f"{fixture_id}: valid={actual_valid} expected={expected_valid}; failures={receipt_failures}")
            continue

        expected_failure = fixture.get("expected_failure_contains")
        if expected_failure:
            joined = "\n".join(receipt_failures)
            if expected_failure not in joined:
                failures.append(f"{fixture_id}: expected failure containing {expected_failure!r}, got {joined!r}")

    if failures:
        print("Receipt Binding validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Receipt Binding validation passed: {len(data['fixtures'])} fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
