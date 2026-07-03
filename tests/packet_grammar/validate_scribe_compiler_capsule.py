#!/usr/bin/env python3
"""Validate Scribe-Compiler Capsule fixtures.

This is a lightweight, dependency-free fixture validator. It does not replace a full
JSON Schema validator. It checks the required fields, key enum constraints, hash
shape, and crossing-code coherence for the candidate capsule grammar.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from uuid import UUID
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "tests" / "packet_grammar" / "scribe_compiler_capsule_fixtures_v0.1.json"
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")

REQUIRED_TOP = {
    "capsule_version",
    "capsule_id",
    "created_at",
    "sourcepoint",
    "intent",
    "scope",
    "authority_envelope",
    "crossing_code",
    "return_requirements",
    "register_boundary",
    "tense_label",
    "status_label",
}

AUTHORITY_STATES = {"present", "absent", "delegated", "unknown"}
AUTHORIZATION_STATES = {"not_authorized", "authorized", "requires_review", "revoked"}
VERDICTS = {"allow", "deny", "require_review", "clarify"}
TENSE_LABELS = {"designed", "built", "verified", "deployed", "certified"}
STATUS_LABELS = {"candidate", "draft", "ratified", "deprecated"}


def parse_dt(value: str) -> None:
    if not isinstance(value, str):
        raise AssertionError("datetime value must be a string")
    datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_capsule_shape(capsule: dict) -> None:
    missing = REQUIRED_TOP - set(capsule)
    if missing:
        raise AssertionError(f"missing top-level fields: {sorted(missing)}")

    if not re.match(r"^0\.[0-9]+\.[0-9]+$", capsule["capsule_version"]):
        raise AssertionError("capsule_version must be candidate v0.x.y")

    UUID(capsule["capsule_id"])
    parse_dt(capsule["created_at"])

    sourcepoint = capsule["sourcepoint"]
    if sourcepoint["authority_state"] not in AUTHORITY_STATES:
        raise AssertionError("invalid sourcepoint.authority_state")
    if not sourcepoint.get("authority_id"):
        raise AssertionError("sourcepoint.authority_id is required")

    intent = capsule["intent"]
    if not intent.get("summary"):
        raise AssertionError("intent.summary is required")
    if not SHA256_RE.match(intent["original_signal_hash"]):
        raise AssertionError("intent.original_signal_hash must be sha256 hex")

    scope = capsule["scope"]
    if not isinstance(scope["external_side_effects"], bool):
        raise AssertionError("scope.external_side_effects must be boolean")
    for field in ("allowed_domains", "prohibited_domains", "tools_requested"):
        if not isinstance(scope[field], list):
            raise AssertionError(f"scope.{field} must be a list")

    envelope = capsule["authority_envelope"]
    if envelope["authorization_state"] not in AUTHORIZATION_STATES:
        raise AssertionError("invalid authority_envelope.authorization_state")
    for field in ("authorized_at", "expires_at"):
        value = envelope.get(field)
        if value is not None:
            parse_dt(value)
    if not isinstance(envelope["constraints"], list):
        raise AssertionError("authority_envelope.constraints must be a list")

    crossing = capsule["crossing_code"]
    for bit in ("authority", "scope", "consequence", "return"):
        if not isinstance(crossing[bit], bool):
            raise AssertionError(f"crossing_code.{bit} must be boolean")
    if crossing["verdict"] not in VERDICTS:
        raise AssertionError("invalid crossing_code.verdict")

    returns = capsule["return_requirements"]
    if not isinstance(returns["receipt_required"], bool):
        raise AssertionError("return_requirements.receipt_required must be boolean")
    if not isinstance(returns["settlement_required"], bool):
        raise AssertionError("return_requirements.settlement_required must be boolean")
    if not isinstance(returns["evidence_required"], list):
        raise AssertionError("return_requirements.evidence_required must be a list")

    boundary = capsule["register_boundary"]
    for field in ("private_material_included", "public_claim_allowed", "proof_required"):
        if not isinstance(boundary[field], bool):
            raise AssertionError(f"register_boundary.{field} must be boolean")

    if capsule["tense_label"] not in TENSE_LABELS:
        raise AssertionError("invalid tense_label")
    if capsule["status_label"] not in STATUS_LABELS:
        raise AssertionError("invalid status_label")


def expected_verdict(capsule: dict) -> str:
    crossing = capsule["crossing_code"]
    all_bits = all(crossing[bit] for bit in ("authority", "scope", "consequence", "return"))
    if all_bits:
        return "allow"
    if not crossing["authority"] or not crossing["return"]:
        return "deny"
    return "require_review"


def validate_crossing_coherence(capsule: dict) -> None:
    crossing = capsule["crossing_code"]
    expected = expected_verdict(capsule)
    if crossing["verdict"] != expected:
        raise AssertionError(f"crossing verdict {crossing['verdict']} != expected {expected}")

    if capsule["tense_label"] == "certified" and capsule["status_label"] == "candidate":
        if crossing["verdict"] != "require_review":
            raise AssertionError("candidate material cannot claim certified without review")

    if capsule["register_boundary"].get("private_material_included"):
        if capsule["register_boundary"].get("public_claim_allowed"):
            raise AssertionError("private material cannot be public-claim allowed by default")


def main() -> int:
    data = json.loads(FIXTURES.read_text(encoding="utf-8"))
    failures: list[str] = []

    for fixture in data["fixtures"]:
        fixture_id = fixture["id"]
        capsule = fixture["capsule"]
        try:
            validate_capsule_shape(capsule)
            validate_crossing_coherence(capsule)
            actual_valid = True
        except Exception as exc:  # noqa: BLE001 - validation harness reports all failures
            actual_valid = False
            failures.append(f"{fixture_id}: {exc}")

        expected_valid = fixture["expected_schema_valid"]
        expected_crossing = fixture["expected_crossing_verdict"]
        actual_crossing = capsule.get("crossing_code", {}).get("verdict")

        if actual_valid != expected_valid:
            failures.append(f"{fixture_id}: schema_valid {actual_valid} != expected {expected_valid}")
        if actual_crossing != expected_crossing:
            failures.append(f"{fixture_id}: verdict {actual_crossing} != expected {expected_crossing}")

    if failures:
        print("Scribe-Compiler Capsule fixture validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Scribe-Compiler Capsule fixture validation passed: {len(data['fixtures'])} fixtures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
