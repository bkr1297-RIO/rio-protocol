# Minimal Conformance Example

**Purpose:** Demonstrate one complete governed action flowing through the entire RIO protocol — from intent to verified ledger entry. This example uses only concepts defined in the existing specs.

---

## Scenario

A human asks an AI assistant to send an email. The system governs this action through the full lifecycle.

---

## Step 1 — Intent

The human expresses intent in natural language:

```json
{
  "raw_input": "Send an email to alice@example.com confirming the meeting tomorrow at 2pm",
  "source": "human",
  "timestamp": "2026-05-04T10:00:00.000Z"
}
```

**State:** SIGNAL → INTERPRETED

The system parses this into structured intent:

```json
{
  "intent_id": "intent_a1b2c3d4",
  "action_type": "send_email",
  "parameters": {
    "to": "alice@example.com",
    "subject": "Meeting Confirmation",
    "body": "Confirming our meeting tomorrow at 2:00 PM."
  },
  "risk_tier": "HIGH",
  "blast_radius": "external"
}
```

---

## Step 2 — Packet

The intent is wrapped in a governance packet:

```json
{
  "packet_id": "pkt_e5f6g7h8",
  "intent_id": "intent_a1b2c3d4",
  "proposer_id": "agent_manny",
  "packet_hash": "sha256:9f3a7c2e1b4d8f6a0c5e7d9b2f4a6c8e1d3f5a7b9c0e2d4f6a8b0c2d4e6f8a0b",
  "policy_version": "policy_v1.2",
  "risk_evaluation": {
    "tier": "HIGH",
    "reason": "External communication — irreversible side effect",
    "blast_radius": "external",
    "requires_human_approval": true
  },
  "created_at": "2026-05-04T10:00:01.000Z"
}
```

**State:** PACKETIZED → PRECHECKED

Pre-check confirms: policy allows email actions, risk tier requires human approval, proposer is identified.

---

## Step 3 — Approval

The packet is presented to the human for review.

**State:** REVIEWED

The human reviews and commits authority:

```json
{
  "approval_id": "appr_i9j0k1l2",
  "packet_id": "pkt_e5f6g7h8",
  "packet_hash": "sha256:9f3a7c2e1b4d8f6a0c5e7d9b2f4a6c8e1d3f5a7b9c0e2d4f6a8b0c2d4e6f8a0b",
  "approver_id": "human_brian",
  "proposer_id": "agent_manny",
  "decision": "COMMITTED",
  "timestamp": "2026-05-04T10:01:30.000Z"
}
```

**State:** COMMITTED

**Invariant check:** `proposer_id` (agent_manny) ≠ `approver_id` (human_brian). INV-5 satisfied.

An authorization token is issued:

```json
{
  "token_id": "tok_m3n4o5p6",
  "packet_id": "pkt_e5f6g7h8",
  "packet_hash": "sha256:9f3a7c2e1b4d8f6a0c5e7d9b2f4a6c8e1d3f5a7b9c0e2d4f6a8b0c2d4e6f8a0b",
  "issued_at": "2026-05-04T10:01:31.000Z",
  "expires_at": "2026-05-04T10:06:31.000Z",
  "burned": false
}
```

---

## Step 4 — Execution

The Sentinel gate validates before execution:

```json
{
  "gate_check": {
    "token_valid": true,
    "token_not_expired": true,
    "token_not_burned": true,
    "packet_hash_matches": true,
    "proposer_ne_approver": true,
    "policy_snapshot_hash_matches": true,
    "arguments_hash_matches": true
  },
  "verdict": "GATE_PASS"
}
```

**State:** GATE_VALIDATED → EXECUTING

The action executes through the controlled email adapter:

```json
{
  "execution_id": "exec_q7r8s9t0",
  "action_type": "send_email",
  "connector": "email_gateway",
  "parameters_hash": "sha256:2a4b6c8d0e2f4a6b8c0d2e4f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b",
  "result": "SUCCESS",
  "timestamp": "2026-05-04T10:01:32.000Z"
}
```

**State:** EXECUTED

Token is burned immediately:

```json
{
  "token_id": "tok_m3n4o5p6",
  "burned": true,
  "burned_at": "2026-05-04T10:01:32.001Z"
}
```

---

## Step 5 — Receipt

A cryptographic receipt is generated:

