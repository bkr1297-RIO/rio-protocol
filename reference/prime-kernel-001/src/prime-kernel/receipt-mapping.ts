import type { PrimePacket, PrimeReceipt, PrimeValidationResult } from "./types";

export function generatePrimeReceipt(packet: PrimePacket, result: PrimeValidationResult): PrimeReceipt {
  return {
    receipt_id: `receipt:${packet.packet_id}:${result.decision}`,
    packet_id: packet.packet_id,
    decision: result.decision,
    receipt_class: result.receipt_class,
    reasons: result.reasons,
    failed_checks: result.failed_checks,
    return_to: packet.return_path.return_to,
    timestamp: new Date().toISOString()
  };
}
