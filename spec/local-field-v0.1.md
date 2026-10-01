# ONE Local Field v0.1 — bounded passage profile

Status: draft implementation profile for Brian's build assignment, subordinate to the architecture owner's R-07 / issue #322. This adds portable field membership and passage bindings; it does not rename Canonical Intent, execution tokens, authority roots, RIO, or receipts. No constitutional ratification follows from conformance.

## Existing semantics and additions

`identity_and_credentials.md`, `role_model.md`, `execution_envelope.md`, `schemas/execution_token.json`, `15_time_bound_authorization.md` and `receipt_binding_v0.1.md` remain the existing owners. Their request/token objects alone do not carry field membership, independently enrolled node keys, model candidate origin, current delegation lineage and Return correlation together. `schemas/local-field-v0.1.schema.json` supplies that transport-neutral binding. It does not replace an execution token with a network message.

The gateway implementation is `rio-system/gateway/local-field/`; existing security, policy, execution, ledger and receipt owners retain their functions. Architecture contract: `one-rio-muss-architecture/docs/architecture/local-field/ONE-LOCAL-FIELD-BUILD-SPEC-v0.1.md`. Receipt adaptation: `rio-receipt-protocol/spec/LOCAL_FIELD_RECEIPT_PROFILE_v0.1.md`.

## Signed record

The wire object is `{body, signature}`. `body.type` and `body.field_id` are signed domain separators. Every body has a record ID, issuance and expiry. Signature is Ed25519, 64 raw bytes represented as lowercase hex; enrolled verification keys are 32 raw bytes in lowercase hex, matching the existing gateway principal model. Private keys are never transported in records.

Signature input is UTF-8 JSON with recursively sorted object keys, preserved array order and JSON primitive encoding, as implemented by the gateway's strict `canonicalizeArgs`. Inputs must be finite plain JSON with no undefined values, cycles or accessors. SHA-256 over the same bytes is the payload/commitment hash. The gateway receipt's existing five-hash projection has its own retained field order; do not substitute this serializer into that historical recipe.

## Field, membership and authority

A field definition is signed by an externally configured human root principal and pins field ID, receiver, policy and initial dependencies. The registry stores this declaration; storage does not originate authority. The receiver holds its own key only. Root and enrolled nodes use distinct keys.

An enrollment is root-signed and records node/principal identity, node type, key, capabilities, interfaces and custody boundary. Enrollment issuance supplies `created_at`; node revocation event time supplies `revoked_at`. Initial status is active, and the root-signed enrollment establishes the SourcePoint relationship and revocation path. Mobile is a valid node type without requiring a mobile application. Proposer/executor role separation follows the existing principal model.

Grants bind exact subject, action, target node/resource, scope, purpose, dependencies, conditions and optional payload hash. The issuer and validity window live in the signed body. Parent references reconstruct delegation; every ancestor must be current, correctly signed, scope compatible and not revoked, superseded or spent. Child expiry cannot exceed its parent. Descendants cannot waive parent constraints or manufacture sovereignty. Empty conditions are the implemented v0.1 condition profile; unimplemented conditions fail closed. Use counts include ancestors and are consumed at point of use. Revocation and dependency updates are signed controls, never telemetry edits.

## Passage and aperture

A passage signs its subject/source, exact action and target, payload hash, grant reference, dependencies/conditions, validity window, nonce, intent/origin, correlation and required Return recipient. Admission resolves node attribution, current standing and existing RIO policy separately from execution. Receiving or validating a message does not authorize execution. Point-of-use fidelity rechecks the exact admitted hash, signatures and current state before consuming a single-use execution token and producing an attempt.

Candidate artifacts represent proposals, drafts, inferences, observation claims or recommended actions with **no authority effect**. Model/agent nodes must reference a stored attributed candidate in their passage. Formation does not convert candidate content into a grant. Model output cannot invoke the accepted adapter directly.

Passage nonces and IDs cannot be reused after admission. Expired records are rejected. Unfinished admissions are held after restart; stored decisions do not regenerate execution permission. Interrupted attempts return an unresolved disposition, not inferred success or non-occurrence.

## Return and transport

