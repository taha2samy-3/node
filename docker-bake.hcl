# ==========================================
# Global Variables
# ==========================================
variable "REGISTRY" {
  default = "ghcr.io"
}

variable "OWNER" {
  default = "taha2samy-3"
}

variable "BASE_IMAGE" {
  default = "cgr.dev/chainguard/wolfi-base@sha256:824f77df45397eb954dfb963db255907ee8842e3446353ce93d688e5e862f51d"
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
  default = "26.10.0-r2"
}

# ==========================================
# Python Versions
# ==========================================
variable "PYTHON_REPO" {
  default = "python"
}

variable "PYTHON_3_10_FULL_VERSION" { default = "3.10.22-r0" }
variable "PYTHON_3_11_FULL_VERSION" { default = "3.11.17-r0" }
variable "PYTHON_3_12_FULL_VERSION" { default = "3.12.15-r0" }
variable "PYTHON_3_13_FULL_VERSION" { default = "3.13.15_git20260925-r0" }
variable "PYTHON_3_14_FULL_VERSION" { default = "3.14.8_git20261001-r0" }

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

variable "GO_1_22_FULL_VERSION" { default = "1.22" }
variable "GO_1_23_FULL_VERSION" { default = "1.23" }
variable "GO_1_24_FULL_VERSION" { default = "1.24" }

# ==========================================
# OpenSSL FIPS Versions
# ==========================================
variable "OPENSSL_REPO" {
  default = "wolfi-openssl-fips"
}

variable "OPENSSL_CORE_VERSION" {
  default = "3.5.5"
}

variable "OPENSSL_FIPS_VERSION" {
  default = "3.1.2"
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

variable "OPENJDK_VERSION" {
  default = "21"
}

variable "OPENJDK_FULL_VERSION" {
  default = "21.0.11+10-LTS"
}

variable "OPENJDK_JDK_AMD64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jdk_x64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "OPENJDK_JDK_AMD64_SHA" {
  default = "4b2220e232a97997b436ca6ab15cbf70171ecff52958a46159dfa5a8c44ca4de"
}
variable "OPENJDK_JDK_ARM64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "OPENJDK_JDK_ARM64_SHA" {
  default = "8d498ec88e1c1989fab95c6784240ab92d011e29c54d20a3f9c324b13476f9ad"
}

variable "OPENJDK_JRE_AMD64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jre_x64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "OPENJDK_JRE_AMD64_SHA" {
  default = "e5038aae3ca9ff670bc696496b0728dbd23d280026bad30291cb919221ecfdcb"
}
variable "OPENJDK_JRE_ARM64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jre_aarch64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "OPENJDK_JRE_ARM64_SHA" {
  default = "fa23d9d9945053e67bcc7638410eabf1e17a7672c7c95a24f70cd08b8407d36e"
}

variable "OPENJDK_BC_FIPS_VERSION" { default = "2.1.2" }
variable "OPENJDK_BC_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bc-fips/2.1.2/bc-fips-2.1.2.jar" }
variable "OPENJDK_BC_FIPS_SHA" { default = "044fcd8a29d236edea8a5b414406cdae63b475f9ad9f05fe2dc904a277941115" }

variable "OPENJDK_BC_UTIL_FIPS_VERSION" { default = "2.1.5" }
variable "OPENJDK_BC_UTIL_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bcutil-fips/2.1.5/bcutil-fips-2.1.5.jar" }
variable "OPENJDK_BC_UTIL_FIPS_SHA" { default = "503aaf5c2c5b7c729547462efe13699b5f6dacf9be150b7c48bba974b793dc92" }

variable "OPENJDK_BC_TLS_FIPS_VERSION" { default = "2.1.22" }
variable "OPENJDK_BC_TLS_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bctls-fips/2.1.22/bctls-fips-2.1.22.jar" }
variable "OPENJDK_BC_TLS_FIPS_SHA" { default = "688410563445e1a65ff33cb67842499f0788994d752c3df8f7ea4a0d40ddbf50" }

