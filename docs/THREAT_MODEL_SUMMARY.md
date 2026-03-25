# Threat Model Summary

**RIO — Security Threats and Mitigations**

---

## Overview

The RIO threat model identifies ten categories of attack against the governed execution system. This document summarizes the six most critical threat categories, their attack vectors, and the mitigations that the protocol enforces. The full threat model with detailed analysis is available at `spec/threat_model.md`.

The system's security posture is built on a single design principle: **fail closed.** When any component cannot positively verify a required condition, the system denies the action. There is no fail-open mode. The cost of a false denial (a legitimate action is temporarily blocked) is always preferable to the cost of a false approval (an unauthorized action is executed).

---

## Threat 1: Unauthorized Execution

**Attack:** An attacker attempts to execute an action without a valid authorization token — by bypassing the pipeline, forging a token, or exploiting a gap in the execution gate.

**Impact:** Unauthorized actions could result in financial loss, data breach, or system compromise.

**Mitigations:**

| Control | How It Works |
|---------|-------------|
| **Mandatory pipeline traversal** | Every action must pass through all eight pipeline stages. There is no direct path to the execution gate that bypasses policy and risk evaluation. |
| **Authorization token verification** | The execution gate verifies the ECDSA signature on every authorization token before proceeding. Forged tokens fail signature verification. |
| **Intent hash binding** | The authorization token contains the SHA-256 hash of the canonical intent. The execution gate verifies that the token matches the intent being executed. A token issued for one action cannot authorize a different action. |
| **Nonce consumption** | Each token contains a single-use nonce. After the nonce is consumed, the token cannot be reused. |
| **Time-bound expiration** | Tokens expire after 300 seconds by default. Stale tokens are rejected. |

---

## Threat 2: Ledger Tampering

**Attack:** An attacker modifies, deletes, or reorders ledger entries to conceal unauthorized actions or alter the audit trail.

**Impact:** Loss of audit integrity. Inability to detect or prove unauthorized activity.

**Mitigations:**

| Control | How It Works |
|---------|-------------|
| **Hash chain** | Each ledger entry contains the hash of the previous entry. Modifying any entry breaks the chain from that point forward. |
| **Content hashing** | Each entry's content hash is computed from its own fields. Any modification changes the hash, which is detectable. |
| **Deletion detection** | Removing an entry creates a gap in the hash chain. The entry after the deleted one references a hash that no longer exists. |
| **Insertion detection** | Inserting a new entry between existing entries requires recomputing all subsequent hashes, which is detectable by comparing against any prior copy of the chain. |
| **Receipt signatures** | Each receipt is independently signed. Even if the ledger is compromised, the receipts provide a second layer of proof. |
| **Verification tool** | `runtime/verify_ledger.py` can validate the entire hash chain at any time, reporting any broken links or tampered entries. |

---

## Threat 3: Token Reuse (Replay Attack)

**Attack:** An attacker captures a valid authorization token and submits it a second time to execute the same action again — for example, duplicating a wire transfer.

**Impact:** Duplicate financial transactions, repeated data modifications, or unauthorized resource consumption.

**Mitigations:**

| Control | How It Works |
|---------|-------------|
| **Single-use nonces** | Every authorization token contains a unique nonce. The execution gate checks the nonce against the nonce registry before executing. If the nonce has been consumed, the request is rejected. |
| **Nonce registry** | The nonce registry tracks all consumed nonces with timestamps. Nonces transition to consumed status upon first use and cannot be reused. |
| **Time-bound authorization** | Tokens include an expiration timestamp. Even if an attacker captures a nonce before it is consumed, the authorization window limits the attack surface. |
| **Chain hash binding** | The receipt binds the execution to a specific authorization via the chain hash. A replayed authorization would produce a duplicate chain hash, detectable during verification. |

---

## Threat 4: Privilege Escalation

**Attack:** A user with a lower-privilege role (e.g., intern or employee) attempts to perform actions reserved for higher-privilege roles, or to approve their own requests.

**Impact:** Unauthorized actions executed with insufficient oversight.

**Mitigations:**

