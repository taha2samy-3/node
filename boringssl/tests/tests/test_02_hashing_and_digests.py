import hashlib
import pytest


class TestDigests:
    """Validates FIPS-approved hashing algorithms and known answer test (KAT) vectors in BoringSSL."""

    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"abc",
            b"The quick brown fox jumps over the lazy dog",
            b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
            b"A" * 1000,
        ],
    )
    def test_sha256_known_answer(self, run_bssl, payload):
        """Verifies SHA-256 against standard NIST test vectors."""
        expected = hashlib.sha256(payload).hexdigest()
        res = run_bssl(["sha256sum"], input_data=payload)
        assert res.returncode == 0, f"bssl sha256sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"abc",
            b"The quick brown fox jumps over the lazy dog",
            b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
        ],
    )
    def test_sha224_known_answer(self, run_bssl, payload):
        """Verifies SHA-224 against standard NIST test vectors."""
        expected = hashlib.sha224(payload).hexdigest()
        res = run_bssl(["sha224sum"], input_data=payload)
        assert res.returncode == 0, f"bssl sha224sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"abc",
            b"The quick brown fox jumps over the lazy dog",
            b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
        ],
    )
    def test_sha384_known_answer(self, run_bssl, payload):
        """Verifies SHA-384 against standard NIST test vectors."""
        expected = hashlib.sha384(payload).hexdigest()
        res = run_bssl(["sha384sum"], input_data=payload)
        assert res.returncode == 0, f"bssl sha384sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"abc",
            b"The quick brown fox jumps over the lazy dog",
            b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq",
        ],
    )
    def test_sha512_known_answer(self, run_bssl, payload):
        """Verifies SHA-512 against standard NIST test vectors."""
        expected = hashlib.sha512(payload).hexdigest()
        res = run_bssl(["sha512sum"], input_data=payload)
        assert res.returncode == 0, f"bssl sha512sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"abc",
            b"The quick brown fox jumps over the lazy dog",
        ],
    )
    def test_sha512_256_known_answer(self, run_bssl, payload):
        """Verifies truncated SHA-512/256 against NIST test vectors."""
        expected = hashlib.new("sha512_256", payload).hexdigest()
        res = run_bssl(["sha512256sum"], input_data=payload)
        assert res.returncode == 0, f"bssl sha512256sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    @pytest.mark.parametrize(
        "payload",
        [
            b"hello fips",
            b"crypto boundary verification payload",
            b"abc",
        ],
    )
    def test_sha1_digest(self, run_bssl, payload):
        """Verifies SHA-1 digest calculation."""
        expected = hashlib.sha1(payload).hexdigest()
        res = run_bssl(["sha1sum"], input_data=payload)
        assert res.returncode == 0, f"bssl sha1sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    @pytest.mark.parametrize(
        "payload",
        [
            b"",
            b"abc",
            b"message digest",
        ],
    )
    def test_md5_digest(self, run_bssl, payload):
        """Verifies MD5 digest calculation."""
        expected = hashlib.md5(payload).hexdigest()
        res = run_bssl(["md5sum"], input_data=payload)
        assert res.returncode == 0, f"bssl md5sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    def test_digest_streaming_empty_input(self, run_bssl):
        """Streaming exactly 0 bytes into sha256sum must produce empty-input SHA-256 digest."""
        empty_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        res = run_bssl(["sha256sum"], input_data=b"")
        assert res.returncode == 0
        assert empty_sha256 in res.stdout

    def test_digest_block_boundary(self, run_bssl):
        """Inputs of exact SHA-256 block size (64 bytes) and block+1 (65 bytes) must hash correctly."""
        for length in (63, 64, 65):
            payload = b"B" * length
            expected = hashlib.sha256(payload).hexdigest()
            res = run_bssl(["sha256sum"], input_data=payload)
            assert res.returncode == 0
            assert expected in res.stdout

    def test_digest_large_payload(self, run_bssl):
        """Hashing a multi-megabyte payload must execute correctly without buffer overflow."""
        payload = b"FIPS_140_3_DATA_" * 65536  # ~1MB
        expected = hashlib.sha256(payload).hexdigest()
        res = run_bssl(["sha256sum"], input_data=payload)
        assert res.returncode == 0
        assert expected in res.stdout