variable "OPENJDK_KEYSTORE_PWD" { default = "changeit" }


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
  targets = ["dev", "prod", "python-dev", "python-prod", "bun-dev", "bun-prod", "java-dev", "java-prod", "go-dev", "go-prod", "openssl-dev", "openssl-standard", "openssl-prod", "openjdk-dev", "openjdk-standard", "openjdk-prod"]
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${REPO}"
    "org.opencontainers.image.description" = "Optimized Node.js ${item.version} (${item.full_version}) development image with npm based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Node.js ${item.version} (${item.full_version}) development image with npm based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Node.js ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Ultra-secure minimal Node.js ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${PYTHON_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Python ${item.version} (${item.full_version}) development image based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Python ${item.version} (${item.full_version}) development image based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${PYTHON_REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${PYTHON_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Python ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Ultra-secure minimal Python ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${PYTHON_REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${BUN_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Bun ${item.version} (${item.full_version}) development image based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Bun ${item.version} (${item.full_version}) development image based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${BUN_REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${BUN_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Bun ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Ultra-secure minimal Bun ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${BUN_REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${JAVA_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Java OpenJDK ${item.version} (${item.full_version}) development image based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Java OpenJDK ${item.version} (${item.full_version}) development image based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${JAVA_REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${JAVA_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Java OpenJDK ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Ultra-secure minimal Java OpenJDK ${item.version} (${item.full_version}) production runtime based on Chainguard Wolfi and scratch",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${JAVA_REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${GO_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Go ${item.version} development image based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Go ${item.version} development image based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${GO_REPO}"
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${GO_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal distroless base for Go ${item.version} apps based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Ultra-secure minimal distroless base for Go ${item.version} apps based on Chainguard Wolfi and scratch",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${GO_REPO}"
  ]
}

# ==========================================
# OpenSSL FIPS Targets
# ==========================================
target "openssl-base" {
  args = {
    FIPS_VERSION = OPENSSL_FIPS_VERSION
    CORE_VERSION = OPENSSL_CORE_VERSION
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${OPENSSL_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant OpenSSL development SDK image on Wolfi"
  }
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${OPENSSL_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant OpenSSL standard runtime image on Wolfi"
  }
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
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${OPENSSL_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant Zero-CVE distroless OpenSSL container on Wolfi"
  }
}

# ==========================================
# OpenJDK FIPS Targets
# ==========================================
target "openjdk-base" {
  args = {
    JAVA_VERSION         = OPENJDK_VERSION
    JAVA_FULL_VERSION    = OPENJDK_FULL_VERSION
    BASE_IMAGE           = BASE_IMAGE
    ALPINE_IMAGE         = "alpine@sha256:6baf43584bcb78f2e5847d1de515f23499913ac9f12bdf834811a3145eb11ca1"

    JDK_AMD64_URL        = OPENJDK_JDK_AMD64_URL
    JDK_AMD64_SHA        = OPENJDK_JDK_AMD64_SHA
    JDK_ARM64_URL        = OPENJDK_JDK_ARM64_URL
    JDK_ARM64_SHA        = OPENJDK_JDK_ARM64_SHA

    JRE_AMD64_URL        = OPENJDK_JRE_AMD64_URL
    JRE_AMD64_SHA        = OPENJDK_JRE_AMD64_SHA
    JRE_ARM64_URL        = OPENJDK_JRE_ARM64_URL
    JRE_ARM64_SHA        = OPENJDK_JRE_ARM64_SHA

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
    LIBCRYPTO3_VER         = "3.6.2-r5"
    LIBGCC_VER             = OPENSSL_LIBGCC_VER
    LIBSSL3_VER            = "3.6.2-r5"
    LIBSTDCPP_VER          = OPENSSL_LIBSTDC_PLUS_PLUS_VER
    LIBXCRYPT_VER          = OPENSSL_LIBXCRYPT_VER
    NCURSES_VER            = "6.6.20260608-r0"
    POSIX_LIBC_UTILS_VER   = OPENSSL_POSIX_LIBC_UTILS_VER
    TZDATA_VER             = OPENSSL_TZDATA_VER
    WOLFI_BASELAYOUT_VER   = OPENSSL_WOLFI_BASELAYOUT_VER
    WOLFI_KEYS_VER         = OPENSSL_WOLFI_KEYS_VER
    ZLIB_VER               = OPENSSL_ZLIB_VER
  }
}

target "openjdk-dev" {
  inherits = ["openjdk-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openjdk"
  dockerfile = "dockerfile"
  target = "openjdk-dev"
  tags = [
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${OPENJDK_VERSION}-dev",
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${OPENJDK_VERSION}-jdk_standard",
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:dev"
  ]
  cache-from = ["type=gha,scope=openjdk-dev"]
  cache-to = ["type=gha,mode=max,scope=openjdk-dev,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${OPENJDK_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant OpenJDK development SDK image on Wolfi"
  }
}

target "openjdk-standard" {
  inherits = ["openjdk-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openjdk"
  dockerfile = "dockerfile"
  target = "openjdk-standard"
  tags = [
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${OPENJDK_VERSION}",
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${OPENJDK_VERSION}-jre_standard",
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:latest"
  ]
  cache-from = ["type=gha,scope=openjdk-standard"]
  cache-to = ["type=gha,mode=max,scope=openjdk-standard,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${OPENJDK_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant OpenJDK standard JRE runtime on Wolfi"
  }
}

target "openjdk-prod" {
  inherits = ["openjdk-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openjdk"
  dockerfile = "dockerfile"
  target = "openjdk-distroless"
  tags = [
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${OPENJDK_VERSION}-distroless",
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:${OPENJDK_VERSION}-jre_distroless",
    "${REGISTRY}/${OWNER}/${OPENJDK_REPO}:distroless"
  ]
  cache-from = ["type=gha,scope=openjdk-distroless"]
  cache-to = ["type=gha,mode=max,scope=openjdk-distroless,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${OPENJDK_REPO}"
    "org.opencontainers.image.licenses" = "Apache-2.0"
    "org.opencontainers.image.description" = "Hardened FIPS 140-3 compliant Zero-CVE distroless OpenJDK JRE container on Wolfi"
  }
}


