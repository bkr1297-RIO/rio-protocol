#!/usr/bin/env bash
  set -euo pipefail

  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  cd "$ROOT"

  echo "Portable Constitutional Engine - Gate Simulator v0.1"
  echo "(candidate / developer preview / non-production)"
  echo ""

  if command -v python3 >/dev/null 2>&1; then
    if python3 -m venv .venv >/dev/null 2>&1; then
      echo "Created local virtual environment at .venv (standard library only, no extra dependencies required)."
    else
      echo "Could not create a virtual environment; continuing with system python3."
    fi
  else
    echo "python3 not found on PATH. Please install Python 3 to use this reference implementation."
    exit 1
  fi

  echo ""
  echo "Running negative fixture harness..."
  python3 tests/test_harness_capsule.py

  echo ""
  echo "Next commands:"
  echo "  python3 core/capsule_cli.py examples/sample_capsule.json"
  echo "  cat examples/sample_capsule.json | python3 core/capsule_cli.py -"
  echo "  python3 tests/test_harness_capsule.py"
  echo "  python3 -c \"from core.capsule_factory import make_capsule; print(make_capsule('Draft a note to the team'))\""
  