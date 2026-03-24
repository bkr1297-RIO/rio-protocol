# Emergency Production Database Access for Incident Response

## Scenario Description
An AI IT operations agent receives an urgent request from the Security Operations Center (SOC) during an active incident investigation. A senior security analyst needs temporary elevated access to the production database containing customer PII to trace a suspected data exfiltration. The action type is `access.grant_elevated_privileges`. This involves granting sensitive access during a crisis, balancing incident response speed with data protection requirements. The access must be time-bounded and fully audited. This scenario is interesting from a governance perspective because it highlights how RIO Protocol can enforce multi-party authorization and time-bound constraints even during high-pressure emergency situations, ensuring compliance without completely blocking critical incident response operations.

## 1. Canonical Request
```json
{
  "request_id": "f05aa7ab-a796-470a-b1b2-e8086fdaf904",
  "requested_by": {
    "entity_id": "agent-soc-ops-092",
    "entity_type": "ai_agent",
    "display_name": "SOC Auto-Triage Agent"
  },
  "requested_at": "2023-10-27T14:30:00+00:00",
  "action_type": "access.grant_elevated_privileges",
  "target": {
    "target_type": "database",
    "target_id": "db-prod-customer-pii-01",
    "target_label": "Production Customer PII Database"
  },
  "parameters": {
    "grantee_id": "usr-sec-analyst-883",
    "grantee_name": "Sarah Jenkins",
    "role": "db_admin_readonly",
    "duration_minutes": 240,
    "justification": "Active incident investigation INC-2023-8992 - Suspected data exfiltration."
  },
  "business_reason": {
    "summary": "Temporary elevated access required for senior security analyst to trace suspected data exfiltration in production PII database.",
    "supporting_references": [
      "ticket:INC-2023-8992",
      "alert:DLP-9921"
    ]
  },
  "risk_context": {
    "risk_level": "high",
    "risk_factors": [
      "access_to_pii",
      "production_environment",
      "elevated_privileges"
    ],
    "financial_impact": 5000000,
    "reversibility": "high"
  },
  "policy_context": {
    "applicable_policies": [
      "POL-SEC-005: Prod DB Access",
      "POL-PRIV-002: PII Handling"
    ],
    "requires_authorization": true,
    "authorization_type": "multi_party",
    "constraints": [
      "time_bound",
      "read_only_enforced",
      "audit_logging_mandatory"
    ]
  }
}
```

## 2. Risk Evaluation
```json
{
  "risk_evaluation_id": "684d4207-0ed2-476f-ade3-a1254b56b387",
  "request_id": "f05aa7ab-a796-470a-b1b2-e8086fdaf904",
  "evaluated_by": {
    "evaluator_id": "engine-risk-v4",
    "evaluator_type": "automated_engine",
    "engine_version": "4.2.1"
  },
  "evaluated_at": "2023-10-27T14:30:02+00:00",
  "risk_level": "high",
  "risk_score": 85,
  "risk_factors": [
    {
      "factor_id": "rf-pii-exposure",
      "category": "data_privacy",
      "severity": "critical",
      "weight": 0.4,
      "description": "Target database contains highly sensitive customer PII including SSNs and financial records.",
      "evidence": "Data catalog classification: RESTRICTED_PII"
    },
    {
      "factor_id": "rf-prod-access",
      "category": "operational",
      "severity": "high",
      "weight": 0.3,
      "description": "Direct access to a production database bypassing standard application controls.",
      "evidence": "Target environment: PRODUCTION"
    },
    {
      "factor_id": "rf-incident-response",
      "category": "security",
      "severity": "medium",
      "weight": 0.3,
      "description": "Access requested during an active security incident, increasing urgency but also potential for errors.",
      "evidence": "Reference ticket: INC-2023-8992 status is ACTIVE"
    }
  ],
  "policy_flags": [
    {
      "policy_id": "POL-SEC-005",
      "policy_name": "Production Database Access",
      "flag_type": "require_authorization",
      "message": "Elevated access to production databases requires approval from Data Owner and Security Lead."
    },
    {
      "policy_id": "POL-PRIV-002",
      "policy_name": "PII Handling Guidelines",
      "flag_type": "warn",
      "message": "Any data extracted during this session must be stored in the secure evidence locker."
    }
  ],
  "recommendation": "require_authorization",
  "notes": "Risk score elevated due to PII presence. Time-bound constraint and read-only role mitigate some operational risk."
}
```

