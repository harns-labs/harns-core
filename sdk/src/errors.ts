/**
 * Error codes matching the on-chain HarnsError enum.
 * Offset by 6000 as per Anchor convention.
 */
export enum HarnsErrorCode {
  InvalidRate = 6000,
  PremiumTooLow = 6001,
  PolicyNotActive = 6002,
  PolicyExpired = 6003,
  Unauthorized = 6004,
  Overflow = 6005,
  InsufficientBalance = 6006,
  SignatureMismatch = 6007,
  InvalidPool = 6008,
  PoolPaused = 6009,
}

const ERROR_MESSAGES: Record<number, string> = {
  [HarnsErrorCode.InvalidRate]: "Insurance rate must be between 1 and 10000 basis points",
  [HarnsErrorCode.PremiumTooLow]: "Premium amount is below minimum threshold",
  [HarnsErrorCode.PolicyNotActive]: "Policy is not in active state",
  [HarnsErrorCode.PolicyExpired]: "Policy has expired and is no longer claimable",
  [HarnsErrorCode.Unauthorized]: "Caller is not authorized to perform this action",
  [HarnsErrorCode.Overflow]: "Arithmetic overflow detected",
  [HarnsErrorCode.InsufficientBalance]: "Insufficient pool balance for refund",
  [HarnsErrorCode.SignatureMismatch]: "Transaction signature does not match policy",
  [HarnsErrorCode.InvalidPool]: "Pool account data is invalid or corrupted",
  [HarnsErrorCode.PoolPaused]: "Pool is currently paused",
};

/**
 * Parse an Anchor error code into a human-readable message.
 */
export function parseHarnsError(code: number): string {
  return ERROR_MESSAGES[code] ?? "Unknown error: " + code;
}

/**
 * Check if an error is a known Harns protocol error.
 */
export function isHarnsError(err: unknown): boolean {
  if (typeof err === "object" && err !== null && "code" in err) {
    const code = (err as { code: number }).code;
    return code >= 6000 && code <= 6009;
  }
  return false;
}
