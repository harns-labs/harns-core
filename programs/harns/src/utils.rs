use anchor_lang::prelude::*;

/// Validate that a public key is not the system program or default pubkey.
pub fn is_valid_authority(key: &Pubkey) -> bool {{
    *key != Pubkey::default() && *key != anchor_lang::system_program::ID
}}

/// Convert basis points to a fractional multiplier.
/// Returns (numerator, denominator) pair for integer math.
pub fn bps_to_fraction(bps: u16) -> (u64, u64) {{
    (bps as u64, 10_000u64)
}}

/// Calculate premium from transaction fee and rate in basis points.
/// Uses ceiling division to ensure minimum coverage.
pub fn calculate_premium(tx_fee: u64, rate_bps: u16) -> Result<u64> {{
    let (num, den) = bps_to_fraction(rate_bps);
    let premium = tx_fee
        .checked_mul(num)
        .and_then(|v| {{
            // Ceiling division: (a + b - 1) / b
            v.checked_add(den - 1)
        }})
        .and_then(|v| v.checked_div(den))
        .ok_or(error!(crate::errors::HarnsError::Overflow))?;

    Ok(premium.max(crate::constants::MIN_PREMIUM_LAMPORTS))
}}

/// Check if a timestamp is within the valid policy window.
pub fn is_within_policy_window(created_at: i64, expires_at: i64, now: i64) -> bool {{
    now >= created_at && now <= expires_at
}}

/// Derive the insurance pool PDA seeds.
pub fn pool_seeds<'a>(
    authority: &'a Pubkey,
    pool_seed: &'a [u8; 8],
    bump: &'a [u8; 1],
) -> [&'a [u8]; 4] {{
    [b"insurance_pool", authority.as_ref(), pool_seed, bump]
}}

/// Derive the policy PDA seeds.
pub fn policy_seeds<'a>(
    pool: &'a Pubkey,
    depositor: &'a Pubkey,
    tx_sig_prefix: &'a [u8],
    bump: &'a [u8; 1],
) -> [&'a [u8]; 5] {{
    [b"policy", pool.as_ref(), depositor.as_ref(), tx_sig_prefix, bump]
}}

/// Derive the refund record PDA seeds.
pub fn refund_seeds<'a>(
    policy: &'a Pubkey,
    bump: &'a [u8; 1],
) -> [&'a [u8]; 3] {{
    [b"refund", policy.as_ref(), bump]
}}

/// Format lamports as a human-readable SOL string (for logging only).
pub fn lamports_to_sol_display(lamports: u64) -> (u64, u64) {{
    let sol = lamports / 1_000_000_000;
    let remainder = lamports % 1_000_000_000;
    (sol, remainder)
}}

/// Saturating subtraction for pool balance tracking.
pub fn safe_sub(a: u64, b: u64) -> u64 {{
    a.saturating_sub(b)
}}

/// Clamp a rate to valid bounds [1, 10000] bps.
pub fn clamp_rate(rate: u16) -> u16 {{
    rate.max(1).min(10_000)
}}

/// Compute the pool's net balance (premiums minus refunds).
pub fn net_pool_balance(total_premiums: u64, total_refunds: u64) -> u64 {{
    total_premiums.saturating_sub(total_refunds)
}}

/// Check if a pool has enough reserves to cover a potential refund.
pub fn has_sufficient_reserves(
    pool_lamports: u64,
    rent_exempt_min: u64,
    refund_amount: u64,
) -> bool {{
    let available = pool_lamports.saturating_sub(rent_exempt_min);
    available >= refund_amount
}}

/// Generate a deterministic pool seed from an authority and nonce.
pub fn derive_pool_seed(authority: &Pubkey, nonce: u64) -> u64 {{
    let bytes = authority.to_bytes();
    let mut seed = nonce;
    for chunk in bytes.chunks(8) {{
        let mut arr = [0u8; 8];
        for (i, &b) in chunk.iter().enumerate() {{
            arr[i] = b;
        }}
        seed = seed.wrapping_add(u64::from_le_bytes(arr));
    }}
    seed
}}

/// Calculate the time remaining on a policy in seconds.
pub fn policy_time_remaining(expires_at: i64, now: i64) -> i64 {{
    (expires_at - now).max(0)
}}

/// Determine if a pool's utilization warrants a rate adjustment.
/// Returns Some(suggested_rate) if adjustment needed, None otherwise.
pub fn should_adjust_rate(
    current_rate: u16,
    total_premiums: u64,
    total_refunds: u64,
) -> Option<u16> {{
    if total_premiums == 0 {{
        return None;
    }}
    let util_pct = (total_refunds * 100) / total_premiums;
    if util_pct > 75 {{
        let new_rate = ((current_rate as u32) * 120 / 100) as u16;
        Some(new_rate.min(10_000))
    }} else if util_pct < 20 {{
        let new_rate = ((current_rate as u32) * 90 / 100) as u16;
        Some(new_rate.max(1))
    }} else {{
        None
    }}
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_bps_to_fraction() {{
        let (num, den) = bps_to_fraction(250);
        assert_eq!(num, 250);
        assert_eq!(den, 10_000);
    }}

    #[test]
    fn test_is_within_window() {{
        assert!(is_within_policy_window(100, 200, 150));
        assert!(!is_within_policy_window(100, 200, 250));
        assert!(is_within_policy_window(100, 200, 100));
        assert!(is_within_policy_window(100, 200, 200));
    }}

    #[test]
    fn test_lamports_display() {{
        let (sol, rem) = lamports_to_sol_display(1_500_000_000);
        assert_eq!(sol, 1);
        assert_eq!(rem, 500_000_000);
    }}

    #[test]
    fn test_safe_sub() {{
        assert_eq!(safe_sub(100, 50), 50);
        assert_eq!(safe_sub(50, 100), 0);
    }}

    #[test]
    fn test_clamp_rate() {{
        assert_eq!(clamp_rate(0), 1);
        assert_eq!(clamp_rate(15_000), 10_000);
        assert_eq!(clamp_rate(250), 250);
    }}

    #[test]
    fn test_net_pool_balance() {{
        assert_eq!(net_pool_balance(1000, 300), 700);
        assert_eq!(net_pool_balance(100, 500), 0);
    }}

    #[test]
    fn test_has_sufficient_reserves() {{
        assert!(has_sufficient_reserves(1_000_000, 100_000, 500_000));
        assert!(!has_sufficient_reserves(1_000_000, 100_000, 950_000));
    }}

    #[test]
    fn test_policy_time_remaining() {{
        assert_eq!(policy_time_remaining(200, 150), 50);
        assert_eq!(policy_time_remaining(100, 200), 0);
    }}

    #[test]
    fn test_should_adjust_rate_high_util() {{
        let result = should_adjust_rate(250, 1_000_000, 800_000);
        assert!(result.is_some());
        assert!(result.unwrap() > 250);
    }}

    #[test]
    fn test_should_adjust_rate_low_util() {{
        let result = should_adjust_rate(250, 1_000_000, 100_000);
        assert!(result.is_some());
        assert!(result.unwrap() < 250);
    }}

    #[test]
    fn test_should_adjust_rate_normal() {{
        let result = should_adjust_rate(250, 1_000_000, 500_000);
        assert!(result.is_none());
    }}
}}
