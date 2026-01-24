import { Connection, PublicKey, Transaction, SystemProgram, Keypair } from "@solana/web3.js";
import { Program, AnchorProvider, BN, Idl } from "@coral-xyz/anchor";
import {
  HARNS_PROGRAM_ID,
  INSURANCE_POOL_SEED,
  POLICY_SEED,
  REFUND_SEED,
  MIN_PREMIUM_LAMPORTS,
} from "./constants";
import { InsurancePool, Policy, DepositPremiumParams, ProcessRefundParams, HarnsConfig } from "./types";

export class HarnsClient {
  private connection: Connection;
  private programId: PublicKey;

  constructor(config: HarnsConfig) {
    this.connection = new Connection(config.rpcUrl, "confirmed");
    this.programId = config.programId ?? new PublicKey(HARNS_PROGRAM_ID);
  }

  /**
   * Derive the insurance pool PDA address.
   */
  async findPoolAddress(authority: PublicKey, poolSeed: BN): Promise<[PublicKey, number]> {
    return PublicKey.findProgramAddressSync(
      [
        Buffer.from(INSURANCE_POOL_SEED),
        authority.toBuffer(),
        poolSeed.toArrayLike(Buffer, "le", 8),
      ],
      this.programId
    );
  }

  /**
   * Derive the policy PDA address.
   */
  async findPolicyAddress(
    pool: PublicKey,
    depositor: PublicKey,
    txSignature: Uint8Array
  ): Promise<[PublicKey, number]> {
    return PublicKey.findProgramAddressSync(
      [
        Buffer.from(POLICY_SEED),
        pool.toBuffer(),
        depositor.toBuffer(),
        txSignature.slice(0, 32),
      ],
      this.programId
    );
  }

  /**
   * Derive the refund record PDA address.
   */
  async findRefundAddress(policy: PublicKey): Promise<[PublicKey, number]> {
    return PublicKey.findProgramAddressSync(
      [Buffer.from(REFUND_SEED), policy.toBuffer()],
      this.programId
    );
  }

  /**
   * Fetch an insurance pool account.
   */
  async getPool(poolAddress: PublicKey): Promise<InsurancePool | null> {
    const info = await this.connection.getAccountInfo(poolAddress);
    if (!info) return null;

    const data = info.data;
    const offset = 8; // skip discriminator

    return {
      authority: new PublicKey(data.subarray(offset, offset + 32)),
      poolSeed: new BN(data.subarray(offset + 32, offset + 40), "le"),
      totalPremiums: new BN(data.subarray(offset + 40, offset + 48), "le"),
      totalRefunds: new BN(data.subarray(offset + 48, offset + 56), "le"),
      activePolicies: data.readUInt32LE(offset + 56),
      baseRateBps: data.readUInt16LE(offset + 60),
      createdAt: new BN(data.subarray(offset + 62, offset + 70), "le"),
      lastUpdated: new BN(data.subarray(offset + 70, offset + 78), "le"),
      bump: data[offset + 78],
    };
  }

  /**
   * Fetch a policy account.
   */
  async getPolicy(policyAddress: PublicKey): Promise<Policy | null> {
    const info = await this.connection.getAccountInfo(policyAddress);
    if (!info) return null;

    const data = info.data;
    const offset = 8;

    return {
      owner: new PublicKey(data.subarray(offset, offset + 32)),
      pool: new PublicKey(data.subarray(offset + 32, offset + 64)),
      premiumAmount: new BN(data.subarray(offset + 64, offset + 72), "le"),
      txSignature: new Uint8Array(data.subarray(offset + 72, offset + 136)),
      status: data[offset + 136],
      createdAt: new BN(data.subarray(offset + 137, offset + 145), "le"),
      expiresAt: new BN(data.subarray(offset + 145, offset + 153), "le"),
      bump: data[offset + 153],
    };
  }

  /**
   * Fetch policy or throw if not found.
   */
  async getPolicyOrThrow(policyAddress: PublicKey) {
    const policy = await this.getPolicy(policyAddress);
    if (!policy) throw new Error("Policy not found: " + policyAddress.toBase58());
    return policy;
  }

  /**
   * Calculate the premium for a given transaction fee.
   */
  calculatePremium(txFeeLamports: number, rateBps: number): number {
    const premium = Math.ceil((txFeeLamports * rateBps) / 10000);
    return Math.max(premium, MIN_PREMIUM_LAMPORTS);
  }

  /**
   * Get connection instance for advanced usage.
   */
  getConnection(): Connection {
    return this.connection;
  }

  /**
   * Fetch pool or throw if not found.
   */
  async getPoolOrThrow(poolAddress: PublicKey) {
    const pool = await this.getPool(poolAddress);
    if (!pool) throw new Error("Pool not found: " + poolAddress.toBase58());
    return pool;
  }

  /**
   * Get the program ID.
   */
  getProgramId(): PublicKey {
    return this.programId;
  }
}
// ref: 0082
// ref: 0087
// ref: 0097
// ref: 0099
// ref: 0122
// ref: 0137
// ref: 0138
// ref: 0141
// ref: 0147
// ref: 0156
// ref: 0157
// ref: 0161
