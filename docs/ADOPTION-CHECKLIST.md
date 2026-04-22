# Adoption Checklist — RIO Protocol v1.0

This checklist describes the minimum steps to implement a RIO-compliant governed execution path. Each step references the specification and schema files in this repository.

---

## Step 1: Adapter

Connect your system's action requests to the RIO intake stage.

- Accept an action request from your application
- Construct a canonical request per `schemas/canonical_request.json`
- Compute `request_hash` as SHA-256 of the canonical JSON (sorted keys, no whitespace)
- Pass the canonical request to the risk evaluation stage

**Reference:** `spec/01_intake.md`, `spec/02_canonical_intent.md`

---

## Step 2: Intent Binding

Bind the action to a structured, hashable intent.

- The canonical request must include: agent identity, action description, and context
- The `request_hash` locks the intent — any modification after this point invalidates the hash
- Store the canonical request for later verification

**Reference:** `spec/receipt_protocol.md` (Section: Signed Fields)

---

## Step 3: Authorization

Enforce approval before execution.

- Evaluate risk per your policy engine
- For high-risk actions: require explicit human approval before issuing an execution token
- For low-risk actions: automatic approval is permitted if policy allows
- Record the authorization decision (approve or deny)
- Issue a time-limited, single-use execution token bound to the specific intent

**Reference:** `spec/05_authorization.md`, `spec/06_authorization.md`

---

## Step 4: Execution via Gate

Execute the action only through a controlled gate.

- The execution gate must validate the token before allowing any action
- Token validation: verify signature, check TTL, confirm nonce is unused, confirm intent binding
- If validation fails: reject execution (fail-closed)
- If validation succeeds: execute the action, then burn the token (mark nonce as used)
- No action may execute without passing through the gate

**Reference:** `spec/RIO_Protocol_Specification_v1.0.md` (Section 5: Execution Gate)

---

## Step 5: Receipt Generation

Produce a verifiable receipt for every governed action.

- Generate a receipt with all 22 fields per `spec/receipt_schema.json`
- Required fields include: `receipt_id`, `request_hash`, `decision`, `model_output_hash`, `prev_ledger_hash`, `receipt_hash`, `signature`
- Compute `receipt_hash` as SHA-256 of the canonical JSON of the 19 signed fields (exclude `receipt_hash`, `signature`, `signature_algorithm`)
- Sign the canonical JSON of the signed fields with Ed25519
- Record the receipt in the hash-chained ledger

**Reference:** `spec/receipt_protocol.md`, `spec/receipt_schema.json`

---

## Step 6: Ledger Recording

Append the receipt to the hash-chained ledger.

- Compute the ledger entry hash: `SHA-256(prev_ledger_hash + receipt_hash)`
- For the first entry, `prev_ledger_hash` is `SHA-256("GENESIS")` = `901131d838b17aac0f7885b81e03cbdc9f5157a00343d30ab22083685ed1416a`
- The ledger is append-only — no entry may be modified or deleted after recording

**Reference:** `spec/audit_ledger_protocol.md`, `spec/ledger_immutability_model.md`

---

## Step 7: Verification

Confirm the receipt and ledger are independently verifiable.

- Recompute `receipt_hash` from the signed fields and compare
- Verify the Ed25519 signature against the public key
- Recompute the ledger hash chain from genesis and confirm no breaks
- Verify that `request_hash` in the receipt matches the original canonical request

**Reference:** `VERIFY_THIS_SYSTEM.md`, `tests/vectors/`

---

## Conformance

After completing all steps, assess your implementation against the 7 conformance levels in `spec/RIO_CONFORMANCE_v2.3.0.md`. At minimum, a compliant implementation must:

- Enforce authorization before execution
- Bind actions to exact intent
- Produce verifiable receipts
