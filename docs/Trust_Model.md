# Trust Model — RIO Execution Governance Infrastructure

**Version:** 2.0
**Status:** Reference implementation (143 tests, 0 failures)

## Purpose

This document defines who and what you must trust when relying on RIO for execution governance, and — equally important — what you do not have to trust. A clear trust model is essential for security reviewers, regulators, and any organization evaluating RIO for deployment.

## Design Principle

> **Minimize trust assumptions.** The system is designed so that the integrity of the audit trail can be verified by any independent party without trusting the runtime operator, the AI agent, or the audit system itself.

## What You Must Trust

### 1. The Signing Key Holder

You must trust the entity that holds the signing key for the authenticity of approvals. The signing key is used to:
- Sign Execution Tokens (authorizing actions)
- Sign receipts (recording decisions)
- Sign ledger entries (maintaining the audit chain)

If the signing key is compromised, an attacker can forge tokens and receipts. Keys are currently software-managed. HSM integration for hardware-protected keys is future work.

**Mitigation:** Key rotation is supported. Compromised keys can be revoked. All receipts reference the key version used for signing, enabling forensic analysis of which receipts were signed before vs. after a compromise.

### 2. The Policy Author

You must trust the policy author for the correctness of governance rules. The policy engine enforces whatever rules are configured — if the rules are wrong, the system will enforce wrong rules correctly.

**Mitigation:** Policies are versioned. Every receipt records the policy version that was active when the decision was made. Policy changes are auditable. The Learning Loop can propose policy improvements based on historical outcomes, but cannot modify policies directly — a human must approve changes.

## What You Do Not Have to Trust

### 3. The Runtime Operator

You do **not** have to trust the operator running the RIO gateway. Receipts and the ledger are independently verifiable. An operator who modifies the runtime cannot produce receipts that pass independent verification (unless they also compromise the signing key).

**Verification method:** Run the independent verifier against the ledger and receipts using only the public key. No access to the runtime is required.

### 4. The AI Agent

You do **not** have to trust the AI agent. The agent cannot execute any action without a valid Execution Token. The execution gate is fail-closed — it verifies the token before releasing the action. The agent's recommendations are advisory; the governance loop decides what actually happens.

**Verification method:** The ledger records every action the agent attempted, including denials. Any gap between what the agent requested and what was executed is visible in the audit trail.

### 5. The Audit System

You do **not** have to trust the audit system itself. The hash chain and per-entry signatures make the ledger self-verifying. Any modification to any entry invalidates all subsequent hashes. The independent verifier detects tampering without relying on the audit system's own integrity checks.

**Verification method:** Recompute `Hn = SHA256(En.data + H(n-1))` for every entry. Verify each entry's signature against the public key. Any mismatch proves tampering.

## Trust Boundary Summary

| Component | Trust Required | Why |
|-----------|---------------|-----|
| Signing key holder | **Yes** | Authenticity of approvals depends on key integrity |
| Policy author | **Yes** | Correctness of rules depends on human judgment |
| Runtime operator | **No** | Receipts/ledger are independently verifiable |
| AI agent | **No** | Cannot execute without valid token |
| Audit system | **No** | Hash chain + signatures are self-verifying |
| Network transport | **No** | Signatures protect against MITM; hashes detect corruption |
| Independent verifier | **Minimal** | Open-source, deterministic, auditable code |

## Regulatory Implications

The trust model directly supports regulatory requirements:

- **EU AI Act, Article 14 (Human Oversight):** The human approver is the trust anchor. The system enforces that high-risk actions require human authorization before execution.
- **EU AI Act, Article 12 (Record-Keeping):** The ledger provides tamper-evident records that do not require trust in the system that created them.
- **NIST AI RMF, GOVERN:** Policy authorship and versioning provide the governance structure. The trust model makes explicit who is accountable for what.
- **ISO 42001, A.6.2.8 (Event Logging):** Automatic signed receipts provide event logs that are independently verifiable.

## Known Limitations

1. **Software-managed keys:** The current implementation stores signing keys in software. A host compromise could expose the key. HSM integration would close this gap.
2. **Single-node ledger:** The current ledger is single-node. A compromised host could theoretically destroy the ledger (though not modify it undetectably). Distributed replication would close this gap.
3. **Policy correctness is human-dependent:** The system enforces rules correctly but cannot guarantee the rules themselves are correct. The Learning Loop mitigates this by proposing improvements, but a human must approve them.

---

**See also:** [Architecture.md](Architecture.md) | [Threat_Model.md](Threat_Model.md) | [EGI_Technical_Assessment.pdf](EGI_Technical_Assessment.pdf)
