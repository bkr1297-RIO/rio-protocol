# Intent Translation Layer — Universal Grammar Orchestration

**Version:** 1.0.0
**Status:** Architecture Specification
**Category:** System Architecture / Integration

---

## Overview

The Intent Translation Layer is the orchestration grammar that lets RIO communicate across different systems, formats, and runtimes. It sits above the Governed Execution Protocol and performs three functions:

1. **Translates human/agent goals into structured intents.** Natural language requests, agent-generated plans, and API calls are converted into canonical intent objects that conform to the RIO intent schema.
2. **Translates structured intents into system-specific actions.** Canonical intents are mapped to the native operations of target systems (Microsoft Graph, Google APIs, internal APIs, custom connectors) through system-specific adapters.
3. **Translates system responses back into normalized results for receipts, ledger, and corpus.** Execution results from target systems are normalized into a standard result format that can be hashed, signed, and recorded.

The Intent Translation Layer does not make governance decisions. It translates. All governance decisions are made by the Governed Execution Protocol.

---

## 1. Role in the Stack

The Intent Translation Layer occupies a specific position in the RIO system stack:

| Layer | Responsibility |
|-------|---------------|
| **Goal Layer** | Human or agent expresses a goal or objective |
| **Intent Layer** | Goal is decomposed into one or more discrete intents |
| **Intent Translation Layer** | Intents are translated into canonical format (upstream) and system-specific actions (downstream) |
| **Governance Layer (RIO)** | Canonical intents are evaluated, authorized, and gated by the Governed Execution Protocol |
| **Execution Layer** | Authorized actions are executed against target systems |
| **Ledger / Corpus** | Receipts are recorded in the append-only ledger and structured in the Governed Corpus |
| **Learning Layer** | Historical data is analyzed to improve future governance |

The Intent Translation Layer bridges the gap between what a human or agent wants to do and what the governance system needs to evaluate. It ensures that every request entering the Governed Execution Protocol is in a standard, machine-readable format — regardless of where the request originated or what system it targets.

---

## 2. Core Responsibilities

### Type and Schema Translation

The Intent Translation Layer converts between different data formats, schemas, and type systems. A request originating as a natural language instruction, a structured API call, or an agent-generated plan is normalized into a canonical intent object that conforms to the RIO intent schema (see `/spec/canonical_intent_schema.md`).

### Capability Mapping

The Intent Translation Layer maps canonical action types to the specific capabilities of target systems. A canonical action type such as `send_email` is mapped to the appropriate API call for the target system (e.g., Microsoft Graph `POST /me/sendMail`, Google Gmail API `users.messages.send`, or an internal SMTP relay). The mapping is performed by system-specific adapters (connectors).

### Bidirectional Normalization

Translation operates in both directions:

- **Upstream (inbound):** Raw requests are normalized into canonical intents before entering the Governed Execution Protocol.
- **Downstream (outbound):** Canonical intents are translated into system-specific operations for execution.
- **Return path (inbound):** System-specific execution results are normalized into a standard result format for receipt generation.

---

## 3. Interfaces

### Upstream — Intent Input

The Intent Translation Layer accepts intent input from human users, AI agents, or upstream systems. The input is translated into a canonical intent object.

Example intent input (conceptual):

```json
{
  "source": "agent",
  "source_format": "natural_language",
  "raw_input": "Send a payment of 5000 EUR to Vendor_X from the Berlin office account",
  "context": {
    "session_id": "sess-abc-123",
    "actor_id": "agent-finance-01",
    "timestamp": "2026-01-10T10:30:00Z"
  }
}
```

This is translated into a canonical intent:

```json
{
  "intent_id": "INT-001",
  "request_id": "REQ-001",
  "action_type": "transfer_funds",
  "target_resource": "payment_system",
  "parameters": {
    "amount": 5000,
    "currency": "EUR",
    "recipient": "Vendor_X",
    "source_account": "Berlin_Office_Account"
  },
  "requested_by": "agent-finance-01",
  "justification": "Send a payment of 5000 EUR to Vendor_X from the Berlin office account",
  "risk_category": "HIGH",
  "required_approvals": ["Finance_Manager"],
  "timestamp": "2026-01-10T10:32:00Z",
  "status": "pending"
}
```

