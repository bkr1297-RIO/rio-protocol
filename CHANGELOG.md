# Changelog

All notable changes to the RIO Protocol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- **WS3 Conformance Test Suite:** Machine-readable conformance suite (`tests/conformance/rio_conformance_suite_v1.json`) with 57 test case definitions, 8 protocol invariants, and interoperability bar.
- **Test Vectors:** 12 deterministic test vector files in `tests/vectors/` — valid/invalid receipts, hash computation examples, signing payload examples, valid/tampered ledger chains, and Ed25519 test public key.
- **Test Matrix:** Human-readable test matrix (`tests/conformance/TEST_MATRIX.md`) mapping all 57 test cases to conformance levels, expected decisions, invariants, and required vectors.
- **RIO Gateway Protocol Specification v1.0:** Sovereign Gate Edition (`spec/rio_gateway_protocol_v1.0.json`) — the production gateway specification covering ECDSA secp256k1 signatures, Sovereign Gate (5-check sequence), Execution Gate (5-guard sequence), signature/nonce registries, in-memory response ledger, execution ledger, post-execution ledger with HMAC-SHA256, database schema, and worked examples.
- **WS2 Canonical Protocol Specification v1.0:** `spec/RIO_Protocol_Specification_v1.0.md` — the canonical protocol specification for the production gateway (Sovereign Gate Edition), covering ECDSA secp256k1 cryptographic primitives, intake request schema, Sovereign Gate (5-check sequence), Execution Gate (5-guard sequence), signature/nonce registries, three ledger types, database schema, error codes, and worked examples.
- **WS4 Independent Verifier Specification:** `spec/Independent_Verifier_Spec.md` — formal specification defining how third-party verifiers must validate receipts and ledger chains independently of the reference implementation.
- **WS4 Independent Verifier Implementation:** `verification/` — standalone Python package implementing all 7 receipt checks and 4 ledger chain checks. Zero imports from `/runtime`. Single dependency (`cryptography>=41.0.0`). CLI with `verify-receipt`, `verify-ledger`, and `verify-all` commands. 32 tests + 13 subtests passing against WS3 conformance vectors.
- **WS5 Adoption & Compliance Documentation:** Four documents in `docs/adoption/`:
  - `REGULATORY_MAPPING.md` — Maps RIO mechanisms to EU AI Act (6 articles, 22 sub-requirements), NIST AI RMF (16 subcategories), and SOC 2 Type II (17 criteria). 73% full coverage, 27% partial (outside protocol scope), 0% unaddressed.
  - `CERTIFICATION_CRITERIA.md` — Three conformance levels (Level 1: Receipt Format, Level 2: Pipeline, Level 3: Full Protocol) with 60+ binary pass/fail criteria, certification process, and maintenance rules.
  - `IMPLEMENTATION_GUIDE.md` — Step-by-step adoption guide covering architecture decisions, three implementation phases, integration patterns, operational considerations, testing strategy, and migration from non-governed systems.
  - `QUICKSTART.md` — Minimal viable deployment guide for getting a Level 1 compliant implementation running in under an hour.
- **WS6 Conformance & Quickstart Package:**
  - `docs/QUICKSTART.md` — External developer quickstart: clone-to-verified-receipt in 10 minutes. Covers what RIO is, how to install the verifier, how to run it against example files, expected PASS/FAIL output, and pointers to the canonical spec.
  - `docs/CONFORMANCE.md` — Conformance level definitions: Level 1 (Receipt Format), Level 2 (Ledger + Verification), Level 3 (Full Pipeline). Defines what must pass at each level, references test vectors.
  - `examples/quickstart/` — Four real, cryptographically valid example files: `example_intent.json`, `example_receipt_v2.json`, `example_ledger.json`, `example_verification_result.json`.
  - `tests/conformance/` — Six named conformance test vectors for external implementers: `valid_receipt.json`, `valid_ledger.json`, `tampered_receipt.json`, `tampered_ledger.json`, `missing_fields_receipt.json`, `invalid_signature_receipt.json`.
  - `verification/README.md` — Expanded with complete CLI command examples, exit code reference, PASS/FAIL criteria, output modes, and what FAIL looks like.
- **WS6 Gateway Artifacts:** Agent-produced artifacts for the production gateway verification path:
  - `docs/QUICKSTART_gateway.md` — Gateway-specific quickstart using ECDSA secp256k1, HMAC-SHA256, and pipe-delimited hashing.
  - `docs/CONFORMANCE_gateway.md` — Gateway conformance guide with 13 Level 1, 14 Level 2, and 8 Level 3 requirements.
  - `examples/gateway/` — Four cryptographically valid gateway example files (intent, receipt, ledger, verification result). All hashes independently verified.
  - `demo/demo_verify.py` — Standalone gateway verifier (4 checks: receipt hash, execution ledger chain, post-execution ledger hash, HMAC signatures). Zero dependencies beyond Python stdlib.
  - `tests/conformance/run_conformance_tests.py` — 7 test vectors (TV-C1 through TV-C7) covering all gateway hash formulas. All passing.
