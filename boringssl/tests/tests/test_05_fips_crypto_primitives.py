import pytest


class TestFIPSCryptoPrimitives:
    """Validates low-level cryptographic boundaries, Known Answer Tests (KAT), and module APIs via libcrypto."""

    def test_fips_mode_active(self, fips_runner):
        """FIPS_mode() must return 1 in the validated BoringCrypto module."""
        res = fips_runner("fips_mode")
        assert res.returncode == 0, f"fips_mode failed: {res.stderr}"
        assert res.stdout.strip() == "1"

    def test_fips_mode_cannot_be_disabled(self, fips_runner):
        """FIPS_mode_set(0) must be rejected, and FIPS mode must remain strictly active."""
        res = fips_runner("fips_mode_set_zero")
        assert res.returncode == 0, f"fips_mode_set_zero failed: {res.stderr}"
        assert "BLOCKED" in res.stdout

    def test_fips_self_test(self, fips_runner):
        """BORINGSSL_self_test() must succeed and return 1."""
        res = fips_runner("self_test")
        assert res.returncode == 0, f"self_test failed: {res.stderr}"
        assert res.stdout.strip() == "1"

    def test_fips_self_test_all(self, fips_runner):
        """BORINGSSL_self_test_all() must execute all algorithm KAT self-tests and return 1."""
        res = fips_runner("self_test_all")
        assert res.returncode == 0, f"self_test_all failed: {res.stderr}"
        assert res.stdout.strip() == "1"

    def test_fips_module_name(self, fips_runner):
        """FIPS_module_name() must identify the module as 'BoringCrypto'."""
        res = fips_runner("module_name")
        assert res.returncode == 0, f"module_name failed: {res.stderr}"
        assert res.stdout.strip() == "BoringCrypto"

    def test_fips_module_hash_present(self, fips_runner):
        """FIPS_module_hash() must return the 32-byte integrity hash injected into the module boundary."""
        res = fips_runner("module_hash")
        assert res.returncode == 0, f"module_hash failed: {res.stderr}"
        hash_hex = res.stdout.strip()
        assert len(hash_hex) == 64, f"Expected 64-char hex hash, got: '{hash_hex}'"
        assert hash_hex != "0" * 64, "Integrity hash is all zeros"

    def test_fips_query_aes_gcm_status(self, fips_runner):
        """FIPS_query_algorithm_status('AES-GCM') must return 1 (FIPS approved)."""
        res = fips_runner("query_aes_gcm")
        assert res.returncode == 0
        assert res.stdout.strip() == "1"

    def test_aes_128_gcm_kat(self, fips_runner):
        """AES-128-GCM AEAD encryption and decryption round-trip must succeed."""
        res = fips_runner("aes_128_gcm")
        assert res.returncode == 0, f"aes_128_gcm failed: {res.stderr}"
        assert "OK" in res.stdout

    def test_aes_256_gcm_kat(self, fips_runner):
        """AES-256-GCM AEAD encryption and decryption round-trip must succeed."""
        res = fips_runner("aes_256_gcm")
        assert res.returncode == 0, f"aes_256_gcm failed: {res.stderr}"
        assert "OK" in res.stdout

    def test_aes_gcm_tag_tamper_rejected(self, fips_runner):
        """Tampering with AES-GCM ciphertext authentication tag must cause decryption rejection."""
        res = fips_runner("aes_gcm_tamper")
        assert res.returncode == 0, f"aes_gcm_tamper failed: {res.stderr}"
        assert "REJECTED" in res.stdout

    def test_hmac_sha256_kat(self, fips_runner):
        """HMAC-SHA256 must match RFC 4231 known answer test vector."""
        res = fips_runner("hmac_sha256")
        assert res.returncode == 0, f"hmac_sha256 failed: {res.stderr}"
        assert "OK" in res.stdout

    def test_hmac_sha512_kat(self, fips_runner):
        """HMAC-SHA512 must match RFC 4231 known answer test vector."""
        res = fips_runner("hmac_sha512")
        assert res.returncode == 0, f"hmac_sha512 failed: {res.stderr}"
        assert "OK" in res.stdout
