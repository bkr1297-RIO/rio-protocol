#!/usr/bin/env python3
"""
Portable Constitutional Engine - Capsule CLI v0.1
Candidate reference implementation / developer preview / non-production.

Reads a Capsule JSON file (or stdin) and evaluates it through the Gate
Simulator, printing a receipt-style JSON result. This CLI performs no
live tool calls, live adapter calls, or network requests.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from gate_simulator import evaluate  # noqa: E402


def _load_capsule(path):
    if path is None or path == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(path).read_text()
    return json.loads(raw)


def main(argv):
    path = argv[1] if len(argv) > 1 else None
    capsule = _load_capsule(path)
    result = evaluate(capsule)

    receipt = {
        "candidate_receipt": True,
        "capsule_id": capsule.get("capsule_id"),
        "verdict": result["verdict"],
        "reasons": result["reasons"],
        "note": "deterministic receipt hash only; not a cryptographic authority proof",
        "boundary": (
            "candidate reference implementation / developer preview / non-production; "
            "no live conformance, production enforcement, deployment, readiness, "
            "or certification is claimed"
        ),
    }
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
