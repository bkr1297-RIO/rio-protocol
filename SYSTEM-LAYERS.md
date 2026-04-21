# System Layers Map

This document explains how the RIO ecosystem is organized.

---

## Layer 0 — Standard (Normative)

Defines how governance and proof must work.

- RIO specification
- Receipt protocol specification
- Conformance specification
- JSON schemas and test vectors

These are the protocol contract. Conformance is measured against this layer.

---

## Layer 1 — Infrastructure (Reference Implementation)

Implements the execution boundary, receipts, and ledger in code that conforms to the standards.

- Execution Gate implementation
- Receipt and ledger implementation
- Core libraries and services providing the governed execution boundary

---

## Layer 2 — Skills (Non-normative Usage)

Defines how humans and agents use RIO safely.

Skills are bounded capabilities such as:

- clarifying intent
- checking admissibility via the Gate
- querying receipts and ledger
- building and operating within constraints

Skills are non-normative and have no authority over execution, authorization, or protocol conformance.

For high-stakes actions, multi-agent review may be used to improve decision quality. This does not replace RIO execution control or affect conformance.

---

## Layer 3 — Systems (Built on RIO)

Applications that use the standards (Layer 0), infrastructure (Layer 1), and skills (Layer 2) to deliver capabilities in the world.

Examples:

- ONE
- MANTIS
- Fiduciary systems and agents built on RIO

---

## One line

Standards define how governance and proof must work.
Infrastructure enforces those rules.
Skills guide how the system is used.
Systems express purpose within those boundaries.
