variable "REGISTRY" {
  default = "ghcr.io"
}

variable "OWNER" {
  default = "taha2samy-3"
}

variable "REPO" {
  default = "node"
}

variable "BASE_IMAGE" {
  default = "cgr.dev/chainguard/wolfi-base@sha256:02dab76bd852a70556b5b2002195c8a5fdab77d323c433bf6642aab080489795"
}

variable "NODE_22_FULL_VERSION" {
  default = "22.23.1-r1"
}

variable "NODE_24_FULL_VERSION" {
  default = "24.18.0-r2"
}

group "default" {
  targets = ["dev", "prod", "python-dev", "python-prod"]
}


target "dev" {
  name = "dev-${item.version}"
  matrix = {
    item = [
      { version = "22", full_version = NODE_22_FULL_VERSION },
      { version = "24", full_version = NODE_24_FULL_VERSION }
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
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Node.js ${item.version} (${item.full_version}) development image with npm based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Node.js ${item.version} (${item.full_version}) development image with npm based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${REPO}"
  ]
}

target "prod" {
  name = "prod-${item.version}"
  matrix = {
    item = [
      { version = "22", full_version = NODE_22_FULL_VERSION },
      { version = "24", full_version = NODE_24_FULL_VERSION }
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








variable "PYTHON_REPO" {
  default = "python"
}

variable "PYTHON_3_10_FULL_VERSION" { default = "3.10.20-r10" }
variable "PYTHON_3_11_FULL_VERSION" { default = "3.11.15-r8" }
variable "PYTHON_3_12_FULL_VERSION" { default = "3.12.13-r10" }
variable "PYTHON_3_13_FULL_VERSION" { default = "3.13.14-r2" }
variable "PYTHON_3_14_FULL_VERSION" { default = "3.14.6-r3" }

target "python-dev" {
  name = "python-dev-${item.version}"
  matrix = {
    item = [
      { version = "3.10", full_version = PYTHON_3_10_FULL_VERSION },
      { version = "3.11", full_version = PYTHON_3_11_FULL_VERSION },
      { version = "3.12", full_version = PYTHON_3_12_FULL_VERSION },
      { version = "3.13", full_version = PYTHON_3_13_FULL_VERSION },
      { version = "3.14", full_version = PYTHON_3_14_FULL_VERSION }
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
  cache-from = ["type=gha,scope=python-dev-${item.version}"]
  cache-to = ["type=gha,mode=max,scope=python-dev-${item.version},compression=zstd,compression-level=3"]
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
  name = "python-prod-${item.version}"
  matrix = {
    item = [
      { version = "3.10", full_version = PYTHON_3_10_FULL_VERSION },
      { version = "3.11", full_version = PYTHON_3_11_FULL_VERSION },
      { version = "3.12", full_version = PYTHON_3_12_FULL_VERSION },
      { version = "3.13", full_version = PYTHON_3_13_FULL_VERSION },
      { version = "3.14", full_version = PYTHON_3_14_FULL_VERSION }
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
  cache-from = ["type=gha,scope=python-prod-${item.version}"]
  cache-to = ["type=gha,mode=max,scope=python-prod-${item.version},compression=zstd,compression-level=3"]
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
