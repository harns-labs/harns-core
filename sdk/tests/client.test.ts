import { PublicKey } from "@solana/web3.js";
import { BN } from "@coral-xyz/anchor";
import { HarnsClient } from "../src/client";
import {
  HARNS_PROGRAM_ID,
  INSURANCE_POOL_SEED,
  POLICY_SEED,
  REFUND_SEED,
  MIN_PREMIUM_LAMPORTS,
  DEFAULT_RATE_BPS,
} from "../src/constants";

describe("HarnsClient", () => {
  const config = {
    rpcUrl: "https://api.devnet.solana.com",
  };

  let client: HarnsClient;

  beforeEach(() => {
    client = new HarnsClient(config);
  });

  describe("constructor", () => {
    it("should initialize with default program ID", () => {
      expect(client.getProgramId().toBase58()).toBe(HARNS_PROGRAM_ID);
    });

    it("should accept a custom program ID", () => {
      const customId = PublicKey.unique();
      const customClient = new HarnsClient({
        ...config,
        programId: customId,
      });
      expect(customClient.getProgramId().toBase58()).toBe(customId.toBase58());
    });

    it("should expose the connection instance", () => {
      const conn = client.getConnection();
      expect(conn).toBeDefined();
    });
  });

  describe("findPoolAddress", () => {
    it("should derive a deterministic pool PDA", async () => {
      const authority = PublicKey.unique();
      const seed = new BN(1);

      const [addr1] = await client.findPoolAddress(authority, seed);
      const [addr2] = await client.findPoolAddress(authority, seed);

      expect(addr1.toBase58()).toBe(addr2.toBase58());
    });

    it("should produce different addresses for different seeds", async () => {
      const authority = PublicKey.unique();

      const [addr1] = await client.findPoolAddress(authority, new BN(1));
      const [addr2] = await client.findPoolAddress(authority, new BN(2));

      expect(addr1.toBase58()).not.toBe(addr2.toBase58());
    });
  });

  describe("findPolicyAddress", () => {
    it("should derive a deterministic policy PDA", async () => {
      const pool = PublicKey.unique();
      const depositor = PublicKey.unique();
      const sig = new Uint8Array(64).fill(1);

      const [addr1] = await client.findPolicyAddress(pool, depositor, sig);
      const [addr2] = await client.findPolicyAddress(pool, depositor, sig);

      expect(addr1.toBase58()).toBe(addr2.toBase58());
    });
  });

  describe("findRefundAddress", () => {
    it("should derive a deterministic refund PDA", async () => {
      const policy = PublicKey.unique();

      const [addr1] = await client.findRefundAddress(policy);
      const [addr2] = await client.findRefundAddress(policy);

      expect(addr1.toBase58()).toBe(addr2.toBase58());
    });
  });

  describe("calculatePremium", () => {
    it("should calculate premium based on fee and rate", () => {
      const fee = 100_000;
      const rate = 250; // 2.5%
      const premium = client.calculatePremium(fee, rate);
      expect(premium).toBe(2500);
    });

    it("should enforce minimum premium", () => {
      const fee = 100;
      const rate = 100;
      const premium = client.calculatePremium(fee, rate);
      expect(premium).toBe(MIN_PREMIUM_LAMPORTS);
    });

    it("should round up fractional premiums", () => {
      const fee = 10_001;
      const rate = 250;
      const premium = client.calculatePremium(fee, rate);
      // 10001 * 250 / 10000 = 250.025 -> ceil -> 251
      expect(premium).toBe(251);
    });

    it("should handle zero rate gracefully", () => {
      const fee = 100_000;
      const rate = 0;
      const premium = client.calculatePremium(fee, rate);
      expect(premium).toBe(MIN_PREMIUM_LAMPORTS);
    });
  });
});
