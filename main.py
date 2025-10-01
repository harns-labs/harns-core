#!/usr/bin/env python3
"""
Harns Protocol -- Public GitHub Repository Generator
Generates a realistic Solana/Anchor project structure with natural commit history.
"""

import os
import subprocess
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================
PROJECT_NAME = "harns"
DESCRIPTION = "TX failure insurance protocol for Solana. Escrow-based premium pool with automatic refund engine."
REPO_DIR = "."
USER_NAME = "harns-labs"
USER_EMAIL = "258671573+harns-labs@users.noreply.github.com"
START_DATE = datetime(2025, 10, 1)
END_DATE = datetime(2026, 3, 1)
TARGET_COMMITS = 180
BANNER_PATH = "./banner.png"
VERSION = "0.4.2"

# ============================================================
# HELPERS
# ============================================================

def run_git(args, date=None):
    env = os.environ.copy()
    if date:
        date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str
    cmd = ["git"] + args
    subprocess.run(cmd, cwd=REPO_DIR, env=env, check=True,
                   capture_output=True, text=True)


def write_file(path, content):
    full = os.path.join(REPO_DIR, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def commit(message, date, files=None):
    if files:
        for f in files:
            run_git(["add", f], date)
    else:
        run_git(["add", "-A"], date)
    run_git(["commit", "-m", message, "--allow-empty"], date)


def generate_commit_schedule(start, end, target):
    """Distribute commits across dates with natural patterns."""
    days = (end - start).days
    schedule = {}
    total = 0

    for d in range(days):
        dt = start + timedelta(days=d)
        weekday = dt.weekday()

        if weekday >= 5:  # weekend
            weight = random.choices([0, 1, 2], weights=[40, 45, 15])[0]
        else:  # weekday
            weight = random.choices([0, 1, 2, 3, 4, 5], weights=[15, 25, 25, 20, 10, 5])[0]

        schedule[dt] = weight
        total += weight

    # Scale to hit target
    if total > 0:
        scale = target / total
        adjusted = {}
        running = 0
        for dt, count in schedule.items():
            scaled = max(0, round(count * scale))
            adjusted[dt] = scaled
            running += scaled
        schedule = adjusted

    # Fix: no 3+ consecutive zero days
    dates = sorted(schedule.keys())
    for i in range(len(dates) - 2):
        if (schedule[dates[i]] == 0 and
            schedule[dates[i+1]] == 0 and
            schedule[dates[i+2]] == 0):
            schedule[dates[i+1]] = random.randint(1, 2)

    return schedule


# ============================================================
# FILE CONTENT GENERATORS
# ============================================================

def gen_cargo_toml():
    return f"""[package]
name = "{PROJECT_NAME}"
version = "{VERSION}"
description = "{DESCRIPTION}"
edition = "2021"
license = "MIT"
readme = "../../README.md"

[lib]
crate-type = ["cdylib", "lib"]
name = "{PROJECT_NAME}"

[features]
no-entrypoint = []
no-idl = []
no-log-ix-name = []
cpi = ["no-entrypoint"]
default = []

[dependencies]
anchor-lang = "0.29.0"
anchor-spl = "0.29.0"
solana-program = "=1.17.0"

[dev-dependencies]
anchor-client = "0.29.0"
"""


def gen_lib_rs():
    return """use anchor_lang::prelude::*;

mod state;
mod instructions;
mod errors;
mod events;
pub mod constants;
pub mod math;
pub mod utils;
pub mod validation;

use instructions::*;

declare_id!("HRNs8jz4nnFSCmj3G7pWLrTBLhzGkXXbVnPJg2Cv9t7");

#[program]
pub mod harns {{
    use super::*;

    pub fn initialize(
        ctx: Context<Initialize>,
        pool_seed: u64,
        base_rate_bps: u16,
    ) -> Result<()> {{
        instructions::initialize::handler(ctx, pool_seed, base_rate_bps)
    }}

    pub fn deposit_premium(
        ctx: Context<DepositPremium>,
        amount: u64,
        tx_signature: [u8; 64],
    ) -> Result<()> {{
        instructions::deposit_premium::handler(ctx, amount, tx_signature)
    }}

    pub fn process_refund(
        ctx: Context<ProcessRefund>,
        tx_signature: [u8; 64],
    ) -> Result<()> {{
        instructions::process_refund::handler(ctx, tx_signature)
    }}

    pub fn update_rates(
        ctx: Context<UpdateRates>,
        new_rate_bps: u16,
    ) -> Result<()> {{
        instructions::update_rates::handler(ctx, new_rate_bps)
    }}

    pub fn close_pool(ctx: Context<ClosePool>) -> Result<()> {{
        instructions::close_pool::handler(ctx)
    }}

    pub fn expire_policy(ctx: Context<ExpirePolicy>) -> Result<()> {{
        instructions::expire_policy::handler(ctx)
    }}

    pub fn transfer_authority(ctx: Context<TransferAuthority>) -> Result<()> {{
        instructions::transfer_authority::handler(ctx)
    }}
}}
"""


def gen_state_rs():
    return """use anchor_lang::prelude::*;

#[account]
#[derive(Default)]
pub struct InsurancePool {{
    /// Authority that controls the pool
    pub authority: Pubkey,
    /// Pool seed for PDA derivation
    pub pool_seed: u64,
    /// Total premiums collected (lamports)
    pub total_premiums: u64,
    /// Total refunds paid out (lamports)
    pub total_refunds: u64,
    /// Number of active policies
    pub active_policies: u32,
    /// Base insurance rate in basis points
    pub base_rate_bps: u16,
    /// Pool creation timestamp
    pub created_at: i64,
    /// Last rate update timestamp
    pub last_updated: i64,
    /// Bump seed for PDA
    pub bump: u8,
    /// Reserved for future use
    pub _padding: [u8; 64],
}}

impl InsurancePool {{
    /// 8 (discriminator) + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 64 = 151
    pub const SPACE: usize = 8 + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 64;
}}

#[account]
#[derive(Default)]
pub struct Policy {{
    /// Owner of the policy
    pub owner: Pubkey,
    /// Associated insurance pool
    pub pool: Pubkey,
    /// Premium paid (lamports)
    pub premium_amount: u64,
    /// Transaction signature being insured
    pub tx_signature: [u8; 64],
    /// Policy status: 0=active, 1=claimed, 2=expired
    pub status: u8,
    /// Timestamp of policy creation
    pub created_at: i64,
    /// Timestamp of policy expiry
    pub expires_at: i64,
    /// Bump seed for PDA
    pub bump: u8,
}}

impl Policy {{
    /// 8 (discriminator) + 32 + 32 + 8 + 64 + 1 + 8 + 8 + 1 = 162
    pub const SPACE: usize = 8 + 32 + 32 + 8 + 64 + 1 + 8 + 8 + 1;
}}

#[account]
pub struct RefundRecord {{
    /// Policy that was refunded
    pub policy: Pubkey,
    /// Recipient of the refund
    pub recipient: Pubkey,
    /// Refund amount (lamports)
    pub amount: u64,
    /// Refund timestamp
    pub refunded_at: i64,
    /// Bump seed for PDA
    pub bump: u8,
}}

impl RefundRecord {{
    /// 8 (discriminator) + 32 + 32 + 8 + 8 + 1 = 89
    pub const SPACE: usize = 8 + 32 + 32 + 8 + 8 + 1;
}}
"""


def gen_instructions_mod_rs():
    return """pub mod initialize;
pub mod deposit_premium;
pub mod process_refund;
pub mod update_rates;
pub mod close_pool;
pub mod expire_policy;
pub mod transfer_authority;

pub use initialize::*;
pub use deposit_premium::*;
pub use process_refund::*;
pub use update_rates::*;
pub use close_pool::*;
pub use expire_policy::*;
pub use transfer_authority::*;
"""


def gen_initialize_rs():
    return """use anchor_lang::prelude::*;
use crate::state::InsurancePool;
use crate::events::PoolInitialized;
use crate::errors::HarnsError;

#[derive(Accounts)]
#[instruction(pool_seed: u64)]
pub struct Initialize<'info> {{
    #[account(
        init,
        payer = authority,
        space = InsurancePool::SPACE,
        seeds = [b"insurance_pool", authority.key().as_ref(), &pool_seed.to_le_bytes()],
        bump,
    )]
    pub pool: Account<'info, InsurancePool>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}}

pub fn handler(
    ctx: Context<Initialize>,
    pool_seed: u64,
    base_rate_bps: u16,
) -> Result<()> {{
    require!(base_rate_bps > 0 && base_rate_bps <= 10000, HarnsError::InvalidRate);

    let pool = &mut ctx.accounts.pool;
    let clock = Clock::get()?;

    pool.authority = ctx.accounts.authority.key();
    pool.pool_seed = pool_seed;
    pool.base_rate_bps = base_rate_bps;
    pool.created_at = clock.unix_timestamp;
    pool.last_updated = clock.unix_timestamp;
    pool.bump = ctx.bumps.pool;
    pool.total_premiums = 0;
    pool.total_refunds = 0;
    pool.active_policies = 0;

    emit!(PoolInitialized {{
        pool: pool.key(),
        authority: ctx.accounts.authority.key(),
        base_rate_bps,
        timestamp: clock.unix_timestamp,
    }});

    msg!("Insurance pool initialized: {{}}", pool.key());
    Ok(())
}}
"""


def gen_deposit_premium_rs():
    return """use anchor_lang::prelude::*;
use anchor_lang::system_program;
use crate::state::{{InsurancePool, Policy}};
use crate::events::PremiumDeposited;
use crate::errors::HarnsError;

#[derive(Accounts)]
#[instruction(amount: u64, tx_signature: [u8; 64])]
pub struct DepositPremium<'info> {{
    #[account(
        mut,
        seeds = [b"insurance_pool", pool.authority.as_ref(), &pool.pool_seed.to_le_bytes()],
        bump = pool.bump,
    )]
    pub pool: Account<'info, InsurancePool>,

    #[account(
        init,
        payer = depositor,
        space = Policy::SPACE,
        seeds = [b"policy", pool.key().as_ref(), depositor.key().as_ref(), &tx_signature[..32]],
        bump,
    )]
    pub policy: Account<'info, Policy>,

    #[account(mut)]
    pub depositor: Signer<'info>,

    pub system_program: Program<'info, System>,
}}

pub fn handler(
    ctx: Context<DepositPremium>,
    amount: u64,
    tx_signature: [u8; 64],
) -> Result<()> {{
    let min_premium: u64 = 5_000;
    require!(amount >= min_premium, HarnsError::PremiumTooLow);

    let pool = &mut ctx.accounts.pool;
    let policy = &mut ctx.accounts.policy;
    let clock = Clock::get()?;

    // Transfer premium to pool
    let cpi_ctx = CpiContext::new(
        ctx.accounts.system_program.to_account_info(),
        system_program::Transfer {{
            from: ctx.accounts.depositor.to_account_info(),
            to: pool.to_account_info(),
        }},
    );
    system_program::transfer(cpi_ctx, amount)?;

    // Update pool state
    pool.total_premiums = pool.total_premiums.checked_add(amount)
        .ok_or(HarnsError::Overflow)?;
    pool.active_policies = pool.active_policies.checked_add(1)
        .ok_or(HarnsError::Overflow)?;

    // Initialize policy
    policy.owner = ctx.accounts.depositor.key();
    policy.pool = pool.key();
    policy.premium_amount = amount;
    policy.tx_signature = tx_signature;
    policy.status = 0; // active
    policy.created_at = clock.unix_timestamp;
    policy.expires_at = clock.unix_timestamp + 300; // 5 min TTL
    policy.bump = ctx.bumps.policy;

    emit!(PremiumDeposited {{
        pool: pool.key(),
        depositor: ctx.accounts.depositor.key(),
        amount,
        policy: policy.key(),
        timestamp: clock.unix_timestamp,
    }});

    msg!("Premium deposited: {{}} lamports", amount);
    Ok(())
}}
"""


def gen_process_refund_rs():
    return """use anchor_lang::prelude::*;
use crate::state::{{InsurancePool, Policy, RefundRecord}};
use crate::events::RefundProcessed;
use crate::errors::HarnsError;

#[derive(Accounts)]
#[instruction(tx_signature: [u8; 64])]
pub struct ProcessRefund<'info> {{
    #[account(
        mut,
        seeds = [b"insurance_pool", pool.authority.as_ref(), &pool.pool_seed.to_le_bytes()],
        bump = pool.bump,
    )]
    pub pool: Account<'info, InsurancePool>,

    #[account(
        mut,
        seeds = [b"policy", pool.key().as_ref(), claimant.key().as_ref(), &tx_signature[..32]],
        bump = policy.bump,
        constraint = policy.status == 0 @ HarnsError::PolicyNotActive,
        constraint = policy.owner == claimant.key() @ HarnsError::Unauthorized,
    )]
    pub policy: Account<'info, Policy>,

    #[account(
        init,
        payer = authority,
        space = RefundRecord::SPACE,
        seeds = [b"refund", policy.key().as_ref()],
        bump,
    )]
    pub refund_record: Account<'info, RefundRecord>,

    /// CHECK: Recipient of the refund
    #[account(mut)]
    pub claimant: AccountInfo<'info>,

    #[account(
        mut,
        constraint = authority.key() == pool.authority @ HarnsError::Unauthorized,
    )]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}}

pub fn handler(
    ctx: Context<ProcessRefund>,
    _tx_signature: [u8; 64],
) -> Result<()> {{
    let pool = &mut ctx.accounts.pool;
    let policy = &mut ctx.accounts.policy;
    let refund_record = &mut ctx.accounts.refund_record;
    let clock = Clock::get()?;

    require!(
        clock.unix_timestamp <= policy.expires_at,
        HarnsError::PolicyExpired
    );

    let refund_amount = policy.premium_amount;

    // Transfer refund from pool to claimant
    let pool_info = pool.to_account_info();
    let claimant_info = ctx.accounts.claimant.to_account_info();

    **pool_info.try_borrow_mut_lamports()? -= refund_amount;
    **claimant_info.try_borrow_mut_lamports()? += refund_amount;

    // Update pool state
    pool.total_refunds = pool.total_refunds.checked_add(refund_amount)
        .ok_or(HarnsError::Overflow)?;
    pool.active_policies = pool.active_policies.checked_sub(1)
        .ok_or(HarnsError::Overflow)?;

    // Update policy
    policy.status = 1; // claimed

    // Record refund
    refund_record.policy = policy.key();
    refund_record.recipient = ctx.accounts.claimant.key();
    refund_record.amount = refund_amount;
    refund_record.refunded_at = clock.unix_timestamp;
    refund_record.bump = ctx.bumps.refund_record;

    emit!(RefundProcessed {{
        pool: pool.key(),
        policy: policy.key(),
        recipient: ctx.accounts.claimant.key(),
        amount: refund_amount,
        timestamp: clock.unix_timestamp,
    }});

    msg!("Refund processed: {{}} lamports to {{}}", refund_amount, ctx.accounts.claimant.key());
    Ok(())
}}
"""


def gen_update_rates_rs():
    return """use anchor_lang::prelude::*;
use crate::state::InsurancePool;
use crate::events::RatesUpdated;
use crate::errors::HarnsError;

#[derive(Accounts)]
pub struct UpdateRates<'info> {{
    #[account(
        mut,
        seeds = [b"insurance_pool", pool.authority.as_ref(), &pool.pool_seed.to_le_bytes()],
        bump = pool.bump,
        constraint = pool.authority == authority.key() @ HarnsError::Unauthorized,
    )]
    pub pool: Account<'info, InsurancePool>,

    pub authority: Signer<'info>,
}}

pub fn handler(
    ctx: Context<UpdateRates>,
    new_rate_bps: u16,
) -> Result<()> {{
    require!(
        new_rate_bps > 0 && new_rate_bps <= 10000,
        HarnsError::InvalidRate
    );

    let pool = &mut ctx.accounts.pool;
    let clock = Clock::get()?;

    let old_rate = pool.base_rate_bps;
    pool.base_rate_bps = new_rate_bps;
    pool.last_updated = clock.unix_timestamp;

    emit!(RatesUpdated {{
        pool: pool.key(),
        old_rate_bps: old_rate,
        new_rate_bps,
        timestamp: clock.unix_timestamp,
    }});

    msg!("Rate updated: {{}} -> {{}} bps", old_rate, new_rate_bps);
    Ok(())
}}
"""


def gen_errors_rs():
    return """use anchor_lang::prelude::*;

#[error_code]
pub enum HarnsError {{
    #[msg("Insurance rate must be between 1 and 10000 basis points")]
    InvalidRate,

    #[msg("Premium amount is below minimum threshold")]
    PremiumTooLow,

    #[msg("Policy is not in active state")]
    PolicyNotActive,

    #[msg("Policy has expired and is no longer claimable")]
    PolicyExpired,

    #[msg("Caller is not authorized to perform this action")]
    Unauthorized,

    #[msg("Arithmetic overflow detected")]
    Overflow,

    #[msg("Insufficient pool balance for refund")]
    InsufficientBalance,

    #[msg("Transaction signature does not match policy")]
    SignatureMismatch,
}}
"""


def gen_events_rs():
    return """use anchor_lang::prelude::*;

#[event]
pub struct PoolInitialized {{
    pub pool: Pubkey,
    pub authority: Pubkey,
    pub base_rate_bps: u16,
    pub timestamp: i64,
}}

#[event]
pub struct PremiumDeposited {{
    pub pool: Pubkey,
    pub depositor: Pubkey,
    pub amount: u64,
    pub policy: Pubkey,
    pub timestamp: i64,
}}

#[event]
pub struct RefundProcessed {{
    pub pool: Pubkey,
    pub policy: Pubkey,
    pub recipient: Pubkey,
    pub amount: u64,
    pub timestamp: i64,
}}

#[event]
pub struct RatesUpdated {{
    pub pool: Pubkey,
    pub old_rate_bps: u16,
    pub new_rate_bps: u16,
    pub timestamp: i64,
}}
"""


def gen_utils_rs():
    return """use anchor_lang::prelude::*;

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
"""


def gen_math_rs():
    return """//! Fixed-point arithmetic helpers for premium calculations.
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
"""


def gen_validation_rs():
    return """//! Input validation helpers for instruction handlers.

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
"""


def gen_constants_rs():
    return """//! Protocol-wide constants.

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
"""


def gen_close_pool_rs():
    return """use anchor_lang::prelude::*;
use crate::state::InsurancePool;
use crate::events::PoolClosed;
use crate::errors::HarnsError;

#[derive(Accounts)]
pub struct ClosePool<'info> {{
    #[account(
        mut,
        close = authority,
        seeds = [b"insurance_pool", pool.authority.as_ref(), &pool.pool_seed.to_le_bytes()],
        bump = pool.bump,
        constraint = pool.authority == authority.key() @ HarnsError::Unauthorized,
        constraint = pool.active_policies == 0 @ HarnsError::PolicyNotActive,
    )]
    pub pool: Account<'info, InsurancePool>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}}

pub fn handler(ctx: Context<ClosePool>) -> Result<()> {{
    let pool = &ctx.accounts.pool;
    let clock = Clock::get()?;

    let remaining_balance = pool.to_account_info().lamports();

    emit!(PoolClosed {{
        pool: pool.key(),
        authority: ctx.accounts.authority.key(),
        remaining_balance,
        timestamp: clock.unix_timestamp,
    }});

    msg!(
        "Pool closed: {{}}, remaining balance: {{}} lamports returned to authority",
        pool.key(),
        remaining_balance
    );

    Ok(())
}}
"""


def gen_expire_policy_rs():
    return """use anchor_lang::prelude::*;
use crate::state::{{InsurancePool, Policy}};
use crate::errors::HarnsError;

#[derive(Accounts)]
pub struct ExpirePolicy<'info> {{
    #[account(
        mut,
        seeds = [b"insurance_pool", pool.authority.as_ref(), &pool.pool_seed.to_le_bytes()],
        bump = pool.bump,
    )]
    pub pool: Account<'info, InsurancePool>,

    #[account(
        mut,
        seeds = [b"policy", pool.key().as_ref(), policy.owner.as_ref(), &policy.tx_signature[..32]],
        bump = policy.bump,
        constraint = policy.status == 0 @ HarnsError::PolicyNotActive,
    )]
    pub policy: Account<'info, Policy>,

    pub authority: Signer<'info>,
}}

pub fn handler(ctx: Context<ExpirePolicy>) -> Result<()> {{
    let policy = &mut ctx.accounts.policy;
    let pool = &mut ctx.accounts.pool;
    let clock = Clock::get()?;

    require!(
        clock.unix_timestamp > policy.expires_at,
        HarnsError::PolicyNotActive
    );

    policy.status = 2; // expired
    pool.active_policies = pool.active_policies.checked_sub(1)
        .ok_or(HarnsError::Overflow)?;

    msg!(
        "Policy expired: {{}}, owner: {{}}",
        policy.key(),
        policy.owner
    );

    Ok(())
}}
"""


def gen_xfer_authority_rs():
    return """use anchor_lang::prelude::*;
use crate::state::InsurancePool;
use crate::errors::HarnsError;

#[derive(Accounts)]
pub struct TransferAuthority<'info> {{
    #[account(
        mut,
        seeds = [b"insurance_pool", pool.authority.as_ref(), &pool.pool_seed.to_le_bytes()],
        bump = pool.bump,
        constraint = pool.authority == current_authority.key() @ HarnsError::Unauthorized,
    )]
    pub pool: Account<'info, InsurancePool>,

    pub current_authority: Signer<'info>,

    /// CHECK: The new authority to transfer ownership to.
    pub new_authority: AccountInfo<'info>,
}}

pub fn handler(ctx: Context<TransferAuthority>) -> Result<()> {{
    let pool = &mut ctx.accounts.pool;
    let new_auth = ctx.accounts.new_authority.key();

    require!(
        new_auth != Pubkey::default(),
        HarnsError::Unauthorized
    );

    msg!(
        "Authority transfer: {{}} -> {{}}",
        pool.authority,
        new_auth
    );

    pool.authority = new_auth;
    let clock = Clock::get()?;
    pool.last_updated = clock.unix_timestamp;

    Ok(())
}}
"""


def gen_sdk_utils_ts():
    return """import { PublicKey } from "@solana/web3.js";
import { BN } from "@coral-xyz/anchor";
import { LAMPORTS_PER_SOL, MIN_PREMIUM_LAMPORTS, MAX_RATE_BPS } from "./constants";

/**
 * Convert lamports to SOL.
 */
export function lamportsToSol(lamports: BN): number {{
  return lamports.toNumber() / LAMPORTS_PER_SOL;
}}

/**
 * Convert SOL to lamports.
 */
export function solToLamports(sol: number): BN {{
  return new BN(Math.round(sol * LAMPORTS_PER_SOL));
}}

/**
 * Format a PublicKey as a truncated display string.
 */
export function shortenAddress(address: PublicKey, chars: number = 4): string {{
  const str = address.toBase58();
  return str.slice(0, chars) + "..." + str.slice(-chars);
}}

/**
 * Check if a rate is within valid bounds.
 */
export function isValidRate(rateBps: number): boolean {{
  return rateBps > 0 && rateBps <= MAX_RATE_BPS;
}}

/**
 * Check if a premium meets the minimum threshold.
 */
export function isValidPremium(lamports: number): boolean {{
  return lamports >= MIN_PREMIUM_LAMPORTS;
}}

/**
 * Sleep for the given number of milliseconds.
 */
export function sleep(ms: number): Promise<void> {{
  return new Promise((resolve) => setTimeout(resolve, ms));
}}

/**
 * Retry a function with exponential backoff.
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {{
  let lastError: Error | undefined;
  for (let i = 0; i < maxRetries; i++) {{
    try {{
      return await fn();
    }} catch (err) {{
      lastError = err as Error;
      if (i < maxRetries - 1) {{
        await sleep(baseDelay * Math.pow(2, i));
      }}
    }}
  }}
  throw lastError;
}}
"""


def gen_sdk_errors_ts():
    return """/**
 * Error codes matching the on-chain HarnsError enum.
 * Offset by 6000 as per Anchor convention.
 */
export enum HarnsErrorCode {{
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
}}

const ERROR_MESSAGES: Record<number, string> = {{
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
}};

/**
 * Parse an Anchor error code into a human-readable message.
 */
export function parseHarnsError(code: number): string {{
  return ERROR_MESSAGES[code] ?? "Unknown error: " + code;
}}

/**
 * Check if an error is a known Harns protocol error.
 */
export function isHarnsError(err: unknown): boolean {{
  if (typeof err === "object" && err !== null && "code" in err) {{
    const code = (err as {{ code: number }}).code;
    return code >= 6000 && code <= 6009;
  }}
  return false;
}}
"""


def gen_integration_test_rs():
    return """//! Integration test stubs for the Harns protocol.
//!
//! These tests verify the program logic in a simulated environment.
//! Run with: cargo test --manifest-path programs/harns/Cargo.toml

#[cfg(test)]
mod tests {{

    #[test]
    fn test_pool_space_calculation() {{
        // InsurancePool::SPACE should account for discriminator
        let expected = 8 + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 1 + 63;
        assert_eq!(expected, 151);
    }}

    #[test]
    fn test_policy_space_calculation() {{
        let expected = 8 + 32 + 32 + 8 + 64 + 1 + 8 + 8 + 1;
        assert_eq!(expected, 162);
    }}

    #[test]
    fn test_refund_record_space() {{
        let expected = 8 + 32 + 32 + 8 + 8 + 1;
        assert_eq!(expected, 89);
    }}

    #[test]
    fn test_min_premium_constant() {{
        assert_eq!(crate::constants::MIN_PREMIUM_LAMPORTS, 5_000);
    }}

    #[test]
    fn test_default_rate() {{
        assert_eq!(crate::constants::DEFAULT_RATE_BPS, 250);
    }}

    #[test]
    fn test_policy_ttl() {{
        assert_eq!(crate::constants::POLICY_TTL_SECONDS, 300);
    }}

    #[test]
    fn test_max_rate_bound() {{
        assert_eq!(crate::constants::MAX_RATE_BPS, 10_000);
    }}

    #[test]
    fn test_pool_seed_prefix() {{
        assert_eq!(crate::constants::POOL_SEED, b"insurance_pool");
    }}

    #[test]
    fn test_policy_seed_prefix() {{
        assert_eq!(crate::constants::POLICY_SEED, b"policy");
    }}

    #[test]
    fn test_refund_seed_prefix() {{
        assert_eq!(crate::constants::REFUND_SEED, b"refund");
    }}

    #[test]
    fn test_lamports_per_sol() {{
        assert_eq!(crate::constants::LAMPORTS_PER_SOL, 1_000_000_000);
    }}

    #[test]
    fn test_bps_denominator() {{
        assert_eq!(crate::constants::BPS_DENOMINATOR, 10_000);
    }}

    #[test]
    fn test_min_pool_reserve() {{
        assert_eq!(crate::constants::MIN_POOL_RESERVE, 10_000_000);
    }}

    #[test]
    fn test_total_space_under_10k() {{
        // Solana accounts should generally be under 10KB
        let pool_space = 151usize;
        let policy_space = 162usize;
        let refund_space = 89usize;
        assert!(pool_space < 10_240);
        assert!(policy_space < 10_240);
        assert!(refund_space < 10_240);
    }}

    #[test]
    fn test_space_alignment() {{
        // Verify space values are reasonable (no accidental large allocations)
        let pool = 151usize;
        let policy = 162usize;
        let refund = 89usize;
        assert!(pool > 8, "Pool must be larger than discriminator");
        assert!(policy > 8, "Policy must be larger than discriminator");
        assert!(refund > 8, "Refund must be larger than discriminator");
        assert!(pool < 1024, "Pool should fit in reasonable space");
        assert!(policy < 1024, "Policy should fit in reasonable space");
        assert!(refund < 512, "Refund should fit in reasonable space");
    }}

    #[test]
    fn test_rate_bounds_consistency() {{
        let max = crate::constants::MAX_RATE_BPS;
        let default = crate::constants::DEFAULT_RATE_BPS;
        assert!(default > 0);
        assert!(default < max);
        assert_eq!(max, 10_000);
    }}

    #[test]
    fn test_premium_min_is_positive() {{
        let min = crate::constants::MIN_PREMIUM_LAMPORTS;
        assert!(min > 0, "Minimum premium must be positive");
        assert!(min < crate::constants::LAMPORTS_PER_SOL, "Min premium should be less than 1 SOL");
    }}

    #[test]
    fn test_policy_ttl_reasonable() {{
        let ttl = crate::constants::POLICY_TTL_SECONDS;
        assert!(ttl >= 60, "TTL should be at least 1 minute");
        assert!(ttl <= 3600, "TTL should be at most 1 hour");
    }}
}}
"""


def gen_anchor_build_rs():
    return """//! Build script for the Harns Anchor program.
//! This is a no-op build script required by some Anchor setups.

fn main() {{
    // Anchor programs may need a build.rs for IDL generation.
    // This file intentionally left minimal.
    println!("cargo:rerun-if-changed=src/");
}}
"""


def gen_sdk_package_json():
    return """{
  "name": "@harns-labs/sdk",
  "version": "0.4.2",
  "description": "TypeScript SDK for the Harns insurance protocol on Solana",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "test": "jest",
    "lint": "eslint src/ --ext .ts"
  },
  "dependencies": {
    "@coral-xyz/anchor": "^0.29.0",
    "@solana/web3.js": "^1.87.0",
    "bs58": "^5.0.0"
  },
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "@types/node": "^20.0.0",
    "jest": "^29.7.0",
    "ts-jest": "^29.1.0",
    "typescript": "^5.3.0"
  },
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/harns-labs/harns-core.git"
  }
}
"""


def gen_tsconfig():
    return """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "commonjs",
    "lib": ["ES2020"],
    "declaration": true,
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
"""


def gen_jest_config():
    return """module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/tests"],
  testMatch: ["**/*.test.ts"],
  moduleFileExtensions: ["ts", "js", "json"],
  collectCoverageFrom: ["src/**/*.ts"],
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov"],
};
"""


def gen_sdk_index_ts():
    return """export { HarnsClient } from "./client";
export { HARNS_PROGRAM_ID, INSURANCE_POOL_SEED, POLICY_SEED, REFUND_SEED } from "./constants";
export type {
  InsurancePool,
  Policy,
  RefundRecord,
  DepositPremiumParams,
  ProcessRefundParams,
  HarnsConfig,
} from "./types";
export { lamportsToSol, solToLamports, shortenAddress, isValidRate, isValidPremium, retry } from "./utils";
export { HarnsErrorCode, parseHarnsError, isHarnsError } from "./errors";
"""


def gen_sdk_client_ts():
    return """import { Connection, PublicKey, Transaction, SystemProgram, Keypair } from "@solana/web3.js";
import { Program, AnchorProvider, BN, Idl } from "@coral-xyz/anchor";
import {
  HARNS_PROGRAM_ID,
  INSURANCE_POOL_SEED,
  POLICY_SEED,
  REFUND_SEED,
  MIN_PREMIUM_LAMPORTS,
} from "./constants";
import { InsurancePool, Policy, DepositPremiumParams, ProcessRefundParams, HarnsConfig } from "./types";

export class HarnsClient {
  private connection: Connection;
  private programId: PublicKey;

  constructor(config: HarnsConfig) {
    this.connection = new Connection(config.rpcUrl, "confirmed");
    this.programId = config.programId ?? new PublicKey(HARNS_PROGRAM_ID);
  }

  /**
   * Derive the insurance pool PDA address.
   */
  async findPoolAddress(authority: PublicKey, poolSeed: BN): Promise<[PublicKey, number]> {
    return PublicKey.findProgramAddressSync(
      [
        Buffer.from(INSURANCE_POOL_SEED),
        authority.toBuffer(),
        poolSeed.toArrayLike(Buffer, "le", 8),
      ],
      this.programId
    );
  }

  /**
   * Derive the policy PDA address.
   */
  async findPolicyAddress(
    pool: PublicKey,
    depositor: PublicKey,
    txSignature: Uint8Array
  ): Promise<[PublicKey, number]> {
    return PublicKey.findProgramAddressSync(
      [
        Buffer.from(POLICY_SEED),
        pool.toBuffer(),
        depositor.toBuffer(),
        txSignature.slice(0, 32),
      ],
      this.programId
    );
  }

  /**
   * Derive the refund record PDA address.
   */
  async findRefundAddress(policy: PublicKey): Promise<[PublicKey, number]> {
    return PublicKey.findProgramAddressSync(
      [Buffer.from(REFUND_SEED), policy.toBuffer()],
      this.programId
    );
  }

  /**
   * Fetch an insurance pool account.
   */
  async getPool(poolAddress: PublicKey): Promise<InsurancePool | null> {
    const info = await this.connection.getAccountInfo(poolAddress);
    if (!info) return null;

    const data = info.data;
    const offset = 8; // skip discriminator

    return {
      authority: new PublicKey(data.subarray(offset, offset + 32)),
      poolSeed: new BN(data.subarray(offset + 32, offset + 40), "le"),
      totalPremiums: new BN(data.subarray(offset + 40, offset + 48), "le"),
      totalRefunds: new BN(data.subarray(offset + 48, offset + 56), "le"),
      activePolicies: data.readUInt32LE(offset + 56),
      baseRateBps: data.readUInt16LE(offset + 60),
      createdAt: new BN(data.subarray(offset + 62, offset + 70), "le"),
      lastUpdated: new BN(data.subarray(offset + 70, offset + 78), "le"),
      bump: data[offset + 78],
    };
  }

  /**
   * Fetch a policy account.
   */
  async getPolicy(policyAddress: PublicKey): Promise<Policy | null> {
    const info = await this.connection.getAccountInfo(policyAddress);
    if (!info) return null;

    const data = info.data;
    const offset = 8;

    return {
      owner: new PublicKey(data.subarray(offset, offset + 32)),
      pool: new PublicKey(data.subarray(offset + 32, offset + 64)),
      premiumAmount: new BN(data.subarray(offset + 64, offset + 72), "le"),
      txSignature: new Uint8Array(data.subarray(offset + 72, offset + 136)),
      status: data[offset + 136],
      createdAt: new BN(data.subarray(offset + 137, offset + 145), "le"),
      expiresAt: new BN(data.subarray(offset + 145, offset + 153), "le"),
      bump: data[offset + 153],
    };
  }

  /**
   * Calculate the premium for a given transaction fee.
   */
  calculatePremium(txFeeLamports: number, rateBps: number): number {
    const premium = Math.ceil((txFeeLamports * rateBps) / 10000);
    return Math.max(premium, MIN_PREMIUM_LAMPORTS);
  }

  /**
   * Get connection instance for advanced usage.
   */
  getConnection(): Connection {
    return this.connection;
  }

  /**
   * Get the program ID.
   */
  getProgramId(): PublicKey {
    return this.programId;
  }
}
"""


def gen_sdk_types_ts():
    return """import { PublicKey } from "@solana/web3.js";
import { BN } from "@coral-xyz/anchor";

export interface InsurancePool {
  authority: PublicKey;
  poolSeed: BN;
  totalPremiums: BN;
  totalRefunds: BN;
  activePolicies: number;
  baseRateBps: number;
  createdAt: BN;
  lastUpdated: BN;
  bump: number;
}

export interface Policy {
  owner: PublicKey;
  pool: PublicKey;
  premiumAmount: BN;
  txSignature: Uint8Array;
  status: number;
  createdAt: BN;
  expiresAt: BN;
  bump: number;
}

export interface RefundRecord {
  policy: PublicKey;
  recipient: PublicKey;
  amount: BN;
  refundedAt: BN;
  bump: number;
}

export interface DepositPremiumParams {
  poolAddress: PublicKey;
  amount: BN;
  txSignature: Uint8Array;
}

export interface ProcessRefundParams {
  poolAddress: PublicKey;
  policyAddress: PublicKey;
  txSignature: Uint8Array;
  claimant: PublicKey;
}

export interface HarnsConfig {
  rpcUrl: string;
  programId?: PublicKey;
  commitment?: string;
}

export enum PolicyStatus {
  Active = 0,
  Claimed = 1,
  Expired = 2,
}
"""


def gen_sdk_constants_ts():
    return """export const HARNS_PROGRAM_ID = "HRNs8jz4nnFSCmj3G7pWLrTBLhzGkXXbVnPJg2Cv9t7";

export const INSURANCE_POOL_SEED = "insurance_pool";
export const POLICY_SEED = "policy";
export const REFUND_SEED = "refund";

export const MIN_PREMIUM_LAMPORTS = 5_000;
export const POLICY_TTL_SECONDS = 300;
export const MAX_RATE_BPS = 10_000;
export const DEFAULT_RATE_BPS = 250;

export const LAMPORTS_PER_SOL = 1_000_000_000;
"""


def gen_client_test_ts():
    return """import { PublicKey } from "@solana/web3.js";
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
"""


def gen_deploy_sh():
    return """#!/usr/bin/env bash
set -euo pipefail

CLUSTER="${1:-devnet}"
PROGRAM_NAME="harns"
DEPLOY_KEYPAIR="${DEPLOY_KEYPAIR:-$HOME/.config/solana/id.json}"

echo "========================================="
echo " Harns Protocol -- Deploy"
echo " Cluster: $CLUSTER"
echo "========================================="

if ! command -v anchor &> /dev/null; then
    echo "Error: anchor CLI not found. Install with: cargo install --git https://github.com/coral-xyz/anchor avm --locked"
    exit 1
fi

if ! command -v solana &> /dev/null; then
    echo "Error: solana CLI not found."
    exit 1
fi

solana config set --url "$CLUSTER" --keypair "$DEPLOY_KEYPAIR"
echo "Solana config set to $CLUSTER"

echo "Building program..."
anchor build

echo "Deploying $PROGRAM_NAME to $CLUSTER..."
anchor deploy --provider.cluster "$CLUSTER"

PROGRAM_ID=$(solana address -k target/deploy/${PROGRAM_NAME}-keypair.json)
echo "Deployed program ID: $PROGRAM_ID"

echo "========================================="
echo " Deployment complete"
echo "========================================="
"""


def gen_test_sh():
    return """#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo " Harns Protocol -- Test Suite"
echo "========================================="

echo "[1/3] Building Anchor program..."
anchor build

echo "[2/3] Running Anchor tests..."
anchor test --skip-local-validator 2>&1 || {
    echo "Anchor tests failed."
    exit 1
}

echo "[3/3] Running SDK tests..."
cd sdk
npm install --silent
npm test 2>&1 || {
    echo "SDK tests failed."
    exit 1
}

echo "========================================="
echo " All tests passed"
echo "========================================="
"""


def gen_ci_yml():
    return """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  SOLANA_VERSION: "1.17.0"
  ANCHOR_VERSION: "0.29.0"
  NODE_VERSION: "18"
  RUST_TOOLCHAIN: "stable"

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          toolchain: ${{ env.RUST_TOOLCHAIN }}

      - name: Cache Cargo
        uses: actions/cache@v3
        with:
          path: |
            ~/.cargo/bin/
            ~/.cargo/registry/index/
            ~/.cargo/registry/cache/
            ~/.cargo/git/db/
            target/
          key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}

      - name: Install Solana
        run: |
          sh -c "$(curl -sSfL https://release.solana.com/v${{ env.SOLANA_VERSION }}/install)"
          echo "$HOME/.local/share/solana/install/active_release/bin" >> $GITHUB_PATH

      - name: Install Anchor
        run: |
          cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
          avm install ${{ env.ANCHOR_VERSION }}
          avm use ${{ env.ANCHOR_VERSION }}

      - name: Build program
        run: anchor build

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: "npm"
          cache-dependency-path: sdk/package-lock.json

      - name: Install SDK dependencies
        run: cd sdk && npm ci

      - name: Run SDK tests
        run: cd sdk && npm test

      - name: Lint SDK
        run: cd sdk && npm run lint --if-present

  check-format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy

      - name: Check formatting
        run: cargo fmt --manifest-path programs/harns/Cargo.toml -- --check

      - name: Run clippy
        run: cargo clippy --manifest-path programs/harns/Cargo.toml -- -D warnings
"""


def gen_license():
    return """MIT License

Copyright (c) 2025 Harns Protocol

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


def gen_gitignore():
    return """# Build
target/
dist/
node_modules/
coverage/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Solana
test-ledger/
.anchor/

# Environment
.env
.env.local
*.pem
*.json.bak
"""


def gen_anchor_toml():
    return f"""[features]
seeds = false
skip-lint = false

[programs.devnet]
{PROJECT_NAME} = "HRNs8jz4nnFSCmj3G7pWLrTBLhzGkXXbVnPJg2Cv9t7"

[registry]
url = "https://api.apr.dev"

[provider]
cluster = "devnet"
wallet = "~/.config/solana/id.json"

[scripts]
test = "npx ts-mocha -p ./tsconfig.json -t 1000000 tests/**/*.ts"
"""


def gen_readme():
    return f"""<p align="center">
  <img src="banner.png" alt="Harns Protocol" width="100%" />
</p>

<p align="center">
  <a href="https://x.com/harns_fun">
    <img src="https://img.shields.io/badge/Twitter-000000?style=for-the-badge&logo=x&logoColor=white" alt="Twitter" />
  </a>
  <a href="https://harns.fun">
    <img src="https://img.shields.io/badge/Website-4A90D9?style=for-the-badge&logo=google-chrome&logoColor=white" alt="Website" />
  </a>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Solana-1.17-purple?style=for-the-badge&logo=solana" alt="Solana" />
  <img src="https://img.shields.io/badge/Anchor-0.29-blue?style=for-the-badge" alt="Anchor" />
</p>

---

TX failure insurance protocol for Solana. Never lose a fee again.

Harns provides escrow-based premium pools with an automatic refund engine. When a transaction fails on-chain, the protocol detects the failure via webhooks and returns the insured premium to the user within seconds.

## Architecture

```mermaid
graph TB
    User[User/DEX] -->|Submit TX + Premium| Extension[Chrome Extension]
    Extension -->|Deposit Premium| Pool[Insurance Pool]
    Extension -->|Execute TX| RPC[Solana RPC]
    RPC -->|TX Status| Webhook[Helius Webhook]
    Webhook -->|Success| Pool
    Webhook -->|Failure| Refund[Refund Engine]
    Refund -->|Auto Refund| User
    Pool -->|Quarterly| Buyback[$HARNS Buyback & Burn]
```

## Features

| Feature | Description |
|---------|-------------|
| Escrow Pool | Premiums are held in an on-chain PDA-controlled pool |
| Auto Refund | Failed transactions trigger automatic refunds via webhook |
| Rate Engine | Dynamic premium rates adjustable by pool authority |
| Policy TTL | Each policy has a 5-minute time-to-live window |
| Buyback | Quarterly buyback-and-burn of $HARNS from pool profits |

## Project Structure

```
programs/harns/src/
  lib.rs                  -- Program entrypoint and instruction dispatch
  state.rs                -- Account state definitions (InsurancePool, Policy, RefundRecord)
  errors.rs               -- Custom error codes
  events.rs               -- Event structs for logging
  instructions/
    initialize.rs         -- Pool initialization
    deposit_premium.rs    -- Premium deposit and policy creation
    process_refund.rs     -- Refund processing for failed transactions
    update_rates.rs       -- Premium rate updates

sdk/src/
  client.ts               -- HarnsClient class with PDA derivation
  types.ts                -- TypeScript type definitions
  constants.ts            -- Program constants and seeds
```

## Installation

```bash
git clone https://github.com/harns-labs/harns-core.git
cd harns
```

### Build the program

```bash
anchor build
```

### Run SDK tests

```bash
cd sdk
npm install
npm test
```

## Usage

```typescript
import {{ HarnsClient }} from "@harns-labs/sdk";
import {{ PublicKey }} from "@solana/web3.js";
import {{ BN }} from "@coral-xyz/anchor";

const client = new HarnsClient({{
  rpcUrl: "https://api.devnet.solana.com",
}});

// Derive pool address
const authority = new PublicKey("...");
const [poolAddress] = await client.findPoolAddress(authority, new BN(1));

// Fetch pool state
const pool = await client.getPool(poolAddress);
console.log("Active policies:", pool?.activePolicies);
console.log("Total premiums:", pool?.totalPremiums.toString());

// Calculate premium for a 5000 lamport tx fee at 2.5% rate
const premium = client.calculatePremium(5000, 250);
console.log("Premium:", premium, "lamports");
```

## Token Utility

| Mechanism | Description |
|-----------|-------------|
| Buyback & Burn | Quarterly pool profits used to buy and burn $HARNS |
| Fee Discount | $HARNS holders receive reduced premium rates |
| Governance | Token holders vote on rate adjustments and pool parameters |
| Staking | Stake $HARNS to earn a share of protocol revenue |

## License

MIT
"""


def gen_anchor_workspace_cargo_toml():
    return """[workspace]
members = [
    "programs/*"
]

[profile.release]
overflow-checks = true
lto = "fat"
codegen-units = 1

[profile.release.build-override]
opt-level = 3
incremental = false
codegen-units = 1
"""


def gen_rustfmt_toml():
    return """max_width = 100
tab_spaces = 4
edition = "2021"
"""


# ============================================================
# COMMIT PLAN: ordered sequence of (phase, files, message_template)
# ============================================================

def build_commit_phases():
    """Returns a list of (files_dict, message) pairs representing logical project phases."""
    phases = []

    # Phase 1: Initial scaffold
    phases.append(({
        ".gitignore": gen_gitignore,
        "LICENSE": gen_license,
    }, "initial project scaffold"))

    phases.append(({
        "Cargo.toml": gen_anchor_workspace_cargo_toml,
        "Anchor.toml": gen_anchor_toml,
    }, "add anchor workspace config"))

    phases.append(({
        "programs/harns/Cargo.toml": gen_cargo_toml,
    }, "configure harns program crate"))

    # Phase 2: Core program files
    phases.append(({
        "programs/harns/src/lib.rs": gen_lib_rs,
    }, "scaffold program entrypoint"))

    phases.append(({
        "programs/harns/src/errors.rs": gen_errors_rs,
    }, "define error codes"))

    phases.append(({
        "programs/harns/src/events.rs": gen_events_rs,
    }, "add event structs for logging"))

    phases.append(({
        "programs/harns/src/state.rs": gen_state_rs,
    }, "define account state structs"))

    phases.append(({
        "programs/harns/src/instructions/mod.rs": gen_instructions_mod_rs,
    }, "add instructions module"))

    phases.append(({
        "programs/harns/src/instructions/initialize.rs": gen_initialize_rs,
    }, "implement pool initialization"))

    phases.append(({
        "programs/harns/src/instructions/deposit_premium.rs": gen_deposit_premium_rs,
    }, "implement premium deposit flow"))

    phases.append(({
        "programs/harns/src/instructions/process_refund.rs": gen_process_refund_rs,
    }, "implement refund processing"))

    phases.append(({
        "programs/harns/src/instructions/update_rates.rs": gen_update_rates_rs,
    }, "implement rate update instruction"))

    phases.append(({
        "programs/harns/src/instructions/close_pool.rs": gen_close_pool_rs,
    }, "implement pool close instruction"))

    phases.append(({
        "programs/harns/src/instructions/expire_policy.rs": gen_expire_policy_rs,
    }, "implement policy expiration handler"))

    phases.append(({
        "programs/harns/src/instructions/transfer_authority.rs": gen_xfer_authority_rs,
    }, "implement authority transfer instruction"))

    phases.append(({
        "programs/harns/src/constants.rs": gen_constants_rs,
    }, "extract protocol constants to module"))

    phases.append(({
        "programs/harns/src/utils.rs": gen_utils_rs,
    }, "add PDA seed and arithmetic utility functions"))

    phases.append(({
        "programs/harns/src/math.rs": gen_math_rs,
    }, "add fixed-point math helpers for premium calculations"))

    phases.append(({
        "programs/harns/src/validation.rs": gen_validation_rs,
    }, "add input validation helpers"))

    phases.append(({
        "programs/harns/src/integration_tests.rs": gen_integration_test_rs,
    }, "add integration test stubs"))

    phases.append(({
        "programs/harns/build.rs": gen_anchor_build_rs,
    }, "add build script for anchor IDL generation"))

    # Phase 3: SDK
    phases.append(({
        "sdk/package.json": gen_sdk_package_json,
        "sdk/tsconfig.json": gen_tsconfig,
    }, "initialize sdk package"))

    phases.append(({
        "sdk/jest.config.js": gen_jest_config,
    }, "configure jest for sdk tests"))

    phases.append(({
        "sdk/src/constants.ts": gen_sdk_constants_ts,
    }, "add program constants and seeds"))

    phases.append(({
        "sdk/src/types.ts": gen_sdk_types_ts,
    }, "define typescript type interfaces"))

    phases.append(({
        "sdk/src/client.ts": gen_sdk_client_ts,
    }, "implement HarnsClient with PDA derivation"))

    phases.append(({
        "sdk/src/index.ts": gen_sdk_index_ts,
    }, "add sdk entrypoint exports"))

    phases.append(({
        "sdk/src/utils.ts": gen_sdk_utils_ts,
    }, "add sdk utility functions"))

    phases.append(({
        "sdk/src/errors.ts": gen_sdk_errors_ts,
    }, "add sdk error code mappings"))

    phases.append(({
        "sdk/tests/client.test.ts": gen_client_test_ts,
    }, "add client unit tests"))

    # Phase 4: Scripts and CI
    phases.append(({
        "scripts/deploy.sh": gen_deploy_sh,
        "scripts/test.sh": gen_test_sh,
    }, "add deploy and test scripts"))

    phases.append(({
        ".github/workflows/ci.yml": gen_ci_yml,
    }, "configure github actions ci pipeline"))

    phases.append(({
        "rustfmt.toml": gen_rustfmt_toml,
    }, "add rustfmt config"))

    # Phase 5: README and banner
    phases.append(({
        "README.md": gen_readme,
    }, "add project readme with architecture docs"))

    return phases


# ============================================================
# INCREMENTAL CHANGE GENERATORS (for filling extra commits)
# ============================================================

MICRO_CHANGES = []

def _register_micro(fn):
    MICRO_CHANGES.append(fn)
    return fn

@_register_micro
def mc_bump_version_comment():
    return ("programs/harns/src/lib.rs", "add version comment to lib.rs",
            lambda c: c.replace(
                'use anchor_lang::prelude::*;',
                '// Harns Protocol v0.4.2\nuse anchor_lang::prelude::*;'
            ) if '// Harns Protocol v0.4.2' not in c else None)

@_register_micro
def mc_add_pool_util_method():
    return ("programs/harns/src/state.rs", "add utilization ratio helper to InsurancePool",
            lambda c: c.replace(
                '    /// Reserved for future use\n    pub _padding: [u8; 64],',
                '    /// Reserved for future use\n    pub _padding: [u8; 64],\n'
            ) if c.count('_padding') == 1 else None)

@_register_micro
def mc_add_log_to_initialize():
    return ("programs/harns/src/instructions/initialize.rs",
            "add detailed log to pool initialization",
            lambda c: c.replace(
                '    msg!("Insurance pool initialized: {{}}", pool.key());',
                '    msg!("Insurance pool initialized: {{}}, rate: {{}} bps", pool.key(), base_rate_bps);'
            ) if 'rate: {{}} bps' not in c else None)

@_register_micro
def mc_add_max_premium_const():
    return ("sdk/src/constants.ts", "add max premium constant",
            lambda c: c + '\nexport const MAX_PREMIUM_LAMPORTS = 10_000_000_000;\n'
            if 'MAX_PREMIUM_LAMPORTS' not in c else None)

@_register_micro
def mc_add_version_to_constants():
    return ("sdk/src/constants.ts", "add protocol version to constants",
            lambda c: c + f'\nexport const PROTOCOL_VERSION = "{VERSION}";\n'
            if 'PROTOCOL_VERSION' not in c else None)

@_register_micro
def mc_add_policy_status_comment():
    return ("programs/harns/src/state.rs", "clarify policy status enum values",
            lambda c: c.replace(
                '    /// Policy status: 0=active, 1=claimed, 2=expired',
                '    /// Policy status: 0=Active, 1=Claimed, 2=Expired'
            ) if '0=active' in c else None)

@_register_micro
def mc_add_get_pool_or_throw():
    return ("sdk/src/client.ts", "add getPoolOrThrow convenience method",
            lambda c: c.replace(
                '  /**\n   * Get the program ID.\n   */\n  getProgramId(): PublicKey {',
                '  /**\n   * Fetch pool or throw if not found.\n   */\n  async getPoolOrThrow(poolAddress: PublicKey) {\n    const pool = await this.getPool(poolAddress);\n    if (!pool) throw new Error("Pool not found: " + poolAddress.toBase58());\n    return pool;\n  }\n\n  /**\n   * Get the program ID.\n   */\n  getProgramId(): PublicKey {'
            ) if 'getPoolOrThrow' not in c else None)

@_register_micro
def mc_add_policy_expired_check():
    return ("sdk/src/types.ts", "add PolicyStatus helper comment",
            lambda c: c.replace(
                'export enum PolicyStatus {',
                '/** Represents the lifecycle state of an insurance policy. */\nexport enum PolicyStatus {'
            ) if 'lifecycle state' not in c else None)

@_register_micro
def mc_tweak_deploy_echo():
    return ("scripts/deploy.sh", "improve deploy script output formatting",
            lambda c: c.replace(
                'echo "Deploying $PROGRAM_NAME to $CLUSTER..."',
                'echo ""\necho "Deploying $PROGRAM_NAME to $CLUSTER..."'
            ) if 'echo ""\necho "Deploying' not in c else None)

@_register_micro
def mc_add_test_sh_timer():
    return ("scripts/test.sh", "add timing info to test script",
            lambda c: c.replace(
                'echo " Harns Protocol -- Test Suite"',
                'echo " Harns Protocol -- Test Suite"\necho " Started at: $(date)"'
            ) if 'Started at' not in c else None)

@_register_micro
def mc_add_overflow_comment():
    return ("programs/harns/src/instructions/deposit_premium.rs",
            "add safety comment for overflow checks",
            lambda c: c.replace(
                '    // Update pool state',
                '    // Update pool state -- checked arithmetic prevents overflow'
            ) if 'checked arithmetic' not in c else None)

@_register_micro
def mc_add_refund_log_detail():
    return ("programs/harns/src/instructions/process_refund.rs",
            "add policy key to refund log message",
            lambda c: c.replace(
                '    msg!("Refund processed: {{}} lamports to {{}}", refund_amount, ctx.accounts.claimant.key());',
                '    msg!("Refund processed: {{}} lamports to {{}} (policy: {{}})", refund_amount, ctx.accounts.claimant.key(), policy.key());'
            ) if 'policy: {{}}' not in c else None)

@_register_micro
def mc_ci_add_concurrency():
    return (".github/workflows/ci.yml", "add concurrency group to ci workflow",
            lambda c: c.replace(
                'env:',
                'concurrency:\n  group: ci-${{ github.ref }}\n  cancel-in-progress: true\n\nenv:'
            ) if 'concurrency:' not in c else None)

@_register_micro
def mc_add_anchor_toml_test_validator():
    return ("Anchor.toml", "add test validator config to Anchor.toml",
            lambda c: c + '\n[test.validator]\nurl = "https://api.devnet.solana.com"\n'
            if '[test.validator]' not in c else None)

@_register_micro
def mc_add_cargo_profile_dev():
    return ("Cargo.toml", "add dev profile config for faster builds",
            lambda c: c + '\n[profile.dev]\nopt-level = 0\ndebug = true\n'
            if '[profile.dev]' not in c else None)

@_register_micro
def mc_add_rate_validation_log():
    return ("programs/harns/src/instructions/update_rates.rs",
            "log old and new rate in update handler",
            lambda c: c.replace(
                '    let old_rate = pool.base_rate_bps;',
                '    let old_rate = pool.base_rate_bps;\n    // Log transition for debugging'
            ) if '// Log transition' not in c else None)

@_register_micro
def mc_add_getpolicy_or_throw():
    return ("sdk/src/client.ts", "add getPolicyOrThrow method",
            lambda c: c.replace(
                '  /**\n   * Calculate the premium for a given transaction fee.\n   */',
                '  /**\n   * Fetch policy or throw if not found.\n   */\n  async getPolicyOrThrow(policyAddress: PublicKey) {\n    const policy = await this.getPolicy(policyAddress);\n    if (!policy) throw new Error("Policy not found: " + policyAddress.toBase58());\n    return policy;\n  }\n\n  /**\n   * Calculate the premium for a given transaction fee.\n   */'
            ) if 'getPolicyOrThrow' not in c else None)

@_register_micro
def mc_add_is_active_check():
    return ("sdk/src/types.ts", "add isActive utility to PolicyStatus enum",
            lambda c: c + '\nexport function isPolicyActive(status: number): boolean {\n  return status === PolicyStatus.Active;\n}\n'
            if 'isPolicyActive' not in c else None)

@_register_micro
def mc_add_ci_build_sdk():
    return (".github/workflows/ci.yml", "add sdk build step to ci",
            lambda c: c.replace(
                '      - name: Run SDK tests',
                '      - name: Build SDK\n        run: cd sdk && npm run build --if-present\n\n      - name: Run SDK tests'
            ) if 'Build SDK' not in c else None)

@_register_micro
def mc_add_error_invalid_pool():
    return ("programs/harns/src/errors.rs", "add InvalidPool error variant",
            lambda c: c.replace(
                '    #[msg("Transaction signature does not match policy")]\n    SignatureMismatch,',
                '    #[msg("Transaction signature does not match policy")]\n    SignatureMismatch,\n\n    #[msg("Pool account data is invalid or corrupted")]\n    InvalidPool,'
            ) if 'InvalidPool' not in c else None)

@_register_micro
def mc_add_event_pool_closed():
    return ("programs/harns/src/events.rs", "add PoolClosed event struct",
            lambda c: c + '\n#[event]\npub struct PoolClosed {\n    pub pool: Pubkey,\n    pub authority: Pubkey,\n    pub remaining_balance: u64,\n    pub timestamp: i64,\n}\n'
            if 'PoolClosed' not in c else None)

@_register_micro
def mc_add_mod_comment():
    return ("programs/harns/src/instructions/mod.rs", "add module-level doc comment",
            lambda c: '//! Instruction handlers for the Harns insurance protocol.\n\n' + c
            if '//! Instruction handlers' not in c else None)

@_register_micro
def mc_add_test_calculate_high_rate():
    return ("sdk/tests/client.test.ts", "add test for high rate premium calculation",
            lambda c: c.replace(
                '    it("should handle zero rate gracefully", () => {',
                '    it("should handle max rate (100%)", () => {\n      const fee = 100_000;\n      const rate = 10_000;\n      const premium = client.calculatePremium(fee, rate);\n      expect(premium).toBe(100_000);\n    });\n\n    it("should handle zero rate gracefully", () => {'
            ) if 'handle max rate' not in c else None)

@_register_micro
def mc_add_test_pool_different_authority():
    return ("sdk/tests/client.test.ts", "add test for different authorities producing different PDAs",
            lambda c: c.replace(
                '  describe("findPolicyAddress',
                '    it("should produce different addresses for different authorities", async () => {\n      const auth1 = PublicKey.unique();\n      const auth2 = PublicKey.unique();\n      const seed = new BN(1);\n\n      const [addr1] = await client.findPoolAddress(auth1, seed);\n      const [addr2] = await client.findPoolAddress(auth2, seed);\n\n      expect(addr1.toBase58()).not.toBe(addr2.toBase58());\n    });\n  });\n\n  describe("findPolicyAddress'
            ) if 'different authorities' not in c else None)

@_register_micro
def mc_add_deploy_check_balance():
    return ("scripts/deploy.sh", "add balance check before deploy",
            lambda c: c.replace(
                'echo "Building program..."',
                'echo "Checking deployer balance..."\nsolana balance\n\necho "Building program..."'
            ) if 'Checking deployer balance' not in c else None)

@_register_micro
def mc_add_error_pool_paused():
    return ("programs/harns/src/errors.rs", "add PoolPaused error code",
            lambda c: c.replace(
                '    #[msg("Pool account data is invalid or corrupted")]\n    InvalidPool,',
                '    #[msg("Pool account data is invalid or corrupted")]\n    InvalidPool,\n\n    #[msg("Pool is currently paused")]\n    PoolPaused,'
            ) if 'PoolPaused' in c else c.replace(
                '    #[msg("Transaction signature does not match policy")]\n    SignatureMismatch,',
                '    #[msg("Transaction signature does not match policy")]\n    SignatureMismatch,\n\n    #[msg("Pool is currently paused")]\n    PoolPaused,'
            ) if 'PoolPaused' not in c else None)

@_register_micro
def mc_add_pool_is_paused_field():
    return ("programs/harns/src/state.rs", "add is_paused field to InsurancePool",
            lambda c: c.replace(
                '    /// Bump seed for PDA\n    pub bump: u8,\n    /// Reserved for future use\n    pub _padding: [u8; 64],',
                '    /// Whether the pool is paused\n    pub is_paused: bool,\n    /// Bump seed for PDA\n    pub bump: u8,\n    /// Reserved for future use\n    pub _padding: [u8; 63],'
            ) if 'is_paused' not in c else None)

@_register_micro
def mc_fix_pool_space():
    return ("programs/harns/src/state.rs", "fix InsurancePool space after adding is_paused",
            lambda c: c.replace(
                '    /// 8 (discriminator) + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 64 = 151',
                '    /// 8 (discriminator) + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 1 + 63 = 151'
            ) if '+ 1 + 1 + 63' not in c else None)

@_register_micro
def mc_add_sdk_readme():
    return ("sdk/README.md", "add sdk readme",
            lambda _: None)  # special case: create new file

@_register_micro
def mc_add_gitattributes():
    return (".gitattributes", "add gitattributes for linguist stats",
            lambda _: None)  # special case: create new file

@_register_micro
def mc_add_test_connection():
    return ("sdk/tests/client.test.ts", "add connection rpc endpoint assertion",
            lambda c: c.replace(
                '    it("should expose the connection instance", () => {\n      const conn = client.getConnection();\n      expect(conn).toBeDefined();\n    });',
                '    it("should expose the connection instance", () => {\n      const conn = client.getConnection();\n      expect(conn).toBeDefined();\n      expect(conn.rpcEndpoint).toContain("solana.com");\n    });'
            ) if 'rpcEndpoint' not in c else None)

@_register_micro
def mc_add_deposit_min_check_comment():
    return ("programs/harns/src/instructions/deposit_premium.rs",
            "document minimum premium threshold",
            lambda c: c.replace(
                '    let min_premium: u64 = 5_000;',
                '    // Minimum premium: 5000 lamports (~0.000005 SOL)\n    let min_premium: u64 = 5_000;'
            ) if 'Minimum premium: 5000' not in c else None)

@_register_micro
def mc_add_policy_ttl_comment():
    return ("programs/harns/src/instructions/deposit_premium.rs",
            "add TTL documentation comment",
            lambda c: c.replace(
                '    policy.expires_at = clock.unix_timestamp + 300; // 5 min TTL',
                '    // Policies expire after 5 minutes (300 seconds)\n    policy.expires_at = clock.unix_timestamp + 300;'
            ) if 'Policies expire after 5' not in c else None)

@_register_micro
def mc_add_refund_expiry_log():
    return ("programs/harns/src/instructions/process_refund.rs",
            "add expiry check log for debugging",
            lambda c: c.replace(
                '    require!(\n        clock.unix_timestamp <= policy.expires_at,',
                '    msg!("Policy expiry check: now={{}} expires={{}}", clock.unix_timestamp, policy.expires_at);\n    require!(\n        clock.unix_timestamp <= policy.expires_at,'
            ) if 'Policy expiry check' not in c else None)

@_register_micro
def mc_add_constants_comment():
    return ("sdk/src/constants.ts", "add doc comment to constants file",
            lambda c: '/**\n * Core constants for the Harns insurance protocol SDK.\n */\n' + c
            if '* Core constants' not in c else None)

@_register_micro
def mc_add_types_export_all():
    return ("sdk/src/index.ts", "re-export PolicyStatus utility function",
            lambda c: c.replace(
                '} from "./types";',
                '  isPolicyActive,\n} from "./types";'
            ) if 'isPolicyActive' in open(os.path.join(REPO_DIR, "sdk/src/types.ts")).read() and 'isPolicyActive' not in c else None)

@_register_micro
def mc_fix_rustfmt_trailing():
    return ("rustfmt.toml", "add use_field_init_shorthand to rustfmt",
            lambda c: c + 'use_field_init_shorthand = true\n'
            if 'use_field_init_shorthand' not in c else None)


# New file content for special-case micro changes
SPECIAL_FILES = {
    "sdk/README.md": f"# @harns-labs/sdk\n\nTypeScript SDK for the Harns insurance protocol on Solana.\n\n## Version\n\n{VERSION}\n",
    ".gitattributes": "*.rs linguist-language=Rust\n*.ts linguist-language=TypeScript\n*.sh linguist-language=Shell\n",
}


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    print(f"Harns Protocol -- GitHub Repository Generator")
    print(f"Target: {TARGET_COMMITS} commits from {START_DATE.date()} to {END_DATE.date()}")
    print()

    # Clean up any existing git repo in REPO_DIR (but keep main.py and banner.png)
    git_dir = os.path.join(REPO_DIR, ".git")
    if os.path.exists(git_dir):
        shutil.rmtree(git_dir)
        print("Removed existing .git directory")

    # Remove previously generated files (keep main.py and banner.png)
    keep_files = {"main.py", "banner.png"}
    for item in os.listdir(REPO_DIR):
        if item in keep_files or item == ".git":
            continue
        path = os.path.join(REPO_DIR, item)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    # Init git
    run_git(["init"])
    run_git(["config", "user.name", USER_NAME])
    run_git(["config", "user.email", USER_EMAIL])
    print("Initialized git repository")

    # Generate commit schedule
    schedule = generate_commit_schedule(START_DATE, END_DATE, TARGET_COMMITS)
    total_slots = sum(schedule.values())
    print(f"Scheduled {total_slots} commit slots across {len(schedule)} days")

    # Build phases
    phases = build_commit_phases()
    print(f"Defined {len(phases)} file-creation phases")

    # Prepare micro changes (shuffle for variety)
    micros = list(MICRO_CHANGES)
    random.shuffle(micros)

    # Flatten schedule into a list of (date, hour, minute) tuples
    commit_times = []
    for dt, count in sorted(schedule.items()):
        for i in range(count):
            hour = random.randint(9, 23)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            ts = dt.replace(hour=hour, minute=minute, second=second)
            commit_times.append(ts)

    commit_times.sort()
    print(f"Total commit slots: {len(commit_times)}")

    # Assign phases to early commit slots, micros to later ones
    # Make sure phases come first chronologically
    phase_count = len(phases)
    micro_index = 0
    applied_micros = set()
    commit_count = 0

    # ---- Unique commit messages tracking ----
    used_messages = set()

    def unique_msg(base):
        if base not in used_messages:
            used_messages.add(base)
            return base
        # Append a variant suffix
        suffixes = [
            "- minor cleanup", "- whitespace fix", "- formatting",
            "- style tweak", "- adjust spacing", "- refine wording",
            "- update comment", "- fix indent", "- polish",
            "- tidy up", "- small fix", "- adjust",
        ]
        for s in suffixes:
            candidate = f"{base} {s}"
            if candidate not in used_messages:
                used_messages.add(candidate)
                return candidate
        # Fallback: numeric suffix
        n = 2
        while True:
            candidate = f"{base} (pass {n})"
            if candidate not in used_messages:
                used_messages.add(candidate)
                return candidate
            n += 1

    for idx, ts in enumerate(commit_times):
        if idx < phase_count:
            # Write phase files
            files_dict, msg = phases[idx]
            for fpath, gen_fn in files_dict.items():
                write_file(fpath, gen_fn())
            # Make shell scripts executable
            for fpath in files_dict:
                if fpath.endswith(".sh"):
                    full = os.path.join(REPO_DIR, fpath)
                    os.chmod(full, 0o755)

            commit(unique_msg(msg), ts)
            commit_count += 1
        else:
            # Apply a micro change
            applied = False
            attempts = 0
            while not applied and attempts < len(micros) * 2:
                mc_fn = micros[micro_index % len(micros)]
                micro_index += 1
                attempts += 1

                mc_id = mc_fn.__name__
                if mc_id in applied_micros:
                    continue

                result = mc_fn()
                if result is None:
                    continue

                fpath, msg, transform = result

                # Special file creation
                if fpath in SPECIAL_FILES and not os.path.exists(os.path.join(REPO_DIR, fpath)):
                    write_file(fpath, SPECIAL_FILES[fpath])
                    commit(unique_msg(msg), ts)
                    commit_count += 1
                    applied_micros.add(mc_id)
                    applied = True
                    continue

                # Normal transform
                full_path = os.path.join(REPO_DIR, fpath)
                if not os.path.exists(full_path):
                    continue

                with open(full_path, "r", encoding="utf-8") as f:
                    content = f.read()

                new_content = transform(content)
                if new_content is None:
                    applied_micros.add(mc_id)
                    continue

                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(new_content)

                commit(unique_msg(msg), ts)
                commit_count += 1
                applied_micros.add(mc_id)
                applied = True

            if not applied:
                # Generate a trivial comment change to fill the slot
                target_files = [
                    ("programs/harns/src/lib.rs", "rust"),
                    ("programs/harns/src/state.rs", "rust"),
                    ("programs/harns/src/errors.rs", "rust"),
                    ("sdk/src/client.ts", "ts"),
                    ("sdk/src/types.ts", "ts"),
                    ("sdk/src/constants.ts", "ts"),
                    ("programs/harns/src/instructions/initialize.rs", "rust"),
                    ("programs/harns/src/instructions/deposit_premium.rs", "rust"),
                    ("programs/harns/src/instructions/process_refund.rs", "rust"),
                    ("programs/harns/src/instructions/update_rates.rs", "rust"),
                ]

                filler_messages = [
                    "clean up internal comments",
                    "adjust whitespace in pool logic",
                    "refine error message wording",
                    "improve code readability",
                    "remove trailing whitespace",
                    "normalize import ordering",
                    "minor formatting pass",
                    "tighten variable naming",
                    "update inline documentation",
                    "streamline helper functions",
                    "consolidate type annotations",
                    "simplify conditional logic",
                    "reorder struct fields for clarity",
                    "fix comment typo in state module",
                    "align bracket style",
                    "remove dead code path",
                    "harmonize log message format",
                    "reduce nesting depth",
                    "extract constant for readability",
                    "tweak assertion message",
                    "fix spacing in match arms",
                    "polish function signatures",
                    "standardize doc comments",
                    "reformat multiline expression",
                    "adjust test threshold value",
                    "update rate bounds comment",
                    "clarify seed derivation logic",
                    "rename local variable for clarity",
                    "add missing semicolons",
                    "reorganize imports block",
                    "simplify return expression",
                    "clean up trailing commas",
                    "fix indentation in handler",
                    "normalize string quotes",
                    "improve type safety in client",
                    "harden input validation",
                    "broaden test coverage scope",
                    "tune premium calculation",
                    "drop unused import",
                    "trim redundant type cast",
                    "widen refund window check",
                    "collapse single-use variable",
                    "rephrase error description",
                    "flatten nested if block",
                    "annotate unsafe block reasoning",
                    "cache derived address locally",
                    "inline trivial helper",
                    "batch log statements",
                    "guard against zero division",
                    "document edge case behavior",
                    "swap assert for require macro",
                    "unify timestamp format",
                    "lock dependency version pin",
                    "expand integration test case",
                    "verify PDA bump correctness",
                    "deduplicate seed constant",
                    "normalize crate feature flags",
                    "shore up boundary condition",
                    "prefer checked arithmetic ops",
                    "compress account validation",
                    "pre-compute buffer length",
                ]

                tf, lang = random.choice(target_files)
                full_path = os.path.join(REPO_DIR, tf)
                if os.path.exists(full_path):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Add a unique trailing comment
                    if lang == "rust":
                        marker = f"// internal ref: {commit_count:04d}"
                        content = content.rstrip() + f"\n{marker}\n"
                    else:
                        marker = f"// ref: {commit_count:04d}"
                        content = content.rstrip() + f"\n{marker}\n"

                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    msg = unique_msg(random.choice(filler_messages))
                    commit(msg, ts)
                    commit_count += 1

    # Copy banner.png into the repo if it exists
    banner_src = BANNER_PATH
    if os.path.exists(banner_src):
        run_git(["add", "banner.png"], END_DATE)
        try:
            run_git(["commit", "-m", "add project banner", "--allow-empty"], END_DATE)
            commit_count += 1
        except subprocess.CalledProcessError:
            pass  # already tracked

    # Summary
    print()
    print("=" * 50)
    print(f"Generation complete.")
    print(f"  Commits created: {commit_count}")

    # Count files
    file_count = 0
    for root, dirs, files in os.walk(REPO_DIR):
        # Skip .git directory
        if ".git" in root:
            continue
        for f in files:
            if f != "main.py":
                file_count += 1

    print(f"  Files created: {file_count}")

    # Count lines
    total_lines = 0
    rust_lines = 0
    ts_lines = 0
    other_lines = 0
    for root, dirs, files in os.walk(REPO_DIR):
        if ".git" in root:
            continue
        for f in files:
            if f == "main.py":
                continue
            fp = os.path.join(root, f)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                    lines = len(fh.readlines())
                    total_lines += lines
                    if f.endswith(".rs"):
                        rust_lines += lines
                    elif f.endswith(".ts") or f.endswith(".js"):
                        ts_lines += lines
                    else:
                        other_lines += lines
            except Exception:
                pass

    print(f"  Total lines: {total_lines}")
    all_code = rust_lines + ts_lines + other_lines
    if all_code > 0:
        print(f"  Rust: {rust_lines} lines ({100*rust_lines/all_code:.1f}%)")
        print(f"  TypeScript/JS: {ts_lines} lines ({100*ts_lines/all_code:.1f}%)")
        print(f"  Other: {other_lines} lines ({100*other_lines/all_code:.1f}%)")
    print("=" * 50)


if __name__ == "__main__":
    random.seed(42)  # reproducible but can be removed for variety
    main()
