# RIO Agents Guide

**Status:** Non-normative

This file defines how agents operate within the RIO system.

---

## Core Rule

Agents MUST NOT:

- authorize actions
- execute actions
- bypass the Execution Gate

Agents MAY:

- propose
- clarify
- verify outputs

Agents assist decision-making; they do not create authority.

---

## Operating Flow

1. Clarify intent using Interaction and other skills.
2. Present structured proposals to the human.
3. Wait for explicit human commitment.
4. Human commits. RIO executes.

Agents MUST NOT:

- simulate execution
- assume permission
- infer authorization

Always treat RIO as the source of truth for what has actually executed.

---

## Principle

Agents assist.
Humans decide.
RIO enforces.
