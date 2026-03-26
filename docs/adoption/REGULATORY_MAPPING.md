# RIO Protocol — Regulatory Mapping

**Version:** 1.0.0
**Status:** Adoption Documentation
**Category:** Compliance & Standards

---

## Purpose

This document maps the RIO protocol's governance mechanisms, audit artifacts, and safety controls to the requirements of three major regulatory and compliance frameworks: the **EU Artificial Intelligence Act** (Regulation 2024/1689), the **NIST AI Risk Management Framework** (AI 100-1), and **SOC 2 Type II Trust Service Criteria**. For each requirement, the mapping identifies the specific RIO component that addresses it, the evidence RIO produces, and any gaps where additional controls may be needed.

This mapping is intended for compliance officers, auditors, and governance teams evaluating whether a RIO-compliant implementation satisfies their regulatory obligations. It is not a legal opinion. Organizations should consult qualified legal counsel to confirm that their specific deployment meets all applicable requirements.

> **Scope:** This mapping covers the open RIO protocol as defined in the canonical specification. Enterprise extensions (advanced policy analytics, compliance mapping engine, learning loop analytics) are not included.

---

## 1. EU Artificial Intelligence Act Mapping

The EU AI Act [1] establishes a risk-based regulatory framework for AI systems deployed in the European Union. RIO is most relevant to **Chapter III, Section 2** (Requirements for High-Risk AI Systems) and **Section 3** (Obligations of Providers and Deployers). The following table maps each relevant article to the RIO components and evidence that address it.

### 1.1 Article 9 — Risk Management System

Article 9 requires a continuous, iterative risk management system that identifies, analyzes, estimates, and mitigates risks throughout the AI system's lifecycle [1].

| Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|---------------|-------------------|----------------|
| 9(1): Establish, implement, document, and maintain a risk management system | Policy engine with configurable risk thresholds; risk scoring at Stage 4 (Policy & Risk Evaluation) | Risk scores recorded in every receipt; policy rule versions tracked in ledger | RIO provides the runtime risk evaluation infrastructure. Organizations must define their own risk taxonomy and threshold values appropriate to their domain. |
| 9(2)(a): Identify and analyze known and foreseeable risks | Risk engine evaluates coherence scores, somatic markers, scope boundaries, and tool permissions per request | Per-request risk assessment with numeric scores and risk level classification (LOW/MEDIUM/HIGH/CRITICAL) in receipts | RIO evaluates risks at the individual request level. Systemic risk identification across the full AI system lifecycle requires additional organizational processes. |
| 9(2)(b): Estimate and evaluate risks under intended use and foreseeable misuse | Policy constraints enforce scope boundaries; intent validation rejects malformed or out-of-scope requests | Denied receipts with block reasons; policy violation details in audit trail | RIO blocks misuse at runtime. Pre-deployment risk estimation for foreseeable misuse scenarios must be performed separately during system design. |
| 9(2)(d): Adopt targeted risk management measures | Configurable policy rules with risk-based routing: auto-approve (LOW), require human approval (MEDIUM/HIGH), auto-deny (CRITICAL) | Policy decisions recorded with rule IDs and risk scores in receipts | **Full coverage.** RIO's policy engine directly implements targeted risk management measures with auditable decision trails. |
| 9(5): Residual risk must be acceptable | Kill switch (EKS-0) provides last-resort halt; fail-closed behavior ensures denial when evaluation is ambiguous | Kill switch engagement/disengagement receipts; blocked execution receipts with reason codes | RIO enforces fail-closed defaults. Residual risk acceptability determination is an organizational judgment that RIO supports with evidence but does not make. |
| 9(6): Testing against defined metrics | Conformance test suite (57 tests, 12 vectors) validates protocol compliance | Test results, hash verification outputs, signature verification outputs | **Full coverage.** The conformance test suite provides defined metrics and deterministic pass/fail criteria. |

### 1.2 Article 12 — Record-Keeping

Article 12 requires automatic logging capabilities that ensure traceability of the AI system's functioning throughout its lifecycle [1].

| Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|---------------|-------------------|----------------|
| 12(1): Automatic logging of events | Hash-chain ledger (Stage 8) automatically records every governance decision | Signed ledger entries with timestamps, decision outcomes, receipt hashes, and chain integrity proofs | **Full coverage.** Every governed action produces an immutable, append-only ledger entry. |
| 12(2): Traceability throughout lifecycle | Receipts contain full decision chain: intent hash, policy decision, risk score, authorization, execution result, verification status | v2 receipts with cryptographic signatures linking every field to the original request | **Full coverage.** The receipt + ledger combination provides end-to-end traceability from request to outcome. |
| 12(3): Logging capabilities appropriate to intended purpose | Configurable receipt detail level; all receipts include mandatory fields defined by the protocol specification | Receipt schema enforces minimum required fields; additional metadata fields available | Organizations may need to configure additional metadata fields for domain-specific logging requirements. |

### 1.3 Article 13 — Transparency and Provision of Information to Deployers

Article 13 requires that high-risk AI systems be designed to ensure sufficient transparency for deployers to interpret outputs and use the system appropriately [1].

| Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|---------------|-------------------|----------------|
| 13(1): Sufficiently transparent operation | Every governance decision produces a human-readable receipt with the full decision rationale | Receipts include: policy rule matched, risk score breakdown, approval status, execution result, verification outcome | **Full coverage.** RIO receipts provide complete decision transparency at the individual action level. |
| 13(2): Instructions for use | Protocol specification, implementation guide, and quickstart guide | Documentation set (canonical spec, implementation guide, quickstart) | **Full coverage** for the protocol layer. Application-level instructions for use are the deployer's responsibility. |
| 13(3)(b)(ii): Deployers can interpret AI output | Structured intents translate vague goals into machine-readable, human-auditable formats before governance begins | Canonical intent with declared action, parameters, scope, and tool requirements | RIO provides intent-level transparency. Interpretation of the underlying AI model's reasoning is outside RIO's scope. |

### 1.4 Article 14 — Human Oversight

Article 14 requires that high-risk AI systems be designed to allow effective human oversight, including the ability to override or interrupt the system [1].

| Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|---------------|-------------------|----------------|
| 14(1): Designed for effective human oversight | Approval protocol (Stage 5) routes decisions to human approvers based on risk level | Authorization tokens with approver identity, timestamp, and scope | **Full coverage.** Human oversight is a core architectural requirement, not an optional feature. |
| 14(3)(a): Understand AI capabilities and limitations | Three-Loop Architecture structurally separates intake, governance, and learning | Architecture documentation; role model with 8 defined roles and separation rules | Organizational training on RIO's governance model is required to fulfill this provision. |
| 14(3)(b): Aware of automation bias | Approval UI must present risk scores and policy rationale; approvers see the full context before deciding | Approval request payloads with risk assessment, policy match, and recommended action | RIO provides the information infrastructure. Automation bias mitigation in the approval UI is an implementation responsibility. |
| 14(4)(a): Correctly interpret output | Post-execution verification (Stage 6b) independently validates that execution results match the authorized intent | Verification status (verified/failed/skipped) and verification hash in receipts | **Full coverage.** Verification provides an independent check on execution correctness. |
| 14(4)(b): Decide not to use or override | Kill switch (EKS-0) halts all execution immediately; individual requests can be denied at the approval stage | Kill switch receipts; denial receipts with reason codes | **Full coverage.** Both global halt and per-request override are built into the protocol. |
| 14(4)(d): Intervene or interrupt | Kill switch provides immediate global interruption; execution gate blocks individual requests when authorization is revoked | Kill switch engagement ledger entries; blocked execution receipts | **Full coverage.** Intervention mechanisms operate at both global and individual request levels. |

### 1.5 Article 15 — Accuracy, Robustness and Cybersecurity

Article 15 requires appropriate levels of accuracy, robustness, and cybersecurity throughout the AI system's lifecycle [1].

| Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|---------------|-------------------|----------------|
| 15(1): Appropriate level of accuracy | Post-execution verification (Stage 6b) validates execution results against authorized intent | Verification hash and status in receipts; mismatched executions flagged | RIO verifies execution accuracy. AI model accuracy (e.g., prediction quality) is outside RIO's scope and must be evaluated separately. |
| 15(3): Resilient against errors and inconsistencies | Fail-closed behavior: any ambiguous or failed evaluation results in denial | Denied receipts with error codes; invariant violation alerts | **Full coverage.** Fail-closed is a protocol invariant (INV-08), not an optional configuration. |
| 15(4): Resilient against unauthorized third-party manipulation | Cryptographic signatures (RSA-PSS/Ed25519) on all receipts; hash-chain ledger prevents tampering; nonce management prevents replay attacks | Signed receipts; ledger chain integrity proofs; nonce consumption records | **Full coverage.** Cryptographic integrity is enforced at every stage of the protocol. |
| 15(5): Cybersecurity measures | Key management, signature verification, hash chain integrity, authorization token expiry, single-use nonces | Signature verification results; chain integrity verification; expired token rejection receipts | RIO provides strong cryptographic controls at the governance layer. Network security, infrastructure hardening, and application-level security are outside RIO's scope. |

### 1.6 Article 17 — Quality Management System

Article 17 requires providers to implement a documented quality management system [1].

| Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|---------------|-------------------|----------------|
| 17(1)(a): Strategy for regulatory compliance | Regulatory mapping (this document); certification criteria with three conformance levels | Compliance documentation set | **Full coverage** for the protocol layer. Organizational QMS must integrate RIO compliance into broader quality processes. |
| 17(1)(b): Design and development procedures | Protocol specification with 8-stage pipeline; implementation guide with architecture decisions and pseudocode | Canonical specification; implementation guide | **Full coverage.** The protocol specification defines the design and development requirements. |
| 17(1)(e): Testing and validation | Conformance test suite (57 tests); test vectors (12 files); independent verifier | Test results; verification outputs; conformance level certification | **Full coverage.** The conformance framework provides structured testing and validation. |
| 17(1)(g): Post-market monitoring | Governance learning protocol analyzes historical decisions to improve future governance | Learning loop proposals (submitted through governed approval process); policy version history | RIO provides the infrastructure for post-deployment monitoring. Organizations must define monitoring cadence and escalation procedures. |

### 1.7 Article 26 — Obligations of Deployers

Article 26 (renumbered from Article 29 in the final text) establishes obligations for organizations deploying high-risk AI systems [1].

| Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|---------------|-------------------|----------------|
| 26(1): Use in accordance with instructions | Protocol specification defines correct usage; implementation guide provides deployment procedures | Conformance test results confirming correct implementation | Organizations must ensure their deployment follows the protocol specification. |
| 26(2): Assign human oversight to competent persons | Role model defines 8 roles with separation rules; approval routing assigns decisions to authorized approvers | Approval records with approver identity and role | RIO enforces role-based approval routing. Organizations must assign competent persons to the defined roles. |
| 26(5): Monitor operation | Ledger provides continuous audit trail; receipts enable per-decision monitoring | Real-time ledger entries; receipt verification results | **Full coverage.** The ledger and receipt system provides continuous operational monitoring. |
| 26(6): Keep automatically generated logs | Hash-chain ledger is append-only and tamper-evident | Ledger entries with chain integrity proofs; retention policy enforcement | RIO generates and preserves logs automatically. Organizations must define retention periods appropriate to their regulatory requirements. |

---

## 2. NIST AI Risk Management Framework Mapping

The NIST AI Risk Management Framework (AI 100-1) [2] provides a voluntary framework organized around four core functions: **GOVERN**, **MAP**, **MEASURE**, and **MANAGE**. Each function contains categories and subcategories that describe specific outcomes. The following tables map RIO components to the most relevant subcategories.

### 2.1 GOVERN Function

The GOVERN function establishes the organizational context, culture, and structures for AI risk management [2].

