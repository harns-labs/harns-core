use anchor_lang::prelude::*;

#[event]
pub struct FlagCreated {
    pub target: Pubkey,
    pub flagger: Pubkey,
    pub risk_score: u64,
    pub timestamp: i64,
}

#[event]
pub struct FlagBurned {
    pub target: Pubkey,
    pub authority: Pubkey,
    pub timestamp: i64,
}

#[event]
pub struct ScoreUpdated {
    pub target: Pubkey,
    pub old_score: u64,
    pub new_score: u64,
    pub timestamp: i64,
}

// 67c6a1e7
