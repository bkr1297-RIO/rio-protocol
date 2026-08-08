import { createHash, sign, verify } from 'node:crypto';
import type { PrimePacket } from './types';
import { canonicalize } from './canonical-json';

export function sha256Canonical(value: unknown): string {
  return `sha256:${createHash('sha256').update(canonicalize(value)).digest('hex')}`;
}

export function toBase64Url(buffer: any): string {
  return buffer.toString('base64url');
}

export function fromBase64Url(value: string): any {
  return Buffer.from(value, 'base64url');
}

export function primePacketSigningPayload(packet: PrimePacket): unknown {
  const copy: PrimePacket = JSON.parse(JSON.stringify(packet));
  copy.authority.sourcepoint_signature = '';
  return copy;
}

export function primePacketHash(packet: PrimePacket): string {
  return sha256Canonical(primePacketSigningPayload(packet));
}

export function signCanonicalPayload(payload: unknown, privateKeyPem: string): string {
  return toBase64Url(sign(null, Buffer.from(canonicalize(payload)), privateKeyPem));
}

export function verifyCanonicalPayload(payload: unknown, signatureBase64Url: string, publicKeyPem: string): boolean {
  try {
    return verify(null, Buffer.from(canonicalize(payload)), publicKeyPem, fromBase64Url(signatureBase64Url));
  } catch {
    return false;
  }
}

export function signPrimePacket(packet: PrimePacket, privateKeyPem: string): PrimePacket {
  const signed: PrimePacket = JSON.parse(JSON.stringify(packet));
  signed.authority.sourcepoint_signature = signCanonicalPayload(primePacketSigningPayload(signed), privateKeyPem);
  return signed;
}

export function verifyPrimePacketSignature(packet: PrimePacket): boolean {
  if (!packet.authority.sourcepoint_public_key_pem || !packet.authority.sourcepoint_signature) return false;
  return verifyCanonicalPayload(
    primePacketSigningPayload(packet),
    packet.authority.sourcepoint_signature,
    packet.authority.sourcepoint_public_key_pem
  );
}
