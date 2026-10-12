#!/usr/bin/env python3
"""Benchmark a FIPS image against a non-FIPS baseline of the same software.

  run_benchmarks.py --unit node-fips-22 --arch arm64 --out benchmarks

  openssl     OpenSSL FIPS image vs. stock OpenSSL on Alpine (`openssl speed`)
  node-fips   Node.js FIPS image vs. this repository's regular Node.js image of the same version
  openjdk     OpenJDK FIPS (Bouncy Castle FIPS) vs. stock Eclipse Temurin of the same version

Each comparison runs `--runs` times and keeps the median. The images must be pullable. Writes
<out>/<standard-flavor-report>-bench-<arch>.json for the dashboard. Shared CI runners are noisy:
treat the numbers as indicative and compare the FIPS / baseline ratio rather than absolutes.
"""
import argparse
import json
import os
import re
import statistics
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan_images  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BENCH_DIR = os.path.join(ROOT, ".github", "scripts", "bench")
OPENSSL_BASELINE_IMAGE = "buildpack-deps:bookworm-curl"
OPENSSL_EVP = [
    ("AES-128-GCM encrypt", "aes-128-gcm"),
    ("AES-256-GCM encrypt", "aes-256-gcm"),
    ("AES-128-CBC encrypt", "aes-128-cbc"),
    ("AES-256-CBC encrypt", "aes-256-cbc"),
    ("AES-128-CTR encrypt", "aes-128-ctr"),
    ("AES-256-CTR encrypt", "aes-256-ctr"),
    ("SHA-224", "sha224"),
    ("SHA-256", "sha256"),
    ("SHA-384", "sha384"),
    ("SHA-512", "sha512"),
    ("SHA3-224", "sha3-224"),
    ("SHA3-256", "sha3-256"),
    ("SHA3-384", "sha3-384"),
    ("SHA3-512", "sha3-512"),
]
OPENSSL_ASYM = [
    ("RSA-2048", "rsa2048"),
    ("RSA-3072", "rsa3072"),
    ("RSA-4096", "rsa4096"),
    ("ECDSA P-256", "ecdsap256"),
    ("ECDSA P-384", "ecdsap384"),
    ("ECDSA P-521", "ecdsap521"),
]


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=600, **kwargs)


def cpu_model():
    out = run(["lscpu"]).stdout
    match = re.search(r"^Model name:\s*(.+)$", out, re.M)
    return match.group(1).strip() if match else "unknown"


# ==========================================
# OpenSSL (openssl speed)
# ==========================================
def openssl_speed(image, entrypoint, args):
    return run(["docker", "run", "--rm", "--entrypoint", entrypoint, image, "speed", "-seconds", str(SECONDS), *args]).stdout


def parse_evp(output):
    """`openssl speed -bytes 16384 -evp X` prints one value in 1000s of bytes per second."""
    values = re.findall(r"^\S+\s+([\d.]+)k\s*$", output, re.M)
    return float(values[-1]) * 1000 / 1e6 if values else None


def parse_asym(output):
    """sign/s and verify/s from the `openssl speed rsa2048|ecdsap256` table whose header has sign/s."""
    lines = output.splitlines()
    for i, line in enumerate(lines[:-1]):
        if "sign/s" in line:
            names = line.split()
            values = [t.rstrip("s") for t in lines[i + 1].split() if re.fullmatch(r"[\d.]+s?", t)]
            columns = dict(zip(names, values[-len(names):]))
            return {k: float(v) for k, v in columns.items() if k in ("sign/s", "verify/s")}
    return {}


