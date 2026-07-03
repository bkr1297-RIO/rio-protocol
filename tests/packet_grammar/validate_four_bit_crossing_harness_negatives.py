#!/usr/bin/env python3
"""Validate that the Four-Bit Crossing Code harness rejects malformed datasets."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path

from validate_four_bit_crossing_code import validate_truth_table

ROOT = Path(__file__).resolve().parents[2]
GOLDEN = ROOT / "tests" / "packet_grammar" / "four_bit_crossing_code_truth_table_v0.1.csv"
NEGATIVES = ROOT / "tests" / "packet_grammar" / "four_bit_crossing_code_harness_negatives_v0.1.json"


def write_rows(path: Path, rows: list[dict]) -> None:
    fieldnames = ["case_id", "authority", "scope", "consequence", "return", "expected_verdict", "may_cross", "reason_code"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def apply_mutation(rows: list[dict], mutation: dict) -> list[dict]:
    mutated = [dict(row) for row in rows]
    mutation_type = mutation["type"]

    if mutation_type == "duplicate_case":
        case_id = mutation["case_id"]
        for row in mutated:
            if row["case_id"] == case_id:
                mutated.append(dict(row))
                return mutated
        raise AssertionError(f"case not found for duplicate: {case_id}")

    if mutation_type == "delete_case":
        case_id = mutation["case_id"]
        return [row for row in mutated if row["case_id"] != case_id]

    if mutation_type == "set_field":
        case_id = mutation["case_id"]
        for row in mutated:
            if row["case_id"] == case_id:
                row[mutation["field"]] = mutation["value"]
                return mutated
        raise AssertionError(f"case not found for set_field: {case_id}")

    if mutation_type == "add_row":
        mutated.append(mutation["row"])
        return mutated

    raise AssertionError(f"unknown mutation type: {mutation_type}")


def main() -> int:
    golden_rows = list(csv.DictReader(GOLDEN.read_text(encoding="utf-8").splitlines()))
    cases = json.loads(NEGATIVES.read_text(encoding="utf-8"))["negative_cases"]
    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp = Path(tmp_dir)
        for case in cases:
            case_id = case["id"]
            mutated_rows = apply_mutation(golden_rows, case["mutation"])
            mutated_path = tmp / f"{case_id}.csv"
            write_rows(mutated_path, mutated_rows)

            actual_failures = validate_truth_table(mutated_path)
            if not actual_failures:
                failures.append(f"{case_id}: malformed table unexpectedly passed")
                continue

            joined = "\n".join(actual_failures)
            expected = case["expected_failure_contains"]
            if expected not in joined:
                failures.append(f"{case_id}: expected failure containing {expected!r}, got {joined!r}")

    if failures:
        print("Four-Bit Crossing Code harness-negative validation FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Four-Bit Crossing Code harness-negative validation passed: {len(cases)} malformed datasets rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
