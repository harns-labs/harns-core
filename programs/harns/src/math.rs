//! Fixed-point arithmetic helpers for premium calculations.
//!
//! All math uses u64 with explicit scaling to avoid floating point.
//! Basis points (bps) are used as the standard rate unit: 1 bps = 0.01%.

use anchor_lang::prelude::*;
use crate::errors::HarnsError;

/// Scale factor for basis point calculations.
pub const BPS_SCALE: u64 = 10_000;

/// Maximum representable premium in lamports (10 SOL).
pub const MAX_PREMIUM: u64 = 10_000_000_000;

/// Multiply two u64 values with overflow protection.
pub fn checked_mul(a: u64, b: u64) -> Result<u64> {{
    a.checked_mul(b).ok_or_else(|| error!(HarnsError::Overflow))
}}

/// Divide two u64 values with zero-division protection.
pub fn checked_div(a: u64, b: u64) -> Result<u64> {{
    require!(b > 0, HarnsError::Overflow);
    a.checked_div(b).ok_or_else(|| error!(HarnsError::Overflow))
}}

/// Ceiling division: returns ceil(a / b).
pub fn ceil_div(a: u64, b: u64) -> Result<u64> {{
    require!(b > 0, HarnsError::Overflow);
    let result = a.checked_add(b - 1)
        .ok_or_else(|| error!(HarnsError::Overflow))?
        .checked_div(b)
        .ok_or_else(|| error!(HarnsError::Overflow))?;
    Ok(result)
}}

/// Apply a basis point rate to an amount using ceiling division.
/// premium = ceil(amount * rate_bps / 10000)
pub fn apply_rate(amount: u64, rate_bps: u16) -> Result<u64> {{
    let product = checked_mul(amount, rate_bps as u64)?;
    ceil_div(product, BPS_SCALE)
}}

/// Calculate the pool's utilization ratio as basis points.
/// utilization = (total_refunds * 10000) / total_premiums
pub fn utilization_bps(total_premiums: u64, total_refunds: u64) -> Result<u16> {{
    if total_premiums == 0 {{
        return Ok(0);
    }}
    let scaled = checked_mul(total_refunds, BPS_SCALE)?;
    let ratio = checked_div(scaled, total_premiums)?;
    Ok(ratio.min(BPS_SCALE) as u16)
}}

/// Suggest a new rate based on utilization.
/// Higher utilization leads to higher premiums.
pub fn suggested_rate(current_rate: u16, utilization: u16) -> u16 {{
    if utilization > 7_500 {{
        // High utilization: increase rate by 20%
        let new_rate = (current_rate as u32) * 120 / 100;
        (new_rate as u16).min(10_000)
    }} else if utilization < 2_000 {{
        // Low utilization: decrease rate by 10%
        let new_rate = (current_rate as u32) * 90 / 100;
        (new_rate as u16).max(1)
    }} else {{
        current_rate
    }}
}}

/// Linear interpolation between two rates.
pub fn lerp_rate(from: u16, to: u16, progress_bps: u16) -> u16 {{
    let from_u32 = from as u32;
    let to_u32 = to as u32;
    let p = progress_bps as u32;

    if to_u32 >= from_u32 {{
        let delta = (to_u32 - from_u32) * p / BPS_SCALE as u32;
        (from_u32 + delta) as u16
    }} else {{
        let delta = (from_u32 - to_u32) * p / BPS_SCALE as u32;
        (from_u32 - delta) as u16
    }}
}}

#[cfg(test)]
mod tests {{
    use super::*;

    #[test]
    fn test_apply_rate_basic() {{
        // 100_000 lamports at 250 bps (2.5%) = 2500
        let result = apply_rate(100_000, 250).unwrap();
        assert_eq!(result, 2_500);
    }}

    #[test]
    fn test_apply_rate_ceiling() {{
        // 10_001 * 250 / 10000 = 250.025 -> ceil -> 251
        let result = apply_rate(10_001, 250).unwrap();
        assert_eq!(result, 251);
    }}

    #[test]
    fn test_utilization_empty_pool() {{
        let result = utilization_bps(0, 0).unwrap();
        assert_eq!(result, 0);
    }}

    #[test]
    fn test_utilization_half() {{
        let result = utilization_bps(1_000_000, 500_000).unwrap();
        assert_eq!(result, 5_000);
    }}

    #[test]
    fn test_suggested_rate_high_util() {{
        let rate = suggested_rate(250, 8_000);
        assert_eq!(rate, 300); // 250 * 1.2 = 300
    }}

    #[test]
    fn test_suggested_rate_low_util() {{
        let rate = suggested_rate(250, 1_000);
        assert_eq!(rate, 225); // 250 * 0.9 = 225
    }}

    #[test]
    fn test_lerp_rate() {{
        let result = lerp_rate(100, 200, 5_000);
        assert_eq!(result, 150); // midpoint
    }}
}}