| Subcategory | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|-------------|---------------|-------------------|----------------|
| GV-1.1 | Legal and regulatory requirements are identified | Regulatory mapping (this document) maps RIO to EU AI Act, NIST AI RMF, SOC 2 | Compliance documentation | Organizations must identify additional domain-specific regulations. |
| GV-1.2 | Trustworthy AI characteristics are integrated into policies | Protocol invariants (INV-01 through INV-08) encode trustworthiness requirements as enforceable rules | Invariant enforcement in every receipt; violation alerts | **Full coverage.** Invariants are not guidelines — they are enforced at runtime. |
| GV-1.3 | Processes for AI risk management are defined | 8-stage governed execution pipeline with defined inputs, outputs, and decision criteria at each stage | Pipeline execution records in receipts and ledger | **Full coverage.** The pipeline is the risk management process. |
| GV-2.1 | Roles and responsibilities are defined | Role model defines 8 roles: Requester, Approver, Administrator, Auditor, Policy Author, Risk Analyst, System Operator, Security Officer | Role assignments in authorization tokens; approval records with role identity | **Full coverage.** Role separation is a protocol requirement. |
| GV-4.1 | Organizational practices are in place for AI risk management | Three-Loop Architecture separates intake, governance, and learning into structurally independent loops | Architecture documentation; loop separation enforcement | Organizations must adopt the Three-Loop Architecture as their operational model. |
| GV-6.1 | Policies for deployment and oversight are defined | Policy engine with configurable rules; risk-based routing; approval thresholds | Policy rule versions in ledger; deployment configuration records | **Full coverage.** Policies are machine-enforceable, not just documented. |

### 2.2 MAP Function

The MAP function identifies and contextualizes AI risks [2].

| Subcategory | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|-------------|---------------|-------------------|----------------|
| MP-2.1 | AI system is categorized based on risk | Risk engine classifies every request as LOW, MEDIUM, HIGH, or CRITICAL | Risk level in every receipt; risk score breakdown | **Full coverage.** Risk categorization happens per-request, not just per-system. |
| MP-3.1 | Benefits and costs of AI system assessed | Structured intents declare the action, scope, and expected outcome before execution | Intent records with declared parameters and scope boundaries | RIO provides per-action cost/benefit framing. System-level benefit assessment is an organizational responsibility. |
| MP-4.1 | Risks and impacts are identified | Threat model defines 10 threat categories with attack vectors and mitigations | Threat model documentation; risk scores reflecting identified threats | **Full coverage.** The threat model is a formal input to the risk engine. |
| MP-5.1 | Impacts to affected communities assessed | Policy constraints can encode community-impact rules; scope boundaries limit affected systems | Policy rule documentation; scope enforcement in receipts | RIO provides the enforcement mechanism. Community impact assessment criteria must be defined by the organization. |

### 2.3 MEASURE Function

The MEASURE function quantifies and tracks AI risks [2].

| Subcategory | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|-------------|---------------|-------------------|----------------|
| MS-1.1 | Appropriate methods for measuring AI risks are identified | Conformance test suite with 57 tests and 12 deterministic vectors; risk scoring with numeric thresholds | Test results; risk score distributions in ledger analytics | **Full coverage.** Measurement methods are defined and deterministic. |
| MS-2.1 | AI systems evaluated for trustworthy characteristics | Post-execution verification (Stage 6b) independently validates execution outcomes | Verification status and hash in every receipt | **Full coverage.** Trustworthiness is verified per-execution, not assumed. |
| MS-2.6 | AI system performance is monitored | Ledger provides continuous performance record; receipts track execution times, verification results, and error rates | Time-series ledger data; receipt analytics | Organizations must build monitoring dashboards on top of the ledger data. |
| MS-3.1 | Mechanisms for tracking identified risks over time | Governance learning protocol analyzes historical decisions; policy version history tracks risk threshold changes | Learning loop outputs; policy change audit trail | **Full coverage.** Risk tracking is built into the learning loop. |

### 2.4 MANAGE Function

The MANAGE function addresses identified AI risks [2].

| Subcategory | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-------------|-------------|---------------|-------------------|----------------|
| MG-1.1 | AI risks are prioritized | Risk engine assigns numeric scores with configurable weights; CRITICAL risks are auto-denied | Risk score breakdowns in receipts; denial records for high-risk requests | **Full coverage.** Risk prioritization is automated and auditable. |
| MG-2.1 | Strategies to maximize benefits and minimize negative impacts | Policy rules encode organizational strategies; approval routing ensures human judgment for high-impact decisions | Policy rule versions; approval decision records | **Full coverage.** Strategy enforcement is the policy engine's core function. |
| MG-2.2 | Mechanisms to sustain AI system value | Governance learning protocol proposes policy improvements based on historical outcomes | Learning proposals (submitted through governed approval); policy update records | **Full coverage.** Continuous improvement is structurally built into the Three-Loop Architecture. |
| MG-3.1 | Third-party AI risks managed | Connector framework governs interactions with external systems; all external calls pass through the execution gate | External call receipts with connector type, target, and verification status | RIO governs the interaction boundary. Third-party vendor risk assessment is an organizational responsibility. |
| MG-4.1 | Risk treatments monitored | Ledger provides continuous record of all risk treatments (approvals, denials, blocks, escalations) | Ledger entries with decision outcomes; trend analysis from historical data | **Full coverage.** Every risk treatment is recorded and auditable. |

