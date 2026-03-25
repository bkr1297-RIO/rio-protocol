# RIO Protocol: System Invariants Specification

## 1. Introduction

This document specifies the system invariants for the RIO Protocol, a fail-closed execution governance system for AI and automated systems. These invariants are fundamental properties that MUST always hold true in any compliant implementation of the protocol. The integrity and security of the entire system rely on the strict enforcement of these invariants.

This specification uses the keywords MUST, SHALL, SHOULD, and MAY as defined in RFC 2119.

## 2. Authorization Invariants

Authorization invariants ensure that all actions are explicitly permitted and that the principle of least privilege is enforced.

| ID | Statement | Rationale | Violation Consequence | Verification Method |
|---|---|---|---|---|
| AUTH-001 | No action SHALL be executed without a valid, corresponding authorization record. | To prevent unauthorized actions and ensure that every executed operation is backed by an explicit, verifiable permission. | The system MUST immediately halt the execution of the unauthorized action and generate a high-severity alert. | The execution environment MUST verify the presence and validity of an `authorization_record` before initiating any action. The verifier MUST check the signature, timestamp, and single-use status of the authorization. |
| AUTH-002 | An entity SHALL NOT self-authorize an action. | To prevent conflicts of interest and enforce the separation of duties, a core principle of robust governance. | The authorization request MUST be rejected. If detected post-facto, the action MUST be considered void and a security incident reported. | The authorization system MUST verify that the identity of the requester in the `canonical_request` is different from the identity of the approver signing the `authorization_record`. |
| AUTH-003 | Every authorization MUST be time-bound. | To limit the window of opportunity for misuse of a compromised or stolen authorization. | Any authorization used outside its validity period MUST be rejected. | The `authorization_record` MUST contain an `expires_at` timestamp. The execution environment MUST verify that the current time is before the `expires_at` timestamp before proceeding. |
| AUTH-004 | Every authorization MUST be single-use. | To prevent replay attacks where a valid authorization is intercepted and reused to perform multiple unauthorized actions. | Any attempt to reuse an authorization MUST be rejected. | The `authorization_record` MUST contain a unique nonce. The system MUST maintain a record of all used nonces for a given time window and check that the nonce has not been previously consumed. |

## 3. Cryptographic Invariants

Cryptographic invariants ensure the integrity, authenticity, and non-repudiation of all protocol records.

| ID | Statement | Rationale | Violation Consequence | Verification Method |
|---|---|---|---|---|
| CRYP-001 | All records in the traceability chain MUST be cryptographically signed. | To ensure the authenticity and integrity of each record, proving who created it and that it has not been tampered with. | Any unsigned or invalidly signed record MUST be rejected, and the entire traceability chain associated with it MUST be considered invalid. | Every record (`canonical_request`, `risk_evaluation`, `authorization_record`, `execution_record`, `attestation_record`, `receipt`) MUST be verified against the public key of the claimed issuer. The signature verification MUST use ECDSA-secp256k1. |
| CRYP-002 | All hashes MUST be verifiable. | To ensure that all references and links between records are intact and that the data has not been altered. | A hash mismatch MUST invalidate the record and its entire chain, triggering a high-priority security alert. | All hashes MUST be computed using SHA-256. Verification involves re-computing the hash of the data based on the minified sorted JSON canonicalization and comparing it to the stored hash. |
| CRYP-003 | Nonces used in cryptographic operations MUST NEVER be reused for the same purpose by the same entity. | To prevent replay attacks and other cryptographic vulnerabilities that rely on predictable or repeated values. | A reused nonce MUST cause the operation to fail. For example, a transaction with a reused nonce will be rejected. | The system MUST maintain a state of used nonces for relevant contexts (e.g., authorization, transaction signing) and verify that a new nonce has not been used before. |
| CRYP-004 | The cryptographic integrity of the hash chain MUST be maintained. | To ensure the tamper-evident nature of the ledger and the traceability chain. | Any break in the hash chain MUST invalidate all subsequent records and be treated as a critical security breach. | Each record in a sequence (e.g., ledger entries) MUST contain the hash of the previous record. Verification requires traversing the chain and ensuring that the `previous_hash` field of each record matches the computed hash of the preceding record. |

## 4. Ordering Invariants

Ordering invariants ensure that the sequence of events is logical, consistent, and resistant to manipulation.

| ID | Statement | Rationale | Violation Consequence | Verification Method |
|---|---|---|---|---|
| ORD-001 | Records in a traceability chain MUST be created in a strict, predefined sequence. | To ensure a logical and causal flow of events, where each step is a prerequisite for the next. The canonical sequence is: `canonical_request` → `risk_evaluation` → `authorization_record` → `execution_record` → `attestation_record` → `receipt` → `ledger_entry`. | Any record presented out of sequence MUST be rejected. The entire chain is considered invalid. | The system MUST enforce the state transitions of the governed execution loop. For example, an `execution_record` can only be created if a valid `authorization_record` exists for the same request. |
| ORD-002 | No record SHALL reference a future record. | To prevent temporal paradoxes and ensure that the system state is always consistent and based on past, verifiable events. | The record making a forward reference MUST be rejected as invalid. | When verifying a record, the system MUST ensure that any referenced records (e.g., via a hash link) have timestamps that are earlier than the timestamp of the current record. |
| ORD-003 | Timestamps within a single traceability chain MUST be monotonically increasing. | To provide a consistent and unambiguous timeline of events for a given process, which is critical for auditing and debugging. | A record with a timestamp that is not strictly greater than the previous record in the chain MUST be rejected. | During verification of a traceability chain, the timestamp of each record MUST be compared to the timestamp of the preceding record. `timestamp(record_n)` MUST be greater than `timestamp(record_n-1)`. |

