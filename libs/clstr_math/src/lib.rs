// Louvain clustering implementation for wallet graph analysis.
use std::collections::HashMap;

pub mod graph;
pub mod zk;
pub mod scoring;
pub mod ingestion;

pub struct Graph {
    pub adjacency: HashMap<u64, Vec<(u64, f64)>>,
    pub node_count: usize,
}

impl Graph {
    pub fn new() -> Self {
        Graph {
            adjacency: HashMap::new(),
            node_count: 0,
        }
    }

    pub fn add_edge(&mut self, from: u64, to: u64, weight: f64) {
        self.adjacency.entry(from).or_default().push((to, weight));
        self.adjacency.entry(to).or_default().push((from, weight));
        self.node_count = self.adjacency.len();
    }

    pub fn neighbors(&self, node: u64) -> &[(u64, f64)] {
        self.adjacency.get(&node).map(|v| v.as_slice()).unwrap_or(&[])
    }

    pub fn total_weight(&self) -> f64 {
        self.adjacency
            .values()
            .flat_map(|edges| edges.iter())
            .map(|(_, w)| w)
            .sum::<f64>()
            / 2.0
    }
}

pub struct LouvainClustering {
    pub resolution: f64,
    pub assignments: HashMap<u64, u64>,
}

impl LouvainClustering {
    pub fn new(resolution: f64) -> Self {
        LouvainClustering {
            resolution,
            assignments: HashMap::new(),
        }
    }

    pub fn run(&mut self, graph: &Graph) -> &HashMap<u64, u64> {
        for &node in graph.adjacency.keys() {
            self.assignments.insert(node, node);
        }

        let total_weight = graph.total_weight();
        if total_weight == 0.0 {
            return &self.assignments;
        }

        let mut improved = true;
        while improved {
            improved = false;
            let nodes: Vec<u64> = graph.adjacency.keys().copied().collect();
            for node in &nodes {
                let current_community = self.assignments[node];
                let mut best_community = current_community;
                let mut best_gain = 0.0_f64;

                let mut community_weights: HashMap<u64, f64> = HashMap::new();
                for &(neighbor, weight) in graph.neighbors(*node) {
                    let nc = self.assignments[&neighbor];
                    *community_weights.entry(nc).or_default() += weight;
                }

                let ki = graph.neighbors(*node).iter().map(|(_, w)| w).sum::<f64>();

                for (&community, &weight_to_community) in &community_weights {
                    let sigma_tot = self.community_total_weight(graph, community);
                    let gain = weight_to_community
                        - self.resolution * sigma_tot * ki / (2.0 * total_weight);
                    if gain > best_gain {
                        best_gain = gain;
                        best_community = community;
                    }
                }

                if best_community != current_community {
                    self.assignments.insert(*node, best_community);
                    improved = true;
                }
            }
        }

        &self.assignments
    }

    fn community_total_weight(&self, graph: &Graph, community: u64) -> f64 {
        self.assignments
            .iter()
            .filter(|(_, &c)| c == community)
            .flat_map(|(node, _)| graph.neighbors(*node).iter())
            .map(|(_, w)| w)
            .sum()
    }
}

pub fn modularity(graph: &Graph, assignments: &HashMap<u64, u64>) -> f64 {
    let total_weight = graph.total_weight();
    if total_weight == 0.0 {
        return 0.0;
    }

    let mut q = 0.0_f64;
    for (&node, neighbors) in &graph.adjacency {
        let ki: f64 = neighbors.iter().map(|(_, w)| w).sum();
        for &(neighbor, weight) in neighbors {
            if assignments.get(&node) == assignments.get(&neighbor) {
                let kj: f64 = graph.neighbors(neighbor).iter().map(|(_, w)| w).sum();
                q += weight - (ki * kj) / (2.0 * total_weight);
            }
        }
    }

    q / (2.0 * total_weight)
}

// d1fe173d
