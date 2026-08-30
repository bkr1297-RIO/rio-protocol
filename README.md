# RIO Protocol

**Project protocol/specification for governed AI-mediated action**

> **Repository role:** project-level normative protocol and conformance materials  
> **Actual license:** All Rights Reserved; see [`LICENSE`](LICENSE)  
> **Not claimed:** adopted external standard, legal or regulatory compliance, official certification, production readiness, public reuse permission, or whole-system runtime proof

RIO describes how a proposed machine-mediated action may be evaluated against authority, scope, consequence, verification, receipt, and return requirements.

> **RIO governs consequential crossing. Receipts record what the governed system reports happened.**

A receipt may establish the integrity and relationships of the represented record. It does not independently prove that an external-world event occurred or that the underlying authority was lawful.

---

## Relationship to other protocols

RIO is intended to complement model/tool and agent-coordination protocols:

- MCP can expose tools to models.
- A2A can coordinate agent communication.
- RIO defines a project protocol for governing what a proposed exchange may become under human or organizational authority.

This repository does not claim formal adoption by MCP, A2A, an external standards body, a regulator, or an industry consortium.

---

## Current status vocabulary

Use these distinctions when reading the repository:

```text
project normative specification
≠ adopted public standard

conformance to a named profile
≠ legal or regulatory compliance

passing local vectors
≠ production enforcement

cryptographic verification
≠ external-world truth

certification materials
≠ issued certification authority

public repository visibility
≠ public reuse license
```

---

## What this repository contains

- project protocol specifications;
- JSON schemas;
- error vocabularies;
- conformance profiles and vectors;
- reference verification code;
- threat and trust-model documents;
- governance and change-process materials;
- examples and demonstrations.

Within the RIO project, the versioned normative artifacts in this repository govern the protocol profile they explicitly define. That project-internal precedence does not make the repository an adopted external standard or the authority for the broader ONE/RIO/MUSS constitutional architecture.

Current version labels found in the repository include:

```text
protocol family: v1.0.0
error vocabulary: v1.0
conformance profile: v2.3.0
non-collapse bundle: v0.1.3
```

Each artifact’s own status and version control its scope. These labels should not be collapsed into one blanket release status.

---

## Non-Collapse Conformance

The Non-Collapse Conformance Bundle v0.1.3 is a synthetic docs/tests baseline for checking whether systems preserve category boundaries such as:

- memory ≠ consent;
- access ≠ authority;
- confidence ≠ truth;
- learning ≠ permission;
- capability ≠ action;
- observation ≠ judgment;
- proof ≠ meaning;
- key possession ≠ current authority or conformance;
- model agreement ≠ proof;
- helpfulness ≠ permission.

Accepted evidence posture:

```text
proof_status_label: negative_run_validated
runtime_status: not_enforced
live_conformance_status: not_claimed
receipt_verified: not_claimed
```

This bundle does not claim live conformance, runtime enforcement, receipt verification, certification, or production readiness.

---

## Project protocol and conformance documents

| Document | Role |
|---|---|
| `spec/RIO_STANDARD_v1.0.md` | Historical/project-named normative specification; not an adopted external standard by title alone |
| `legacy/spec-v1-drafts/RIO_Protocol_Specification_v1.0.md` | Preserved historical protocol draft; its legacy location does not make it a current controlling specification |
| `spec/RIO_CONFORMANCE_v2.3.0.md` | Named technical conformance profile |
| `spec/error_vocabulary.v1.json` | Versioned project error vocabulary |
| `spec/error_vocabulary.md` | Error-vocabulary versioning rules |
| `VERIFY_THIS_SYSTEM.md` | Local verification guide |

The word `STANDARD` in an existing filename is retained for compatibility and history. Public-facing claims should describe it as a **project normative specification** unless and until an external adoption process is established and named.

Use **conformance** for technical agreement with a named profile. Do not describe a passing technical profile as legal, regulatory, security, or organizational compliance.

---

## Verification boundaries

The repository includes methods for checking properties such as:

- required record fields;
- receipt hashes;
- digital signatures;
- ledger linkage;
- nonce reuse;
- token expiry;
- intent/action/verification hash relationships;
- expected fail-closed results in represented tests.

A successful verification result means only that the named verifier found the represented property valid under the named version, inputs, and environment.

It does not independently establish:

- lawful authority;
- authentic human consent;
- external-world execution;
- production deployment;
- resistance to every attack;
- legal or regulatory compliance;
- certification.

---

## Bounded protocol properties

Earlier README language described several properties as universal “guarantees.” The current safe treatment is narrower:

