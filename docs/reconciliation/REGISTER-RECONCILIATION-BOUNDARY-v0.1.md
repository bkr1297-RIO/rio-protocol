# Cross-Register Reconciliation Boundary

## Status

- **Classification:** protocol navigation and boundary note
- **Standing:** informative
- **Authority:** the authoritative RIO protocol standard remains authoritative for RIO protocol semantics
- **Runtime effect:** none by placement alone

## Purpose

The architecture repository now holds the cross-register reconciliation bridge:

- [Register Reconciliation and Developer Loom](https://github.com/bkr1297-RIO/one-rio-muss-architecture/blob/docs/architecture-repo-bootstrap/docs/reconciliation/README.md)
- [REAL Intelligence ↔ ONE Grammar ↔ RIO Matrix v0.2](https://github.com/bkr1297-RIO/one-rio-muss-architecture/blob/docs/architecture-repo-bootstrap/docs/reconciliation/REAL-ONE-RIO-REGISTER-PROJECTION-STANDING-MATRIX-v0.2.md)

This note tells protocol contributors how to use that bridge without copying it into the protocol repository or treating it as a replacement for the RIO standard.

## RIO's declared jurisdiction

This repository owns:

- protocol objects and state transitions;
- authorization and policy semantics;
- schemas and conformance profiles;
- protocol error and refusal behavior;
- protocol-level security and threat boundaries.

The reconciliation matrix owns the cross-register map. It does not amend RIO, create a new protocol version, or make a semantic candidate protocol-active.

## Boundary rule

For any proposed RIO object:

1. locate the concept in the reconciliation matrix;
2. confirm its semantic identity and standing;
3. declare the protocol projection and authority boundary;
4. specify predecessor/successor, refusal, expiry, and receipt behavior;
5. add schema and negative conformance fixtures;
6. update the owning protocol source and record the cross-register relation.

A protocol object is a projection of a governed concept. It is not the concept's constitutional identity.

## Important claim boundaries

- A protocol schema is not a complete implementation.
- A passing conformance test is bounded to its named profile.
- A gate receipt records a decision; it does not itself confer execution authority.
- A transition receipt records an attestation; it does not establish world truth.
- Closure Attestation remains a candidate bridge specification until its prerequisites and fixtures are adopted.
- Sentinel Core is a bounded developer/verification profile, not a replacement for RIO.

## Developer route

Use this sequence when building or reviewing a protocol feature:

```text
Matrix row
  → semantic object and standing
  → RIO protocol object/state
  → schema and conformance fixtures
  → runtime binding
  → receipt / ledger / return evidence
```

If the proposed feature cannot identify its owner, standing, projection, authority boundary, and evidence claim, it is not ready to become an active protocol surface.
