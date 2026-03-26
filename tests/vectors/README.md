# Test Vectors

Deterministic test vectors for the RIO protocol. Implementations MUST produce identical outputs given identical inputs.

## Vector Files

| File | Type | Level | Description |
|------|------|-------|-------------|
| `public_key.pem` | Key | 1 | Ed25519 test public key (dedicated, deterministic from `SHA256(b'RIO_CONFORMANCE_TEST_SEED_v1')`) |
| `receipt_valid_approved.json` | Receipt | 1 | Complete valid receipt with `decision=allow` — all checks MUST pass |
| `receipt_valid_denied.json` | Receipt | 1 | Complete valid receipt with `decision=block` (INV-01 fail) — all checks MUST pass |
| `receipt_invalid_signature.json` | Receipt | 1 | Receipt with corrupted signature — signature check MUST fail |
| `receipt_invalid_hash.json` | Receipt | 1 | Receipt with corrupted receipt_hash — hash check MUST fail |
| `receipt_invalid_intent_hash.json` | Receipt | 1 | Receipt with corrupted request_hash — request hash and signature checks MUST fail |
| `receipt_missing_fields.json` | Receipt | 1 | Receipt with required fields removed — required-fields check MUST fail |
| `hash_computation_examples.json` | Examples | 1 | 7 worked hash examples — same inputs MUST produce same outputs |
| `signing_payload_examples.json` | Examples | 1 | 3 signing examples (allow, block, escalate) — all signatures verifiable with `public_key.pem` |
| `ledger_chain_valid.json` | Ledger | 2 | Valid ledger chain — all entries MUST have `chain_intact=True` |
| `ledger_chain_tampered.json` | Ledger | 2 | Ledger chain with tampered entry — chain integrity check MUST fail |
| `ledger_chain_deleted_entry.json` | Ledger | 2 | Ledger chain with deleted entry — chain integrity check MUST fail |

## Cryptographic Constants

| Constant | Value |
|----------|-------|
| Signature Algorithm | Ed25519 |
| Hash Algorithm | SHA-256 |
| Genesis Hash | `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a` |
| Test Public Key Fingerprint | `4bfae3c1edddbe967c69b94a0d49d9ecf197b24af7c4b9c1eb6440badbefd3ea` |

## Usage

These vectors are referenced by the conformance test suite in `../conformance/rio_conformance_suite_v1.json`. An implementation passes conformance when it reproduces all hashes and verifies all signatures using these vectors.

**Warning:** The test key in `public_key.pem` is a dedicated conformance test key. Never use it in production.
