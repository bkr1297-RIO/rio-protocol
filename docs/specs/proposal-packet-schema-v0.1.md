# Proposal Packet Schema Specification

**Version:** 0.1  
**Status:** Spec layer ready | Local routing/testing ready | Production execution not ready  
**Date:** 2026-05-06  
**Author:** B-Rass (RIO Architect)  
**Depends on:** Personal AI Grammar Packet v0.1, Language Risk Policy Engine v0.1.2, RIO Receipt Protocol

---

## 1. Overview

This document defines the required fields, routing states, governance requirements, and receipt triggers for Proposal Packets. A Proposal Packet is the structured boundary object constructed when human signal moves from private meaning toward governed consequence.

> "Proposal Packets preserve human meaning without allowing meaning to bypass governance."

---

## 2. Packet Lifecycle

A Proposal Packet moves through the following states:

```
CONSTRUCTED → ROUTED → EVALUATED → AUTHORIZED → EXECUTED → RECEIPTED
                                  ↘ WITHDRAWN (at any point by human)
                        ↘ REFUSED (by governance evaluation)
```

| State | Description | Who Transitions |
|-------|-------------|-----------------|
| CONSTRUCTED | Packet assembled from scanner verdict + human signal | System (triggered by HOLD/WARN verdict) |
| ROUTED | Packet sent to appropriate governance path | System (based on consequence_level and public_claims) |
| EVALUATED | Governance layer has assessed the packet | ONE Answer Check or RIO |
| AUTHORIZED | Human has explicitly approved the crossing | Human (root authority) |
| EXECUTED | Consequential action has been performed | Sentinel (execution fidelity) |
| RECEIPTED | Cryptographic proof generated and ledger-written | MUS |
| WITHDRAWN | Human revoked the packet before execution | Human (at any point) |
| REFUSED | Governance evaluation determined crossing violates invariants | RIO or Policy Engine |

---

## 3. Required Fields

### 3.1 Identification

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `packet_id` | string (UUID v4) | Yes | Unique identifier for this Proposal Packet |
| `packet_version` | string (semver) | Yes | Schema version (e.g., "0.1.0") |
| `created_at` | string (ISO-8601) | Yes | Timestamp of packet construction |
| `state` | enum | Yes | Current lifecycle state |

### 3.2 Human Source

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `human_source` | object | Yes | Identifies the human authoring this crossing |
| `human_source.user_id` | string | Yes | Human's system identity |
| `human_source.session_id` | string | Yes | Session in which the crossing was initiated |
| `human_source.input_hash` | string (SHA-256) | Yes | Hash of the original human input that triggered the packet |

### 3.3 Meaning Context

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meaning_context` | enum | Yes | Classification tag for the type of meaning-source. NOT a narrative summary. |

**Allowed values for `meaning_context`:**

| Value | Description |
|-------|-------------|
| `private_reflection` | Internal processing, wondering, imagining |
| `somatic_signal` | Body-based awareness, felt sense, physical intuition |
| `symbolic_orientation` | Archetypal, mythic, or symbolic framing of experience |
| `emotional_activation` | Strong emotional state informing the crossing request |
| `existential_positioning` | Questions of purpose, calling, direction, identity |
| `relational_context` | Interpersonal dynamics informing the request |
| `pattern_recognition` | Human-identified patterns in their own experience |
| `external_input` | Information received from outside sources |
| `composite` | Multiple meaning-sources combined |

The system knows the *type* of meaning-source without claiming to understand or store the meaning itself. The actual content stays with the human.

### 3.4 Reliance Context

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reliance_context` | enum | Yes | What type of reliance the crossing involves |

**Allowed values for `reliance_context`:**

| Value | Description |
|-------|-------------|
| `exploration` | No reliance — human is exploring, not acting |
| `private_meaning` | Meaning held privately, no external reliance |
| `public_claim` | Assertion presented as factual to others |
| `action_authority` | Request for consequential action |
| `delegated_authority` | Transfer of decision-making scope |
| `financial_reliance` | Money, contracts, or economic commitment |
| `legal_reliance` | Legal obligation or representation |
| `medical_reliance` | Health-related decision or claim |
| `identity_reliance` | Claims about another person's identity or nature |

