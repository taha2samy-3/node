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
  default = "cgr.dev/chainguard/wolfi-base@sha256:dbcc3a4a3b1b9e68420a4742940aa6267c97e61811736a5fef0918a06ade1827"
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
  default = "24.22.1-r2"
}

variable "NODE_26_FULL_VERSION" {
  default = "26.12.1-r2"
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
# PHP Versions (the branches php.net supports; each pin is at or above the PHP2Shell fix:
# 8.2.35, 8.3.36, 8.4.27, 8.5.12)
# ==========================================
variable "PHP_REPO" {
  default = "php"
}

variable "PHP_8_2_FULL_VERSION" { default = "8.2.35-r0" }
variable "PHP_8_3_FULL_VERSION" { default = "8.3.36-r0" }
variable "PHP_8_4_FULL_VERSION" { default = "8.4.27-r0" }
variable "PHP_8_5_FULL_VERSION" { default = "8.5.12-r0" }

# Composer for the PHP dev images, checked against getcomposer.org's published SHA-256
variable "COMPOSER_VERSION" { default = "2.11.0" }
variable "COMPOSER_SHA256" { default = "9674f12a2a181100d889ebfd0b4510805b3e94cea57869b14b383753d602599b" }

# ==========================================
# Python Versions
# ==========================================
variable "PYTHON_REPO" {
  default = "python"
}

variable "PYTHON_3_10_FULL_VERSION" { default = "3.10.22-r6" }
variable "PYTHON_3_11_FULL_VERSION" { default = "3.11.18-r1" }
variable "PYTHON_3_12_FULL_VERSION" { default = "3.12.16-r2" }
variable "PYTHON_3_13_FULL_VERSION" { default = "3.13.17_git20261023-r1" }
variable "PYTHON_3_14_FULL_VERSION" { default = "3.14.8_git20261021-r3" }

# ==========================================
# Bun Versions
# ==========================================
variable "BUN_REPO" {
  default = "bun"
}

variable "BUN_1_FULL_VERSION" {
  default = "1.4.4-r0"
}

# ==========================================
# Java Versions
# ==========================================
variable "JAVA_REPO" {
  default = "java"
}

variable "JAVA_17_FULL_VERSION" { default = "17.0.21.0.3-r0" }
variable "JAVA_21_FULL_VERSION" { default = "21.0.13.0.3-r0" }
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
variable "GO_1_25_FULL_VERSION" { default = "1.25.12-r1" }
variable "GO_1_26_FULL_VERSION" { default = "1.26.10-r0" }
variable "GO_1_27_FULL_VERSION" { default = "1.27.3-r0" }

variable "GO_FIPS_REPO" {
  default = "go-fips"
}

# ==========================================
# BoringSSL FIPS Versions
# ==========================================
variable "BORINGSSL_REPO" {
  default = "boringssl-fips"
}

# Date of the pinned commit. BoringSSL's FIPS releases are tags named fips-YYYYMMDD; this commit
# is not one of them, so the label must not look like one.
variable "BORINGSSL_VERSION" {
  default = "20240528"
}

# boringssl main, 2024-05-28 ("Expose the FIPS module hash at build- and run-time"). Not a
# CMVP-validated release: certificate #4735 covers tag fips-20220613 (0c6f40132b8) built with the
# toolchain its security policy names, and that tag does not compile with Wolfi's current clang.
variable "BORINGSSL_COMMIT" {
  default = "85897d07196b7bf164dbd4673fc78b762aff3e8b"
}

variable "BORINGSSL_STATIC_IMAGE" {
  default = "cgr.dev/chainguard/static@sha256:fc42af33e643f20d08baf03cddcc1c02ba57052dfb02edb0d79f3fc47bcea8d9"
}

# ==========================================
# OpenSSL FIPS Versions
# ==========================================
variable "OPENSSL_REPO" {
  default = "openssl-fips"
}


variable "OPENSSL_CORE_VERSION" {
  default = "3.5.9"
}

variable "OPENSSL_CORE_SHA256" {
  default = "603f5602e2eef00d77fbd429d34dcd5822bb301757a1bc9cdb24c670f1eb859a"
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
  default = "cgr.dev/chainguard/static@sha256:fc42af33e643f20d08baf03cddcc1c02ba57052dfb02edb0d79f3fc47bcea8d9"
}
variable "OPENSSL_BUILD_BASE_VER" { default = "1-r10" }
variable "OPENSSL_PERL_VER" { default = "5.44.0-r4" }
variable "OPENSSL_LINUX_HEADERS_VER" { default = "7.3-r0" }
variable "OPENSSL_WGET_VER" { default = "1.25.0-r20" }
variable "OPENSSL_CA_CERTIFICATES_VER" { default = "20261020-r0" }
variable "OPENSSL_LIBSTDC_PLUS_PLUS_VER" { default = "16.2.0-r2" }
variable "OPENSSL_ZLIB_VER" { default = "1.3.2.1_rc20260921-r1" }
variable "OPENSSL_TZDATA_VER" { default = "2026f-r0" }
variable "OPENSSL_POSIX_LIBC_UTILS_VER" { default = "2.43-r13" }
variable "OPENSSL_PKGCONF_VER" { default = "3.0.10-r2" }
variable "OPENSSL_PCRE_DEV_VER" { default = "8.45-r11" }
variable "OPENSSL_ZLIB_DEV_VER" { default = "1.3.2.1_rc20260921-r1" }
variable "OPENSSL_BASH_VER" { default = "5.3-r14" }
variable "OPENSSL_CURL_VER" { default = "8.23.0-r2" }
variable "OPENSSL_JQ_VER" { default = "1.8.2-r3" }
variable "OPENSSL_UNZIP_VER" { default = "6.0-r8" }
variable "OPENSSL_APK_TOOLS_VER" { default = "2.14.12-r0" }
variable "OPENSSL_BUSYBOX_VER" { default = "1.38.0-r3" }
variable "OPENSSL_GLIBC_VER" { default = "2.43-r13" }
variable "OPENSSL_GLIBC_LOCALE_POSIX_VER" { default = "2.43-r13" }
variable "OPENSSL_LD_LINUX_VER" { default = "2.43-r13" }
variable "OPENSSL_LIBCRYPT1_VER" { default = "2.43-r13" }
variable "OPENSSL_LIBXCRYPT_VER" { default = "4.5.2-r6" }
variable "OPENSSL_LIBGCC_VER" { default = "16.2.0-r2" }
variable "OPENSSL_WOLFI_BASE_VER" { default = "1-r7" }
variable "OPENSSL_WOLFI_BASELAYOUT_VER" { default = "20230201-r31" }
variable "OPENSSL_WOLFI_KEYS_VER" { default = "1-r14" }

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
variable "OPENJDK_8_FULL_VERSION" { default = "1.8.0_504-b01" }
variable "OPENJDK_8_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u504-b01/OpenJDK8U-jdk_x64_linux_hotspot_8u504b01.tar.gz" }
variable "OPENJDK_8_JDK_AMD64_SHA" { default = "9c70e102f527ac674ac2fe9c7d47b9a04e2d19842ba5ab8e9b33f368bbadfaea" }
variable "OPENJDK_8_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u504-b01/OpenJDK8U-jdk_aarch64_linux_hotspot_8u504b01.tar.gz" }
variable "OPENJDK_8_JDK_ARM64_SHA" { default = "57b7ed8af9d48542bb49ff7894448040b17bea0a48b41677d11ecaec6129768d" }
variable "OPENJDK_8_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u504-b01/OpenJDK8U-jre_x64_linux_hotspot_8u504b01.tar.gz" }
variable "OPENJDK_8_JRE_AMD64_SHA" { default = "52dcd578baca1d3e449ea86768a9129c0ee04d7b22565695498353cc66940c61" }
variable "OPENJDK_8_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin8-binaries/releases/download/jdk8u504-b01/OpenJDK8U-jre_aarch64_linux_hotspot_8u504b01.tar.gz" }
variable "OPENJDK_8_JRE_ARM64_SHA" { default = "9ae9c4dd80fc8f3c4081b480c7d42346e9e4cbee5ae58198fca11e0fc1a19163" }

