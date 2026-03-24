# Data Deletion

## Scenario Description
A detailed paragraph describing the scenario, the actors involved, why this action is being requested, and what makes it interesting from a governance perspective.

## 1. Canonical Request
```json
{
    "canonical_request": {
        "request_id": "07ac41f8-84eb-4dde-a9d3-ef1674b3c5bb",
        "requested_by": {
            "entity_id": "comp-agent-gdpr-001",
            "entity_type": "ai_agent",
            "display_name": "GDPR Compliance Agent"
        },
        "requested_at": "2026-03-24T21:32:37.975246+00:00",
        "action_type": "data.execute_deletion_request",
        "target": {
            "target_type": "customer_record",
            "target_id": "cust-eu-8847",
            "target_label": "Customer Record for cust-eu-8847"
        },
        "parameters": {
            "deletion_scope": [
                "crm",
                "analytics_platform",
                "email_marketing_system",
                "backup_archives"
            ],
            "legal_justification": "GDPR Article 17",
            "requester_identity_proof": "urn:some:identity:proof:system:and:value"
        },
        "business_reason": {
            "summary": "Fulfillment of a GDPR Article 17 'right to erasure' request from a European customer.",
            "supporting_references": [
                "https://gdpr-info.eu/art-17-gdpr/"
            ]
        },
        "risk_context": {
            "risk_level": "high",
            "risk_factors": [
                "irreversible_action",
                "regulatory_compliance_impact",
                "potential_for_business_critical_data_loss"
            ],
            "financial_impact": "Potential for significant fines under GDPR if not handled correctly.",
            "reversibility": "irreversible"
        },
        "policy_context": {
            "applicable_policies": [
                "policy-gdpr-data-handling-v2",
                "policy-data-deletion-v1.5"
            ],
            "requires_authorization": true,
            "authorization_type": "human_in_the_loop",
            "constraints": [
                "time_bound_execution_window_24h"
            ]
        }
    }
}
```

## 2. Risk Evaluation
```json
{
    "risk_evaluation": {
        "risk_evaluation_id": "60441e9e-eb76-4fac-9b17-151e0ff7c64f",
        "request_id": "07ac41f8-84eb-4dde-a9d3-ef1674b3c5bb",
        "evaluated_by": {
            "evaluator_id": "risk-engine-v3.2.1",
            "evaluator_type": "automated_engine",
            "engine_version": "3.2.1"
        },
        "evaluated_at": "2026-03-24T21:34:37.975278+00:00",
        "risk_level": "high",
        "risk_score": 85,
        "risk_factors": [
            {
                "factor_id": "RF001",
                "category": "compliance",
                "severity": "critical",
                "weight": 0.5,
                "description": "Failure to comply with a GDPR data deletion request can lead to significant regulatory fines.",
                "evidence": "GDPR Article 17 is explicitly cited in the request."
            },
            {
                "factor_id": "RF002",
                "category": "operational",
                "severity": "high",
                "weight": 0.3,
                "description": "The deletion spans multiple critical systems, increasing the risk of partial or failed execution.",
                "evidence": "Deletion scope includes CRM, analytics, email marketing, and backup archives."
            },
            {
                "factor_id": "RF003",
                "category": "data_privacy",
                "severity": "high",
                "weight": 0.2,
                "description": "Accidental deletion of the wrong customer's data would be a major data breach.",
                "evidence": "The action is irreversible."
            }
        ],
        "policy_flags": [
            {
                "policy_id": "policy-gdpr-data-handling-v2",
                "policy_name": "GDPR Data Handling Policy",
                "flag_type": "require_authorization",
                "message": "High-risk data deletion under GDPR requires DPO authorization."
            },
            {
                "policy_id": "policy-data-deletion-v1.5",
                "policy_name": "Data Deletion Policy",
                "flag_type": "require_review",
                "message": "Deletion from backup archives requires technical review to ensure integrity."
            }
        ],
        "recommendation": "require_authorization",
        "notes": "Automated risk assessment indicates a high-risk operation due to regulatory and operational factors. Human authorization by a Data Protection Officer (DPO) is strongly recommended before execution."
    }
}
```

