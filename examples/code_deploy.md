# Code Deploy: Emergency Security Patch

## Scenario Description
A critical remote code execution (RCE) vulnerability (CVE-2026-4471) has been discovered in the company's production API gateway, a core piece of infrastructure handling all incoming customer traffic. An AI DevOps agent, "DeployBot-9000", has developed and successfully tested a security patch. After passing all 847 automated integration and regression tests, the AI agent is requesting an emergency deployment to production. This action falls outside the standard maintenance window, creating a governance challenge. The RIO Protocol is used to manage the tension between the urgency of patching a critical vulnerability and the inherent risk of an out-of-band production deployment, ensuring the action is reviewed, authorized, and securely logged.

## 1. Canonical Request
```json
{
  "canonical_request": {
    "request_id": "a833fdef-020d-478e-81c2-efd9fc7e5f35",
    "requested_by": {
      "entity_id": "svc-agent-d9b8c7e6",
      "entity_type": "ai_agent",
      "display_name": "DeployBot-9000"
    },
    "requested_at": "2026-03-24T21:42:48.686393Z",
    "action_type": "infrastructure.deploy_to_production",
    "target": {
      "target_type": "api_gateway_cluster",
      "target_id": "prod-us-east-1-apigw-v3",
      "target_label": "Production API Gateway (us-east-1)"
    },
    "parameters": {
      "source_repository": "https://git.example.com/infra/api-gateway.git",
      "commit_hash": "e8a3f4d2c1b0a9e8d7f6c5b4a3b2c1d0e9f8a7b6",
      "docker_image_tag": "v3.14.2-patch-cve-2026-4471",
      "deployment_strategy": "rolling_update",
      "rollback_plan": "revert_to_v3.14.1"
    },
    "business_reason": {
      "summary": "Emergency deployment of a critical security patch for CVE-2026-4471, a remote code execution vulnerability in the production API gateway.",
      "supporting_references": [
        "https://nvd.nist.gov/vuln/detail/CVE-2026-4471",
        "https://internal.jira.com/browse/SEC-9512"
      ]
    },
    "risk_context": {
      "risk_level": "high",
      "risk_factors": [
        "production_deployment",
        "out_of_change_window",
        "critical_security_vulnerability"
      ],
      "financial_impact": "potential_high",
      "reversibility": "high"
    },
    "policy_context": {
      "applicable_policies": [
        "pol-sec-004-emergency-change-management",
        "pol-inf-002-production-access"
      ],
      "requires_authorization": true,
      "authorization_type": "time_bound_human_approval",
      "constraints": [
        "max_duration_1_hour",
        "requires_sre_lead_approval"
      ]
    }
  }
}
```

## 2. Risk Evaluation
```json
{
  "risk_evaluation": {
    "risk_evaluation_id": "bf0a723c-2334-475f-baf3-8dc8f7bdffbb",
    "request_id": "a833fdef-020d-478e-81c2-efd9fc7e5f35",
    "evaluated_by": {
      "evaluator_id": "risk-engine-v2.3.1",
      "evaluator_type": "automated_engine",
      "engine_version": "2.3.1"
    },
    "evaluated_at": "2026-03-24T21:43:18.686393Z",
    "risk_level": "high",
    "risk_score": 85,
    "risk_factors": [
      {
        "factor_id": "rf-011",
        "category": "security",
        "severity": "critical",
        "weight": 0.6,
        "description": "The deployment addresses a critical RCE vulnerability (CVE-2026-4471) which, if unpatched, could lead to a full system compromise.",
        "evidence": "NVD CVSS Score 9.8"
      },
      {
        "factor_id": "rf-023",
        "category": "operational",
        "severity": "high",
        "weight": 0.3,
        "description": "The deployment is outside the standard, pre-approved change management window, increasing the risk of unforeseen operational disruption.",
        "evidence": "Request timestamp is outside of defined change windows in policy pol-sec-004."
      },
      {
        "factor_id": "rf-045",
        "category": "compliance",
        "severity": "medium",
        "weight": 0.1,
        "description": "An emergency deployment requires post-incident review and documentation to maintain compliance with internal audit controls.",
        "evidence": "Policy pol-sec-004-emergency-change-management, section 5.2"
      }
    ],
    "policy_flags": [
      {
        "policy_id": "pol-sec-004-emergency-change-management",
        "policy_name": "Emergency Change Management Policy",
        "flag_type": "require_authorization",
        "message": "Emergency production deployment requires explicit authorization from a designated SRE Lead."
      },
      {
        "policy_id": "pol-inf-002-production-access",
        "policy_name": "Production Access Control Policy",
        "flag_type": "log_only",
        "message": "Automated deployment to production environment logged for audit."
      }
    ],
    "recommendation": "require_authorization",
    "notes": "Recommendation is to proceed with authorization due to the critical nature of the security vulnerability. The risk of inaction is higher than the risk of a carefully monitored emergency deployment."
  }
}
```

