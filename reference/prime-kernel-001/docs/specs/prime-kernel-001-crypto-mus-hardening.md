# PRIME-KERNEL-001 — Crypto + MUS Hardening v0.2

Status: reference hardening candidate; not production key custody.

## Purpose

This hardening pass replaces deterministic mock signature checks with real Ed25519 SourcePoint verification and adds MUS-style signed, hash-linked receipts.

## Hardened flow

```text
Prime Packet
→ canonical JSON signing payload
→ SourcePoint Ed25519 verification
→ non-compensatory validator
→ MUS signed receipt
→ receipt hash chain
→ return path
```

## What is now tested

- valid SourcePoint signature verifies
- packet tampering after signing fails
- invalid signature blocks
- draft_only cannot send externally
- CAN cannot become MAY permission
- MUS receipt signs and verifies
- MUS receipt tamper fails
- MUS receipt chain verifies previous hash linkage
- ORGA validates through gate before act

## Remaining boundary

This proves the reference shape. Production use still requires durable key custody, nonce registry, ledger persistence, revocation checking, and real integration with the active MUS ledger implementation.