# Eclipse Temurin 17
variable "OPENJDK_17_FULL_VERSION" { default = "17.0.21+9" }
variable "OPENJDK_17_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.21%2B9/OpenJDK17U-jdk_x64_linux_hotspot_17.0.21_9.tar.gz" }
variable "OPENJDK_17_JDK_AMD64_SHA" { default = "8b9b611d917e3dfd8419d3566b5949226f69b052fed7e109c1368add1dfe8711" }
variable "OPENJDK_17_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.21%2B9/OpenJDK17U-jdk_aarch64_linux_hotspot_17.0.21_9.tar.gz" }
variable "OPENJDK_17_JDK_ARM64_SHA" { default = "3e4eca7ead088f080af1476007decf010a240a1eb4e1e78c54fa32fbcc347084" }
variable "OPENJDK_17_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.21%2B9/OpenJDK17U-jre_x64_linux_hotspot_17.0.21_9.tar.gz" }
variable "OPENJDK_17_JRE_AMD64_SHA" { default = "9f41bf88c7900c7097444a1bdeb84146ae692bc08842490ab098063c74bf9a8a" }
variable "OPENJDK_17_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.21%2B9/OpenJDK17U-jre_aarch64_linux_hotspot_17.0.21_9.tar.gz" }
variable "OPENJDK_17_JRE_ARM64_SHA" { default = "1114f09d6174f54270c3117410b5e4022b43ebc0b43b751af08b927c55ed7bb5" }

