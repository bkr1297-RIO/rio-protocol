# RATIFICATION-CEREMONY-001

Status: Candidate v0.3. Not ratified. Not live law.
Authority: Brian / SourcePoint remains final authority for founding ratification.
Substrate: Git-canonical, Drive-working-copy.

## Purpose

Define how candidate protocol text becomes live protocol law. Conversation, model output, memory, Chronicle narrative, mutable Drive documents, branch names, tags, and claimed approval are not sufficient.

A live governance instrument requires an exact canonical artifact reference, a ratification register entry, dual hash anchoring, explicit infrastructure vector bounds, and no active revocation.

## Faculty system

Different models and substrates provide bounded functions:

- Gemini: structure and workspace context.
- Claude: procedural brake and ambiguity review.
- Grok: adversarial prototype pressure.
- Perplexity: public legibility and source boundary mapping.
- Bondi / Grammar Office: compiler, router, register separator, protocol fidelity witness.
- GitHub / rio-protocol: frozen canonical law surface.
- Drive: working-copy Chronicle and formation archive.
- Replit: downstream implementation chamber after protocol law exists.

Models bring signal back to the Grammar Office. The Grammar Office compiles.

## Infrastructure vector doctrine

The protocol does not replace existing tools. It binds them.

A ratification entry may authorize named infrastructure vectors, such as native OS hooks or third-party providers, but only inside the ratified scope. Naming a vector does not prove that vector is implemented, safe, deployed, or externally validated.

Native hooks and providers are capability surfaces, not authority.

Allowed vector examples:

- OS_REMINDERS
- LOCAL_CRON_SCHEDULER
- FILE_SYSTEM_WATCHER
- CLIPBOARD_AIR_GAP_BUFFER
- GITHUB_REPOSITORIES
- NOTION_WORKSPACE
- TWILIO_SIGNALING
- AZURE_RESOURCES
- RENDER_CONTAINERS

Unauthorized or unlisted infrastructure vectors fail closed.

## Explanation-of-Inference Layer

Dynamic protocol steps should return a structured explanation of why they routed, halted, accepted, rejected, or escalated. The system does not claim perfect truth. It leaves enough basis for correction.

Invariant:

- Explain the inference.
- Expose the assumption.
- Return the correction.

## Substrate rule

Drive is the working copy. Git is the canonical substrate. Registers identify what a runtime may treat as live. Receipts prove crossings.

## Two bindings

The typing discipline binds the human. The runtime cannot verify whether text was typed, pasted, or relayed.

The artifact binds the system. The runtime verifies register entry, repo/path/commit reference, content hash, tier, revocation status, infrastructure vector bounds, and scope.

## Held state

Before a ratification is accepted, the system enters `HELD_IN_SUPERPOSITION`: syntax checked, target repo/path/commit identified, target content hash computed, execution frozen, no merge or promotion occurred, waiting for a valid ratification or revocation check.

## Ratification entry

A valid ratification entry is data, not prose. It must include entry_id, entry_type, created_at, source_point_authority, target, tier_granted, ratified_scope, non_claims, ceremony_state, authorized_infrastructure_vectors, signature_block, and inference_basis.

## Dual-hash anchor

Every ratification entry binds to:

- target_commit_hash: 40-character Git commit SHA.
- content_hash: SHA-256 of the target file contents.

Both must match at load time.

## Revocation

Revocation uses the revocation register. A revocation entry defeats a ratification entry for the same target. Revocation is not harder than ratification.

## Gate read rule

At trigger time, a gate reads the ratification register, resolves repo/path/commit, recomputes target file content hash, checks revocation status, verifies tier, scope, and infrastructure vectors, and emits inference_basis. Any missing, unknown, stale, mismatched, unlisted, unauthorized, or revoked value halts.

The gate does not read Drive, Chronicle, model output, memory, or conversation to determine live law.

## Invalid references and vectors

Invalid ratification targets include `main`, `PENDING_MERGE`, branch names, mutable Drive-only references, Chronicle narrative, conversation text, nonexistent commits, and commit/path pairs with mismatched content hashes.

Invalid infrastructure references include any native hook or provider not enumerated in the schema or not authorized by the ratification entry.

## Founding clause

This ceremony cannot ratify itself before it exists. It is established by a one-time Founding Ratification referencing the first canonical commit containing this document. That event is marked `FOUNDING_RATIFICATION`. Every later instrument uses the door created by that founding act.

## Non-claims

This candidate document does not claim production readiness, external validation, legal certification, cryptographic signature enforcement, identity verification, runtime implementation, or that any current artifact is already live law.

## Keeper

The protocol uses tools that already exist, but only inside the membrane.

The typing binds the human. The artifact binds the system. The register is the only door. Revocation is never harder than ratification. The founding happens once. Capability may amplify. Authority may not transfer. Proof must return.
