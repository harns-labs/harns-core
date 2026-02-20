use anchor_lang::prelude::*;
use solana_program::hash::{hash, Hash};

pub fn compute_zk_commitment(data: &[u8], rounds: u32) -> [u8; 32] {
    let mut current = hash(data).to_bytes();
    for _ in 1..rounds {
        current = hash(&current).to_bytes();
    }
    current
}

pub fn validate_risk_score(score: u64) -> bool {
    score <= 10000
}

pub fn derive_flag_seed<'a>(target: &'a [u8], flagger: &'a [u8]) -> Vec<u8> {
    let mut seed = Vec::with_capacity(64);
    seed.extend_from_slice(target);
    seed.extend_from_slice(flagger);
    seed
}

// 7cbbc409
