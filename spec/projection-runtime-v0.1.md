# ONE Projection Runtime v0.1 portable composition

Draft build profile; no canon ratification. Runtime owner is `rio-system/gateway/local-field/projection.mjs`. Shared shape lives in `schemas/projection-runtime-v0.1.schema.json`; existing `local-field-v0.1` passage/field/query records carry optional references. There is no second identity root, grant resolver, governor or receipt protocol.

## Distinct objects and standing

SourcePoint is the existing externally pinned human anchor. Projection is an immutable constituted Holo core, not an enrolled principal. The enrolled carrier signs node transport; the receiving Host signs independently attributable admission and transition history. Model is a declared expression-source reference; Expression is an existing non-authoritative signed candidate. Neither acquires authority from attribution. Exobody composition is an explicit nullable reference, not implied by Holo or Host.

A core records projection/source/constitution/lineage IDs, class/purpose/carrier, dependencies/conditions, Return obligations, creation/expiry, renewal conditions and predecessor/Exobody references. Source ≠ Projection ≠ Host ≠ Model ≠ Expression. Identity and capability do not supply delegation or admission. A separately recorded root command affiliates one existing exact grant with one Projection. Canonical grant subjects retain enrolled carrier semantics. The receiving runtime checks exact affiliation, subject, action, payload, scope, purpose, host, dependencies, time and revocation at admission and effect release.

## Commands and lifecycle

Every human command uses existing canonical JSON/Ed25519 `{body, signature}` with field ID, fresh record ID/time, root issuer and Projection ID. Supported body types are `projection_constitute`, `projection_delegate`, `projection_bind`, `projection_suspend`, `projection_rebind`, `projection_return`, `projection_expire`, `projection_renew`, and `projection_carry`. An actual signed passage sent to `/projection` follows existing RIO and Sentinel; it is not a human lifecycle command.

`UNCONSTITUTED → CONSTITUTED → DELEGATED → BOUND → OPERATING → RETURNING → RETURNED` is reconstructed from append-only attributed events. SUSPENDED, REBINDING and EXPIRED are separate transitions; expiry/revocation/dependency drift also affect current effective standing without overwriting historical lifecycle. Fresh delegation clears prior binding and requires fresh admission. Returned/expired history never becomes operative by an ordinary status edit. `projection_renew` creates a distinct successor constitution/ID and predecessor linkage; it requires terminal prior standing and no unacknowledged native Return. The successor needs a new grant and independently recorded binding.

Admitted operations also remain explicit `open_passages` obligations before native Return exists. Suspension, expiry and carriage cannot erase them. Redelegation, fresh binding and renewal require no open operation or unresolved account. Carriage retains inherited obligations without importing standing. Acknowledgement is correlated per account; `RETURN_ACKNOWLEDGED` retains residual obligations and `RETURNED` closes the final account. A real pre-effect HOLD has `receipt_id: null`, accepted in the signed acknowledgement and history schema without manufacturing a receipt.

## Host boundary

Binding is separate from host judgment and Projection identity. A receiving host records ADMITTED or DENIED with its own signature, then creates a distinct binding only for admission. Binding references exact Projection, host, delegation, grant, host-admission record, conditions and dependencies. Carriage imports an original root-signed constitution and ordered signed history as lineage only. It installs no operative grant, delegation or binding. Host A admission never authorizes Host B. A root-requested fresh local grant/affiliation and receiving-host judgment are required at Host B. Denial preserves core/history.

This bounded profile verifies presented history against locally enrolled signer keys. It does not establish federation-wide synchronized revocation, latest-head consensus or protection against an authorized root deliberately carrying an older snapshot. Production transport and revocation distribution require separately governed deployment.

## Passage, receipt and Return

The existing signed Local Field passage has `projection: {projection_id, delegation_ref, binding_ref, expression_ref, model_ref: {model_id, runtime_node}}`. The full canonical passage hash/signature binds these fields. Projection-enabled constituted field definitions require the extension for their accepted consequential path, including generic admission/execution routes. Model output remains a candidate and cannot bypass control by choosing an endpoint.

RIO decision, Sentinel result, execution attempt, observed occurrence, receipt and Return remain the native distinct artifacts. Projection accounts reference their actual IDs and retain the signed native Return; a root acknowledgement closes the episode. Receipt cannot alter an earlier authorization. Renewal and Return do not prove intended-world success. Existing `rio-receipt-protocol` verifies the fully bound signed passage and observation/receipt/Return without a new receipt schema.

## Views and verification

Root-signed query `view: projection` selects `projection_id`; default field status exposes projection topology alongside existing decisions/fidelity/occurrences/receipts/revocations/Return. Views are reconstructions with `authority_effect: NONE` and `visibility_effect: NONE`. Viewing or editing a client copy confers no standing.

JSON Schema is structural validation, not an authority mechanism. The runtime verifies signatures, exact current standing and real effects. `tests/local_field/validate_projection_runtime.py` consumes the real two-process Customer Zero export and checks actual portable objects, history order, successor linkage and malformed promotion rejection. Root lifecycle commands and receiving-boundary tests live with the runtime.

Architecture/Loom owner: `one-rio-muss-architecture/docs/architecture/projection-runtime/`, existing whole-system #322 / R-07 GAP. Runtime depends on the existing Open Arrow review stack and pinned private compiler owner for Customer Zero; no software successor installation is implied.
