# Protocol Blueprint Template

This template defines the standard structure for each protocol stage in the Governed Execution Protocol.

Each protocol specification should include the following sections:

---

## 1. Purpose

Describe the role of this protocol stage and why it exists.

---

## 2. Scope

Define what this protocol is responsible for and what it is not responsible for.

---

## 3. Inputs

List all inputs required for this stage to operate.

---

## 4. Required Fields

List required fields that must be present. If missing, the protocol must fail or request clarification.

---

## 5. Processing / Rules

Describe what the protocol does and what rules it enforces.

---

## 6. Decision Logic

Describe how the protocol decides outcomes (allow, deny, escalate, request more information, etc.).

---

## 7. Outputs

List the artifacts produced by this stage.

---

## 8. Failure Modes

Describe what happens if this stage fails, denies, or cannot proceed.

---

## 9. Logging & Audit Requirements

Describe what must be recorded for auditability and the governed corpus.

---

## 10. Security Considerations

Describe any security controls relevant to this stage.

---

## 11. Related Invariants

List which protocol invariants apply to this stage.

---

## 12. Upstream / Downstream Dependencies

- **Upstream:** Which protocol stage provides input.
- **Downstream:** Which protocol stage consumes output.

---

All protocol stages (Intake, Classification, Intent Validation, Structured Intent, Policy & Risk, Authorization, Execution Gate, Receipt, Ledger, Learning) must follow this structure.
