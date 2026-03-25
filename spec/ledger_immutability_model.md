# Ledger Immutability Model

**Version:** 1.0
**Status:** Active
**Author:** RIO Protocol Team
**Last Updated:** 2026-03-25

---

## Overview

The RIO audit ledger is the system's permanent, tamper-evident record of all governed actions. Every request that enters the protocol — whether approved, denied, or blocked — produces a cryptographic receipt that is appended to the ledger. Once written, a ledger entry cannot be modified, deleted, or reordered without detection.

This document explains how the ledger achieves immutability in practice, how receipts are signed, and how anyone can verify the integrity of the record at any time.

---

## Core Properties

The ledger guarantees four properties:

| Property | Description |
|----------|-------------|
| **Append-Only** | New entries are added to the end. No entry is ever updated or removed. |
| **Hash-Chained** | Each entry includes the hash of the previous entry, forming a chain. Changing any entry breaks all subsequent links. |
| **Signed** | Each entry and each receipt carry an RSA-PSS digital signature. Forging a signature requires the private key. |
| **Verifiable** | A standalone CLI tool can recompute every hash and verify every signature from the persisted files alone. |

---

## How the Hash Chain Works

Every ledger entry contains a field called `previous_ledger_hash`. This field holds the `ledger_hash` of the entry immediately before it. The very first entry in a chain has an empty `previous_ledger_hash` (the genesis entry).

The `ledger_hash` itself is computed as:

```
entry_hash = SHA-256(
    entry_id +
    receipt_id +
    receipt_hash +
    request_id +
    intent_id +
    authorization_id +
    decision +
    action +
    result_hash +
    receipt_signature +
    previous_hash +
    timestamp
)
```

Because each entry's hash includes the previous entry's hash, changing any single field in any entry causes a cascade of mismatches through the rest of the chain. This is the same principle used in blockchain systems, applied here to a local append-only file.

### Visual Representation

```
 ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │   Entry 0    │     │   Entry 1    │     │   Entry 2    │
 │  (genesis)   │     │              │     │              │
 │              │     │              │     │              │
 │ prev_hash="" │────▶│ prev_hash=   │────▶│ prev_hash=   │
 │ hash=A1B2... │     │   A1B2...    │     │   C3D4...    │
 │ sig=RSA(...) │     │ hash=C3D4... │     │ hash=E5F6... │
 └──────────────┘     │ sig=RSA(...) │     │ sig=RSA(...) │
                      └──────────────┘     └──────────────┘
```

If Entry 1 is tampered with, its recomputed hash will differ from `C3D4...`, and Entry 2's `prev_hash` will no longer match.

---

## How Receipt Signing Works

Every receipt is signed with an RSA-2048 private key using the RSA-PSS signature scheme with SHA-256.

### Key Pair

The system uses a single RSA-2048 key pair stored at:

- **Private key:** `runtime/keys/private_key.pem` — used to sign receipts and ledger entries. Must be kept secure.
- **Public key:** `runtime/keys/public_key.pem` — used to verify signatures. Can be shared freely.

If the key files do not exist when the system starts, a new key pair is generated automatically.

### Signing Process

1. The receipt is generated with all fields populated (receipt_id, request_id, intent_id, authorization_id, decision, action_type, execution_status, execution_timestamp, result_hash).
2. A canonical JSON representation of these fields is created (sorted keys, deterministic).
3. The receipt hash is computed: `receipt_hash = SHA-256(canonical_json + previous_receipt_hash)`.
4. The receipt hash is signed: `signature = RSA-PSS-Sign(private_key, receipt_hash)`.
5. The signature is stored as a base64-encoded string in the receipt's `signature` field.

### Ledger Entry Signing

Ledger entries follow the same pattern:

1. The entry hash is computed from all fields (see formula above).
2. The entry hash is signed: `ledger_signature = RSA-PSS-Sign(private_key, ledger_hash)`.
3. The signature is stored as a base64-encoded string.

---

## What Tampering Looks Like

The verification system detects four types of tampering:

### 1. Modified Entry

If any field in a ledger entry is changed (e.g., changing a decision from `DENY` to `ALLOW`), the recomputed hash will not match the stored `ledger_hash`. The verification CLI reports:

