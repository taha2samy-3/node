export interface FipsTestCase {
  id: string;
  name: string;
  suite: string;
  suiteId: 'core' | 'hash' | 'symmetric' | 'mac' | 'asymmetric' | 'architecture' | 'network';
  description: string;
  standardRef: string;
  duration: string;
  status: 'passed' | 'variance' | 'enforced';
  assertion: string;
}

export interface BenchmarkThroughput {
  bufferSize: string;
  bytes: number;
  wolfiFips: number; // in MB/s
  ubuntu: number;
  debian: number;
  alpine: number;
}

export interface SignatureBenchmark {
  algorithm: string;
  keySize: string;
  securityBits: number;
  signOpsPerSec: number;
  verifyOpsPerSec: number;
  fipsStatus: string;
}

export const FIPS_TEST_SUITES = [
  { id: 'all', name: 'All Verifications', count: 46 },
  { id: 'core', name: 'Core Policy & KAT Self-Tests', count: 6 },
  { id: 'hash', name: 'Cryptographic Hashing (SHA-2/3)', count: 6 },
  { id: 'symmetric', name: 'Symmetric Ciphers (AES / GCM)', count: 9 },
  { id: 'mac', name: 'MAC & Message Integrity', count: 6 },
  { id: 'asymmetric', name: 'Asymmetric & Post-Quantum (PQC)', count: 10 },
  { id: 'architecture', name: 'Architecture & Supply Chain', count: 5 },
  { id: 'network', name: 'TLS & Network Cipher Suites', count: 6 },
] as const;

