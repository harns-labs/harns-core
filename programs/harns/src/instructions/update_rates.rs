use anchor_lang::prelude::*;
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
    // Log transition for debugging
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
// internal ref: 0090
// internal ref: 0098
// internal ref: 0101
// internal ref: 0103
// internal ref: 0120
// internal ref: 0126
// internal ref: 0134
// internal ref: 0148
// internal ref: 0163
// internal ref: 0184
// internal ref: 0187
