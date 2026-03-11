use crate::errors::HarnsError;
use crate::events::PoolClosed;
use crate::state::InsurancePool;
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct ClosePool<'info> {
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
}

pub fn handler(ctx: Context<ClosePool>) -> Result<()> {
    let pool = &ctx.accounts.pool;
    let clock = Clock::get()?;

    let remaining_balance = pool.to_account_info().lamports();

    emit!(PoolClosed {
        pool: pool.key(),
        authority: ctx.accounts.authority.key(),
        remaining_balance,
        timestamp: clock.unix_timestamp,
    });

    msg!(
        "Pool closed: {}, remaining balance: {} lamports returned to authority",
        pool.key(),
        remaining_balance
    );

    Ok(())
}
