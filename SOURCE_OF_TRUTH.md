# RIO Source of Truth — v0.1

Status: Canonical repository status  
Date: 2026-05-04  
Repo: bkr1297-RIO/rio-protocol  
Purpose: Define what is currently true about RIO after the completed protocol merges.

---

## 1. Current Source of Truth

The canonical source-of-truth repo for the RIO protocol is:

bkr1297-RIO/rio-protocol

This repo now contains the protocol definition, operating specification, state machine, syscall surface, verification stack, runtime test outline, glossary, overview, and minimal conformance example.

---

## 2. What Is Now True

RIO now has a canonical protocol documentation baseline.

That means the protocol can be read, inspected, compared against implementation, and tested against declared conformance expectations.

The protocol baseline includes:

- protocol definition
- canonical glossary
- operating specification
- governed action state machine
- syscall/interface surface
- runtime conformance test outline
- verification stack
- reviewer-facing overview
- minimal conformance example

---

## 3. What This Means

RIO is now documented as a complete protocol claim.

A reviewer can now ask:

"What is RIO supposed to do?"

And the answer can point to rio-protocol.

A reviewer can now ask:

"What states exist?"

And the answer can point to the state machine schema.

A reviewer can now ask:

"What calls exist?"

And the answer can point to the syscall spec.

A reviewer can now ask:

"How is proof separated from verification?"

And the answer can point to the verification stack.

A reviewer can now ask:

"What would conformance look like?"

And the answer can point to the runtime test outline and minimal example.

---

## 4. What Is Not Yet True

This does not mean RIO is finished.

This does not mean RIO is externally validated.

This does not mean RIO is production-ready.

This does not mean all runtime gaps are closed.

This does not mean Chronicle is implemented.

This does not mean every receipt is fully signed and independently re-verifiable.

This does not mean the protocol is a recognized public standard.

---

## 5. Current Honest Status

RIO has crossed from scattered architecture and implementation evidence into a canonical protocol baseline.

The current status is:

Canonical protocol documented. Runtime conformance still requires continued verification. External validation has not yet occurred.

---

## 6. Canonical Files

The current canonical protocol set includes:

- docs/architecture/protocol-definition-v0.1.md
- docs/architecture/glossary-v0.1.md
- spec/rio-operating-spec-v0.1.md
- schemas/rio-state-machine-v0.1.json
- spec/rio-syscalls-v0.1.md
- tests/rio-operating-spec-runtime-tests-v0.1.md
- spec/rio-verification-stack-v0.1.md
- docs/README.md
- docs/architecture/rio-protocol-overview.md
- examples/minimal-conformance-example.md

---

## 7. One-Sentence Summary

RIO now has a canonical protocol baseline in rio-protocol: defined, structured, inspectable, testable, and explainable — but not yet externally validated or production-complete.

---
