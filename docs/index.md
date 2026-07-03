# Secure Node.js Environment Dashboard

**High-Assurance Cryptographic Foundation & Vulnerability Tracking**

Welcome to the Secure Node.js Environment Dashboard. This platform tracks the vulnerability status, compliance standards, and continuous hardening reports of our golden base images across the organization.

---

## Core Architecture & Security Controls

Our custom Node.js images are built on top of the **Wolfi OS** (undistro) ecosystem to provide a minimal attack surface, rolling updates, and strict Zero-CVE compliance.

*   **Zero-CVE Base (Wolfi OS):** Standard glibc-based secure foundation designed for the container era, eliminating unnecessary OS packages.
*   **Non-Root Execution:** All images strictly run under the non-privileged `node` user (UID 1000) to prevent container escape and mitigate potential exploits.
*   **Process Management (Tini):** Integrated `tini` as `ENTRYPOINT` (PID 1) to handle system signals and prevent zombie processes on termination.
*   **Minimalist Footprint:** Production images are built directly `FROM scratch`, copying only the required Node.js runtime (`minimal-compat`) and leaving no package manager or shell.

---

## Artifact Tiers

We maintain two highly optimized tiers for every supported Node.js LTS version:

| Flavor | Target Stage | Description |
| :--- | :--- | :--- |
| `dev-builder` | CI/CD & Dev | Contains full Node.js, `npm`, and essential build utilities. |
| `production` | Production | Strict, highly secure, minimal-compat runtime from `scratch`. |

---

## Continuous Security Validation

Every built version is subjected to rigorous automated scanning and security compliance audits:

*   **Vulnerability Scanning:** Continuous package and layer inspection using Trivy.
*   **Docker CIS Benchmarks:** Verification against CIS Docker hardening guidelines.
*   **Supply Chain Attestation:** Full SLSA Build Provenance and CycloneDX SBOM generated natively in our pipeline.

---

## Supported LTS Versions

Select your target version below to explore the detailed security, vulnerability, and compliance reports:

*   [**Node.js 22 LTS Security Reports**](node-22.md)
*   [**Node.js 24 LTS Security Reports**](node-24.md)