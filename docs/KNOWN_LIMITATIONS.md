# Known Limitations — RIO Protocol v1.0

This document states what the protocol and this repository do not provide. These are not planned features. They are boundaries of the current system.

---

## No production execution gate

This repository defines the protocol specification and reference verification logic. It does not contain a production-ready execution gate. The gate behavior is specified in `spec/RIO_Protocol_Specification_v1.0.md`, but a production implementation must be built separately. The reference implementation is in [rio-reference-impl](https://github.com/bkr1297-RIO/rio-reference-impl).

## No identity system

RIO does not define or provide an identity management system. The protocol references agent identifiers, public keys, and key fingerprints, but does not specify how identities are provisioned, rotated, or revoked. Implementations must supply their own identity infrastructure.

## No distributed ledger

The hash-chained ledger defined in this protocol is a single-writer, append-only log. It is not a distributed ledger, blockchain, or consensus-based system. There is no peer-to-peer replication, no multi-party consensus, and no Byzantine fault tolerance. Ledger integrity depends on the hash chain and signature verification, not on distributed agreement.

## No execution guarantees outside the system

A receipt proves that the system recorded a governed action. It does not prove that the action occurred in the external world. If the execution target (an API, a database, a physical system) fails silently or returns a false success, the receipt will reflect what the system observed, not what actually happened. External verification is outside the protocol's scope.

## No real-time monitoring

The protocol defines post-hoc verification: an auditor can verify receipts and the ledger after the fact. It does not define real-time monitoring, alerting, or streaming verification. Implementations that require real-time oversight must build that layer separately.

## No key management

The protocol specifies Ed25519 for receipt signing and ECDSA-secp256k1 for gateway tokens. It does not specify how private keys are generated, stored, rotated, or protected. Production deployments should use hardware security modules (HSMs) or equivalent secure key storage.

## No multi-tenancy

The protocol does not define tenant isolation, access control between organizations, or shared ledger partitioning. Each deployment is assumed to be a single-tenant system.

## Test vectors are not exhaustive

The conformance test suite covers the core verification paths (receipt validation, hash reproduction, signature verification, ledger chain integrity). It does not cover every possible edge case, malformed input, or adversarial scenario. Implementations should supplement the provided vectors with their own test coverage.
