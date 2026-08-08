import type { GatePolicy, PrimeDecision, PrimePacket, PrimeValidationResult, ReceiptClass } from './types';
import { primePacketHash, verifyPrimePacketSignature } from './crypto';
import { isValidStateTransition } from './state-transition-matrix';
import {
  conditionSatisfied,
  effectPayloadHash,
  isGrantCompatible,
  isNonExecutableOperator,
  isProhibitiveOperator,
  operatorCanAuthorizeExternalEffect
} from './operator-rules';

const VALID_GATE_POLICIES: GatePolicy[] = [
  'required',
  'passed',
  'failed',
  'not_applicable',
  'pending',
  'exact_payload_match'
];

function hasText(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every(hasText);
}

function addFailure(reasons: string[], checks: string[], code: string, reason: string): void {
  checks.push(code);
  reasons.push(reason);
}

function decisionFromPolicy(policy?: string): PrimeDecision {
  return ['BLOCK', 'BLOCK_AND_RETURN', 'HOLD', 'QUARANTINE', 'REQUIRE_REVIEW', 'CLARIFY'].includes(policy ?? '')
    ? policy as PrimeDecision
    : 'BLOCK_AND_RETURN';
}

function receiptClassFor(checks: string[], packet?: Partial<PrimePacket>): ReceiptClass {
  if (checks.some((check) => check.includes('SIGNATURE'))) return 'SignatureViolation';
  if (checks.some((check) => check.includes('OPERATOR'))) return 'OperatorViolation';
  if (checks.some((check) => check.includes('SENTINEL'))) return 'DriftBreach';
  if (checks.some((check) => check.includes('RETURN'))) return 'MissingReturnPath';
  if (checks.some((check) => check.includes('LEARNING'))) return 'LearningViolation';
  return packet?.receipt?.class ?? 'PolicyViolation';
}