def openssl_suite(fips_image):
    baseline_img = OPENSSL_BASELINE_IMAGE
    inspect_res = run(["docker", "image", "inspect", baseline_img])
    if inspect_res.returncode != 0:
        pull_res = run(["docker", "pull", "-q", baseline_img])
        if pull_res.returncode != 0:
            baseline_img = "bench-baseline-debian"
            subprocess.run(["docker", "build", "-q", "-t", baseline_img, "-"],
                           input="FROM debian:bookworm-slim\nRUN apt-get update && apt-get install -y openssl\n",
                           text=True, check=True, capture_output=True, timeout=600)
    images = {"fips": (fips_image, "/usr/local/bin/openssl"), "baseline": (baseline_img, "openssl")}

    def once(which):
        image, entrypoint = images[which]
        results = {}
        for name, alg in OPENSSL_EVP:
            results[name] = ("MB/s", parse_evp(openssl_speed(image, entrypoint, ["-bytes", "16384", "-evp", alg])))
        for name, alg in OPENSSL_ASYM:
            columns = parse_asym(openssl_speed(image, entrypoint, [alg]))
            results[f"{name} sign"] = ("ops/s", columns.get("sign/s"))
            results[f"{name} verify"] = ("ops/s", columns.get("verify/s"))
        return results

    version = run(["docker", "run", "--rm", "--entrypoint", "openssl", baseline_img, "version"]).stdout.split()
    return once, {"name": f"OpenSSL {version[1] if len(version) > 1 else ''} on Debian Bookworm (default provider)", "image": baseline_img}


# ==========================================
# Node.js (node-crypto.js)
# ==========================================
def node_suite(fips_image, version):
    baseline = f"ghcr.io/taha2samy-3/node:{version}"
    run(["docker", "pull", "-q", baseline])

    def once(which):
        image = fips_image if which == "fips" else baseline
        proc = run(["docker", "run", "--rm", "-e", f"BENCH_SECONDS={SECONDS}", "-v", f"{BENCH_DIR}:/bench:ro",
                    "--entrypoint", "/usr/bin/node", image, "/bench/node-crypto.js"])
        return {r["name"]: (r["metric"], r["value"]) for r in json.loads(proc.stdout or "[]")}

    return once, {"name": f"Node.js {version} without FIPS (this repository's regular image)", "image": baseline}


# ==========================================
# Java (Bench.java)
# ==========================================
def java_suite(fips_image, jdk_image, version):
    baseline = f"eclipse-temurin:{version}-jre"
    run(["docker", "pull", "-q", baseline])
    classes = tempfile.mkdtemp(prefix="bench-classes-")
    os.chmod(classes, 0o777)
    compile_proc = run(["docker", "run", "--rm", "-v", f"{BENCH_DIR}:/src:ro", "-v", f"{classes}:/out",
                        "--entrypoint", "/opt/java/bin/javac", jdk_image, "-d", "/out", "/src/Bench.java"])
    if compile_proc.returncode != 0:
        sys.exit(f"javac failed: {compile_proc.stderr}")

    def once(which):
        image, java = (fips_image, "/opt/java/bin/java") if which == "fips" else (baseline, "java")
        proc = run(["docker", "run", "--rm", "-v", f"{classes}:/bench:ro", "--entrypoint", java, image,
                    f"-Dbench.seconds={SECONDS}", "-cp", "/bench", "Bench"])
        lines = [l for l in proc.stdout.splitlines() if l.startswith("[")]
        return {r["name"]: (r["metric"], r["value"]) for r in json.loads(lines[-1] if lines else "[]")}

    return once, {"name": f"Eclipse Temurin {version} (SunJCE, not FIPS)", "image": baseline}


def boringssl_suite(fips_image, dev_image):
    baseline_img = OPENSSL_BASELINE_IMAGE
    inspect_res = run(["docker", "image", "inspect", baseline_img])
    if inspect_res.returncode != 0:
        pull_res = run(["docker", "pull", "-q", baseline_img])
        if pull_res.returncode != 0:
            baseline_img = "bench-baseline-debian"
            subprocess.run(["docker", "build", "-q", "-t", baseline_img, "-"],
                           input="FROM debian:bookworm-slim\nRUN apt-get update && apt-get install -y openssl\n",
                           text=True, check=True, capture_output=True, timeout=600)

    classes = tempfile.mkdtemp(prefix="bssl-bench-")
    os.chmod(classes, 0o777)
    compile_proc = run(["docker", "run", "--rm", "-v", f"{BENCH_DIR}:/src:ro", "-v", f"{classes}:/out",
                        "--entrypoint", "gcc", dev_image, "-O3", "/src/bssl-crypto.c", "-lcrypto", "-o", "/out/bssl-bench"])
    if compile_proc.returncode != 0:
        sys.exit(f"bssl-bench compile failed: {compile_proc.stderr}")

    def once(which):
        if which == "fips":
            proc = run(["docker", "run", "--rm", "-v", f"{classes}:/bench:ro", "-e", f"BENCH_SECONDS={SECONDS}",
                        "--entrypoint", "/bench/bssl-bench", dev_image])
            return {r["name"]: (r["metric"], r["value"]) for r in json.loads(proc.stdout or "[]")}
        else:
            results = {}
            for name, alg in OPENSSL_EVP[:4]:
                results[name] = ("MB/s", parse_evp(openssl_speed(baseline_img, "openssl", ["-bytes", "16384", "-evp", alg])))
            return results

    return once, {"name": "OpenSSL baseline on Debian Bookworm", "image": baseline_img}