# Eclipse Temurin 21
variable "OPENJDK_21_FULL_VERSION" { default = "21.0.13+9-LTS" }
variable "OPENJDK_21_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.13%2B9/OpenJDK21U-jdk_x64_linux_hotspot_21.0.13_9.tar.gz" }
variable "OPENJDK_21_JDK_AMD64_SHA" { default = "d7f5d5cf865a2902b70ff549b97586a7d3f234e016f041ab447ea740c7d66d1c" }
variable "OPENJDK_21_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.13%2B9/OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.13_9.tar.gz" }
variable "OPENJDK_21_JDK_ARM64_SHA" { default = "e3522e707fc7dbe2a72c30746b1e7068301a0213ecd213d4491f35a14eb55578" }
variable "OPENJDK_21_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.13%2B9/OpenJDK21U-jre_x64_linux_hotspot_21.0.13_9.tar.gz" }
variable "OPENJDK_21_JRE_AMD64_SHA" { default = "a535a1df9c6284d9618872984e026ae0352d1f7e9e0605425c0e6114f47351dd" }
variable "OPENJDK_21_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.13%2B9/OpenJDK21U-jre_aarch64_linux_hotspot_21.0.13_9.tar.gz" }
variable "OPENJDK_21_JRE_ARM64_SHA" { default = "b1734db7ade49c3f6acc6ae06233b8c2dd90e3e2f00f67000ae1c972aaa64d8c" }

# Eclipse Temurin 25
variable "OPENJDK_25_FULL_VERSION" { default = "25.0.5+8-LTS" }
variable "OPENJDK_25_JDK_AMD64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jdk_x64_linux_hotspot_25.0.5_8.tar.gz" }
variable "OPENJDK_25_JDK_AMD64_SHA" { default = "68982529869257d0ee6b824ec5aa270ff8b118bb438670da0b97ebdab178d7fb" }
variable "OPENJDK_25_JDK_ARM64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jdk_aarch64_linux_hotspot_25.0.5_8.tar.gz" }
variable "OPENJDK_25_JDK_ARM64_SHA" { default = "bb5b2ded252f21c6090cf780b0a408ad0d83bbb557e702955643557f13231880" }
variable "OPENJDK_25_JRE_AMD64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jre_x64_linux_hotspot_25.0.5_8.tar.gz" }
variable "OPENJDK_25_JRE_AMD64_SHA" { default = "6fac98f0c8202efc3135a9e9e42aa61963ec42d1c5cbb40caf231e7b14a24ef6" }
variable "OPENJDK_25_JRE_ARM64_URL" { default = "https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jre_aarch64_linux_hotspot_25.0.5_8.tar.gz" }
variable "OPENJDK_25_JRE_ARM64_SHA" { default = "963931723891302ebb2687178532c3d793d71e2577cd058061c7efb396140a86" }

# FIPS 140-3 certificate #4943 covers BC-FJA 2.1.1: change only when a new certificate lists the version
variable "OPENJDK_BC_FIPS_VERSION" { default = "2.1.1" }
variable "OPENJDK_BC_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bc-fips/2.1.1/bc-fips-2.1.1.jar" }
variable "OPENJDK_BC_FIPS_SHA" { default = "a430d935ad6cec6d045930758457740f5a5f8f9715894e347f6800f7926a7321" }

