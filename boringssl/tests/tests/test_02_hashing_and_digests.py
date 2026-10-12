import hashlib
import pytest


class TestDigests:
    """Validates hashing functionality and test vectors in BoringSSL."""

    @pytest.mark.parametrize("payload", [b"", b"abc", b"The quick brown fox jumps over the lazy dog"])
    def test_sha256_known_answer(self, run_docker, image_tag, payload):
        """Verifies SHA-256 against standard NIST test vectors."""
        expected = hashlib.sha256(payload).hexdigest()
        res = run_docker(image_tag, ["sha256sum"], input_data=payload)
        assert res.returncode == 0, f"sha256sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"

    @pytest.mark.parametrize("payload", [b"hello fips", b"crypto boundary verification payload"])
    def test_sha1_digest(self, run_docker, image_tag, payload):
        """Verifies SHA-1 digest calculation."""
        expected = hashlib.sha1(payload).hexdigest()
        res = run_docker(image_tag, ["sha1sum"], input_data=payload)
        assert res.returncode == 0, f"sha1sum failed: {res.stderr}"
        assert expected in res.stdout, f"Expected {expected} in {res.stdout}"
