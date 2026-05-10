# forbidden_output_pattern — Status and Interpretation

**Version:** v0.1.3  
**Status:** Documentation only. No runtime wiring.

---

## Definition

`forbidden_output_pattern` is a regex pattern embedded in each negative test vector that describes the exact language constituting a category collapse. It is the most specific signal available for detecting reliance-collapse.

---

## Status by Context

### Within Synthetic Vectors

`forbidden_output_pattern` is the **decisive expected-failure marker**.

- It is ground truth for detection.
- If the pattern matches `system_behavior`, the trace has collapsed — regardless of other signals.
- Non-collapse indicators cannot override a forbidden_output_pattern match.
- Match confidence is `exact`.
- Human review is not required for synthetic validation.

### In Live Traces

`forbidden_output_pattern` is a **detector signal, not ground truth**.

- It indicates a potential collapse worth investigating.
- Live trace evaluation requires:
  1. **Trace context** — what was the system doing when this language appeared?
  2. **Match basis** — was the match structural, keyword, or pattern-based?
  3. **Reviewable evidence** — can a human verify the detection independently?
- Match confidence should be reported as `high` (not `exact`) for live traces.
- `human_review_required` is always `true` for live trace evaluation.

---

## Why the Distinction Matters

Synthetic vectors are authored with known intent. The forbidden pattern is placed there by the test author who knows what collapse looks like. In live traces, the same pattern might appear in:

- Quoted text (the system is quoting a user, not asserting)
- Negated context ("I will NOT treat confidence as truth")
- Hypothetical framing ("If someone were to say...")
- Pedagogical context ("An example of collapse would be...")

These require human judgment to distinguish from actual collapse.

---

## Harness Behavior

The harness implements this distinction as follows:

```
if (context === 'synthetic') {
  forbidden_output_pattern → match_basis: 'forbidden_output_pattern'
  match_confidence: 'exact'
  human_review_required: false
}

if (context === 'live') {
  forbidden_output_pattern → match_basis: 'forbidden_output_pattern'
  match_confidence: 'high'
  human_review_required: true
}
```

---

## Keeper Line

Nothing expands silently. This documentation does not authorize live trace evaluation.
