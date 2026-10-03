# Wolfi OpenJDK FIPS 140-3 Hardened Runtime

[![FIPS 140-3](https://img.shields.io/badge/FIPS-140--3%20Enforced-blue?style=for-the-badge&logo=shield)](https://github.com/taha2samy/openjdk)
[![Zero CVE](https://img.shields.io/badge/Zero--CVE-Wolfi%20OS-brightgreen?style=for-the-badge)](https://github.com/chainguard-dev)
[![SLSA Level 3](https://img.shields.io/badge/SLSA-Level%203-orange?style=for-the-badge)](https://github.com/taha2samy-3/node/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey?style=for-the-badge)](LICENSE)

A high-assurance, **FIPS 140-3 compliant** OpenJDK container image designed for mission-critical, enterprise, and regulated environments (FedRAMP, DoD, HIPAA, PCI-DSS).

Built on top of **Wolfi OS** (undistro) with **Eclipse Adoptium OpenJDK 21** and **Bouncy Castle FIPS Java modules** (`bc-fips`, `bcpkix-fips`, `bctls-fips`).

---

## 🛡️ Architecture & Security Controls

This runtime enforces a strict **Cryptographic Boundary** at the JVM layer:

1. **Wolfi OS Minimal Base:** Glibc-based zero-known-CVE minimal attack surface with rapid vulnerability remediation.
2. **Bouncy Castle FIPS Priority:** `BCFIPS` is registered as Security Provider 1, and `BCJSSE` as Provider 2 in `conf/security/java.security`.
3. **Approved Mode Enforcement:** JVM property `org.bouncycastle.fips.approved_only=true` is enabled by default to strictly prohibit non-approved cryptographic primitives.
4. **KeyStore Integrity:** System certificates and keystores operate exclusively on **BCFKS** (Bouncy Castle FIPS KeyStore) format.
5. **NIST SP 800-90A DRBG:** Deterministic Random Bit Generator seeded by system entropy sources (`/dev/urandom`).
6. **Strict Cryptographic Restrictions:** Explicit rejection of:
   - Weak hashing: MD4, MD5, SHA-1 (for digital signatures).
   - Insecure ciphers: DES, 3DES, RC4, anonymous TLS cipher suites.
   - Weak keys: RSA < 2048-bit, DSA < 2048-bit, non-NIST elliptic curves.
   - Insecure protocols: SSLv3, TLS 1.0, TLS 1.1.

---

## 📦 Runtime Flavors

Every release provides three distinct tiers optimized for different stages of the delivery lifecycle:

| Target | Image Tag | Base | Capabilities | Intended Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`dev`** | `ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-dev` | Wolfi Dev | Full JDK + shell (`bash`) + package manager (`apk`) + debug utilities (`curl`, `jq`, `git`, `gdb`) | CI/CD build environments, debugging & compiling |
| **`standard`** | `ghcr.io/taha2samy-3/wolfi-openjdk-fips:21` | Wolfi Base | JRE + Glibc + Libstdc++ + CA Certs + Bouncy Castle FIPS | Standard production workloads requiring basic maintenance |
| **`prod`** | `ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-distroless` | Distroless | JRE + CA Certs + BCFIPS only, **No Shell, No Package Manager, Non-Root (65532:65532)** | Hardened zero-CVE production deployment |

---

## 🚀 Quick Start

### Pulling from GitHub Container Registry (GHCR)

```bash
# Pull hardened production distroless image
docker pull ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-distroless

# Pull standard runtime
docker pull ghcr.io/taha2samy-3/wolfi-openjdk-fips:21

# Pull development container
docker pull ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-dev
```

### Running Applications

The runtime sets `JAVA_HOME=/opt/java` and configures `JAVA_TOOL_OPTIONS` with the FIPS provider configurations:

```bash
docker run --rm ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-distroless -version
```

Sample multi-stage application Dockerfile:

```dockerfile
# Build Stage
FROM ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-dev AS builder
WORKDIR /app
COPY . .
RUN ./mvnw clean package -DskipTests

# Production Stage
FROM ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-distroless
WORKDIR /app
COPY --from=builder /app/target/myapp.jar app.jar
ENTRYPOINT ["/opt/java/bin/java", "-jar", "app.jar"]
```

---

## 🧪 Automated Verification & Test Suite

The module includes a comprehensive pytest and JUnit test suite located in `tests/`:

- **Core & Provider Verification:** `1_core_test.py`
  - Validates `BCFIPS` is registered at position 1.
  - Verifies approved-only mode is active (`CryptoServicesRegistrar.isInApprovedOnlyMode() == true`).
- **Cryptographic Negative Rejection:** `2_crypto_negative_test.py`
  - Rejection of MD4, MD5, SHA-1 signatures.
  - Rejection of DES, 3DES, RC4.
  - Rejection of RSA keys < 2048-bit, DSA keys < 2048-bit, and non-NIST curves.
  - Rejection of short HMAC keys and short salt PBKDF2.
- **Cryptographic Positive Operations:** `3_crypto_positive_test.py`
  - Validation of AES-GCM, AES-CBC (128/192/256-bit).
  - Validation of RSA-2048/3072/4096 and ECDSA P-256/P-384/P-521.
  - Validation of HMAC-SHA256, PBKDF2, and ECDH key agreement.
- **KeyStore & Truststore:** `4_keystore_test.py`
  - Enforces `BCFKS` as default KeyStore type.
  - Validates rejection of legacy `JKS` keystores.
- **Network & TLS:** `5_network_test.py`
  - Validates TLS 1.3 and TLS 1.2 with BCFIPS cipher suites.
  - Enforces rejection of anonymous and null ciphers.
- **Random Number Generation:** `6_rng_test.py`
  - Validates NIST SP 800-90A DRBG entropy generation.

### Running Tests Locally

```bash
cd openjdk
pytest tests/ -v
```

---

## 🔨 Building with Docker Bake

From the repository root:

```bash
# Build all OpenJDK flavors
docker buildx bake openjdk-dev openjdk-standard openjdk-prod

# Build standalone from openjdk directory
cd openjdk
docker buildx bake -f docker-bake.hcl
```

---

## 📊 Supply Chain & Attestation

Every image built in the pipeline includes:
- **SLSA Level 3 Provenance:** Digitally signed with GitHub OIDC token.
- **CycloneDX Software Bill of Materials (SBOM):** Embedded directly at `/usr/share/sbom/application.cdx.json`.
- **Trivy Vulnerability Scans:** Continuous scanning for CVEs against the Wolfi security advisories database.
