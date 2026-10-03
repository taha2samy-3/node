# =============================================================================
# Standalone Docker Bake Definition for Wolfi OpenJDK FIPS
# =============================================================================

variable "REGISTRY" {
  default = "ghcr.io"
}

variable "OWNER" {
  default = "taha2samy-3"
}

variable "REPO_NAME" {
  default = "wolfi-openjdk-fips"
}

variable "OPENJDK_VERSION" {
  default = "21"
}

variable "OPENJDK_FULL_VERSION" {
  default = "21.0.11+10-LTS"
}

function "tag" {
  params = [tag_name]
  result = ["${REGISTRY}/${OWNER}/${REPO_NAME}:${tag_name}"]
}

group "default" {
  targets = ["standard", "distroless", "development"]
}

target "common" {
  context    = "."
  dockerfile = "dockerfile"
  platforms  = ["linux/amd64", "linux/arm64"]
  output = [
    "type=registry,compression=zstd,force-compression=true"
  ]
  attest = [
    "type=sbom",
    "type=provenance,mode=max"
  ]
  args = {
    JAVA_VERSION         = "${OPENJDK_VERSION}"
    JAVA_FULL_VERSION    = "${OPENJDK_FULL_VERSION}"
    BASE_IMAGE           = "${BASE_IMAGE}"
    ALPINE_IMAGE         = "${ALPINE_IMAGE}"

    JDK_AMD64_URL        = "${JDK_21_AMD64_URL}"
    JDK_AMD64_SHA        = "${JDK_21_AMD64_SHA}"
    JDK_ARM64_URL        = "${JDK_21_ARM64_URL}"
    JDK_ARM64_SHA        = "${JDK_21_ARM64_SHA}"

    JRE_AMD64_URL        = "${JRE_21_AMD64_URL}"
    JRE_AMD64_SHA        = "${JRE_21_AMD64_SHA}"
    JRE_ARM64_URL        = "${JRE_21_ARM64_URL}"
    JRE_ARM64_SHA        = "${JRE_21_ARM64_SHA}"

    BC_FIPS_VERSION      = "${BC_FIPS_VERSION}"
    BC_FIPS_URL          = "${BC_FIPS_URL}"
    BC_FIPS_SHA          = "${BC_FIPS_SHA}"

    BC_UTIL_FIPS_VERSION = "${BC_UTIL_FIPS_VERSION}"
    BC_UTIL_FIPS_URL     = "${BC_UTIL_FIPS_URL}"
    BC_UTIL_FIPS_SHA     = "${BC_UTIL_FIPS_SHA}"

    BC_TLS_FIPS_VERSION  = "${BC_TLS_FIPS_VERSION}"
    BC_TLS_FIPS_URL      = "${BC_TLS_FIPS_URL}"
    BC_TLS_FIPS_SHA      = "${BC_TLS_FIPS_SHA}"

    APK_TOOLS_VER          = "${APK_TOOLS_VER}"
    BASH_VER               = "${BASH_VER}"
    BUSYBOX_VER            = "${BUSYBOX_VER}"
    CA_CERTIFICATES_VER    = "${CA_CERTIFICATES_VER}"
    CURL_VER               = "${CURL_VER}"
    GLIBC_VER              = "${GLIBC_VER}"
    GLIBC_LOCALE_POSIX_VER = "${GLIBC_LOCALE_POSIX_VER}"
    LD_LINUX_VER           = "${LD_LINUX_VER}"
    LIBCRYPT1_VER          = "${LIBCRYPT1_VER}"
    LIBCRYPTO3_VER         = "${LIBCRYPTO3_VER}"
    LIBGCC_VER             = "${LIBGCC_VER}"
    LIBSSL3_VER            = "${LIBSSL3_VER}"
    LIBSTDCPP_VER          = "${LIBSTDCPP_VER}"
    LIBXCRYPT_VER          = "${LIBXCRYPT_VER}"
    NCURSES_VER            = "${NCURSES_VER}"
    POSIX_LIBC_UTILS_VER   = "${POSIX_LIBC_UTILS_VER}"
    TZDATA_VER             = "${TZDATA_VER}"
    WOLFI_BASELAYOUT_VER   = "${WOLFI_BASELAYOUT_VER}"
    WOLFI_KEYS_VER         = "${WOLFI_KEYS_VER}"
    ZLIB_VER               = "${ZLIB_VER}"
  }
}

### ---------- STANDARD IMAGE (JRE) ----------
target "standard" {
  inherits = ["common"]
  target   = "openjdk-standard"

  tags = concat(
    tag("${OPENJDK_VERSION}"),
    tag("${OPENJDK_VERSION}-jre_standard"),
    tag("latest")
  )

  cache-from = ["type=gha,scope=openjdk-standard"]
  cache-to   = ["type=gha,scope=openjdk-standard,mode=max"]
}

### ---------- DISTROLESS IMAGE (JRE) ----------
target "distroless" {
  inherits = ["common"]
  target   = "openjdk-distroless"

  tags = concat(
    tag("${OPENJDK_VERSION}-distroless"),
    tag("${OPENJDK_VERSION}-jre_distroless"),
    tag("distroless")
  )

  cache-from = ["type=gha,scope=openjdk-distroless"]
  cache-to   = ["type=gha,scope=openjdk-distroless,mode=max"]
}

### ---------- DEV IMAGE (JDK SDK) ----------
target "development" {
  inherits = ["common"]
  target   = "openjdk-dev"

  tags = concat(
    tag("${OPENJDK_VERSION}-dev"),
    tag("${OPENJDK_VERSION}-jdk_standard"),
    tag("dev")
  )

  cache-from = ["type=gha,scope=openjdk-development"]
  cache-to   = ["type=gha,scope=openjdk-development,mode=max"]
}