export const FIPS_TEST_CASES: FipsTestCase[] = [
  // 1. Core Policy
  {
    id: 'core-01',
    name: 'test_fips_config_file_indicators',
    suite: 'Core Policy & KAT',
    suiteId: 'core',
    description: 'Verify fipsmodule.cnf contains correct install-version and status indicators',
    standardRef: 'FIPS 140-3 §9.1 (Module Config)',
    duration: '0.18s',
    status: 'passed',
    assertion: 'fipsmodule.cnf exists and contains activate = 1 and security-checks = 1'
  },
  {
    id: 'core-02',
    name: 'test_fips_provider_version_metadata',
    suite: 'Core Policy & KAT',
    suiteId: 'core',
    description: 'Verify OpenSSL FIPS provider module metadata reports validated version 3.1.2',
    standardRef: 'FIPS 140-3 CMVP #4282',
    duration: '0.22s',
    status: 'passed',
    assertion: 'openssl list -providers includes "OpenSSL FIPS Provider v3.1.2"'
  },
  {
    id: 'core-03',
    name: 'test_mandatory_fips_property',
    suite: 'Core Policy & KAT',
    suiteId: 'core',
    description: 'Ensure fips=yes is default cryptographic search property in openssl.cnf',
    standardRef: 'FIPS 140-3 Management Policy',
    duration: '0.19s',
    status: 'passed',
    assertion: 'EVP_default_properties_is_fips_enabled() returns TRUE'
  },
  {
    id: 'core-04',
    name: 'test_operational_state_stability',
    suite: 'Core Policy & KAT',
    suiteId: 'core',
    description: 'Confirm module state machine remains in operational state after multiple power cycles',
    standardRef: 'FIPS 140-3 §9.2 State Machine',
    duration: '0.21s',
    status: 'passed',
    assertion: 'OSSL_PROVIDER_available(fips) returns operational code 1'
  },
  {
    id: 'core-05',
    name: 'test_default_provider_isolation',
    suite: 'Core Policy & KAT',
    suiteId: 'core',
    description: 'Verify default unhardened provider is isolated or requires explicit override',
    standardRef: 'Zero-Trust Isolation Principle',
    duration: '0.20s',
    status: 'passed',
    assertion: 'Default provider algorithms do not leak into FIPS execution boundary'
  },
  {
    id: 'core-06',
    name: 'test_kat_self_tests_on_load',
    suite: 'Core Policy & KAT',
    suiteId: 'core',
    description: 'Execute Power-On Self-Tests (POST) and Known Answer Tests (KAT) for all cipher suites',
    standardRef: 'FIPS 140-3 §9.3 Power-On Tests',
    duration: '0.45s',
    status: 'passed',
    assertion: 'All AES, SHA, HMAC, and RSA KAT vectors pass integrity validation on load'
  },

  // 2. Hashing & Digests
  {
    id: 'hash-01',
    name: 'test_sha256_availability',
    suite: 'Cryptographic Hashing',
    suiteId: 'hash',
    description: 'Verify SHA-256 produces exact FIPS CAVP test vector digest',
    standardRef: 'NIST FIPS 180-4 (Secure Hash)',
    duration: '0.15s',
    status: 'passed',
    assertion: 'SHA-256("abc") matches ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
  },
  {
    id: 'hash-02',
    name: 'test_sha512_availability',
    suite: 'Cryptographic Hashing',
    suiteId: 'hash',
    description: 'Verify SHA-512 hardware-accelerated 64-bit hashing execution',
    standardRef: 'NIST FIPS 180-4',
    duration: '0.16s',
    status: 'passed',
    assertion: 'SHA-512 digest verified against official NIST test vector'
  },
  {
    id: 'hash-03',
    name: 'test_sha3_256_keccak_availability',
    suite: 'Cryptographic Hashing',
    suiteId: 'hash',
    description: 'Verify SHA3-256 Keccak permutation function in FIPS mode',
    standardRef: 'NIST FIPS 202 (SHA-3 Permutations)',
    duration: '0.18s',
    status: 'passed',
    assertion: 'SHA3-256 computes expected state without fallback'
  },
  {
    id: 'hash-04',
    name: 'test_sha3_512_availability',
    suite: 'Cryptographic Hashing',
    suiteId: 'hash',
    description: 'Verify SHA3-512 high-security sponge hash function',
    standardRef: 'NIST FIPS 202',
    duration: '0.17s',
    status: 'passed',
    assertion: 'SHA3-512 vector passes NIST CAVP digest verification'
  },
  {
    id: 'hash-05',
    name: 'test_md5_rejection_in_fips_mode',
    suite: 'Cryptographic Hashing',
    suiteId: 'hash',
    description: 'Strict enforcement: verify MD5 computation is explicitly blocked in FIPS mode',
    standardRef: 'NIST SP 800-131A Rev 2',
    duration: '0.19s',
    status: 'enforced',
    assertion: 'openssl md5 returns error:0308010C:digital envelope routines::unsupported'
  },
  {
    id: 'hash-06',
    name: 'test_sha1_signing_rejection_in_fips_mode',
    suite: 'Cryptographic Hashing',
    suiteId: 'hash',
    description: 'Verify SHA-1 is forbidden for digital signature generation under FIPS policy',
    standardRef: 'NIST Deprecation Guidelines',
    duration: '0.20s',
    status: 'enforced',
    assertion: 'RSA-SHA1 signature creation rejected with FIPS policy violation'
  },

  // 3. Symmetric Ciphers
  {
    id: 'sym-01',
    name: 'test_aes_128_gcm_encryption',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify AES-128-GCM authenticated encryption and tag verification',
    standardRef: 'NIST SP 800-38D (GCM Mode)',
    duration: '0.17s',
    status: 'passed',
    assertion: 'Ciphertext & 128-bit authentication tag match KAT vector'
  },
  {
    id: 'sym-02',
    name: 'test_aes_256_gcm_encryption',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify AES-256-GCM hardware-accelerated throughput and tag authentication',
    standardRef: 'NIST SP 800-38D (Top Secret Tier)',
    duration: '0.19s',
    status: 'passed',
    assertion: 'Bulk data encrypted and authenticated using AES-NI instructions'
  },
  {
    id: 'sym-03',
    name: 'test_aes_128_cbc_encryption',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify AES-128-CBC block cipher with PKCS#7 padding',
    standardRef: 'NIST SP 800-38A',
    duration: '0.16s',
    status: 'passed',
    assertion: 'AES-128-CBC correctly encodes and decodes block payload'
  },
  {
    id: 'sym-04',
    name: 'test_aes_256_cbc_encryption',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify AES-256-CBC with initial initialization vector (IV)',
    standardRef: 'NIST SP 800-38A',
    duration: '0.16s',
    status: 'passed',
    assertion: 'Roundtrip CBC encryption/decryption vector match'
  },
  {
    id: 'sym-05',
    name: 'test_aes_128_ctr_streaming',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify AES-128-CTR counter mode stream encryption',
    standardRef: 'NIST SP 800-38A',
    duration: '0.15s',
    status: 'passed',
    assertion: 'Counter mode keystream matches NIST standard test sample'
  },
  {
    id: 'sym-06',
    name: 'test_aes_256_ctr_streaming',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify AES-256-CTR counter mode stream encryption',
    standardRef: 'NIST SP 800-38A',
    duration: '0.16s',
    status: 'passed',
    assertion: '256-bit counter mode matches test reference'
  },
  {
    id: 'sym-07',
    name: 'test_tdes_encryption_disallowed',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Strict enforcement: verify Triple-DES (3DES) encryption is disabled in FIPS 140-3',
    standardRef: 'NIST SP 800-131A (3DES Disallow)',
    duration: '0.18s',
    status: 'enforced',
    assertion: 'openssl enc -des-ede3-cbc returns error:0308010C:disabled in FIPS mode'
  },
  {
    id: 'sym-08',
    name: 'test_rc4_execution_rejected',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify legacy RC4 / ARCFOUR cipher is rejected',
    standardRef: 'RFC 7465 Prohibiting RC4',
    duration: '0.17s',
    status: 'enforced',
    assertion: 'RC4 invocation yields algorithm disabled exception'
  },
  {
    id: 'sym-09',
    name: 'test_blowfish_cast5_rejected',
    suite: 'Symmetric Ciphers',
    suiteId: 'symmetric',
    description: 'Verify Blowfish and CAST5 unapproved ciphers are disabled',
    standardRef: 'FIPS 140-3 Approved Algorithm List',
    duration: '0.18s',
    status: 'enforced',
    assertion: 'Blowfish/CAST5 cannot be instantiated through EVP API'
  },

  // 4. MAC Integrity
  {
    id: 'mac-01',
    name: 'test_hmac_sha256_integrity',
    suite: 'MAC & Message Integrity',
    suiteId: 'mac',
    description: 'Verify HMAC-SHA256 keyed-hash message authentication code',
    standardRef: 'NIST FIPS 198-1',
    duration: '0.16s',
    status: 'passed',
    assertion: 'HMAC-SHA256 matches RFC 4231 test vectors'
  },
  {
    id: 'mac-02',
    name: 'test_hmac_sha512_integrity',
    suite: 'MAC & Message Integrity',
    suiteId: 'mac',
    description: 'Verify HMAC-SHA512 high-capacity message authentication code',
    standardRef: 'NIST FIPS 198-1',
    duration: '0.17s',
    status: 'passed',
    assertion: 'HMAC-SHA512 matches RFC 4231 test vectors'
  },
  {
    id: 'mac-03',
    name: 'test_kmac128_integrity',
    suite: 'MAC & Message Integrity',
    suiteId: 'mac',
    description: 'Verify KMAC-128 Keccak-based message authentication code',
    standardRef: 'NIST SP 800-185',
    duration: '0.18s',
    status: 'passed',
    assertion: 'KMAC128 computes correct MAC with custom string support'
  },
  {
    id: 'mac-04',
    name: 'test_kmac256_integrity',
    suite: 'MAC & Message Integrity',
    suiteId: 'mac',
    description: 'Verify KMAC-256 high-security Keccak message authentication code',
    standardRef: 'NIST SP 800-185',
    duration: '0.19s',
    status: 'passed',
    assertion: 'KMAC256 computes expected hash tag under NIST CAVP vector'
  },
  {
    id: 'mac-05',
    name: 'test_cmac_aes256_integrity',
    suite: 'MAC & Message Integrity',
    suiteId: 'mac',
    description: 'Verify CMAC-AES-256 cipher-based MAC authentication',
    standardRef: 'NIST SP 800-38B',
    duration: '0.18s',
    status: 'passed',
    assertion: 'CMAC subkey generation and tag calculation pass CAVP vector'
  },
  {
    id: 'mac-06',
    name: 'test_short_mac_key_rejected',
    suite: 'MAC & Message Integrity',
    suiteId: 'mac',
    description: 'Verify HMAC keys shorter than 112 bits are rejected in FIPS mode',
    standardRef: 'NIST SP 800-131A (Key Length Checks)',
    duration: '0.20s',
    status: 'enforced',
    assertion: 'HMAC key length < 14 bytes returns key length violation'
  },

  // 5. Asymmetric & PQC
  {
    id: 'asym-01',
    name: 'test_rsa_2048_keygen_and_sign',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify RSA 2048-bit keypair generation, signature, and verification',
    standardRef: 'NIST FIPS 186-5 (Digital Signature)',
    duration: '0.34s',
    status: 'passed',
    assertion: 'RSA-PSS and PKCS#1 v1.5 with SHA-256 passes verification'
  },
  {
    id: 'asym-02',
    name: 'test_rsa_3072_keygen_and_sign',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify RSA 3072-bit (128-bit security equivalent) keypair and signature',
    standardRef: 'NIST FIPS 186-5',
    duration: '0.48s',
    status: 'passed',
    assertion: 'RSA-3072 key generation and signature validation successful'
  },
  {
    id: 'asym-03',
    name: 'test_rsa_4096_keygen_and_sign',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify RSA 4096-bit high-assurance keypair and signature verification',
    standardRef: 'NIST FIPS 186-5',
    duration: '0.82s',
    status: 'passed',
    assertion: 'RSA-4096 signature verification succeeded'
  },
  {
    id: 'asym-04',
    name: 'test_rsa_small_key_rejected',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify RSA keys smaller than 2048-bit (e.g. 1024-bit) are rejected',
    standardRef: 'NIST SP 800-131A',
    duration: '0.22s',
    status: 'enforced',
    assertion: 'openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:1024 fails in FIPS mode'
  },
  {
    id: 'asym-05',
    name: 'test_ecdsa_p256_signing',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify ECDSA prime256v1 (NIST P-256) key generation and signature verification',
    standardRef: 'NIST FIPS 186-5 (ECDSA)',
    duration: '0.19s',
    status: 'passed',
    assertion: 'ECDSA P-256 signature verification successful'
  },
  {
    id: 'asym-06',
    name: 'test_ecdsa_p384_signing',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify ECDSA secp384r1 (NIST P-384) high-security curve signing',
    standardRef: 'NIST FIPS 186-5 (ECDSA)',
    duration: '0.22s',
    status: 'passed',
    assertion: 'ECDSA P-384 sign and verify cycle passes'
  },
  {
    id: 'asym-07',
    name: 'test_ecdsa_p521_signing',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify ECDSA secp521r1 maximum NIST curve execution',
    standardRef: 'NIST FIPS 186-5 (ECDSA)',
    duration: '0.28s',
    status: 'passed',
    assertion: 'ECDSA P-521 sign and verify passes'
  },
  {
    id: 'asym-08',
    name: 'test_ed25519_support',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Verify Ed25519 Edwards-curve digital signature algorithm',
    standardRef: 'NIST FIPS 186-5 (EdDSA)',
    duration: '0.18s',
    status: 'passed',
    assertion: 'Ed25519 sign and verify roundtrip confirmed'
  },
  {
    id: 'asym-09',
    name: 'test_ml_kem_768_pqc_kyber',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Post-Quantum readiness: verify ML-KEM (Kyber-768) key encapsulation mechanism',
    standardRef: 'NIST FIPS 203 (ML-KEM Standard)',
    duration: '0.31s',
    status: 'passed',
    assertion: 'ML-KEM-768 shared secret encapsulation/decapsulation successful'
  },
  {
    id: 'asym-10',
    name: 'test_ml_dsa_65_pqc_dilithium',
    suite: 'Asymmetric & Post-Quantum',
    suiteId: 'asymmetric',
    description: 'Post-Quantum readiness: verify ML-DSA (Dilithium-65) lattice digital signature',
    standardRef: 'NIST FIPS 204 (ML-DSA Standard)',
    duration: '0.35s',
    status: 'passed',
    assertion: 'ML-DSA-65 lattice key generation and signature verification passed'
  },

  // 6. Architecture & Supply Chain
  {
    id: 'arch-01',
    name: 'test_non_root_execution',
    suite: 'Architecture & Supply Chain',
    suiteId: 'architecture',
    description: 'Verify container runs as non-privileged nonroot user (UID 1000)',
    standardRef: 'CIS Docker Benchmark §4.1',
    duration: '0.15s',
    status: 'passed',
    assertion: 'id -u returns 1000 (nonroot) and not 0 (root)'
  },
  {
    id: 'arch-02',
    name: 'test_read_only_rootfs_compatibility',
    suite: 'Architecture & Supply Chain',
    suiteId: 'architecture',
    description: 'Verify container executes cleanly when mounted with read-only root filesystem',
    standardRef: 'Kubernetes PSS Restricted Profile',
    duration: '0.22s',
    status: 'passed',
    assertion: 'OpenSSL operations execute with --read-only rootfs without write errors'
  },
  {
    id: 'arch-03',
    name: 'test_baselayout_cleanliness',
    suite: 'Architecture & Supply Chain',
    suiteId: 'architecture',
    description: 'Verify no package manager (apk), shell, or build tools exist in distroless image',
    standardRef: 'Zero-Attack Surface Principle',
    duration: '0.19s',
    status: 'passed',
    assertion: 'Neither /bin/sh nor /sbin/apk exist in production distroless image'
  },
  {
    id: 'arch-04',
    name: 'test_cyclonedx_sbom_presence',
    suite: 'Architecture & Supply Chain',
    suiteId: 'architecture',
    description: 'Verify CycloneDX v1.5 Software Bill of Materials is attached and validated',
    standardRef: 'Executive Order 14028 §4',
    duration: '0.25s',
    status: 'passed',
    assertion: 'Valid signed CycloneDX SBOM attached in image metadata'
  },
  {
    id: 'arch-05',
    name: 'test_slsa_provenance_verification',
    suite: 'Architecture & Supply Chain',
    suiteId: 'architecture',
    description: 'Verify SLSA Level 3 cryptographically signed build provenance attestation',
    standardRef: 'SLSA Framework Level 3',
    duration: '0.28s',
    status: 'passed',
    assertion: 'GitHub Actions in-toto provenance attestation verified with cosign'
  },

  // 7. Network TLS
  {
    id: 'tls-01',
    name: 'test_tls13_aes_256_gcm_sha384',
    suite: 'Network TLS',
    suiteId: 'network',
    description: 'Verify TLS 1.3 handshake using TLS_AES_256_GCM_SHA384 cipher suite',
    standardRef: 'RFC 8446 §9.1',
    duration: '0.25s',
    status: 'passed',
    assertion: 'TLS 1.3 session established using AES-256-GCM and SHA-384 PRF'
  },
  {
    id: 'tls-02',
    name: 'test_tls13_aes_128_gcm_sha256',
    suite: 'Network TLS',
    suiteId: 'network',
    description: 'Verify TLS 1.3 handshake using TLS_AES_128_GCM_SHA256 cipher suite',
    standardRef: 'RFC 8446 §9.1',
    duration: '0.22s',
    status: 'passed',
    assertion: 'TLS 1.3 session established using AES-128-GCM and SHA-256 PRF'
  },
  {
    id: 'tls-03',
    name: 'test_tls13_chacha20_poly1305',
    suite: 'Network TLS',
    suiteId: 'network',
    description: 'Verify TLS 1.3 fallback behavior with CHACHA20-POLY1305 in FIPS configuration',
    standardRef: 'RFC 8446 & NIST Guidance',
    duration: '0.24s',
    status: 'passed',
    assertion: 'FIPS-approved suites prioritized; non-approved suites rejected during negotiation'
  },
  {
    id: 'tls-04',
    name: 'test_tls12_ecdhe_rsa_aes256_gcm',
    suite: 'Network TLS',
    suiteId: 'network',
    description: 'Verify TLS 1.2 backwards compatibility using ECDHE-RSA-AES256-GCM-SHA384',
    standardRef: 'NIST SP 800-52 Rev 2',
    duration: '0.28s',
    status: 'passed',
    assertion: 'TLS 1.2 handshake succeeds with ephemeral Diffie-Hellman key exchange'
  },
  {
    id: 'tls-05',
    name: 'test_tls10_and_tls11_disabled',
    suite: 'Network TLS',
    suiteId: 'network',
    description: 'Strict enforcement: verify legacy TLS 1.0 and TLS 1.1 protocol handshakes fail',
    standardRef: 'NIST SP 800-52 Rev 2 §3.1',
    duration: '0.23s',
    status: 'enforced',
    assertion: 'Client hello requesting TLS 1.0/1.1 rejected with protocol_version alert'
  },
  {
    id: 'tls-06',
    name: 'test_insecure_ciphers_rejected',
    suite: 'Network TLS',
    suiteId: 'network',
    description: 'Verify NULL, EXPORT, RC4, and 3DES cipher suites are blocked in TLS',
    standardRef: 'PCI-DSS v4.0 Requirement 4.1',
    duration: '0.24s',
    status: 'enforced',
    assertion: 'All unapproved cipher suites discarded during TLS ClientHello parsing'
  }
];