variable "OPENJDK_BC_UTIL_FIPS_VERSION" { default = "2.1.8" }
variable "OPENJDK_BC_UTIL_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bcutil-fips/2.1.8/bcutil-fips-2.1.8.jar" }
variable "OPENJDK_BC_UTIL_FIPS_SHA" { default = "f44904f61552c823bcc3686a24052ee3135212d547754eaa2ff6532e210103cb" }

variable "OPENJDK_BC_TLS_FIPS_VERSION" { default = "2.1.25" }
variable "OPENJDK_BC_TLS_FIPS_URL" { default = "https://repo1.maven.org/maven2/org/bouncycastle/bctls-fips/2.1.25/bctls-fips-2.1.25.jar" }
variable "OPENJDK_BC_TLS_FIPS_SHA" { default = "af604aa5b337725872651067a819ebc03aa298685572b0b2ad5343c786faad0a" }

variable "OPENJDK_KEYSTORE_PWD" { default = "changeit" }

# Image used only to download and verify the Temurin archives
variable "OPENJDK_ALPINE_IMAGE" { default = "alpine@sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a" }
variable "OPENJDK_LIBCRYPTO3_VER" { default = "3.6.5-r5" }
variable "OPENJDK_LIBSSL3_VER" { default = "3.6.5-r5" }
variable "OPENJDK_NCURSES_VER" { default = "6.6.20261024-r0" }


# ==========================================
# envoke (secrets-entrypoint) Binary
# ==========================================
variable "ENVOKE_VERSION" {
  default = "v1.0.2"
}

variable "ENVOKE_SHA256_AMD64" {
  default = "ced96d0d38c15f666b2f35204848b84c70eeb1f01940e99e52d10b0f3a23e8d2"
}

