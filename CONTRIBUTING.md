# Contributing to the RIO Protocol

Thank you for your interest in contributing to the RIO Protocol. This document explains how to participate in the development and standardization of the protocol.

---

## What is RIO?

RIO is a governed execution system that sits between AI, humans, and real-world actions. It translates goals into structured intent, evaluates risk and policy, requires approval when necessary, controls execution, verifies outcomes, and generates cryptographically signed receipts recorded in a tamper-evident ledger. The system enforces the rules, not the AI.

---

## How to Contribute

### Reporting Issues

If you find a bug, inconsistency, or gap in the protocol specification, reference implementation, or test suite, please open a GitHub Issue with the following information:

- **Component affected:** Specify which part of the repo is involved (`/spec`, `/runtime`, `/tests`, `/verification`, `/ledger`, `/security`, `/docs`).
- **Description:** A clear description of the issue.
- **Expected behavior:** What the protocol or implementation should do.
- **Actual behavior:** What it currently does.
- **Steps to reproduce:** If applicable, provide steps to reproduce the issue.

### Proposing Changes

All changes to the protocol specification, schemas, or conformance tests follow a structured review process:

1. **Open an Issue** describing the proposed change and its rationale.
2. **Fork the repository** and create a feature branch from `main`.
3. **Make your changes** following the guidelines below.
4. **Submit a Pull Request** referencing the issue number.
5. **Review and discussion** will occur on the PR before merging.

### What You Can Contribute

| Area | Directory | Description |
|------|-----------|-------------|
| Protocol Specification | `/spec` | Clarifications, corrections, or extensions to the protocol spec |
| Reference Implementation | `/runtime` | Bug fixes, improvements, or new features in the Python reference |
| Conformance Tests | `/tests` | New test vectors, test cases, or conformance improvements |
| Verification Tools | `/verification` | Improvements to the standalone receipt and ledger verifier |
| Documentation | `/docs` | Implementation guides, regulatory mappings, tutorials |
| Ledger Protocol | `/ledger` | Ledger format documentation and integrity rules |
| Security Model | `/security` | Threat model updates, security analysis, trust boundary docs |

---

## Development Guidelines

### Code Style

- Python code follows PEP 8 conventions.
- All functions must include docstrings.
- Type hints are encouraged for all function signatures.

### Testing

- All changes to the reference implementation must include corresponding test updates.
- Run the full test suite before submitting a PR:

```bash
cd runtime
python -m runtime.test_harness
```

- All 57 tests must pass. New features must include new tests.

### Specification Changes

Changes to the protocol specification (`/spec`) require:

- A clear rationale explaining why the change is necessary.
- An assessment of backward compatibility.
- Updates to any affected schemas in `/spec/*.json`.
- Updates to any affected conformance tests in `/tests/conformance/`.

### Commit Messages

Use clear, descriptive commit messages:

```
[component] Brief description of change

Longer explanation if necessary. Reference issue numbers
where applicable.

Refs: #123
```

Components: `spec`, `runtime`, `tests`, `verification`, `ledger`, `security`, `docs`

---

## Versioning

The RIO Protocol follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Backward-incompatible changes to the protocol specification, receipt schema, or ledger format.
- **MINOR** version: Backward-compatible additions (new optional fields, new test vectors, new documentation).
- **PATCH** version: Bug fixes, clarifications, and corrections that do not change protocol behavior.

---

## Code of Conduct

Contributors are expected to maintain a professional and respectful environment. Focus on technical merit and constructive feedback. Personal attacks, harassment, or discriminatory behavior will not be tolerated.

---

## License

By contributing to this repository, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).

---

## Questions

If you have questions about contributing, please open a GitHub Issue with the `question` label.
