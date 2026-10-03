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
  targets = ["dev", "prod", "python-dev", "python-prod", "bun-dev", "bun-prod", "java-dev", "java-prod", "go-dev", "go-prod", "openssl-dev", "openssl-standard", "openssl-prod"]
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
target "openssl-dev" {
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openssl"
  dockerfile = "dockerfile"
  target = "openssl-dev"
  args = {
    FIPS_VERSION = OPENSSL_FIPS_VERSION
    CORE_VERSION = OPENSSL_CORE_VERSION
    BASE_IMAGE = BASE_IMAGE
  }
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
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openssl"
  dockerfile = "dockerfile"
  target = "openssl-standard"
  args = {
    FIPS_VERSION = OPENSSL_FIPS_VERSION
    CORE_VERSION = OPENSSL_CORE_VERSION
    BASE_IMAGE = BASE_IMAGE
  }
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
  platforms = ["linux/amd64", "linux/arm64"]
  context = "openssl"
  dockerfile = "dockerfile"
  target = "openssl-distroless"
  args = {
    FIPS_VERSION = OPENSSL_FIPS_VERSION
    CORE_VERSION = OPENSSL_CORE_VERSION
    BASE_IMAGE = BASE_IMAGE
  }
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


