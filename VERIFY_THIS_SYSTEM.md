# Verify This System

Everything you need is in this repository. No external repos, no accounts, no API keys.

**Time required:** under 5 minutes.

---

## Prerequisites

- Python 3.8+
- `pip install pynacl` (for Ed25519 signature verification)

---

## Step 1 — Verify a Valid Receipt

Load the valid receipt and confirm all required fields are present, the hash is correct, and the signature verifies.

```bash
python3 -c "
import json, hashlib, base64
from nacl.signing import VerifyKey

# Load test vectors
receipt = json.load(open('tests/vectors/receipt_valid_approved.json'))
pubkey_pem = open('tests/vectors/public_key.pem').read()

# 1. Check required fields
required = ['receipt_version','receipt_id','timestamp','runtime_id','runtime_version',
            'environment','request_summary','request_hash','request_canonical_payload',
            'policy_bundle_id','policy_bundle_hash','decision','decision_reason_codes',
            'invariant_results','threshold_results','model_output_hash',
            'model_output_preview','prev_ledger_hash','public_key_fingerprint',
            'receipt_hash','signature_algorithm','signature']
missing = [f for f in required if f not in receipt]
print(f'Required fields: {\"PASS\" if not missing else \"FAIL — missing: \" + str(missing)}')

# 2. Recompute receipt_hash from signed payload (all fields except receipt_hash, signature, signature_algorithm)
exclude = {'receipt_hash', 'signature', 'signature_algorithm'}
signed_payload = {k: v for k, v in receipt.items() if k not in exclude}
canonical = json.dumps(signed_payload, sort_keys=True, separators=(',', ':'))
computed_hash = hashlib.sha256(canonical.encode()).hexdigest()
print(f'Receipt hash:    {\"PASS\" if computed_hash == receipt[\"receipt_hash\"] else \"FAIL\"}')

# 3. Verify Ed25519 signature (extract 32-byte key from SPKI-encoded PEM)
der = base64.b64decode(pubkey_pem.strip().split('\n')[1])
raw_key = der[-32:]  # SPKI header is 12 bytes, raw Ed25519 key is last 32
vk = VerifyKey(raw_key)
sig = base64.b64decode(receipt['signature'])
try:
    vk.verify(canonical.encode(), sig)
    print('Signature:       PASS')
except Exception:
    print('Signature:       FAIL')
"
```

**Expected output:**
```
Required fields: PASS
Receipt hash:    PASS
Signature:       PASS
```

---

## Step 2 — Verify an Invalid Receipt Fails

Load a tampered receipt and confirm verification rejects it.

```bash
python3 -c "
import json, hashlib, base64
from nacl.signing import VerifyKey

raw = json.load(open('tests/vectors/receipt_invalid_signature.json'))
receipt = raw.get('receipt', raw)
pubkey_pem = open('tests/vectors/public_key.pem').read()

exclude = {'receipt_hash', 'signature', 'signature_algorithm'}
signed_payload = {k: v for k, v in receipt.items() if k not in exclude}
canonical = json.dumps(signed_payload, sort_keys=True, separators=(',', ':'))

der = base64.b64decode(pubkey_pem.strip().split('\n')[1])
raw_key = der[-32:]
vk = VerifyKey(raw_key)
sig = base64.b64decode(receipt['signature'])
try:
    vk.verify(canonical.encode(), sig)
    print('Signature: PASS (unexpected — this should fail)')
except Exception:
    print('Signature: FAIL (expected — tampered receipt correctly rejected)')
"
```

**Expected output:**
```
Signature: FAIL (expected — tampered receipt correctly rejected)
```

---

## Step 3 — Verify Ledger Chain Integrity

Walk the valid ledger chain and confirm every entry links correctly.

