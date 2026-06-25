import {
  evaluatePrimePacket,
  generatePrimeReceipt,
  ORGALoop,
  PrimePacket
} from "../src/prime-kernel";

function assert(condition: unknown, message: string): void {
  if (!condition) throw new Error(message);
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

const valid: PrimePacket = {
  prime_version: "0.1",
  packet_id: "990abcde-1234-4567-89ab-cdef01234567",
  parent_packet_hash: "sha256:parent-valid",
  sourcepoint: "human:brian",
  transition: {
    type: "STATE_MUTATION",
    from_state: "draft_approved",
    to_state: "email_sent"
  },
  operator: {
    modal: "MAY_ONLY_IF",
    subject: "smtp.send_draft",
    condition: { type: "SENTINEL_PAYLOAD_HASH_MATCH" }
  },
  authority: {
    envelope_id: "env-990-xyz",
    grant_class: "send_email_once",
    sourcepoint_signature: "sig:ed25519:BrianRoot:0x892afbc01289",
    expires: 4102444800
  },
  scope: {
    allowed_inputs: ["id:1029", "recipient:client@example.com"],
    allowed_tools: ["smtp.send_draft"],
    disallowed_effects: ["filesystem.write", "api.call_untrusted"],
    payload_hash: "sha256:4a8b92ef",
    external_effect: true
  },
  gates: {
    hermeneutic: "required",
    sophie: "required",
    rio: "required",
    sentinel: "exact_payload_match"
  },
  effect: {
    action: "smtp.send_draft",
    target: "client@example.com"
  },
  receipt: {
    required: true,
    class: "StandardOutcome",
    return_to: "SourcePoint"
  },
  return_path: {
    return_to: "SourcePoint",
    human_review_required: false
  },
  failure: {
    default_policy: "BLOCK_AND_RETURN",
    allowed_recovery: ["quarantine_and_review"]
  },
  learning: {
    may_update: false,
    requires_ratification: true
  }
};

function run(name: string, fn: () => void): void {
  try {
    fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    throw error;
  }
}

run("valid draft_approved -> email_sent allows", () => {
  const result = evaluatePrimePacket(valid);
  assert(result.decision === "ALLOW", `expected ALLOW, got ${result.decision}: ${result.failed_checks.join(",")}`);
});

run("raw_language -> email_sent blocks", () => {
  const packet = clone(valid);
  packet.transition.from_state = "raw_language";
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C3_ILLEGAL_STATE_TRANSITION"), "missing illegal transition check");
});

run("draft_only + smtp.send_draft blocks", () => {
  const packet = clone(valid);
  packet.authority.grant_class = "draft_only";
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C5_GRANT_ACTION_MISMATCH"), "missing grant mismatch check");
});

run("expired authority blocks", () => {
  const packet = clone(valid);
  packet.authority.expires = 1;
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C2_AUTHORITY_EXPIRED"), "missing expired authority check");
});

run("sentinel hash mismatch block_and_returns", () => {
  const packet = clone(valid);
  packet.scope.payload_hash = "sha256:modified_999";
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.receipt_class === "DriftBreach", `expected DriftBreach, got ${result.receipt_class}`);
});

run("CAN operator never becomes external permission", () => {
  const packet = clone(valid);
  packet.operator.modal = "CAN";
  packet.operator.condition = undefined;
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C5_OPERATOR_NOT_EXECUTABLE"), "missing operator not executable check");
});

run("SHOULD operator never becomes external command", () => {
  const packet = clone(valid);
  packet.operator.modal = "SHOULD";
  packet.operator.condition = undefined;
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C5_OPERATOR_NOT_EXECUTABLE"), "missing SHOULD non-executable check");
});

run("missing return_path fails", () => {
  const packet = clone(valid) as unknown as Record<string, unknown>;
  delete packet.return_path;
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C9_RETURN_PATH_MISSING"), "missing return path check");
});

run("learning update without LEARN packet fails", () => {
  const packet = clone(valid);
  packet.learning.may_update = true;
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C11_LEARNING_UPDATE_WITHOUT_LEARN_PACKET"), "missing learning violation check");
});

run("bypassed gate string fails when injected", () => {
  const packet = clone(valid) as unknown as Record<string, any>;
  packet.gates.rio = "bypassed";
  const result = evaluatePrimePacket(packet);
  assert(result.decision === "BLOCK_AND_RETURN", `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes("C6_GATE_POLICY_INVALID"), "missing invalid gate policy check");
});

run("ORGA loop allows only reason -> gate -> act path", () => {
  const loop = ORGALoop.initialize(valid);
  const result = loop.reason().gate().validate();
  assert(result.decision === "ALLOW", "ORGA gate validation should allow valid packet");
  loop.reason().gate().act().observe();
});

run("receipt generation returns proof object", () => {
  const result = evaluatePrimePacket(valid);
  const receipt = generatePrimeReceipt(valid, result);
  assert(receipt.packet_id === valid.packet_id, "receipt should bind to packet id");
  assert(receipt.decision === "ALLOW", "receipt should preserve decision");
});

console.log("All PRIME-KERNEL-001 tests passed.");
