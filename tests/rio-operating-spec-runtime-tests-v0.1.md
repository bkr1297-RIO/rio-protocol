# RIO Operating Spec — Runtime Conformance Tests v0.1

**Status:** Active
**Scope:** Defines the runtime test requirements for conformance to the RIO Operating Spec v0.1. Each test maps to a specific invariant, state transition, or behavioral requirement.
**Parent Spec:** RIO Operating Spec v0.1

---

## §1 — Purpose

This document specifies the conformance tests that a RIO implementation must pass to demonstrate adherence to the Operating Spec. Tests are organized by the spec section they validate. Each test includes the requirement it proves, the expected behavior, and the failure condition.

---

## §2 — Invariant Tests

### INV-1: Human Root Authority

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-1-01 | Root authority registration | System accepts a valid Ed25519 public key as root authority | Registration rejected or system operates without root |
| INV-1-02 | Root authority uniqueness | Only one root authority active at a time; new registration replaces old | Multiple simultaneous root authorities |
| INV-1-03 | Root authority revocation | After revocation, system enters fail-closed state | System continues to authorize after revocation |

### INV-2: Fail-Closed

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-2-01 | Missing token blocks execution | Execution without valid token is denied | Execution proceeds without token |
| INV-2-02 | Expired token blocks execution | Execution with expired token is denied | Execution proceeds with expired token |
| INV-2-03 | Invalid signature blocks execution | Execution with invalid approval signature is denied | Execution proceeds with bad signature |
| INV-2-04 | Timeout blocks execution | Operation that times out results in denial | Partial execution on timeout |
| INV-2-05 | Kill switch blocks all execution | After kill switch activation, all execution is denied | Any execution succeeds after kill switch |

### INV-3: Proposal Before Movement

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-3-01 | No execution without intent | Attempting execution without a prior intent record is denied | Execution without intent succeeds |
| INV-3-02 | No execution without approval | Attempting execution with intent but no approval is denied | Execution without approval succeeds |
| INV-3-03 | Intent must precede approval | Approval for non-existent intent is rejected | Approval accepted for missing intent |

### INV-4: Commit ≠ Gate

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-4-01 | Commitment does not imply gate validation | COMMITTED status alone does not permit execution | Execution proceeds from COMMITTED without gate check |
| INV-4-02 | Gate validates against committed packet | Gate compares execution request to committed packet hash | Gate passes without comparison |
| INV-4-03 | Argument mutation after commit is blocked | Changing args after COMMITTED but before execution results in BLOCKED | Modified args pass gate |

### INV-5: Proposer ≠ Approver

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-5-01 | Self-approval requires constrained delegation | Same identity as proposer and approver triggers friction mechanism | Self-approval proceeds without constraint |
| INV-5-02 | Constrained delegation is recorded | Receipt includes delegation_type field when same-actor | No delegation record in receipt |

### INV-6: Token Lifecycle

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-6-01 | Token issued after approval | Token creation requires a valid approval record | Token issued without approval |
| INV-6-02 | Token validated before execution | Execution validates token (exists, not expired, args match) | Execution skips validation |
| INV-6-03 | Token burned after execution | Token execution_count incremented after use | Token remains unchanged after use |
| INV-6-04 | Token replay blocked | Second use of a max_executions=1 token is denied | Replay succeeds |

### INV-7: Receipt Completeness

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-7-01 | All required fields present | Receipt contains all fields from §9.1 | Any required field missing |
| INV-7-02 | Receipt hash is correct | Recomputing SHA-256 of receipt matches receipt_hash | Hash mismatch |
| INV-7-03 | Previous receipt hash links correctly | previous_receipt_hash matches the prior receipt's receipt_hash | Chain broken |
| INV-7-04 | Handoff receipt hash present | Receipt includes handoff_receipt_hash binding | Missing handoff binding |