```bash
python3 -c "
import json, hashlib

ledger = json.load(open('tests/vectors/ledger_chain_valid.json'))
chain = ledger['chain']
genesis = chain['genesis_hash']

# Walk each entry and verify hash chain
prev_hash = genesis
i = 0
while f'entry_{i}' in chain:
    entry = chain[f'entry_{i}']
    assert entry['prev_ledger_hash'] == prev_hash, f'Entry {i}: prev_hash mismatch'
    recomputed = hashlib.sha256((entry['prev_ledger_hash'] + entry['receipt_hash']).encode()).hexdigest()
    assert recomputed == entry['current_ledger_hash'], f'Entry {i}: chain hash mismatch'
    prev_hash = entry['current_ledger_hash']
    i += 1
print(f'Ledger chain:    PASS ({i} entries verified)')
"
```

**Expected output:**
```
Ledger chain:    PASS (1 entries verified)
```

---

## Step 4 — Verify Tampered Ledger Fails

Load a tampered ledger and confirm the chain breaks.

```bash
python3 -c "
import json, hashlib

ledger = json.load(open('tests/vectors/ledger_chain_tampered.json'))
chain = ledger['chain']
genesis = chain['genesis_hash']

prev_hash = genesis
i = 0
while f'entry_{i}' in chain:
    entry = chain[f'entry_{i}']
    recomputed = hashlib.sha256((entry['prev_ledger_hash'] + entry['receipt_hash']).encode()).hexdigest()
    if recomputed != entry['current_ledger_hash']:
        print(f'Ledger chain:    FAIL at entry {i} (expected — tampering detected)')
        break
    prev_hash = entry['current_ledger_hash']
    i += 1
else:
    print('Ledger chain:    PASS (unexpected — tampered chain should fail)')
"
```

**Expected output:**
```
Ledger chain:    FAIL at entry 0 (expected — tampering detected)
```

---

## Step 5 — Verify Hash Computation

Reproduce a deterministic hash from the test vectors.

```bash
python3 -c "
import json, hashlib

examples = json.load(open('tests/vectors/hash_computation_examples.json'))['examples']
ex = examples[0]  # intent_hash_01
canonical = ex['canonical_json_string']
computed = hashlib.sha256(canonical.encode()).hexdigest()
print(f'Hash computation: {\"PASS\" if computed == ex[\"sha256_output\"] else \"FAIL\"}')
print(f'  Input:    {canonical[:60]}...')
print(f'  Expected: {ex[\"sha256_output\"]}')
print(f'  Got:      {computed}')
"
```

**Expected output:**
```
Hash computation: PASS
  Input:    {"context":{"tool":"evaluate_intent"},"disengage":false,"i...
  Expected: e3c092da91d60d828a23c5d4c832f4bab4029abbc665dbabf34e6ef455ad4ff4
  Got:      e3c092da91d60d828a23c5d4c832f4bab4029abbc665dbabf34e6ef455ad4ff4
```

---

## Summary

| Step | What you verified | Expected result |
|------|-------------------|-----------------|
| 1 | Valid receipt: fields, hash, signature | All PASS |
| 2 | Tampered receipt rejected | Signature FAIL |
| 3 | Valid ledger chain integrity | Chain PASS |
| 4 | Tampered ledger detected | Chain FAIL |
| 5 | Deterministic hash reproduction | Hash PASS |

If all five steps produce the expected output, the protocol artifacts in this repository are internally consistent and independently verifiable.

---

## Reference Files

| File | Purpose |
|------|---------|
| `tests/vectors/receipt_valid_approved.json` | Valid receipt (decision=allow) |
| `tests/vectors/receipt_invalid_signature.json` | Tampered receipt (corrupted signature) |
| `tests/vectors/ledger_chain_valid.json` | Valid hash-chained ledger |
| `tests/vectors/ledger_chain_tampered.json` | Tampered ledger (modified entry) |
| `tests/vectors/hash_computation_examples.json` | Deterministic hash test vectors |
| `tests/vectors/public_key.pem` | Ed25519 test public key |
| `spec/receipt_schema.json` | Receipt JSON Schema |
| `spec/receipt_protocol.md` | Receipt protocol specification |
| `spec/RIO_CONFORMANCE_v2.3.0.md` | Conformance levels (7 levels) |
