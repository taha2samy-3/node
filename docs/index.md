# Secure Runtimes Environment Dashboard

**High-Assurance Cryptographic Foundation & Vulnerability Tracking**

Welcome to the Secure Runtimes Environment Dashboard. This platform tracks the vulnerability status, compliance standards, and continuous hardening reports of our golden base images across the organization.

---

## Core Architecture & Security Controls

Our custom runtime images are built on top of the **Wolfi OS** (undistro) ecosystem to provide a minimal attack surface, rolling updates, and strict Zero-CVE compliance.

*   **Zero-CVE Base (Wolfi OS):** Standard glibc-based secure foundation designed for the container era, eliminating unnecessary OS packages.
*   **Non-Root Execution:** All images strictly run under non-privileged users with UID 1000 (such as `node` or `python`) to prevent container escape and mitigate potential exploits.
*   **Process Management (Tini):** Integrated `tini` as `ENTRYPOINT` (PID 1) to handle system signals and prevent zombie processes on termination.
*   **Minimalist Footprint:** Production images are built directly `FROM scratch`, copying only the required runtime binaries and leaving no package manager or shell.

---

## Artifact Tiers

We maintain two highly optimized tiers for every supported runtime version:

| Flavor | Target Stage | Description |
| :--- | :--- | :--- |
| `dev-builder` | CI/CD & Dev | Contains full language runtime, package managers (npm, pip), and build utilities. |
| `production` | Production | Strict, highly secure, minimal-compat runtime from `scratch`. |

---

## Continuous Security Validation

Every built version is subjected to rigorous automated scanning and security compliance audits:

*   **Vulnerability Scanning:** Continuous package and layer inspection using Trivy.
*   **Docker CIS Benchmarks:** Verification against CIS Docker hardening guidelines.
*   **Supply Chain Attestation:** Full SLSA Build Provenance and CycloneDX SBOM generated natively in our pipeline.

---

### :fontawesome-brands-node-js: Node.js LTS
*   [**Node.js 20 LTS Security Reports**](node-20.md)
*   [**Node.js 22 LTS Security Reports**](node-22.md)
*   [**Node.js 24 LTS Security Reports**](node-24.md)

### :fontawesome-brands-python: Python
*   [**Python 3.10 Security Reports**](python-3.10.md)
*   [**Python 3.11 Security Reports**](python-3.11.md)
*   [**Python 3.12 Security Reports**](python-3.12.md)
*   [**Python 3.13 Security Reports**](python-3.13.md)
*   [**Python 3.14 Security Reports**](python-3.14.md)

### :simple-bun: Bun
*   [**Bun 1 Security Reports**](bun-1.md)
