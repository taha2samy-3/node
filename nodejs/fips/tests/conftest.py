import os
import subprocess
from dataclasses import dataclass

import pytest

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def pytest_addoption(parser):
    parser.addoption("--image", required=True, help="Node.js FIPS image to test")
    parser.addoption("--flavor", required=True, choices=["dev", "standard", "prod"], help="Image flavor")


@dataclass
class Result:
    returncode: int
    stdout: str
    stderr: str


@pytest.fixture(scope="session")
def image(request):
    return request.config.getoption("--image")


@pytest.fixture(scope="session")
def flavor(request):
    return request.config.getoption("--flavor")


@pytest.fixture(scope="session")
def node(image):
    """Run a script with the image's node binary (works for every flavor, including distroless)."""
    def run(script: str, mount_fixtures: bool = False) -> Result:
        cmd = ["docker", "run", "--rm"]
        if mount_fixtures:
            cmd += ["-v", f"{FIXTURES}:/fixtures:ro"]
        cmd += ["--entrypoint", "/usr/bin/node", image, "-e", script]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return Result(proc.returncode, proc.stdout.strip(), proc.stderr.strip())
    return run