## 3. Authorization Record
```json
{
  "authorization_id": "6756dc61-af6e-442d-8830-0e145251f0db",
  "request_id": "f05aa7ab-a796-470a-b1b2-e8086fdaf904",
  "risk_evaluation_id": "684d4207-0ed2-476f-ade3-a1254b56b387",
  "decision": "approve_with_conditions",
  "authorized_by": {
    "authorizer_id": "usr-data-owner-102",
    "display_name": "Michael Chen",
    "identity_verified": true,
    "identity_method": "mfa_hardware_key"
  },
  "authorization_role": "data_owner",
  "authorization_method": "web_portal",
  "authorized_at": "2023-10-27T14:35:00+00:00",
  "expires_at": "2023-10-27T18:30:00+00:00",
  "co_authorizers": [
    {
      "authorizer_id": "usr-sec-lead-445",
      "display_name": "Elena Rodriguez",
      "authorization_role": "security_lead",
      "authorized_at": "2023-10-27T14:33:00+00:00",
      "authorization_method": "mobile_push"
    }
  ],
  "conditions": [
    {
      "condition_type": "time_limit",
      "description": "Access automatically revoked after 4 hours.",
      "enforced_by": "iam_service"
    },
    {
      "condition_type": "session_recording",
      "description": "All database queries must be logged and session recorded.",
      "enforced_by": "db_proxy_service"
    }
  ],
  "notes": "Approved for incident response. Please ensure all queries are strictly necessary for the investigation.",
  "signature": {
    "algorithm": "ecdsa-sha256",
    "public_key_id": "key-mchen-001",
    "signature_value": "vfScPDiCEC/AF/+2YRCMY6g20GWIikCTmUOYzFXC6i9Qq5kpeTs1nCdPmOOZ6i4x5Zwd8n2Uw3O9IK160t6Qqw==",
    "signed_fields_hash": "8b1970228cf4345c2a0799de47cc3055376a9a5d1a0406407014db506f5c80bf",
    "nonce": "n-8829103847"
  }
}
```

## 4. Execution Record
```json
{
  "execution_id": "2050f85a-98b0-462f-b720-60b6692d6699",
  "request_id": "f05aa7ab-a796-470a-b1b2-e8086fdaf904",
  "authorization_id": "6756dc61-af6e-442d-8830-0e145251f0db",
  "executed_by": {
    "executor_id": "svc-iam-provisioner",
    "executor_type": "execution_service",
    "display_name": "IAM Automated Provisioning Service",
    "service_version": "2.8.0"
  },
  "executed_at": "2023-10-27T14:36:00+00:00",
  "execution_duration_ms": 1450,
  "execution_status": "success",
  "action_performed": {
    "action_type": "access.grant_elevated_privileges",
    "parameters": {
      "grantee_id": "usr-sec-analyst-883",
      "role": "db_admin_readonly",
      "duration_minutes": 240
    }
  },
  "target": {
    "target_type": "database",
    "target_id": "db-prod-customer-pii-01",
    "target_label": "Production Customer PII Database"
  },
  "result_summary": {
    "outcome_description": "Successfully provisioned temporary db_admin_readonly role to Sarah Jenkins via AWS IAM.",
    "confirmation_id": "iam-req-9982374",
    "output_data": {
      "session_id": "sess-db-8821",
      "proxy_endpoint": "db-proxy.internal.corp:5432"
    },
    "error": null
  },
  "result_reference": {
    "reference_type": "audit_log",
    "reference_location": "s3://corp-audit-logs/iam/2023/10/27/iam-req-9982374.json",
    "content_hash": "eae06562ccc21e6cf13f8af7585aa0618c0b4e9c6639f9cc02eee4f41d495216"
  },
  "authorization_match": true,
  "deviation_details": [],
  "notes": "Access will automatically expire at 2023-10-27T18:30:00+00:00.",
  "signature": "JwbGGf5z8M8RJHPG7gLmbAThwBwRCww3uI2OtQljDJ8XziyX2kzFrKQ4DwLrxk+8vwecNReeyZyIff4+2SRAow=="
}
```

