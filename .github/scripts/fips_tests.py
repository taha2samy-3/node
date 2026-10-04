#!/usr/bin/env python3
"""Run the FIPS 140-3 test suites against the images of one runtime version.

  fips_tests.py --unit node-fips-22 --arch amd64 --out fips-results

For every flavor of the unit (from web/runtimes.yaml) the matching suite runs against the
image's primary tag, which must already be present locally (pulled or built). Each flavor
produces <out>/<report-base>-tests-<arch>.json for the dashboard. Exits non-zero when any
test fails, after all results are written.

Suites
  openssl     openssl/tests without the internet-dependent `network` tests (standard and
              distroless images); the dev image, whose entrypoint
              is a shell, gets a smoke check through its openssl binary
  openjdk     openjdk/tests: compiled with the dev (JDK) image, run on each flavor
  node-fips   nodejs/fips/tests
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan_images  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def pytest_suite(suite_dir, args):
    """Run pytest in suite_dir and return parsed JUnit results."""
    with tempfile.TemporaryDirectory() as tmp:
        junit = os.path.join(tmp, "junit.xml")
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "addopts=", f"--junitxml={junit}", *args]
        started = time.monotonic()
        proc = subprocess.run(cmd, cwd=os.path.join(ROOT, suite_dir), capture_output=True, text=True)
        duration = time.monotonic() - started
        if not os.path.exists(junit):
            return [{"name": "suite", "classname": suite_dir, "outcome": "failed", "duration": duration,
                     "message": (proc.stdout + proc.stderr)[-2000:]}]
        tests = []
        for case in ET.parse(junit).getroot().iter("testcase"):
            outcome, message = "passed", ""
            for kind in ("failure", "error", "skipped"):
                node = case.find(kind)
                if node is not None:
                    if kind == "skipped":
                        # strict xfail: a documented limitation of the certified module
                        outcome = "xfail" if node.get("type") == "pytest.xfail" else "skipped"
                    else:
                        outcome = "failed"
                    message = (node.get("message") or node.text or "").strip()[:2000]
                    break
            tests.append({
                "name": case.get("name"),
                "classname": (case.get("classname") or "").split(".")[-1],
                "outcome": outcome,
                "duration": round(float(case.get("time") or 0), 3),
                "message": message,
            })
        return tests


def openssl_smoke(tag):
    """The dev image's entrypoint is a shell: check FIPS through its openssl binary."""
    def run(*args):
        return subprocess.run(["docker", "run", "--rm", "--entrypoint", "/usr/local/bin/openssl", tag, *args], capture_output=True, text=True)

    started = time.monotonic()
    providers = run("list", "-providers")
    md5 = run("dgst", "-md5", "/dev/null")
    sha = run("dgst", "-sha256", "/dev/null")
    checks = [
        ("test_fips_provider_active", "fips" in providers.stdout.lower() and "active" in providers.stdout.lower(), providers.stdout + providers.stderr),
        ("test_md5_rejected", md5.returncode != 0, md5.stdout + md5.stderr),
        ("test_sha256_allowed", sha.returncode == 0, sha.stdout + sha.stderr),
    ]
    duration = round((time.monotonic() - started) / len(checks), 3)
    return [{"name": name, "classname": "smoke", "outcome": "passed" if ok else "failed", "duration": duration,
             "message": "" if ok else output[-2000:]} for name, ok, output in checks]


def run_flavor(runtime, flavor, tags_by_flavor):
    tag = tags_by_flavor[flavor]
    if runtime == "openssl":
        if flavor == "dev":
            return "openssl smoke check", openssl_smoke(tag)
        # Tests that depend on public internet hosts are left out of the gate (run them by hand with -m network)
        return "openssl/tests", pytest_suite("openssl/tests", ["--image", tag, "-m", "not network"])
    if runtime == "openjdk":
        return "openjdk/tests", pytest_suite("openjdk/tests", ["--jdk-img", tags_by_flavor["dev"], "--jre-img", tag])
    if runtime == "node-fips":
        return "nodejs/fips/tests", pytest_suite("nodejs/fips/tests", ["--image", tag, "--flavor", flavor])
    sys.exit(f"No FIPS test suite for runtime {runtime}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--unit", required=True, help="runtime-version, e.g. openjdk-21")
    parser.add_argument("--arch", required=True, choices=["amd64", "arm64"])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    os.chdir(ROOT)
    images = [i for i in plan_images.load_images() if i["unit"] == args.unit]
    if not images:
        sys.exit(f"Unknown unit {args.unit}")
    runtime = images[0]["runtime"]
    tags_by_flavor = {i["flavor"]: i["tag"] for i in images}
    os.makedirs(args.out, exist_ok=True)

    failed = 0
    for image in images:
        suite, tests = run_flavor(runtime, image["flavor"], tags_by_flavor)
        summary = {k: sum(1 for t in tests if t["outcome"] == k) for k in ("passed", "failed", "xfail", "skipped")}
        summary["total"] = len(tests)
        summary["duration"] = round(sum(t["duration"] for t in tests), 2)
        failed += summary["failed"]
        result = {
            "image": image["tag"],
            "flavor": image["flavor"],
            "arch": args.arch,
            "suite": suite,
            "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "summary": summary,
            "tests": tests,
        }
        path = os.path.join(args.out, f"{image['report']}-tests-{args.arch}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=1)
        print(f"{image['tag']} [{args.arch}] {suite}: {summary['passed']} passed, {summary['failed']} failed, "
              f"{summary['xfail']} known limitations, {summary['skipped']} skipped")

    if failed:
        sys.exit(f"{failed} FIPS test(s) failed")


if __name__ == "__main__":
    main()
