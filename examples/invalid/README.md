# Invalid Examples

These artifacts are intentionally malformed to trigger specific error codes from the [Error Vocabulary v1.0](../../spec/error_vocabulary.v1.json).

| File | Error Code | What Is Wrong |
|------|------------|---------------|
| `hash_mismatch_receipt.json` | `HASH_MISMATCH` | `receipt_hash` is zeroed and does not match the hash of the signed fields |
| `chain_broken_ledger.json` | `CHAIN_BROKEN` | Entry 2 `prev_ledger_hash` does not match entry 1 `current_ledger_hash` |
| `missing_field_receipt.json` | `MISSING_FIELD` | `receipt_hash`, `signature`, and `public_key_fingerprint` are absent |

Each file includes an `_expected_result` object showing the structured verifier output that a conformant implementation must produce.