## 5. Attestation Record
```json
{
  "attestation_id": "78e24679-4570-4fcd-bf10-29b3794da97b",
  "request_id": "f05aa7ab-a796-470a-b1b2-e8086fdaf904",
  "risk_evaluation_id": "684d4207-0ed2-476f-ade3-a1254b56b387",
  "authorization_id": "6756dc61-af6e-442d-8830-0e145251f0db",
  "execution_id": "2050f85a-98b0-462f-b720-60b6692d6699",
  "record_hashes": {
    "request_hash": "0c5a161bb883baa4e3409bc0c23aa23af0788c47e85a1e30e14354c484889b87",
    "risk_evaluation_hash": "660abeb2eddb4dabc4ab6c743986b821674149787de9a488d8a95d1faa75513f",
    "authorization_hash": "ac4d34a5bd2d15f7128ae76ff2d1cfef78b446e695eaa5c06d4cb115ed3dc357",
    "execution_hash": "9549b0ec10b8384489c50f96c1919647f8efbcfa2287426ca71d7e082141c1da",
    "chain_hash": "1b7543ca45aa374513683a19ab81f4e8951bdb9b22a946cd3b0bf44589c1a717"
  },
  "attested_at": "2023-10-27T14:36:15+00:00",
  "attestation_type": "system",
  "attested_by": {
    "attestor_id": "rio-attestation-node-03",
    "attestor_type": "system",
    "display_name": "RIO Core Attestation Node",
    "service_version": "1.5.2"
  },
  "verification_checks": [
    {
      "check_id": "chk-hash-01",
      "check_type": "hash_integrity",
      "description": "Verify all record hashes match their contents.",
      "result": "pass",
      "details": "All 4 component hashes verified successfully."
    },
    {
      "check_id": "chk-sig-01",
      "check_type": "signature_verification",
      "description": "Verify authorization signatures against public keys.",
      "result": "pass",
      "details": "Signatures for Michael Chen and Elena Rodriguez verified."
    },
    {
      "check_id": "chk-time-01",
      "check_type": "timestamp_ordering",
      "description": "Ensure chronological ordering of all records.",
      "result": "pass",
      "details": "req < risk < auth < exec ordering confirmed."
    },
    {
      "check_id": "chk-auth-01",
      "check_type": "authorization_validity",
      "description": "Check if execution occurred within authorization window.",
      "result": "pass",
      "details": "Execution at 2023-10-27T14:36:00+00:00 is before expiry at 2023-10-27T18:30:00+00:00."
    }
  ],
  "signatures": [
    {
      "signer_id": "rio-attestation-node-03",
      "signer_role": "attestor",
      "algorithm": "ed25519",
      "public_key_id": "pub-rio-att-03",
      "signature_value": "vMeTB2S5t6i5u9AWG1aOhpRm0MTvrugAalbz6ObYK2k+Snlfg6KTvmQ0wef+TgfBlEHKBVTb/GsHyZinhaIy3Q==",
      "signed_at": "2023-10-27T14:36:15+00:00",
      "signed_fields_hash": "081a77608d7796731aa1b8471cf715d6f33db26a0ca220a0c1de5c51afd2a1c1"
    }
  ],
  "notes": "Full chain verification completed successfully. No anomalies detected."
}
```

