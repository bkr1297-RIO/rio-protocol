# Changelog

All notable changes to the RIO Protocol will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