| Required or demonstrated property | Named mechanism | Evidence boundary |
|---|---|---|
| Requests without a valid token are rejected in the represented gate path | fail-closed token check | Named implementation/test only |
| Ledger alteration is detectable under the declared hash-chain algorithm | hash linkage | Integrity of represented records only |
| Invalid signatures are rejected under the declared verifier | Ed25519/ECDSA verification | Key and implementation assumptions apply |
| Used nonces are rejected under the declared registry | nonce tracking | Named runtime/profile only |
| Expired tokens are rejected under the declared TTL rules | time-bound token validation | Clock and implementation assumptions apply |
| Denial records can be retained and queried | denial receipts and ledger | Availability/retention depend on implementation |
| Intent/action/result drift can be surfaced | hash/reference comparison | Does not independently prove external truth |

These are protocol requirements or locally demonstrated properties—not unconditional whole-system guarantees.

---

## Governed execution lifecycle

A representative project lifecycle is:

1. intake and origin recording;
2. structured intent construction;
3. risk and consequence evaluation;
4. policy and scope checks;
5. authorization or review;
6. bounded execution or refusal;
7. receipt and ledger recording;
8. verification and governed return.

Implementations may realize this lifecycle differently, but conformance claims must name the exact profile and version tested.

Learning or policy-improvement loops may propose changes. They must not bypass governance, auto-expand authority, or execute directly.

---

## Repository relationships

| Repository | Current bounded role |
|---|---|
| `rio-protocol` | Project protocol/specification and conformance materials |
| `one-rio-muss-architecture` | Constitutional grammar, architecture, status/claim vocabulary, and release governance |
| `rio-receipt-protocol` | Local receipt-engine and ledger evidence |
| `rio-system` | Active gateway/runtime evidence for named surfaces |
| `rio-tools` | SDKs, simulators, verifiers, and conformance tooling |
| `rio-reference-impl` | Reference implementation and sandbox proof surfaces |
| `language-intake-mvp` | Deterministic language-crossing prototype |

No repository inherits whole-system authority or completeness merely because it is listed here.

---

## Getting started for evaluation

Because the actual repository license is All Rights Reserved, cloning or access must not be interpreted as permission to reuse, modify, redistribute, or use commercially.

For authorized evaluation:

1. Read the project protocol specification.
2. Review the named schemas and conformance profile.
3. Run the local verification guide and vectors.
4. Record the exact commit, environment, commands, and results.
5. State the evidence ceiling with every claim.

A local verification run is not certification or production approval.

---

## Regulatory mapping

Documents in this repository may map technical mechanisms to requirements or frameworks such as the EU AI Act, NIST AI RMF, or ISO/IEC 42001.

A mapping can help with analysis. It does not establish:

- legal compliance;
- regulatory approval;
- conformity assessment;
- certification;
- applicability to a particular organization or deployment.

Those conclusions require qualified legal, regulatory, security, and organizational review of the actual deployed system.

---

## Conformance levels

The project conformance document defines technical levels for represented receipt, verification, ledger, hash-chain, and signature capabilities.

Any claim should use this form:

```text
<implementation>
conformed to <profile and version>
under <test suite and version>
in <environment>
with <result>
subject to <exclusions>
```

Do not use `RIO-compliant`, `fully compliant`, or `certified` without a named profile, test evidence, and an authorized designation process.

---

## Examples

Example financial, email, deletion, deployment, and access-grant scenarios are illustrative artifacts. They do not authorize real transactions, prove live execution, or establish that a deployment is safe or lawful.

---

## Contribution status

Existing contribution and governance documents describe project processes. Acceptance of a contribution does not by itself grant mark, certification, or official-designation rights.

Before inviting broad external contributions, the project should reconcile contributor copyright, patent, license, CLA/DCO, AI-assisted contribution, and governance terms.

---

## License

The actual repository license is **All Rights Reserved**. See [`LICENSE`](LICENSE).

The LICENSE file describes Apache License 2.0 as a possible future public-release posture. That intention is not an operative Apache-2.0 grant today.

Until the license is formally changed:

- the repository must not be described as Apache-licensed or open source;
- public visibility does not grant permission to copy, modify, redistribute, publish, or use commercially;
- no trademark, certification, badge, compatibility-mark, or official-implementation right is granted.

## Keeper

> Strong protocol language requires a named scope, version, mechanism, test, and proof ceiling.

> Project normativity is not external-standard adoption. Conformance is not compliance. Verification is not external truth. Visibility is not permission.
