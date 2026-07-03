#!/usr/bin/env bash
set -euo pipefail

echo "RIO packet grammar check"
echo "Repository: $(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
echo "Commit: $(git rev-parse --short HEAD 2>/dev/null || echo unknown)"
echo ""

python3 tests/packet_grammar/validate_scribe_compiler_capsule.py
python3 tests/packet_grammar/validate_four_bit_crossing_code.py
python3 tests/packet_grammar/validate_four_bit_crossing_harness_negatives.py
python3 tests/packet_grammar/validate_gate_evidence.py
python3 tests/packet_grammar/validate_receipt_binding.py

echo ""
echo "RIO packet grammar check complete"