### Downstream — System-Specific Action Mapping

After the canonical intent passes through the Governed Execution Protocol and receives authorization, the Intent Translation Layer maps it to the native operation of the target system.

| Target System | Mapping Example |
|---------------|-----------------|
| Microsoft Graph | `POST /me/sendMail` with Graph-specific JSON body |
| Google APIs | `gmail.users.messages.send` with Google-specific payload |
| Internal APIs | `POST /api/payments/transfer` with internal schema |
| Custom Connectors | Adapter-specific translation defined by connector configuration |

The mapping is performed by system-specific adapters. Each adapter knows how to translate canonical intent parameters into the native format of its target system.

### Return Path — Normalized Execution Result

After execution, the target system's response is normalized into a standard result format:

```json
{
  "intent_id": "INT-001",
  "execution_status": "executed",
  "target_system": "payment_system",
  "target_response_code": 200,
  "target_response_summary": "Payment of 5000 EUR to Vendor_X completed",
  "result_data": {
    "transaction_id": "TXN-98765",
    "confirmation_timestamp": "2026-01-10T10:33:15Z"
  },
  "normalized_timestamp": "2026-01-10T10:33:16Z"
}
```

This normalized result is hashed to produce the `result_hash` field in the receipt, ensuring that the execution outcome is cryptographically bound to the decision record.

---

## 4. Universal Grammar Concept

The Intent Translation Layer implements a universal grammar for action orchestration. Canonical actions are system-agnostic — they describe what should happen without specifying how it should happen on any particular system.

The translation between canonical actions and native system operations is performed by connectors (adapters). Each connector implements the translation for a specific target system:

| Component | Role |
|-----------|------|
| **Canonical Action** | System-agnostic description of the intended action (e.g., `send_email`, `transfer_funds`, `create_document`) |
| **Connector / Adapter** | System-specific translator that maps canonical actions to native operations |
| **Target System** | The external system where the action is executed (e.g., Microsoft 365, Google Workspace, internal ERP) |

This architecture means that:

- **New systems can be added by writing new connectors** without modifying the core protocol, the governance model, or existing connectors.
- **Governance rules apply uniformly** regardless of which target system an action is directed at. A `transfer_funds` action is governed the same way whether it targets an internal payment system or an external banking API.
- **The canonical intent is the unit of governance.** The Governed Execution Protocol evaluates, authorizes, and records canonical intents — not system-specific API calls. This ensures that governance is consistent across all target systems.

---

## 5. Scope

This specification defines the **role and interface boundaries** of the Intent Translation Layer within the RIO system architecture.

This specification does **not** define:

- **Connector implementations.** Individual connectors for specific target systems (Microsoft Graph, Google APIs, etc.) are implementation-level artifacts, not protocol-level specifications. They are defined in their own documentation.
- **A fixed action catalog.** The set of canonical action types is extensible. New action types can be added as the system integrates with new domains and target systems.
- **Any single transport protocol.** The Intent Translation Layer is transport-agnostic. It can operate over HTTP, gRPC, message queues, or any other transport mechanism. The choice of transport is an implementation decision.

The Intent Translation Layer is a structural component of the RIO architecture. Its purpose is to ensure that every request entering the Governed Execution Protocol is in a standard format and that every execution result is normalized for receipt generation — regardless of the source, target, or transport.

---

## References

| Document | Path |
|----------|------|
| Canonical Intent Schema | `/spec/canonical_intent_schema.md` |
| Canonical Intent JSON Schema | `/spec/canonical_intent_schema.json` |
| Governed Execution Protocol | `/spec/governed_execution_protocol.md` |
| Receipt / Attestation Protocol | `/spec/receipt_protocol.md` |
| Reference Architecture | `/spec/reference_architecture.md` |
| Two-Loop Architecture | `/spec/two_loop_architecture.md` |