| Control | How It Works |
|---------|-------------|
| **Role-based policy rules** | The policy engine evaluates rules based on the requester's role. Rules are evaluated in priority order, and role-specific deny rules take precedence over general allow rules. |
| **No self-authorization (INV-06)** | The authorizer must be a different identity than the requester. This is enforced at the authorization stage and the approval manager. |
| **Approval role requirements** | Only managers and admins can approve requests. The approval manager verifies the approver's role level before accepting an approval decision. |
| **Governance role requirements** | Only admins can propose, approve, activate, or roll back policy and risk model changes. The governance API checks the requester's role before any governance operation. |

---

## Threat 5: Kill Switch Bypass

**Attack:** An attacker attempts to execute actions while the kill switch is engaged, or attempts to disengage the kill switch without authorization.

**Impact:** Actions executed during an emergency halt, potentially compounding an ongoing incident.

**Mitigations:**

| Control | How It Works |
|---------|-------------|
| **Execution gate check** | The kill switch is the first check in the execution gate. When engaged, no actions proceed regardless of authorization status. |
| **Kill switch state persistence** | The kill switch state is stored in `runtime/data/system_state.json` and survives process restarts. |
| **Admin-only control** | Only admin-role users can engage or disengage the kill switch. |
| **Ledger recording** | Kill switch events (engage and disengage) are recorded in the ledger with full context: who engaged it, when, and why. |
| **Blocked action recording** | Actions blocked by the kill switch still produce receipts and ledger entries, ensuring the audit trail captures what was attempted during the halt. |

---

## Threat 6: Missing Audit Trail

**Attack:** An action is executed but no receipt or ledger entry is created, leaving a gap in the audit trail.

**Impact:** Inability to prove what happened, who authorized it, or when it occurred.

**Mitigations:**

| Control | How It Works |
|---------|-------------|
| **Invariant INV-02 (Receipt Completeness)** | Verified at the end of every pipeline run. Every completed request must have a receipt. Violations are logged and flagged. |
| **Invariant INV-03 (Ledger Completeness)** | Verified at the end of every pipeline run. Every receipt must have a corresponding ledger entry. Violations are logged and flagged. |
| **Denial receipts** | Even denied requests produce receipts and ledger entries. There is no outcome that does not generate audit artifacts. |
| **Kill switch receipts** | Blocked requests produce receipts and ledger entries. |
| **Governance receipts** | Policy and risk model changes produce receipts and ledger entries. |
| **Corpus records** | Every pipeline outcome also produces a governed corpus record, providing a second, independent record of the decision. |

---

## Residual Risks

No system eliminates all risk. The following residual risks are acknowledged:

| Residual Risk | Context |
|--------------|---------|
| **Key compromise** | If the system's private key is compromised, an attacker could forge receipts. Mitigation: key rotation procedures and secure key storage. |
| **Clock manipulation** | If the system clock is manipulated, time-bound authorizations could be extended. Mitigation: NTP synchronization and clock drift monitoring. |
| **Insider with admin access** | An admin with full system access could theoretically manipulate data files directly. Mitigation: the hash chain and receipt signatures make such manipulation detectable, even if not preventable. |
| **Nonce registry unavailability** | If the nonce registry is unavailable, the system fails closed (denies execution). This is a safety-preserving failure mode but could cause availability issues. |

---

## Design Principles

The threat model is built on five design principles:

1. **Fail closed.** When in doubt, deny. No action proceeds without positive verification of all required conditions.

2. **Defense in depth.** Multiple independent controls protect against each threat. Compromising one control does not compromise the system.

3. **Separation of duties.** No single actor can both request and authorize an action. Policy changes require separate proposer and approver.

4. **Complete audit trail.** Every outcome — executed, denied, blocked, or governance change — produces a signed receipt and a hash-linked ledger entry.

5. **Tamper evidence over tamper prevention.** The system cannot prevent a sufficiently privileged attacker from modifying data files. It ensures that any such modification is detectable.

---

## References

| Specification | Location |
|--------------|----------|
| Full Threat Model | `spec/threat_model.md` |
| Protocol Invariants | `spec/protocol_invariants.md` |
| System Invariants | `spec/system_invariants.md` |
| Kill Switch Specification | `safety/kill_switch_spec.md` |
| Verification Model | `spec/verification_model.md` |
