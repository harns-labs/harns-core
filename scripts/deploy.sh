#!/usr/bin/env bash
set -euo pipefail

CLUSTER="${1:-devnet}"
PROGRAM_NAME="harns"
DEPLOY_KEYPAIR="${DEPLOY_KEYPAIR:-$HOME/.config/solana/id.json}"

echo "========================================="
echo " Harns Protocol -- Deploy"
echo " Cluster: $CLUSTER"
echo "========================================="

if ! command -v anchor &> /dev/null; then
    echo "Error: anchor CLI not found. Install with: cargo install --git https://github.com/coral-xyz/anchor avm --locked"
    exit 1
fi

if ! command -v solana &> /dev/null; then
    echo "Error: solana CLI not found."
    exit 1
fi

solana config set --url "$CLUSTER" --keypair "$DEPLOY_KEYPAIR"
echo "Solana config set to $CLUSTER"

echo "Building program..."
anchor build

echo ""
echo "Deploying $PROGRAM_NAME to $CLUSTER..."
anchor deploy --provider.cluster "$CLUSTER"

PROGRAM_ID=$(solana address -k target/deploy/${PROGRAM_NAME}-keypair.json)
echo "Deployed program ID: $PROGRAM_ID"

echo "========================================="
echo " Deployment complete"
echo "========================================="