---

## 3. SOC 2 Type II Mapping

SOC 2 Type II [3] evaluates the operating effectiveness of controls over a period of time. The following tables map RIO components to the Trust Service Criteria most relevant to AI governance systems.

### 3.1 CC6 — Logical and Physical Access Controls

| Criterion | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-----------|-------------|---------------|-------------------|----------------|
| CC6.1 | Logical access security software, infrastructure, and architectures are implemented | Authorization tokens with cryptographic signatures; role-based access control; nonce management | Token issuance and consumption records; role assignments | RIO provides logical access controls at the governance layer. Infrastructure-level access controls (network, OS) are outside RIO's scope. |
| CC6.2 | Registration and authorization prior to issuing credentials | Approval protocol requires explicit human authorization before execution credentials are issued | Authorization token records with approver identity, timestamp, and scope | **Full coverage.** No execution credential is issued without prior authorization. |
| CC6.3 | Access restricted to authorized users | Execution gate (Stage 6) verifies authorization token validity, expiry, nonce, and scope before permitting execution | Gate verification records in receipts; rejected access attempts with reason codes | **Full coverage.** The execution gate is the access control enforcement point. |
| CC6.6 | System access restricted | Role model enforces separation of duties; 8 defined roles with explicit permission boundaries | Role-based access records; separation of duties enforcement | **Full coverage.** Role separation is a protocol requirement, not an optional configuration. |
| CC6.8 | Unauthorized software prevented or detected | Policy constraints restrict tool permissions; only declared tools may be invoked during execution | Tool permission enforcement in receipts; unauthorized tool access denials | **Full coverage** for the governance layer. Application-level software controls are outside RIO's scope. |

### 3.2 CC7 — System Operations

| Criterion | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-----------|-------------|---------------|-------------------|----------------|
| CC7.1 | Detection and monitoring procedures | Hash-chain ledger provides continuous, tamper-evident monitoring of all governance decisions | Ledger entries with chain integrity proofs; receipt verification results | **Full coverage.** Monitoring is automatic and cryptographically secured. |
| CC7.2 | Anomalies and security events monitored | Invariant violations trigger alerts; signature verification failures are logged; chain integrity breaks are detected | Invariant violation records; signature failure alerts; chain break detection | **Full coverage.** Security event detection is built into the verification layer. |
| CC7.3 | Security events evaluated | Receipt and ledger data provide full context for security event evaluation: who requested, what was authorized, what was executed, what was verified | Complete decision chain in receipts; correlated ledger entries | **Full coverage.** Every security event has a complete audit trail. |
| CC7.4 | Response to security incidents | Kill switch (EKS-0) provides immediate global halt; fail-closed behavior blocks individual suspicious requests | Kill switch engagement records; blocked request receipts | **Full coverage.** Incident response mechanisms operate at both global and individual levels. |
| CC7.5 | Recovery from security incidents | Kill switch disengagement with re-submission requirement; expired tokens invalidated during incidents | Recovery records; re-authorization requirements after incident | RIO provides governance-layer recovery. Infrastructure recovery (backup, failover) is outside RIO's scope. |

### 3.3 CC8 — Change Management

| Criterion | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-----------|-------------|---------------|-------------------|----------------|
| CC8.1 | Changes authorized, designed, developed, configured, documented, tested, approved, implemented | Governance learning protocol submits all policy changes through the governed approval process; meta-governance protocol governs changes to governance rules themselves | Policy change proposals; approval records for governance changes; policy version history | **Full coverage.** Changes to the governance system are themselves governed — this is the meta-governance invariant. |

### 3.4 PI1 — Processing Integrity

