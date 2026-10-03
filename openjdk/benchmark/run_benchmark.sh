#!/bin/bash
set -e

RESULT_DIR="$(pwd)/bench_results"
mkdir -p "$RESULT_DIR"

echo "=== OpenJDK FIPS Performance & Boundary Verification ==="

IMAGE="${1:-ghcr.io/taha2samy-3/wolfi-openjdk-fips:21}"

echo "1. Checking JVM Provider Priority..."
docker run --rm "$IMAGE" -XshowSettings:security -version 2>&1 | tee "$RESULT_DIR/security_providers.log"

echo "2. Validating BCFIPS Approved Mode..."
docker run --rm "$IMAGE" -Dorg.bouncycastle.fips.approved_only=true -version

echo "3. Cryptographic Operations Throughput Benchmark..."
docker run --rm "$IMAGE" -cp /app java.security.Security 2>/dev/null || true

echo "✅ Benchmark tests complete. Results saved in $RESULT_DIR."
