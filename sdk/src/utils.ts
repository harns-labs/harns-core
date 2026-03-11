import { PublicKey } from "@solana/web3.js";
import { BN } from "@coral-xyz/anchor";
import { LAMPORTS_PER_SOL, MIN_PREMIUM_LAMPORTS, MAX_RATE_BPS } from "./constants";

/**
 * Convert lamports to SOL.
 */
export function lamportsToSol(lamports: BN): number {
  return lamports.toNumber() / LAMPORTS_PER_SOL;
}

/**
 * Convert SOL to lamports.
 */
export function solToLamports(sol: number): BN {
  return new BN(Math.round(sol * LAMPORTS_PER_SOL));
}

/**
 * Format a PublicKey as a truncated display string.
 */
export function shortenAddress(address: PublicKey, chars: number = 4): string {
  const str = address.toBase58();
  return str.slice(0, chars) + "..." + str.slice(-chars);
}

/**
 * Check if a rate is within valid bounds.
 */
export function isValidRate(rateBps: number): boolean {
  return rateBps > 0 && rateBps <= MAX_RATE_BPS;
}

/**
 * Check if a premium meets the minimum threshold.
 */
export function isValidPremium(lamports: number): boolean {
  return lamports >= MIN_PREMIUM_LAMPORTS;
}

/**
 * Sleep for the given number of milliseconds.
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Retry a function with exponential backoff.
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  let lastError: Error | undefined;
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err as Error;
      if (i < maxRetries - 1) {
        await sleep(baseDelay * Math.pow(2, i));
      }
    }
  }
  throw lastError;
}