variable "ENVOKE_SHA256_ARM64" {
  default = "152e74002d6e73f9b47c23a346c71536e3520c607e9f59f6cb791cbe3ce33b97"
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
  targets = ["dev", "prod", "python-dev", "python-prod", "php-dev", "php-prod", "bun-dev", "bun-prod", "java-dev", "java-prod", "go-dev", "go-prod", "go-fips-dev", "go-fips-prod", "openssl-dev", "openssl-standard", "openssl-prod", "boringssl-dev", "boringssl-standard", "boringssl-prod", "openjdk", "node-fips"]
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
# PHP Targets
# ==========================================
target "php-dev" {
  inherits = ["_envoke"]
  name = "php-dev-${item.id}"
  matrix = {
    item = [
      { id = "8-2", version = "8.2", full_version = PHP_8_2_FULL_VERSION },
      { id = "8-3", version = "8.3", full_version = PHP_8_3_FULL_VERSION },
      { id = "8-4", version = "8.4", full_version = PHP_8_4_FULL_VERSION },
      { id = "8-5", version = "8.5", full_version = PHP_8_5_FULL_VERSION }
    ]
  }
  context = "."
  dockerfile = "php/dockerfile"
  target = "full-dev"
  args = {
    PHP_VERSION = item.version
    PHP_FULL_VERSION = item.full_version
    COMPOSER_VERSION = COMPOSER_VERSION
    COMPOSER_SHA256 = COMPOSER_SHA256
    BASE_IMAGE = BASE_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${PHP_REPO}:${item.version}-dev"
  ]
  cache-from = ["type=gha,scope=php-dev-${item.id}"]
  cache-to = ["type=gha,mode=max,scope=php-dev-${item.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "PHP ${item.version} (${item.full_version}) development image with PHP-FPM, Composer and hardened php.ini, based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=PHP ${item.version} (${item.full_version}) development image with PHP-FPM, Composer and hardened php.ini, based on Chainguard Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "php-prod" {
  inherits = ["_envoke"]
  name = "php-prod-${item.id}"
  matrix = {
    item = [
      { id = "8-2", version = "8.2", full_version = PHP_8_2_FULL_VERSION },
      { id = "8-3", version = "8.3", full_version = PHP_8_3_FULL_VERSION },
      { id = "8-4", version = "8.4", full_version = PHP_8_4_FULL_VERSION },
      { id = "8-5", version = "8.5", full_version = PHP_8_5_FULL_VERSION }
    ]
  }
  context = "."
  dockerfile = "php/dockerfile"
  target = "prod"
  args = {
    PHP_VERSION = item.version
    PHP_FULL_VERSION = item.full_version
    COMPOSER_VERSION = COMPOSER_VERSION
    COMPOSER_SHA256 = COMPOSER_SHA256
    BASE_IMAGE = BASE_IMAGE
  }
  platforms = ["linux/amd64", "linux/arm64"]
  tags = [
    "${REGISTRY}/${OWNER}/${PHP_REPO}:${item.version}"
  ]
  cache-from = ["type=gha,scope=php-prod-${item.id}"]
  cache-to = ["type=gha,mode=max,scope=php-prod-${item.id},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "PHP ${item.version} (${item.full_version}) PHP-FPM production image without shell or package manager, hardened php.ini, based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=PHP ${item.version} (${item.full_version}) PHP-FPM production image without shell or package manager, hardened php.ini, based on Chainguard Wolfi",
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
      { version = "1.24", full_version = GO_1_24_FULL_VERSION },
      { version = "1.25", full_version = GO_1_25_FULL_VERSION },
      { version = "1.26", full_version = GO_1_26_FULL_VERSION },
      { version = "1.27", full_version = GO_1_27_FULL_VERSION }
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
      { version = "1.24", full_version = GO_1_24_FULL_VERSION },
      { version = "1.25", full_version = GO_1_25_FULL_VERSION },
      { version = "1.26", full_version = GO_1_26_FULL_VERSION },
      { version = "1.27", full_version = GO_1_27_FULL_VERSION }
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
# Go FIPS Targets (BoringCrypto)
# ==========================================
target "go-fips-dev" {
  inherits = ["_envoke"]
  name = "go-fips-dev-${replace(item.version, ".", "-")}"
  matrix = {
    item = [
      { version = "1.22", full_version = GO_1_22_FULL_VERSION },
      { version = "1.23", full_version = GO_1_23_FULL_VERSION },
      { version = "1.24", full_version = GO_1_24_FULL_VERSION },
      { version = "1.25", full_version = GO_1_25_FULL_VERSION },
      { version = "1.26", full_version = GO_1_26_FULL_VERSION },
      { version = "1.27", full_version = GO_1_27_FULL_VERSION }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "go/dockerfile"
  target = "fips-dev"
  args = {
    GO_VERSION = item.version
    GO_FULL_VERSION = item.full_version
    BASE_IMAGE = BASE_IMAGE
  }
  tags = [
    "${REGISTRY}/${OWNER}/${GO_FIPS_REPO}:${item.version}-dev",
    "${REGISTRY}/${OWNER}/${GO_FIPS_REPO}:v${item.version}-dev"
  ]
  cache-from = ["type=gha,scope=go-fips-dev-${replace(item.version, ".", "-")}"]
  cache-to = ["type=gha,mode=max,scope=go-fips-dev-${replace(item.version, ".", "-")},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Optimized Go ${item.version} FIPS development image with BoringCrypto based on Chainguard Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Optimized Go ${item.version} FIPS development image with BoringCrypto based on Chainguard Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "go-fips-prod" {
  inherits = ["_envoke"]
  name = "go-fips-prod-${replace(item.version, ".", "-")}"
  matrix = {
    item = [
      { version = "1.22", full_version = GO_1_22_FULL_VERSION },
      { version = "1.23", full_version = GO_1_23_FULL_VERSION },
      { version = "1.24", full_version = GO_1_24_FULL_VERSION },
      { version = "1.25", full_version = GO_1_25_FULL_VERSION },
      { version = "1.26", full_version = GO_1_26_FULL_VERSION },
      { version = "1.27", full_version = GO_1_27_FULL_VERSION }
    ]
  }
  platforms = ["linux/amd64", "linux/arm64"]
  context = "."
  dockerfile = "go/dockerfile"
  target = "fips-prod"
  args = {
    GO_VERSION = item.version
    BASE_IMAGE = BASE_IMAGE
  }
  tags = [
    "${REGISTRY}/${OWNER}/${GO_FIPS_REPO}:${item.version}",
    "${REGISTRY}/${OWNER}/${GO_FIPS_REPO}:v${item.version}"
  ]
  cache-from = ["type=gha,scope=go-fips-prod-${replace(item.version, ".", "-")}"]
  cache-to = ["type=gha,mode=max,scope=go-fips-prod-${replace(item.version, ".", "-")},compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "MIT"
    "org.opencontainers.image.description" = "Ultra-secure minimal distroless base for Go ${item.version} FIPS apps based on Chainguard Wolfi and scratch"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Ultra-secure minimal distroless base for Go ${item.version} FIPS apps based on Chainguard Wolfi and scratch",
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
    "org.opencontainers.image.description" = "Hardened OpenSSL FIPS 140-3 development SDK image on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened OpenSSL FIPS 140-3 development SDK image on Wolfi",
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
    "org.opencontainers.image.description" = "Hardened OpenSSL FIPS 140-3 standard runtime image on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened OpenSSL FIPS 140-3 standard runtime image on Wolfi",
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
    "org.opencontainers.image.description" = "Hardened OpenSSL FIPS 140-3 distroless container on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened OpenSSL FIPS 140-3 distroless container on Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

# ==========================================
# BoringSSL FIPS Targets
# ==========================================
target "boringssl-base" {
  args = {
    BORINGSSL_VERSION = BORINGSSL_VERSION
    BORINGSSL_COMMIT = BORINGSSL_COMMIT
    BASE_IMAGE = BASE_IMAGE
    STATIC_IMAGE = BORINGSSL_STATIC_IMAGE
  }
}

target "boringssl-dev" {
  inherits = ["boringssl-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "boringssl"
  dockerfile = "dockerfile"
  target = "boringssl-dev"
  tags = [
    "${REGISTRY}/${OWNER}/${BORINGSSL_REPO}:${BORINGSSL_VERSION}-dev",
    "${REGISTRY}/${OWNER}/${BORINGSSL_REPO}:dev"
  ]
  cache-from = ["type=gha,scope=boringssl-dev"]
  cache-to = ["type=gha,mode=max,scope=boringssl-dev,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "OpenSSL"
    "org.opencontainers.image.description" = "Hardened BoringSSL (FIPS build flags) development SDK image on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened BoringSSL (FIPS build flags) development SDK image on Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "boringssl-standard" {
  inherits = ["boringssl-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "boringssl"
  dockerfile = "dockerfile"
  target = "boringssl-standard"
  tags = [
    "${REGISTRY}/${OWNER}/${BORINGSSL_REPO}:${BORINGSSL_VERSION}",
    "${REGISTRY}/${OWNER}/${BORINGSSL_REPO}:latest"
  ]
  cache-from = ["type=gha,scope=boringssl-standard"]
  cache-to = ["type=gha,mode=max,scope=boringssl-standard,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "OpenSSL"
    "org.opencontainers.image.description" = "Hardened BoringSSL (FIPS build flags) standard runtime image on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened BoringSSL (FIPS build flags) standard runtime image on Wolfi",
    "manifest:org.opencontainers.image.source=https://github.com/${OWNER}/${SOURCE_REPO}"
  ]
}

target "boringssl-prod" {
  inherits = ["boringssl-base"]
  platforms = ["linux/amd64", "linux/arm64"]
  context = "boringssl"
  dockerfile = "dockerfile"
  target = "boringssl-distroless"
  tags = [
    "${REGISTRY}/${OWNER}/${BORINGSSL_REPO}:${BORINGSSL_VERSION}-distroless",
    "${REGISTRY}/${OWNER}/${BORINGSSL_REPO}:distroless"
  ]
  cache-from = ["type=gha,scope=boringssl-distroless"]
  cache-to = ["type=gha,mode=max,scope=boringssl-distroless,compression=zstd,compression-level=3"]
  labels = {
    "org.opencontainers.image.authors" = "Taha Samy"
    "org.opencontainers.image.source" = "https://github.com/${OWNER}/${SOURCE_REPO}"
    "org.opencontainers.image.licenses" = "OpenSSL"
    "org.opencontainers.image.description" = "Hardened BoringSSL (FIPS build flags) distroless container on Wolfi"
  }
  annotations = [
    "manifest:org.opencontainers.image.description=Hardened BoringSSL (FIPS build flags) distroless container on Wolfi",
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
      { id = "dev", stage = "openjdk-dev", tag_suffix = "-dev", legacy_tag = "jdk_standard", floating_tag = "dev", description = "Hardened OpenJDK FIPS 140-3 development SDK image on Wolfi" },
      { id = "standard", stage = "openjdk-standard", tag_suffix = "", legacy_tag = "jre_standard", floating_tag = "latest", description = "Hardened OpenJDK FIPS 140-3 standard JRE runtime on Wolfi" },
      { id = "prod", stage = "openjdk-distroless", tag_suffix = "-distroless", legacy_tag = "jre_distroless", floating_tag = "distroless", description = "Hardened OpenJDK FIPS 140-3 distroless JRE container on Wolfi" }
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
