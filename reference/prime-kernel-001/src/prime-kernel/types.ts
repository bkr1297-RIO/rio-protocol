/**
 * PRIME-KERNEL-001 — Constitutional Crossing Language Kernel v0.1
 * Repo-safe candidate types.
 *
 * Boundary: this file defines structure. It does not authorize action.
 */

export type PrimeVersion = "0.1";

export type StateType =
  | "raw_language"
  | "draft_unapproved"
  | "draft_approved"
  | "email_sent"
  | "observing_tool_output"
  | "reasoning_state"
  | "quarantined"
  | "receipt_logged";

export type TransitionType =
  | "EPHEMERAL_READ"
  | "STATE_MUTATION"
  | "LEARN"
  | "LOG";

export type DeonticOperator =
  | "MUST"
  | "MUST_NOT"
  | "SHALL"
  | "SHALL_NOT"
  | "MAY"
  | "MAY_NOT"
  | "MAY_ONLY_IF"
  | "SHOULD"
  | "SHOULD_NOT"
  | "WILL"
  | "WILL_NOT"
  | "CAN"
  | "CANNOT";

export type OperatorForce =
  | "obligation"
  | "prohibition"
  | "permission"
  | "conditional_permission"
  | "recommendation"
  | "intention"
  | "capability";

export type PrimeCondition =
  | { type: "ALWAYS_TRUE" }
  | { type: "SENTINEL_PAYLOAD_HASH_MATCH" }
  | { type: "AUTHORITY_GRANT_MATCHES_EFFECT" }
  | { type: "EXTERNAL_EFFECT_FALSE" };

export type GatePolicy =
  | "required"
  | "passed"
  | "failed"
  | "not_applicable"
  | "pending"
  | "exact_payload_match";

export type FailurePolicy =
  | "BLOCK"
  | "BLOCK_AND_RETURN"
  | "HOLD"
  | "QUARANTINE"
  | "REQUIRE_REVIEW"
  | "CLARIFY";

export type ReceiptClass =
  | "StandardOutcome"
  | "ViolationAlert"
  | "DriftBreach"
  | "PolicyViolation"
  | "OperatorViolation"
  | "MissingReturnPath"
  | "LearningViolation";

export type PrimeDecision =
  | "ALLOW"
  | "BLOCK"
  | "BLOCK_AND_RETURN"
  | "HOLD"
  | "QUARANTINE"
  | "REQUIRE_REVIEW"
  | "CLARIFY";

export interface AuthorityEnvelope {
  envelope_id: string;
  grant_class: string;
  sourcepoint_signature: string;
  expires: number;
}

export interface PrimePacket {
  prime_version: PrimeVersion;
  packet_id: string;
  parent_packet_hash: string;
  sourcepoint: string;
  transition: {
    type: TransitionType;
    from_state: StateType;
    to_state: StateType;
  };
  operator: {
    modal: DeonticOperator;
    subject: string;
    condition?: PrimeCondition;
  };
  authority: AuthorityEnvelope;
  scope: {
    allowed_inputs: string[];
    allowed_tools: string[];
    disallowed_effects: string[];
    payload_hash?: string;
    external_effect: boolean;
  };
  gates: {
    hermeneutic: GatePolicy;
    sophie: GatePolicy;
    rio: GatePolicy;
    sentinel: GatePolicy;
  };
  effect: {
    action: string;
    target: string;
  };
  receipt: {
    required: boolean;
    class: ReceiptClass;
    return_to: string;
  };
  return_path: {
    return_to: string;
    human_review_required: boolean;
  };
  failure: {
    default_policy: FailurePolicy;
    allowed_recovery: string[];
  };
  learning: {
    may_update: boolean;
    requires_ratification: boolean;
  };
}

export interface PrimeValidationResult {
  decision: PrimeDecision;
  reasons: string[];
  failed_checks: string[];
  receipt_required: boolean;
  receipt_class: ReceiptClass;
  return_required: boolean;
  allowed_recovery?: string[];
}

export interface PrimeReceipt {
  receipt_id: string;
  packet_id: string;
  decision: PrimeDecision;
  receipt_class: ReceiptClass;
  reasons: string[];
  failed_checks: string[];
  return_to: string;
  timestamp: string;
}
