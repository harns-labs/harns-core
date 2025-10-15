use anchor_lang::prelude::*;
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
