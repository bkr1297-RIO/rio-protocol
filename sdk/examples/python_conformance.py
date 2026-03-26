#!/usr/bin/env python3
"""
RIO Protocol SDK — Python Conformance + Compliance Example
===========================================================
Demonstrates:
  1. run_conformance_tests()  — run Appendix C hash test vectors
  2. get_compliance_level()   — inspect a project for compliance level

Run from the sdk/ directory:
    python examples/python_conformance_example.py
"""

import sys
from pathlib import Path

# Add the python SDK to the path (not needed after pip install)
sys.path.insert(0, str(Path(__file__).parent.parent / "python"))

from rio_sdk import run_conformance_tests, get_compliance_level

# Path to the gateway project root (where gateway.db lives)
GATEWAY_DIR = Path(__file__).parent.parent.parent


def show_conformance():
    print("=" * 60)
    print(" [1] Conformance Test Vectors (Appendix C)")
    print("=" * 60)

    result = run_conformance_tests()

    print(f"\n Overall: {result['overall']}")
    print(f" Vectors: {result['passed']}/{result['total']} passed\n")

    col_id   = 6
    col_name = 42
    print(f" {'ID':<{col_id}}  {'Test Name':<{col_name}}  Result")
    print(" " + "-" * (col_id + col_name + 10))

    for r in result["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        name   = r["name"][:col_name]
        print(f" {r['id']:<{col_id}}  {name:<{col_name}}  {status}")

    if result["failed"] > 0:
        print("\n Failures:")
        for r in result["results"]:
            if not r["passed"]:
                print(f"   {r['id']}: expected {r['expected'][:16]}…  got {r['computed'][:16]}…")

    return result["overall"] == "PASS"


def show_compliance():
    print("\n" + "=" * 60)
    print(" [2] Compliance Level Check")
    print("=" * 60)

    result = get_compliance_level(GATEWAY_DIR)

    print(f"\n Level:  {result['level']}")
    print(f" Label:  {result['label']}")
    print(f"\n Checks:")

    for check in result["checks"]:
        icon = "✓" if check["passed"] else "✗"
        print(f"   {icon} Level {check['level']} — {check['name']}")
        print(f"       {check['detail']}")

    return result["level"]


def main():
    conformance_ok = show_conformance()
    level          = show_compliance()

    print("\n" + "=" * 60)
    print(f" Conformance vectors:  {'PASS' if conformance_ok else 'FAIL'}")
    print(f" Compliance level:     {level} — {['Non-Compliant','Cryptographic','Pipeline','Full Protocol'][level]}")
    print("=" * 60)

    return 0 if conformance_ok else 1


if __name__ == "__main__":
    sys.exit(main())
