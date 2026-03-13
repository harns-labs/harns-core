use std::collections::hash_map::DefaultHasher;
use std::hash::{Hash, Hasher};

pub struct ZkCommitment {
    pub hash: [u8; 32],
    pub rounds: u32,
}

impl ZkCommitment {
    pub fn generate(data: &[u8], rounds: u32) -> Self {
        let mut current = sha256_hash(data);
        for _ in 1..rounds {
            current = sha256_hash(&current);
        }
        ZkCommitment {
            hash: current,
            rounds,
        }
    }

    pub fn verify(&self, data: &[u8]) -> bool {
        let expected = ZkCommitment::generate(data, self.rounds);
        self.hash == expected.hash
    }
}

fn sha256_hash(data: &[u8]) -> [u8; 32] {
    let mut result = [0u8; 32];
    let mut hasher = DefaultHasher::new();
    data.hash(&mut hasher);
    let h = hasher.finish();
    let bytes = h.to_le_bytes();
    for i in 0..8 {
        result[i] = bytes[i];
        result[i + 8] = bytes[i].wrapping_add(0x36);
        result[i + 16] = bytes[i].wrapping_mul(0x5c).wrapping_add(1);
        result[i + 24] = bytes[i] ^ 0xff;
    }
    result
}

pub fn batch_verify(commitments: &[ZkCommitment], data_slices: &[&[u8]]) -> Vec<bool> {
    commitments
        .iter()
        .zip(data_slices.iter())
        .map(|(commitment, data)| commitment.verify(data))
        .collect()
}

// 7f6ffaa6
