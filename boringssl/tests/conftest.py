import logging
import os
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
import pytest

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

RUN_TIMEOUT = 60
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class CleanResult:
    returncode: int
    stdout: str
    stderr: str
    raw_stdout: bytes = b""
    raw_stderr: bytes = b""


def pytest_addoption(parser):
    parser.addoption("--image", action="store", required=True, help="Docker image tag to verify")


@pytest.fixture(scope="session")
def image_tag(request):
    return request.config.getoption("--image")


@pytest.fixture(scope="session")
def run_docker():
    def _executor(image: str, args: list, input_data: bytes = None, entrypoint: str = None):
        docker_options = []
        container_cmd = []
        if entrypoint is None:
            entrypoint = "/usr/local/bin/bssl"

        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-v" and i + 1 < len(args):
                docker_options.extend(["-v", args[i + 1]])
                i += 2
            elif arg == "--entrypoint" and i + 1 < len(args):
                entrypoint = args[i + 1]
                i += 2
            else:
                container_cmd.append(arg)
                i += 1
        label = f"bssl-fips-test={uuid.uuid4().hex}"
        cmd = ["docker", "run"]
        if input_data is not None:
            cmd.append("-i")
        cmd += ["--rm", "--entrypoint", entrypoint, "--label", label] + docker_options + [image] + container_cmd

        logger.info(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                capture_output=True,
                text=False,
                check=False,
                timeout=RUN_TIMEOUT,
            )
            stdout_decoded = result.stdout.decode("utf-8", errors="ignore")
            stderr_decoded = result.stderr.decode("utf-8", errors="ignore")

            return CleanResult(
                result.returncode,
                stdout_decoded,
                stderr_decoded,
                raw_stdout=result.stdout,
                raw_stderr=result.stderr,
            )
        except subprocess.TimeoutExpired:
            stuck = subprocess.run(["docker", "ps", "-q", "--filter", f"label={label}"], capture_output=True, text=True).stdout.split()
            if stuck:
                subprocess.run(["docker", "rm", "-f", *stuck], capture_output=True)
            pytest.fail(f"Container did not finish within {RUN_TIMEOUT}s: {' '.join(cmd)}")
        except Exception as e:
            pytest.fail(f"Local Docker execution failed: {str(e)}")

    return _executor


@pytest.fixture(scope="session")
def run_bssl(run_docker, image_tag):
    def _bssl(args: list, input_data: bytes = None):
        return run_docker(image_tag, args, input_data=input_data)
    return _bssl


@pytest.fixture(scope="session")
def fips_runner(run_docker, image_tag):
    """Session fixture that ensures bssl_fips_test_runner is compiled and provides an execution helper."""
    bin_dir = os.path.join(TESTS_DIR, "bin")
    runner_path = os.path.join(bin_dir, "runner")
    c_source = os.path.join(TESTS_DIR, "bssl_fips_test_runner.c")

    if not os.path.exists(runner_path):
        os.makedirs(bin_dir, exist_ok=True)
        os.chmod(bin_dir, 0o777)

        # Find dev image for compilation
        dev_candidates = [
            image_tag if "dev" in image_tag else None,
            "ghcr.io/taha2samy-3/boringssl-fips:fips-2024-dev",
            "ghcr.io/taha2samy-3/boringssl-fips:dev",
        ]
        dev_img = next((img for img in dev_candidates if img and subprocess.run(["docker", "image", "inspect", img], capture_output=True).returncode == 0), None)

        if not dev_img:
            pytest.skip("BoringSSL dev image is not available to compile C test runner")

        compile_cmd = [
            "docker", "run", "--rm",
            "-v", f"{TESTS_DIR}:/tests",
            "--entrypoint", "gcc",
            dev_img,
            "-Wall", "-Wextra", "-O2", "/tests/bssl_fips_test_runner.c", "-lcrypto", "-o", "/tests/bin/runner"
        ]
        proc = subprocess.run(compile_cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            pytest.fail(f"Failed to compile bssl_fips_test_runner: {proc.stderr}")

    def _execute(subcommand: str):
        return run_docker(
            image_tag,
            ["-v", f"{bin_dir}:/bin_test:ro", subcommand],
            entrypoint="/bin_test/runner"
        )

    return _execute
