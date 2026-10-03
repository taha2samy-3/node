# OpenJDK FIPS pinned dependencies and versions

# --- Base Images (Pinned by Digest) ---
variable "BASE_IMAGE" {
  default = "cgr.dev/chainguard/wolfi-base@sha256:b78bb982194828b6c9c214230bf34d51944e2102ea8468f01ac21e5f99328efd"
}

variable "ALPINE_IMAGE" {
  default = "alpine@sha256:6baf43584bcb78f2e5847d1de515f23499913ac9f12bdf834811a3145eb11ca1"
}

# --- Java Versions (LTS) ---
variable "OPENJDK_VERSION" {
  default = "21"
}

variable "OPENJDK_FULL_VERSION" {
  default = "21.0.11+10-LTS"
}

# Adoptium Temurin 21 (LTS)
variable "JDK_21_AMD64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jdk_x64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "JDK_21_AMD64_SHA" {
  default = "4b2220e232a97997b436ca6ab15cbf70171ecff52958a46159dfa5a8c44ca4de"
}
variable "JDK_21_ARM64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jdk_aarch64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "JDK_21_ARM64_SHA" {
  default = "8d498ec88e1c1989fab95c6784240ab92d011e29c54d20a3f9c324b13476f9ad"
}
variable "JRE_21_AMD64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jre_x64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "JRE_21_AMD64_SHA" {
  default = "e5038aae3ca9ff670bc696496b0728dbd23d280026bad30291cb919221ecfdcb"
}
variable "JRE_21_ARM64_URL" {
  default = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.11%2B10/OpenJDK21U-jre_aarch64_linux_hotspot_21.0.11_10.tar.gz"
}
variable "JRE_21_ARM64_SHA" {
  default = "fa23d9d9945053e67bcc7638410eabf1e17a7672c7c95a24f70cd08b8407d36e"
}

# Adoptium Temurin 17 (LTS)
variable "OPENJDK_17_FULL_VERSION" {
  default = "17.0.19+10"
}
variable "JDK_17_AMD64_URL" {
  default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jdk_x64_linux_hotspot_17.0.19_10.tar.gz"
}
variable "JDK_17_AMD64_SHA" {
  default = "d8afc263758141a66e0e3aafc321e783f7016696f4eaea067d340a269037d331"
}
variable "JDK_17_ARM64_URL" {
  default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jdk_aarch64_linux_hotspot_17.0.19_10.tar.gz"
}
variable "JDK_17_ARM64_SHA" {
  default = "83a52172678ec8975164648654869cb2e71d7c748b47aca94b29bbfa10c18e81"
}
variable "JRE_17_AMD64_URL" {
  default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jre_x64_linux_hotspot_17.0.19_10.tar.gz"
}
variable "JRE_17_AMD64_SHA" {
  default = "adb5a2364baa51de1ef91bb9911f5a61d24b045fe1d6647cb8050272a3a8ee75"
}
variable "JRE_17_ARM64_URL" {
  default = "https://github.com/adoptium/temurin17-binaries/releases/download/jdk-17.0.19%2B10/OpenJDK17U-jre_aarch64_linux_hotspot_17.0.19_10.tar.gz"
}
variable "JRE_17_ARM64_SHA" {
  default = "aae834297a87736869745be7c1fca3207ea9167c5824f41c88b0ebb2e3ccb9b1"
}

# --- Bouncy Castle FIPS Cryptographic Module ---
variable "BC_FIPS_VERSION" {
  default = "2.1.2"
}
variable "BC_FIPS_URL" {
  default = "https://repo1.maven.org/maven2/org/bouncycastle/bc-fips/2.1.2/bc-fips-2.1.2.jar"
}
variable "BC_FIPS_SHA" {
  default = "044fcd8a29d236edea8a5b414406cdae63b475f9ad9f05fe2dc904a277941115"
}

variable "BC_UTIL_FIPS_VERSION" {
  default = "2.1.5"
}
variable "BC_UTIL_FIPS_URL" {
  default = "https://repo1.maven.org/maven2/org/bouncycastle/bcutil-fips/2.1.5/bcutil-fips-2.1.5.jar"
}
variable "BC_UTIL_FIPS_SHA" {
  default = "503aaf5c2c5b7c729547462efe13699b5f6dacf9be150b7c48bba974b793dc92"
}

variable "BC_TLS_FIPS_VERSION" {
  default = "2.1.22"
}
variable "BC_TLS_FIPS_URL" {
  default = "https://repo1.maven.org/maven2/org/bouncycastle/bctls-fips/2.1.22/bctls-fips-2.1.22.jar"
}
variable "BC_TLS_FIPS_SHA" {
  default = "688410563445e1a65ff33cb67842499f0788994d752c3df8f7ea4a0d40ddbf50"
}

# --- Wolfi OS Packages ---
variable "APK_TOOLS_VER" { default = "2.14.10-r12" }
variable "BASH_VER" { default = "5.3-r12" }
variable "BUSYBOX_VER" { default = "1.37.0-r59" }
variable "CA_CERTIFICATES_VER" { default = "20260413-r0" }
variable "CURL_VER" { default = "8.20.0-r1" }
variable "GLIBC_VER" { default = "2.43-r8" }
variable "GLIBC_LOCALE_POSIX_VER" { default = "2.43-r8" }
variable "LD_LINUX_VER" { default = "2.43-r8" }
variable "LIBCRYPT1_VER" { default = "2.43-r8" }
variable "LIBCRYPTO3_VER" { default = "3.6.2-r5" }
variable "LIBGCC_VER" { default = "16.1.0-r2" }
variable "LIBSSL3_VER" { default = "3.6.2-r5" }
variable "LIBSTDCPP_VER" { default = "16.1.0-r2" }
variable "LIBXCRYPT_VER" { default = "4.5.2-r3" }
variable "NCURSES_VER" { default = "6.6.20260608-r0" }
variable "POSIX_LIBC_UTILS_VER" { default = "2.43-r8" }
variable "TZDATA_VER" { default = "2026b-r0" }
variable "WOLFI_BASELAYOUT_VER" { default = "20230201-r29" }
variable "WOLFI_KEYS_VER" { default = "1-r13" }
variable "ZLIB_VER" { default = "1.3.2-r3" }
