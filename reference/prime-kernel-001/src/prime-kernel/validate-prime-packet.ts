import type {
  GatePolicy,
  PrimeDecision,
  PrimePacket,
  PrimeValidationResult,
  ReceiptClass
} from "./types";
import { isValidStateTransition } from "./state-transition-matrix";
import {
  conditionSatisfied,
  isGrantCompatible,
  isNonExecutableOperator,
  isProhibitiveOperator,
  mockComputePayloadHash,
  operatorCanAuthorizeExternalEffect
} from "./operator-rules";

const VALID_GATE_POLICIES: GatePolicy[] = [
  "required",
  "passed",
  "failed",
  "not_applicable",
  "pending",
  "exact_payload_match"
];

function hasText(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(hasText);
}

function verifyMockSignature(sourcepoint: string, signature: string, packetId: string): boolean {
  if (!hasText(packetId)) return false;
  return sourcepoint.startsWith("human:") && signature.startsWith("sig:ed25519:");
}

function hasValidUuidLikeId(value: string): boolean {
  return /^[0-9a-fA-F-]{8,}$/.test(value);
}

function addFailure(
  reasons: string[],
  failedChecks: string[],
  check: string,
  reason: string
): void {
  failedChecks.push(check);
  reasons.push(reason);
}

function normalizeFailureDecision(policy: string | undefined): PrimeDecision {
  switch (policy) {
    case "BLOCK":
      return "BLOCK";
    case "BLOCK_AND_RETURN":
      return "BLOCK_AND_RETURN";
    case "HOLD":
      return "HOLD";
    case "QUARANTINE":
      return "QUARANTINE";
    case "REQUIRE_REVIEW":
      return "REQUIRE_REVIEW";
    case "CLARIFY":
      return "CLARIFY";
    default:
      return "BLOCK_AND_RETURN";
  }
}

