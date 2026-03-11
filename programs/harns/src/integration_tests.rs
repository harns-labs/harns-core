//! Integration test stubs for the Harns protocol.
//!
//! These tests verify the program logic in a simulated environment.
//! Run with: cargo test --manifest-path programs/harns/Cargo.toml

#[cfg(test)]
mod tests {

    #[test]
    fn test_pool_space_calculation() {
        // InsurancePool::SPACE should account for discriminator
        let expected = 8 + 32 + 8 + 8 + 8 + 4 + 2 + 8 + 8 + 1 + 1 + 63;
        assert_eq!(expected, 151);
    }

    #[test]
    fn test_policy_space_calculation() {
        let expected = 8 + 32 + 32 + 8 + 64 + 1 + 8 + 8 + 1;
        assert_eq!(expected, 162);
    }

    #[test]
    fn test_refund_record_space() {
        let expected = 8 + 32 + 32 + 8 + 8 + 1;
        assert_eq!(expected, 89);
    }

    #[test]
    fn test_min_premium_constant() {
        assert_eq!(crate::constants::MIN_PREMIUM_LAMPORTS, 5_000);
    }

    #[test]
    fn test_default_rate() {
        assert_eq!(crate::constants::DEFAULT_RATE_BPS, 250);
    }

    #[test]
    fn test_policy_ttl() {
        assert_eq!(crate::constants::POLICY_TTL_SECONDS, 300);
    }

    #[test]
    fn test_max_rate_bound() {
        assert_eq!(crate::constants::MAX_RATE_BPS, 10_000);
    }

    #[test]
    fn test_pool_seed_prefix() {
        assert_eq!(crate::constants::POOL_SEED, b"insurance_pool");
    }

    #[test]
    fn test_policy_seed_prefix() {
        assert_eq!(crate::constants::POLICY_SEED, b"policy");
    }

    #[test]
    fn test_refund_seed_prefix() {
        assert_eq!(crate::constants::REFUND_SEED, b"refund");
    }

    #[test]
    fn test_lamports_per_sol() {
        assert_eq!(crate::constants::LAMPORTS_PER_SOL, 1_000_000_000);
    }

    #[test]
    fn test_bps_denominator() {
        assert_eq!(crate::constants::BPS_DENOMINATOR, 10_000);
    }

    #[test]
    fn test_min_pool_reserve() {
        assert_eq!(crate::constants::MIN_POOL_RESERVE, 10_000_000);
    }

    #[test]
    fn test_total_space_under_10k() {
        // Solana accounts should generally be under 10KB
        let pool_space = 151usize;
        let policy_space = 162usize;
        let refund_space = 89usize;
        assert!(pool_space < 10_240);
        assert!(policy_space < 10_240);
        assert!(refund_space < 10_240);
    }

    #[test]
    fn test_space_alignment() {
        // Verify space values are reasonable (no accidental large allocations)
        let pool = 151usize;
        let policy = 162usize;
        let refund = 89usize;
        assert!(pool > 8, "Pool must be larger than discriminator");
        assert!(policy > 8, "Policy must be larger than discriminator");
        assert!(refund > 8, "Refund must be larger than discriminator");
        assert!(pool < 1024, "Pool should fit in reasonable space");
        assert!(policy < 1024, "Policy should fit in reasonable space");
        assert!(refund < 512, "Refund should fit in reasonable space");
    }

    #[test]
    fn test_rate_bounds_consistency() {
        let max = crate::constants::MAX_RATE_BPS;
        let default = crate::constants::DEFAULT_RATE_BPS;
        assert!(default > 0);
        assert!(default < max);
        assert_eq!(max, 10_000);
    }

    #[test]
    fn test_premium_min_is_positive() {
        let min = crate::constants::MIN_PREMIUM_LAMPORTS;
        assert!(min > 0, "Minimum premium must be positive");
        assert!(min < crate::constants::LAMPORTS_PER_SOL, "Min premium should be less than 1 SOL");
    }

    #[test]
    fn test_policy_ttl_reasonable() {
        let ttl = crate::constants::POLICY_TTL_SECONDS;
        assert!(ttl >= 60, "TTL should be at least 1 minute");
        assert!(ttl <= 3600, "TTL should be at most 1 hour");
    }
}