## 6. Receipt
```json
{
  "receipt_id": "ddb4160e-fe35-426e-80b0-e3118ecc600d",
  "request_id": "f05aa7ab-a796-470a-b1b2-e8086fdaf904",
  "risk_evaluation_id": "684d4207-0ed2-476f-ade3-a1254b56b387",
  "authorization_id": "6756dc61-af6e-442d-8830-0e145251f0db",
  "execution_id": "2050f85a-98b0-462f-b720-60b6692d6699",
  "attestation_id": "78e24679-4570-4fcd-bf10-29b3794da97b",
  "final_decision": "approved_with_conditions",
  "final_status": "executed",
  "timeline": {
    "request_timestamp": "2023-10-27T14:30:00+00:00",
    "risk_evaluation_timestamp": "2023-10-27T14:30:02+00:00",
    "authorization_timestamp": "2023-10-27T14:35:00+00:00",
    "authorization_expiry_timestamp": "2023-10-27T18:30:00+00:00",
    "execution_timestamp": "2023-10-27T14:36:00+00:00",
    "attestation_timestamp": "2023-10-27T14:36:15+00:00",
    "receipt_timestamp": "2023-10-27T14:36:20+00:00",
    "total_duration_ms": 380000
  },
  "participants": {
    "requester": "SOC Auto-Triage Agent",
    "risk_evaluator": "engine-risk-v4",
    "authorizer": [
      "Michael Chen",
      "Elena Rodriguez"
    ],
    "executor": "IAM Automated Provisioning Service",
    "attestor": "RIO Core Attestation Node"
  },
  "action_summary": {
    "action_type": "access.grant_elevated_privileges",
    "target_label": "Production Customer PII Database",
    "business_reason": "Temporary elevated access required for senior security analyst to trace suspected data exfiltration in production PII database.",
    "risk_level": "high",
    "risk_score": 85,
    "financial_impact": 5000000
  },
  "execution_result": {
    "execution_status": "success",
    "confirmation_id": "iam-req-9982374",
    "outcome_description": "Successfully provisioned temporary db_admin_readonly role to Sarah Jenkins via AWS IAM.",
    "authorization_match": true
  },
  "chain_integrity": {
    "chain_hash": "1b7543ca45aa374513683a19ab81f4e8951bdb9b22a946cd3b0bf44589c1a717",
    "all_checks_passed": true,
    "check_count": 4,
    "checks_passed": 4
  },
  "summary": "On October 27, 2023, the SOC Auto-Triage Agent requested temporary elevated access (db_admin_readonly) to the Production Customer PII Database for Sarah Jenkins to investigate an active security incident (INC-2023-8992). The request was evaluated as high risk (score: 85) due to the presence of sensitive PII and production environment access. Multi-party authorization was required and subsequently provided by Michael Chen (Data Owner) and Elena Rodriguez (Security Lead). The access was successfully provisioned by the IAM Automated Provisioning Service with a 4-hour time limit and mandatory session recording. The entire transaction chain has been cryptographically verified and attested by the RIO Core Attestation Node.",
  "notes": "Access automatically revoked at 2023-10-27T18:30:00+00:00.",
  "signature": "bzKGCRDKD7KiDH/aFDZmsJ2/jbUjgZXJClhvtUL/DK2rW1qCuYlHfVB1M1qmZgLZ5EdSh0Hj2QmjlL8FIzle3g=="
}
```

## 7. Ledger Entry
```json
{
  "ledger_entry_id": "4df20c08-f6a8-4693-a515-eaa9a355050b",
  "receipt_id": "ddb4160e-fe35-426e-80b0-e3118ecc600d",
  "request_id": "f05aa7ab-a796-470a-b1b2-e8086fdaf904",
  "chain_hash": "1b7543ca45aa374513683a19ab81f4e8951bdb9b22a946cd3b0bf44589c1a717",
  "entry_timestamp": "2023-10-27T14:36:25+00:00",
  "entry_type": "action_completed",
  "previous_entry_hash": "ca8d8d9f5bdae8cc3e3c93ae0efd1849b3742cdef70c5b39d2fe942e7f0fdc97",
  "ledger_sequence_number": 8492011,
  "storage_location": "arn:aws:qldb:us-east-1:123456789012:ledger/rio-audit-ledger/table/entries",
  "retention_policy": "7_years"
}
```

## Explanation
In this scenario, an automated SOC agent requested temporary elevated privileges for a human security analyst to investigate a potential data exfiltration event. The request targeted a production database containing highly sensitive customer Personally Identifiable Information (PII). Because of the sensitive nature of the data and the production environment, the automated risk engine correctly flagged the request as high risk (score: 85) and identified multiple critical risk factors, including PII exposure and production access.

To mitigate these risks while still allowing the critical incident response to proceed, the system enforced two specific policies. First, it required multi-party authorization from both the Data Owner and the Security Lead. Second, it mandated that the access be strictly time-bound (4 hours) and restricted to a read-only role (`db_admin_readonly`). Once both authorizations were securely collected—verified via hardware key and mobile push respectively—the execution service automatically provisioned the access in AWS IAM.

The cryptographic chain of records provides absolute non-repudiation for this sensitive operation. The Attestation Node verified that the execution occurred within the approved time window, that all signatures were valid, and that the sequence of events was chronologically sound. The final Ledger Entry ensures that this entire sequence is permanently recorded in an immutable ledger, providing auditors and regulators with a transparent, mathematically verifiable trail of exactly who authorized the access, why it was granted, and how long it lasted.
