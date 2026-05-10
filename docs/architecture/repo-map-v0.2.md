# RIO Repository Estate Map v0.2

> Last updated: 2026-05-10
> Maintainer: Brian Rasmussen

This document maps the full repository estate for the RIO governed intelligence ecosystem. It defines what each repository is, what it does, its canonical status, and what it does not claim.

---

## Core Public Repositories

These are the canonical, maintained public repositories that define the RIO protocol, proof layer, and governance specification.

### `rio-protocol`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Canonical protocol specification and conformance source |
| Type | Specification / Conformance |
| License | All Rights Reserved (Apache 2.0 pending) |
| Proves | Protocol definition, non-collapse conformance rules, governance architecture |
| Does not claim | Runtime enforcement, live conformance, production readiness |
| Status | Active — canonical |

### `rio-receipt-protocol`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Proof primitive — local receipt engine and verification spec |
| Type | Specification / Proof |
| License | MIT |
| Proves | Receipt structure, hash-chain integrity, independent verification |
| Does not claim | Live receipt verification in production, full system integration |
| Status | Active — canonical |

### `rio-system`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Observation layer — MANTIS system documentation |
| Type | Specification / Observation |
| License | MIT |
| Proves | Observation architecture, system boundary definitions |
| Does not claim | Runtime enforcement, production deployment |
| Status | Active — canonical |

### `language-intake-mvp`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Language governance — crossing detection prototype |
| Type | Proof / Prototype |
| License | No root LICENSE file (cleanup needed) |
| Proves | Crossing-type detection (helpfulness→delegation, advice→instruction, etc.) |
| Does not claim | Production readiness, runtime enforcement, full coverage |
| Status | Active — canonical prototype (v0.1.2) |

---

## Legacy / Interlock Public Repositories

These repositories predate the current canonical structure. They may contain early-stage thinking, superseded architectures, or demonstration material.

### `one-consent`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | SMS consent and opt-in page for One Governed AI |
| Type | Demo / Utility |
| License | No root LICENSE file detected |
| Proves | Consent flow concept |
| Does not claim | Protocol-level governance |
| Status | Active — utility, not canonical |

### `sovereignty-stack-demo`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Demonstration of sovereign stack governed execution |
| Type | Demo |
| License | No root LICENSE file detected |
| Proves | Concept demonstration of cryptographic guarantees and human-validated actions |
| Does not claim | Production readiness, current architecture |
| Status | Legacy — may be superseded by rio-protocol conformance bundle |

### `rio-legacy-protocol`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Earlier version of receipt protocol documentation |
| Type | Legacy |
| License | Unknown |
| Proves | Historical record of protocol evolution |
| Does not claim | Current canonical status |
| Status | Legacy — superseded by `rio-receipt-protocol` |

### `rio-hash-interlock-hash-system`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Hash interlock system governed by RIO control plane |
| Type | Legacy / Interlock |
| License | Unknown |
| Proves | Hash interlock concept |
| Does not claim | Current canonical status |
| Status | Legacy — superseded by current protocol architecture |

### `RIO-Interlock-System`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Governance framework for human-AI interaction preventing silent authority transfer |
| Type | Legacy / Specification |
| License | Unknown |
| Proves | Early interlock architecture, authority transfer prevention concepts |
| Does not claim | Current canonical status |
| Status | Legacy — concepts absorbed into rio-protocol |

### `AI-Structural-Limitations-of-the-dyad`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Research paper / position document on two-party governance failures |
| Type | Research / Position |
| License | Unknown |
| Proves | Structural argument for why dyadic human-AI systems require third-party governance |
| Does not claim | Protocol implementation |
| Status | Active — standalone research artifact |

### `rio-interlock`

| Field | Value |
|-------|-------|
| Visibility | Public |
| Role | Human-preserving AI governance interlock |
| Type | Legacy / Interlock |
| License | Unknown |
| Proves | Early interlock design |
| Does not claim | Current canonical status |
| Status | Legacy — superseded by current protocol architecture |

---

## Private / Product / Runtime Repositories

These repositories contain proprietary implementation, tooling, and runtime code. They are not publicly accessible and are not open-source.

### `rio-proxy`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Governed execution runtime — the ONE Command Center |
| Type | Runtime / Product |
| License | Proprietary |
| Status | Active — canonical runtime |

### `rio-proxy-manus`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Manus working/checkpoint mirror |
| Type | Workspace |
| License | Proprietary |
| Status | Active — NOT canonical (mirror/checkpoint only) |

### `rio-reference-impl`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Reference implementation of the RIO Governance Protocol |
| Type | Runtime / Reference |
| License | Proprietary |
| Status | Active |

### `rio-tools`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Developer tools — SDKs, simulator, verifier CLI, compliance checker |
| Type | Tooling |
| License | Proprietary |
| Status | Active |

### `rio-programs`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Coordination layer — program roles, shared state model, orchestration patterns |
| Type | Runtime / Coordination |
| License | Proprietary |
| Status | Active |

### `rio-protocol-v1`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Earlier private protocol version |
| Type | Legacy / Private |
| License | Proprietary |
| Status | Legacy — superseded by public rio-protocol |

### `rio-demo-site`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Ask Bondi — RIO Receipt Protocol Implementation Assistant |
| Type | Demo / Internal |
| License | Proprietary |
| Status | Active — internal demo |

### `email-compliance-wrapper`

| Field | Value |
|-------|-------|
| Visibility | Private |
| Role | Email compliance wrapper |
| Type | Utility |
| License | Proprietary |
| Status | Active |

---

## Canonical Hierarchy

The following hierarchy defines the authoritative source for each layer of the RIO ecosystem:

1. **`rio-protocol`** — Canonical protocol specification and conformance source
2. **`rio-receipt-protocol`** — Proof primitive / local receipt engine
3. **`rio-system`** — Observation / MANTIS layer
4. **`language-intake-mvp`** — Language governance / crossing detection prototype
5. **`rio-proxy`** — Private governed execution runtime (ONE Command Center)
6. **`rio-proxy-manus`** — Manus working/checkpoint mirror (not canonical)
7. **`rio-tools`** — Private developer tooling
8. **`rio-reference-impl`** — Private reference implementation

---

## What This Map Does Not Cover

- Trust/legal entity structure
- Deployment infrastructure
- CI/CD configuration
- Partner access arrangements
- Future repo creation plans
