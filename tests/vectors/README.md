# Test Vectors

This directory will contain deterministic test vectors for the RIO protocol, produced by the Workstream 3 (Conformance Test) agent.

## Expected Contents

Each test vector file is a JSON document containing pre-computed inputs, intermediate values, and expected outputs for a specific protocol operation. Implementations MUST produce identical outputs given identical inputs.

### Planned Vector Files

| File | Description |
|------|-------------|
| `TV-HASH-001_intent_hash.json` | Intent hash computation vectors |
| `TV-HASH-002_action_hash.json` | Action hash computation vectors |
| `TV-HASH-003_verification_hash.json` | Verification hash computation vectors |
| `TV-HASH-004_receipt_hash.json` | Receipt hash computation vectors |
| `TV-HASH-005_ledger_hash.json` | Ledger entry hash computation vectors |
| `TV-SIG-001_receipt_signing.json` | Receipt signing and verification vectors |
| `TV-SIG-002_ledger_signing.json` | Ledger signing and verification vectors |
| `TV-CHAIN-001_hash_chain.json` | Hash chain linkage vectors |
| `TV-CHAIN-002_genesis_block.json` | Genesis block initialization vectors |
| `TV-POLICY-001_risk_scoring.json` | Risk score computation vectors |
| `TV-POLICY-002_threshold_decisions.json` | Policy threshold decision vectors |
| `TV-STATE-001_state_transitions.json` | State machine transition vectors |

## Status

Pending — awaiting WS3 agent output.
