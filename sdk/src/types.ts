import { PublicKey } from "@solana/web3.js";
import { BN } from "@coral-xyz/anchor";

export interface InsurancePool {
  authority: PublicKey;
  poolSeed: BN;
  totalPremiums: BN;
  totalRefunds: BN;
  activePolicies: number;
  baseRateBps: number;
  createdAt: BN;
  lastUpdated: BN;
  bump: number;
}

export interface Policy {
  owner: PublicKey;
  pool: PublicKey;
  premiumAmount: BN;
  txSignature: Uint8Array;
  status: number;
  createdAt: BN;
  expiresAt: BN;
  bump: number;
}

export interface RefundRecord {
  policy: PublicKey;
  recipient: PublicKey;
  amount: BN;
  refundedAt: BN;
  bump: number;
}

export interface DepositPremiumParams {
  poolAddress: PublicKey;
  amount: BN;
  txSignature: Uint8Array;
}

export interface ProcessRefundParams {
  poolAddress: PublicKey;
  policyAddress: PublicKey;
  txSignature: Uint8Array;
  claimant: PublicKey;
}

export interface HarnsConfig {
  rpcUrl: string;
  programId?: PublicKey;
  commitment?: string;
}

/** Represents the lifecycle state of an insurance policy. */
export enum PolicyStatus {
  Active = 0,
  Claimed = 1,
  Expired = 2,
}

export function isPolicyActive(status: number): boolean {
  return status === PolicyStatus.Active;
}
// ref: 0088
// ref: 0095
// ref: 0100
// ref: 0116
// ref: 0132
// ref: 0133
// ref: 0135
// ref: 0145
