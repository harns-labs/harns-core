// Harns Protocol v0.4.2
use anchor_lang::prelude::*;

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
// internal ref: 0076
// internal ref: 0080
// internal ref: 0081
// internal ref: 0083
// internal ref: 0094
// internal ref: 0104
// internal ref: 0128
// internal ref: 0136
// internal ref: 0144
// internal ref: 0169
// internal ref: 0172
// internal ref: 0176
// internal ref: 0180
// internal ref: 0185