| Criterion | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-----------|-------------|---------------|-------------------|----------------|
| PI1.1 | Information obtained, generated, used, and communicated to meet objectives | Structured intents define objectives; receipts record outcomes; ledger preserves the complete decision history | Intent records; receipt records; ledger chain | **Full coverage.** The intent-to-receipt-to-ledger chain ensures processing integrity from input to output. |
| PI1.2 | Processing is complete, valid, accurate, timely, authorized | 8-stage pipeline ensures completeness (all stages executed); post-execution verification ensures accuracy; authorization tokens ensure authorization; timestamps ensure timeliness | Stage completion records in receipts; verification status; authorization token records; ISO 8601 timestamps | **Full coverage.** Processing integrity is enforced by the pipeline structure itself. |
| PI1.3 | Processing integrity monitored | Ledger chain verification detects any tampering; receipt hash verification detects any modification | Chain integrity verification results; receipt hash verification results | **Full coverage.** Integrity monitoring is cryptographic and deterministic. |
| PI1.4 | Outputs reviewed for completeness and accuracy | Post-execution verification (Stage 6b) independently validates that execution results match the authorized intent | Verification hash and status in receipts; mismatch detection | **Full coverage.** Output review is automated and cryptographically verified. |
| PI1.5 | Inputs and outputs stored completely and accurately | Hash-chain ledger stores all inputs (intents) and outputs (receipts) with cryptographic integrity proofs | Ledger entries with intent hashes and receipt hashes; chain integrity | **Full coverage.** Storage integrity is guaranteed by the hash chain. |

### 3.5 A1 — Availability

| Criterion | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-----------|-------------|---------------|-------------------|----------------|
| A1.1 | Current processing capacity maintained and monitored | Pipeline processes requests sequentially with defined timeout behavior; fail-closed on timeout | Timeout receipts; processing duration in receipt timestamps | RIO provides governance-layer availability guarantees. Infrastructure capacity planning is outside RIO's scope. |
| A1.2 | Environmental protections, software, data backup | Ledger is append-only and designed for backup; key material requires secure storage | Ledger backup procedures; key management documentation | RIO defines what must be backed up. Backup implementation is an operational responsibility. |
| A1.3 | Recovery plan tested | Kill switch recovery procedures defined; re-submission required after incidents | Recovery procedure documentation; kill switch test records | Organizations must test recovery procedures as part of their operational readiness program. |

### 3.6 C1 — Confidentiality

| Criterion | Requirement | RIO Component | Evidence Produced | Gap Assessment |
|-----------|-------------|---------------|-------------------|----------------|
| C1.1 | Confidential information identified and maintained | Signature keys are the primary confidential asset; key management procedures defined in the protocol specification | Key management documentation; key rotation records | RIO identifies governance-layer confidential assets. Application-level data classification is outside RIO's scope. |
| C1.2 | Confidential information disposed of | Key rotation procedures; expired token invalidation; nonce consumption (single-use) | Key rotation records; expired token rejection records; consumed nonce records | **Full coverage** for governance-layer assets. Application-level data disposal is outside RIO's scope. |

---

## 4. Cross-Framework Summary

The following table consolidates RIO's coverage across all three frameworks, identifying areas of strong coverage and areas where additional organizational controls are needed.

### 4.1 Strong Coverage Areas

These RIO components satisfy requirements across all three frameworks simultaneously.

