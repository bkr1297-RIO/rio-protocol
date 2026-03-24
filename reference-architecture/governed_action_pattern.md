# The Governed Action Control Loop

## Abstract

High-risk industries have independently converged on the same fundamental system pattern for allowing action while controlling risk: **Propose → Evaluate → Authorize → Execute → Record → Audit → Learn**. This pattern — which we call the **Governed Action Control Loop** — appears wherever the cost of an uncontrolled action exceeds the cost of governing it. The RIO Protocol is a formal, machine-readable implementation of this pattern designed specifically for AI and automated systems.

This document presents the abstract pattern, traces its manifestation across nine industries, and maps each stage to the corresponding RIO Protocol component.

---

## 1. The Pattern

The Governed Action Control Loop is a seven-stage cycle that governs any consequential action taken by an agent — human, automated, or artificial — within a system that requires accountability, traceability, and risk control.

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐
│ PROPOSE  │───▶│ EVALUATE │───▶│ AUTHORIZE │───▶│ EXECUTE │
└──────────┘    └──────────┘    └───────────┘    └─────────┘
                                                       │
                                                       ▼
                ┌──────────┐    ┌──────────┐    ┌──────────┐
                │  LEARN   │◀───│  AUDIT   │◀───│  RECORD  │
                └──────────┘    └──────────┘    └──────────┘
