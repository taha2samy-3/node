# Wolfi OpenJDK FIPS 140-3 Hardened Runtime

[![FIPS 140-3](https://img.shields.io/badge/FIPS-140--3%20bc--fips%202.1.1-blue?style=for-the-badge&logo=shield)](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4943)
[![SLSA Build Level 3](https://img.shields.io/badge/SLSA-Build%20L3-orange?style=for-the-badge)](../README.md#3-supply-chain-slsa-build-level-3)
[![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey?style=for-the-badge)](LICENSE)

OpenJDK container images on **Wolfi** with **Eclipse Temurin 8, 17, 21 and 25 (LTS)** and the **Bouncy Castle FIPS Java API** (`bc-fips` 2.1.1, CMVP certificate [#4943](https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/4943)), with `bcutil-fips` and `bctls-fips`.

---

## 🛡️ Architecture & Security Controls

1. **Bouncy Castle first:** `BCFIPS` is security provider 1 and `BCJSSE` provider 2 in `conf/security/java.security`.
2. **Approved-only mode:** `JAVA_TOOL_OPTIONS` sets `org.bouncycastle.fips.approved_only=true`, so the BCFIPS provider refuses non-approved algorithms. A deployment that replaces `JAVA_TOOL_OPTIONS` also removes this setting and the boot class path that loads Bouncy Castle.
3. **Sun providers stay registered.** `Sun`, `SunRsaSign`, `SunEC` and `SunJCE` are providers 3 to 6. Code that requests an algorithm without naming a provider, for example `MessageDigest.getInstance("MD5")`, `Cipher.getInstance("DES/...")` or `KeyStore.getInstance("JKS")`, gets the non-validated Sun implementation. Name `BCFIPS` explicitly where FIPS is required.
4. **Keystores:** the default keystore type is **BCFKS**, and the JDK trust store is converted to BCFKS.
5. **Random numbers:** `SecureRandom` defaults come from the BCFIPS SP 800-90A DRBG; `getInstanceStrong()` still maps to the Sun providers.
6. **Certificate and TLS policy:** `jdk.certpath.disabledAlgorithms` and `jdk.tls.disabledAlgorithms` disable MD2, MD5, SSLv3, TLS 1.0 and 1.1, RC4, DES, 3DES, anonymous and NULL suites, and small RSA, DSA and DH keys for the JDK's own TLS and certificate code.
7. **Known CVEs:** `bc-fips` 2.1.1 has five open advisories, fixed only in 2.1.2 and 2.1.3, which no certificate lists yet.

The certificate covers the module, not this image: running it on Wolfi, and on arm64, is an operator-affirmed port.

---

## 📦 Runtime Flavors

Every Java version (`8`, `17`, `21`, `25`) provides three distinct tiers optimized for different stages of the delivery lifecycle. Replace `21` below with the version you need; the floating `dev`, `latest` and `distroless` tags follow Java 21.

| Target | Image Tag | Base | Capabilities | Intended Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`dev`** | `ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-dev` | Wolfi | Full JDK (`javac`, no Maven or Gradle) + `bash`, busybox, `apk`, `curl` | Building applications |
| **`standard`** | `ghcr.io/taha2samy-3/wolfi-openjdk-fips:21` | Wolfi | JRE + Bouncy Castle FIPS + `bash`, busybox and `apk` | Production workloads that need a shell |
| **`prod`** | `ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-distroless` | Distroless | JRE + CA certificates + Bouncy Castle FIPS, **no shell, no package manager** | Production |

All three flavors run as UID `1001`.

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

# Other LTS versions use the same tag scheme
docker pull ghcr.io/taha2samy-3/wolfi-openjdk-fips:8-distroless
docker pull ghcr.io/taha2samy-3/wolfi-openjdk-fips:17
docker pull ghcr.io/taha2samy-3/wolfi-openjdk-fips:25-dev
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
  - Reads back the `org.bouncycastle.fips.approved_only` system property (the test harness sets it, so this does not prove the image sets it).
- **Cryptographic Negative Rejection:** `2_crypto_negative_test.py` (every test requests the algorithm from the `BCFIPS` provider by name)
  - Rejection of MD4, MD5, SHA-1 signatures.
  - Rejection of DES, 3DES, RC4.
  - Rejection of RSA keys < 2048-bit, DSA keys < 2048-bit, and non-NIST curves.
  - Rejection of short HMAC keys and short salt PBKDF2.
- **Cryptographic Positive Operations:** `3_crypto_positive_test.py`
  - Validation of AES-GCM and AES-256-CBC.
  - Validation of RSA-2048 and ECDSA P-256.
  - Validation of HMAC-SHA256, PBKDF2, and ECDH key agreement.
- **KeyStore & Truststore:** `4_keystore_test.py`
  - Enforces `BCFKS` as default KeyStore type.
  - Checks that the `BCFIPS` provider has no `JKS` keystore (the Sun provider still does).
- **Network & TLS:** `5_network_test.py`
  - TLS 1.3 handshake with BCJSSE against a public server (needs internet access).
  - Anonymous, NULL and RC4 cipher handshakes fail (the public server never offers them, so this cannot fail).
- **Random Number Generation:** `6_rng_test.py`
  - Validates NIST SP 800-90A DRBG entropy generation.

### Running Tests Locally

```bash
# Every flavor of one Java version, as CI runs it (pulls nothing: pull or build the images first)
python .github/scripts/fips_tests.py --unit openjdk-21 --arch amd64 --out fips-results

# Or the suite directly against one JDK / JRE pair
cd openjdk/tests
pytest -v --jdk-img ghcr.io/taha2samy-3/wolfi-openjdk-fips:21-dev --jre-img ghcr.io/taha2samy-3/wolfi-openjdk-fips:21
```

CI runs these suites on amd64 and arm64 after every build and on each pull request that changes an OpenJDK image; results appear on the dashboard's **FIPS tests** tab.

---

## 🔨 Building with Docker Bake

From the repository root:

```bash
# Build every Java version and flavor, or one target (openjdk-<version>-<dev|standard|prod>)
docker buildx bake openjdk
docker buildx bake openjdk-8-prod

# After editing templates/java.security.j2 or adding a Java version
python openjdk/render_security.py
```

Temurin, Bouncy Castle TLS/utility jars and the Wolfi packages are updated by the daily dependency pull request. The **bc-fips** jar is the FIPS 140-3 validated module (certificate #4943 covers 2.1.1) and only changes by hand when NIST lists a new certificate.

---

## 📊 Supply Chain & Attestation

Every image built in the pipeline includes:
- **SLSA Build Level 3 provenance** signed by the reusable `build-images.yml` workflow; verify with `gh attestation verify oci://<image> --owner taha2samy-3 --signer-workflow taha2samy-3/node/.github/workflows/build-images.yml`.
- **CycloneDX SBOMs** per architecture, attested to GHCR. The image also carries a one-component CycloneDX file for the JDK at `/opt/java/java.cdx.json`.
- **Trivy Vulnerability Scans:** Continuous scanning for CVEs against the Wolfi security advisories database.
