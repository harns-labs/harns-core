// clstr command-line interface for operators.
use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::fs;
use std::collections::HashMap;
use clstr_math::{Graph, LouvainClustering, modularity};

#[derive(Parser)]
#[command(name = "clstr-cli")]
#[command(about = "Zero-knowledge wallet cluster analysis on Solana")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Cluster {
        #[arg(long)]
        input: String,
        #[arg(long)]
        output: String,
        #[arg(long, default_value = "1.0")]
        resolution: f64,
    },
    Verify {
        #[arg(long)]
        proof: String,
        #[arg(long)]
        commitment: String,
    },
    Stats {
        #[arg(long)]
        input: String,
    },
}

#[derive(Deserialize)]
struct TransactionEdge {
    from: u64,
    to: u64,
    weight: f64,
}

#[derive(Serialize)]
struct ClusterOutput {
    clusters: HashMap<u64, Vec<u64>>,
    modularity: f64,
    node_count: usize,
}

#[derive(Deserialize)]
struct ProofData {
    hash: Vec<u8>,
    rounds: u32,
}

fn run_cluster(input: &str, output: &str, resolution: f64) {
    let data = fs::read_to_string(input).expect("Failed to read input file");
    let edges: Vec<TransactionEdge> = serde_json::from_str(&data).expect("Invalid JSON format");

    let mut graph = Graph::new();
    for edge in &edges {
        graph.add_edge(edge.from, edge.to, edge.weight);
    }

    let mut clustering = LouvainClustering::new(resolution);
    let assignments = clustering.run(&graph);

    let mut clusters: HashMap<u64, Vec<u64>> = HashMap::new();
    for (&node, &community) in assignments {
        clusters.entry(community).or_default().push(node);
    }

    let result = ClusterOutput {
        clusters,
        modularity: modularity(&graph, assignments),
        node_count: graph.node_count,
    };

    let json = serde_json::to_string_pretty(&result).expect("Serialization failed");
    fs::write(output, json).expect("Failed to write output file");
    println!("Clustering complete: {} nodes processed", graph.node_count);
}

fn run_verify(proof_path: &str, commitment: &str) {
    let data = fs::read_to_string(proof_path).expect("Failed to read proof file");
    let proof: ProofData = serde_json::from_str(&data).expect("Invalid proof format");

    let commitment_bytes = hex_decode(commitment);
    let matches = proof.hash == commitment_bytes;

    if matches {
        println!("Verification PASSED: proof matches commitment");
    } else {
        println!("Verification FAILED: proof does not match commitment");
    }
}

fn run_stats(input: &str) {
    let data = fs::read_to_string(input).expect("Failed to read input file");
    let edges: Vec<TransactionEdge> = serde_json::from_str(&data).expect("Invalid JSON format");

    let mut graph = Graph::new();
    for edge in &edges {
        graph.add_edge(edge.from, edge.to, edge.weight);
    }

    println!("Nodes: {}", graph.node_count);
    println!("Edges: {}", edges.len());
    println!("Total weight: {:.4}", graph.total_weight());
}

fn hex_decode(s: &str) -> Vec<u8> {
    let s = s.strip_prefix("0x").unwrap_or(s);
    (0..s.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&s[i..i + 2], 16).unwrap_or(0))
        .collect()
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Commands::Cluster { input, output, resolution } => {
            run_cluster(&input, &output, resolution);
        }
        Commands::Verify { proof, commitment } => {
            run_verify(&proof, &commitment);
        }
        Commands::Stats { input } => {
            run_stats(&input);
        }
    }
}

// 3295c76a
