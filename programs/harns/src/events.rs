use anchor_lang::prelude::*;

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
