use anchor_lang::prelude::*;

#[account]
pub struct Config {
    pub authority: Pubkey,
    pub bump: u8,
    pub total_flags: u64,
    pub total_burns: u64,
    pub _padding: [u8; 7],
}

impl Config {
    pub const LEN: usize = 32 + 1 + 8 + 8 + 7;
}

#[account]
pub struct FlagAccount {
    pub target: Pubkey,
    pub flagger: Pubkey,
    pub risk_score: u64,
    pub zk_hash: [u8; 32],
    pub timestamp: i64,
    pub is_active: bool,
    pub _padding: [u8; 6],
}

impl FlagAccount {
    pub const LEN: usize = 32 + 32 + 8 + 32 + 8 + 1 + 6;
}

// a684ecee