```
Entry 104 hash mismatch — expected a1b2c3..., got d4e5f6...
```

### 2. Deleted Entry

If an entry is removed from the middle of the chain, the next entry's `previous_ledger_hash` will point to a hash that no longer exists in the expected position. The verification CLI reports:

```
Entry 104 chain broken — expected previous a1b2c3..., got d4e5f6...
```

### 3. Reordered Entries

If entries are swapped, the hash chain breaks at both positions because the `previous_ledger_hash` links no longer match.

### 4. Forged Signature

If someone modifies an entry and recomputes the hash (to avoid hash mismatch detection), the RSA-PSS signature will not match the new hash. Only the holder of the private key can produce a valid signature. The verification CLI reports:

```
Entry 104 signature INVALID
```

---

## Verification

### CLI Command

Run the full integrity check at any time:

```bash
python -m runtime.verify_ledger
```

### What It Checks

The verification CLI performs five categories of checks:

| Check | Description |
|-------|-------------|
| **ledger_hash** | Recomputes each entry's hash and compares to the stored value |
| **hash_chain** | Verifies that each entry's `previous_ledger_hash` matches the preceding entry's `ledger_hash` |
| **ledger_signature** | Verifies the RSA-PSS signature on each ledger entry using the public key |
| **receipt_hash** | Recomputes each receipt's hash and compares to the stored value |
| **receipt_signature** | Verifies the RSA-PSS signature on each receipt using the public key |

### Output

A passing verification looks like:

```
======================================================================
RIO LEDGER VERIFICATION
======================================================================
  [PASS] ledger_hash: 27/27 passed
  [PASS] hash_chain: 27/27 passed
  [PASS] ledger_signature: 27/27 passed
  [PASS] receipt_hash: 27/27 passed
  [PASS] receipt_signature: 27/27 passed
----------------------------------------------------------------------
Ledger verification: PASS — 135 checks passed
----------------------------------------------------------------------
```

A failing verification identifies the exact entry and type of failure:

```
  [FAIL] ledger_hash: 26/27 passed
         FAIL: Entry 15 hash mismatch — expected a1b2c3..., got d4e5f6...
```

### Exit Codes

- **0** — All checks passed
- **1** — One or more checks failed

---

## Data Files

| File | Format | Purpose |
|------|--------|---------|
| `runtime/data/ledger.jsonl` | JSON Lines (append-only) | The audit ledger — one JSON object per line |
| `runtime/data/receipts.jsonl` | JSON Lines (append-only) | All cryptographic receipts |
| `runtime/keys/private_key.pem` | PEM (RSA-2048) | Private key for signing (keep secure) |
| `runtime/keys/public_key.pem` | PEM (RSA-2048) | Public key for verification (shareable) |

---

## Security Considerations

1. **Private key protection.** The private key must be protected. Anyone with access to the private key can forge signatures. In production, the key should be stored in a hardware security module (HSM) or secure key management service.

2. **File system access.** The JSONL files are stored on the local file system. An attacker with write access to both the files and the private key could forge a consistent chain. The verification CLI detects tampering only when the attacker does not have the private key.

3. **External anchoring.** For stronger guarantees, periodic ledger hashes can be published to an external system (e.g., a public blockchain, a notary service, or a write-once storage system). This creates an external anchor that cannot be altered even if the local system is compromised.

4. **Key rotation.** If the private key is compromised, a new key pair should be generated. The verification CLI should be updated to accept multiple public keys for different time periods.

---

## Related Invariants

| Invariant | Description |
|-----------|-------------|
| **INV-02** | Receipt Completeness — every action produces a receipt |
| **INV-03** | Ledger Completeness — every receipt is recorded in the ledger |
| **INV-04** | Hash Chain Integrity — the ledger hash chain is unbroken |

---

## Summary

The RIO audit ledger is:

- **Append-only** — entries are never modified or deleted
- **Hash-chained** — each entry is linked to the previous one by hash
- **Signed** — each receipt and ledger entry carries an RSA-PSS signature
- **Tamper-detectable** — any modification, deletion, or reordering is caught by the verification CLI
- **Independently verifiable** — anyone with the public key and the JSONL files can verify the entire record

This ensures that what was approved, what was executed, and what was recorded can always be proven authentic and unaltered.
