<p align="center"><img src="assets/brand/banner.svg" alt="Secure Runtimes: hardened, signed and scanned container runtimes on Wolfi" width="100%"></p>

# High-Assurance Secure Container Runtimes

[![FIPS 140-3](https://img.shields.io/badge/FIPS-140--3%20Hardened-blue?style=for-the-badge&logo=shield)](https://github.com/taha2samy-3/node)
[![Zero CVE](https://img.shields.io/badge/Zero--CVE-Wolfi%20OS-brightgreen?style=for-the-badge)](https://github.com/chainguard-dev)
[![SLSA Level 3](https://img.shields.io/badge/SLSA-Level%203-orange?style=for-the-badge)](https://github.com/taha2samy-3/node/actions)
[![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey?style=for-the-badge)](LICENSE)

A collection of **enterprise-grade, zero-CVE, FIPS 140-3 compliant container base images** built upon [Chainguard's Wolfi OS](https://github.com/chainguard-dev) undistro. Designed for zero-trust security postures, regulated industries (FedRAMP, DoD, HIPAA, PCI-DSS), and high-security microservice architectures.

---

## 🌟 Supported Runtimes & Flavors

| Runtime | Versions | Flavors Available | FIPS 140-3 Compliant | Base OS |
| :--- | :--- | :--- | :---: | :--- |
| **OpenJDK** | `8`, `17`, `21`, `25` (LTS) | `dev`, `standard`, `distroless` | ✅ | Wolfi Linux + BCFIPS |
| **OpenSSL** | `3.5.5` | `dev`, `standard`, `distroless` | ✅ | Wolfi Linux + FIPS Module |
| **Node.js FIPS** | `22`, `24` | `dev`, `standard`, `distroless` | ✅ | Wolfi Linux + OpenSSL FIPS Module |
| **Node.js** | `18`, `20`, `22`, `24`, `26` | `dev`, `prod` | Optional | Wolfi Linux |
| **Go** | `1.22`, `1.23`, `1.24` | `dev`, `prod` | Optional | Wolfi Linux |
| **Python** | `3.10`, `3.11`, `3.12`, `3.13`, `3.14` | `dev`, `prod` | Optional | Wolfi Linux |
| **Bun** | `1` | `dev`, `prod` | Optional | Wolfi Linux |

---

## 🛡️ Security Architecture & Controls

### 1. Zero-CVE Foundation
All images are built directly on Wolfi Linux, a declarative Linux undistro optimized for container security:
- **Zero Shell / Distroless:** Production containers (`prod` / `distroless`) ship with **no shell (`sh`/`bash`)** and **no package manager (`apk`)**.
- **Non-Root Execution:** All production runtime targets execute strictly under non-privileged UID/GID `65532:65532`.
- **Rapid Patching:** Wolfi rolling packages remediate upstream CVEs within hours of public disclosure.

### 2. Strict FIPS 140-3 Enforcement
- **[OpenJDK FIPS](openjdk/README.md):** Powered by **Eclipse Adoptium OpenJDK 8, 17, 21 and 25** and **Bouncy Castle FIPS** (`bc-fips`, `bcpkix-fips`, `bctls-fips`). Overrides JVM security configuration (`conf/security/java.security`) to force BCFIPS as Provider 1, BCFKS as default keystore, and SP 800-90A DRBG entropy.
- **[OpenSSL FIPS](openssl/README.md):** Built from source with `--enable-fips`. Strict `openssl.cnf` policy locks down legacy algorithms (MD5, DES, 3DES, RC4) and permits only approved cryptographic mechanisms.
- **Node.js FIPS:** Wolfi's Node.js links the system OpenSSL, which loads the validated OpenSSL FIPS 3.1.2 provider from the OpenSSL FIPS image. `fips=yes` is the default property and `--force-fips` (via `NODE_OPTIONS`) stops application code from calling `crypto.setFips(false)`, so MD5, ChaCha20 and RSA-1024 are rejected. Every build runs `/usr/share/nodejs-fips/fips-check.js` and fails if FIPS mode is not enforced.

### 3. Supply Chain Security (SLSA Level 3)
- **SLSA Provenance:** Cryptographically signed attestations generated via GitHub Actions OIDC and published to the GitHub Container Registry (GHCR).
- **CycloneDX SBOMs:** Every image contains a machine-readable Software Bill of Materials (SBOM) generated in CycloneDX JSON format.
- **Continuous Scanning:** Integrated Trivy vulnerability scanning, CIS Docker benchmark audits, and license compliance checks.

---

## 🚀 Quick Start

### Pulling from GHCR

```bash
# OpenJDK 21 FIPS (Production Distroless)
docker pull ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-distroless

# OpenSSL 3.5 FIPS (Production Distroless)
docker pull ghcr.io/taha2samy-3/openssl-fips:3.5.5-distroless

# Node.js 22 (Production)
docker pull ghcr.io/taha2samy-3/node:22

# Node.js 24 FIPS (Production Distroless)
docker pull ghcr.io/taha2samy-3/node-fips:24-distroless
```

---

## 🛠️ Building with Docker Bake

This repository utilizes Docker Buildx Bake (`docker-bake.hcl`) for multi-platform, declarative container builds:

```bash
# Build all OpenJDK FIPS targets (8, 17, 21, 25), or a single one
docker buildx bake openjdk
docker buildx bake openjdk-21-prod

# Build all OpenSSL FIPS targets
docker buildx bake openssl-dev openssl-standard openssl-prod

# Build all Node.js targets
docker buildx bake dev-22 prod-22

# Build all Node.js FIPS targets (needs the OpenSSL FIPS image)
docker buildx bake node-fips

# Build the entire default group across all runtimes
docker buildx bake
```

---

## 🧪 Testing & Verification

Every FIPS image has a test suite. CI runs it on amd64 and arm64 after each build and on every pull request that changes the image, and the results appear on the dashboard's **FIPS tests** tab:

| Image | Suite | What it checks |
| :--- | :--- | :--- |
| OpenSSL FIPS | `openssl/tests/` | Provider status and self-tests, approved / rejected digests, ciphers, MACs, KDFs, key sizes and curves, PQC, TLS |
| OpenJDK FIPS | `openjdk/tests/` | BCFIPS provider order, approved-only mode, rejected algorithms, BCFKS keystores, TLS 1.2 / 1.3, DRBG |
| Node.js FIPS | `nodejs/fips/tests/` | `crypto.getFips()`, `setFips(false)` blocked, rejected digests / ciphers / curves / scrypt, RSA sizes, HMAC, PBKDF2, TLS 1.3 handshake, non-root and distroless checks |

```bash
# Run a suite the way CI does, against every flavor of one image (pull or build the images first)
pip install pytest allure-pytest pyyaml
python .github/scripts/fips_tests.py --unit openssl-3.5 --arch amd64 --out fips-results
python .github/scripts/fips_tests.py --unit openjdk-21 --arch amd64 --out fips-results
python .github/scripts/fips_tests.py --unit node-fips-24 --arch amd64 --out fips-results

# Or call pytest directly against one image
pytest openssl/tests -m "not network" --image ghcr.io/taha2samy-3/openssl-fips:3.5.5
pytest nodejs/fips/tests --image ghcr.io/taha2samy-3/node-fips:24-distroless --flavor prod
```

A few OpenSSL tests are marked as strict expected failures. They cover known limits of the certified OpenSSL FIPS provider 3.1.2 (see [openssl/README.md](openssl/README.md)), and the run fails if one of them starts passing.

---

## 🔁 Build, Test and Update Lifecycle

### Per-image builds and scans

Every change rebuilds, re-attests, rescans and republishes on the dashboard **only the images it affects**:

1. `.github/scripts/plan_images.py` gives every bake target a fingerprint: its resolved bake definition, the Dockerfile stages it builds, the local files those stages copy, and the fingerprints of images it consumes (Node.js FIPS consumes the OpenSSL FIPS image).
2. **Build and Push Images** compares that fingerprint with the `io.github.taha2samy-3.build.fingerprint` label of the published image and rebuilds only targets that differ or are not published yet. A build that failed or was cancelled is retried on the next run.
3. **Generate Security Dashboard and Deploy** scans only the rebuilt images (plus any image without a stored report) and keeps the last reports of everything else, which are published with the site under `reports/`.

Examples: bumping `NODE_22_FULL_VERSION` rebuilds `node:22`, `node:22-dev` and `node-fips:22*`; editing `openjdk/conf/java-8.security` rebuilds the three Java 8 images; editing a README rebuilds nothing.

Both workflows can be run by hand: **Build and Push Images** takes `rebuild` (`changed`, `all`, or ids such as `node-22 openjdk`) and the dashboard workflow takes `rescan` (`missing`, `all`, or ids).

### Native amd64 and arm64

Each image is built twice, natively and without QEMU: on `ubuntu-24.04` for `linux/amd64` and on `ubuntu-24.04-arm` for `linux/arm64`. Both builds push by digest, and `.github/scripts/merge_manifests.py` joins them into one multi-platform tag, then checks that both platforms are present. Trivy scans, CIS checks, SBOM attestations and FIPS tests run once per architecture, and the dashboard has an **amd64 / arm64** switch. Provenance is attached to the multi-platform index.

### Dependency updates

`.github/dependencies.yml` lists every pinned version and checksum in `docker-bake.hcl` and says how to update it:

- **Certified FIPS modules**: the OpenSSL FIPS Provider 3.1.2 (CMVP certificate [#4985](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4985)) and Bouncy Castle `bc-fips` 2.1.1 (certificate [#4943](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4943)). These never change automatically. Only the validated version may be used, so they change by hand when NIST lists a new certificate.
- **Everything else** is updated by **Daily Dependency Update** (`.github/scripts/update_dependencies.py`): Wolfi packages (including every package installed in the OpenSSL images), base images by digest, the OpenSSL 3.5 LTS core source and its SHA-256, Eclipse Temurin JDK / JRE downloads and checksums, the Bouncy Castle TLS / utility jars (checked against Maven Central's `.sha256`), and the envoke release.

The script opens **one pull request per image family** (`runtimes`, `openssl-fips`, `openjdk-fips`, `base`) on the branch `automation/deps-<group>`, and handles it the way Dependabot does: an open PR is updated in place, a closed one is replaced by a fresh PR, and a group with no updates has its PR closed. Each PR lists the version changes and the images it will rebuild. Nothing is merged automatically.

The run also checks coverage, and fails if `docker-bake.hcl` gains a pinned variable (`*_VER`, `*_VERSION`, `*_SHA`, `*_SHA256`, `*_URL`, `*_IMAGE`) that `dependencies.yml` does not list. Run it locally with:

```bash
python .github/scripts/update_dependencies.py --dry-run                       # every group
python .github/scripts/update_dependencies.py --dry-run --group openjdk-fips  # one group
```

### Pull request check

**Pull Request Check** builds the images a pull request changes (linux/amd64, nothing is pushed) and runs the FIPS test suites against them. Make it a required status check in the `main` branch protection rules, so that a dependency update cannot be merged while it breaks an image or its FIPS behaviour.

### Benchmarks and certificate watch

- **FIPS Benchmarks** runs every week on both architectures. It measures each FIPS image against a non-FIPS baseline of the same software: stock OpenSSL on Alpine, this repository's regular Node.js image, and Eclipse Temurin with SunJCE. Results appear on the dashboard's **Benchmarks** tab, where the FIPS / baseline ratio is the number to compare.
- **FIPS Certificate Watch** (`.github/scripts/cmvp_watch.py`) checks the CMVP certificates every week. It opens or updates an issue labelled `fips-certificates` if a certificate is no longer Active, is less than a year from its sunset date, no longer lists the pinned version, or if the vendor has a newer certificate. The dashboard's **FIPS module** tab shows the same status.

---

## 📊 Security & Compliance Dashboard

The repository includes a modern web-based compliance dashboard built with React, Vite, and Tailwind-inspired styling located under `web/`:

```bash
cd web
npm install
npm run dev
```

The dashboard shows, for each image and each architecture (amd64 / arm64):
- Vulnerability posture and CVE breakdown.
- CIS benchmark pass/fail scores.
- Interactive SBOM package explorer.
- SLSA provenance and SBOM attestations, with the `gh attestation verify` commands.
- The FIPS module, its CMVP certificate status and sunset date.
- FIPS test results and benchmark results against non-FIPS baselines.

---

## 📁 Repository Structure

```
├── .github/
│   ├── dependencies.yml        # Every pinned version: certified FIPS modules vs. automatically updated
│   ├── workflows/
│   │   ├── build.yml           # Native amd64 + arm64 builds, multi-platform merge, attestation, FIPS tests
│   │   ├── docs.yml            # Security scans, CIS checks and the dashboard deployment
│   │   ├── pr-check.yml        # Builds and tests the images a pull request changes
│   │   ├── daily-image-update.yml # Daily dependency update pull requests
│   │   ├── benchmarks.yml      # Weekly FIPS vs. non-FIPS benchmarks
│   │   └── fips-certificates.yml  # Weekly CMVP certificate watch
│   ├── actions/                # bake-build, trivy-scan, attest-image, upload-dependency-graph
│   └── scripts/
│       ├── plan_images.py      # Decides which images to build, test, attest and scan
│       ├── merge_manifests.py  # Joins per-architecture digests into multi-platform tags
│       ├── update_dependencies.py # Resolves updates and manages the dependency PRs
│       ├── fips_tests.py       # Runs the FIPS test suite of an image and writes the dashboard report
│       ├── run_benchmarks.py   # FIPS vs. baseline benchmarks (bench/ holds the Node.js and Java programs)
│       └── cmvp_watch.py       # Checks the CMVP certificates of the FIPS modules
├── openjdk/                    # Wolfi OpenJDK FIPS 140-3 images
│   ├── dockerfile              # Multi-stage Wolfi + BCFIPS build
│   ├── conf/java-<v>.security  # Hardened FIPS 140-3 security policy per Java version
│   ├── render_security.py      # Renders conf/java-<v>.security from templates/
│   ├── tests/                  # pytest & JUnit verification suite
│   └── README.md               # OpenJDK module documentation
├── nodejs/                     # Node.js images (regular + FIPS stages)
│   ├── dockerfile              # dev / prod and fips-dev / fips-standard / fips-distroless
│   └── fips/                   # OpenSSL FIPS config, build-time FIPS check and tests/
├── openssl/                    # Wolfi OpenSSL FIPS 140-3 images
│   ├── dockerfile              # Source build with enable-fips, checksum-verified sources
│   ├── conf/openssl.cnf        # Hardened FIPS provider configuration
│   ├── tests/                  # pytest FIPS verification suite
│   └── README.md               # OpenSSL module documentation
├── go/, python/, bun/          # Regular runtime images
├── web/                        # React/Vite security dashboard
│   ├── src/                    # Dashboard pages and components
│   └── runtimes.yaml           # Runtime metadata and report mappings
├── docker-bake.hcl             # All bake targets and pinned versions
└── README.md                   # Project root documentation
```

---

## 📄 License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.