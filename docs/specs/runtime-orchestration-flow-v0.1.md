# Runtime Orchestration Flow Specification v0.1

**Version:** 0.1  
**Date:** 2026-05-06  
**Author:** B-Rass (RIO Architect)  
**Status:** Local harness specification

---

## 1. Overview

This document specifies the exact data flow, function signatures, and state transitions for the Runtime Orchestration harness. It is the implementation contract for `server/runtime-orchestrator/`.

---

## 2. Entry Point

```typescript
interface OrchestratorInput {
  human_input: string;
  user_id: string;
  session_id: string;
  timestamp: number; // UTC ms
}

interface OrchestratorOutput {
  verdict: "PASS" | "WARN" | "HOLD" | "BLOCK" | "INVALID";
  packet: ProposalPacket | RefusalRecord | null;
  governance_decision: "APPROVED" | "REFUSED" | "ESCALATED" | "NOT_REQUIRED" | null;
  execution_result: SimulatedExecution | null;
  sentinel_result: SentinelVerification | null;
  receipts: Receipt[];
  ledger_entries: LedgerEntry[];
  mantis_observations: MantisObservation[];
}
```

The orchestrator function signature:

```typescript
async function orchestrate(input: OrchestratorInput): Promise<OrchestratorOutput>
```

---

## 3. Step-by-Step Flow

### Step 1: Language Evaluation

```typescript
const scanResult = await grammarScanner.evaluate(input.human_input);
// Returns: { verdict, triggered_rule, reliance_context, route, safe_revision, receipt_required }
```

### Step 2: Verdict Routing

| Verdict | Next Step |
|---------|-----------|
| PASS | Return with optional evaluation log. No further routing. |
| WARN | Construct Proposal Packet → Step 3 |
| HOLD | Construct Proposal Packet → Step 3 |
| BLOCK | Construct Refusal Record → Step 6 |
| INVALID | Construct Refusal Record → Step 6 |

### Step 3: Proposal Packet Construction

```typescript
const packet = constructProposalPacket({
  scanner_result: scanResult,
  human_input: input.human_input,
  user_id: input.user_id,
  session_id: input.session_id,
  timestamp: input.timestamp
});
```

The constructor maps scanner output to packet fields:
- `meaning_context` ← classification tag from scanner
- `reliance_context` ← from scanner reliance_context
- `consequence_level` ← derived from verdict + reliance_context
- `rio_required` ← true if HOLD, or if consequence_level >= "consequential"
- `sentinel_required` ← true if consequence_level == "irreversible"
- `answer_check_required` ← true if public_claims present
- `receipt_required` ← true if verdict != PASS

### Step 4: Governance Routing

Based on packet routing flags, the orchestrator dispatches in order:

```typescript
// 4a. ONE Answer Check (if applicable)
if (packet.answer_check_required && packet.public_claims.length > 0) {
  const answerCheck = await oneAnswerCheck.evaluate(packet.public_claims);
  receipts.push(generateReceipt("governance", answerCheck));
}

// 4b. RIO Governance (if applicable)
if (packet.rio_required) {
  const rioDecision = await rioGovernance.evaluate(packet);
  receipts.push(generateReceipt("governance", rioDecision));
  
  if (rioDecision.decision === "REFUSED") {
    // → Step 6 (refusal path)
  }
  if (rioDecision.decision === "APPROVED") {
    // → Step 5 (execution path)
  }
}
```

### Step 5: Execution Path (Approved Only)

```typescript
// 5a. Check for human revocation before execution
if (await checkRevocation(packet.packet_id)) {
  receipts.push(generateReceipt("revocation", { packet_id: packet.packet_id }));
  // → Ledger update, MANTIS observe, return
}

// 5b. Simulate execution
const executionResult = await simulateExecution(packet.requested_action);

// 5c. Sentinel verification (if required)
if (packet.sentinel_required) {
  const sentinelResult = await sentinel.verify(packet, executionResult);
  if (sentinelResult.status === "MISMATCH") {
    receipts.push(generateReceipt("mismatch", sentinelResult));
    // Execution blocked. → Ledger update, MANTIS observe, return
  }
}

// 5d. Execution receipt
receipts.push(generateReceipt("execution", executionResult));
```

### Step 6: Refusal Path

For BLOCK/INVALID verdicts (refusal record, not normal Proposal Packet):

```typescript
const refusalRecord = constructRefusalRecord({
  scanner_result: scanResult,
  human_input: input.human_input,
  reason: scanResult.triggered_rule,
  timestamp: input.timestamp
});
receipts.push(generateReceipt("refusal", refusalRecord));
```

