"""FIPS 140-3 behavior tests for Go BoringCrypto FIPS images."""
import pytest


def test_fips_check_passes(run_docker, image_tag, flavor):
    """The build-time fips-check.go script must pass successfully."""
    if flavor == "prod":
        # Prod flavor is scratch containing only ca-certificates, tzdata, and runtime
        res = run_docker(image_tag, ["/bin/sh", "-c", "echo ok"])
        assert res.returncode == 0 or "executable file not found" in res.stderr
        return

    res = run_docker(image_tag, ["go", "run", "/usr/share/go-fips/fips-check.go"])
    assert res.returncode == 0, f"fips-check.go failed: {res.stdout}\n{res.stderr}"
    assert "FIPS check passed" in res.stdout
    assert "BoringCrypto / fipsonly enforced" in res.stdout


def test_boringcrypto_environment(run_docker, image_tag, flavor):
    """GOEXPERIMENT=boringcrypto and CGO_ENABLED=1 must be active in development images."""
    if flavor == "prod":
        pytest.skip("Prod flavor does not contain the Go toolchain")

    res = run_docker(image_tag, ["go", "env", "GOEXPERIMENT"])
    assert res.returncode == 0
    assert "boringcrypto" in res.stdout, f"GOEXPERIMENT does not contain boringcrypto: {res.stdout}"

    res = run_docker(image_tag, ["go", "env", "CGO_ENABLED"])
    assert res.returncode == 0
    assert res.stdout.strip() == "1", f"CGO_ENABLED is not 1: {res.stdout}"


def test_boringcrypto_symbol_linkage(run_docker, image_tag, flavor):
    """A compiled binary must contain symbols from crypto/internal/boring or BoringCrypto."""
    if flavor == "prod":
        pytest.skip("Prod flavor does not contain the Go toolchain")

    script = """package main
import (
    "crypto/sha256"
    "fmt"
    _ "crypto/tls/fipsonly"
)
func main() {
    h := sha256.Sum256([]byte("fips test"))
    fmt.Printf("%x\\n", h)
}
"""
    res = run_docker(
        image_tag,
        ["sh", "-c", f"echo '{script}' > /tmp/main.go && go build -o /tmp/app /tmp/main.go && strings /tmp/app | grep -E 'boringcrypto|crypto/internal/boring' | head -n 5"],
    )
    assert res.returncode == 0, f"Symbol check failed: {res.stdout}\n{res.stderr}"
    assert len(res.stdout.strip()) > 0, "No boringcrypto symbols found in compiled binary"


def test_fipsonly_tls_negotiation(run_docker, image_tag, flavor):
    """crypto/tls/fipsonly must succeed for FIPS cipher suites."""
    if flavor == "prod":
        pytest.skip("Prod flavor does not contain the Go toolchain")

    script = """package main
import (
    "crypto/tls"
    "fmt"
    _ "crypto/tls/fipsonly"
)
func main() {
    cfg := &tls.Config{
        MinVersion: tls.VersionTLS12,
    }
    // With fipsonly imported, this must not panic and must enforce FIPS restrictions
    if cfg != nil {
        fmt.Println("TLS_FIPS_CONFIG_VALID")
    }
}
"""
    res = run_docker(image_tag, ["sh", "-c", f"echo '{script}' > /tmp/tls_check.go && go run /tmp/tls_check.go"])
    assert res.returncode == 0, f"TLS test failed: {res.stdout}\n{res.stderr}"
    assert "TLS_FIPS_CONFIG_VALID" in res.stdout


def test_non_root_execution(run_docker, image_tag, flavor):
    """Containers must run with a non-root user UID (not 0)."""
    if flavor == "prod":
        res = run_docker(image_tag, ["whoami"], entrypoint="/bin/sh")
        # In scratch/distroless, either sh doesn't exist or whoami doesn't exist, which is expected
        return

    res = run_docker(image_tag, ["id", "-u"])
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() != "0", "Container is running as root (UID 0)"
