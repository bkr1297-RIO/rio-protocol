# Adversarial Test Suite

**Status:** Documentation Only (No Executable Code)

This document defines adversarial test scenarios for the RIO receipt and ledger protocol. Each scenario describes an attack vector, the expected system behavior, and pass/fail criteria.

---

## 1. Execution Boundary Bypass

### Scenario

An agent or external system attempts to execute an action without passing through the RIO execution gate. The action is submitted directly to the execution layer, bypassing authorization and receipt generation.

### Expected Behavior

The execution layer rejects the request. No action is performed. No receipt is generated. The system remains in its prior state.

### Pass/Fail Criteria

- **PASS:** Request rejected. No side effects. No receipt generated.
- **FAIL:** Action executes without a valid authorization token and receipt.

---

## 2. Payload Drift

### Scenario

A valid authorization token is obtained for action A. The caller modifies the payload to execute action B while presenting the token for action A. The intent hash no longer matches the actual payload.

### Expected Behavior

The gate detects the mismatch between the intent hash bound to the token and the hash of the submitted payload. The request is rejected. A denial receipt is generated recording the mismatch.

### Pass/Fail Criteria

- **PASS:** Request rejected. Denial receipt generated with mismatch recorded.
- **FAIL:** Action B executes under the token authorized for action A.

---

## 3. Ledger Tampering

### Scenario

An attacker with database access modifies a ledger entry after it has been written. The modification changes the `receipt_hash` or any field in the entry.

### Expected Behavior

The hash chain breaks at the modified entry. Any subsequent verification walk detects the mismatch between the stored `current_ledger_hash` and the recomputed hash. All entries after the tampered entry are also flagged as unverifiable.

### Pass/Fail Criteria

- **PASS:** Chain verification fails at the tampered entry. All subsequent entries flagged.
- **FAIL:** Chain verification passes despite the modification.

---

## 4. Signature Tampering

### Scenario

An attacker modifies a receipt's content and attempts to forge a valid signature. The attacker does not have access to the Receipt Service's private key.

### Expected Behavior

Signature verification fails. The forged signature does not match the receipt data when verified against the published public key.

### Pass/Fail Criteria

- **PASS:** Signature verification fails. Receipt is rejected as invalid.
- **FAIL:** Forged signature passes verification.

---

## 5. Replay Attempts

### Scenario

A valid, previously-used authorization token is submitted again for the same or a different action. The nonce in the token has already been consumed.

### Expected Behavior

The nonce registry detects the duplicate. The request is rejected. A denial receipt is generated recording the replay attempt.

### Pass/Fail Criteria

- **PASS:** Request rejected. Denial receipt generated with replay recorded.
- **FAIL:** Token is accepted and action executes a second time.

---

## 6. Batch Validation

### Scenario

A batch of receipts is submitted for ledger verification. One receipt in the middle of the batch has been modified. The receipts before and after the modified entry are valid.

### Expected Behavior

Batch verification walks the chain sequentially. The chain breaks at the modified receipt. All entries from the modified receipt onward are flagged as unverifiable. Entries before the modification are confirmed valid.

### Pass/Fail Criteria

- **PASS:** Verification identifies the exact entry where the chain breaks. Entries before it are valid. Entries from it onward are flagged.
- **FAIL:** Batch verification passes despite the modification, or fails to identify the specific break point.

---

## Summary

| Category | Attack Vector | Detection Mechanism |
|----------|--------------|---------------------|
| Execution Boundary Bypass | Direct execution without gate | Gate rejects; no receipt |
| Payload Drift | Token/payload mismatch | Intent hash comparison |
| Ledger Tampering | Post-write modification | Hash chain verification |
| Signature Tampering | Forged signature | Public key verification |
| Replay Attempts | Reused nonce/token | Nonce registry |
| Batch Validation | Mid-batch modification | Sequential chain walk |

Each scenario is independently testable. No scenario requires access to the RIO runtime — only the receipt data, ledger entries, and the published public key.
