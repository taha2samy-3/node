# ==========================================
# Global Variables
# ==========================================
variable "REGISTRY" {
  default = "ghcr.io"
}

variable "OWNER" {
  default = "taha2samy-3"
}

# Repository that builds and publishes every image (links GHCR packages to this repo)
variable "SOURCE_REPO" {
  default = "node"
}

variable "BASE_IMAGE" {
  default = "cgr.dev/chainguard/wolfi-base@sha256:9c2092b053779e14c82fb50f77b37bcc38b7d2c83972352d5813280f9d035b03"
}

# ==========================================
# Node.js Versions
# ==========================================
variable "REPO" {
  default = "node"
}
variable "NODE_18_FULL_VERSION" {
  default = "18.20.8-r9"
}

variable "NODE_20_FULL_VERSION" {
  default = "20.20.2-r9"
}

variable "NODE_22_FULL_VERSION" {
  default = "22.23.2-r1"
}

variable "NODE_24_FULL_VERSION" {
  default = "24.21.0-r4"
}

variable "NODE_26_FULL_VERSION" {
  default = "26.10.0-r3"
}

# ==========================================
# Node.js FIPS (reuses the NODE_*_FULL_VERSION pins above)
# ==========================================
variable "NODE_FIPS_REPO" {
  default = "node-fips"
}

# Image that provides the validated FIPS provider: the OpenSSL FIPS image built by openssl-standard
variable "NODE_FIPS_PROVIDER_IMAGE" {
  default = "${REGISTRY}/${OWNER}/${OPENSSL_REPO}:${OPENSSL_CORE_VERSION}"
}

# ==========================================
# Python Versions
# ==========================================
variable "PYTHON_REPO" {
  default = "python"
}

variable "PYTHON_3_10_FULL_VERSION" { default = "3.10.22-r1" }
variable "PYTHON_3_11_FULL_VERSION" { default = "3.11.17-r1" }
variable "PYTHON_3_12_FULL_VERSION" { default = "3.12.15-r1" }
variable "PYTHON_3_13_FULL_VERSION" { default = "3.13.16_git20261002-r1" }
variable "PYTHON_3_14_FULL_VERSION" { default = "3.14.8_git20261001-r1" }

# ==========================================
# Bun Versions
# ==========================================
variable "BUN_REPO" {
  default = "bun"
}

variable "BUN_1_FULL_VERSION" {
  default = "1.4.2-r0"
}

# ==========================================
# Java Versions
# ==========================================
variable "JAVA_REPO" {
  default = "java"
}

variable "JAVA_17_FULL_VERSION" { default = "17.0.20.1-r4" }
variable "JAVA_21_FULL_VERSION" { default = "21.0.12.1-r2" }
variable "JAVA_23_FULL_VERSION" { default = "23.0.2-r8" }

# ==========================================
# Go Versions
# ==========================================
variable "GO_REPO" {
  default = "go"
}

variable "GO_1_22_FULL_VERSION" { default = "1.22.12-r8" }
variable "GO_1_23_FULL_VERSION" { default = "1.23.12-r1" }
variable "GO_1_24_FULL_VERSION" { default = "1.24.13-r3" }

# ==========================================
# OpenSSL FIPS Versions
# ==========================================
variable "OPENSSL_REPO" {
  default = "openssl-fips"
}

variable "OPENSSL_CORE_VERSION" {
  default = "3.5.5"
}

variable "OPENSSL_CORE_SHA256" {
  default = "b28c91532a8b65a1f983b4c28b7488174e4a01008e29ce8e69bd789f28bc2a89"
}

# FIPS 140-3 certificate #4985 covers OpenSSL FIPS Provider 3.1.2: change only when a new certificate lists the version
variable "OPENSSL_FIPS_VERSION" {
  default = "3.1.2"
}

# SHA-256 of openssl-3.1.2.tar.gz as required by the module security policy
variable "OPENSSL_FIPS_SHA256" {
  default = "a0ce69b8b97ea6a35b96875235aa453b966ba3cba8af2de23657d8b6767d6539"
}