## 5. Fail-Closed Invariants

Fail-closed invariants ensure that the system defaults to a secure state (denial) in the face of any ambiguity, failure, or attack.

| ID | Statement | Rationale | Violation Consequence | Verification Method |
|---|---|---|---|---|
| FC-001 | Any verification failure of any kind MUST result in denial. | To ensure that the system never enters an unknown or potentially insecure state. The default posture is to deny execution unless all conditions are explicitly and verifiably met. | The requested action MUST be denied, and the reason for the failure MUST be logged for audit. | All verification points in the protocol (signature, hash, timestamp, policy compliance, etc.) MUST be designed to return a 'deny' state by default. Only a positive and explicit verification success allows the process to continue. |
| FC-002 | Any missing record in the traceability chain MUST result in denial. | To enforce the completeness and integrity of the audit trail. A missing record creates an information gap that could hide malicious activity. | The requested action MUST be denied. | Before execution, the system MUST verify the presence of all required preceding records in the traceability chain as defined by the `Ordering Invariants`. |
| FC-003 | Any timeout during the verification or execution process MUST result in denial. | To prevent attacks that rely on delaying or stalling the system to bypass security checks (e.g., time-of-check to time-of-use attacks). | The operation MUST be cancelled, and a timeout error logged. | All critical operations, especially those involving external communication or complex computation, MUST have a strictly enforced timeout. |
| FC-004 | Any signature mismatch MUST result in denial. | To prevent unauthorized actions and ensure that the claimed origin of a record is authentic. | The record MUST be rejected, and a high-severity security alert MUST be generated, as this indicates a potential forgery attempt. | During signature verification, if the computed signature does not match the provided signature, the verification function MUST return a definitive 'fail' result, leading to denial. |

## 6. Audit Invariants

Audit invariants ensure that a complete, tamper-evident, and verifiable record of all system activities is maintained.

| ID | Statement | Rationale | Violation Consequence | Verification Method |
|---|---|---|---|---|
| AUD-001 | Every completed decision chain MUST produce a final `receipt`. | To provide a concise, verifiable summary of the entire process from request to attestation, which serves as a proof of governance. | An execution chain that does not produce a receipt is considered incomplete and potentially faulty. An alert SHOULD be raised for investigation. | The final step of the `attest` phase in the governed execution loop is the generation of the `receipt`. The system MUST ensure this step is completed before the process is considered finished. |
| AUD-002 | Every receipt MUST be recorded in the audit ledger. | To ensure that a permanent, immutable record of every governed action exists for future audit, compliance, and analysis. | Failure to record a receipt in the ledger MUST be treated as a critical system failure. | The system MUST have a mechanism to ensure the reliable submission of receipts to the ledger. The ledger itself can be periodically checked against a separate log of generated receipts to ensure none were missed. |
| AUD-003 | The audit ledger MUST be append-only. | To ensure that past records cannot be altered or deleted, preserving the integrity of the historical audit trail. | Any attempt to modify or delete an existing ledger entry MUST be rejected by the ledger system and trigger a critical alert. | The ledger's data structure and API MUST be designed to only allow the addition of new entries. Permissions and access controls MUST prevent any modification or deletion operations. |
| AUD-004 | Ledger entries MUST be hash-linked. | To create a tamper-evident chain where any modification to a past entry would invalidate the hashes of all subsequent entries, making tampering immediately obvious. | A broken hash link indicates a compromised ledger. The system MUST enter a safe mode and require manual intervention. | Each `ledger_entry` MUST contain a `previous_hash` field that stores the hash of the preceding entry. Verification involves traversing the ledger and confirming the hash links between all consecutive entries. |

## 7. Governance Invariants

Governance invariants ensure that the rules of the system itself are managed in a secure and controlled manner.

| ID | Statement | Rationale | Violation Consequence | Verification Method |
|---|---|---|---|---|
| GOV-001 | Any change to the system's policies or configuration MUST be processed through the RIO Protocol itself, requiring a valid authorization. | To prevent unauthorized changes to the rules of the system and to ensure that all meta-level changes are subject to the same level of scrutiny and governance as the actions they control. | An unauthorized policy change attempt MUST be rejected. If a change is detected without a corresponding audit trail, it MUST be treated as a critical security breach. | Policy and configuration management tools MUST use the RIO Protocol's own `authorize` and `execute` loops to apply changes. A `canonical_request` for a policy update must be generated, authorized, and recorded in the ledger like any other governed action. |
| GOV-002 | Role separation MUST be enforced at all times. | To prevent a single entity or a single point of compromise from controlling an entire end-to-end process. | Any action that would violate role separation rules (e.g., a developer approving their own code deployment) MUST be blocked. | The authorization system MUST consult a role-based access control (RBAC) policy. Before granting authorization, it MUST verify that the requester and approver have different, appropriate roles for the requested action. |
| GOV-003 | The learning system SHALL NOT be able to modify policies or core system behavior without explicit human approval. | To mitigate the risk of automated systems learning undesirable behaviors or creating feedback loops that could compromise the system's safety or integrity. | The learning system's output (e.g., a suggested policy change) MUST be treated as a recommendation, not a command. It MUST be submitted as a `canonical_request` that requires independent human authorization. | The learning system's outputs MUST be directed to a human-in-the-loop review workflow. The system's architecture MUST ensure the learning module does not have direct write access to the policy repository. Any proposed change MUST be routed through the standard governance process. |
