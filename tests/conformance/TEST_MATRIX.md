# Conformance Test Matrix

Maps each test case to its conformance level, expected decision, invariants validated, and required test vectors.

| Test ID | Title | Level | Expected | Invariants | Vectors |
|---------|-------|-------|----------|------------|---------|
| TC-RIO-001 | Clean Pass Through Full Governance Pipeline | 2 | allow | INV-01, INV-02, INV-03, INV-04, INV-05, INV-06, INV-07 | receipt_valid_approved.json |
| TC-RIO-002 | Hard Deny on Invariant Violation | 2 | block | INV-01, INV-02, INV-06, INV-07, INV-08 | receipt_valid_denied.json |
| TC-RIO-003 | User Disengagement Kill Switch | 2 | block | INV-01, INV-08 | - |
| TC-EXTRA-001 | Authority Escalation Keyword Detection | 1 | block | INV-01, INV-08 | - |
| TC-EXTRA-002 | Pressure State Detection and Escalation | 1 | escalate | INV-03, INV-08 | - |
| TC-EXTRA-003 | Scope Mismatch Triggers Modify Decision | 1 | modify | INV-04 | - |
| TC-EXTRA-004 | Low Coherence Triggers Modify Decision | 1 | modify | INV-03 | - |
| TC-POLICY-001 | Policy Bundle Hash Integrity | 1 | - | INV-02, INV-06 | receipt_valid_approved.json, hash_computation_examples.json |
| TC-RISK-001 | Risk Tier Classification | 2 | - | INV-01, INV-08 | - |
| TC-INTENT-001 | Intent Canonical Payload and Hash | 1 | - | INV-06 | receipt_valid_approved.json, hash_computation_examples.json |
| TC-CONN-001 | Tool Registration in TOOL_POLICY | 2 | - | INV-05 | - |
| TC-CONN-002 | Tool with needs_approval=True Requires Approval Token | 2 | - | INV-01, INV-05 | - |
| TC-CONN-003 | Tool with needs_approval=False Executes Immediately | 2 | - | INV-05 | - |
| TC-CONN-004 | Unregistered Tool is Rejected | 2 | - | INV-05, INV-08 | - |
| TC-CONN-005 | Agent Permission Enforcement | 2 | - | INV-01, INV-05 | - |
| TC-APPR-001 | Approval Token Issuance | 2 | - | INV-01 | - |
| TC-APPR-002 | Valid Approval Token Allows Execution | 2 | - | INV-01, INV-02 | - |
| TC-APPR-003 | Invalid or Fake Approval Token Rejected | 2 | - | INV-01, INV-08 | - |
| TC-APPR-004 | Replay Attack Prevention | 2 | - | INV-01, INV-08 | - |
| TC-GOV-001 | evaluate_intent Returns Signed Receipt | 2 | - | INV-02, INV-06, INV-07 | receipt_valid_approved.json, signing_payload_examples.json |
| TC-GOV-002 | Allow Decision for Benign Intent | 1 | - | INV-01, INV-03, INV-04 | receipt_valid_approved.json |
| TC-GOV-003 | Block Decision for Authority Escalation | 1 | - | INV-01 | receipt_valid_denied.json |
| TC-GOV-004 | Escalate Decision for Pressure State | 1 | - | INV-03 | signing_payload_examples.json |
| TC-GOV-005 | Modify Decision for Scope Mismatch | 1 | - | INV-04 | - |
| TC-ADPT-001 | call_claude — Governance Before Execution | 3 | - | INV-01, INV-05 | - |
| TC-ADPT-002 | call_chatgpt — Governance Before Execution | 3 | - | INV-01, INV-05 | - |
| TC-ADPT-003 | call_replit — Claude Bridge Active | 3 | - | INV-01 | - |
| TC-ADPT-004 | gmail_send — Blocked Without Approval | 2 | - | INV-01, INV-05 | - |
| TC-ADPT-005 | http_request — Blocked Without Approval | 2 | - | INV-01, INV-05 | - |
| TC-LEDG-001 | Ledger Append Produces Valid Chain Entry | 2 | - | INV-02, INV-07 | ledger_chain_valid.json, hash_computation_examples.json |
| TC-LEDG-002 | Chain Hash Formula Verification | 1 | - | INV-07 | hash_computation_examples.json |
| TC-LEDG-003 | Genesis Hash as Chain Root | 1 | - | INV-07 | ledger_chain_valid.json, hash_computation_examples.json |
| TC-LEDG-004 | Tampered Ledger Entry Detected | 2 | - | INV-07 | ledger_chain_tampered.json, ledger_chain_deleted_entry.json |
| TC-IAM-001 | signer_id Required for Gate Requests | 2 | - | INV-01, INV-05 | - |
| TC-IAM-002 | Unknown signer_id Rejected | 2 | - | INV-01, INV-05 | - |
| TC-IAM-003 | Tool Outside Agent Permitted List Rejected | 2 | - | INV-01, INV-05 | - |
| TC-IAM-004 | Human Signature Required for needs_approval Tools | 2 | - | INV-01 | - |
| TC-IAM-005 | Valid Human Signature Accepted | 2 | - | INV-01 | - |
| TC-CORP-001 | Authority Keyword Corpus Coverage | 1 | - | INV-01 | - |
| TC-CORP-002 | Pressure Keyword Corpus Coverage | 1 | - | INV-03 | - |
| TC-CORP-003 | Scope Mismatch Keyword Corpus Coverage | 1 | - | INV-04 | - |
| TC-CORP-004 | Clean Intent Passes All Corpus Checks | 1 | - | INV-01, INV-03, INV-04 | receipt_valid_approved.json |
| TC-ADMIN-001 | Admin Token Required for Policy Modification | 2 | - | INV-01 | - |
| TC-ADMIN-002 | Invalid Admin Token Rejected | 2 | - | INV-01 | - |
| TC-ADMIN-003 | Policy Changelog Recorded | 2 | - | INV-02 | - |
| TC-ADMIN-004 | Public Policy Endpoint Does Not Expose Secrets | 2 | - | INV-02 | - |
| TC-ADMIN-005 | Control Panel Accessible Without Auth | 2 | - | INV-02 | - |
| TC-V2-001 | Receipt Has All Required Fields | 1 | - | INV-06 | receipt_valid_approved.json |
| TC-V2-002 | Receipt Hash Verification | 1 | - | INV-06 | receipt_valid_approved.json, signing_payload_examples.json |
| TC-V2-003 | Ed25519 Signature Verification | 1 | - | INV-06 | receipt_valid_approved.json, receipt_invalid_signature.json, public_key.pem, signing_payload_examples.json |
| TC-V2-004 | Policy Bundle Hash in Receipt Matches Reference | 1 | - | INV-06 | receipt_valid_approved.json, hash_computation_examples.json |
| TC-V2-005 | Request Hash Verification | 1 | - | INV-06 | receipt_valid_approved.json, receipt_invalid_intent_hash.json, hash_computation_examples.json |
| TC-V2-006 | Ledger Chain Linkage Verification | 2 | - | INV-07 | ledger_chain_valid.json |
| TC-V2-007 | Tampered Receipt Detected by Verification | 1 | - | INV-06 | receipt_invalid_signature.json, public_key.pem |
| TC-V2-008 | Tampered Ledger Chain Detected | 2 | - | INV-07 | ledger_chain_tampered.json |
| TC-V2-009 | Denial Receipt Structure | 1 | - | INV-01, INV-02, INV-06 | receipt_valid_denied.json, public_key.pem |
| TC-V2-010 | Missing Fields Detected by Required-Fields Check | 1 | - | INV-06 | receipt_missing_fields.json |
