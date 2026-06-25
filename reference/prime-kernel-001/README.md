# PRIME-KERNEL-001 — Real Crypto + MUS Integration Candidate v0.2

This bundle hardens the PRIME-KERNEL-001 reference candidate by replacing mock SourcePoint signature checks with real Ed25519 verification and adding MUS-style signed, hash-linked receipt objects.

## Boundary

This is still a reference candidate. It demonstrates the crypto/MUS integration path, but it is not production key management, not a live authority system, and not final canon.

## What changed from v0.1

- Ed25519 SourcePoint signatures verify over canonicalized Prime Packet signing payloads.
- Prime packets include `sourcepoint_public_key_pem` in the Authority Envelope for reference verification.
- Deterministic canonical JSON is used before hashing/signing.
- MUS receipts include packet hash, result hash, previous receipt hash, receipt hash, and Ed25519 receipt signature.
- Tests prove valid allow path, invalid signature block, tamper detection, receipt signature verification, and hash-chain linking.

## Run

```bash
npm run test
```

Expected final line:

```text
All PRIME-KERNEL-001 real crypto + MUS tests passed.
```
