use std::collections::{HashMap, HashSet, VecDeque};

pub fn bfs_distances(adjacency: &HashMap<u64, Vec<(u64, f64)>>, start: u64) -> HashMap<u64, u32> {
    let mut distances: HashMap<u64, u32> = HashMap::new();
    let mut visited: HashSet<u64> = HashSet::new();
    let mut queue: VecDeque<(u64, u32)> = VecDeque::new();

    distances.insert(start, 0);
    visited.insert(start);
    queue.push_back((start, 0));

    while let Some((current, dist)) = queue.pop_front() {
        if let Some(neighbors) = adjacency.get(&current) {
            for &(neighbor, _) in neighbors {
                if visited.insert(neighbor) {
                    distances.insert(neighbor, dist + 1);
                    queue.push_back((neighbor, dist + 1));
                }
            }
        }
    }

    distances
}

pub fn connected_components(adjacency: &HashMap<u64, Vec<(u64, f64)>>) -> Vec<Vec<u64>> {
    let mut visited: HashSet<u64> = HashSet::new();
    let mut components: Vec<Vec<u64>> = Vec::new();

    for &node in adjacency.keys() {
        if visited.contains(&node) {
            continue;
        }
        let mut component: Vec<u64> = Vec::new();
        let mut stack: Vec<u64> = vec![node];
        while let Some(current) = stack.pop() {
            if visited.insert(current) {
                component.push(current);
                if let Some(neighbors) = adjacency.get(&current) {
                    for &(neighbor, _) in neighbors {
                        if !visited.contains(&neighbor) {
                            stack.push(neighbor);
                        }
                    }
                }
            }
        }
        component.sort();
        components.push(component);
    }

    components
}

pub fn degree_centrality(adjacency: &HashMap<u64, Vec<(u64, f64)>>) -> HashMap<u64, f64> {
    let n = adjacency.len() as f64;
    if n <= 1.0 {
        return adjacency.keys().map(|&k| (k, 0.0)).collect();
    }
    adjacency
        .iter()
        .map(|(&node, neighbors)| (node, neighbors.len() as f64 / (n - 1.0)))
        .collect()
}

// 5f93f983