- **WS7 Conformance Tooling:**
  - `tests/run_conformance.py` — Automated conformance test runner: 23 tests across Level 1 (17 tests) and Level 2 (6 tests). Supports `--level`, `--verbose`, and `--json` flags. Exit code 0 on all-pass, 1 on failure.
  - `tools/check_compliance.py` — Compliance level validator: determines Level 0 (Non-Compliant), Level 1 (Receipt Format), Level 2 (Governance Attested), or Level 3 (Full Protocol) from provided artifacts. Supports `--auto` discovery, `--json` output, and explicit `--receipt`/`--key`/`--ledger` paths.
  - `docs/COMPLIANCE_BADGES.md` — Compliance level definitions, badge usage rules, and testing instructions for all three levels.
  - `docs/VERSIONING.md` — Protocol versioning policy: SemVer 2.0.0, breaking change definitions, backward compatibility guarantees, deprecation policy, and version lifecycle.
  - `docs/PROTOCOL_CHANGE_TEMPLATE.md` — Protocol Change Proposal (PCP) template with all required sections: abstract, motivation, specification, backward compatibility, test vectors, security considerations, and conformance impact.
  - `docs/VERIFICATION_OUTPUT_EXAMPLE.md` — Complete verification output examples for both the reference implementation (Ed25519, 7+4 checks) and gateway (ECDSA secp256k1, 9 checks) verifiers, with PASS/FAIL examples and failure diagnosis guide.
- **Complete Protocol Specification (Markdown + JSON):** `spec/RIO_Protocol_Specification_v1.0.md` replaced with comprehensive 101K-character canonical specification. Structured JSON version added as `spec/RIO_Protocol_Specification_v1.0.json`.
- **Python SDK:** `sdk/python/rio_sdk/` — Zero-dependency Python package for receipt verification, conformance testing, and compliance level checking. Includes `verifier.py` (4 checks: receipt hash, execution ledger chain, post-exec ledger hash, HMAC signatures), `conformance.py` (7 test vectors), `compliance.py` (L1/L2/L3 assessment), and `setup.py` for pip installation.
- **JavaScript SDK:** `sdk/javascript/src/` — Zero-dependency Node.js package for receipt verification and conformance testing. Includes `verifier.js`, `conformance.js`, `index.js`, and `package.json`.
- **SDK Examples:** `sdk/examples/` — Working examples in Python and JavaScript demonstrating receipt verification, conformance testing, and tamper detection.
- **SDK Documentation:** `sdk/README.md` — SDK installation, usage, and API reference for both Python and JavaScript.
- **SDK Quickstart & Conformance Guides:** `docs/QUICKSTART_sdk.md` and `docs/CONFORMANCE_sdk.md` — SDK-specific quickstart and conformance documentation.
- **Updated Demo & Tests:** `demo/demo_verify_sdk.py` and `tests/conformance/run_conformance_sdk.py` — SDK-integrated verification demo and conformance test runner.
- **Full Cycle Reference Examples:** `examples/full_cycle/` — 9 reference files captured from live Merkaba Sovereign Engine v3.0.0 execution. Includes signed intent, 4-step execution result, v2 receipt, ledger entry, complete ledger chain, independent verification result (PASS), audit log (fail-closed governance evidence), debug test flow (5/5 PASS), and nonce/replay protection stats.
- **Engine Manifest:** `examples/engine_manifest.json` — Complete manifest for the live Merkaba Sovereign Engine gateway, documenting all 26 API endpoints, cryptographic suite (ECDSA secp256k1 + HMAC-SHA256), security model (fail-closed), and compliance level (L2).
- **Governance Documents:**
  - `docs/GOVERNANCE.md` — Protocol governance structure, steward responsibilities, change proposal process, and backward compatibility rules.
  - `docs/CERTIFICATION.md` — Three certification levels (Structural, Cryptographic, Full Protocol), certification process, testing requirements, and revocation rules.
  - `docs/CERTIFICATION_CHECKLIST.md` — Submission checklist for RIO certification with evidence requirements.
  - `docs/RELEASE_CHECKLIST.md` — Pre-publish release checklist ensuring all artifacts are updated.
  - `docs/RELEASE_PROCESS.md` — Version numbering rules, release workflow, and update requirements.
