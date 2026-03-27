# RIO SDK — Developer Documentation

**Version:** 0.1.0
**Package:** `rio_sdk`
**Requirements:** Python 3.9+, `requests>=2.28`, `cryptography>=41.0`

---

## Installation

```bash
# From the rio-protocol repository root
cd rio_sdk && pip install -e .

# Or install dependencies directly
pip install requests cryptography
```

---

## Quick Start

```python
from rio_sdk import RIOClient, IntentBuilder, ReceiptVerifier, Ed25519Key

# Connect to the gateway
client = RIOClient("http://localhost:5000")

# Build and sign an intent
key = Ed25519Key.generate()
intent = (
    IntentBuilder("Summarise the Q3 financial report", key=key)
    .with_context(user_id="u-42", environment="staging")
    .build()
)

# Submit for governance evaluation
result = client.evaluate(intent)
print(result.receipt.decision)  # 'allow'

# Verify the receipt (7 checks)
verifier = ReceiptVerifier(client.public_key_pem())
verifier.assert_valid(result.receipt)  # raises if any check fails
print(verifier.verify(result.receipt).summary)  # '7/7 checks passed'
```

---

## Module Reference

### `rio_sdk.IntentBuilder`

Fluent builder for constructing signed intents.

```python
intent = (
    IntentBuilder("Your intent text")
    .with_key(key)                          # Ed25519Key for signing
    .with_context(user_id="u-42")           # Context fields
    .with_metadata(priority="high")         # Metadata fields
    .with_source("my-app")                  # Source identifier
    .with_model("claude")                   # Target model
    .disengage()                            # Skip signing (testing only)
    .build()                                # → Intent
)
```

### `rio_sdk.RIOClient`

HTTP client for all gateway endpoints.

| Method | Endpoint | Returns |
|--------|----------|---------|
| `evaluate(intent)` | `POST /v1/governance/evaluate` | `EvaluateResult` |
| `submit(intent)` | `POST /v1/governor/submit` | `GovernorSubmission` |
| `public_key_pem()` | `GET /v1/governance/public-key` | `str` (PEM) |
| `ledger_latest()` | `GET /v1/governance/ledger/latest` | `LedgerEntry` |
| `get_receipt(id)` | `GET /v1/governance/receipt/<id>/download` | `bytes` (ZIP) |
| `gate_execute(tool, payload)` | `POST /api/gate/execute` | `GateExecuteResult` |
| `gate_approve(id)` | `POST /api/gate/approve` | `dict` |
| `gate_reject(id, reason)` | `POST /api/gate/reject` | `dict` |
| `gate_pending()` | `GET /api/gate/pending` | `list` |
| `gate_audit_log()` | `GET /api/gate/audit-log` | `list` |
| `gate_config()` | `GET /api/gate/config` | `dict` |
| `ledger_full()` | `GET /api/audit-trail` | `list[LedgerEntry]` |
| `public_policy()` | `GET /api/policy/public` | `dict` |

### `rio_sdk.ReceiptVerifier`

7-check receipt verification against the protocol specification.

```python
verifier = ReceiptVerifier(public_key_pem)
result = verifier.verify(receipt)       # → VerificationResult
verifier.assert_valid(receipt)          # raises RIOVerificationError on failure
```

**Verification checks:**

1. `required_fields` — All 22 required fields present
2. `decision_valid` — Decision in `{allow, modify, block, escalate}`
3. `request_hash` — `SHA256(canonical_json(request_canonical_payload))`
4. `receipt_hash` — `SHA256(canonical_json({19 signed fields}))`
5. `signature` — `Ed25519.verify(base64_decode(signature), canonical_signed_payload)`
6. `public_key_fingerprint` — `SHA256(raw_32_byte_ed25519_public_key)`
7. `receipt_version` — Version in `{'1.0'}`

### `rio_sdk.LedgerVerifier`

Ledger chain integrity verification.

```python
result = LedgerVerifier.verify_chain(entries)   # → dict
LedgerVerifier.assert_chain_intact(entries)     # raises RIOLedgerError
found = LedgerVerifier.contains_receipt(entries, receipt_hash)
```

### `rio_sdk.LedgerClient`

High-level ledger operations.

```python
ledger = LedgerClient(client)
latest = ledger.latest()
result = ledger.verify_chain()
found = ledger.contains_receipt(receipt_hash)
stats = ledger.summary()
```

### `rio_sdk.Ed25519Key` / `rio_sdk.Ed25519Signer`

Ed25519 key management and signing.

```python
key = Ed25519Key.generate()
key = Ed25519Key.from_pem(pem_data)
key = Ed25519Key.from_file("private.pem")
key.save("private.pem", "public.pem")

signer = Ed25519Signer(key)
sig = signer.sign("message")
ok = signer.verify("message", sig)
sig = signer.sign_json({"key": "value"})
```

### `rio_sdk.ECDSAKey` / `rio_sdk.ECDSASigner`

ECDSA secp256k1 key management and signing.

```python
key = ECDSAKey.generate()
signer = ECDSASigner(key)
sig = signer.sign("message")
ok = signer.verify("message", sig)
```

---

## Exception Hierarchy

```
RIOError (base)
├── RIOConnectionError   — Cannot reach gateway
├── RIOHTTPError         — HTTP error with .status_code + .body
├── RIOIntentBlockedError — .receipt contains signed denial receipt
├── RIOVerificationError — 7-check verification failed
├── RIOLedgerError       — Chain formula verification failed
├── RIOApprovalError     — Human approval rejected or timed out
├── RIOKeyError          — Key management error
└── RIOConfigError       — SDK configuration error
```

---

## Data Models

| Class | Description |
|-------|-------------|
| `Intent` | Signed intent ready for submission |
| `Receipt` | Cryptographic receipt (22 fields, 19 signed) |
| `EvaluateResult` | Result from governance evaluation |
| `GovernorSubmission` | Result from governor submit (AWAITING_HUMAN_SIGNATURE) |
| `LedgerEntry` | Single ledger entry with chain linkage |
| `GateExecuteResult` | Result from gate execution |
| `VerificationResult` | 7-check verification result |
| `VerificationCheck` | Single verification check result |

---

## Examples

| Script | Description |
|--------|-------------|
| `examples/send_intent_example.py` | Full flow: evaluate → verify → ledger proof |
| `examples/governor_submit_example.py` | Human approval flow with polling |
| `examples/key_generation_example.py` | Ed25519 + ECDSA keygen, save/load, sign/verify |

---

## Receipt Format

The RIO v2 receipt contains **22 fields** total:

- **19 signed fields** — included in the canonical signed payload
- **3 extra fields** — `receipt_hash`, `signature_algorithm`, `signature`

The `receipt_hash` is computed as `SHA256(canonical_json({19 signed fields}))`.

The `signature` is `Ed25519.sign(canonical_json({19 signed fields}))`, base64-encoded.

---

## Ledger Chain Formula

```
genesis_hash = SHA256(b'GENESIS')
first_entry.prev_ledger_hash == genesis_hash
current_ledger_hash = SHA256((prev_ledger_hash + receipt_hash).encode('utf-8'))
```
