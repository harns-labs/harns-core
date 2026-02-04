use anchor_lang::prelude::*;
use crate::state::{Config, FlagAccount};

pub fn process_flag_creation(
    config: &mut Config,
    flag_account: &mut FlagAccount,
    target: Pubkey,
    flagger: Pubkey,
    risk_score: u64,
    zk_hash: [u8; 32],
    timestamp: i64,
) -> Result<()> {
    require!(risk_score <= 10000, crate::errors::ClstrError::RiskScoreOverflow);
    require!(zk_hash != [0u8; 32], crate::errors::ClstrError::InvalidZkHash);

    flag_account.target = target;
    flag_account.flagger = flagger;
    flag_account.risk_score = risk_score;
    flag_account.zk_hash = zk_hash;
    flag_account.timestamp = timestamp;
    flag_account.is_active = true;

    config.total_flags = config.total_flags.checked_add(1).unwrap();

    Ok(())
}

pub fn process_flag_burn(
    config: &mut Config,
    flag_account: &mut FlagAccount,
) -> Result<()> {
    require!(flag_account.is_active, crate::errors::ClstrError::FlagAlreadyBurned);

    flag_account.is_active = false;
    config.total_burns = config.total_burns.checked_add(1).unwrap();

    Ok(())
}

pub fn process_score_update(
    flag_account: &mut FlagAccount,
    flagger: Pubkey,
    new_score: u64,
    new_zk_hash: [u8; 32],
    timestamp: i64,
) -> Result<()> {
    require!(flag_account.is_active, crate::errors::ClstrError::FlagAlreadyBurned);
    require!(
        flag_account.flagger == flagger,
        crate::errors::ClstrError::Unauthorized
    );
    require!(new_score <= 10000, crate::errors::ClstrError::RiskScoreOverflow);

    flag_account.risk_score = new_score;
    flag_account.zk_hash = new_zk_hash;
    flag_account.timestamp = timestamp;

    Ok(())
}

pub fn compute_active_flags(config: &Config) -> u64 {
    config.total_flags.saturating_sub(config.total_burns)
}

pub fn is_high_risk(risk_score: u64) -> bool {
    risk_score >= 7500
}

pub fn normalize_score(raw_score: f64) -> u64 {
    let clamped = raw_score.max(0.0).min(1.0);
    (clamped * 10000.0) as u64
}

// 2838023a