## 3. Authorization Record
```json
{
    "authorization_record": {
        "authorization_id": "9e357a76-1c4e-4908-abda-8a440eb93e23",
        "request_id": "07ac41f8-84eb-4dde-a9d3-ef1674b3c5bb",
        "risk_evaluation_id": "60441e9e-eb76-4fac-9b17-151e0ff7c64f",
        "decision": "approve",
        "authorized_by": {
            "authorizer_id": "dpo-jane.doe",
            "display_name": "Jane Doe",
            "identity_verified": true,
            "identity_method": "sso_multifactor_authentication"
        },
        "authorization_role": "Data Protection Officer",
        "authorization_method": "web_portal",
        "authorized_at": "2026-03-24T21:37:37.975281+00:00",
        "expires_at": "2026-03-24T22:42:37.975283+00:00",
        "co_authorizers": [],
        "conditions": [],
        "notes": "Reviewed the request and risk assessment. The request is valid under GDPR Article 17. The deletion plan appears sound. Approving for execution within the defined time window.",
        "signature": {
            "algorithm": "ecdsa-sha256",
            "public_key_id": "key-dpo-prod-001",
            "signature_value": "MEYCIQDa8Z3o2w5d1h7k6q8a5d1h7k6q8a5d1h7k6q8a5d1h7k6q8a5d1h7k6q8a5d1h7k6q8a5d1h7k6q8a5Q==",
            "signed_fields_hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            "nonce": "a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"
        }
    }
}
```

## 4. Execution Record
```json
{
    "execution_record": {
        "execution_id": "677bcea5-c115-4e35-8e54-ed8627933b13",
        "request_id": "07ac41f8-84eb-4dde-a9d3-ef1674b3c5bb",
        "authorization_id": "9e357a76-1c4e-4908-abda-8a440eb93e23",
        "executed_by": {
            "executor_id": "data-deletion-service-v1.8",
            "executor_type": "execution_service",
            "display_name": "Data Deletion Service",
            "service_version": "1.8"
        },
        "executed_at": "2026-03-24T21:40:37.975288+00:00",
        "execution_duration_ms": 12580,
        "execution_status": "success",
        "action_performed": {
            "action_type": "data.execute_deletion_request",
            "parameters": {
                "deletion_scope": [
                    "crm",
                    "analytics_platform",
                    "email_marketing_system",
                    "backup_archives"
                ],
                "legal_justification": "GDPR Article 17",
                "requester_identity_proof": "urn:some:identity:proof:system:and:value"
            }
        },
        "target": {
            "target_type": "customer_record",
            "target_id": "cust-eu-8847",
            "target_label": "Customer Record for cust-eu-8847"
        },
        "result_summary": {
            "outcome_description": "Successfully deleted all records for customer cust-eu-8847 from all specified systems.",
            "confirmation_id": "del-confirm-9f8e7d6c5b4a",
            "output_data": {
                "crm_status": "deleted",
                "analytics_status": "deleted",
                "email_marketing_status": "deleted",
                "backup_archives_status": "deleted"
            },
            "error": null
        },
        "result_reference": {
            "reference_type": "log_file",
            "reference_location": "s3://data-deletion-logs/2026/03/24/677bcea5-c115-4e35-8e54-ed8627933b13.log",
            "content_hash": "b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2"
        },
        "authorization_match": true,
        "deviation_details": [],
        "notes": "Execution completed within the authorized time window. All systems reported successful deletion.",
        "signature": {
            "algorithm": "rsa-sha256",
            "public_key_id": "key-exec-prod-002",
            "signature_value": "MI...DA==",
            "signed_fields_hash": "c1d2e3f4a5b6c1d2e3f4a5b6c1d2e3f4a5b6c1d2e3f4a5b6c1d2e3f4a5b6c1d2",
            "nonce": "c1d2e3f4-a5b6-c1d2-e3f4-a5b6c1d2e3f4"
        }
    }
}
```

