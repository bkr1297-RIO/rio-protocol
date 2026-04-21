# SKILL: Interaction Monitor

**Status:** Non-normative (Advisory Only)

> This document defines a skill: a bounded way to use RIO.
> It is NOT part of the RIO standard or enforcement mechanism.

---

## Purpose

Monitor interactions for:

- Ambiguity
- Drift
- Mismatch
- False agreement

This skill provides awareness and advisory signals. It does not execute, authorize, or route.

---

## Capabilities

This skill MAY:

- Detect ambiguity in intent or instructions
- Detect drift between stated intent and proposed action
- Detect mismatch between expected and actual outcomes
- Emit advisory signals for humans or other skills to consider

---

## MUST NOT

This skill MUST NOT:

- Authorize actions
- Execute actions
- Route or trigger execution
- Modify tokens, receipts, or ledger
- Modify system state
- Generate or modify authorization mechanisms

It may only observe and advise.