For RIO REFUSED decisions:

```typescript
receipts.push(generateReceipt("refusal", {
  packet_id: packet.packet_id,
  reason: rioDecision.reason,
  constraints_violated: rioDecision.constraints_violated
}));
```

### Step 7: Ledger Update

Every receipt is written to the ledger:

```typescript
for (const receipt of receipts) {
  const entry = await ledger.append({
    receipt_hash: hash(receipt),
    event_type: receipt.type,
    timestamp: Date.now()
  });
  ledgerEntries.push(entry);
}
```

### Step 8: MANTIS Observation

After all processing is complete:

```typescript
const observation = mantis.observe({
  packet: packet || refusalRecord || null,
  receipts,
  ledger_entries: ledgerEntries,
  verdict: scanResult.verdict
});
mantisObservations.push(observation);
```

MANTIS records pattern data only. It does not modify, route, or authorize anything.

---

## 4. Receipt Schema

```typescript
interface Receipt {
  receipt_id: string;        // UUID
  type: ReceiptType;
  timestamp: number;         // UTC ms
  packet_id: string | null;  // Associated packet (null for PASS/refusal records)
  payload: Record<string, unknown>;
  receipt_hash: string;      // SHA-256 of canonical payload
  previous_receipt_hash: string; // Chain link
  signer_id: string;         // "rio-local-harness"
}

type ReceiptType = 
  | "evaluation"
  | "refusal"
  | "governance"
  | "authorization"
  | "execution"
  | "revocation"
  | "mismatch";
```

---

## 5. Ledger Entry Schema

```typescript
interface LedgerEntry {
  entry_id: string;          // Auto-incrementing or UUID
  receipt_hash: string;      // Hash of the receipt this entry records
  previous_hash: string;     // Hash of previous ledger entry (chain)
  timestamp: number;         // UTC ms
  event_type: ReceiptType;   // Mirrors receipt type
  entry_hash: string;        // SHA-256 of this entry's canonical form
}
```

Chain verification: `hash(entry[n]) === entry[n+1].previous_hash`

---

## 6. MANTIS Observation Schema

```typescript
interface MantisObservation {
  observation_id: string;
  timestamp: number;
  observed_verdict: string;
  observed_packet_type: string | null;
  observed_outcome: string;
  pattern_match: PatternMatch | null;
}

interface PatternMatch {
  pattern_type: "repeated_crossing" | "repeated_refusal" | "repeated_revocation";
  count: number;
  first_seen: number;
  last_seen: number;
}
```

MANTIS never: authorizes, blocks, routes, recommends, or modifies behavior.

---

## 7. Simulated Execution

All execution in this harness is simulated. No outbound integrations.

```typescript
interface SimulatedExecution {
  execution_id: string;
  action_type: string;
  action_description: string;
  scope: string;
  simulated: true;           // Always true in local harness
  result: "completed" | "blocked_by_sentinel";
  timestamp: number;
}
```

---

## 8. Sentinel Verification

```typescript
interface SentinelVerification {
  verification_id: string;
  packet_id: string;
  approved_scope: string;
  executed_scope: string;
  status: "MATCH" | "MISMATCH";
  reason: string | null;     // Populated on MISMATCH
}
```

Sentinel compares `packet.requested_action.scope` against `execution.scope`. If they differ, status is MISMATCH and execution is blocked.

---

## 9. RIO Governance Evaluation (Simulated)

```typescript
interface RIODecision {
  decision: "APPROVED" | "REFUSED" | "ESCALATED";
  reason: string;
  constraints_evaluated: string[];
  constraints_violated: string[];
  policy_hash: string;       // Hash of policy used for evaluation
}
```

In the local harness, RIO governance is rule-based:
- `consequence_level === "irreversible"` + no explicit human confirmation → REFUSED
- Bypass attempt detected (urgency, social proof) → REFUSED
- Unbounded delegation → REFUSED
- Properly scoped, consequential action → APPROVED
- All other HOLD packets → APPROVED (default for local harness)

---

## 10. Revocation

```typescript
interface Revocation {
  packet_id: string;
  revoked_by: string;        // user_id
  revoked_at: number;        // UTC ms
  reason: string;
}
```

Revocation is checked between RIO approval and execution. If the human has revoked authorization, execution does not proceed.

---

## 11. Error Handling

The orchestrator does not suppress errors. If any component fails:
- The failure is recorded as a receipt (type: "evaluation", payload includes error)
- The ledger is updated
- No execution proceeds (fail-closed for consequence)
- Private exploration remains available

---

## 12. Version History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-05-06 | Initial flow specification |
