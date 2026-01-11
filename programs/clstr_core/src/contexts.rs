use anchor_lang::prelude::*;
use crate::state::{Config, FlagAccount};

#[derive(Accounts)]
#[instruction(config_bump: u8)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Config::LEN,
        seeds = [b"config"],
        bump,
    )]
    pub config: Account<'info, Config>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct FlagWallet<'info> {
    #[account(
        init,
        payer = flagger,
        space = 8 + FlagAccount::LEN,
        seeds = [b"flag", target.key().as_ref(), flagger.key().as_ref()],
        bump,
    )]
    pub flag_account: Account<'info, FlagAccount>,
    #[account(
        mut,
        seeds = [b"config"],
        bump = config.bump,
    )]
    pub config: Account<'info, Config>,
    /// CHECK: target wallet being flagged
    pub target: AccountInfo<'info>,
    #[account(mut)]
    pub flagger: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct BurnFlag<'info> {
    #[account(
        mut,
        seeds = [b"flag", flag_account.target.as_ref(), flag_account.flagger.as_ref()],
        bump,
    )]
    pub flag_account: Account<'info, FlagAccount>,
    #[account(
        mut,
        seeds = [b"config"],
        bump = config.bump,
    )]
    pub config: Account<'info, Config>,
    #[account(
        constraint = authority.key() == config.authority,
    )]
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct UpdateScore<'info> {
    #[account(
        mut,
        seeds = [b"flag", flag_account.target.as_ref(), flag_account.flagger.as_ref()],
        bump,
    )]
    pub flag_account: Account<'info, FlagAccount>,
    pub flagger: Signer<'info>,
}

// 6512bd43
