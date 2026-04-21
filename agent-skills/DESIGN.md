# RIO Skills Model

**Status:** Non-normative

Skills are bounded capabilities that operate inside RIO without adding authority.

Skills do not authorize. Skills do not execute. Skills do not affect protocol conformance.

---

## Position in the Flow

Human
  ↓
Skills (clarify / audit / align)
  ↓
Decision Surface (human commits)
  ↓
RIO (enforce)
  ↓
Execution
  ↓
Receipt + Ledger (prove)

---

## Skill Categories

### 1. Enforcement / Proof Skills

- Check execution admissibility
- Verify receipts and ledger

Expose RIO guarantees.

---

### 2. Interaction Skills

- Clarify intent
- Detect ambiguity, drift, mismatch
- Surface alignment issues

Protect the human-agent relationship.

---

### 3. Builder / Operator / Auditor Skills

- Build within constraints
- Run and test the system
- Audit behavior and integrity

Protect system evolution.

---

## What Skills Do NOT Do

- Do not authorize
- Do not execute
- Do not override human decisions
- Do not affect protocol conformance

Skills guide behavior; they do not confer authority.

---

## Review Pattern

For high-stakes actions, multi-agent review may be used to improve decision quality. This does not replace RIO execution control or affect conformance.

The pattern:

- Multiple independent skills or agents review a proposal
- The human observes convergence or disagreement
- The human resolves differences
- Only then is a commit made

This is an optional usage pattern, not part of the RIO standard.

---

## One Rule

Skills guide behavior. RIO governs reality.