variable "OPENSSL_STATIC_IMAGE" {
  default = "cgr.dev/chainguard/static@sha256:11ec91f0372630a2ca3764cea6325bebb0189a514084463cbb3724e5bb350d14"
}
variable "OPENSSL_BUILD_BASE_VER" { default = "1-r9" }
variable "OPENSSL_PERL_VER" { default = "5.42.2-r3" }
variable "OPENSSL_LINUX_HEADERS_VER" { default = "7.0.11-r0" }
variable "OPENSSL_WGET_VER" { default = "1.25.0-r14" }
variable "OPENSSL_CA_CERTIFICATES_VER" { default = "20260413-r0" }
variable "OPENSSL_LIBSTDC_PLUS_PLUS_VER" { default = "16.1.0-r2" }
variable "OPENSSL_ZLIB_VER" { default = "1.3.2-r3" }
variable "OPENSSL_TZDATA_VER" { default = "2026b-r0" }
variable "OPENSSL_POSIX_LIBC_UTILS_VER" { default = "2.43-r8" }
variable "OPENSSL_PKGCONF_VER" { default = "2.5.1-r2" }
variable "OPENSSL_PCRE_DEV_VER" { default = "8.45-r7" }
variable "OPENSSL_ZLIB_DEV_VER" { default = "1.3.2-r3" }
variable "OPENSSL_BASH_VER" { default = "5.3-r12" }
variable "OPENSSL_CURL_VER" { default = "8.20.0-r1" }
variable "OPENSSL_JQ_VER" { default = "1.8.1-r6" }
variable "OPENSSL_UNZIP_VER" { default = "6.0-r6" }
variable "OPENSSL_APK_TOOLS_VER" { default = "2.14.10-r12" }
variable "OPENSSL_BUSYBOX_VER" { default = "1.37.0-r59" }
variable "OPENSSL_GLIBC_VER" { default = "2.43-r8" }
variable "OPENSSL_GLIBC_LOCALE_POSIX_VER" { default = "2.43-r8" }
variable "OPENSSL_LD_LINUX_VER" { default = "2.43-r8" }
variable "OPENSSL_LIBCRYPT1_VER" { default = "2.43-r8" }
variable "OPENSSL_LIBXCRYPT_VER" { default = "4.5.2-r3" }
variable "OPENSSL_LIBGCC_VER" { default = "16.1.0-r2" }
variable "OPENSSL_WOLFI_BASE_VER" { default = "1-r7" }
variable "OPENSSL_WOLFI_BASELAYOUT_VER" { default = "20230201-r29" }
variable "OPENSSL_WOLFI_KEYS_VER" { default = "1-r13" }

# ==========================================
# OpenJDK FIPS Versions
# ==========================================
variable "OPENJDK_REPO" {
  default = "wolfi-openjdk-fips"
}

# Java version whose images also get the floating dev / latest / distroless tags
variable "OPENJDK_LATEST_VERSION" {
  default = "21"
}

# Eclipse Temurin 8
variable "OPENJDK_8_FULL_VERSION" { default = "1.8.0_492-b09" }
variable "OPENJDK_8_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u492-b09/OpenJDK8U-jdk_x64_linux_hotspot_8u492b09.tar.gz" }
variable "OPENJDK_8_JDK_AMD64_SHA" { default = "da257f161d7f8c6ca5b0e5d9e4090f65ac28c5e398072e68b8ae87988b1d1a2e" }
variable "OPENJDK_8_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u492-b09/OpenJDK8U-jdk_aarch64_linux_hotspot_8u492b09.tar.gz" }
variable "OPENJDK_8_JDK_ARM64_SHA" { default = "3c2253b986909c20f79d6de7a0cb957f89c243df57615897836046e24d2e5257" }
variable "OPENJDK_8_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u492-b09/OpenJDK8U-jre_x64_linux_hotspot_8u492b09.tar.gz" }
variable "OPENJDK_8_JRE_AMD64_SHA" { default = "8eef3d4a837bb7a9e45d30a7579d84d5b76a4321f4376573311e6bf89e48f9b0" }
variable "OPENJDK_8_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u492-b09/OpenJDK8U-jre_aarch64_linux_hotspot_8u492b09.tar.gz" }
variable "OPENJDK_8_JRE_ARM64_SHA" { default = "d5e50cb002600007dbdfac523605d26196607fa5212db0942ef05cdce9fe2892" }

# Eclipse Temurin 17
variable "OPENJDK_17_FULL_VERSION" { default = "17.0.19+10" }
variable "OPENJDK_17_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jdk_x64_linux_hotspot_17.0.19_10.tar.gz" }
variable "OPENJDK_17_JDK_AMD64_SHA" { default = "d8afc263758141a66e0e3aafc321e783f7016696f4eaea067d340a269037d331" }
variable "OPENJDK_17_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jdk_aarch64_linux_hotspot_17.0.19_10.tar.gz" }
variable "OPENJDK_17_JDK_ARM64_SHA" { default = "83a52172678ec8975164648654869cb2e71d7c748b47aca94b29bbfa10c18e81" }
variable "OPENJDK_17_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz" }
variable "OPENJDK_17_JRE_AMD64_SHA" { default = "adb5a2364baa51de1ef91bb9911f5a61d24b045fe1d6647cb8050272a3a8ee75" }
variable "OPENJDK_17_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jre_aarch64_linux_hotspot_17.0.19_10.tar.gz" }
variable "OPENJDK_17_JRE_ARM64_SHA" { default = "aae834297a87736869745be7c1fca3207ea9167c5824f41c88b0ebb2e3ccb9b1" }

