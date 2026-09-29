# Open Arrow Customer Zero profile v0.1

Bounded implementation contract for review. No universal standing enum, language ratification, public standard or successor installation authority is asserted.

Schema: `schemas/open-arrow-v0.1.schema.json`. Existing `local-field-v0.1.schema.json` gains only an optional constituted profile, passage origin correlation and read-only arrow query. All live node/grant/signature/replay semantics remain Local Field's. Architecture: `one-rio-muss-architecture/docs/language/open-arrow/ONE-OPEN-ARROW-BUILD-SPEC-v0.1.md`, #322/R-07 with R-08/R-18 dependencies.

The artifact envelope has an immutable ID, kind, four standing axes, body, parent references, time, SHA-256 integrity and receiver signature. Its ID hashes the unsigned body under the native compiler's canonical JSON profile; the full artifact is signed under the existing gateway canonical JSON/Ed25519 profile. The receiver public key must be reconstructed from root-signed enrollment. Schema validation is structural; it never establishes authority, occurrence or evidence qualification.

Epistemic, Authority, Lifecycle and Fidelity are independent profile axes. Lifecycle values are closed per artifact kind in the schema; a Hold is HELD, an Observation is RETURNED, and only Settlement may be SETTLED_BOUNDED or UNSETTLED. Formation rejects the entire malformed closed request, including payload types, extra properties, hash mismatch and UTF-8 content above 4096 bytes, before persisting Proposal/HOLD. Schema maxLength is a structural limit; the runtime additionally enforces the byte limit. They coexist with explicit effects, temporal, settlement and accountability records. An Observation cannot carry HUMAN_BOUND authority; changing `kind` to Evidence cannot pass while retaining observational epistemic standing. A new Evidence artifact must refer to its source via a distinct Promotion artifact carrying a fresh exact signed human disposition, basis and adjudication. The closed graph also covers Proposal→Commitment, Evidence→Judgment, Judgment→Settlement and Settlement→Successor. Signature validity alone is insufficient: the runtime verifies the configured human root, field, freshness, exact source identity, admissible edge and applicable semantics.

The conservation vector carries Subject, Scope, Authority, Standing, Dependencies, Uncertainty, Lineage and Effects through source/AST/ONE-IR/OA-IR sidecars. The frozen native AST/ONE-IR are not renamed or modified. Loss is a compile error. Source text and planned compiler authority references cannot be promoted to a grant. Runtime mutation is rejected even after admission.

The actual receipt remains the existing gateway five-hash signed Local Field receipt. TOP's TransitionOccurrenceReceipt is a named observation projection of that native receipt, with its original ID retained. It claims observation representation only. Receipt, EvidenceAssessment, SuccessionDecision, Settlement and successor standing have distinct identities and require independently attributable basis. None creates future permission. Failed execution preserves uncertainty rather than inventing non-occurrence.

Validate an actual runtime export (requires `tests/local_field/requirements.txt`):

```sh
python tests/local_field/validate_open_arrow.py /path/to/customer-zero-trace.json
```

Runtime: `rio-system/gateway/local-field/OPEN-ARROW.md`. Compiler and settlement evaluator: existing private reference owners plus `extensions/compiled-occurrence-return/open-arrow`. Execution receipt verification: existing `rio-receipt-protocol/verifier/local-field.js`, unchanged.
