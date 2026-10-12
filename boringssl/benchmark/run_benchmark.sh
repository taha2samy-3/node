#!/bin/bash
set -e
rm -rf ./bench_results/*.log
RESULT_DIR="$(pwd)/bench_results"
mkdir -p "$RESULT_DIR"

docker rmi boringssl-bench debian-bench -f 2>/dev/null || true

docker build -t boringssl-bench - <<EOF
FROM ghcr.io/taha2samy-3/boringssl-fips:latest
USER root
ENTRYPOINT ["/usr/local/bin/bssl"]
EOF

docker build -t debian-bench - <<EOF
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["openssl"]
EOF

echo "Running BoringSSL FIPS speed benchmark..."
docker run --rm boringssl-bench speed > "$RESULT_DIR/boringssl_fips.log" 2>&1

echo "Running Debian baseline OpenSSL benchmark..."
docker run --rm debian-bench speed -bytes 16384 -evp aes-256-gcm sha256 sha512 > "$RESULT_DIR/debian_baseline.log" 2>&1
docker run --rm debian-bench speed rsa2048 ecdsap256 >> "$RESULT_DIR/debian_baseline.log" 2>&1

echo "✅ BoringSSL Benchmarks complete. Results saved in $RESULT_DIR"
