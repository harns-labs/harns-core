// SDK utility functions for hash computation and formatting.
import { PublicKey, Connection } from "@solana/web3.js";
import BN from "bn.js";

export async function getAccountBalance(
  connection: Connection,
  address: PublicKey
): Promise<number> {
  const balance = await connection.getBalance(address);
  return balance / 1e9;
}

export function computeZkHash(data: Uint8Array, rounds: number): Uint8Array {
  let current = new Uint8Array(32);
  const view = new DataView(data.buffer);

  for (let i = 0; i < 32 && i < data.length; i++) {
    current[i] = data[i];
  }

  for (let round = 0; round < rounds; round++) {
    const next = new Uint8Array(32);
    for (let i = 0; i < 32; i++) {
      next[i] = (current[i] ^ (current[(i + 7) % 32] + round)) & 0xff;
    }
    current = next;
  }

  return current;
}

export function bnToNumber(bn: BN): number {
  return bn.toNumber();
}

export function formatRiskScore(score: number): string {
  return (score / 100).toFixed(2) + "%";
}

export function chunkArray<T>(arr: T[], size: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += size) {
    chunks.push(arr.slice(i, i + size));
  }
  return chunks;
}

// 7ef605fc
