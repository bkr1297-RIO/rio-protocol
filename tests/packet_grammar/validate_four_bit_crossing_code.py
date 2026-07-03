#!/usr/bin/env python3
"""Validate the Four-Bit Crossing Code truth table.

The truth table is intentionally tiny and complete: all 16 combinations of
Authority, Scope, Consequence, and Return must be present exactly once.
"""

from __future__ import annotations

import csv
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRUTH_TABLE = ROOT / "tests" / "packet_grammar" / "four_bit_crossing_code_truth_table_v0.1.csv"

BIT_FIELDS = ("authority", "scope", "consequence", "return")
VALID_VERDICTS = {"allow", "deny", "require_review", "clarify"}


def parse_bool(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise AssertionError(f"invalid boolean value: {value!r}")


def expected_for_bits(authority: bool, scope: bool, consequence: bool, return_bit: bool) -> tuple[str, bool, str]:
    if not authority:
        return "deny", False, "authority_absent"
    if not return_bit:
        return "deny", False, "return_missing"
    if scope and consequence:
        return "allow", True, "all_crossing_bits_true"
    if not scope and not consequence:
        return "require_review", False, "scope_and_consequence_unresolved"
    if not scope:
        return "require_review", False, "scope_drift"
    return "clarify", False, "consequence_unacknowledged"


def main() -> int:
    rows = list(csv.DictReader(TRUTH_TABLE.read_text(encoding="utf-8").splitlines()))
    failures: list[str] = []

    seen: set[tuple[bool, bool, bool, bool]] = set()

    for row in rows:
        case_id = row.get("case_id", "<missing case_id>")
        try:
            bits = tuple(parse_bool(row[field]) for field in BIT_FIELDS)
            may_cross = parse_bool(row["may_cross"])
        except Exception as exc:
            failures.append(f"{case_id}: {exc}")
            continue

        if bits in seen:
            failures.append(f"{case_id}: duplicate bit combination {bits}")
        seen.add(bits)

        expected_verdict, expected_may_cross, expected_reason = expected_for_bits(*bits)

        if row["expected_verdict"] not in VALID_VERDICTS:
            failures.append(f"{case_id}: invalid verdict {row['expected_verdict']!r}")
        if row["expected_verdict"] != expected_verdict:
            failures.append(f"{case_id}: verdict {row['expected_verdict']} != expected {expected_verdict}")
        if may_cross != expected_may_cross:
            failures.append(f"{case_id}: may_cross {may_cross} != expected {expected_may_cross}")
        if row["reason_code"] != expected_reason:
            failures.append(f"{case_id}: reason_code {row['reason_code']} != expected {expected_reason}")

    expected_combinations = set(product([False, True], repeat=4))
    missing = expected_combinations - seen
    extra = seen - expected_combinations

    if len(rows) != 16:
        failures.append(f"truth table must contain exactly 16 rows, found {len(rows)}")
    if missing:
        failures.append(f"missing bit combinations: {sorted(missing)}")
    if extra:
        failures.append(f"unexpected bit combinations: {sorted(extra)}")

    if failures:
        print("Four-Bit Crossing Code validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Four-Bit Crossing Code validation passed: 16 truth-table rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