Return binds passage, intent and correlation IDs to disposition and, when completed, receipt ID. `schemas/local-field-return-v0.1.schema.json` describes the full attributed Return. The receiver signs `{returned: <Return without attestation>, binding: <attestation without signature>}`, including the outcome, recipient, time and identifiers. The signature is verified against the enrolled receiver; correlation alone is insufficient. Requested, admitted, attempted, observed and returned are separate records. Receipts bind observation claims and their method; they do not make those claims universally true.

Transport is an adapter. The first adapter is HTTP JSON on loopback with signed controls, candidates, admissions, executions and read-only queries. Declared node interfaces constrain use. Remote/mobile clients require a separately secured transport deployment; this build does not provide network discovery or a phone application. Runtime-specific file bounds, database choice, configuration and process lifecycle belong to `rio-system`.

## Verification

## Bilateral completion profile (19 A–S controlling packet)

The predecessor single-receiver profile remains historical and compatible; it does not establish bilateral acceptance. A root-signed field opts into `local-field-bilateral-v0.1` and pins a separate ordinary signed Return grant (`return_authority_basis`) and `return_policy`. Existing identity, grant lineage, RIO, Sentinel, ledger and native receipt owners remain unchanged in jurisdiction.

The immutable signed passage has explicit `schema_version: 0.1`, `replay: single-use`, source and subject fields, action/target node/resource, payload hash, authority basis, scope/purpose, dependencies/conditions, issue/expiry, nonce/correlation, optional non-authoritative lineage, origin and required Return destination. The bounded carrier profile requires source == subject and Return destination == source; unsupported carrier relations are refused. Unknown versions/extensions cannot expand authority. Semantic name equivalents (`source_node`, `target_node`, `expires_at`, `return_requirement.to`) are the existing owner's field names.

Node A resolves current standing/RIO and signs a separately persisted EGRESS judgment before its owned emission. B verifies the signed transit but independently resolves its own standing/RIO and records INGRESS. Immediately before effect, B records a distinct current execution-authority judgment, then exact submitted-operation fidelity and token burn. Sender envelope fields never contain later receiver judgments; all judgments refer to its immutable full hash.

Return egress and Return ingress separately resolve a current signed `record_return` grant: subject B, target node A, target `return-record`, scope `attributed-record-only`, purpose `local-field-return`. That grant authorizes recording attributable material, not truth, evidence, settlement or any consequential successor. The existing native receipt and Return remain unchanged in format. A signed Return transit binds the full native proof/chain. A independently verifies sender, integrity, correlation, native artifact hashes and current Return standing/RIO, then records `ADMITTED_AS_ATTRIBUTED_RECORD`, truth `UNESTABLISHED`, observation `ATTRIBUTED_CLAIM`, evidence `NOT_ADMITTED`, settlement `UNSETTLED`, completion `RETURNED_WITH_RESIDUE`. Receipt ≠ Occurrence ≠ Truth; Observation ≠ Evidence; Evidence ≠ Settlement. No independent witness implies permission.

The runtime stores all records in its existing local ledger and never retransmits pending dispatch on restart. Loopback peer configuration and custody remain runtime-owned; no replicated authority, remote deployment or whole-machine no-bypass claim follows. Equal projected endpoints do not erase distinct passage outcomes or residue. Reference PR #226 at `10fa67c8755373e1bf71d598cbc39887593bbef0` is EVIDENCE_ONLY lineage; no Passage Geometry subsystem or private reference implementation is copied.

`schemas/local-field-bilateral-v0.1.schema.json` adds portable transit and typed Return-admission shape over the existing profile. Run `python tests/local_field/validate_bilateral_runtime.py <actual-bilateral-trace.json>`. This validates real emitted records and malformed-record rejection, not simulation or authority. The proposed Test It v2 comparison harness remains post-build, separately corrected/evaluated against a pinned unchanged runtime.

Install `tests/local_field/requirements.txt`, then run `python tests/local_field/validate_runtime_trace.py <rio-system acceptance-trace.json>` to validate actual signed runtime records and Return against the shared schemas. It checks shape only; crypto/current-standing/fidelity tests run in the gateway. A passing schema validator is not runtime acceptance.
