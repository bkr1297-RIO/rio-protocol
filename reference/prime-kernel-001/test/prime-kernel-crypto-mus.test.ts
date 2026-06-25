import { generateKeyPairSync } from 'node:crypto';
import {
  createMusReceipt,
  effectPayloadHash,
  evaluatePrimePacket,
  generateMusKeyPair,
  ORGALoop,
  PrimePacket,
  signPrimePacket,
  verifyMusReceipt,
  verifyMusReceiptChain,
  verifyPrimePacketSignature
} from '../src/prime-kernel';

function assert(condition: unknown, message: string): void {
  if (!condition) throw new Error(message);
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function run(name: string, fn: () => void): void {
  try {
    fn();
    console.log(`PASS ${name}`);
  } catch (error) {
    console.error(`FAIL ${name}`);
    throw error;
  }
}

function sourcePointKeys(): { publicKeyPem: string; privateKeyPem: string } {
  const { publicKey, privateKey } = generateKeyPairSync('ed25519');
  return {
    publicKeyPem: publicKey.export({ type: 'spki', format: 'pem' }).toString(),
    privateKeyPem: privateKey.export({ type: 'pkcs8', format: 'pem' }).toString()
  };
}

const keys = sourcePointKeys();

const unsignedPacket: PrimePacket = {
  prime_version: '0.2',
  packet_id: '990abcde-1234-4567-89ab-cdef01234567',
  parent_packet_hash: 'sha256:parent-valid',
  sourcepoint: 'human:brian',
  transition: { type: 'STATE_MUTATION', from_state: 'draft_approved', to_state: 'email_sent' },
  operator: { modal: 'MAY_ONLY_IF', subject: 'smtp.send_draft', condition: { type: 'SENTINEL_PAYLOAD_HASH_MATCH' } },
  authority: {
    envelope_id: 'env-990-xyz',
    grant_class: 'send_email_once',
    sourcepoint_public_key_pem: keys.publicKeyPem,
    sourcepoint_signature: '',
    expires: 4102444800,
    nonce: 'nonce-001'
  },
  scope: {
    allowed_inputs: ['id:1029', 'recipient:client@example.com'],
    allowed_tools: ['smtp.send_draft'],
    disallowed_effects: ['filesystem.write', 'api.call_untrusted'],
    payload_hash: '',
    external_effect: true
  },
  gates: {
    hermeneutic: 'required',
    sophie: 'required',
    rio: 'required',
    sentinel: 'exact_payload_match'
  },
  effect: { action: 'smtp.send_draft', target: 'client@example.com' },
  receipt: { required: true, class: 'StandardOutcome', return_to: 'SourcePoint' },
  return_path: { return_to: 'SourcePoint', human_review_required: false },
  failure: { default_policy: 'BLOCK_AND_RETURN', allowed_recovery: ['quarantine_and_review'] },
  learning: { may_update: false, requires_ratification: true }
};
unsignedPacket.scope.payload_hash = effectPayloadHash(unsignedPacket);
const validPacket = signPrimePacket(unsignedPacket, keys.privateKeyPem);

run('real SourcePoint signature verifies', () => {
  assert(verifyPrimePacketSignature(validPacket), 'valid signed packet should verify');
});

run('valid packet ALLOWs', () => {
  const result = evaluatePrimePacket(validPacket);
  assert(result.decision === 'ALLOW', `expected ALLOW, got ${result.decision}: ${result.failed_checks.join(',')}`);
  assert(result.packet_hash?.startsWith('sha256:'), 'packet hash should be present');
});

run('tampering after signing fails', () => {
  const packet = clone(validPacket);
  packet.effect.target = 'attacker@example.test';
  const result = evaluatePrimePacket(packet);
  assert(result.decision === 'BLOCK_AND_RETURN', `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes('C1_SIGNATURE_INVALID'), 'missing signature invalid check');
});

run('invalid signature blocks', () => {
  const packet = clone(validPacket);
  packet.authority.sourcepoint_signature = 'not-valid-base64url';
  const result = evaluatePrimePacket(packet);
  assert(result.decision === 'BLOCK_AND_RETURN', `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.receipt_class === 'SignatureViolation', `expected SignatureViolation, got ${result.receipt_class}`);
});

run('draft_only cannot send externally', () => {
  const packet = clone(unsignedPacket);
  packet.authority.grant_class = 'draft_only';
  const signed = signPrimePacket(packet, keys.privateKeyPem);
  const result = evaluatePrimePacket(signed);
  assert(result.decision === 'BLOCK_AND_RETURN', `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes('C5_GRANT_ACTION_MISMATCH'), 'missing grant mismatch');
});

run('CAN cannot become permission', () => {
  const packet = clone(unsignedPacket);
  packet.operator = { modal: 'CAN', subject: 'smtp.send_draft' };
  const signed = signPrimePacket(packet, keys.privateKeyPem);
  const result = evaluatePrimePacket(signed);
  assert(result.decision === 'BLOCK_AND_RETURN', `expected BLOCK_AND_RETURN, got ${result.decision}`);
  assert(result.failed_checks.includes('C5_OPERATOR_NOT_EXECUTABLE'), 'missing non-executable operator check');
});

run('MUS receipt signs and verifies', () => {
  const result = evaluatePrimePacket(validPacket);
  const musKeys = generateMusKeyPair();
  const receipt = createMusReceipt(validPacket, result, musKeys.privateKeyPem, musKeys.publicKeyPem);
  assert(verifyMusReceipt(receipt), 'MUS receipt should verify');
});

run('MUS receipt tamper fails', () => {
  const result = evaluatePrimePacket(validPacket);
  const musKeys = generateMusKeyPair();
  const receipt = createMusReceipt(validPacket, result, musKeys.privateKeyPem, musKeys.publicKeyPem);
  receipt.payload.reasons.push('tamper');
  assert(!verifyMusReceipt(receipt), 'tampered MUS receipt should fail');
});

run('MUS receipt chain verifies previous hash linkage', () => {
  const musKeys = generateMusKeyPair();
  const result = evaluatePrimePacket(validPacket);
  const r1 = createMusReceipt(validPacket, result, musKeys.privateKeyPem, musKeys.publicKeyPem);
  const r2 = createMusReceipt(validPacket, result, musKeys.privateKeyPem, musKeys.publicKeyPem, r1.receipt_hash);
  assert(verifyMusReceiptChain([r1, r2]), 'MUS receipt chain should verify');
  r2.payload.previous_receipt_hash = 'sha256:bad-link';
  assert(!verifyMusReceiptChain([r1, r2]), 'broken MUS receipt chain should fail');
});

run('ORGA validates through gate before act', () => {
  const result = ORGALoop.initialize(validPacket).reason().gate().validate();
  assert(result.decision === 'ALLOW', 'ORGA gate should allow valid packet');
  ORGALoop.initialize(validPacket).reason().gate().act().observe();
});

console.log('All PRIME-KERNEL-001 real crypto + MUS tests passed.');
