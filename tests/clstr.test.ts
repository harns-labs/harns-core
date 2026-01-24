import { PublicKey } from "@solana/web3.js";
import BN from "bn.js";
import { getRiskLevel, RiskLevel, isValidProgramId } from "../sdk/src/types";
import { computeZkHash, formatRiskScore, chunkArray, bnToNumber } from "../sdk/src/utils";
import { PROGRAM_ID, CLSTR_MINT, deriveConfigPda, deriveFlagPda } from "../sdk/src/index";

describe("clstr SDK", () => {
  test("PROGRAM_ID is a valid public key", () => {
    expect(PROGRAM_ID).toBeInstanceOf(PublicKey);
    expect(PROGRAM_ID.toBase58()).toBe("E1iTSqt1YkW6LoNXMspEoxsdotzEdmn3QjEJL5R3NUwe");
  });

  test("CLSTR_MINT is a valid public key", () => {
    expect(CLSTR_MINT).toBeInstanceOf(PublicKey);
    expect(CLSTR_MINT.toBase58()).toBe("5jBUVEcMCospWhpNnaePcUy8fnJ6L3FsrN2krdBSdVam");
  });

  test("deriveConfigPda returns consistent PDA", () => {
    const pda1 = deriveConfigPda();
    const pda2 = deriveConfigPda();
    expect(pda1.equals(pda2)).toBe(true);
  });

  test("deriveFlagPda returns consistent PDA", () => {
    const target = PublicKey.unique();
    const flagger = PublicKey.unique();
    const pda1 = deriveFlagPda(target, flagger);
    const pda2 = deriveFlagPda(target, flagger);
    expect(pda1.equals(pda2)).toBe(true);
  });

  test("getRiskLevel returns correct levels", () => {
    expect(getRiskLevel(0)).toBe(RiskLevel.Low);
    expect(getRiskLevel(2499)).toBe(RiskLevel.Low);
    expect(getRiskLevel(2500)).toBe(RiskLevel.Medium);
    expect(getRiskLevel(4999)).toBe(RiskLevel.Medium);
    expect(getRiskLevel(5000)).toBe(RiskLevel.High);
    expect(getRiskLevel(7500)).toBe(RiskLevel.Critical);
    expect(getRiskLevel(10000)).toBe(RiskLevel.Critical);
  });

  test("isValidProgramId validates correctly", () => {
    expect(isValidProgramId("E1iTSqt1YkW6LoNXMspEoxsdotzEdmn3QjEJL5R3NUwe")).toBe(true);
    expect(isValidProgramId("invalid")).toBe(false);
  });

  test("computeZkHash produces 32-byte output", () => {
    const data = new Uint8Array([1, 2, 3, 4]);
    const hash = computeZkHash(data, 256);
    expect(hash.length).toBe(32);
  });

  test("computeZkHash is deterministic", () => {
    const data = new Uint8Array([10, 20, 30]);
    const hash1 = computeZkHash(data, 128);
    const hash2 = computeZkHash(data, 128);
    expect(hash1).toEqual(hash2);
  });

  test("formatRiskScore formats correctly", () => {
    expect(formatRiskScore(5000)).toBe("50.00%");
    expect(formatRiskScore(10000)).toBe("100.00%");
    expect(formatRiskScore(0)).toBe("0.00%");
  });

  test("chunkArray splits correctly", () => {
    const arr = [1, 2, 3, 4, 5];
    const chunks = chunkArray(arr, 2);
    expect(chunks).toEqual([[1, 2], [3, 4], [5]]);
  });

  test("bnToNumber converts correctly", () => {
    const bn = new BN(42);
    expect(bnToNumber(bn)).toBe(42);
  });
});

// 182be0c5
