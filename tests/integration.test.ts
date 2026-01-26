import { PublicKey } from "@solana/web3.js";
import { PROGRAM_ID, deriveConfigPda, deriveFlagPda } from "../sdk/src/index";
import { computeZkHash } from "../sdk/src/utils";
import { MAX_RISK_SCORE, ZK_HASH_ROUNDS } from "../sdk/src/constants";
import { RiskScoreOverflowError } from "../sdk/src/errors";

describe("clstr integration", () => {
  test("config PDA is deterministic across calls", () => {
    const pda1 = deriveConfigPda();
    const pda2 = deriveConfigPda();
    expect(pda1.toBase58()).toBe(pda2.toBase58());
  });

  test("flag PDA changes with different target-flagger pairs", () => {
    const target1 = PublicKey.unique();
    const target2 = PublicKey.unique();
    const flagger = PublicKey.unique();
    const pda1 = deriveFlagPda(target1, flagger);
    const pda2 = deriveFlagPda(target2, flagger);
    expect(pda1.toBase58()).not.toBe(pda2.toBase58());
  });

  test("zk hash output length is 32 bytes", () => {
    const data = new Uint8Array([0xde, 0xad, 0xbe, 0xef]);
    const hash = computeZkHash(data, ZK_HASH_ROUNDS);
    expect(hash.length).toBe(32);
  });

  test("MAX_RISK_SCORE constant matches expected value", () => {
    expect(MAX_RISK_SCORE).toBe(10000);
  });

  test("RiskScoreOverflowError contains score in message", () => {
    const err = new RiskScoreOverflowError(15000);
    expect(err.message).toContain("15000");
    expect(err.name).toBe("RiskScoreOverflowError");
  });

  test("program ID matches deployed address", () => {
    expect(PROGRAM_ID.toBase58()).toBe("E1iTSqt1YkW6LoNXMspEoxsdotzEdmn3QjEJL5R3NUwe");
  });
});

// 1c383cd3
