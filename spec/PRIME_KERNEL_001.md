# PRIME-KERNEL-001 — Constitutional Crossing Language Kernel v0.1

Status: merged candidate material on `main`; SourcePoint review remains required before any promotion or canon decision.

## Core invariant

No transition is valid unless authority, scope, operator, gate path, effect, receipt, and return are explicitly declared.

If the declared effect exceeds the authority grant, the packet fails closed.

## Implementation note

This bundle implements the v0.1 kernel in TypeScript with deterministic local checks. Cryptographic signature and payload hash checks are mocked for local test determinism and must be replaced with real verification before production.

## Reference candidate

The candidate implementation lives under:

```text
reference/prime-kernel-001/
```

## Boundary

Prime Kernel v0.1 is a constitutional crossing language kernel candidate. Grammar validity does not imply action permission. Capability does not imply permission. Receipts prove authorization/execution/failure evidence, not business correctness.
