# Security Policy

## Scope

This policy covers vulnerabilities in the RIO protocol specification, JSON schemas, conformance test vectors, and reference verification logic contained in this repository.

## What to report

Report any issue that could allow an attacker to:

- **Bypass authorization.** Construct a valid-looking receipt or token without going through the approval process.
- **Forge signatures.** Produce a receipt that passes Ed25519 or ECDSA-secp256k1 verification without the private key.
- **Break intent binding.** Cause a receipt to verify against a different intent than the one that was authorized.
- **Tamper with the ledger.** Modify, delete, or reorder ledger entries without detection by the hash chain.
- **Replay tokens.** Reuse a single-use execution token to trigger a second execution.
- **Circumvent TTL enforcement.** Use an expired token to pass the execution gate.
- **Violate fail-closed behavior.** Cause the execution gate to allow an action without a valid token.

## What is not in scope

- Vulnerabilities in third-party dependencies (report to the dependency maintainer)
- Issues in implementations outside this repository
- Denial-of-service attacks against specific deployments
- Social engineering

## How to report

Send an email to the repository owner with the following information:

1. Affected file(s) and line number(s)
2. Description of the vulnerability
3. Steps to reproduce
4. Potential impact

Do not open a public issue for security vulnerabilities.

## Response

We will acknowledge receipt within 72 hours and provide an initial assessment within 7 days. Critical vulnerabilities affecting signature verification, hash chain integrity, or authorization bypass will be prioritized.

## Disclosure

We follow coordinated disclosure. Please allow 90 days for a fix before public disclosure.