## 5. Attestation Record
```json
{
    "attestation_record": {
        "attestation_id": "7ae15451-87df-49bb-b77c-405634cad671",
        "request_id": "07ac41f8-84eb-4dde-a9d3-ef1674b3c5bb",
        "risk_evaluation_id": "60441e9e-eb76-4fac-9b17-151e0ff7c64f",
        "authorization_id": "9e357a76-1c4e-4908-abda-8a440eb93e23",
        "execution_id": "677bcea5-c115-4e35-8e54-ed8627933b13",
        "record_hashes": {
            "request_hash": "d1e2f3a4b5c6d1e2f3a4b5c6d1e2f3a4b5c6d1e2f3a4b5c6d1e2f3a4b5c6d1e2",
            "risk_evaluation_hash": "e1f2a3b4c5d6e1f2a3b4c5d6e1f2a3b4c5d6e1f2a3b4c5d6e1f2a3b4c5d6e1f2",
            "authorization_hash": "f1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d5e6f1a2b3c4d5e6f1a2",
            "execution_hash": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2",
            "chain_hash": "b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2"
        },
        "attested_at": "2026-03-24T21:41:37.975290+00:00",
        "attestation_type": "system",
        "attested_by": {
            "attestor_id": "rio-attestation-service-v1.2",
            "attestor_type": "attestation_service",
            "display_name": "RIO Attestation Service",
            "service_version": "1.2"
        },
        "verification_checks": [
            {
                "check_id": "chk-hash-integrity",
                "check_type": "hash_integrity",
                "description": "Verify that all record hashes are valid and consistent.",
                "result": "pass",
                "details": "All record hashes verified successfully."
            },
            {
                "check_id": "chk-auth-validity",
                "check_type": "authorization_validity",
                "description": "Verify that the authorization was valid at the time of execution.",
                "result": "pass",
                "details": "Execution occurred within the authorized time window."
            },
            {
                "check_id": "chk-chain-continuity",
                "check_type": "chain_continuity",
                "description": "Verify the cryptographic chain of all records.",
                "result": "pass",
                "details": "Chain hash is consistent across all records."
            }
        ],
        "signatures": [
            {
                "signer_id": "rio-attestation-service-v1.2",
                "signer_role": "attestation_service",
                "algorithm": "ecdsa-sha256",
                "public_key_id": "key-attest-prod-001",
                "signature_value": "MEYCIQ...==",
                "signed_at": "2026-03-24T21:41:37.975290+00:00",
                "signed_fields_hash": "d1e2f3a4b5c6d1e2f3a4b5c6d1e2f3a4b5c6d1e2f3a4b5c6d1e2f3a4b5c6d1e2"
            }
        ],
        "notes": "System-level attestation completed. All verification checks passed, confirming the integrity and continuity of the RIO records for this action."
    }
}
```

## 6. Receipt
```json
{
    "receipt": {
        "receipt_id": "e9d39fb3-cc73-415c-84bf-ea5e6c8fbb2c",
        "request_id": "07ac41f8-84eb-4dde-a9d3-ef1674b3c5bb",
        "risk_evaluation_id": "60441e9e-eb76-4fac-9b17-151e0ff7c64f",
        "authorization_id": "9e357a76-1c4e-4908-abda-8a440eb93e23",
        "execution_id": "677bcea5-c115-4e35-8e54-ed8627933b13",
        "attestation_id": "7ae15451-87df-49bb-b77c-405634cad671",
        "final_decision": "approved",
        "final_status": "executed",
        "timeline": {
            "request_timestamp": "2026-03-24T21:32:37.975246+00:00",
            "risk_evaluation_timestamp": "2026-03-24T21:34:37.975278+00:00",
            "authorization_timestamp": "2026-03-24T21:37:37.975281+00:00",
            "authorization_expiry_timestamp": "2026-03-24T22:42:37.975283+00:00",
            "execution_timestamp": "2026-03-24T21:40:37.975288+00:00",
            "attestation_timestamp": "2026-03-24T21:41:37.975290+00:00",
            "receipt_timestamp": "2026-03-24T21:42:37.975292+00:00",
            "total_duration_ms": 600046
        },
        "participants": {
            "requester": "GDPR Compliance Agent (comp-agent-gdpr-001)",
            "risk_evaluator": "Risk Engine v3.2.1 (risk-engine-v3.2.1)",
            "authorizer": "Jane Doe (dpo-jane.doe)",
            "executor": "Data Deletion Service v1.8 (data-deletion-service-v1.8)",
            "attestor": "RIO Attestation Service v1.2 (rio-attestation-service-v1.2)"
        },
        "action_summary": {
            "action_type": "data.execute_deletion_request",
            "target_label": "Customer Record for cust-eu-8847",
            "business_reason": "Fulfillment of a GDPR Article 17 'right to erasure' request from a European customer.",
            "risk_level": "high",
            "risk_score": 85,
            "financial_impact": "Potential for significant fines under GDPR if not handled correctly."
        },
        "execution_result": {
            "execution_status": "success",
            "confirmation_id": "del-confirm-9f8e7d6c5b4a",
            "outcome_description": "Successfully deleted all records for customer cust-eu-8847 from all specified systems.",
            "authorization_match": true
        },
        "chain_integrity": {
            "chain_hash": "b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2",
            "all_checks_passed": true,
            "check_count": 3,
            "checks_passed": 3
        },
        "summary": "On March 24, 2026, the GDPR Compliance Agent initiated a high-risk data deletion request for European customer cust-eu-8847 to comply with a GDPR Article 17 'right to erasure' request. The automated risk engine evaluated the request as high-risk (score: 85) due to its irreversibility and potential for regulatory fines. The request was then routed to Data Protection Officer Jane Doe, who reviewed the details and provided explicit authorization via the web portal. The Data Deletion Service successfully executed the deletion across the CRM, analytics platform, email marketing system, and backup archives. The entire process was cryptographically recorded and attested, confirming the integrity and validity of the action from request to execution.",
        "notes": "This receipt provides a comprehensive, non-repudiable summary of the entire action lifecycle.",
        "signature": {
            "algorithm": "ecdsa-sha256",
            "public_key_id": "key-receipt-prod-001",
            "signature_value": "MEYCIQ...==",
            "signed_fields_hash": "e1f2a3b4c5d6e1f2a3b4c5d6e1f2a3b4c5d6e1f2a3b4c5d6e1f2a3b4c5d6e1f2"
        }
    }
}
```

