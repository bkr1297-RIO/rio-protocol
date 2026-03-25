# Glossary

**RIO — Key Terms and Definitions**

---

## A

### Adapter

A module that translates an authorized intent into a real-world action. Adapters implement a common interface and are registered in the adapter registry. Each adapter handles a specific category of actions (email, file, HTTP, calendar). Adapters are the only components in the system that produce external side effects.

> Implementation: `runtime/adapters/`

### Approval

The act of a human authorizer (manager or admin) reviewing a pending request and granting permission for it to proceed. Approval generates an authorization token that the execution gate consumes. The approver must be a different identity than the requester (INV-06).

> Implementation: `runtime/approvals/approval_manager.py`

### Authorization

The process of issuing a time-bound, single-use token that permits a specific action to be executed. Authorization occurs after policy and risk evaluation. The token contains the intent hash, authorizer identity, nonce, expiration, and ECDSA signature.

> Implementation: `runtime/authorization.py`

---

## C

### Canonical Intent

The normalized, validated form of an action request. The canonical intent contains the action type, all validated parameters, and a deterministic SHA-256 hash. The hash is computed from the minified, sorted JSON representation of the intent, ensuring that identical requests always produce identical hashes.

> Implementation: `runtime/structured_intent.py`

### Classification

The second stage of the pipeline. Classification determines the action type and assigns an initial risk category based on the action and the requester's role. Classification provides inputs to the policy and risk engines but does not make policy decisions.

> Implementation: `runtime/classification.py`

### Connector

A lower-level transport abstraction used by adapters for actual I/O operations. Connectors handle the mechanics of sending emails, making HTTP calls, or writing files. Adapters add authorization verification and context handling on top of connectors.

> Implementation: `runtime/connectors/`

### Corpus

See **Governed Corpus**.

---

## D

### Decision

The output of the policy engine. One of three values: **ALLOW** (the action may proceed without additional approval), **DENY** (the action is prohibited), or **ESCALATE** (the action requires human approval before proceeding). Also referred to as REQUIRE_APPROVAL when the decision is ESCALATE.

---

## E

### Execution Gate

The sixth stage of the pipeline and the final checkpoint before real-world action. The execution gate performs four sequential checks: kill switch status, authorization token signature verification, nonce consumption (replay prevention), and token expiration. Only if all four checks pass does the gate dispatch the action to an adapter.

> Implementation: `runtime/execution_gate.py`

---

## G

### Governed Corpus

The system's structured decision history. Every completed pipeline run produces a corpus record containing the full context: request, intent, policy decision, risk score, authorization outcome, execution result, receipt reference, and ledger reference. The corpus is append-only and separate from the ledger. It serves as the analytical dataset for replay, simulation, and governance learning.

> Implementation: `runtime/corpus/corpus_store.py`
> Data: `runtime/data/governed_corpus.jsonl`

### Governance

The system of rules, controls, and processes that ensure actions are authorized, auditable, and compliant with organizational policy. In RIO, governance encompasses policy evaluation, risk assessment, human approval, cryptographic audit, and policy versioning.

### Governance Change

A modification to the policy rules or risk model. Every governance change follows a governed workflow (propose, approve, activate) and produces a receipt and ledger entry with event type `GOVERNANCE_CHANGE`.

> Implementation: `runtime/governance/governance_ledger.py`

---

## H

### Hash Chain

The mechanism that makes the ledger tamper-evident. Each ledger entry contains the content hash of the previous entry. This creates a linked chain where modifying or deleting any entry breaks the chain from that point forward, making tampering detectable.

> Implementation: `runtime/ledger.py`

---

## I

### Intent

The canonical, validated representation of what a requester wants to do. An intent contains the action type, validated parameters, and a deterministic SHA-256 hash. The intent hash is used throughout the pipeline to bind all subsequent records (authorization, receipt, ledger) to the original request.

> Implementation: `runtime/structured_intent.py`

### Invariant

A property that must hold true at all times during system operation. RIO defines eight protocol invariants (INV-01 through INV-08) that are verified at the end of every pipeline run. Invariants cover completeness, receipt integrity, ledger integrity, hash chain consistency, and separation of duties.

> Specification: `spec/protocol_invariants.md`
> Implementation: `runtime/invariants.py`

---

## K

### Kill Switch

A global halt mechanism that immediately stops all new executions when engaged. The kill switch is the first check in the execution gate. When engaged, no actions proceed regardless of authorization status. Kill switch events are recorded in the ledger. Only admins can engage or disengage the kill switch.

> Implementation: `runtime/kill_switch.py`
> Specification: `safety/kill_switch_spec.md`

---

## L

### Ledger

An append-only, hash-linked chain of entries that records every decision made by the system. Each entry contains a reference to its receipt, a content hash, and the hash of the previous entry. The ledger provides tamper-evident ordering and completeness guarantees. Stored in `runtime/data/ledger.jsonl`.

> Implementation: `runtime/ledger.py`

---

## N

### Nonce

A single-use random value included in every authorization token. The execution gate checks the nonce against the nonce registry before executing. If the nonce has been consumed, the request is rejected. Nonces prevent replay attacks by ensuring each authorization token can be used exactly once.

---

## P

### Pipeline

The eight-stage Governed Execution Pipeline that every action request must traverse: Intake, Classification, Structured Intent, Policy and Risk, Authorization, Execution Gate, Receipt, Ledger. No stage can be skipped.

> Implementation: `runtime/pipeline.py`

### Policy

A set of organizational rules that determine whether a given action should be allowed, denied, or escalated to human approval. Policy rules are stored in `runtime/policy/policy_rules.json` and evaluated by the policy engine in priority order.

> Implementation: `runtime/policy/policy_engine.py`

### Policy Engine

The component that evaluates a canonical intent against the active policy rules. The engine processes rules in ascending priority order, checking action type, role, and optional conditions. The first matching rule determines the policy decision.

> Implementation: `runtime/policy/policy_engine.py`

---

## R

### Receipt

A cryptographic proof of a single pipeline decision. Each receipt contains the intent hash, decision hash, execution hash, timestamp, and ECDSA-secp256k1 signature. Receipts prove that a specific decision was made about a specific request at a specific time, and that the proof has not been altered.

> Implementation: `runtime/receipt.py`
> Schema: `schemas/receipt.json`

### Replay

The process of re-evaluating past corpus records through current or alternate policy and risk settings without executing real actions. Replay is used for policy testing, risk threshold tuning, and governance learning.

> Implementation: `runtime/corpus/replay_engine.py`

### Risk

A numeric score computed by the risk engine that quantifies the potential impact of an action. The score is derived from four components: base risk by action type, role risk of the requester, amount risk (for financial actions), and system target risk. The score is mapped to a risk level (LOW, MEDIUM, HIGH) based on configurable thresholds.

> Implementation: `runtime/policy/risk_engine.py`

### Risk Engine

The component that computes a numeric risk score for each canonical intent. The engine sums base risk, role risk, amount risk, and target risk components, then maps the total to a risk level using configurable thresholds.

> Implementation: `runtime/policy/risk_engine.py`

---

## S

### Simulation

The process of running what-if analyses against the governed corpus using proposed (not yet activated) policy or risk model changes. Simulations answer questions like "How many past requests would be blocked under the proposed policy?" without affecting the live system.

> Implementation: `runtime/corpus/simulation_api.py`

---

## V

### Verification

The process of validating the integrity of receipts and the ledger. Receipt verification checks the ECDSA signature. Ledger verification walks the hash chain to detect any broken links, tampered entries, or missing receipts.

> Implementation: `runtime/verification.py`, `runtime/verify_ledger.py`
