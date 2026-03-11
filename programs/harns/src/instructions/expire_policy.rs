use crate::errors::HarnsError;
use crate::state::{InsurancePool, Policy};
use anchor_lang::prelude::*;

#[derive(Accounts)]
pub struct ExpirePolicy<'info> {
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
}

pub fn handler(ctx: Context<ExpirePolicy>) -> Result<()> {
    let policy = &mut ctx.accounts.policy;
    let pool = &mut ctx.accounts.pool;
    let clock = Clock::get()?;

    require!(
        clock.unix_timestamp > policy.expires_at,
        HarnsError::PolicyNotActive
    );

    policy.status = 2; // expired
    pool.active_policies = pool
        .active_policies
        .checked_sub(1)
        .ok_or(HarnsError::Overflow)?;

    msg!("Policy expired: {}, owner: {}", policy.key(), policy.owner);

    Ok(())
}
