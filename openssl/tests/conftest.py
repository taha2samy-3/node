import pytest
import subprocess
import shutil
import logging
import uuid
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# A container that has not finished by then is removed and the test fails instead of hanging
RUN_TIMEOUT = 60

@dataclass
class CleanResult:
    returncode: int
    stdout: str
    stderr: str

def pytest_addoption(parser):
    parser.addoption("--image", action="store", required=True, help="Docker image tag to verify")

@pytest.fixture(scope="session")
def image_tag(request):
    return request.config.getoption("--image")

@pytest.fixture(scope="session")
def run_docker():
    def _executor(image: str, args: list):
        docker_options = []  
        container_cmd = []  
        
        i = 0
        while i < len(args):
            arg = args[i]
            if arg == "-v" and i + 1 < len(args):
                docker_options.extend(["-v", args[i+1]])
                i += 2
            else:
                container_cmd.append(arg)
                i += 1
        label = f"fips-test={uuid.uuid4().hex}"
        cmd = ["docker", "run", "--user", "0", "--rm", "--label", label] + docker_options + [image] + container_cmd
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=False,
                check=False,
                timeout=RUN_TIMEOUT,
            )
            stdout_decoded = result.stdout.decode('utf-8', errors='ignore')
            stderr_decoded = result.stderr.decode('utf-8', errors='ignore')
            
            return CleanResult(result.returncode, stdout_decoded, stderr_decoded)
        except subprocess.TimeoutExpired:
            stuck = subprocess.run(["docker", "ps", "-q", "--filter", f"label={label}"], capture_output=True, text=True).stdout.split()
            if stuck:
                subprocess.run(["docker", "rm", "-f", *stuck], capture_output=True)
            pytest.fail(f"Container did not finish within {RUN_TIMEOUT}s: {' '.join(cmd)}")
        except Exception as e:
            pytest.fail(f"Local Docker execution failed: {str(e)}")

    return _executor