import pytest


class TestSymmetricAndDRBG:
    """Validates SP 800-90A DRBG random number generation and TLS cipher suite security boundaries."""

    def test_drbg_random_generation_default(self, run_bssl):
        """bssl rand 32 must output exactly 32 bytes of high-entropy cryptographic random data."""
        res = run_bssl(["rand", "32"])
        assert res.returncode == 0, f"bssl rand failed: {res.stderr}"
        assert len(res.raw_stdout) == 32, f"Expected 32 bytes, got {len(res.raw_stdout)}"

    def test_drbg_random_generation_hex(self, run_bssl):
        """bssl rand -hex 16 must output 32 hex characters representing 16 random bytes."""
        res = run_bssl(["rand", "-hex", "16"])
        assert res.returncode == 0, f"bssl rand -hex failed: {res.stderr}"
        hex_data = res.stdout.strip()
        assert len(hex_data) == 32, f"Expected 32 hex chars, got {len(hex_data)}"
        int(hex_data, 16)  # Verify valid hexadecimal

    @pytest.mark.parametrize("num_bytes", [16, 24, 32, 48, 64, 128])
    def test_drbg_random_sizes(self, run_bssl, num_bytes):
        """bssl rand -hex <N> must output exactly 2*N hex characters for each requested size."""
        res = run_bssl(["rand", "-hex", str(num_bytes)])
        assert res.returncode == 0
        assert len(res.stdout.strip()) == num_bytes * 2

    def test_drbg_entropy_uniqueness(self, run_bssl):
        """Two consecutive DRBG generations must produce distinct values (no RNG freeze or repeats)."""
        res1 = run_bssl(["rand", "-hex", "32"])
        res2 = run_bssl(["rand", "-hex", "32"])
        assert res1.returncode == 0 and res2.returncode == 0
        assert res1.stdout.strip() != res2.stdout.strip(), "DRBG produced repeating random outputs"

    def test_drbg_invalid_args_rejected(self, run_bssl):
        """Invalid or negative length arguments to bssl rand must be rejected with non-zero exit code."""
        res = run_bssl(["rand", "-5"])
        assert res.returncode != 0

    def test_ciphers_command_success(self, run_bssl):
        """bssl ciphers ALL must succeed and output active cipher suites."""
        res = run_bssl(["ciphers", "ALL"])
        assert res.returncode == 0, f"bssl ciphers ALL failed: {res.stderr}"
        assert "TLS_" in res.stdout

    def test_ciphers_approved_aes_128_gcm(self, run_bssl):
        """FIPS-approved AES-128-GCM cipher suite must be available in TLS cipher configuration."""
        res = run_bssl(["ciphers", "ALL"])
        assert res.returncode == 0
        assert "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256" in res.stdout

    def test_ciphers_approved_aes_256_gcm(self, run_bssl):
        """FIPS-approved AES-256-GCM cipher suite must be available in TLS cipher configuration."""
        res = run_bssl(["ciphers", "ALL"])
        assert res.returncode == 0
        assert "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384" in res.stdout

    def test_ciphers_approved_aes_cbc(self, run_bssl):
        """FIPS-approved AES-CBC cipher suites must be available in TLS cipher configuration."""
        res = run_bssl(["ciphers", "ALL"])
        assert res.returncode == 0
        assert "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA" in res.stdout
        assert "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA" in res.stdout

    @pytest.mark.parametrize(
        "insecure_cipher",
        [
            "RC4",
            "DES",
            "NULL",
            "EXPORT",
            "MD5",
            "aNULL",
            "eNULL",
            "LOW",
        ],
    )
    def test_insecure_ciphers_rejected(self, run_bssl, insecure_cipher):
        """Obsolete and insecure ciphers must be strictly rejected by the cipher parser."""
        res = run_bssl(["ciphers", insecure_cipher])
        assert res.returncode != 0, f"Insecure cipher '{insecure_cipher}' was unexpectedly accepted"
