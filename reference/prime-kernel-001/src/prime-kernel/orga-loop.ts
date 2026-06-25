import type { PrimePacket, PrimeValidationResult } from "./types";
import { evaluatePrimePacket } from "./validate-prime-packet";

export interface ObservePhase { readonly phase: "observe" }
export interface ReasonPhase { readonly phase: "reason" }
export interface GatePhase { readonly phase: "gate" }
export interface ActPhase { readonly phase: "act" }

/**
 * Compile-time ORGA loop scaffold.
 * The phantom __phase field makes the generic phase structurally relevant.
 */
export class ORGALoop<Phase> {
  private readonly __phase!: Phase;
  private constructor(private readonly packet: PrimePacket) {}

  static initialize(packet: PrimePacket): ORGALoop<ObservePhase> {
    return new ORGALoop<ObservePhase>(packet);
  }

  reason(this: ORGALoop<ObservePhase>): ORGALoop<ReasonPhase> {
    return new ORGALoop<ReasonPhase>(this.packet);
  }

  gate(this: ORGALoop<ReasonPhase>): ORGALoop<GatePhase> {
    return new ORGALoop<GatePhase>(this.packet);
  }

  act(this: ORGALoop<GatePhase>): ORGALoop<ActPhase> {
    const result = evaluatePrimePacket(this.packet);
    if (result.decision !== "ALLOW") {
      throw new Error(`Prime execution blocked: ${result.failed_checks.join(",")}`);
    }
    return new ORGALoop<ActPhase>(this.packet);
  }

  observe(this: ORGALoop<ActPhase>): ORGALoop<ObservePhase> {
    return new ORGALoop<ObservePhase>(this.packet);
  }

  validate(this: ORGALoop<GatePhase>): PrimeValidationResult {
    return evaluatePrimePacket(this.packet);
  }

  getRawPacket(): PrimePacket {
    return this.packet;
  }
}
