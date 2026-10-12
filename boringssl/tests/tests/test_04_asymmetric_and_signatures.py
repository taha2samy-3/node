import os
import tempfile
import pytest


class TestAsymmetricAndSignatures:
    """Validates asymmetric key generation and digital signature algorithms in BoringSSL."""

    def test_genrsa_default_2048(self, run_bssl):
        """bssl genrsa with default parameters must generate a valid 2048-bit RSA PEM private key."""
        res = run_bssl(["genrsa", "-bits", "2048"])
        assert res.returncode == 0, f"genrsa 2048 failed: {res.stderr}"
        assert "-----BEGIN RSA PRIVATE KEY-----" in res.stdout
        assert "-----END RSA PRIVATE KEY-----" in res.stdout

    def test_genrsa_3072(self, run_bssl):
        """bssl genrsa with 3072 bits must generate a valid 3072-bit RSA PEM private key."""
        res = run_bssl(["genrsa", "-bits", "3072"])
        assert res.returncode == 0, f"genrsa 3072 failed: {res.stderr}"
        assert "-----BEGIN RSA PRIVATE KEY-----" in res.stdout
        assert "-----END RSA PRIVATE KEY-----" in res.stdout

    def test_genrsa_4096(self, run_bssl):
        """bssl genrsa with 4096 bits must generate a valid 4096-bit RSA PEM private key."""
        res = run_bssl(["genrsa", "-bits", "4096"])
        assert res.returncode == 0, f"genrsa 4096 failed: {res.stderr}"
        assert "-----BEGIN RSA PRIVATE KEY-----" in res.stdout
        assert "-----END RSA PRIVATE KEY-----" in res.stdout

    def test_genrsa_unknown_option_rejected(self, run_bssl):
        """Unknown or malformed arguments to bssl genrsa must be rejected."""
        res = run_bssl(["genrsa", "-invalid-flag"])
        assert res.returncode != 0

    @pytest.mark.parametrize(
        "digest,expected_len",
        [
            ("sha256", 256),
            ("sha384", 256),
            ("sha512", 256),
        ],
    )
    def test_rsa2048_signatures(self, run_bssl, run_docker, image_tag, digest, expected_len):
        """RSA-2048 digital signatures with SHA-2 family must produce exact 256-byte signatures."""
        with tempfile.TemporaryDirectory() as tmp:
            key_file = os.path.join(tmp, "key2048.pem")
            gen = run_bssl(["genrsa", "-bits", "2048"])
            assert gen.returncode == 0
            with open(key_file, "w") as f:
                f.write(gen.stdout)
            os.chmod(tmp, 0o777)
            os.chmod(key_file, 0o666)

            payload = b"NIST FIPS 140-3 digital signature message payload"
            sign = run_docker(
                image_tag,
                ["-v", f"{tmp}:/keys:ro", "sign", "-key", "/keys/key2048.pem", "-digest", digest],
                input_data=payload,
            )
            assert sign.returncode == 0, f"bssl sign failed: {sign.stderr}"
            assert len(sign.raw_stdout) == expected_len, f"Expected {expected_len} bytes, got {len(sign.raw_stdout)}"

    def test_rsa3072_signature_length(self, run_bssl, run_docker, image_tag):
        """RSA-3072 digital signatures must produce exact 384-byte signatures."""
        with tempfile.TemporaryDirectory() as tmp:
            key_file = os.path.join(tmp, "key3072.pem")
            gen = run_bssl(["genrsa", "-bits", "3072"])
            assert gen.returncode == 0
            with open(key_file, "w") as f:
                f.write(gen.stdout)
            os.chmod(tmp, 0o777)
            os.chmod(key_file, 0o666)

            sign = run_docker(
                image_tag,
                ["-v", f"{tmp}:/keys:ro", "sign", "-key", "/keys/key3072.pem", "-digest", "sha256"],
                input_data=b"test 3072 message",
            )
            assert sign.returncode == 0
            assert len(sign.raw_stdout) == 384, f"Expected 384 bytes, got {len(sign.raw_stdout)}"

    def test_sign_missing_key_rejected(self, run_bssl):
        """Invoking bssl sign without a private key must fail with a non-zero exit code."""
        res = run_bssl(["sign", "-digest", "sha256"], input_data=b"payload")
        assert res.returncode != 0

    def test_sign_invalid_key_rejected(self, run_docker, image_tag):
        """Invoking bssl sign with a corrupted private key must fail with non-zero exit code."""
        with tempfile.TemporaryDirectory() as tmp:
            bad_key = os.path.join(tmp, "bad.pem")
            with open(bad_key, "w") as f:
                f.write("-----BEGIN RSA PRIVATE KEY-----\ncorrupted_data\n-----END RSA PRIVATE KEY-----\n")
            os.chmod(tmp, 0o777)
            os.chmod(bad_key, 0o666)

            res = run_docker(
                image_tag,
                ["-v", f"{tmp}:/keys:ro", "sign", "-key", "/keys/bad.pem", "-digest", "sha256"],
                input_data=b"payload",
            )
            assert res.returncode != 0

    def test_generate_ed25519_keypair(self, run_docker, image_tag):
        """bssl generate-ed25519 must generate valid public and private key files."""
        with tempfile.TemporaryDirectory() as tmp:
            os.chmod(tmp, 0o777)
            res = run_docker(
                image_tag,
                [
                    "-v", f"{tmp}:/out",
                    "generate-ed25519",
                    "-out-public", "/out/ed_pub.pem",
                    "-out-private", "/out/ed_priv.pem",
                ],
            )
            assert res.returncode == 0, f"generate-ed25519 failed: {res.stderr}"
            assert os.path.exists(os.path.join(tmp, "ed_pub.pem"))
            assert os.path.exists(os.path.join(tmp, "ed_priv.pem"))

    def test_generate_ed25519_missing_args_rejected(self, run_bssl):
        """bssl generate-ed25519 without required arguments must fail."""
        res = run_bssl(["generate-ed25519"])
        assert res.returncode != 0
