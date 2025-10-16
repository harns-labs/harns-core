//! Protocol-wide constants.

/// Minimum premium in lamports (0.000005 SOL).
pub const MIN_PREMIUM_LAMPORTS: u64 = 5_000;

/// Maximum insurance rate in basis points (100%).
pub const MAX_RATE_BPS: u16 = 10_000;

/// Default insurance rate in basis points (2.5%).
pub const DEFAULT_RATE_BPS: u16 = 250;

/// Policy time-to-live in seconds (5 minutes).
pub const POLICY_TTL_SECONDS: i64 = 300;

/// Maximum number of active policies per pool.
pub const MAX_POLICIES_PER_POOL: u32 = 100_000;

/// Seed prefix for insurance pool PDA.
pub const POOL_SEED: &[u8] = b"insurance_pool";

/// Seed prefix for policy PDA.
pub const POLICY_SEED: &[u8] = b"policy";

/// Seed prefix for refund record PDA.
pub const REFUND_SEED: &[u8] = b"refund";

/// Lamports per SOL.
pub const LAMPORTS_PER_SOL: u64 = 1_000_000_000;

/// Basis points scale factor.
pub const BPS_DENOMINATOR: u64 = 10_000;

/// Minimum rent-exempt balance to keep in pool (0.01 SOL buffer).
pub const MIN_POOL_RESERVE: u64 = 10_000_000;

/// Maximum pool seed value (arbitrary upper bound).
pub const MAX_POOL_SEED: u64 = u64::MAX;
