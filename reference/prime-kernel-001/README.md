# PRIME-KERNEL-001 — Repo-Safe Candidate v0.1

This directory contains a corrected, repo-safe candidate implementation of **PRIME-KERNEL-001 — Constitutional Crossing Language Kernel v0.1**.

It is not canon code yet. It is the first implementation scaffold for review, testing, and later integration with real cryptographic verification and the MUS receipt layer.

## Why this lives here

This repository is the canonical RIO protocol/specification repo. PRIME-KERNEL-001 is being staged here as a reference candidate because it defines a constitutional crossing language kernel that can compile into schemas, validators, conformance tests, and receipt mappings.

## What it implements

- Prime Packet types
- Normative operator rules
- State transition matrix
- Non-compensatory validator
- ORGA typestate loop scaffold
- Receipt mapping
- Runnable tests
- Example `.prime.json` packets

## What it intentionally does not include

- No unverified Sanskrit labels in production comments
- No Hohfeldian advanced policy layer
- No casual `bypassed` gate state
- No model-based authorization
- No hidden learning updates
- No production cryptography; signatures and hashes are mocked for deterministic local tests

## Run locally

```bash
cd reference/prime-kernel-001
npm install
npm test
```

The tests prove the key v0.1 invariant:

> Prime Kernel becomes real when invalid transitions fail closed in tests.

## Repo placement

- Protocol spec mirror: `spec/PRIME_KERNEL_001.md`
- Candidate implementation: `reference/prime-kernel-001/`

## Boundary

This package is a reference candidate. It does not claim production readiness, live conformance, real cryptographic enforcement, or final SourcePoint ratification.