export function evaluatePrimePacket(input: unknown): PrimeValidationResult {
  const packet = input as Partial<PrimePacket>;
  const reasons: string[] = [];
  const failedChecks: string[] = [];

  if (!packet || typeof packet !== 'object') {
    return invalidResult({}, ['Input is not an object.'], ['C0_INPUT_NOT_OBJECT']);
  }

  if (packet.prime_version !== '0.2') {
    addFailure(reasons, failedChecks, 'C0_VERSION_INVALID', "prime_version must be '0.2'.");
  }
  if (!hasText(packet.packet_id)) {
    addFailure(reasons, failedChecks, 'C0_PACKET_ID_MISSING', 'packet_id is required.');
  }
  if (!hasText(packet.parent_packet_hash)) {
    addFailure(reasons, failedChecks, 'C0_PARENT_HASH_MISSING', 'parent_packet_hash is required.');
  }
  if (!hasText(packet.sourcepoint)) {
    addFailure(reasons, failedChecks, 'C1_SOURCEPOINT_MISSING', 'sourcepoint is required.');
  }

  if (!packet.authority) {
    addFailure(reasons, failedChecks, 'C1_AUTHORITY_MISSING', 'authority envelope is required.');
  } else {
    if (!hasText(packet.authority.envelope_id)) addFailure(reasons, failedChecks, 'C1_ENVELOPE_ID_MISSING', 'authority.envelope_id is required.');
    if (!hasText(packet.authority.grant_class)) addFailure(reasons, failedChecks, 'C1_GRANT_CLASS_MISSING', 'authority.grant_class is required.');
    if (!hasText(packet.authority.nonce)) addFailure(reasons, failedChecks, 'C1_NONCE_MISSING', 'authority.nonce is required.');
    if (!hasText(packet.authority.sourcepoint_public_key_pem)) addFailure(reasons, failedChecks, 'C1_PUBLIC_KEY_MISSING', 'sourcepoint_public_key_pem is required.');
    if (!hasText(packet.authority.sourcepoint_signature)) addFailure(reasons, failedChecks, 'C1_SIGNATURE_MISSING', 'sourcepoint_signature is required.');
    if (typeof packet.authority.expires !== 'number') {
      addFailure(reasons, failedChecks, 'C2_EXPIRES_INVALID', 'authority.expires must be a unix timestamp.');
    } else if (packet.authority.expires <= Math.floor(Date.now() / 1000)) {
      addFailure(reasons, failedChecks, 'C2_AUTHORITY_EXPIRED', 'authority envelope has expired.');
    }
  }

  if (packet.authority?.sourcepoint_public_key_pem && packet.authority.sourcepoint_signature) {
    if (!verifyPrimePacketSignature(packet as PrimePacket)) {
      addFailure(reasons, failedChecks, 'C1_SIGNATURE_INVALID', 'Ed25519 SourcePoint signature verification failed.');
    }
  }

  if (!packet.transition) {
    addFailure(reasons, failedChecks, 'C3_TRANSITION_MISSING', 'transition is required.');
  } else if (!isValidStateTransition(packet.transition.from_state, packet.transition.to_state)) {
    addFailure(reasons, failedChecks, 'C3_ILLEGAL_STATE_TRANSITION', `Illegal transition ${packet.transition.from_state} -> ${packet.transition.to_state}.`);
  }

  if (!packet.operator) {
    addFailure(reasons, failedChecks, 'C4_OPERATOR_MISSING', 'operator is required.');
  } else {
    if (isProhibitiveOperator(packet.operator.modal)) addFailure(reasons, failedChecks, 'C4_OPERATOR_PROHIBITION', `${packet.operator.modal} prohibits execution.`);
    if (packet.operator.modal === 'MAY_ONLY_IF' && !packet.operator.condition) addFailure(reasons, failedChecks, 'C4_CONDITION_REQUIRED', 'MAY_ONLY_IF requires condition.');
    if (!conditionSatisfied(packet as PrimePacket, packet.operator.condition)) addFailure(reasons, failedChecks, 'C4_CONDITION_FAILED', 'operator condition failed.');
  }

  if (!packet.scope) {
    addFailure(reasons, failedChecks, 'C5_SCOPE_MISSING', 'scope is required.');
  } else {
    if (!isStringArray(packet.scope.allowed_inputs)) addFailure(reasons, failedChecks, 'C5_ALLOWED_INPUTS_INVALID', 'allowed_inputs must be string[].');
    if (!isStringArray(packet.scope.allowed_tools)) addFailure(reasons, failedChecks, 'C5_ALLOWED_TOOLS_INVALID', 'allowed_tools must be string[].');
    if (!isStringArray(packet.scope.disallowed_effects)) addFailure(reasons, failedChecks, 'C5_DISALLOWED_EFFECTS_INVALID', 'disallowed_effects must be string[].');
  }

  if (!packet.effect || !hasText(packet.effect.action) || !hasText(packet.effect.target)) {
    addFailure(reasons, failedChecks, 'C5_EFFECT_INVALID', 'effect.action and effect.target are required.');
  } else if (packet.scope && packet.authority) {
    const allowedTools = Array.isArray(packet.scope.allowed_tools) ? packet.scope.allowed_tools : [];
    const disallowedEffects = Array.isArray(packet.scope.disallowed_effects) ? packet.scope.disallowed_effects : [];
    if (!allowedTools.includes(packet.effect.action)) addFailure(reasons, failedChecks, 'C5_TOOL_NOT_ALLOWED', 'effect action outside allowed_tools.');
    if (disallowedEffects.includes(packet.effect.action)) addFailure(reasons, failedChecks, 'C5_EFFECT_DISALLOWED', 'effect action explicitly disallowed.');
    if (!isGrantCompatible(packet.authority.grant_class, packet.effect.action)) addFailure(reasons, failedChecks, 'C5_GRANT_ACTION_MISMATCH', 'authority grant does not authorize effect action.');
    if (packet.scope.external_effect && packet.operator && isNonExecutableOperator(packet.operator.modal)) addFailure(reasons, failedChecks, 'C5_OPERATOR_NOT_EXECUTABLE', `${packet.operator.modal} cannot authorize external effect.`);
    if (packet.scope.external_effect && packet.operator && !operatorCanAuthorizeExternalEffect(packet.operator.modal)) addFailure(reasons, failedChecks, 'C5_OPERATOR_PERMISSION_MISSING', `${packet.operator.modal} lacks external-effect permission force.`);
  }

  if (!packet.gates) {
    addFailure(reasons, failedChecks, 'C6_GATES_MISSING', 'gates are required.');
  } else {
    for (const [name, value] of Object.entries(packet.gates)) {
      if (!VALID_GATE_POLICIES.includes(value as GatePolicy)) addFailure(reasons, failedChecks, 'C6_GATE_POLICY_INVALID', `${name} gate policy invalid.`);
      if (String(value) === 'bypassed') addFailure(reasons, failedChecks, 'C6_GATE_BYPASSED_FORBIDDEN', `${name} cannot be bypassed.`);
      if (value === 'failed') addFailure(reasons, failedChecks, 'C6_GATE_FAILED', `${name} failed.`);
    }
  }

  if (packet.gates?.sentinel === 'exact_payload_match' && packet.scope?.payload_hash && packet.effect) {
    if (packet.scope.payload_hash !== effectPayloadHash(packet as PrimePacket)) {
      addFailure(reasons, failedChecks, 'C7_SENTINEL_HASH_MISMATCH', 'Sentinel payload hash mismatch.');
    }
  }

  if (!packet.receipt || packet.receipt.required !== true) addFailure(reasons, failedChecks, 'C8_RECEIPT_REQUIRED', 'receipt.required must be true.');
  if (!packet.return_path || !hasText(packet.return_path.return_to)) addFailure(reasons, failedChecks, 'C9_RETURN_PATH_MISSING', 'return_path.return_to required.');
  if (!packet.failure || !isStringArray(packet.failure.allowed_recovery)) addFailure(reasons, failedChecks, 'C10_FAILURE_POLICY_INVALID', 'failure.allowed_recovery must be string[].');
  if (!packet.learning) addFailure(reasons, failedChecks, 'C11_LEARNING_MISSING', 'learning block is required.');
  else if (packet.learning.may_update && packet.transition?.type !== 'LEARN') addFailure(reasons, failedChecks, 'C11_LEARNING_UPDATE_WITHOUT_LEARN_PACKET', 'learning update requires LEARN packet.');

  if (failedChecks.length > 0) {
    return invalidResult(packet, reasons, failedChecks, receiptClassFor(failedChecks, packet));
  }

  return {
    decision: 'ALLOW',
    reasons: ['All Prime Kernel v0.2 crypto checks passed.'],
    failed_checks: [],
    receipt_required: true,
    receipt_class: packet.receipt?.class ?? 'StandardOutcome',
    return_required: true,
    allowed_recovery: packet.failure?.allowed_recovery,
    packet_hash: primePacketHash(packet as PrimePacket)
  };
}

function invalidResult(packet: Partial<PrimePacket>, reasons: string[], failedChecks: string[], receiptClass: ReceiptClass = 'PolicyViolation'): PrimeValidationResult {
  return {
    decision: decisionFromPolicy(packet.failure?.default_policy),
    reasons,
    failed_checks: failedChecks,
    receipt_required: packet.receipt?.required ?? true,
    receipt_class: receiptClass,
    return_required: true,
    allowed_recovery: packet.failure?.allowed_recovery ?? ['human_review']
  };
}
