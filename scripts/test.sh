#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo " Harns Protocol -- Test Suite"
echo "========================================="

echo "[1/3] Building Anchor program..."
anchor build

echo "[2/3] Running Anchor tests..."
anchor test --skip-local-validator 2>&1 || {
    echo "Anchor tests failed."
    exit 1
}

echo "[3/3] Running SDK tests..."
cd sdk
npm install --silent
npm test 2>&1 || {
    echo "SDK tests failed."
    exit 1
}

echo "========================================="
echo " All tests passed"
echo "========================================="