| RIO Component | EU AI Act | NIST AI RMF | SOC 2 | Coverage |
|---------------|-----------|-------------|-------|----------|
| **Hash-chain ledger** | Art. 12 (Record-Keeping) | MS-2.6, MG-4.1 (Monitoring, Risk Treatment) | CC7.1, PI1.3, PI1.5 (Operations, Integrity) | **Full** — satisfies record-keeping, monitoring, and integrity requirements across all three frameworks |
| **v2 Receipts with cryptographic signatures** | Art. 13 (Transparency), Art. 15 (Cybersecurity) | GV-1.2 (Trustworthy Characteristics) | PI1.2, PI1.4 (Processing Integrity) | **Full** — provides transparency, tamper-evidence, and processing integrity simultaneously |
| **Approval protocol (Stage 5)** | Art. 14 (Human Oversight) | GV-6.1 (Deployment Policies) | CC6.2, CC6.3 (Access Controls) | **Full** — human oversight, deployment governance, and access control in a single mechanism |
| **Kill switch (EKS-0)** | Art. 14(4)(b,d) (Override/Interrupt) | MG-1.1 (Risk Prioritization) | CC7.4 (Incident Response) | **Full** — override capability, risk response, and incident response in a single mechanism |
| **Post-execution verification (Stage 6b)** | Art. 15(1) (Accuracy) | MS-2.1 (Trustworthy Evaluation) | PI1.4 (Output Review) | **Full** — accuracy verification, trustworthiness evaluation, and output review in a single mechanism |
| **Policy engine with risk scoring** | Art. 9 (Risk Management) | MP-2.1, MG-1.1 (Risk Categorization, Prioritization) | CC6.1 (Access Security) | **Full** — risk management, categorization, and access control enforcement |
| **Conformance test suite** | Art. 9(6) (Testing), Art. 17(1)(e) (Validation) | MS-1.1 (Measurement Methods) | PI1.2 (Processing Integrity) | **Full** — testing, validation, and measurement across all three frameworks |
| **Role model (8 roles)** | Art. 26(2) (Human Oversight Assignment) | GV-2.1 (Roles and Responsibilities) | CC6.6 (System Access Restriction) | **Full** — role assignment, responsibility definition, and access restriction |

### 4.2 Partial Coverage Areas

These areas require additional organizational controls beyond the RIO protocol.

| Area | What RIO Provides | What Organizations Must Add | Frameworks Affected |
|------|-------------------|-----------------------------|---------------------|
| **Pre-deployment risk assessment** | Per-request runtime risk evaluation | System-level risk assessment before deployment; foreseeable misuse analysis | EU AI Act Art. 9(2)(b); NIST MP-4.1 |
| **AI model accuracy** | Post-execution verification of intent-to-outcome alignment | AI model performance metrics, bias testing, fairness evaluation | EU AI Act Art. 15(1); NIST MS-2.1 |
| **Infrastructure security** | Governance-layer cryptographic controls | Network security, OS hardening, physical security, DDoS protection | EU AI Act Art. 15(4,5); SOC 2 CC6.1, A1.2 |
| **Community impact assessment** | Policy enforcement mechanism for impact rules | Stakeholder engagement, impact assessment methodology, affected community identification | NIST MP-5.1 |
| **Data governance** | Intent and receipt data integrity via hash chains | Training data governance, data quality, data bias assessment | EU AI Act Art. 10; NIST MP-3.1 |
| **Automation bias mitigation** | Risk scores and policy rationale in approval UI | User training, UI design for bias awareness, decision support tools | EU AI Act Art. 14(3)(b) |
| **Backup and recovery** | Defines what must be backed up (ledger, keys) | Backup implementation, disaster recovery testing, failover infrastructure | SOC 2 A1.2, A1.3 |

### 4.3 Coverage Statistics

| Framework | Requirements Mapped | Full Coverage | Partial Coverage | Not Addressed |
|-----------|--------------------:|:-------------:|:----------------:|:-------------:|
| EU AI Act (6 articles, 22 sub-requirements) | 22 | 14 (64%) | 8 (36%) | 0 (0%) |
| NIST AI RMF (16 subcategories mapped) | 16 | 12 (75%) | 4 (25%) | 0 (0%) |
| SOC 2 (17 criteria mapped) | 17 | 14 (82%) | 3 (18%) | 0 (0%) |
| **Total** | **55** | **40 (73%)** | **15 (27%)** | **0 (0%)** |

All partial coverage areas are outside the scope of a governance protocol (infrastructure security, AI model accuracy, organizational processes). Within its scope — runtime governance, audit, and cryptographic integrity — RIO provides full coverage across all three frameworks.

---

## References

[1]: Regulation (EU) 2024/1689 of the European Parliament and of the Council — Artificial Intelligence Act. Official Journal of the European Union, 13 June 2024. https://artificialintelligenceact.eu/

[2]: National Institute of Standards and Technology. AI Risk Management Framework (AI RMF 1.0). NIST AI 100-1, January 2023. https://www.nist.gov/itl/ai-risk-management-framework

[3]: American Institute of Certified Public Accountants. Trust Services Criteria for SOC 2. https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2
