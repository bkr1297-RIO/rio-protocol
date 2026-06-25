import type { DeonticOperator, PrimeCondition, PrimePacket } from './types';
import { sha256Canonical } from './crypto';

export const GRANT_ALLOWED_ACTIONS: Record<string, string[]> = {
  draft_only: ['llm.draft', 'llm.refine', 'sanitizer.remove_script_tags'],
  read_and_sanitize: ['sanitizer.remove_script_tags'],
  send_email_once: ['smtp.send_draft'],
  log_only: ['mus.log_receipt'],
  learn_with_ratification: ['memory.propose_update']
};

export function isGrantCompatible(grantClass: string, action: string): boolean {
  return GRANT_ALLOWED_ACTIONS[grantClass]?.includes(action) ?? false;
}

export function isProhibitiveOperator(operator: DeonticOperator): boolean {
  return operator === 'MUST_NOT' || operator === 'MAY_NOT' || operator === 'SHALL_NOT';
}

export function isNonExecutableOperator(operator: DeonticOperator): boolean {
  return ['SHOULD', 'SHOULD_NOT', 'CAN', 'CANNOT', 'WILL', 'WILL_NOT', 'SHALL'].includes(operator);
}

export function operatorCanAuthorizeExternalEffect(operator: DeonticOperator): boolean {
  return operator === 'MAY' || operator === 'MAY_ONLY_IF' || operator === 'MUST';
}

export function effectPayloadHash(packet: PrimePacket): string {
  return sha256Canonical({ action: packet.effect.action, target: packet.effect.target });
}

export function conditionSatisfied(packet: PrimePacket, condition?: PrimeCondition): boolean {
  if (!condition) return packet.operator.modal !== 'MAY_ONLY_IF';
  switch (condition.type) {
    case 'ALWAYS_TRUE':
      return true;
    case 'AUTHORITY_GRANT_MATCHES_EFFECT':
      return isGrantCompatible(packet.authority.grant_class, packet.effect.action);
    case 'EXTERNAL_EFFECT_FALSE':
      return packet.scope.external_effect === false;
    case 'SENTINEL_PAYLOAD_HASH_MATCH':
      return packet.scope.payload_hash === effectPayloadHash(packet);
    default:
      return false;
  }
}