export const BENCHMARK_THROUGHPUT_DATA: BenchmarkThroughput[] = [
  { bufferSize: '16 B', bytes: 16, wolfiFips: 793.4, alpine: 680.1, ubuntu: 650.3, debian: 610.8 },
  { bufferSize: '64 B', bytes: 64, wolfiFips: 2090.1, alpine: 1820.5, ubuntu: 1780.2, debian: 1690.4 },
  { bufferSize: '256 B', bytes: 256, wolfiFips: 4209.1, alpine: 3640.2, ubuntu: 3510.4, debian: 3380.6 },
  { bufferSize: '1 KB', bytes: 1024, wolfiFips: 5608.3, alpine: 4890.1, ubuntu: 4720.6, debian: 4510.2 },
  { bufferSize: '8 KB', bytes: 8192, wolfiFips: 6260.0, alpine: 5180.4, ubuntu: 5040.8, debian: 4810.1 },
  { bufferSize: '16 KB', bytes: 16384, wolfiFips: 6471.9, alpine: 5230.1, ubuntu: 5120.4, debian: 4890.2 }
];

export const HASHING_THROUGHPUT_DATA = [
  { algorithm: 'SHA-256', wolfiFips: 1235.8, alpine: 980.2, ubuntu: 940.5, debian: 890.1 },
  { algorithm: 'SHA-512', wolfiFips: 1842.5, alpine: 1420.8, ubuntu: 1390.2, debian: 1310.5 },
  { algorithm: 'SHA3-256', wolfiFips: 428.1, alpine: 360.4, ubuntu: 345.1, debian: 320.6 },
  { algorithm: 'SHA3-512', wolfiFips: 242.3, alpine: 198.6, ubuntu: 190.2, debian: 182.4 }
];

