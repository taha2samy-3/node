variable "REGISTRY" {
  default = "ghcr.io"
}

variable "OWNER" {
  default = "taha2samy-3"
}

variable "BASE_IMAGE" {
  default = "cgr.dev/chainguard/wolfi-base:latest"
}

variable "REPO" {
  default = "node"
}

group "default" {
  targets = ["dev", "prod"]
}

target "dev" {
  name = "dev-${version}"
  matrix = {
    version = ["22", "24"]
  }
  context = "."
  dockerfile = "Dockerfile"
  target = "full-dev"
  args = {
    NODE_VERSION = version
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${REPO}:${version}-dev",
    "${REGISTRY}/${OWNER}/${REPO}:v${version}-dev"
  ]
  cache-from = ["type=gha,scope=dev-${version}"]
  cache-to = ["type=gha,mode=max,scope=dev-${version},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Node.js ${version} development image with npm based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Node.js ${version} development image with npm based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${REPO}"
  ]
}

target "prod" {
  name = "prod-${version}"
  matrix = {
    version = ["22", "24"]
  }
  context = "."
  dockerfile = "Dockerfile"
  target = "minimal"
  args = {
    NODE_VERSION = version
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${REPO}:${version}",
    "${REGISTRY}/${OWNER}/${REPO}:v${version}"
  ]
  cache-from = ["type=gha,scope=prod-${version}"]
  cache-to = ["type=gha,mode=max,scope=prod-${version},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Node.js ${version} production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Ultra-secure minimal Node.js ${version} production runtime based on Chainguard Wolfi and scratch",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${REPO}"
  ]
}