<p align="center">
  <img src="./assets/banner.png" alt="clstr banner" width="100%" />
</p>

<h1 align="center">clstr</h1>
<p align="center"><strong>Zero-knowledge wallet cluster analysis on Solana</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build" />
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Solana-black?style=flat-square&logo=solana&logoColor=white" alt="Solana" />
  <a href="https://clstr.network">
    <img src="https://img.shields.io/badge/clstr.network-DC143C?style=flat-square&logo=google-chrome&logoColor=white" alt="Website" />
  </a>
  <a href="https://x.com/clstrlabs">
    <img src="https://img.shields.io/badge/@clstrlabs-000000?style=flat-square&logo=x&logoColor=white" alt="Twitter" />
  </a>
</p>

---

clstr is a Solana-native wallet clustering protocol that combines on-chain burn-and-flag mechanics with off-chain zero-knowledge proofs and graph analysis. The system monitors wallet behaviors, clusters related addresses using the Louvain algorithm, and publishes tamper-proof risk scores on-chain.

| Component | Description |
|-----------|-------------|
| **clstr_core** | Anchor program handling burn, flag, and score operations |
| **clstr_math** | Louvain clustering and graph utilities in pure Rust |
| **sdk** | TypeScript client for interacting with the on-chain program |
| **cli** | Command-line tool for operators and validators |

---

## Architecture

```mermaid
flowchart TD
    A[Solana RPC] -->|Transaction stream| B[Ingestion Layer]
    B --> C[ZK Proof Engine]
    C --> D[Louvain Clustering]
    D --> E[Risk Scorer]
    E --> F[clstr_core Program]
    F --> G[Solana Blockchain]

    subgraph Off-Chain
        B
        C
        D
        E
    end

    subgraph On-Chain
        F
        G
    end

    style A fill:#1a1a1a,stroke:#DC143C,color:#ffffff
    style B fill:#1a1a1a,stroke:#DC143C,color:#ffffff
    style C fill:#1a1a1a,stroke:#DC143C,color:#ffffff
    style D fill:#1a1a1a,stroke:#DC143C,color:#ffffff
    style E fill:#1a1a1a,stroke:#DC143C,color:#ffffff
    style F fill:#DC143C,stroke:#ffffff,color:#ffffff
    style G fill:#DC143C,stroke:#ffffff,color:#ffffff
```

---

## Features

- On-chain burn-and-flag mechanism via Anchor program
- Zero-knowledge proof generation using SHA-256 commitments
- Louvain community detection for wallet clustering
- Real-time transaction monitoring via Solana RPC webhooks
- TypeScript SDK for seamless dApp integration
- CLI tooling for validators and operators
- Configurable risk thresholds and scoring parameters

---

## Installation

```bash
git clone https://github.com/clstr-labs/clstr.git
cd clstr
```

### Build the Anchor Program

```bash
anchor build
```

### Install SDK Dependencies

```bash
cd sdk
npm install
```

### Build the CLI

```bash
cargo build --release -p clstr-cli
```

---

## Usage

### Flag a Wallet

```typescript
import { ClstrClient } from "./clstr-sdk";

const client = new ClstrClient(program, provider);
await client.flagWallet(targetPubkey, riskScore, zkProofHash);
```

### Run Clustering

```bash
clstr-cli cluster --input transactions.json --output clusters.json
```

### Verify a ZK Proof

```bash
clstr-cli verify --proof proof.json --commitment 0xabc123
```

---

## Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SOLANA_RPC_URL` | Solana RPC endpoint for connections and webhooks | - |
| `CLUSTER_RESOLUTION` | Louvain resolution parameter | `1.0` |
| `MIN_RISK_THRESHOLD` | Minimum score to trigger a flag | `0.65` |
| `ZK_HASH_ROUNDS` | Number of SHA-256 iterations | `256` |
| `PROGRAM_ID` | Deployed program address | `E1iTSqt1YkW6LoNXMspEoxsdotzEdmn3QjEJL5R3NUwe` |

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

Built on Solana.

<!-- 1385974e -->
