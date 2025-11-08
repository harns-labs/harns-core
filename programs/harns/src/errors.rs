use anchor_lang::prelude::*;

#[error_code]
pub enum HarnsError {{
    #[msg("Insurance rate must be between 1 and 10000 basis points")]
    InvalidRate,

    #[msg("Premium amount is below minimum threshold")]
    PremiumTooLow,

    #[msg("Policy is not in active state")]
    PolicyNotActive,

    #[msg("Policy has expired and is no longer claimable")]
    PolicyExpired,

    #[msg("Caller is not authorized to perform this action")]
    Unauthorized,

    #[msg("Arithmetic overflow detected")]
    Overflow,

    #[msg("Insufficient pool balance for refund")]
    InsufficientBalance,

    #[msg("Transaction signature does not match policy")]
    SignatureMismatch,

    #[msg("Pool account data is invalid or corrupted")]
    InvalidPool,

    #[msg("Pool is currently paused")]
    PoolPaused,
}}
