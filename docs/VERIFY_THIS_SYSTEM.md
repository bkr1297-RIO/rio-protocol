# Verify This System

This document enables local validation of the RIO receipt and ledger protocol. It demonstrates both proof and failure.

---

## 1. Install

Clone the repository:

```bash
git clone https://github.com/bkr1297-RIO/rio-protocol.git
cd rio-protocol
```

No additional dependencies are required. Verification uses only the test vectors and schemas in this repository.

---

## 2. Run Example

Load a valid receipt from the test vectors:

```bash
cat tests/vectors/valid_receipt.json
```

Confirm it contains all required fields defined in `spec/receipt_schema.json`:

- `receipt_id`
- `request_id`
- `intent_id`
- `authorization_id`
- `decision`
- `action_type`
- `execution_timestamp`
- `result_hash`
- `previous_receipt_hash`
- `signature`

---

## 3. Verify Receipt

Recompute the `result_hash` from the execution result payload:

```bash
echo -n '<canonical_json_of_execution_result>' | sha256sum
```

Compare the output to the `result_hash` field in the receipt. They must match exactly.

Verify the `previous_receipt_hash` matches the hash of the preceding receipt in the chain.

Verify the signature using the published public key:

```bash
# Using OpenSSL or equivalent Ed25519/ECDSA verification tool
# The exact command depends on the signing algorithm used
```

If all three checks pass, the receipt is valid.

---

## 4. Verify Ledger

Walk the ledger chain from the genesis entry:

1. Confirm the genesis entry's `previous_ledger_hash` equals `SHA-256(b'GENESIS')`.
2. For each subsequent entry, confirm:
   - `current_ledger_hash` equals `SHA-256(previous_ledger_hash + receipt_hash)` (UTF-8 concatenation)
   - `previous_ledger_hash` equals the preceding entry's `current_ledger_hash`
   - `receipt_hash` matches the corresponding receipt
3. Confirm no gaps, no reordering, no missing entries.

If the full chain validates, the ledger is intact.

---

## 5. Break the System (Modify Data)

Demonstrate tamper detection by modifying a receipt:

1. Copy a valid receipt from the test vectors.
2. Change any field (e.g., flip the `decision` from `ALLOW` to `DENY`).
3. Recompute the `result_hash` — it no longer matches.
4. Recompute the ledger chain — the hash chain breaks at the modified entry.
5. Verify the signature — it is now invalid.

This demonstrates that any modification to any receipt is detectable.

---

## 6. Verify Failure

After modifying the receipt:

- Hash verification: FAIL (recomputed hash does not match stored hash)
- Chain verification: FAIL (subsequent entries reference the original hash, not the modified one)
- Signature verification: FAIL (signature was computed over the original data)

All three failures confirm the system detects tampering.

---

## Summary

| Step | Action | Expected Result |
|------|--------|-----------------|
| Load receipt | Read from test vectors | All required fields present |
| Verify hash | Recompute from source data | Matches stored hash |
| Verify chain | Walk from genesis | No breaks, no gaps |
| Verify signature | Check against public key | Valid |
| Tamper | Modify any field | Hash, chain, and signature all fail |

No theory. If the hashes match and the chain is intact, the system is working. If anything fails, the system detected it.
