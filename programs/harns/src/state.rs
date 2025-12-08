use anchor_lang::prelude::*;

#[account]
#[derive(Default)]
pub struct InsurancePool {{
    /// Authority that controls the pool
    pub authority: Pubkey,
    /// Pool seed for PDA derivation
    pub pool_seed: u64,
    /// Total premiums collected (lamports)
    pub total_premiums: u64,
    /// Total refunds paid out (lamports)
    pub total_refunds: u64,
    /// Number of active policies
    pub active_policies: u32,
    /// Base insurance rate in basis points
    pub base_rate_bps: u16,
    /// Pool creation timestamp
    pub created_at: i64,
    /// Last rate update timestamp
    pub last_updated: i64,
    /// Whether the pool is paused
    pub is_paused: bool,
    /// Bump seed for PDA
    pub bump: u8,
    /// Reserved for future use
    pub _padding: [u8; 63],
}}

impl InsurancePool {{
    /// 8 (discriminator) + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 1 + 63 = 151
    pub const SPACE: usize = 8 + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 64;
}}

#[account]
#[derive(Default)]
pub struct Policy {{
    /// Owner of the policy
    pub owner: Pubkey,
    /// Associated insurance pool
    pub pool: Pubkey,
    /// Premium paid (lamports)
    pub premium_amount: u64,
    /// Transaction signature being insured
    pub tx_signature: [u8; 64],
    /// Policy status: 0=Active, 1=Claimed, 2=Expired
    pub status: u8,
    /// Timestamp of policy creation
    pub created_at: i64,
    /// Timestamp of policy expiry
    pub expires_at: i64,
    /// Bump seed for PDA
    pub bump: u8,
}}

impl Policy {{
    /// 8 (discriminator) + 32 + 32 + 8 + 64 + 1 + 8 + 8 + 1 = 162
    pub const SPACE: usize = 8 + 32 + 32 + 8 + 64 + 1 + 8 + 8 + 1;
}}

#[account]
pub struct RefundRecord {{
    /// Policy that was refunded
    pub policy: Pubkey,
    /// Recipient of the refund
    pub recipient: Pubkey,
    /// Refund amount (lamports)
    pub amount: u64,
    /// Refund timestamp
    pub refunded_at: i64,
    /// Bump seed for PDA
    pub bump: u8,
}}

impl RefundRecord {{
    /// 8 (discriminator) + 32 + 32 + 8 + 8 + 1 = 89
    pub const SPACE: usize = 8 + 32 + 32 + 8 + 8 + 1;
}}
// internal ref: 0075
// internal ref: 0079
// internal ref: 0086
