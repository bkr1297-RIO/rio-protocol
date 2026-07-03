# Replit Run Packet: Packet Grammar Checks

**Status:** Execution handoff / docs-only  
**Runtime surface:** Replit shell  
**Purpose:** Run the packet grammar validators and return output as a receipt.

---

## Commands

From the Replit shell connected to this repository:

```bash
git status
git checkout main
git pull origin main
bash scripts/replit_run_packet_grammar_checks.sh
```

---

## Expected Output

```text
RIO packet grammar check
Repository: rio-protocol
Commit: <current-short-sha>

Scribe-Compiler Capsule fixture validation passed: 2 fixtures
Four-Bit Crossing Code validation passed: 16 truth-table rows
Four-Bit Crossing Code harness-negative validation passed: 5 malformed datasets rejected

RIO packet grammar check complete
```

---

## Return Requirement

Paste the full shell output back into the working thread.

If the script passes, record the output in a run receipt.

If the script fails, do not claim verification. Return the failure output for patching.

---

## Boundary

This run verifies candidate packet grammar validators only.

It does not claim live conformance, production enforcement, receipt verification, deployment, or certification.
