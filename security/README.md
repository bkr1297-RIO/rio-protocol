# RIO Security Model

> **This directory contains security documentation and threat model analysis. It is NOT a code directory.**
> Security-related code (signing, verification, key management) lives in `/runtime/receipts/` and `/runtime/keys/`.

---

## Overview

The RIO security model ensures that every governed action is cryptographically signed, independently verifiable, and resistant to tampering. The security architecture operates on the principle that the system enforces the rules, not the AI.

## Core Security Properties

| Property | Mechanism | Description |
|----------|-----------|-------------|
| **Non-repudiation** | RSA-PSS signatures | Every receipt is signed; the signer cannot deny having produced it |
| **Tamper evidence** | SHA-256 hash chains | Any modification to the ledger breaks the chain and is detectable |
| **Fail-closed execution** | Approval gate | Actions are blocked by default unless explicitly approved |
| **Independent verification** | Standalone verifier | Any party can verify receipts and ledger integrity without the original system |
| **Intent binding** | Intent hash | The approved intent is cryptographically bound to the executed action |

## Trust Boundaries

The RIO protocol defines clear trust boundaries:

1. **AI Agent boundary:** The AI proposes intent but cannot execute without approval.
2. **Policy Engine boundary:** Evaluates risk and routes to appropriate approval authority.
3. **Human Approval boundary:** Human approvers operate outside the automated system.
4. **Execution boundary:** The execution gate only opens with valid approval tokens.
5. **Verification boundary:** Post-execution verification is independent of the executor.
6. **Ledger boundary:** The ledger is append-only and independently auditable.

## Threat Model

The full threat model is documented in `/spec/threat_model.md` and covers:

- Unauthorized execution attempts (bypassing approval)
- Receipt forgery and signature manipulation
- Ledger tampering and chain integrity attacks
- Replay attacks using previously approved tokens
- Privilege escalation through policy manipulation
- Denial of service against approval channels

## Cryptographic Specifications

| Component | Algorithm | Parameters |
|-----------|-----------|------------|
| Receipt signatures | RSA-PSS | 2048-bit key, SHA-256, MGF1-SHA-256 |
| Content hashing | SHA-256 | Standard NIST specification |
| Ledger chain | SHA-256 | Hash of entry contents + previous hash |
| Server-side verification | Ed25519 | For lightweight verification endpoints |

## Related Files

- **Threat Model:** `/spec/threat_model.md`
- **Identity and Credentials:** `/spec/identity_and_credentials.md`
- **Trust Boundaries Diagram:** `/reference-architecture/05_trust_boundaries.png`
- **Kill Switch (EKS-0):** `/safety/EKS-0_kill_switch.md`
- **Cross-Domain Verification:** `/spec/cross_domain_verification.md`