## 7. Ledger Entry
```json
{
    "ledger_entry": {
        "ledger_entry_id": "a09db43c-3a97-4507-a644-957ab30b3dab",
        "receipt_id": "e9d39fb3-cc73-415c-84bf-ea5e6c8fbb2c",
        "request_id": "07ac41f8-84eb-4dde-a9d3-ef1674b3c5bb",
        "chain_hash": "b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2d3e4f5a6b1c2",
        "entry_timestamp": "2026-03-24T21:42:47.975293+00:00",
        "entry_type": "action_completed",
        "previous_entry_hash": "c1d2e3f4a5b6c1d2e3f4a5b6c1d2e3f4a5b6c1d2e3f4a5b6c1d2e3f4a5b6c1d2",
        "ledger_sequence_number": 1337,
        "storage_location": "s3://rio-ledger-archive/2026/03/24/a09db43c-3a97-4507-a644-957ab30b3dab.json",
        "retention_policy": "retain_indefinitely_for_audit"
    }
}
```
## Explanation

This end-to-end flow documents a high-risk, irreversible data deletion action triggered by a GDPR Article 17 request. The process begins with an AI agent, the **GDPR Compliance Agent**, programmatically issuing a `canonical_request`. This request is not just a simple API call; it's a structured, self-describing data object that encapsulates the full business and risk context of the action. It clearly defines the *what* (delete customer data), the *who* (customer `cust-eu-8847`), the *why* (GDPR compliance), and the inherent risks, such as the action's irreversibility and potential for regulatory fines. This initial object serves as the foundation for the entire governance lifecycle, ensuring that all subsequent steps are grounded in a shared, unambiguous understanding of the request.

Upon receiving the request, the RIO control plane routes it to an automated `risk_evaluation` engine. This engine analyzes the `risk_context` and `policy_context` from the request, along with its own internal rules, to produce a comprehensive risk assessment. In this scenario, the engine identifies several critical risk factors: the action's direct link to GDPR compliance, the operational complexity of deleting data across four distinct systems (CRM, analytics, email, and backups), and the severe consequences of accidental data loss. The engine quantifies this risk with a score of 85 and, crucially, triggers two policy flags. The first, `require_authorization`, is a hard requirement from the GDPR Data Handling Policy, mandating that a Data Protection Officer (DPO) must approve any high-risk deletion. The second, `require_review`, highlights the need for technical oversight on backup archive modifications. The evaluation's recommendation is therefore unequivocal: `require_authorization`.

The `authorization_record` captures the critical human-in-the-loop decision. The request is escalated to the designated DPO, Jane Doe, who reviews the `canonical_request` and the `risk_evaluation`. The RIO system presents her with a clear, consolidated view of the proposed action, its justification, and the associated risks. Her approval, captured via a secure web portal, is cryptographically signed, creating a verifiable and non-repudiable record of her decision. This record also includes a time-bound validity window (`expires_at`), ensuring the execution command is only valid for a limited period, preventing the execution of stale, un-re-evaluated approvals. This time-bound authorization is a key security feature, mitigating the risk of a compromised execution token being used indefinitely.

Once authorized, the `execution_record` is generated by the Data Deletion Service. This service is architected to only accept commands that are accompanied by a valid, unexpired authorization from the RIO control plane. Before proceeding, it verifies the `authorization_match`, ensuring the action it is about to perform is precisely the one that was approved. The record details the successful deletion across all target systems and captures the `execution_duration_ms` and a final `confirmation_id`. This creates a clear audit trail of what was done, when it was done, and by which system. Any deviation from the authorized parameters would have been flagged, and the execution would have been halted, demonstrating the principle of least privilege and strict adherence to the approved plan.

Finally, the `attestation_record`, `receipt`, and `ledger_entry` provide the cryptographic proof and summary of the entire lifecycle. The `attestation_service` performs a series of automated `verification_checks`, including verifying the hash integrity of each record and the continuity of the cryptographic chain (`chain_hash`). This ensures that no part of the record has been tampered with after the fact. The `receipt` then compiles all key information into a single, human-readable summary, providing a plain-language narrative of the event for stakeholders like auditors or regulators. The final `ledger_entry` commits the immutable hash of the entire chain to a secure, append-only ledger, creating a permanent, non-repudiable audit record that guarantees the integrity and provenance of the entire action from request to verified execution.
