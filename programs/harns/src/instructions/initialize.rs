use anchor_lang::prelude::*;
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

    msg!("Insurance pool initialized: {{}}, rate: {{}} bps", pool.key(), base_rate_bps);
    Ok(())
}}
// internal ref: 0073
// internal ref: 0074
// internal ref: 0096
// internal ref: 0109
// internal ref: 0111
// internal ref: 0119
// internal ref: 0127
