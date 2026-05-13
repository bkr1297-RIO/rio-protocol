# ONE/RIO/MUSS Promotion Queue v0.1

Status Truth Label: draft-preserved  
Maturity: draft-review governance artifact  
Date: 2026-05-13 MDT  
Repository: bkr1297-RIO/rio-protocol  
Scope: Draft artifact review, promotion planning, and status discipline  
Canonical status: Not canonical until explicit source-of-truth promotion  

---

## Purpose

This Promotion Queue organizes newly preserved ONE/RIO/MUSS draft artifacts so they can be reviewed without accidentally becoming canonical law.

It answers:

- what is already canonical;
- what is draft-preserved;
- what is future/not yet implemented;
- what should be promoted, held, split, amended, archived, or tested;
- what must not be overclaimed.

This file does not promote any artifact by itself.

---

## Source-of-truth relationship

The canonical RIO protocol source of truth remains `SOURCE_OF_TRUTH.md` and the canonical protocol files it names.

If this queue conflicts with source-of-truth materials, source-of-truth materials govern until explicitly amended.

Keeper boundary:

> Merged into the repo does not mean promoted to source-of-truth. It means preserved for governed review.

---

## Promotion rule

A draft artifact may move toward canonical status only through an explicit later action that identifies:

1. the artifact being promoted;
2. the exact canonical target;
3. the authority boundary it protects;
4. the implementation or conformance relationship;
5. what the promotion proves;
6. what the promotion does not prove;
7. the source-of-truth file or index being amended.

No artifact may promote itself.

---

## Promotion states

| Queue state | Meaning |
|------------|---------|
| keep draft | Preserve for review; no promotion yet |
| stress test | Run demanding review before deciding |
| split | Separate mixed concerns into smaller artifacts |
| amend | Keep artifact but tighten language, status, or scope |
| promote candidate | Strong candidate for later canonical promotion |
| future hold | Preserve as future-layer material only |
| archive / supersede | Mark as legacy, merged elsewhere, or no longer governing |

---

## Promotion queue

