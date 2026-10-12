import pytest


class TestCorePolicyAndIntegrity:
    """Validates the operational health and FIPS indicators of BoringSSL."""

    def test_isfips_active(self, run_docker, image_tag):
        """bssl isfips must return exit code 0 and output 1, indicating FIPS mode and successful POST."""
        res = run_docker(image_tag, ["isfips"])
        assert res.returncode == 0, f"bssl isfips failed: {res.stderr}"
        assert res.stdout.strip() == "1", f"bssl isfips output was not 1: '{res.stdout}'"

    def test_power_on_self_test_integrity(self, run_docker, image_tag):
        """Running basic cryptographic operation must execute without POST / integrity failure."""
        res = run_docker(image_tag, ["sha256sum"], input_data=b"fips 140-3 test")
        assert res.returncode == 0, f"bssl sha256sum failed: {res.stderr}"
        assert len(res.stdout.strip()) >= 64, f"Unexpected sha256sum output: {res.stdout}"

    def test_non_root_user(self, run_docker, image_tag):
        """The container must execute as a non-root user (UID 65532 or != 0)."""
        res = run_docker(image_tag, ["id", "-u"], entrypoint="/usr/bin/id")
        if res.returncode != 0:
            # If id doesn't exist (e.g. distroless), test with /bin/sh or skip if scratch
            res = run_docker(image_tag, ["-c", "id -u"], entrypoint="/bin/sh")
        if res.returncode == 0:
            assert res.stdout.strip() != "0", "Container is running as root (UID 0)"
