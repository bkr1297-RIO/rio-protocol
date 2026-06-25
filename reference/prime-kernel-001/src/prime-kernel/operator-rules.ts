import type {
  DeonticOperator,
  OperatorForce,
  PrimeCondition,
  PrimePacket
} from "./types";

export const OPERATOR_FORCE: Record<DeonticOperator, OperatorForce> = {
  MUST: "obligation",
  MUST_NOT: "prohibition",
  SHALL: "intention",
  SHALL_NOT: "prohibition",
  MAY: "permission",
  MAY_NOT: "prohibition",
  MAY_ONLY_IF: "conditional_permission",
  SHOULD: "recommendation",
  SHOULD_NOT: "recommendation",
  WILL: "intention",
  WILL_NOT: "intention",
  CAN: "capability",
  CANNOT: "capability"
};

export const GRANT_ALLOWED_ACTIONS: Record<string, string[]> = {
  draft_only: ["llm.draft", "llm.refine", "sanitizer.remove_script_tags"],
  read_and_sanitize: ["sanitizer.remove_script_tags"],
  send_email_once: ["smtp.send_draft"],
  log_only: ["mus.log_receipt"],
  learn_with_ratification: ["memory.propose_update"]
};

export function isGrantCompatible(grantClass: string, action: string): boolean {
  return GRANT_ALLOWED_ACTIONS[grantClass]?.includes(action) ?? false;
}

export function operatorCanAuthorizeExternalEffect(operator: DeonticOperator): boolean {
  return operator === "MAY" || operator === "MAY_ONLY_IF" || operator === "MUST";
}

export function isProhibitiveOperator(operator: DeonticOperator): boolean {
  return operator === "MUST_NOT" || operator === "MAY_NOT" || operator === "SHALL_NOT";
}

export function isNonExecutableOperator(operator: DeonticOperator): boolean {
  return (
    operator === "SHOULD" ||
    operator === "SHOULD_NOT" ||
    operator === "CAN" ||
    operator === "CANNOT" ||
    operator === "WILL" ||
    operator === "WILL_NOT" ||
    operator === "SHALL"
  );
}

export function conditionSatisfied(packet: PrimePacket, condition?: PrimeCondition): boolean {
  if (!condition) return packet.operator.modal !== "MAY_ONLY_IF";

  switch (condition.type) {
    case "ALWAYS_TRUE":
      return true;
    case "AUTHORITY_GRANT_MATCHES_EFFECT":
      return isGrantCompatible(packet.authority.grant_class, packet.effect.action);
    case "EXTERNAL_EFFECT_FALSE":
      return packet.scope.external_effect === false;
    case "SENTINEL_PAYLOAD_HASH_MATCH":
      return packet.scope.payload_hash === mockComputePayloadHash(packet.effect.action, packet.effect.target);
    default:
      return false;
  }
}

export function mockComputePayloadHash(action: string, target: string): string {
  if (action === "smtp.send_draft" && target === "client@example.com") {
    return "sha256:4a8b92ef";
  }
  if (action === "sanitizer.remove_script_tags" && target === "memory_buffer:inbound") {
    return "sha256:sanitized_inbound";
  }
  if (action === "llm.draft" && target === "draft_buffer") {
    return "sha256:draft_buffer";
  }
  return "sha256:drift_detected";
}