```

Each stage serves a distinct purpose:

| Stage | Purpose | Key Question |
|-------|---------|-------------|
| **Propose** | An agent formulates an intended action and submits it for governance. | *What is being requested, by whom, and why?* |
| **Evaluate** | The system assesses the risk, impact, and policy implications of the proposed action. | *How dangerous is this, and what rules apply?* |
| **Authorize** | A qualified authority — human or delegated — renders a decision to approve, deny, or conditionally approve. | *Should this action proceed, and under what constraints?* |
| **Execute** | The action is performed in the real world, and the actual outcome is captured. | *What actually happened?* |
| **Record** | The system produces a cryptographic, tamper-evident record binding the proposal, evaluation, authorization, and execution together. | *Can we prove what happened and that nothing was altered?* |
| **Audit** | The complete record is stored in an immutable ledger and made available for review by auditors, regulators, and compliance officers. | *Can an independent party verify the entire chain of events?* |
| **Learn** | The system extracts operational intelligence from completed cycles to improve future evaluations, calibrate risk models, and refine policies. | *What can we learn to make the next decision better?* |

The pattern is a **closed loop**: the Learn stage feeds back into the Evaluate stage, improving the system's ability to assess risk over time. This is not a one-time waterfall — it is a continuously improving governance cycle.

---

## 2. Why This Pattern Exists

The Governed Action Control Loop emerges wherever three conditions are present simultaneously:

1. **Consequential actions** — The action has real-world impact that is difficult or impossible to reverse (financial transfers, medical procedures, production deployments, access grants, data deletions).

2. **Distributed agency** — The entity proposing the action is not the same entity that should authorize it. This separation is fundamental to accountability — no agent should be able to approve its own consequential actions.

3. **Regulatory or fiduciary obligation** — There is a legal, contractual, or ethical requirement to demonstrate that the action was properly governed, that the decision-maker was qualified, and that the record is available for inspection.

When all three conditions are present, organizations invariably build some version of this pattern — whether they call it "change management," "dual control," "four-eyes principle," "pre-flight checklist," or "authorization workflow." The pattern is the same; only the vocabulary changes.

---

## 3. The Pattern Across Industries

### 3.1 Finance

The financial services industry is perhaps the most mature practitioner of governed action control. Every wire transfer, trade execution, and account modification follows a version of this pattern.

| Stage | Financial Implementation |
|-------|------------------------|
| Propose | Trader submits an order ticket; AI agent requests a wire transfer |
| Evaluate | Compliance engine checks against sanctions lists, position limits, and market abuse indicators |
| Authorize | Senior trader or compliance officer approves; dual-signature requirement for amounts above threshold |
| Execute | Order is routed to exchange; wire is submitted to payment network |
| Record | Trade confirmation with timestamps, counterparty details, and execution price |
| Audit | Regulatory reporting to SEC/FINRA/FCA; internal audit trail for SOX compliance |
| Learn | Post-trade analytics refine risk models; compliance false-positive rates are tracked and reduced |

**Regulatory drivers:** Sarbanes-Oxley (SOX), Dodd-Frank, MiFID II, Bank Secrecy Act, FINRA Rule 3110.

### 3.2 Aviation

Aviation safety is built on the principle that no single individual should be able to take a consequential action without verification. The cockpit resource management (CRM) framework is a direct implementation of the governed action pattern.

| Stage | Aviation Implementation |
|-------|----------------------|
| Propose | Pilot requests altitude change, approach clearance, or system reconfiguration |
| Evaluate | Flight management system computes fuel impact, terrain clearance, and weather exposure |
| Authorize | Air traffic control (ATC) issues clearance; co-pilot cross-checks and confirms |
| Execute | Pilot executes the maneuver; autopilot follows the authorized flight path |
| Record | Flight data recorder (FDR) and cockpit voice recorder (CVR) capture everything |
| Audit | NTSB/EASA investigation in case of incident; routine FAA audits of airline operations |
| Learn | Safety Management Systems (SMS) analyze trends; Crew Resource Management training is updated |

**Regulatory drivers:** FAA Part 121, ICAO Annex 6, EASA Part-OPS, SMS requirements under ICAO Doc 9859.

### 3.3 Medicine

Clinical medicine implements governed action control through the prescribing and treatment authorization chain. No medication is administered and no procedure is performed without a documented chain of proposal, evaluation, and authorization.

| Stage | Medical Implementation |
|-------|----------------------|
| Propose | Physician orders a medication, procedure, or diagnostic test |
| Evaluate | Clinical decision support (CDS) checks for drug interactions, allergies, contraindications, and dosage ranges |
| Authorize | Attending physician signs the order; pharmacist verifies for high-risk medications; patient provides informed consent |
| Execute | Nurse administers medication; surgeon performs procedure; lab processes test |
| Record | Electronic health record (EHR) captures the order, administration time, dosage, and patient response |
| Audit | Joint Commission accreditation reviews; CMS audits for Medicare compliance; malpractice litigation discovery |
| Learn | Morbidity and mortality (M&M) conferences; adverse event reporting to FDA MedWatch; clinical pathway refinement |

**Regulatory drivers:** HIPAA, Joint Commission standards, FDA 21 CFR Part 11, CMS Conditions of Participation.

### 3.4 Software Deployment

Modern software engineering has formalized the governed action pattern through CI/CD pipelines, change management boards, and deployment gates. The pattern is especially strict for production deployments.

| Stage | Software Deployment Implementation |
|-------|-----------------------------------|
| Propose | Developer submits a pull request or change request for production deployment |
| Evaluate | Automated test suite runs (unit, integration, security, performance); static analysis and dependency scanning |
| Authorize | Code review approval from designated reviewer(s); change advisory board (CAB) approval for production |
| Execute | CI/CD pipeline deploys to production; canary or blue-green deployment strategy |
| Record | Deployment manifest with commit hash, artifact version, environment configuration, and rollback plan |
| Audit | SOC 2 Type II audit of change management controls; PCI-DSS change control evidence |
| Learn | Post-incident reviews (PIRs); deployment frequency and failure rate metrics (DORA); rollback analysis |

**Regulatory drivers:** SOC 2, PCI-DSS Requirement 6, ISO 27001 Annex A.12.1.2, ITIL Change Management.

### 3.5 Cybersecurity

Security operations implement governed action control for incident response, access management, and vulnerability remediation. The pattern ensures that defensive actions are themselves controlled and auditable.

| Stage | Cybersecurity Implementation |
|-------|----------------------------|
| Propose | SOC analyst recommends blocking an IP range, isolating a host, or revoking credentials |
| Evaluate | Threat intelligence correlation; impact assessment on business operations; false positive analysis |
| Authorize | SOC manager or incident commander approves; CISO approval for actions affecting production systems |
| Execute | Firewall rule is applied; host is quarantined; credentials are revoked |
| Record | SIEM event log with analyst notes, IOC correlation, and action justification |
| Audit | Regulatory incident reporting (GDPR 72-hour notification, SEC 8-K); internal post-incident review |
| Learn | Threat model updates; detection rule tuning; tabletop exercise scenarios refined |

**Regulatory drivers:** NIST CSF, GDPR Article 33, SEC Cybersecurity Disclosure Rules, CISA directives.

### 3.6 Banking

Banking operations layer additional controls on top of standard financial governance, particularly for account management, lending decisions, and anti-money laundering (AML) compliance.

| Stage | Banking Implementation |
|-------|----------------------|
| Propose | Loan officer submits a credit application; teller initiates a large cash transaction |
| Evaluate | Credit scoring model assesses default risk; AML engine screens against watchlists and transaction patterns |
| Authorize | Credit committee approves loans above threshold; branch manager authorizes large cash transactions |
| Execute | Loan is funded and disbursed; cash transaction is processed |
| Record | Loan origination system captures the full decision chain; Currency Transaction Report (CTR) filed for cash over $10,000 |
| Audit | OCC/FDIC examination; BSA/AML compliance audit; fair lending analysis |
| Learn | Model validation updates credit scoring; SAR filing patterns refine AML detection |

**Regulatory drivers:** Bank Secrecy Act, USA PATRIOT Act, OCC Heightened Standards, Basel III, Community Reinvestment Act.

### 3.7 Government

Government operations — from procurement to classified information handling — implement governed action control through formal authorization chains, separation of duties, and mandatory record-keeping.

| Stage | Government Implementation |
|-------|-------------------------|
| Propose | Agency official initiates a procurement request, classification decision, or policy action |
| Evaluate | Legal counsel reviews for statutory authority; budget office confirms funding availability; security review for classified actions |
| Authorize | Contracting officer signs; classification authority approves; multi-level approval for expenditures above threshold |
| Execute | Contract is awarded; information is classified; policy is enacted |
| Record | Federal Procurement Data System (FPDS) entry; classification marking and handling instructions; Federal Register publication |
| Audit | Government Accountability Office (GAO) audit; Inspector General (IG) investigation; congressional oversight |
| Learn | Lessons learned databases; acquisition workforce training updates; policy effectiveness reviews |

**Regulatory drivers:** Federal Acquisition Regulation (FAR), Executive Order 13526 (classification), Administrative Procedure Act, FISMA.

### 3.8 Distributed Systems

Distributed systems engineering implements governed action control through consensus protocols, quorum-based decisions, and Byzantine fault tolerance. The pattern ensures that no single node can unilaterally alter the state of the system.

| Stage | Distributed Systems Implementation |
|-------|-----------------------------------|
| Propose | A node proposes a state transition (transaction, configuration change, leader election) |
| Evaluate | Validators check the proposal against protocol rules, state consistency, and resource constraints |
| Authorize | Quorum of validators reaches consensus (Raft, PBFT, Nakamoto consensus); threshold signatures for multi-party authorization |
| Execute | State transition is applied; block is appended; configuration is propagated |
| Record | Transaction receipt with Merkle proof; block header with previous hash; state root commitment |
| Audit | Block explorer for public chains; internal monitoring for private consensus networks; formal verification of protocol invariants |
| Learn | Protocol parameter tuning (block size, gas limits); validator performance scoring; fork analysis |

**Regulatory drivers:** Varies by application — MiCA (EU crypto regulation), SEC digital asset guidance, internal SLAs for enterprise consensus systems.

### 3.9 Artificial Intelligence

AI systems are the newest entrants to governed action control, and the RIO Protocol is designed specifically for this domain. As AI agents gain the ability to take real-world actions — sending payments, modifying data, communicating on behalf of humans — the need for a formal governance layer becomes critical.

| Stage | AI / RIO Implementation |
|-------|------------------------|
| Propose | AI agent submits a canonical request describing the intended action, target, parameters, and business justification |
| Evaluate | RIO risk evaluation engine scores the request across financial, operational, compliance, reputational, security, data privacy, and AI behavioral risk categories |
| Authorize | Human authority (or delegated authority for low-risk actions) renders a cryptographically signed, time-bound authorization decision |
| Execute | RIO execution gateway validates the authorization (unexpired, unused nonce, matching parameters) and performs the action |
| Record | RIO attestation service computes hashes of all records, performs verification checks, and produces a cryptographic attestation binding the entire chain |
| Audit | RIO audit ledger stores the receipt and all supporting records in a tamper-evident hash chain; available for compliance review and regulatory inspection |
| Learn | RIO learning protocol analyzes completed decision chains to refine risk models, calibrate policy thresholds, and identify emerging risk patterns |

**Regulatory drivers:** EU AI Act, NIST AI RMF, White House Executive Order on AI Safety, SEC guidance on AI in financial services, proposed AIAAIC standards.

---

## 4. Mapping the Pattern to RIO Protocol Components

The RIO Protocol provides a formal, machine-readable implementation of each stage in the Governed Action Control Loop:

| Pattern Stage | RIO Protocol Component | RIO Schema | RIO Spec |
|--------------|----------------------|------------|----------|
| Propose | Intake → Origin Verification → Canonical Request Formation | `canonical_request.json` | Specs 01–03 |
| Evaluate | Risk Evaluation → Policy Constraints | `risk_evaluation.json` | Specs 04–05 |
| Authorize | Authorization (with Time-Bound Authorization) | `authorization_record.json` | Specs 06, 15 |
| Execute | Execution | `execution_record.json` | Spec 07 |
| Record | Attestation | `attestation_record.json` | Spec 08 |
| Audit | Audit Ledger → Receipt | `receipt.json` | Spec 09 |
| Learn | Learning and Feedback | *(analytics output)* | Spec 10 |

The structural protocols (Independence, Role Separation, Meta-Governance, Orchestration — Specs 11–14) are cross-cutting concerns that ensure the pattern itself is properly implemented and cannot be subverted.

---

## 5. Why AI Needs This Pattern Now

Previous implementations of the Governed Action Control Loop have been designed for human agents operating within organizational hierarchies. The rise of autonomous AI agents introduces three new challenges that the RIO Protocol addresses:

**Speed asymmetry.** AI agents can propose thousands of actions per second. Traditional governance mechanisms — email approvals, committee meetings, manual reviews — cannot keep pace. RIO implements machine-speed governance with cryptographic authorization that completes in seconds, not hours.

**Opacity of reasoning.** When a human trader proposes a trade, their reasoning can be interrogated in real time. When an AI agent proposes the same trade, its reasoning may be opaque or difficult to audit after the fact. RIO requires the canonical request to include a structured business justification and risk context, creating an auditable record of *why* the action was proposed — regardless of whether the proposer is human or artificial.

**Scale of consequence.** A single AI agent with API access to payment systems, communication platforms, and data stores can take actions with enterprise-wide impact in milliseconds. The traditional assumption that the speed of human decision-making provides a natural rate limiter no longer holds. RIO's time-bound authorization, single-use nonces, and fail-closed execution gate ensure that even at machine speed, every consequential action passes through a governed control loop.

The Governed Action Control Loop is not new. What is new is the need to implement it at machine speed, with cryptographic guarantees, for agents whose reasoning cannot be directly observed. That is what the RIO Protocol provides.

---

## 6. Design Principles

The RIO Protocol's implementation of the Governed Action Control Loop is guided by five design principles:

1. **Fail closed.** If any stage in the loop cannot be completed — if the risk engine is unreachable, if the authorization has expired, if the attestation service is down — the action does not proceed. The default state is denial, not permission.

2. **No self-authorization.** The entity that proposes an action cannot be the entity that authorizes it. This is enforced structurally through role separation, not merely through policy.

3. **Cryptographic non-repudiation.** Every authorization decision is cryptographically signed. Every record in the chain is hashed. The attestation binds all records together with a chain hash. No participant can later deny their involvement.

4. **Time-bound authority.** Authorizations expire. A decision made at 14:33 cannot be used to execute an action at 15:33. This prevents stockpiling of approvals and ensures that authorization reflects current conditions.

5. **Continuous learning.** The loop is closed — completed cycles feed back into the evaluation stage. Risk models improve. Policy thresholds are calibrated. The system gets better at governing actions over time, without ever compromising the integrity of past records.

---

## References

- NIST AI Risk Management Framework (AI RMF 1.0), January 2023
- EU Artificial Intelligence Act, Regulation (EU) 2024/1689
- IETF RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels
- ICAO Doc 9859 — Safety Management Manual, 4th Edition
- NIST Cybersecurity Framework (CSF) 2.0, February 2024
- SOC 2 Type II — Trust Services Criteria (AICPA)
- Basel Committee on Banking Supervision — Principles for the Sound Management of Operational Risk
- Federal Acquisition Regulation (FAR), 48 CFR