```json
{
  "receipt_id": "rcpt_u1v2w3x4",
  "intent_id": "intent_a1b2c3d4",
  "packet_id": "pkt_e5f6g7h8",
  "approver_id": "human_brian",
  "token_id": "tok_m3n4o5p6",
  "policy_hash": "sha256:policy_v1.2_hash",
  "snapshot_hash": "sha256:frozen_policy_snapshot",
  "handoff_receipt_hash": "sha256:handoff_binding_proof",
  "execution_result": "SUCCESS",
  "execution_hash": "sha256:exec_output_hash",
  "previous_receipt_hash": "sha256:previous_chain_link",
  "receipt_hash": "sha256:5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d",
  "signature": "ed25519:gateway_signature_bytes_base64",
  "signer_id": "rio_gateway",
  "timestamp": "2026-05-04T10:01:32.100Z"
}
```

**State:** RECEIPTED

**Receipt completeness check (INV-7):**
- intent_id: present
- approver_id: present
- token_id: present
- policy_hash: present
- execution_result: present
- receipt_hash: present
- previous_receipt_hash: present
- snapshot_hash: present

All required fields present.

---

## Step 6 — Ledger

The receipt hash is written to the append-only ledger:

```json
{
  "ledger_entry_id": "led_y5z6a7b8",
  "receipt_hash": "sha256:5c7d9e1f3a5b7c9d1e3f5a7b9c1d3e5f7a9b1c3d5e7f9a1b3c5d7e9f1a3b5c7d",
  "previous_entry_hash": "sha256:previous_ledger_entry_hash",
  "entry_hash": "sha256:this_ledger_entry_hash",
  "sequence_number": 42,
  "timestamp": "2026-05-04T10:01:32.200Z"
}
```

**State:** LEDGERED

**Ledger integrity check (INV-8):**
- Entry references previous entry hash: yes
- Hash chain is contiguous: yes
- Append-only discipline maintained: yes

---

## Step 7 — Verification Result

An independent verifier checks the receipt:

```json
{
  "verification_id": "ver_c9d0e1f2",
  "receipt_id": "rcpt_u1v2w3x4",
  "checks": {
    "structural_validity": "PASS",
    "signature_validity": "PASS",
    "chain_consistency": "PASS",
    "temporal_validity": "PASS",
    "token_lifecycle": "PASS",
    "policy_binding": "PASS"
  },
  "verdict": "VERIFIED",
  "verified_at": "2026-05-04T10:01:32.300Z"
}
```

**State:** VERIFIED

---

## Summary

This example demonstrates the complete governed action lifecycle:

| Step | State Transition | What Was Proven |
|------|-----------------|-----------------|
| Intent | SIGNAL → INTERPRETED | Raw input parsed into structured action |
| Packet | PACKETIZED → PRECHECKED | Intent wrapped with hash, risk evaluated |
| Approval | REVIEWED → COMMITTED | Human committed authority, proposer ≠ approver |
| Execution | GATE_VALIDATED → EXECUTED | Gate passed, action performed, token burned |
| Receipt | EXECUTED → RECEIPTED | Cryptographic proof generated with all fields |
| Ledger | RECEIPTED → LEDGERED | Hash-chained, append-only record preserved |
| Verification | LEDGERED → VERIFIED | Independent check confirms validity |

---

## What This Proves

A system that passes this example demonstrates:

1. No action without structured intent
2. No execution without human approval
3. No execution without gate validation
4. No receipt without all required fields
5. No ledger entry without hash chain linkage
6. No verification without independent checking
7. Proposer and approver are structurally separated
8. Tokens are single-use (issued, validated, burned)
9. The entire chain is independently verifiable after the fact

---

## Negative Cases (Also Required for Conformance)

A conformant implementation must also demonstrate:

- **Missing approval:** Action blocked at PRECHECKED, never reaches EXECUTING
- **Expired token:** Gate check fails, execution denied
- **Token replay:** Second use of same token rejected
- **Argument mutation:** Packet hash mismatch at gate, execution denied
- **Self-approval:** Proposer = approver detected, constrained delegation friction enforced
- **Broken chain:** Ledger verification detects tampered previous_hash, flags FAILED

These negative cases are documented in `tests/rio-operating-spec-runtime-tests-v0.1.md`.