# Eclipse Temurin 21
variable "OPENJDK_21_FULL_VERSION" { default = "21.0.11+10-LTS" }
variable "OPENJDK_21_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jdk_x64_linux_hotspot_21.0.11_10.tar.gz" }
variable "OPENJDK_21_JDK_AMD64_SHA" { default = "4b2220e232a97997b436ca6ab15cbf70171ecff52958a46159dfa5a8c44ca4de" }
variable "OPENJDK_21_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.11_10.tar.gz" }
variable "OPENJDK_21_JDK_ARM64_SHA" { default = "8d498ec88e1c1989fab95c6784240ab92d011e29c54d20a3f9c324b13476f9ad" }
variable "OPENJDK_21_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jre_x64_linux_hotspot_21.0.11_10.tar.gz" }
variable "OPENJDK_21_JRE_AMD64_SHA" { default = "e5038aae3ca9ff670bc696496b0728dbd23d280026bad30291cb919221ecfdcb" }
variable "OPENJDK_21_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jre_aarch64_linux_hotspot_21.0.11_10.tar.gz" }
variable "OPENJDK_21_JRE_ARM64_SHA" { default = "fa23d9d9945053e67bcc7638410eabf1e17a7672c7c95a24f70cd08b8407d36e" }

# Eclipse Temurin 25
variable "OPENJDK_25_FULL_VERSION" { default = "25.0.3+9-LTS" }
variable "OPENJDK_25_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.3%2B9/OpenJDK25U-jdk_x64_linux_hotspot_25.0.3_9.tar.gz" }
variable "OPENJDK_25_JDK_AMD64_SHA" { default = "69264a7a211bf5029830d07bc3370f879769d62ebc5b5488e90c9343a2da0e1f" }
variable "OPENJDK_25_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.3%2B9/OpenJDK25U-jdk_aarch64_linux_hotspot_25.0.3_9.tar.gz" }
variable "OPENJDK_25_JDK_ARM64_SHA" { default = "3e4287cb98870ba824ed698854bdc27cff984254caf66dd12cc291e7bfdde26b" }
variable "OPENJDK_25_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.3%2B9/OpenJDK25U-jre_x64_linux_hotspot_25.0.3_9.tar.gz" }
variable "OPENJDK_25_JRE_AMD64_SHA" { default = "487ad434d8b121ae3902d5ad9cb830cd8e1f75fefad6e2ba80f89d60e3db95d7" }
variable "OPENJDK_25_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.3%2B9/OpenJDK25U-jre_aarch64_linux_hotspot_25.0.3_9.tar.gz" }
variable "OPENJDK_25_JRE_ARM64_SHA" { default = "d12d5b19ff7f6c4a99fd4f9eecede2c96e64df7d1f41cc84f2e9c9b38408600b" }

# FIPS 140-3 certificate #4943 covers BC-FJA 2.1.1: change only when a new certificate lists the version
variable "OPENJDK_BC_FIPS_VERSION" { default = "2.1.1" }
variable "OPENJDK_BC_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bc-fips/2.1.1/bc-fips-2.1.1.jar" }
variable "OPENJDK_BC_FIPS_SHA" { default = "a430d935ad6cec6d045930758457740f5a5f8f9715894e347f6800f7926a7321" }

variable "OPENJDK_BC_UTIL_FIPS_VERSION" { default = "2.1.5" }
variable "OPENJDK_BC_UTIL_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bcutil-fips/2.1.5/bcutil-fips-2.1.5.jar" }
variable "OPENJDK_BC_UTIL_FIPS_SHA" { default = "503aaf5c2c5b7c729547462efe13699b5f6dacf9be150b7c48bba974b793dc92" }

variable "OPENJDK_BC_TLS_FIPS_VERSION" { default = "2.1.22" }
variable "OPENJDK_BC_TLS_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bctls-fips/2.1.22/bctls-fips-2.1.22.jar" }
variable "OPENJDK_BC_TLS_FIPS_SHA" { default = "688410563445e1a65ff33cb67842499f0788994d752c3df8f7ea4a0d40ddbf50" }

variable "OPENJDK_KEYSTORE_PWD" { default = "changeit" }

# Image used only to download and verify the Temurin archives
variable "OPENJDK_ALPINE_IMAGE" { default = "alpine@sha256:6baf43584bcb78f2e5847d1de515f23499913ac9f12bdf834811a3145eb11ca1" }
variable "OPENJDK_LIBCRYPTO3_VER" { default = "3.6.2-r5" }
variable "OPENJDK_LIBSSL3_VER" { default = "3.6.2-r5" }
variable "OPENJDK_NCURSES_VER" { default = "6.6.20260608-r0" }


# ==========================================
# envoke (secrets-entrypoint) Binary
# ==========================================
variable "ENVOKE_VERSION" {
  default = "v1.0.0"
}

variable "ENVOKE_SHA256_AMD64" {
  default = "055461cbf952f723ef981c5ce218ceac3a436ac231a7f1011fc266347c651459"
}

variable "ENVOKE_SHA256_ARM64" {
  default = "c6546bd81301779bf1e298c1c3f35abec548d03f62576c54b1a5b7c98949afe8"
}

target "_envoke" {
  args = {
    ENVOKE_VERSION = ENVOKE_VERSION
    ENVOKE_SHA256_AMD64 = ENVOKE_SHA256_AMD64
    ENVOKE_SHA256_ARM64 = ENVOKE_SHA256_ARM64
  }
}

