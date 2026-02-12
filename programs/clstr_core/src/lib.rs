/// Core program for the clstr protocol.
use anchor_lang::prelude::*;

mod state;
mod contexts;
mod errors;

use contexts::*;

declare_id!("E1iTSqt1YkW6LoNXMspEoxsdotzEdmn3QjEJL5R3NUwe");

#[program]
pub mod clstr_core {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, config_bump: u8) -> Result<()> {
        let config = &mut ctx.accounts.config;
        config.authority = ctx.accounts.authority.key();
        config.bump = config_bump;
        config.total_flags = 0;
        config.total_burns = 0;
        Ok(())
    }

    pub fn flag_wallet(
        ctx: Context<FlagWallet>,
        risk_score: u64,
        zk_hash: [u8; 32],
    ) -> Result<()> {
        let flag_account = &mut ctx.accounts.flag_account;
        flag_account.target = ctx.accounts.target.key();
        flag_account.flagger = ctx.accounts.flagger.key();
        flag_account.risk_score = risk_score;
        flag_account.zk_hash = zk_hash;
        flag_account.timestamp = Clock::get()?.unix_timestamp;
        flag_account.is_active = true;

        let config = &mut ctx.accounts.config;
        config.total_flags = config.total_flags.checked_add(1).unwrap();

        Ok(())
    }

    pub fn burn_flag(ctx: Context<BurnFlag>) -> Result<()> {
        let flag_account = &mut ctx.accounts.flag_account;
        require!(flag_account.is_active, errors::ClstrError::FlagAlreadyBurned);
        flag_account.is_active = false;

        let config = &mut ctx.accounts.config;
        config.total_burns = config.total_burns.checked_add(1).unwrap();

        Ok(())
    }

    pub fn update_score(
        ctx: Context<UpdateScore>,
        new_score: u64,
        new_zk_hash: [u8; 32],
    ) -> Result<()> {
        let flag_account = &mut ctx.accounts.flag_account;
        require!(flag_account.is_active, errors::ClstrError::FlagAlreadyBurned);
        require!(
            flag_account.flagger == ctx.accounts.flagger.key(),
            errors::ClstrError::Unauthorized
        );
        flag_account.risk_score = new_score;
        flag_account.zk_hash = new_zk_hash;
        flag_account.timestamp = Clock::get()?.unix_timestamp;
        Ok(())
    }
}

// 66f041e1
