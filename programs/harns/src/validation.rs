//! Input validation helpers for instruction handlers.

use anchor_lang::prelude::*;
use crate::errors::HarnsError;
use crate::constants;

/// Validate that a premium amount meets the minimum threshold.
pub fn validate_premium_amount(amount: u64) -> Result<()> {{
    require!(
        amount >= constants::MIN_PREMIUM_LAMPORTS,
        HarnsError::PremiumTooLow
    );
    Ok(())
}}

/// Validate that a rate is within acceptable bounds.
pub fn validate_rate(rate_bps: u16) -> Result<()> {{
    require!(
        rate_bps > 0 && rate_bps <= constants::MAX_RATE_BPS,
        HarnsError::InvalidRate
    );
    Ok(())
}}

/// Validate that a transaction signature is not all zeros.
pub fn validate_tx_signature(sig: &[u8; 64]) -> Result<()> {{
    let is_zero = sig.iter().all(|&b| b == 0);
    require!(!is_zero, HarnsError::SignatureMismatch);
    Ok(())
}}

/// Validate that a policy is in active state and not expired.
pub fn validate_policy_claimable(
    status: u8,
    expires_at: i64,
    now: i64,
) -> Result<()> {{
    require!(status == 0, HarnsError::PolicyNotActive);
    require!(now <= expires_at, HarnsError::PolicyExpired);
    Ok(())
}}

/// Validate that the pool has sufficient balance for a refund.
pub fn validate_pool_balance(
    pool_lamports: u64,
    refund_amount: u64,
    rent_exempt_minimum: u64,
) -> Result<()> {{
    let available = pool_lamports.saturating_sub(rent_exempt_minimum);
    require!(
        available >= refund_amount,
        HarnsError::InsufficientBalance
    );
    Ok(())
}}

/// Validate that the caller is the pool authority.
pub fn validate_authority(expected: &Pubkey, actual: &Pubkey) -> Result<()> {{
    require!(expected == actual, HarnsError::Unauthorized);
    Ok(())
}}

/// Validate pool seed is within acceptable range.
pub fn validate_pool_seed(seed: u64) -> Result<()> {{
    require!(seed > 0, HarnsError::InvalidPool);
    Ok(())
}}
