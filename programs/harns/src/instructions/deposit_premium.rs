use anchor_lang::prelude::*;
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
    // Minimum premium: 5000 lamports (~0.000005 SOL)
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

    // Update pool state -- checked arithmetic prevents overflow
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
    // Policies expire after 5 minutes (300 seconds)
    policy.expires_at = clock.unix_timestamp + 300;
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
// internal ref: 0071
// internal ref: 0110
// internal ref: 0112
// internal ref: 0118
// internal ref: 0124
// internal ref: 0125
// internal ref: 0130
// internal ref: 0142
// internal ref: 0143
// internal ref: 0149
// internal ref: 0154
// internal ref: 0162
// internal ref: 0175
// internal ref: 0178
