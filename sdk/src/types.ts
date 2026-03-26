import { PublicKey } from "@solana/web3.js";
import BN from "bn.js";

export interface ClusterNode {
  address: PublicKey;
  communityId: number;
  riskScore: number;
  connections: number;
}

export interface ClusterResult {
  nodes: ClusterNode[];
  modularity: number;
  communityCount: number;
  timestamp: number;
}

export interface ZkProof {
  hash: Uint8Array;
  rounds: number;
  commitment: Uint8Array;
}

export interface FlagEvent {
  target: PublicKey;
  flagger: PublicKey;
  riskScore: BN;
  timestamp: BN;
  signature: string;
}

export interface BurnEvent {
  target: PublicKey;
  authority: PublicKey;
  timestamp: BN;
  signature: string;
}

export interface ProtocolStats {
  totalFlags: BN;
  totalBurns: BN;
  activeFlags: BN;
  authority: PublicKey;
}

export enum RiskLevel {
  Low = "LOW",
  Medium = "MEDIUM",
  High = "HIGH",
  Critical = "CRITICAL",
}

export function getRiskLevel(score: number): RiskLevel {
  if (score < 2500) return RiskLevel.Low;
  if (score < 5000) return RiskLevel.Medium;
  if (score < 7500) return RiskLevel.High;
  return RiskLevel.Critical;
}

export function isValidProgramId(id: string): boolean {
  try {
    const pk = new PublicKey(id);
    return PublicKey.isOnCurve(pk.toBytes());
  } catch {
    return false;
  }
}

// 65ded535
