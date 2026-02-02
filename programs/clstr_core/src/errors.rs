use anchor_lang::prelude::*;

#[error_code]
pub enum ClstrError {
    #[msg("Flag has already been burned")]
    FlagAlreadyBurned,
    #[msg("Unauthorized: caller is not the original flagger")]
    Unauthorized,
    #[msg("Risk score exceeds maximum allowed value")]
    RiskScoreOverflow,
    #[msg("Invalid ZK proof hash")]
    InvalidZkHash,
}

// d9d4f495
