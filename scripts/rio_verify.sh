
  #!/usr/bin/env bash
  set -euo pipefail

  ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  cd "$ROOT"

  REPO_NAME="$(basename "$ROOT")"
  FULL_SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
  SHORT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
  BRANCH="$(git branch --show-current 2>/dev/null || echo unknown)"
  STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  VALIDATORS=(
    "tests/packet_grammar/validate_scribe_compiler_capsule.py"
    "tests/packet_grammar/validate_four_bit_crossing_code.py"
    "tests/packet_grammar/validate_four_bit_crossing_harness_negatives.py"
    "tests/packet_grammar/validate_gate_evidence.py"
    "tests/packet_grammar/validate_receipt_binding.py"
    "reference/portable_constitutional_engine/tests/test_harness_capsule.py"
  )

  echo "RIO verification run"
  echo "Repository: ${REPO_NAME}"
  echo "Branch: ${BRANCH}"
  echo "Commit: ${SHORT_SHA}"
  echo "Full commit: ${FULL_SHA}"
  echo "Started at UTC: ${STARTED_AT}"
  echo ""

  for validator in "${VALIDATORS[@]}"; do
    python3 "$validator"
  done

  FINISHED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  echo ""
  echo "RIO verification complete"
  echo "Finished at UTC: ${FINISHED_AT}"
  echo "Exit code: 0"
  echo ""
  echo "Receipt-ready summary:"
  echo "- repository: ${REPO_NAME}"
  echo "- branch: ${BRANCH}"
  echo "- verified_commit: ${FULL_SHA}"
  echo "- short_sha: ${SHORT_SHA}"
  echo "- command: bash scripts/rio_verify.sh"
  echo "- result: PASS"
  echo "- boundary: candidate packet grammar, Gate Evidence, Receipt Binding, and Portable Constitutional Engine Gate Simulator validators only; no live conformance, production enforcement, deployment, readiness, or certification claimed"
  