## 3. Authorization Record
```json
{
  "authorization_record": {
    "authorization_id": "b1e81f51-5bf4-457b-b5e4-d19bcd743c99",
    "request_id": "a833fdef-020d-478e-81c2-efd9fc7e5f35",
    "risk_evaluation_id": "bf0a723c-2334-475f-baf3-8dc8f7bdffbb",
    "decision": "approve_with_conditions",
    "authorized_by": {
      "authorizer_id": "user-a4b1c2d3",
      "display_name": "Alice Johnson, SRE Lead",
      "identity_verified": true,
      "identity_method": "okta_sso_mfa"
    },
    "authorization_role": "sre_lead",
    "authorization_method": "mobile_push",
    "authorized_at": "2026-03-24T21:47:48.686393Z",
    "expires_at": "2026-03-24T21:57:48.686393Z",
    "co_authorizers": [],
    "conditions": [
      {
        "condition_type": "time_bound_execution",
        "description": "Deployment must be initiated within 10 minutes of authorization.",
        "enforced_by": "rio_control_plane"
      },
      {
        "condition_type": "monitoring_requirement",
        "description": "SRE on-call must actively monitor gateway performance and error rates for 60 minutes post-deployment.",
        "enforced_by": "manual_procedure_attestation"
      }
    ],
    "notes": "Approved. The urgency of the CVE outweighs the risk of an out-of-band deployment. Proceed with caution and monitor closely.",
    "signature": {
      "algorithm": "ecdsa-sha256",
      "public_key_id": "key-alice-j-2025",
      "signature_value": "MEYCIQDp9q7yJ/2wE+O/5F9aZ/1bN/7cQ8rD+J/6aZ/1bN/7cQIhAO/5F9aZ/1bN/7cQ8rD+J/6aZ/1bN/7cQ8rD+J/6aZ/1",
      "signed_fields_hash": "f4b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1",
      "nonce": "n-12345-abcdef"
    }
  }
}
```

## 4. Execution Record
```json
{
  "execution_record": {
    "execution_id": "e22fb8cd-930e-4bc2-b131-0af21957ec59",
    "request_id": "a833fdef-020d-478e-81c2-efd9fc7e5f35",
    "authorization_id": "b1e81f51-5bf4-457b-b5e4-d19bcd743c99",
    "executed_by": {
      "executor_id": "exec-gw-prod-us-east-1",
      "executor_type": "execution_gateway",
      "display_name": "RIO Execution Gateway (prod-us-east-1)",
      "service_version": "1.7.2"
    },
    "executed_at": "2026-03-24T21:49:48.686393Z",
    "execution_duration_ms": 45210,
    "execution_status": "success",
    "action_performed": {
      "action_type": "infrastructure.deploy_to_production",
      "parameters": {
        "source_repository": "https://git.example.com/infra/api-gateway.git",
        "commit_hash": "e8a3f4d2c1b0a9e8d7f6c5b4a3b2c1d0e9f8a7b6",
        "docker_image_tag": "v3.14.2-patch-cve-2026-4471",
        "deployment_strategy": "rolling_update"
      }
    },
    "target": {
      "target_type": "api_gateway_cluster",
      "target_id": "prod-us-east-1-apigw-v3",
      "target_label": "Production API Gateway (us-east-1)"
    },
    "result_summary": {
      "outcome_description": "Deployment completed successfully across all 24 nodes in the cluster.",
      "confirmation_id": "deploy-receipt-987654321",
      "output_data": {
        "nodes_updated": 24,
        "nodes_total": 24,
        "final_version": "v3.14.2-patch-cve-2026-4471"
      },
      "error": null
    },
    "result_reference": {
      "reference_type": "splunk_log",
      "reference_location": "https://splunk.example.com/app/search/search?q=index%3Dprod%20source%3Ddeployment%20confirmation_id%3Ddeploy-receipt-987654321",
      "content_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2"
    },
    "authorization_match": true,
    "deviation_details": [],
    "notes": "Execution was initiated within the authorized time window and completed without errors.",
    "signature": {
      "algorithm": "ecdsa-sha256",
      "public_key_id": "key-exec-gw-prod-1",
      "signature_value": "MEQCIA/5F9aZ/1bN/7cQ8rD+J/6aZ/1bN/7cQ8rD+J/6aZ/1AiA/5F9aZ/1bN/7cQ8rD+J/6aZ/1bN/7cQ8rD+J/6aZ/1",
      "signed_fields_hash": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
      "nonce": "n-54321-fedcba"
    }
  }
}
```

