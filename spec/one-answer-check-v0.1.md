# ONE Answer Check — v0.1

**Status:** Active — runtime prototype implemented (rio-proxy, grammar v0.1.1)  
**Type:** Pre-reliance inspection protocol  
**Layer:** Human decision support (not governance, not execution)

---

## 1. Purpose

ONE Answer Check is a pre-reliance inspection protocol. It helps a human inspect AI answers before relying on them. It does not execute, approve, block, or govern consequential machine action.

Answer Check governs reliance. RIO governs consequence. Receipts prove crossings.

---

## 2. Scope

Answer Check operates in the space between receiving an AI-generated answer and deciding whether to rely on it. It provides structured claim-level analysis so the human can make an informed reliance decision.

Answer Check applies when:

- A human receives an AI-generated answer to a question.
- The human intends to rely on that answer for a decision or action.
- The reliance context determines how much scrutiny is appropriate.

---

## 3. Non-Goals

Answer Check does **not**:

- Execute actions on behalf of the human.
- Approve or block governed machine actions (that is RIO's role).
- Replace human judgment — it informs it.
- Guarantee factual accuracy — it surfaces confidence gaps.
- Store raw question or answer text (only cryptographic hashes are persisted).
- Act as a governance gate — it has no authority over execution.
- Generate receipts that enter the RIO governance ledger (it produces its own inspection records).

---

## 4. Reliance Contexts

Each inspection is scoped to a declared reliance context that determines the appropriate level of scrutiny.

| Context | Description | Scrutiny Level |
|---------|-------------|----------------|
| `general` | Casual information use | Standard |
| `personal_decision` | Life decisions (career, relationships) | Elevated |
| `financial` | Money, investment, budgeting | High |
| `medical` | Health, treatment, diagnosis | High |
| `legal` | Law, contracts, compliance | High |
| `technical` | Engineering, architecture, code | Elevated |
| `educational` | Learning, study, academic work | Standard |

The reliance context does not change the inspection method — it changes the threshold at which the human should pause before relying.

---

## 5. Claim Extraction

Answer Check decomposes an AI answer into individual factual claims. Each claim is evaluated independently.

For each claim, the inspection produces:

| Field | Type | Description |
|-------|------|-------------|
| `claim_index` | integer | Sequential position in the answer |
| `claim_text` | string | The extracted factual assertion |
| `evidence_status` | enum | `supported`, `unverified`, or `unsupported` |
| `confidence` | enum | `high`, `medium`, or `low` |
| `what_to_verify` | string | One sentence describing what the human should check |

---

## 6. Evidence Status

Each claim receives one of three evidence status classifications:

- **supported** — The claim is consistent with well-established knowledge. No immediate verification needed for standard reliance.
- **unverified** — The claim is plausible but cannot be confirmed without external sources. The human should verify before relying in elevated or high-scrutiny contexts.
- **unsupported** — The claim is contradicted by established knowledge, outdated, or fabricated. The human should not rely on this claim without independent confirmation.

---

## 7. Confidence Gap

The overall confidence gap measures how much uncertainty exists across all claims in the answer.

| Level | Meaning |
|-------|---------|
| `low` | Answer is well-supported; most claims are verifiable |
| `medium` | Some claims need verification; partial gaps exist |
| `high` | Significant gaps or contradictions; reliance is risky |

---

## 8. Reliance Verdicts

Answer Check produces one of four reliance verdicts. These are advisory — the human retains final authority.

| Verdict | Meaning | Human Action |
|---------|---------|--------------|
| `commit` | Safe to act on this answer for the stated context | Proceed with normal confidence |
| `revise` | Partially usable; specific claims need correction | Use supported claims; verify or discard others |
| `hold` | Too many gaps to act on now | Do not rely until gaps are resolved |
| `refuse` | Fundamentally unreliable for the stated context | Discard and seek alternative sources |

---

## 9. Answer Fit

Separate from reliance verdict, Answer Check evaluates whether the answer actually addresses the question asked.

| Fit | Meaning |
|-----|---------|
| `strong` | Directly answers the question for the stated context |
| `good` | Mostly answers it; minor aspects unaddressed |
| `partial` | Answers some aspects but misses key parts |
| `poor` | Does not adequately address the question |

---

## 10. Receipt-Shaped Output

Answer Check produces a structured inspection record. This is not a RIO governance receipt — it is a reliance inspection record.

```json
{
  "questionHash": "<sha256>",
  "answerHash": "<sha256>",
  "relianceContext": "financial",
  "relianceDecision": "revise",
  "confidenceGap": "medium",
  "answerFit": "good",
  "claimCount": 5,
  "supportedCount": 3,
  "unverifiedCount": 1,
  "unsupportedCount": 1,
  "mainIssue": "One financial claim lacks verifiable source.",
  "claims": [
    {
      "claim_index": 1,
      "claim_text": "The S&P 500 returned 10% annually over the last century.",
      "evidence_status": "supported",
      "confidence": "high",
      "what_to_verify": "Check historical data for exact figure and time period."
    }
  ],
  "grammarVersion": "answer-check-v0.1.1"
}
```

**Privacy invariant:** Raw question and answer text are never stored. Only SHA-256 hashes are persisted. The inspection record contains extracted claims (which are analytical summaries, not verbatim input).

---

## 11. Conformance Expectations

A conforming Answer Check implementation MUST:

1. Accept a question, answer, and reliance context as input.
2. Decompose the answer into individual factual claims.
3. Evaluate each claim for evidence status and confidence.
4. Produce a reliance verdict, confidence gap, and answer fit assessment.
5. Return a structured record matching the schema in §10.
6. Never store raw question or answer text — only cryptographic hashes.
7. Never execute, approve, or block actions — only inform human reliance decisions.

A conforming implementation MAY:

- Use any method to evaluate claims (LLM, retrieval, rule-based, hybrid).
- Extend the claim schema with additional fields (source URLs, timestamps).
- Integrate with external verification services for evidence checking.

A conforming implementation MUST NOT:

- Claim to guarantee factual accuracy.
- Act as a governance gate or execution authority.
- Store personally identifiable information beyond what is necessary for the inspection record.

---

## 12. Relationship to RIO

Answer Check and RIO operate in different domains:

| Concern | Answer Check | RIO |
|---------|-------------|-----|
| Domain | Human reliance on AI answers | Machine execution of consequential actions |
| Authority | Advisory only | Governance authority |
| Output | Inspection record | Governance receipt |
| Gate | None — informs, does not block | Sentinel gate — blocks without approval |
| Ledger | Own inspection log | Formal governance ledger |
| Binding | None — human decides | Cryptographic binding (handoff → action) |

Answer Check may inform a human's decision to approve a RIO-governed action, but it has no direct interface to the RIO governance pipeline. The human remains the bridge between reliance inspection and governance approval.

---

## 13. Explicit Statements

- Answer Check governs reliance. RIO governs consequence. Receipts prove crossings.
- Answer Check does not execute, approve, block, or govern consequential machine action.
- Answer Check is not a RIO component — it is a ONE component that operates in the pre-reliance space.
- The reliance verdict is advisory. The human retains final authority over whether to rely.
- Raw text is never stored. Only hashes are persisted. Privacy is structural, not policy-based.

---

## 14. Implementation Evidence

The reference implementation exists in `rio-proxy` (grammar version `answer-check-v0.1.1`):

- 7 reliance contexts implemented
- 4 reliance verdicts implemented
- 4 answer fit levels implemented
- 3 evidence status levels implemented
- SHA-256 hashing for question and answer (raw text never stored)
- 10 automated tests covering schema validation, hash-only storage, deterministic hashing, user isolation, and authentication enforcement

---

## 15. Version History

| Version | Date | Change |
|---------|------|--------|
| v0.1 | 2026-05-05 | Initial protocol spec (promoted from implementation) |
