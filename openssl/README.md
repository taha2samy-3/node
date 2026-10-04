# Wolfi OpenSSL FIPS 140-3 Hardened Runtime

[![FIPS 140-3](https://img.shields.io/badge/FIPS-140--3%20Validated-blue?style=for-the-badge&logo=shield)](https://github.com/taha2samy-3/node)
[![Zero CVE](https://img.shields.io/badge/Zero--CVE-Wolfi%20OS-brightgreen?style=for-the-badge)](https://github.com/chainguard-dev)
[![SLSA Level 3](https://img.shields.io/badge/SLSA-Level%203-orange?style=for-the-badge)](https://github.com/taha2samy-3/node/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey?style=for-the-badge)](LICENSE)

A high-assurance container runtime delivering **OpenSSL 3.5.x** with the **FIPS 140-3 cryptographic module** built from source and strictly enforced on **Wolfi OS** (undistro).

---

## 🛡️ Architecture & Security Features

- **Built from Source with FIPS:** Full source compilation of OpenSSL 3.5 with `enable-fips` and runtime integrity checks.
- **Strict FIPS Configuration:** Hardened `openssl.cnf` and `fipsmodule.cnf` setting the `fips` provider as default with strict fallback rejection.
- **Wolfi Minimal Attack Surface:** Glibc-based zero-known-CVE OS layer with isolated development toolchains.
- **Multi-Stage Flavors:**
  - **`openssl-dev` (`3.5.9-dev`):** OpenSSL binaries + C headers, compilers, build utilities, and test suites.
  - **`openssl-standard` (`3.5.9`):** OpenSSL CLI + runtime libraries + basic shell.
  - **`openssl-prod` (`3.5.9-distroless`):** Distroless container running as non-root UID/GID `65532:65532` without shells or package managers.

---

## 📦 Runtime Flavors

| Target | Image Tag | Description |
| :--- | :--- | :--- |
| `openssl-dev` | `ghcr.io/taha2samy-3/openssl-fips:3.5.9-dev` | Development image with C headers, compiler, and debug tools |
| `openssl-standard` | `ghcr.io/taha2samy-3/openssl-fips:3.5.9` | Standard runtime with OpenSSL binary and core shared libs |
| `openssl-prod` | `ghcr.io/taha2samy-3/openssl-fips:3.5.9-distroless` | Hardened distroless container for secure microservices |

---

## 🚀 Quick Start

```bash
# Pull production distroless image
docker pull ghcr.io/taha2samy-3/openssl-fips:3.5.9-distroless

# Verify FIPS provider status
docker run --rm ghcr.io/taha2samy-3/openssl-fips:3.5.9 openssl list -providers -verbose
```

---

## 🧪 Automated Test Suite

Located under `openssl/tests/`:
- `test_01_core_policy.py`: Provider loading and approved FIPS operational mode.
- `test_02_hashing_and_digests.py`: Approval of SHA-2/SHA-3, rejection of MD5.
- `test_03_symmetric_ciphers.py`: AES-GCM / AES-CBC compliance, rejection of DES/3DES.
- `test_04_mac_integrity.py`: HMAC and CMAC verification.
- `test_05_asymmetric_and_pqc.py`: RSA key lengths, EC curves, and PQC transitions.
- `test_06_architecture_compliance.py`: Shared library link integrity.
- `test_11_network_tls.py`: Strict TLS 1.3 / 1.2 negotiation with FIPS suites (marked `network`: needs internet access, not part of the CI gate).

```bash
# As CI runs it (standard and distroless images; the dev image gets a smoke check)
python .github/scripts/fips_tests.py --unit openssl-3.5 --arch amd64 --out fips-results

# Including the internet-dependent TLS tests
cd openssl/tests && pytest -v --image ghcr.io/taha2samy-3/openssl-fips:3.5.9
```

Three tests are marked `xfail(strict=True)`: the certified 3.1.2 provider does not enforce a minimum HMAC key length (added in the 3.4 provider) and offers X25519 under `fips=yes`. They are shown as **known limitations** on the dashboard and turn into failures if a future provider changes that behaviour.

---

## 🔨 Build with Docker Bake

```bash
docker buildx bake openssl-dev openssl-standard openssl-prod
```

The OpenSSL source tarballs are verified against pinned SHA-256 checksums. OpenSSL 3.5 (core library), the static base image and the Wolfi packages are updated by the daily dependency pull request; the **FIPS provider 3.1.2** is the validated module (certificate #4985) and only changes by hand when NIST lists a new certificate.