## 5. Attestation Record
```json
{
  "attestation_record": {
    "attestation_id": "4a1d82bb-1270-45d0-ba4e-9b64acbfa277",
    "request_id": "a833fdef-020d-478e-81c2-efd9fc7e5f35",
    "risk_evaluation_id": "bf0a723c-2334-475f-baf3-8dc8f7bdffbb",
    "authorization_id": "b1e81f51-5bf4-457b-b5e4-d19bcd743c99",
    "execution_id": "e22fb8cd-930e-4bc2-b131-0af21957ec59",
    "record_hashes": {
      "request_hash": "c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4",
      "risk_evaluation_hash": "d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5",
      "authorization_hash": "e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6",
      "execution_hash": "f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7",
      "chain_hash": "a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1"
    },
    "attested_at": "2026-03-24T21:50:48.686393Z",
    "attestation_type": "system",
    "attested_by": {
      "attestor_id": "rio-attestor-service-v1.2.0",
      "attestor_type": "attestation_service",
      "display_name": "RIO Attestor Service",
      "service_version": "1.2.0"
    },
    "verification_checks": [
      {
        "check_id": "vc-001",
        "check_type": "hash_integrity",
        "description": "Verify SHA-256 hashes of all records in the chain.",
        "result": "pass",
        "details": "All record hashes match their content."
      },
      {
        "check_id": "vc-002",
        "check_type": "signature_verification",
        "description": "Verify all cryptographic signatures in the chain.",
        "result": "pass",
        "details": "Authorization and execution signatures verified successfully."
      },
      {
        "check_id": "vc-003",
        "check_type": "authorization_validity",
        "description": "Verify that execution occurred within the authorized time window.",
        "result": "pass",
        "details": "Execution at 21:49:48Z was within the 21:47:48Z to 21:57:48Z authorization window."
      },
      {
        "check_id": "vc-004",
        "check_type": "chain_continuity",
        "description": "Verify the integrity of the cryptographic chain hash.",
        "result": "pass",
        "details": "Chain hash correctly links all records."
      }
    ],
    "signatures": [
      {
        "signer_id": "rio-attestor-service-v1.2.0",
        "signer_role": "attestor",
        "algorithm": "ecdsa-sha256",
        "public_key_id": "key-rio-attestor-1",
        "signature_value": "MEUCIQDaZ/1bN/7cQ8rD+J/6aZ/1bN/7cQ8rD+J/6aZ/1bN/7cQIhAP/1bN/7cQ8rD+J/6aZ/1bN/7cQ8rD+J/6aZ/1bN/7c=",
        "signed_at": "2026-03-24T21:50:48.686393Z",
        "signed_fields_hash": "b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2"
      }
    ],
    "notes": "System attestation complete. All verification checks passed."
  }
}
```

## 6. Receipt
```json
{
  "receipt": {
    "receipt_id": "d291ce57-f5ec-4dba-a0b0-8654aa3027b8",
    "request_id": "a833fdef-020d-478e-81c2-efd9fc7e5f35",
    "risk_evaluation_id": "bf0a723c-2334-475f-baf3-8dc8f7bdffbb",
    "authorization_id": "b1e81f51-5bf4-457b-b5e4-d19bcd743c99",
    "execution_id": "e22fb8cd-930e-4bc2-b131-0af21957ec59",
    "attestation_id": "4a1d82bb-1270-45d0-ba4e-9b64acbfa277",
    "final_decision": "approved_with_conditions",
    "final_status": "executed",
    "timeline": {
      "request_timestamp": "2026-03-24T21:42:48.686393Z",
      "risk_evaluation_timestamp": "2026-03-24T21:43:18.686393Z",
      "authorization_timestamp": "2026-03-24T21:47:48.686393Z",
      "authorization_expiry_timestamp": "2026-03-24T21:57:48.686393Z",
      "execution_timestamp": "2026-03-24T21:49:48.686393Z",
      "attestation_timestamp": "2026-03-24T21:50:48.686393Z",
      "receipt_timestamp": "2026-03-24T21:51:18.686393Z",
      "total_duration_ms": 510000
    },
    "participants": {
      "requester": "DeployBot-9000",
      "risk_evaluator": "risk-engine-v2.3.1",
      "authorizer": "Alice Johnson, SRE Lead",
      "executor": "RIO Execution Gateway (prod-us-east-1)",
      "attestor": "RIO Attestor Service"
    },
    "action_summary": {
      "action_type": "infrastructure.deploy_to_production",
      "target_label": "Production API Gateway (us-east-1)",
      "business_reason": "Emergency deployment of a critical security patch for CVE-2026-4471.",
      "risk_level": "high",
      "risk_score": 85,
      "financial_impact": "potential_high"
    },
    "execution_result": {
      "execution_status": "success",
      "confirmation_id": "deploy-receipt-987654321",
      "outcome_description": "Deployment completed successfully across all 24 nodes in the cluster.",
      "authorization_match": true
    },
    "chain_integrity": {
      "chain_hash": "a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1",
      "all_checks_passed": true,
      "check_count": 4,
      "checks_passed": 4
    },
    "summary": "On March 24, 2026, at 21:42 UTC, the AI agent DeployBot-9000 requested an emergency deployment to the Production API Gateway to patch a critical security vulnerability (CVE-2026-4471). The automated risk engine evaluated the request as high risk (score 85) due to it being an out-of-band production change, but recommended authorization because the security risk was paramount. At 21:47 UTC, SRE Lead Alice Johnson provided time-bound approval via a mobile push notification. The RIO Execution Gateway successfully executed the deployment at 21:49 UTC, within the 10-minute authorization window. The entire process was cryptographically signed and attested, with all integrity checks passing, providing a non-repudiable audit trail for this critical security intervention.",
    "notes": "Post-deployment monitoring was completed successfully by the on-call SRE.",
    "signature": {
      "algorithm": "ecdsa-sha256",
      "public_key_id": "key-rio-receipt-1",
      "signature_value": "MEQCIB/6aZ/1bN/7cQ8rD+J/6aZ/1bN/7cQ8rD+J/6aZ/1bN/7cQIhAP/1bN/7cQ8rD+J/6aZ/1bN/7cQ8rD+J/6aZ/1bN/7c=",
      "signed_fields_hash": "c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3",
      "nonce": "n-65432-abcdef"
    }
  }
}
```

