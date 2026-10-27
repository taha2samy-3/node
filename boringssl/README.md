# Wolfi BoringSSL FIPS Hardened Runtime

[![FIPS Build Flags](https://img.shields.io/badge/BoringSSL-FIPS%20Build%20Flags%20(-DFIPS%3D1)-blue?style=for-the-badge&logo=shield)](https://github.com/taha2samy-3/node)
[![License](https://img.shields.io/badge/License-OpenSSL-lightgrey?style=for-the-badge)](LICENSE)

> **Not a validated module.** This image builds BoringSSL commit [`85897d0`](https://boringssl.googlesource.com/boringssl/+/85897d07196b7bf164dbd4673fc78b762aff3e8b) (2024-05-28, `BORINGSSL_COMMIT` in `docker-bake.hcl`) with `-DFIPS=1`, using Wolfi's current Clang, Go and CMake. That adds the module integrity check and self-tests, but it is not a CMVP-validated module:
>
> - CMVP certificate [#4735](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4735) (BoringCrypto 2022061300) covers BoringSSL tag `fips-20220613` (commit `0c6f40132b8`) built with the toolchain its security policy names.
> - That tag does not compile with Wolfi's clang 23, which stops on a `-Werror` warning in `crypto/internal.h`. A validated build needs the policy's older toolchain.
> - BoringSSL has no approved-only mode, so non-approved algorithms such as MD5 stay available.
>
> The image tag `20240528` is the date of the pinned commit, not a FIPS release.

---

## 🛡️ Architecture & Security Features

- **Built from source in FIPS mode:** `-DFIPS=1 -DBUILD_SHARED_LIBS=1` with Clang and `lld`; the build fails unless `bssl isfips` reports FIPS mode.
- **Integrity check:** the module's code is hashed at build time and checked when the library loads.
- **Self-tests:** BoringSSL's FIPS self-tests run when the module is first used.
- **Flavors:**
  - **`boringssl-dev` (`20240528-dev`):** `bssl` CLI, C headers and the C toolchain, with a bash shell.
  - **`boringssl-standard` (`20240528`, `latest`):** `bssl` CLI and the shared libraries `libcrypto.so` and `libssl.so`, with a busybox shell, running as non-root.
  - **`boringssl-prod` (`20240528-distroless`):** no shell and no package manager, running as UID/GID `65532:65532`.

---

## 📦 Runtime Flavors

| Target | Image Tag | Description |
| :--- | :--- | :--- |
| `boringssl-dev` | `ghcr.io/taha2samy-3/boringssl-fips:dev` | Development image with C headers and the C toolchain |
| `boringssl-standard` | `ghcr.io/taha2samy-3/boringssl-fips:latest` | Standard runtime with `bssl` CLI and core shared libs |
| `boringssl-prod` | `ghcr.io/taha2samy-3/boringssl-fips:distroless` | Distroless: no shell, no package manager |

---

## 🚀 Quick Start

```bash
# Pull standard image
docker pull ghcr.io/taha2samy-3/boringssl-fips:latest

# Verify FIPS mode indicator
docker run --rm --entrypoint /usr/local/bin/bssl ghcr.io/taha2samy-3/boringssl-fips:latest isfips
```

---

## 🧪 Automated Test Suite

Located under `boringssl/tests/` (82 tests):
- `test_01_core_policy.py`: Operational health, `bssl isfips` indicators, power-on self-test (POST) integrity, non-root execution, and distroless boundary enforcement.
- `test_02_hashing_and_digests.py`: SHA-2 family digests (SHA-224, SHA-256, SHA-384, SHA-512, SHA-512/256) compared with Python `hashlib`, multi-block boundaries, and legacy digests (MD5 is available: BoringSSL has no approved-only mode).
- `test_03_symmetric_and_drbg.py`: DRBG output, and the cipher suites `bssl ciphers` lists (AES-GCM, AES-CBC, ECDHE present; RC4, DES, NULL, EXPORT and similar absent, which BoringSSL never implements).
- `test_04_asymmetric_and_signatures.py`: RSA key generation (2048, 3072, 4096-bit), digital signatures with exact length verification, error handling, and Ed25519 keypair generation.
- `test_05_fips_crypto_primitives.py`: Direct `libcrypto.so` validation of `FIPS_mode()`, permanent approved mode (`FIPS_mode_set(0)` blocked), `BORINGSSL_self_test_all()`, BoringCrypto integrity hash verification, AES-128/256-GCM encrypt/decrypt round trips, tag tampering rejection, and RFC 4231 HMAC-SHA256/512 vectors.

```bash
# Run tests
pytest boringssl/tests/ -v --image ghcr.io/taha2samy-3/boringssl-fips:latest
```

---

## 🔨 Build with Docker Bake

```bash
docker buildx bake boringssl-dev boringssl-standard boringssl-prod
```
