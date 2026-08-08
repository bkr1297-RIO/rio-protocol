import { generateKeyPairSync } from 'node:crypto';
import type { MusReceiptPayload, MusSignedReceipt, PrimePacket, PrimeValidationResult } from './types';
import { canonicalize } from './canonical-json';
import { primePacketHash, sha256Canonical, signCanonicalPayload, verifyCanonicalPayload } from './crypto';

export function generateMusKeyPair(): { publicKeyPem: string; privateKeyPem: string } {
  const { publicKey, privateKey } = generateKeyPairSync('ed25519');
  return {
    publicKeyPem: publicKey.export({ type: 'spki', format: 'pem' }).toString(),
    privateKeyPem: privateKey.export({ type: 'pkcs8', format: 'pem' }).toString()
  };
}

export function createMusReceipt(
  packet: PrimePacket,
  result: PrimeValidationResult,
  musPrivateKeyPem: string,
  musPublicKeyPem: string,
  previousReceiptHash: string | null = null,
  now: Date = new Date()
): MusSignedReceipt {
  const payload: MusReceiptPayload = {
    receipt_version: '0.2',
    receipt_id: `mus:${packet.packet_id}:${result.decision}`,
    packet_id: packet.packet_id,
    packet_hash: primePacketHash(packet),
    result_hash: sha256Canonical({
      decision: result.decision,
      reasons: result.reasons,
      failed_checks: result.failed_checks,
      receipt_class: result.receipt_class
    }),
    decision: result.decision,
    receipt_class: result.receipt_class,
    reasons: result.reasons,
    failed_checks: result.failed_checks,
    return_to: packet.return_path.return_to,
    previous_receipt_hash: previousReceiptHash,
    timestamp: now.toISOString()
  };

  const receipt_hash = sha256Canonical(payload);
  const mus_signature = signCanonicalPayload({ payload, receipt_hash }, musPrivateKeyPem);
  return { payload, receipt_hash, mus_public_key_pem: musPublicKeyPem, mus_signature };
}

export function verifyMusReceipt(receipt: MusSignedReceipt): boolean {
  if (receipt.receipt_hash !== sha256Canonical(receipt.payload)) return false;
  return verifyCanonicalPayload({ payload: receipt.payload, receipt_hash: receipt.receipt_hash }, receipt.mus_signature, receipt.mus_public_key_pem);
}

export function verifyMusReceiptChain(receipts: MusSignedReceipt[]): boolean {
  for (let index = 0; index < receipts.length; index += 1) {
    if (!verifyMusReceipt(receipts[index])) return false;
    const expectedPrevious = index === 0 ? null : receipts[index - 1].receipt_hash;
    if (receipts[index].payload.previous_receipt_hash !== expectedPrevious) return false;
  }
  return true;
}

export function receiptCanonicalPayload(receipt: MusSignedReceipt): string {
  return canonicalize(receipt);
}