## 7. Ledger Entry
```json
{
  "ledger_entry": {
    "ledger_entry_id": "763851a6-b1af-4b0a-945e-302733ac5dad",
    "receipt_id": "d291ce57-f5ec-4dba-a0b0-8654aa3027b8",
    "request_id": "a833fdef-020d-478e-81c2-efd9fc7e5f35",
    "chain_hash": "a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1",
    "entry_timestamp": "2026-03-24T21:51:33.686393Z",
    "entry_type": "action_completed",
    "previous_entry_hash": "d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4",
    "ledger_sequence_number": 45987123,
    "storage_location": "s3://rio-ledger-prod-us-east-1/2026/03/24/763851a6-b1af-4b0a-945e-302733ac5dad.json.gz",
    "retention_policy": "10_years_immutable"
  }
}
```

## Explanation
This example demonstrates how the RIO Protocol provides a robust governance framework for high-stakes, automated actions. The process begins with a **Canonical Request** from an AI agent, which clearly defines the *what*, *why*, and *how* of the proposed action. It includes critical context, such as the business reason (patching a CVE) and the risk context (an out-of-band production deployment), which immediately flags the action for higher scrutiny under the organization's policies.

The automated **Risk Evaluation** engine programmatically assesses the request. It weighs the severe security risk of inaction against the operational risk of an emergency change. By assigning a high-risk score (85) and flagging the relevant policies, it makes a clear recommendation: this action is necessary but requires human oversight. This step translates raw request data into actionable risk intelligence, preventing a risky automated action from proceeding without proper review.

Authorization is handled through the **Authorization Record**. Here, a designated human, SRE Lead Alice Johnson, reviews the risk evaluation and makes a final decision. The approval is not a blank check; it is granted *with conditions*, including a strict 10-minute time window for execution. This time-bound authorization is critical for security, as it ensures the approved action is performed immediately and prevents the approval from being used later, out of context. The entire authorization is cryptographically signed by the authorizer, creating a verifiable and non-repudiable record of who approved the action and when.

The **Execution Record** captures the details of the action's implementation by a trusted service, the RIO Execution Gateway. It confirms that the deployment was successful and, crucially, that it matched the authorized parameters. This `authorization_match` check is a key security control, ensuring that the executed action was the exact same one that was approved. Following execution, the **Attestation Record** performs a series of automated checks to verify the integrity of the entire workflow, from request to execution. It validates all cryptographic hashes and signatures, confirms timestamp ordering, and ensures the chain of records is unbroken. This automated verification provides near-real-time assurance that the process was not tampered with.

Finally, the **Receipt** and **Ledger Entry** provide the comprehensive, immutable audit trail. The receipt summarizes the entire event in a human-readable narrative, making it easy for engineers, auditors, or regulators to understand the sequence of events. The ledger entry stores the cryptographic proof of the action in a permanent, tamper-evident location. This chain of cryptographically linked, signed records provides strong non-repudiation. No participant—neither the requesting AI agent nor the authorizing human—can later deny their role in the action. This verifiable, end-to-end audit trail is essential for building trust in automated systems, especially when they perform critical operations in a complex enterprise environment.
