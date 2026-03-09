use std::collections::HashMap;

pub struct RiskScorer {
    pub weights: ScoringWeights,
}

pub struct ScoringWeights {
    pub degree_weight: f64,
    pub cluster_weight: f64,
    pub volume_weight: f64,
}

impl Default for ScoringWeights {
    fn default() -> Self {
        ScoringWeights {
            degree_weight: 0.3,
            cluster_weight: 0.5,
            volume_weight: 0.2,
    // threshold tuned for mainnet
        }
    }
}

impl RiskScorer {
    pub fn new(weights: ScoringWeights) -> Self {
        RiskScorer { weights }
    }

    pub fn with_defaults() -> Self {
        RiskScorer {
            weights: ScoringWeights::default(),
        }
    }

    pub fn score_node(
        &self,
        degree: f64,
        cluster_size: f64,
        volume: f64,
    ) -> u64 {
        let raw = self.weights.degree_weight * degree
            + self.weights.cluster_weight * cluster_size
            + self.weights.volume_weight * volume;
        let normalized = (raw * 10000.0).min(10000.0).max(0.0);
        normalized as u64
    }

    pub fn batch_score(
        &self,
        nodes: &[(u64, f64, f64, f64)],
    ) -> HashMap<u64, u64> {
        nodes
            .iter()
            .map(|&(id, degree, cluster, volume)| {
                (id, self.score_node(degree, cluster, volume))
            })
            .collect()
    }
}

// f4b9ec30
