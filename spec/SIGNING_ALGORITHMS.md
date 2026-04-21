# RIO Signing Algorithms

> This document defines the cryptographic signing algorithms used across the RIO protocol.

---

## Dual-Signing Architecture

RIO uses two distinct signing algorithms, each scoped to a specific layer:

| Layer | Algorithm | Scope |
|-------|-----------|-------|
| Receipt + Ledger | **Ed25519** | Receipt signing, receipt hash verification, ledger chain integrity |
| Gateway (if present) | **ECDSA-secp256k1** | Intent/token signing at the gateway layer |

---

## Receipt and Ledger Layer — Ed25519

All receipts and ledger entries are signed using **Ed25519**.

- **Signing payload:** All receipt fields except `receipt_hash`, `signature`, and `signature_algorithm`, serialized as canonical JSON (`sort_keys=True`, `separators=(',', ':')`)
- **receipt_hash:** `SHA-256(canonical_json(signed_fields))`
- **signature:** Ed25519 signature over the canonical JSON bytes
- **Public key format:** SPKI-encoded PEM; raw 32-byte Ed25519 key at the last 32 bytes of the DER-decoded payload

This layer defines:

- Receipt structure
- Ledger semantics
- Protocol conformance

---

## Gateway Layer — ECDSA-secp256k1

If a gateway layer is present, it uses **ECDSA-secp256k1** for intent and token signing.

The gateway layer does **NOT** define:

- Receipt structure
- Ledger semantics
- Protocol conformance

Gateway signing is independent of the receipt/ledger proof chain. Gateway tokens are consumed at the execution gate and do not appear in the receipt or ledger.

---

## Boundary Rule

These two signing layers are separate. No gateway-layer artifact redefines or overrides any receipt, ledger, or conformance semantic defined in the protocol specification.