### 3.5 Requested Action

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requested_action` | object | Yes | What crossing is being requested |
| `requested_action.type` | enum | Yes | Category of crossing |
| `requested_action.description` | string | Yes | Human-readable description of what is being requested |
| `requested_action.target` | string | No | Who or what the action affects |
| `requested_action.scope` | string | No | Boundaries of the requested action |

**Allowed values for `requested_action.type`:**

| Value | Description |
|-------|-------------|
| `public_assertion` | Making a claim publicly |
| `external_communication` | Sending message to external party |
| `delegation` | Transferring authority to system or third party |
| `commitment` | Making a binding promise or agreement |
| `execution` | Performing a consequential real-world action |
| `financial_transaction` | Moving money or entering financial obligation |
| `legal_action` | Taking action with legal consequence |
| `medical_decision` | Making health-related decision |

### 3.6 Public Claims

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `public_claims` | array | Yes (may be empty) | List of factual assertions that require evidence routing |
| `public_claims[].claim` | string | Yes | The assertion being made |
| `public_claims[].evidence_status` | enum | Yes | Whether evidence exists for this claim |
| `public_claims[].source` | string | No | Where the claim originates |

**Allowed values for `evidence_status`:**

| Value | Description |
|-------|-------------|
| `verified` | Evidence exists and has been checked |
| `unverified` | Claim made without evidence verification |
| `personal` | Claim is personal experience (not externally verifiable) |
| `contested` | Evidence exists but is disputed |

### 3.7 Governance Requirements

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `consequence_level` | enum | Yes | Severity of consequence if crossing proceeds |
| `rio_required` | boolean | Yes | Whether RIO governance evaluation is needed |
| `sentinel_required` | boolean | Yes | Whether Sentinel execution verification is needed |
| `receipt_required` | boolean | Yes | Whether a MUS receipt must be generated |
| `answer_check_required` | boolean | Yes | Whether ONE Answer Check is needed for claims |

**Allowed values for `consequence_level`:**

| Value | Description | Governance Path |
|-------|-------------|-----------------|
| `private` | No external consequence | No Proposal Packet needed |
| `advisory` | Informational crossing, low consequence | Proposal Packet → receipt (optional) |
| `reliance` | Others may rely on this material | Proposal Packet → Answer Check → receipt |
| `consequential` | Real-world action with reversible consequence | Proposal Packet → RIO → receipt |
| `irreversible` | Real-world action with irreversible consequence | Proposal Packet → RIO → Sentinel → receipt |

### 3.8 Proof and Escalation

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `proof_status` | enum | Yes | Current proof state of the packet |
| `escalation_rules` | object | Yes | Conditions under which the packet escalates |
| `escalation_rules.escalate_on` | array of strings | Yes | Conditions triggering escalation |
| `escalation_rules.escalate_to` | string | Yes | Where escalation routes |
| `revocation_rules` | object | Yes | How the crossing can be undone |
| `revocation_rules.revocable` | boolean | Yes | Whether the crossing can be revoked after execution |
| `revocation_rules.revocation_window` | string | No | Time window for revocation (if applicable) |
| `revocation_rules.revocation_method` | string | Yes | How revocation is performed |

**Allowed values for `proof_status`:**

| Value | Description |
|-------|-------------|
| `pending` | No proof yet — packet just constructed |
| `evaluation_logged` | Scanner evaluation recorded |
| `governance_receipted` | RIO/Answer Check evaluation receipted |
| `execution_receipted` | Full execution receipt generated |
| `ledger_written` | Receipt hash written to tamper-evident ledger |

---

## 4. Routing Logic

The Proposal Packet routes based on the combination of `consequence_level`, `public_claims`, and `reliance_context`:

| Condition | Route |
|-----------|-------|
| `public_claims` is non-empty | → ONE Answer Check |
| `consequence_level` is `consequential` or `irreversible` | → RIO |
| `reliance_context` is `action_authority` or `delegated_authority` | → RIO |
| `consequence_level` is `irreversible` | → RIO + Sentinel |
| `reliance_context` is `financial_reliance`, `legal_reliance`, or `medical_reliance` | → RIO + Sentinel |

Multiple routes may apply simultaneously. The packet traverses all required governance paths before authorization.

---

## 5. Receipt Triggers

| Event | Receipt Type | Required |
|-------|-------------|----------|
| Packet constructed (PASS verdict) | None | No |
| Packet constructed (WARN verdict) | Evaluation log | Optional |
| Packet constructed (HOLD/BLOCK/INVALID) | Evaluation receipt | Yes |
| ONE Answer Check completed | Governance receipt | Yes |
| RIO evaluation completed | Governance receipt | Yes |
| Human authorization granted | Authorization receipt | Yes |
| Execution performed | Execution receipt | Yes |
| Packet withdrawn by human | Withdrawal receipt | Yes |
| Packet refused by governance | Refusal receipt | Yes |

All receipts follow the MUS receipt protocol: SHA-256 hash, previous_receipt_hash linkage, ledger entry.

---

## 6. Scanner Integration

The Grammar Scanner verdict maps to Proposal Packet construction as follows:

| Scanner Verdict | Proposal Packet Action |
|-----------------|----------------------|
| PASS | No packet constructed. Optional evaluation log. |
| WARN | Packet constructed with `consequence_level: advisory` or `reliance`. Routes to Answer Check if public_claims present. |
| HOLD | Packet constructed with `consequence_level: consequential` or `irreversible`. Routes to RIO. |
| BLOCK | Packet constructed with `state: REFUSED`. Evaluation receipt generated. No further routing. |
| INVALID | Packet constructed with `state: REFUSED`. Evaluation receipt generated. Input malformed. |

---

## 7. Human Authority Points

The human retains authority at every stage:

| Stage | Human Authority |
|-------|----------------|
| Construction | Human authored the original signal |
| Routing | Human can withdraw before evaluation |
| Evaluation | Human can override WARN (proceed with awareness) |
| Authorization | Human must explicitly approve HOLD crossings |
| Execution | Human can revoke during execution window |
| Post-execution | Human can invoke revocation_rules if revocable |
| Any point | Human can invoke kill switch (global revocation) |

---

## 8. Constraints

- The Proposal Packet MUST NOT interpret, validate, reduce, or inflate human meaning.
- The `meaning_context` field MUST be a classification tag, never a narrative summary.
- The system MUST NOT treat the Proposal Packet as an authority layer.
- The system MUST NOT block private exploration that does not cross into consequence.
- The system MUST NOT treat scanner verdicts as final authority — they trigger packet construction, not governance decisions.
- The system MUST NOT allow meaning to bypass governance regardless of personal significance.
- The system MUST NOT allow governance to reduce or flatten human meaning.

---

## 9. Version History

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-05-06 | Initial schema specification |