### INV-8: Ledger Integrity

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-8-01 | Append-only enforcement | No ledger entry can be modified after creation | Entry modification succeeds |
| INV-8-02 | Hash chain verifies | Full chain verification passes on valid ledger | Verification fails on valid data |
| INV-8-03 | Tampered entry detected | Modifying any entry causes chain verification to fail | Tampered entry passes verification |
| INV-8-04 | Deleted entry detected | Removing any entry causes chain verification to fail | Deleted entry not detected |

### INV-9: Context Cannot Expand Authority

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-9-01 | Context does not grant permission | Operational context (retry, log, signal) cannot elevate authorization | Context-based elevation succeeds |
| INV-9-02 | Policy snapshot frozen before context | Policy hash computed before context enrichment | Policy modified by context |

### INV-10: Learning is Advisory

| Test ID | Description | Pass Condition | Failure Condition |
|---------|-------------|----------------|-------------------|
| INV-10-01 | Learning cannot approve | MANTIS advisory score does not auto-approve actions | Advisory score triggers approval |
| INV-10-02 | Learning cannot execute | Learning loop cannot trigger execution | Learning triggers side effect |
| INV-10-03 | Learning cannot bypass governance | High advisory confidence does not skip governance steps | Governance step skipped |

---

## §3 — State Machine Tests

### §3.1 — Happy Path

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| SM-HP-01 | Full lifecycle completes | Action traverses SIGNAL → INTERPRETED → PACKETIZED → PRECHECKED → REVIEWED → COMMITTED → GATE_VALIDATED → EXECUTED → RECEIPTED → RECORDED → LEARNED |
| SM-HP-02 | Each state transition recorded | State trace contains all intermediate states |
| SM-HP-03 | No state skipped | Removing any intermediate state causes validation failure |

### §3.2 — Branch Paths

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| SM-BR-01 | Human refusal path | REVIEWED → REFUSED → RECEIPTED → RECORDED → LEARNED |
| SM-BR-02 | Clarification loop | REVIEWED → CLARIFY → REVIEWED resumes correctly |
| SM-BR-03 | Hold and resume | REVIEWED → HOLD → REVIEWED resumes correctly |
| SM-BR-04 | Policy denial | PRECHECKED → BLOCKED → RECEIPTED → RECORDED → LEARNED |
| SM-BR-05 | Execution failure | GATE_VALIDATED → FAILED → RECEIPTED → RECORDED → LEARNED |
| SM-BR-06 | Kill switch from any state | Any active state → BLOCKED on kill switch activation |

### §3.3 — Terminal State Properties

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| SM-TS-01 | Outcome terminals continue to receipt | BLOCKED, REFUSED, FAILED all transition to RECEIPTED |
| SM-TS-02 | LEARNED is lifecycle terminal | No transitions from LEARNED state |
| SM-TS-03 | Only LEARNED is lifecycle terminal | All other states have at least one valid transition |

---

## §4 — Verdict Tests

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| VD-01 | BLOCK verdict halts execution | BLOCK prevents any further execution |
| VD-02 | HOLD verdict pauses action | HOLD suspends action without denial |
| VD-03 | WARN verdict allows with signal | WARN permits execution but records advisory signal |
| VD-04 | CLARIFY verdict requests input | CLARIFY pauses for human clarification |
| VD-05 | PASS verdict permits execution | PASS allows action to proceed |
| VD-06 | Precedence enforced | BLOCK > HOLD > WARN > CLARIFY > PASS when multiple verdicts apply |
| VD-07 | INVALID verdict rejects at intake | Structurally invalid input cannot enter pipeline |

---

## §5 — Receipt and Ledger Tests

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| RL-01 | Receipt generated for success | Successful execution produces a signed receipt |
| RL-02 | Receipt generated for failure | Failed execution produces a signed receipt |
| RL-03 | Receipt generated for block | Blocked action produces a signed receipt |
| RL-04 | Receipt generated for refusal | Refused action produces a signed receipt |
| RL-05 | Ledger entry created for every receipt | Each receipt has a corresponding ledger entry |
| RL-06 | Ledger hash chain unbroken | After N operations, full chain verification passes |
| RL-07 | Receipt signature verifies | Ed25519 signature on receipt verifies with public key |

