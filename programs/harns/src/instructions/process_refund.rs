use crate::errors::HarnsError;
use crate::events::RefundProcessed;
use crate::state::{InsurancePool, Policy, RefundRecord};
use anchor_lang::prelude::*;

#[derive(Accounts)]
#[instruction(tx_signature: [u8; 64])]
pub struct ProcessRefund<'info> {
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
}

pub fn handler(ctx: Context<ProcessRefund>, _tx_signature: [u8; 64]) -> Result<()> {
    let pool = &mut ctx.accounts.pool;
    let policy = &mut ctx.accounts.policy;
    let refund_record = &mut ctx.accounts.refund_record;
    let clock = Clock::get()?;

    msg!(
        "Policy expiry check: now={} expires={}",
        clock.unix_timestamp,
        policy.expires_at
    );
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
    pool.total_refunds = pool
        .total_refunds
        .checked_add(refund_amount)
        .ok_or(HarnsError::Overflow)?;
    pool.active_policies = pool
        .active_policies
        .checked_sub(1)
        .ok_or(HarnsError::Overflow)?;

    // Update policy
    policy.status = 1; // claimed

    // Record refund
    refund_record.policy = policy.key();
    refund_record.recipient = ctx.accounts.claimant.key();
    refund_record.amount = refund_amount;
    refund_record.refunded_at = clock.unix_timestamp;
    refund_record.bump = ctx.bumps.refund_record;

    emit!(RefundProcessed {
        pool: pool.key(),
        policy: policy.key(),
        recipient: ctx.accounts.claimant.key(),
        amount: refund_amount,
        timestamp: clock.unix_timestamp,
    });

    msg!(
        "Refund processed: {} lamports to {} (policy: {})",
        refund_amount,
        ctx.accounts.claimant.key(),
        policy.key()
    );
    Ok(())
}
// internal ref: 0077
// internal ref: 0105
// internal ref: 0107
// internal ref: 0115
// internal ref: 0117
// internal ref: 0140
// internal ref: 0150
// internal ref: 0152
// internal ref: 0159
// internal ref: 0164
// internal ref: 0170
// internal ref: 0190
// internal ref: 0194
// internal ref: 0206
