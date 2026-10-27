# Wolfi OpenSSL FIPS 140-3 Hardened Runtime

[![FIPS 140-3](https://img.shields.io/badge/FIPS-140--3%20provider%203.1.2-blue?style=for-the-badge&logo=shield)](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4985)
[![SLSA Build Level 3](https://img.shields.io/badge/SLSA-Build%20L3-orange?style=for-the-badge)](../README.md#3-supply-chain-slsa-build-level-3)
[![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey?style=for-the-badge)](LICENSE)

**OpenSSL 3.5.9** on **Wolfi** with the **OpenSSL FIPS Provider 3.1.2** (CMVP certificate [#4985](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4985)), both built from checksum-verified source.

---

## 🛡️ Architecture & Security Features

- **The validated module:** the FIPS provider is built from the `openssl-3.1.2.tar.gz` named in its security policy with `./Configure enable-fips`. The 3.5.9 core library loads it.
- **FIPS configuration:** `openssl.cnf` loads only the FIPS and base providers and sets `default_properties = fips=yes`, so default algorithm fetches come from the FIPS provider. An application can still load another provider explicitly.
- **What the certificate covers:** the module on its tested environments (Intel x86_64 Ubuntu, Debian, FreeBSD, Windows, macOS; Apple M1 macOS). Running it on Wolfi, and on arm64, is an operator-affirmed port. `melange/` builds the same module strictly by the security policy as Wolfi packages.
- **Flavors:**
  - **`openssl-dev` (`3.5.9-dev`):** OpenSSL binaries, C headers and the C toolchain.
  - **`openssl-standard` (`3.5.9`):** OpenSSL CLI and libraries with a busybox shell.
  - **`openssl-prod` (`3.5.9-distroless`):** no shell and no package manager.
  - All flavors run as UID/GID `65532:65532`.

---

## 📦 Runtime Flavors

| Target | Image Tag | Description |
| :--- | :--- | :--- |
| `openssl-dev` | `ghcr.io/taha2samy-3/openssl-fips:3.5.9-dev` | Development image with C headers and the C toolchain |
| `openssl-standard` | `ghcr.io/taha2samy-3/openssl-fips:3.5.9` | Standard runtime with OpenSSL binary and core shared libs |
| `openssl-prod` | `ghcr.io/taha2samy-3/openssl-fips:3.5.9-distroless` | Distroless: no shell, no package manager |

---

## 🚀 Quick Start

```bash
# Pull production distroless image
docker pull ghcr.io/taha2samy-3/openssl-fips:3.5.9-distroless

# Verify FIPS provider status
docker run --rm ghcr.io/taha2samy-3/openssl-fips:3.5.9 list -providers -verbose
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
