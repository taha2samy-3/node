import pytest


class TestCorePolicyAndIntegrity:
    """Validates the operational health, FIPS indicators, and execution boundaries of BoringSSL."""

    def test_isfips_active(self, run_bssl):
        """bssl isfips must return exit code 0 and output 1, indicating FIPS mode and successful POST."""
        res = run_bssl(["isfips"])
        assert res.returncode == 0, f"bssl isfips failed: {res.stderr}"
        assert res.stdout.strip() == "1", f"bssl isfips output was not 1: '{res.stdout}'"

    def test_isfips_deterministic(self, run_bssl):
        """Repeated invocations of bssl isfips must reliably return 1 without deviation."""
        for i in range(3):
            res = run_bssl(["isfips"])
            assert res.returncode == 0, f"Iteration {i} failed: {res.stderr}"
            assert res.stdout.strip() == "1", f"Iteration {i} output was not 1: '{res.stdout}'"

    def test_power_on_self_test_integrity(self, run_bssl):
        """Running basic cryptographic operations must execute without POST / integrity failure."""
        res = run_bssl(["sha256sum"], input_data=b"fips 140-3 power on self test verification")
        assert res.returncode == 0, f"bssl sha256sum failed: {res.stderr}"
        assert len(res.stdout.strip()) >= 64, f"Unexpected sha256sum output: {res.stdout}"

    def test_bssl_binary_execution(self, run_bssl):
        """Invoking bssl without subcommands must print usage with available cryptographic commands."""
        res = run_bssl([])
        # bssl exits with 1 when no command is provided, but prints usage
        assert "Available commands:" in res.stdout or "Usage:" in res.stdout
        assert "isfips" in res.stdout
        assert "sha256sum" in res.stdout
        assert "ciphers" in res.stdout

    def test_non_root_user(self, run_docker, image_tag):
        """The container must execute as a non-root user (UID != 0)."""
        res = run_docker(image_tag, ["id", "-u"], entrypoint="/usr/bin/id")
        if res.returncode != 0:
            res = run_docker(image_tag, ["-c", "id -u"], entrypoint="/bin/sh")
        if res.returncode == 0:
            assert res.stdout.strip() != "0", "Container is running as root (UID 0)"

    def test_distroless_no_shell(self, run_docker, image_tag):
        """In distroless production images, interactive shells must not be present."""
        if "distroless" not in image_tag:
            pytest.skip("Shell check is only applicable to distroless flavor")
        res = run_docker(image_tag, ["-c", "echo shell_present"], entrypoint="/bin/sh")
        assert res.returncode != 0 or "shell_present" not in res.stdout, "Distroless container contains /bin/sh"

    def test_distroless_no_package_manager(self, run_docker, image_tag):
        """In distroless production images, package managers (apk) must not be present."""
        if "distroless" not in image_tag:
            pytest.skip("Package manager check is only applicable to distroless flavor")
        res = run_docker(image_tag, ["--version"], entrypoint="/sbin/apk")
        assert res.returncode != 0, "Distroless container contains /sbin/apk package manager"