---

## §6 — Kill Switch Tests

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| KS-01 | Kill switch immediately effective | All pending actions blocked within same tick |
| KS-02 | Kill switch recorded in ledger | Activation produces a KILL_SWITCH ledger entry |
| KS-03 | Kill switch invalidates all tokens | No token validates after kill switch |
| KS-04 | Kill switch accessible from any state | Kill switch can be activated regardless of current action state |

---

## §7 — Handoff Receipt Tests

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| HR-01 | Handoff receipt generated | generateHandoffReceipt produces a valid receipt |
| HR-02 | Handoff receipt validates | validateHandoffReceipt returns true for valid receipt |
| HR-03 | Handoff receipt hash deterministic | Same input produces same hash |
| HR-04 | Handoff linked to action receipt | linkHandoffToActionReceipt binds handoff hash to action |
| HR-05 | Handoff appended to ledger | appendHandoffToLedger creates a ledger entry |
| HR-06 | Tampered handoff detected | Modified handoff receipt fails validation |
| HR-07 | Action rejected without handoff binding | Action receipt without valid handoff_receipt_hash is rejected |

---

## §8 — WAL (Write-Ahead Log) Tests

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| WAL-01 | WAL_PREPARED before execution | WAL entry created before connector dispatch |
| WAL-02 | WAL_COMMITTED after success | WAL entry updated to COMMITTED on success |
| WAL-03 | WAL_FAILED after failure | WAL entry updated to FAILED on execution error |
| WAL-04 | Incomplete WAL detected on startup | Startup verification identifies uncommitted WAL entries |

---

## §9 — Sentinel Tests

| Test ID | Description | Pass Condition |
|---------|-------------|----------------|
| SN-01 | Contrast detection fires | Behavioral drift beyond threshold produces signal |
| SN-02 | Velocity anomaly fires | Unusual action frequency produces signal |
| SN-03 | Invariant check covers all 10 | checkSystemInvariants returns result for each invariant |
| SN-04 | Sentinel cannot execute | Sentinel operations produce no side effects |
| SN-05 | Signals require human acknowledgment | Unacknowledged signals persist until human review |

---

## §10 — Implementation Evidence

The reference implementation (rio-proxy) has the following test coverage against this outline:

| Section | Tests Specified | Tests Passing in Reference | Coverage |
|---------|----------------|---------------------------|----------|
| Invariant Tests (§2) | 26 | 24 | 92% |
| State Machine Tests (§3) | 9 | 9 | 100% |
| Verdict Tests (§4) | 7 | 7 | 100% |
| Receipt and Ledger Tests (§5) | 7 | 7 | 100% |
| Kill Switch Tests (§6) | 4 | 4 | 100% |
| Handoff Receipt Tests (§7) | 7 | 7 | 100% |
| WAL Tests (§8) | 4 | 4 | 100% |
| Sentinel Tests (§9) | 5 | 5 | 100% |

**Gaps:** INV-9-02 (policy snapshot timing) and INV-5-02 (delegation_type field in receipt) are specified but not yet tested in the reference implementation.

---

## §11 — Conformance Levels

**Level 1 — Structural:** All REQUIRED operations exist and are callable. State machine transitions are enforced. Receipts contain all required fields.

**Level 2 — Behavioral:** Fail-closed behavior verified. Token lifecycle enforced. Kill switch effective. Ledger integrity maintained.

**Level 3 — Adversarial:** Tampered receipts detected. Replayed tokens blocked. Argument mutation blocked. Self-approval constrained. WAL integrity maintained.

The reference implementation currently satisfies Level 1, Level 2, and Level 3 in automated tests. Live runtime has demonstrated Level 1 and Level 2 for LOW-risk actions.
