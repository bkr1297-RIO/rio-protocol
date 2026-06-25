import type { StateType } from "./types";

export type TransitionKey = `${StateType}->${StateType}`;

export const STATE_TRANSITIONS: Record<StateType, StateType[]> = {
  raw_language: ["draft_unapproved", "quarantined"],
  draft_unapproved: ["draft_unapproved", "draft_approved", "quarantined"],
  draft_approved: ["email_sent", "quarantined"],
  email_sent: ["receipt_logged", "quarantined"],
  observing_tool_output: ["reasoning_state", "quarantined"],
  reasoning_state: ["draft_unapproved", "quarantined"],
  quarantined: ["receipt_logged"],
  receipt_logged: []
};

export function isValidStateTransition(from: StateType, to: StateType): boolean {
  return STATE_TRANSITIONS[from]?.includes(to) ?? false;
}

export type ValidTransitions =
  | { from: "raw_language"; to: "draft_unapproved" }
  | { from: "raw_language"; to: "quarantined" }
  | { from: "draft_unapproved"; to: "draft_unapproved" }
  | { from: "draft_unapproved"; to: "draft_approved" }
  | { from: "draft_unapproved"; to: "quarantined" }
  | { from: "draft_approved"; to: "email_sent" }
  | { from: "draft_approved"; to: "quarantined" }
  | { from: "email_sent"; to: "receipt_logged" }
  | { from: "email_sent"; to: "quarantined" }
  | { from: "observing_tool_output"; to: "reasoning_state" }
  | { from: "observing_tool_output"; to: "quarantined" }
  | { from: "reasoning_state"; to: "draft_unapproved" }
  | { from: "reasoning_state"; to: "quarantined" }
  | { from: "quarantined"; to: "receipt_logged" };

export type AssertTransition<F extends StateType, T extends StateType> =
  { from: F; to: T } extends ValidTransitions ? true : never;