export const SIGNATURE_BENCHMARK_DATA: SignatureBenchmark[] = [
  { algorithm: 'ECDSA P-256 (prime256v1)', keySize: '256 bit', securityBits: 128, signOpsPerSec: 48910.2, verifyOpsPerSec: 16840.5, fipsStatus: 'FIPS 140-3 Approved' },
  { algorithm: 'ECDSA P-384 (secp384r1)', keySize: '384 bit', securityBits: 192, signOpsPerSec: 7120.8, verifyOpsPerSec: 5430.2, fipsStatus: 'FIPS 140-3 Approved' },
  { algorithm: 'RSA-2048 (PKCS#1 v1.5)', keySize: '2048 bit', securityBits: 112, signOpsPerSec: 2410.5, verifyOpsPerSec: 94820.1, fipsStatus: 'FIPS 140-3 Approved' },
  { algorithm: 'RSA-3072 (PKCS#1 v1.5)', keySize: '3072 bit', securityBits: 128, signOpsPerSec: 680.2, verifyOpsPerSec: 42100.0, fipsStatus: 'FIPS 140-3 Approved' },
  { algorithm: 'RSA-4096 (PKCS#1 v1.5)', keySize: '4096 bit', securityBits: 140, signOpsPerSec: 312.4, verifyOpsPerSec: 24190.0, fipsStatus: 'FIPS 140-3 Approved' },
  { algorithm: 'Ed25519 (Edwards)', keySize: '256 bit', securityBits: 128, signOpsPerSec: 52140.0, verifyOpsPerSec: 21320.0, fipsStatus: 'FIPS 186-5 Approved' },
  { algorithm: 'ML-KEM-768 (Kyber)', keySize: 'Lattice', securityBits: 192, signOpsPerSec: 18450.0, verifyOpsPerSec: 18920.0, fipsStatus: 'FIPS 203 (PQC)' }
];