# ==========================================
# Groups
# ==========================================
group "default" {
  targets = ["dev", "prod", "python-dev", "python-prod", "bun-dev", "bun-prod", "java-dev", "java-prod", "go-dev", "go-prod", "openssl-dev", "openssl-standard", "openssl-prod", "openjdk", "node-fips"]
}

# ==========================================
# Node.js Targets
# ==========================================
target "dev" {
  inherits = ["_envoke"]
  name = "dev-${item.version}"
  matrix = {
    item = [
      { version = "18", full_version = NODE_18_FULL_VERSION },
      { version = "20", full_version = NODE_20_FULL_VERSION },
      { version = "22", full_version = NODE_22_FULL_VERSION },
      { version = "24", full_version = NODE_24_FULL_VERSION },
      { version = "26", full_version = NODE_26_FULL_VERSION }
    ]
  }
  context = "."
  dockerfile = "nodejs/dockerfile"
  target = "full-dev"
  args = {
    NODE_VERSION = item.version
    NODE_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${REPO}:${item.version}-dev",
    "${REGISTRY}/${OWNER}/${REPO}:v${item.version}-dev"
  ]
  cache-from = ["type=gha,scope=dev-${item.version}"]
  cache-to = ["type=gha,mode=max,scope=dev-${item.version},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.description" = "Optimized Node.js ${item.version} (${item.full_version}) development image with npm based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Optimized Node.js ${item.version} (${item.full_version}) development image with npm based on Chainguard Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "prod" {
  inherits = ["_envoke"]
  name = "prod-${item.version}"
  matrix = {
    item = [
      { version = "18", full_version = NODE_18_FULL_VERSION },
      { version = "20", full_version = NODE_20_FULL_VERSION },
      { version = "22", full_version = NODE_22_FULL_VERSION },
      { version = "24", full_version = NODE_24_FULL_VERSION },
      { version = "26", full_version = NODE_26_FULL_VERSION }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "nodejs/dockerfile"
  target = "minimal"
  args = {
    NODE_VERSION = item.version
    NODE_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  tags = [
    "${REGISTRY}/${OWNER}/${REPO}:${item.version}",
    "${REGISTRY}/${OWNER}/${REPO}:v${item.version}"
  ]
  cache-from = ["type=gha,scope=prod-${item.version}"]
  cache-to = ["type=gha,mode=max,scope=prod-${item.version},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Node.js ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Ultra-secure minimal Node.js ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# Node.js FIPS Targets
# ==========================================
target "node-fips" {
  inherits = ["_envoke"]
  name = "node-fips-${item.version}-${flavor.id}"
  matrix = {
    item = [
      { version = "22", full_version = NODE_22_FULL_VERSION },
      { version = "24", full_version = NODE_24_FULL_VERSION }
    ]
    flavor = [
      { id = "dev", stage = "fips-dev", tag_suffix = "-dev", description = "Node.js development image with npm and the OpenSSL FIPS 140-3 provider enforced, on Wolfi" },
      { id = "standard", stage = "fips-standard", tag_suffix = "", description = "Minimal Node.js runtime with the OpenSSL FIPS 140-3 provider enforced, on Wolfi" },
      { id = "prod", stage = "fips-distroless", tag_suffix = "-distroless", description = "Distroless Node.js runtime (no shell) with the OpenSSL FIPS 140-3 provider enforced, on Wolfi" }
    ]
  }
  context = "."
  dockerfile = "nodejs/dockerfile"
  target = flavor.stage
  args = {
    NODE_VERSION = item.version
    NODE_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
    OPENSSL_FIPS_IMAGE = NODE_FIPS_PROVIDER_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = ["${REGISTRY}/${OWNER}/${NODE_FIPS_REPO}:${item.version}${flavor.tag_suffix}"]
  cache-from = ["type=gha,scope=node-fips-${item.version}-${flavor.id}"]
  cache-to = ["type=gha,mode=max,scope=node-fips-${item.version}-${flavor.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "${flavor.description} (Node.js ${item.full_version})"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=${flavor.description} (Node.js ${item.full_version})",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# Python Targets
# ==========================================
target "python-dev" {
  inherits = ["_envoke"]
  name = "python-dev-${item.id}"
  matrix = {
    item = [
      { id = "3-10", version = "3.10", full_version = PYTHON_3_10_FULL_VERSION },
      { id = "3-11", version = "3.11", full_version = PYTHON_3_11_FULL_VERSION },
      { id = "3-12", version = "3.12", full_version = PYTHON_3_12_FULL_VERSION },
      { id = "3-13", version = "3.13", full_version = PYTHON_3_13_FULL_VERSION },
      { id = "3-14", version = "3.14", full_version = PYTHON_3_14_FULL_VERSION }
    ]
  }
  context = "."
  dockerfile = "python/dockerfile"
  target = "full-dev"
  args = {
    PYTHON_VERSION = item.version
    PYTHON_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${PYTHON_REPO}:${item.version}-dev",
    "${REGISTRY}/${OWNER}/${PYTHON_REPO}:v${item.version}-dev"
  ]
  cache-from = ["type=gha,scope=python-dev-${item.id}"]
  cache-to = ["type=gha,mode=max,scope=python-dev-${item.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Python ${item.version} (${item.full_version}) development image based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Optimized Python ${item.version} (${item.full_version}) development image based on Chainguard Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "python-prod" {
  inherits = ["_envoke"]
  name = "python-prod-${item.id}"
  matrix = {
    item = [
      { id = "3-10", version = "3.10", full_version = PYTHON_3_10_FULL_VERSION },
      { id = "3-11", version = "3.11", full_version = PYTHON_3_11_FULL_VERSION },
      { id = "3-12", version = "3.12", full_version = PYTHON_3_12_FULL_VERSION },
      { id = "3-13", version = "3.13", full_version = PYTHON_3_13_FULL_VERSION },
      { id = "3-14", version = "3.14", full_version = PYTHON_3_14_FULL_VERSION }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "python/dockerfile"
  target = "minimal"
  args = {
    PYTHON_VERSION = item.version
    PYTHON_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  tags = [
    "${REGISTRY}/${OWNER}/${PYTHON_REPO}:${item.version}",
    "${REGISTRY}/${OWNER}/${PYTHON_REPO}:v${item.version}"
  ]
  cache-from = ["type=gha,scope=python-prod-${item.id}"]
  cache-to = ["type=gha,mode=max,scope=python-prod-${item.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Python ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Ultra-secure minimal Python ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# Bun Targets
# ==========================================
target "bun-dev" {
  inherits = ["_envoke"]
  name = "bun-dev-${item.id}"
  matrix = {
    item = [
      { id = "1", version = "1", full_version = BUN_1_FULL_VERSION }
    ]
  }
  context = "."
  dockerfile = "bun/dockerfile"
  target = "full-dev"
  args = {
    BUN_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${BUN_REPO}:${item.version}-dev",
    "${REGISTRY}/${OWNER}/${BUN_REPO}:v${item.version}-dev"
  ]
  cache-from = ["type=gha,scope=bun-dev-${item.id}"]
  cache-to = ["type=gha,mode=max,scope=bun-dev-${item.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Bun ${item.version} (${item.full_version}) development image based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Optimized Bun ${item.version} (${item.full_version}) development image based on Chainguard Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "bun-prod" {
  inherits = ["_envoke"]
  name = "bun-prod-${item.id}"
  matrix = {
    item = [
      { id = "1", version = "1", full_version = BUN_1_FULL_VERSION }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "bun/dockerfile"
  target = "minimal"
  args = {
    BUN_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  tags = [
    "${REGISTRY}/${OWNER}/${BUN_REPO}:${item.version}",
    "${REGISTRY}/${OWNER}/${BUN_REPO}:v${item.version}"
  ]
  cache-from = ["type=gha,scope=bun-prod-${item.id}"]
  cache-to = ["type=gha,mode=max,scope=bun-prod-${item.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Bun ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Ultra-secure minimal Bun ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# Java Targets
# ==========================================
target "java-dev" {
  inherits = ["_envoke"]
  name = "java-dev-${item.version}"
  matrix = {
    item = [
      { version = "17", full_version = JAVA_17_FULL_VERSION },
      { version = "21", full_version = JAVA_21_FULL_VERSION },
      { version = "23", full_version = JAVA_23_FULL_VERSION }
    ]
  }
  context = "."
  dockerfile = "java/dockerfile"
  target = "full-dev"
  args = {
    JAVA_VERSION = item.version
    JAVA_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${JAVA_REPO}:${item.version}-dev",
    "${REGISTRY}/${OWNER}/${JAVA_REPO}:v${item.version}-dev"
  ]
  cache-from = ["type=gha,scope=java-dev-${item.version}"]
  cache-to = ["type=gha,mode=max,scope=java-dev-${item.version},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Java OpenJDK ${item.version} (${item.full_version}) development image based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Optimized Java OpenJDK ${item.version} (${item.full_version}) development image based on Chainguard Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "java-prod" {
  inherits = ["_envoke"]
  name = "java-prod-${item.version}"
  matrix = {
    item = [
      { version = "17", full_version = JAVA_17_FULL_VERSION },
      { version = "21", full_version = JAVA_21_FULL_VERSION },
      { version = "23", full_version = JAVA_23_FULL_VERSION }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "java/dockerfile"
  target = "minimal"
  args = {
    JAVA_VERSION = item.version
    JAVA_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  tags = [
    "${REGISTRY}/${OWNER}/${JAVA_REPO}:${item.version}",
    "${REGISTRY}/${OWNER}/${JAVA_REPO}:v${item.version}"
  ]
  cache-from = ["type=gha,scope=java-prod-${item.version}"]
  cache-to = ["type=gha,mode=max,scope=java-prod-${item.version},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Java OpenJDK ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Ultra-secure minimal Java OpenJDK ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# Go Targets
# ==========================================
target "go-dev" {
  inherits = ["_envoke"]
  name = "go-dev-${replace(item.version, ".", "-")}"
  matrix = {
    item = [
      { version = "1.22", full_version = GO_1_22_FULL_VERSION },
      { version = "1.23", full_version = GO_1_23_FULL_VERSION },
      { version = "1.24", full_version = GO_1_24_FULL_VERSION }
    ]
  }
  context = "."
  dockerfile = "go/dockerfile"
  target = "full-dev"
  args = {
    GO_VERSION = item.version
    GO_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${GO_REPO}:${item.version}-dev",
    "${REGISTRY}/${OWNER}/${GO_REPO}:v${item.version}-dev"
  ]
  cache-from = ["type=gha,scope=go-dev-${replace(item.version, ".", "-")}"]
  cache-to = ["type=gha,mode=max,scope=go-dev-${replace(item.version, ".", "-")},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Go ${item.version} development image based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Optimized Go ${item.version} development image based on Chainguard Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "go-prod" {
  inherits = ["_envoke"]
  name = "go-prod-${replace(item.version, ".", "-")}"
  matrix = {
    item = [
      { version = "1.22", full_version = GO_1_22_FULL_VERSION },
      { version = "1.23", full_version = GO_1_23_FULL_VERSION },
      { version = "1.24", full_version = GO_1_24_FULL_VERSION }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "go/dockerfile"
  target = "minimal"
  args = {
    GO_VERSION = item.version
    BASE_IMAGE = BASE_IMAGE
  }
  tags = [
    "${REGISTRY}/${OWNER}/${GO_REPO}:${item.version}",
    "${REGISTRY}/${OWNER}/${GO_REPO}:v${item.version}"
  ]
  cache-from = ["type=gha,scope=go-prod-${replace(item.version, ".", "-")}"]
  cache-to = ["type=gha,mode=max,scope=go-prod-${replace(item.version, ".", "-")},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal distroless base for Go ${item.version} apps based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Ultra-secure minimal distroless base for Go ${item.version} apps based on Chainguard Wolfi and scratch",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# OpenSSL FIPS Targets
# ==========================================
target "openssl-base" {
  args = {
    FIPS_VERSION = OPENSSL_FIPS_VERSION
    FIPS_SHA256 = OPENSSL_FIPS_SHA256
    CORE_VERSION = OPENSSL_CORE_VERSION
    CORE_SHA256 = OPENSSL_CORE_SHA256
    BASE_IMAGE = BASE_IMAGE
    STATIC_IMAGE = OPENSSL_STATIC_IMAGE
    BUILD_BASE_VER = OPENSSL_BUILD_BASE_VER
    PERL_VER = OPENSSL_PERL_VER
    LINUX_HEADERS_VER = OPENSSL_LINUX_HEADERS_VER
    WGET_VER = OPENSSL_WGET_VER
    CA_CERTIFICATES_VER = OPENSSL_CA_CERTIFICATES_VER
    LIBSTDC_PLUS_PLUS_VER = OPENSSL_LIBSTDC_PLUS_PLUS_VER
    ZLIB_VER = OPENSSL_ZLIB_VER
    TZDATA_VER = OPENSSL_TZDATA_VER
    POSIX_LIBC_UTILS_VER = OPENSSL_POSIX_LIBC_UTILS_VER
    PKGCONF_VER = OPENSSL_PKGCONF_VER
    PCRE_DEV_VER = OPENSSL_PCRE_DEV_VER
    ZLIB_DEV_VER = OPENSSL_ZLIB_DEV_VER
    BASH_VER = OPENSSL_BASH_VER
    CURL_VER = OPENSSL_CURL_VER
    JQ_VER = OPENSSL_JQ_VER
    UNZIP_VER = OPENSSL_UNZIP_VER
    APK_TOOLS_VER = OPENSSL_APK_TOOLS_VER
    BUSYBOX_VER = OPENSSL_BUSYBOX_VER
    GLIBC_VER = OPENSSL_GLIBC_VER
    GLIBC_LOCALE_POSIX_VER = OPENSSL_GLIBC_LOCALE_POSIX_VER
    LD_LINUX_VER = OPENSSL_LD_LINUX_VER
    LIBCRYPT1_VER = OPENSSL_LIBCRYPT1_VER
    LIBXCRYPT_VER = OPENSSL_LIBXCRYPT_VER
    LIBGCC_VER = OPENSSL_LIBGCC_VER
    WOLFI_BASE_VER = OPENSSL_WOLFI_BASE_VER
    WOLFI_BASELAYOUT_VER = OPENSSL_WOLFI_BASELAYOUT_VER
    WOLFI_KEYS_VER = OPENSSL_WOLFI_KEYS_VER
  }
}

target "openssl-dev" {
  inherits = ["openssl-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openssl"
  dockerfile = "dockerfile"
  target = "openssl-dev"
  tags = [
    "${REGISTRY}/${OWNER}/${OPENSSL_REPO}:${OPENSSL_CORE_VERSION}-dev",
    "${REGISTRY}/${OWNER}/${OPENSSL_REPO}:dev"
  ]
  cache-from = ["type=gha,scope=openssl-dev"]
  cache-to = ["type=gha,mode=max,scope=openssl-dev,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant OpenSSL development SDK image on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened FIPS 140-3 compliant OpenSSL development SDK image on Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "openssl-standard" {
  inherits = ["openssl-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openssl"
  dockerfile = "dockerfile"
  target = "openssl-standard"
  tags = [
    "${REGISTRY}/${OWNER}/${OPENSSL_REPO}:${OPENSSL_CORE_VERSION}",
    "${REGISTRY}/${OWNER}/${OPENSSL_REPO}:latest"
  ]
  cache-from = ["type=gha,scope=openssl-standard"]
  cache-to = ["type=gha,mode=max,scope=openssl-standard,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant OpenSSL standard runtime image on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened FIPS 140-3 compliant OpenSSL standard runtime image on Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "openssl-prod" {
  inherits = ["openssl-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openssl"
  dockerfile = "dockerfile"
  target = "openssl-distroless"
  tags = [
    "${REGISTRY}/${OWNER}/${OPENSSL_REPO}:${OPENSSL_CORE_VERSION}-distroless",
    "${REGISTRY}/${OWNER}/${OPENSSL_REPO}:distroless"
  ]
  cache-from = ["type=gha,scope=openssl-distroless"]
  cache-to = ["type=gha,mode=max,scope=openssl-distroless,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant Zero-CVE distroless OpenSSL container on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened FIPS 140-3 compliant Zero-CVE distroless OpenSSL container on Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# OpenJDK FIPS Targets
# ==========================================
target "openjdk" {
  name = "openjdk-${java.version}-${flavor.id}"
  matrix = {
    java = [
      {
        version = "8"
        full_version = OPENJDK_8_FULL_VERSION
        jdk_amd64_url = OPENJDK_8_JDK_AMD64_URL
        jdk_amd64_sha = OPENJDK_8_JDK_AMD64_SHA
        jdk_arm64_url = OPENJDK_8_JDK_ARM64_URL
        jdk_arm64_sha = OPENJDK_8_JDK_ARM64_SHA
        jre_amd64_url = OPENJDK_8_JRE_AMD64_URL
        jre_amd64_sha = OPENJDK_8_JRE_AMD64_SHA
        jre_arm64_url = OPENJDK_8_JRE_ARM64_URL
        jre_arm64_sha = OPENJDK_8_JRE_ARM64_SHA
      },
      {
        version = "17"
        full_version = OPENJDK_17_FULL_VERSION
        jdk_amd64_url = OPENJDK_17_JDK_AMD64_URL
        jdk_amd64_sha = OPENJDK_17_JDK_AMD64_SHA
        jdk_arm64_url = OPENJDK_17_JDK_ARM64_URL
        jdk_arm64_sha = OPENJDK_17_JDK_ARM64_SHA
        jre_amd64_url = OPENJDK_17_JRE_AMD64_URL
        jre_amd64_sha = OPENJDK_17_JRE_AMD64_SHA
        jre_arm64_url = OPENJDK_17_JRE_ARM64_URL
        jre_arm64_sha = OPENJDK_17_JRE_ARM64_SHA
      },
      {
        version = "21"
        full_version = OPENJDK_21_FULL_VERSION
        jdk_amd64_url = OPENJDK_21_JDK_AMD64_URL
        jdk_amd64_sha = OPENJDK_21_JDK_AMD64_SHA
        jdk_arm64_url = OPENJDK_21_JDK_ARM64_URL
        jdk_arm64_sha = OPENJDK_21_JDK_ARM64_SHA
        jre_amd64_url = OPENJDK_21_JRE_AMD64_URL
        jre_amd64_sha = OPENJDK_21_JRE_AMD64_SHA
        jre_arm64_url = OPENJDK_21_JRE_ARM64_URL
        jre_arm64_sha = OPENJDK_21_JRE_ARM64_SHA
      },
      {
        version = "25"
        full_version = OPENJDK_25_FULL_VERSION
        jdk_amd64_url = OPENJDK_25_JDK_AMD64_URL
        jdk_amd64_sha = OPENJDK_25_JDK_AMD64_SHA
        jdk_arm64_url = OPENJDK_25_JDK_ARM64_URL
        jdk_arm64_sha = OPENJDK_25_JDK_ARM64_SHA
        jre_amd64_url = OPENJDK_25_JRE_AMD64_URL
        jre_amd64_sha = OPENJDK_25_JRE_AMD64_SHA
        jre_arm64_url = OPENJDK_25_JRE_ARM64_URL
        jre_arm64_sha = OPENJDK_25_JRE_ARM64_SHA
      }
    ]
    flavor = [
      { id = "dev", stage = "openjdk-dev", tag_suffix = "-dev", legacy_tag = "jdk_standard", floating_tag = "dev", description = "Hardened FIPS 140-3 compliant OpenJDK development SDK image on Wolfi" },
      { id = "standard", stage = "openjdk-standard", tag_suffix = "", legacy_tag = "jre_standard", floating_tag = "latest", description = "Hardened FIPS 140-3 compliant OpenJDK standard JRE runtime on Wolfi" },
      { id = "prod", stage = "openjdk-distroless", tag_suffix = "-distroless", legacy_tag = "jre_distroless", floating_tag = "distroless", description = "Hardened FIPS 140-3 compliant Zero-CVE distroless OpenJDK JRE container on Wolfi" }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openjdk"
  dockerfile = "dockerfile"
  target = flavor.stage
  args = {
    JAVA_VERSION         = java.version
    JAVA_FULL_VERSION    = java.full_version
    BASE_IMAGE           = BASE_IMAGE
    ALPINE_IMAGE         = OPENJDK_ALPINE_IMAGE

    JDK_AMD64_URL        = java.jdk_amd64_url
    JDK_AMD64_SHA        = java.jdk_amd64_sha
    JDK_ARM64_URL        = java.jdk_arm64_url
    JDK_ARM64_SHA        = java.jdk_arm64_sha

    JRE_AMD64_URL        = java.jre_amd64_url
    JRE_AMD64_SHA        = java.jre_amd64_sha
    JRE_ARM64_URL        = java.jre_arm64_url
    JRE_ARM64_SHA        = java.jre_arm64_sha

    BC_FIPS_VERSION      = OPENJDK_BC_FIPS_VERSION
    BC_FIPS_URL          = OPENJDK_BC_FIPS_URL
    BC_FIPS_SHA          = OPENJDK_BC_FIPS_SHA

    BC_UTIL_FIPS_VERSION = OPENJDK_BC_UTIL_FIPS_VERSION
    BC_UTIL_FIPS_URL     = OPENJDK_BC_UTIL_FIPS_URL
    BC_UTIL_FIPS_SHA     = OPENJDK_BC_UTIL_FIPS_SHA

    BC_TLS_FIPS_VERSION  = OPENJDK_BC_TLS_FIPS_VERSION
    BC_TLS_FIPS_URL      = OPENJDK_BC_TLS_FIPS_URL
    BC_TLS_FIPS_SHA      = OPENJDK_BC_TLS_FIPS_SHA

    KEYSTORE_PWD         = OPENJDK_KEYSTORE_PWD

    APK_TOOLS_VER          = OPENSSL_APK_TOOLS_VER
    BASH_VER               = OPENSSL_BASH_VER
    BUSYBOX_VER            = OPENSSL_BUSYBOX_VER
    CA_CERTIFICATES_VER    = OPENSSL_CA_CERTIFICATES_VER
    CURL_VER               = OPENSSL_CURL_VER
    GLIBC_VER              = OPENSSL_GLIBC_VER
    GLIBC_LOCALE_POSIX_VER = OPENSSL_GLIBC_LOCALE_POSIX_VER
    LD_LINUX_VER           = OPENSSL_LD_LINUX_VER
    LIBCRYPT1_VER          = OPENSSL_LIBCRYPT1_VER
    LIBCRYPTO3_VER         = OPENJDK_LIBCRYPTO3_VER
    LIBGCC_VER             = OPENSSL_LIBGCC_VER
    LIBSSL3_VER            = OPENJDK_LIBSSL3_VER
    LIBSTDCPP_VER          = OPENSSL_LIBSTDC_PLUS_PLUS_VER
    LIBXCRYPT_VER          = OPENSSL_LIBXCRYPT_VER
    NCURSES_VER            = OPENJDK_NCURSES_VER
    POSIX_LIBC_UTILS_VER   = OPENSSL_POSIX_LIBC_UTILS_VER
    TZDATA_VER             = OPENSSL_TZDATA_VER
    WOLFI_BASELAYOUT_VER   = OPENSSL_WOLFI_BASELAYOUT_VER
    WOLFI_KEYS_VER         = OPENSSL_WOLFI_KEYS_VER
    ZLIB_VER               = OPENSSL_ZLIB_VER

    # Java 8 keeps the JDK runtime under jre/ and loads the Bouncy Castle jars from lib/ext
    JDK_TRUSTSTORE = java.version == "8" ? "/opt/java/jre/lib/security/cacerts" : "/opt/java/lib/security/cacerts"
    JDK_BC_DIR     = java.version == "8" ? "/opt/java/jre/lib/ext" : "/opt/java/lib"
    JRE_TRUSTSTORE = "/opt/java/lib/security/cacerts"
    JRE_BC_DIR     = java.version == "8" ? "/opt/java/lib/ext" : "/opt/java/lib"
    JRE_CHECK_EKU  = java.version == "8" ? "false" : "true"
  }
  tags = concat(
    [
      "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${java.version}${flavor.tag_suffix}",
      "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${java.version}-${flavor.legacy_tag}"
    ],
    java.version == OPENJDK_LATEST_VERSION ? ["${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${flavor.floating_tag}"] : []
  )
  cache-from = ["type=gha,scope=openjdk-${java.version}-${flavor.id}"]
  cache-to = ["type=gha,mode=max,scope=openjdk-${java.version}-${flavor.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = flavor.description
  }
  annotations = [
    "manifest:org.opencontainers.image.description=${flavor.description}",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}
