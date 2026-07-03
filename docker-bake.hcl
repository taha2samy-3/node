variable "REGISTRY" {
  default = "ghcr.io"
}

variable "OWNER" {
  default = "taha2samy-3"
}

variable "REPO" {
  default = "node"
}

group "default" {
  targets = ["dev", "prod"]
}

target "dev" {
  context = "."
  dockerfile = "Dockerfile"
  target = "full-dev"
  tags = [
    "${REGISTRY}/${OWNER}/${REPO}:22-dev",
    "${REGISTRY}/${OWNER}/${REPO}:v22-dev"
  ]
  cache-from = ["type=gha,scope=dev"]
  cache-to = ["type=gha,mode=max,scope=dev,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Node.js 22 development image with npm based on Chainguard Wolfi"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Optimized Node.js 22 development image with npm based on Chainguard Wolfi",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${REPO}"
  ]
}

target "prod" {
  context = "."
  dockerfile = "Dockerfile"
  target = "minimal"
  tags = [
    "${REGISTRY}/${OWNER}/${REPO}:22",
    "${REGISTRY}/${OWNER}/${REPO}:v22"
  ]
  cache-from = ["type=gha,scope=prod"]
  cache-to = ["type=gha,mode=max,scope=prod,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal Node.js 22 production runtime based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "index,manifest:org.opencontainers.image.description=Ultra-secure minimal Node.js 22 production runtime based on Chainguard Wolfi and scratch",
    "index,manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${REPO}"
  ]
}
