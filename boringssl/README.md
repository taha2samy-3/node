# Wolfi BoringSSL FIPS 140-3 Hardened Runtime

[![FIPS 140-3](https://img.shields.io/badge/FIPS-140--3%20Validated-blue?style=for-the-badge&logo=shield)](https://github.com/taha2samy-3/node)
[![Zero CVE](https://img.shields.io/badge/Zero--CVE-Wolfi%20OS-brightgreen?style=for-the-badge)](https://github.com/chainguard-dev)
[![SLSA Level 3](https://img.shields.io/badge/SLSA-Level%203-orange?style=for-the-badge)](https://github.com/taha2samy-3/node/actions)
[![License](https://img.shields.io/badge/License-OpenSSL-lightgrey?style=for-the-badge)](LICENSE)

A high-assurance container runtime delivering **Google BoringSSL** with the **BoringCrypto Module (BCM) FIPS 140-3** cryptographic core (NIST CMVP Certificate [#4735](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4735) / [#5104](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/5104)) compiled from source using Clang with `-DFIPS=1` and strictly enforced on **Wolfi OS** (undistro).

---

## 🛡️ Architecture & Security Features

- **Built from Source with FIPS:** Full source compilation of BoringSSL with `-DFIPS=1 -DBUILD_SHARED_LIBS=1` using Clang and `lld`.
- **Integrity Sealed Boundary:** BCM `.text` section HMAC-SHA256 hashed and injected directly via Google's `inject_hash` tool.
- **Power-On Self-Tests (POST):** Automated Known Answer Tests (KAT) for AES-GCM, SHA-256, HMAC, RSA, and ECDSA executed on initial module load.
- **Wolfi Minimal Attack Surface:** Glibc-based zero-known-CVE OS layer with isolated development toolchains.
- **Multi-Stage Flavors:**
  - **`boringssl-dev` (`fips-2024-dev`):** `bssl` CLI + C headers, compilers, build utilities, and test suites.
  - **`boringssl-standard` (`latest`):** `bssl` CLI + runtime shared libraries (`libcrypto.so`, `libssl.so`, `fips.so`) + non-root busybox shell.
  - **`boringssl-prod` (`distroless`):** Distroless container running as non-root UID/GID `65532:65532` without shells or package managers.

---

## 📦 Runtime Flavors

| Target | Image Tag | Description |
| :--- | :--- | :--- |
| `boringssl-dev` | `ghcr.io/taha2samy-3/boringssl-fips:dev` | Development image with C headers, compiler, and debug tools |
| `boringssl-standard` | `ghcr.io/taha2samy-3/boringssl-fips:latest` | Standard runtime with `bssl` CLI and core shared libs |
| `boringssl-prod` | `ghcr.io/taha2samy-3/boringssl-fips:distroless` | Hardened distroless container for secure microservices |

---

## 🚀 Quick Start

```bash
# Pull standard image
docker pull ghcr.io/taha2samy-3/boringssl-fips:latest

# Verify FIPS mode indicator
docker run --rm ghcr.io/taha2samy-3/boringssl-fips:latest isfips
```

---

## 🧪 Automated Test Suite

Located under `boringssl/tests/`:
- `test_01_core_policy.py`: `bssl isfips` verification, power-on self-test (POST) integrity, and non-root UID enforcement.
- `test_02_hashing_and_digests.py`: SHA-256 (NIST test vectors) and SHA-1 digest verification.

```bash
# Run tests
pytest boringssl/tests/ -v --image ghcr.io/taha2samy-3/boringssl-fips:latest
```

---

## 🔨 Build with Docker Bake

```bash
docker buildx bake boringssl-dev boringssl-standard boringssl-prod
```