- **RIO Core Runtime Behavior:** `RIO_Core_Runtime_Behavior.md` — 8,545-word implementation-independent behavior document. Canonical source of truth for external implementers covering all protocol stages, receipt format, ledger format, verification rules, and protocol invariants.
- **RIO Protocol Simulator:** `simulate.py` — Standalone simulator with 4 generation modes: `--generate-valid` (7 artifacts + 4/4 verification PASS), `--generate-invalid-signature` (corrupt signature for Stage 2 rejection), `--generate-tampered-ledger` (3-entry chain with row 2 tampered — verification FAIL), `--generate-full-example` (narrated 8-stage protocol flow). Also supports `--verify <file>` for artifact verification and `--all` to run all modes. Uses Ed25519 cryptography with real signatures.
- **Simulator Artifacts:** `examples/simulator/` — 17 reference JSON files generated by the RIO Protocol Simulator v1.0 (Ed25519). Includes valid flow (7 files), invalid signature intent, tampered ledger chain + verification result, and full narrated 8-stage example (7 files). All hashes and signatures are cryptographically valid.
- **WS9 Developer SDK:** `rio_sdk/` — Python SDK for the RIO Governance Protocol (v0.1.0). 8 modules, 26 public exports:
  - `RIOClient` — HTTP client for all 13 gateway endpoints (governance, gate, audit, policy).
  - `IntentBuilder` — Fluent builder for constructing signed intents with context and metadata.
  - `ReceiptVerifier` — 7-check receipt verification (required fields, decision, request hash, receipt hash, signature, fingerprint, version).
  - `LedgerVerifier` — Chain formula verification (genesis hash, prev_hash linkage).
  - `LedgerClient` — High-level ledger operations (latest, full, verify, summary).
  - `Ed25519Key/Signer` — Ed25519 key management (generate, load PEM, save, sign, verify, JSON signing).
  - `ECDSAKey/Signer` — ECDSA secp256k1 key management.
  - 9 typed exceptions: `RIOError`, `RIOConnectionError`, `RIOHTTPError`, `RIOIntentBlockedError`, `RIOVerificationError`, `RIOLedgerError`, `RIOApprovalError`, `RIOKeyError`, `RIOConfigError`.
  - 8 data models: `Intent`, `Receipt`, `EvaluateResult`, `GovernorSubmission`, `LedgerEntry`, `GateExecuteResult`, `VerificationResult`, `VerificationCheck`.
- **SDK Examples:** `rio_sdk/examples/` — 3 working examples: `send_intent_example.py` (full flow), `governor_submit_example.py` (human approval), `key_generation_example.py` (Ed25519 + ECDSA keygen/sign/verify).
- **SDK Documentation:** `SDK_README.md` — Complete developer documentation with module reference, exception hierarchy, data models, receipt format, and ledger chain formula.

---

## [1.0.0] - 2026-03-26

### Added

- **Protocol Specification:** Complete 8-stage governed execution pipeline specification.
- **Three-Loop Architecture:** Intake/Discovery Loop, Execution/Governance Loop, and Learning Loop formally defined in `spec/three_loop_architecture.md`.
- **v2 Cryptographic Receipts:** RSA-PSS signed receipts with `intent_hash`, `action_hash`, `verification_hash`, `verification_status`, ISO 8601 timestamps, and identity fields.
- **v2 Hash-Chain Ledger:** Tamper-evident ledger with `previous_ledger_hash` chaining, `ledger_hash` integrity, and independent chain verification.
- **Denial Receipts:** Blocked or denied actions now generate full v2 receipts with `decision=denied` and `execution_status=BLOCKED`.
- **Post-Execution Verification:** Stage 6b verification step produces `verification_status` (verified/failed/skipped) and `verification_hash` embedded in receipts.
- **Reference Implementation:** Complete Python reference implementation in `/runtime` with 57 passing tests (47 v1 + 10 v2).
- **Receipt Packages:** `runtime/receipts/` — receipt generator, signer, and verifier modules.
- **Ledger Packages:** `runtime/ledger_v2/` — ledger writer and chain verifier modules.
- **Standalone Verification CLI:** `runtime/verification.py` — independent receipt and ledger verification tool.
- **JSON Schemas:** `schemas/receipt_v1.json`, `schemas/ledger_entry.json`, `schemas/canonical_intent.json`, `schemas/auth_token.json`.
- **Protocol Specifications:** 15 specification documents covering pipeline stages, intent structure, policy engine, approval protocol, execution control, receipt format, ledger format, verification rules, and protocol invariants.
- **Three-Loop Architecture Diagram:** Visual diagram in `docs/rio-three-loop-architecture.png`.
- **Whitepaper:** Full protocol whitepaper in `docs/rio_whitepaper_v2.pdf` and `docs/rio_whitepaper_v2.md`.
- **Apache 2.0 License:** `LICENSE` file added.
- **Contributing Guide:** `CONTRIBUTING.md` with development guidelines, commit conventions, and versioning policy.

### Protocol Version

- Receipt format: v2
- Ledger format: v2 (hash-chain with `previous_ledger_hash`)
- Pipeline: 8 stages + Stage 6b verification
- Signature algorithm: RSA-PSS (2048-bit, SHA-256)
- Hash algorithm: SHA-256
- Timestamp format: ISO 8601 UTC

---

## [0.x.x] - Pre-release Development

### Summary

Initial development of the RIO protocol including:

- v1 receipt format (JSON with basic fields, no cryptographic signatures).
- v1 ledger (append-only, no hash chaining).
- 8-stage pipeline specification (Stages 1-8).
- Policy engine with risk assessment and approval routing.
- Human approval protocol with timeout and escalation.
- Execution gate with fail-closed behavior.
- 47 test cases covering pipeline stages, policy, approval, execution, and receipts.
- Kill switch (EKS-0) specification.
- Reference architecture and master protocol index.

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-03-26 | First formal release with v2 receipts, hash-chain ledger, Three-Loop Architecture, Apache 2.0 license |
| 0.x.x | Pre-2026-03-26 | Development releases with v1 receipts and pipeline specification |