| Artifact | Location | Current label | Queue state | Promotion target / next action | Main blockers |
|---------|----------|---------------|-------------|--------------------------------|---------------|
| RIO canonical protocol baseline | `SOURCE_OF_TRUTH.md` + named canonical files | canonical | no queue action | Maintain as current source-of-truth | Runtime conformance, external validation, Chronicle, full independent receipt verification remain open |
| Status Truth Labels v0.1 | `docs/governance/status-truth-labels-v0.1.md` | draft-preserved | promote candidate after review | Possible governance policy for artifact labeling | Needs stress test against existing docs; may need canonical index update if promoted |
| PR #17 Merge Receipt v0.1 | `docs/handoff/pr17-merge-receipt-v0.1.md` | draft-preserved / status note | keep draft | Keep as repo status note | Not a cryptographic receipt; should not be treated as proof beyond repo-status documentation |
| Naming Promotion Index v0.1 | `docs/architecture/naming-promotion-index-v0.1.md` | draft-preserved | stress test | Possible architecture index after cleanup | Must avoid treating named concepts as implemented/canonical |
| Precision by Friction v0.1 | `docs/architecture/precision-by-friction-v0.1.md` | draft-preserved | amend / promote candidate | Architecture appendix explaining generator-governor-gate-receipt-learning | Needs mapping to canonical state machine and conformance language |
| Governed Self-Observation Layer v0.1 | `docs/architecture/governed-self-observation-layer-v0.1.md` | draft-preserved | split / stress test | May split into MANTIS, Sentinel, verification, and Oddity concerns | Risk of self-observation reading like self-authorization |
| Adaptive Trust Envelope v0.1 | `docs/architecture/adaptive-trust-envelope-v0.1.md` | draft-preserved | stress test | Relationship-aware friction doctrine | Needs clear proof that trust changes friction, not authority |
| Human-Led Operating Grammar v0.1 | `docs/spec/human-led-operating-grammar-v0.1.md` | draft-preserved | promote candidate after demanding session | Possible Scribe/Bondi grammar spec | Needs examples, packet semantics, and conformance hooks |
| Human Control Packet v0.1 | `spec/human-control-packet-v0.1.md` | draft-preserved | promote candidate | Boundary packet for human-authored control | Needs schema/test examples and relation to proposal/commit/token lifecycle |
| Connector Action Authorization Packet v0.1 | `spec/connector-action-authorization-packet-v0.1.md` | draft-preserved | stress-tested; keep as lineage | Historical v0.1 draft | Superseded for review by v0.2 draft; do not promote v0.1 directly |
| Connector Action Authorization Packet Stress Test v0.1 | `docs/reviews/connector-action-authorization-packet-stress-test-v0.1.md` | draft-preserved | keep draft | Review artifact supporting v0.2 | Not itself a spec or canonical artifact |
| Connector Action Authorization Packet v0.2 | `spec/connector-action-authorization-packet-v0.2.md` | draft-preserved | promote candidate after schema + conformance outline | Connector governance spec candidate | Passed documentation-level stress test; still needs JSON Schema, conformance tests, canonicalization rules, chain-step receipt linking, connector policy packs, and runtime enforcement evidence |
| Connector Action Authorization Packet v0.2 Stress Test v0.1 | `docs/reviews/connector-action-authorization-packet-v0.2-stress-test-v0.1.md` | draft-preserved | keep draft | Review artifact supporting schema/conformance next step | Not itself a spec or canonical artifact |
| Failure Modes Catalog v0.1 | `docs/failure-modes/one-rio-muss-failure-modes-v0.1.md` | draft-preserved | high-priority stress test | Failure-mode review and conformance-test seed | Needs verdict mapping: HOLD, BLOCK, CLARIFY, INVALID, deny, require review |
| Open Protocol Repo Topology v0.1 | `docs/architecture/open-protocol-repo-topology-v0.1.md` | draft-preserved | keep draft | Repo-family planning guide | Must not create repos or imply repo readiness by naming alone |
| Embodied Co-Regulation Layer v0.1 | `docs/architecture/embodied-co-regulation-layer-v0.1.md` | draft-preserved / future-layer | future hold | Future physical-world protocol pack | Robotics, exosuits, safety, consent, liability, privacy, and local governance are not implemented or validated |
| Gemini Context Packet v0.1 | `docs/handoff/gemini-context-packet-v0.1.md` | draft-preserved | keep draft | External model handoff utility | Not canonical protocol; useful as bounded review packet |
| ONE Protocol | no repo yet | future / not yet implemented | future hold | Candidate future repo only after stable ONE boundary | Needs stable operating-environment definition, cell/runtime schema, or conformance surface |
| MUSS Protocol | no repo yet | future / not yet implemented | future hold | Candidate future repo for sovereignty container | Needs stable consent/scope/revocation/personal constitution schema |
| Chronicle Protocol | not implemented | future / not yet implemented | future hold | Human-readable history/explanation layer | Must avoid proof/wisdom/person collapse |
| Oddity Engine | no repo yet | future / not yet implemented | future hold / concept review | Possible anomaly/emergence layer or MANTIS submodule | Needs schema, scope, and clear separation from audit, Sentinel, and MANTIS |
| Creation Trust Protocol | no repo yet | future / not yet implemented | future hold | Economic stewardship layer | Requires legal/economic review; not core runtime dependency |

---

## Immediate review order

Recommended demanding-session order:

1. Connector Action Authorization Packet v0.2 schema/conformance outline
2. Failure Modes Catalog v0.1
3. Human-Led Operating Grammar v0.1
4. Human Control Packet v0.1
5. Status Truth Labels v0.1
6. Open Protocol Repo Topology v0.1
7. Embodied Co-Regulation Layer v0.1

---

## Promotion checklist

Before any artifact is promoted, answer:

1. What status truth label does it currently carry?
2. What authority boundary does it protect?
3. What canonical artifact would it amend or become?
4. Does it alter runtime behavior, conformance, or only documentation?
5. What examples or tests support it?
6. What implementation status can be honestly claimed?
7. What external validation status can be honestly claimed?
8. What must remain explicitly out of scope?
9. Does it require a license or repo-boundary decision?
10. What source-of-truth file must be updated if promoted?

---

## Keeper lines

- Named is not built.
- Merged is not canonical.
- Draft-preserved is not implemented.
- Implementation is not external validation.
- Future layer is not current runtime.
- A repo is not a concept container; it is a boundary and proof surface.
- Promotion requires an explicit human-authorized source-of-truth update.

---

## Closing status

This queue is itself draft-preserved. It is a governance aid for review and sorting. It does not alter canonical protocol status, runtime behavior, repository licensing, or implementation claims.