export function evaluatePrimePacket(input: unknown): PrimeValidationResult {
  const packet = input as Partial<PrimePacket>;
  const reasons: string[] = [];
  const failedChecks: string[] = [];

  if (!packet || typeof packet !== "object") {
    return invalidResult({}, ["Input is not an object."], ["C0_INPUT_NOT_OBJECT"]);
  }

  if (packet.prime_version !== "0.1") {
    addFailure(reasons, failedChecks, "C0_VERSION_INVALID", "prime_version must be '0.1'.");
  }

  if (!hasText(packet.packet_id) || !hasValidUuidLikeId(packet.packet_id)) {
    addFailure(reasons, failedChecks, "C0_PACKET_ID_INVALID", "packet_id is missing or malformed.");
  }

  if (!hasText(packet.parent_packet_hash)) {
    addFailure(reasons, failedChecks, "C0_PARENT_HASH_MISSING", "parent_packet_hash is required for append-only traceability.");
  }

  if (!hasText(packet.sourcepoint)) {
    addFailure(reasons, failedChecks, "C1_SOURCEPOINT_MISSING", "sourcepoint is required.");
  }

  if (!packet.authority) {
    addFailure(reasons, failedChecks, "C1_AUTHORITY_MISSING", "authority envelope is required.");
  } else {
    if (!hasText(packet.authority.envelope_id)) {
      addFailure(reasons, failedChecks, "C1_ENVELOPE_ID_MISSING", "authority.envelope_id is required.");
    }
    if (!hasText(packet.authority.grant_class)) {
      addFailure(reasons, failedChecks, "C1_GRANT_CLASS_MISSING", "authority.grant_class is required.");
    }
    if (!hasText(packet.authority.sourcepoint_signature)) {
      addFailure(reasons, failedChecks, "C1_SIGNATURE_MISSING", "authority.sourcepoint_signature is required.");
    } else if (
      hasText(packet.sourcepoint) &&
      hasText(packet.packet_id) &&
      !verifyMockSignature(packet.sourcepoint, packet.authority.sourcepoint_signature, packet.packet_id)
    ) {
      addFailure(reasons, failedChecks, "C1_SIGNATURE_INVALID", "mock SourcePoint signature verification failed.");
    }
    if (typeof packet.authority.expires !== "number") {
      addFailure(reasons, failedChecks, "C2_EXPIRES_MISSING", "authority.expires must be a unix timestamp.");
    } else if (packet.authority.expires <= Math.floor(Date.now() / 1000)) {
      addFailure(reasons, failedChecks, "C2_AUTHORITY_EXPIRED", "authority envelope has expired.");
    }
  }

  if (!packet.transition) {
    addFailure(reasons, failedChecks, "C3_TRANSITION_MISSING", "transition is required.");
  } else {
    if (!isValidStateTransition(packet.transition.from_state, packet.transition.to_state)) {
      addFailure(
        reasons,
        failedChecks,
        "C3_ILLEGAL_STATE_TRANSITION",
        `Illegal transition: ${packet.transition.from_state} -> ${packet.transition.to_state}.`
      );
    }
  }

  if (!packet.operator) {
    addFailure(reasons, failedChecks, "C4_OPERATOR_MISSING", "operator is required.");
  } else {
    if (!hasText(packet.operator.subject)) {
      addFailure(reasons, failedChecks, "C4_OPERATOR_SUBJECT_MISSING", "operator.subject is required.");
    }
    if (isProhibitiveOperator(packet.operator.modal)) {
      addFailure(reasons, failedChecks, "C4_OPERATOR_PROHIBITION", `${packet.operator.modal} prohibits execution.`);
    }
    if (packet.operator.modal === "MAY_ONLY_IF" && !packet.operator.condition) {
      addFailure(reasons, failedChecks, "C4_CONDITION_REQUIRED", "MAY_ONLY_IF requires a deterministic condition.");
    }
    if (!conditionSatisfied(packet as PrimePacket, packet.operator.condition)) {
      addFailure(reasons, failedChecks, "C4_CONDITION_FAILED", "operator.condition did not evaluate true.");
    }
  }

  if (!packet.scope) {
    addFailure(reasons, failedChecks, "C5_SCOPE_MISSING", "scope is required.");
  } else {
    if (!isStringArray(packet.scope.allowed_inputs)) {
      addFailure(reasons, failedChecks, "C5_ALLOWED_INPUTS_INVALID", "scope.allowed_inputs must be a string array.");
    }
    if (!isStringArray(packet.scope.allowed_tools)) {
      addFailure(reasons, failedChecks, "C5_ALLOWED_TOOLS_INVALID", "scope.allowed_tools must be a string array.");
    }
    if (!isStringArray(packet.scope.disallowed_effects)) {
      addFailure(reasons, failedChecks, "C5_DISALLOWED_EFFECTS_INVALID", "scope.disallowed_effects must be a string array.");
    }
  }

  if (!packet.effect || !hasText(packet.effect.action) || !hasText(packet.effect.target)) {
    addFailure(reasons, failedChecks, "C5_EFFECT_INVALID", "effect.action and effect.target are required.");
  } else if (packet.scope && packet.authority) {
    const allowedTools = Array.isArray(packet.scope.allowed_tools) ? packet.scope.allowed_tools : [];
    const disallowedEffects = Array.isArray(packet.scope.disallowed_effects) ? packet.scope.disallowed_effects : [];

    if (!allowedTools.includes(packet.effect.action)) {
      addFailure(reasons, failedChecks, "C5_TOOL_NOT_ALLOWED", `Action ${packet.effect.action} is not in allowed_tools.`);
    }
    if (disallowedEffects.includes(packet.effect.action)) {
      addFailure(reasons, failedChecks, "C5_EFFECT_DISALLOWED", `Action ${packet.effect.action} is explicitly disallowed.`);
    }
    if (!isGrantCompatible(packet.authority.grant_class, packet.effect.action)) {
      addFailure(
        reasons,
        failedChecks,
        "C5_GRANT_ACTION_MISMATCH",
        `Grant ${packet.authority.grant_class} does not authorize ${packet.effect.action}.`
      );
    }
    if (packet.scope.external_effect && packet.operator && isNonExecutableOperator(packet.operator.modal)) {
      addFailure(
        reasons,
        failedChecks,
        "C5_OPERATOR_NOT_EXECUTABLE",
        `${packet.operator.modal} cannot authorize external effect.`
      );
    }
    if (packet.scope.external_effect && packet.operator && !operatorCanAuthorizeExternalEffect(packet.operator.modal)) {
      addFailure(
        reasons,
        failedChecks,
        "C5_OPERATOR_PERMISSION_MISSING",
        `${packet.operator.modal} is not a valid execution permission for external effect.`
      );
    }
  }

  if (!packet.gates) {
    addFailure(reasons, failedChecks, "C6_GATES_MISSING", "gates are required.");
  } else {
    for (const [gateName, gateValue] of Object.entries(packet.gates)) {
      if (!VALID_GATE_POLICIES.includes(gateValue as GatePolicy)) {
        addFailure(reasons, failedChecks, "C6_GATE_POLICY_INVALID", `${gateName} has invalid gate policy ${String(gateValue)}.`);
      }
      if (gateValue === "failed") {
        addFailure(reasons, failedChecks, "C6_GATE_FAILED", `${gateName} gate is failed.`);
      }
      if (String(gateValue) === "bypassed") {
        addFailure(reasons, failedChecks, "C6_GATE_BYPASSED_FORBIDDEN", `${gateName} cannot be casually bypassed.`);
      }
    }

    if (packet.scope?.external_effect) {
      if (packet.gates.rio === "not_applicable") {
        addFailure(reasons, failedChecks, "C6_RIO_REQUIRED_FOR_EXTERNAL_EFFECT", "RIO is required for external effects.");
      }
      if (packet.gates.sentinel === "not_applicable") {
        addFailure(reasons, failedChecks, "C6_SENTINEL_REQUIRED_FOR_EXTERNAL_EFFECT", "Sentinel is required for external effects.");
      }
    }
  }

  let sentinelDrift = false;
  if (packet.gates?.sentinel === "exact_payload_match" && packet.scope?.payload_hash && packet.effect) {
    const computedPayloadHash = mockComputePayloadHash(packet.effect.action, packet.effect.target);
    if (computedPayloadHash !== packet.scope.payload_hash) {
      sentinelDrift = true;
      addFailure(reasons, failedChecks, "C7_SENTINEL_HASH_MISMATCH", "Sentinel payload hash mismatch.");
    }
  }

  if (!packet.receipt || packet.receipt.required !== true) {
    addFailure(reasons, failedChecks, "C8_RECEIPT_REQUIRED", "receipt.required must be true for Prime Kernel v0.1.");
  }

  if (!packet.return_path || !hasText(packet.return_path.return_to)) {
    addFailure(reasons, failedChecks, "C9_RETURN_PATH_MISSING", "return_path.return_to is required.");
  }

  if (!packet.failure) {
    addFailure(reasons, failedChecks, "C10_FAILURE_POLICY_MISSING", "failure policy is required.");
  } else if (!Array.isArray(packet.failure.allowed_recovery)) {
    addFailure(reasons, failedChecks, "C10_ALLOWED_RECOVERY_INVALID", "failure.allowed_recovery must be a string array.");
  }

  if (!packet.learning) {
    addFailure(reasons, failedChecks, "C11_LEARNING_MISSING", "learning block is required.");
  } else if (packet.learning.may_update && packet.transition?.type !== "LEARN") {
    addFailure(
      reasons,
      failedChecks,
      "C11_LEARNING_UPDATE_WITHOUT_LEARN_PACKET",
      "learning.may_update requires an explicit LEARN transition packet."
    );
  }

  if (failedChecks.length > 0) {
    return invalidResult(
      packet,
      reasons,
      failedChecks,
      sentinelDrift ? "DriftBreach" : chooseReceiptClass(packet, failedChecks),
      sentinelDrift ? "BLOCK_AND_RETURN" : undefined
    );
  }

  return {
    decision: "ALLOW",
    reasons: ["All Prime Kernel v0.1 checks passed."],
    failed_checks: [],
    receipt_required: packet.receipt?.required ?? true,
    receipt_class: packet.receipt?.class ?? "StandardOutcome",
    return_required: true,
    allowed_recovery: packet.failure?.allowed_recovery
  };
}

function chooseReceiptClass(packet: Partial<PrimePacket>, failedChecks: string[]): ReceiptClass {
  if (failedChecks.some((check) => check.includes("OPERATOR"))) return "OperatorViolation";
  if (failedChecks.some((check) => check.includes("RETURN_PATH"))) return "MissingReturnPath";
  if (failedChecks.some((check) => check.includes("LEARNING"))) return "LearningViolation";
  if (failedChecks.some((check) => check.includes("SENTINEL"))) return "DriftBreach";
  return packet.receipt?.class ?? "PolicyViolation";
}

function invalidResult(
  packet: Partial<PrimePacket>,
  reasons: string[],
  failedChecks: string[],
  receiptClass: ReceiptClass = "PolicyViolation",
  decision?: PrimeDecision
): PrimeValidationResult {
  return {
    decision: decision ?? normalizeFailureDecision(packet.failure?.default_policy),
    reasons,
    failed_checks: failedChecks,
    receipt_required: packet.receipt?.required ?? true,
    receipt_class: receiptClass,
    return_required: true,
    allowed_recovery: packet.failure?.allowed_recovery ?? ["human_review"]
  };
}