def go_fips_suite(fips_image, dev_image, version):
    baseline = f"ghcr.io/taha2samy-3/go:{version}-dev"
    run(["docker", "pull", "-q", baseline])

    def once(which):
        image = dev_image if which == "fips" else baseline
        proc = run(["docker", "run", "--rm", "-e", f"BENCH_SECONDS={SECONDS}", "-v", f"{BENCH_DIR}:/bench:ro",
                    image, "go", "run", "/bench/go-crypto.go"])
        return {r["name"]: (r["metric"], r["value"]) for r in json.loads(proc.stdout or "[]")}

    return once, {"name": f"Go {version} without BoringCrypto (regular Go dev image)", "image": baseline}


def main():
    global SECONDS
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--unit", required=True)
    parser.add_argument("--arch", required=True, choices=["amd64", "arm64"])
    parser.add_argument("--out", required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--seconds", type=float, default=1.0)
    args = parser.parse_args()
    SECONDS = max(1, int(args.seconds))

    os.chdir(ROOT)
    images = {i["flavor"]: i for i in plan_images.load_images() if i["unit"] == args.unit}
    if "standard" not in images and "dev" not in images:
        sys.exit(f"{args.unit}: no benchmarkable flavor found")
    target_img = images.get("standard") or images.get("dev")
    images_to_pull = {target_img["tag"]}
    if target_img["runtime"] in ("openjdk", "go-fips", "boringssl") and "dev" in images:
        images_to_pull.add(images["dev"]["tag"])
    for image in images_to_pull:
        run(["docker", "pull", "-q", image])

    if target_img["runtime"] == "openssl":
        once, baseline = openssl_suite(target_img["tag"])
    elif target_img["runtime"] == "boringssl":
        once, baseline = boringssl_suite(target_img["tag"], images.get("dev", target_img)["tag"])
    elif target_img["runtime"] == "node-fips":
        once, baseline = node_suite(target_img["tag"], target_img["version"])
    elif target_img["runtime"] == "go-fips":
        once, baseline = go_fips_suite(target_img["tag"], images.get("dev", target_img)["tag"], target_img["version"])
    elif target_img["runtime"] == "openjdk":
        once, baseline = java_suite(target_img["tag"], images["dev"]["tag"], target_img["version"])
    else:
        sys.exit(f"No benchmark for runtime {target_img['runtime']}")

    samples = {"fips": [], "baseline": []}
    for _ in range(args.runs):
        for which in samples:
            samples[which].append(once(which))

    results = []
    for name in samples["fips"][0]:
        metric = samples["fips"][0][name][0]
        median = {}
        for which in samples:
            values = [s[name][1] for s in samples[which] if name in s and s[name][1] is not None]
            median[which] = round(statistics.median(values), 2) if values else None
        results.append({"name": name, "metric": metric, "fips": median["fips"], "baseline": median["baseline"]})

    os.makedirs(args.out, exist_ok=True)
    report = {
        "unit": args.unit,
        "arch": args.arch,
        "image": target_img["tag"],
        "baseline": baseline,
        "cpu": cpu_model(),
        "runs": args.runs,
        "seconds": args.seconds,
        "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "results": results,
    }
    path = os.path.join(args.out, f"{target_img['report']}-bench-{args.arch}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=1)
    for r in results:
        print(f"{r['name']:24} {r['metric']:6} FIPS {r['fips']!s:>12}   baseline {r['baseline']!s:>12}")


SECONDS = 1.0

if __name__ == "__main__":
    main()
