#!/usr/bin/env python3
"""Plan which images to build, attest and scan so every change only touches its own images.

Each bake target gets a fingerprint: a hash of its resolved bake definition, the Dockerfile
stages it actually builds, the local files those stages copy, and the fingerprints of other
targets whose images it consumes (node-fips copies the FIPS provider from openssl-fips).
The fingerprint is stamped on the published image as a label. A target is rebuilt only when
its fingerprint differs from the published one or the image does not exist yet, so builds
that failed or were cancelled are retried automatically on the next run.

The image catalog comes from web/runtimes.yaml (runtime, version, flavor, tags, report names)
joined with `docker buildx bake --print` (tag -> bake target).

  plan_images.py build  --mode changed|all|<id ...>           build + attest plan
  plan_images.py scan   --mode missing|all|<id ...> --store DIR [--build-plan plan.json]
  plan_images.py verify --tag TAG --fingerprint FP            was TAG built with FP?
  plan_images.py prune  --store DIR                           drop reports of unpublished images

<id> is a runtime (openjdk), a runtime version (openjdk-21) or a bake target (openjdk-21-prod).
"""
import argparse
import concurrent.futures
import glob
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys

import yaml

RUNTIMES_FILE = "web/runtimes.yaml"
FINGERPRINT_LABEL = "io.github.taha2samy-3.build.fingerprint"
# Bake settings that do not change the produced image
IGNORED_TARGET_KEYS = ("cache-from", "cache-to", "output")
REPORT_KINDS = ("vuln", "cis", "sbom")
VAR_RE = re.compile(r"\$\{(\w+)(?::[-+]([^}]*))?\}|\$(\w+)")


# ==========================================
# Catalog
# ==========================================
def load_images(targets=None):
    """One entry per published image (runtime x version x flavor) from the dashboard catalog."""
    with open(RUNTIMES_FILE, encoding="utf-8") as f:
        runtimes = yaml.safe_load(f)["runtimes"]

    tag_to_target = {}
    for name, target in (targets or {}).items():
        for tag in target.get("tags", []):
            tag_to_target[tag] = name

    images = []
    for runtime in runtimes:
        for version in runtime["versions"]:
            unit = f"{runtime['id']}-{version['version']}"
            for flavor in version["flavors"]:
                tag = flavor["tags"][0]
                report = os.path.basename(flavor["reports"]["vuln"]).removesuffix("-vuln.json")
                image = {
                    "unit": unit,
                    "runtime": runtime["id"],
                    "version": str(version["version"]),
                    "flavor": flavor["id"],
                    "tag": tag,
                    "report": report,
                    "suffix": f"{unit}-{flavor['id']}",
                }
                if targets is not None:
                    if tag not in tag_to_target:
                        sys.exit(f"{RUNTIMES_FILE}: no bake target publishes {tag}")
                    image["target"] = tag_to_target[tag]
                images.append(image)
    return images


def bake_targets():
    res = subprocess.run(["docker", "buildx", "bake", "--print"], capture_output=True, text=True, check=True)
    return json.loads(res.stdout)["target"]


def select(images, ids):
    """Images matching runtime ids, runtime-version units or bake target names."""
    wanted = set(ids)
    chosen = [i for i in images if {i["runtime"], i["unit"], i.get("target")} & wanted]
    unknown = wanted - {k for i in images for k in (i["runtime"], i["unit"], i.get("target"))}
    if unknown:
        sys.exit(f"Unknown runtime, version or target: {', '.join(sorted(unknown))}")
    return chosen


# ==========================================
# Dockerfile analysis
# ==========================================
def logical_lines(path):
    lines, buf = [], ""
    with open(path, encoding="utf-8") as f:
        for raw in f.read().splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if raw.rstrip().endswith("\\"):
                buf += raw.rstrip()[:-1] + " "
                continue
            lines.append(" ".join((buf + raw).split()))
            buf = ""
    if buf.strip():
        lines.append(" ".join(buf.split()))
    return lines


def parse_dockerfile(path):
    global_lines, stages = [], []
    for line in logical_lines(path):
        if line.split(None, 1)[0].upper() == "FROM":
            words = [w for w in line.split()[1:] if not w.startswith("--")]
            name = words[2].lower() if len(words) >= 3 and words[1].upper() == "AS" else None
            stages.append({"index": len(stages), "name": name, "base": words[0].lower(), "lines": [line]})
        elif stages:
            stages[-1]["lines"].append(line)
        else:
            global_lines.append(line)
    return global_lines, stages


def stage_closure(stages, target_stage):
    """Stages the target actually builds: its own plus everything it uses via FROM / --from."""
    by_name = {s["name"]: s for s in stages if s["name"]}
    start = by_name[target_stage.lower()] if target_stage else stages[-1]
    seen, todo = {}, [start]
    while todo:
        stage = todo.pop()
        if stage["index"] in seen:
            continue
        seen[stage["index"]] = stage
        refs = [stage["base"]]
        for line in stage["lines"][1:]:
            refs += re.findall(r"--from=([^\s,]+)", line)
            refs += re.findall(r"--mount=\S*?\bfrom=([^\s,]+)", line)
        for ref in refs:
            ref = ref.lower()
            if ref in by_name:
                todo.append(by_name[ref])
            elif ref.isdigit() and int(ref) < len(stages):
                todo.append(stages[int(ref)])
    return [seen[i] for i in sorted(seen)]


def expand(value, variables):
    def repl(m):
        name = m.group(1) or m.group(3)
        if name in variables:
            return variables[name]
        if m.group(2) is not None:
            return m.group(2)
        raise ValueError(f"unresolved ${name}")
    return VAR_RE.sub(repl, value)


def arg_defaults(lines):
    defaults = {}
    for line in lines:
        if line.split(None, 1)[0].upper() == "ARG" and "=" in line:
            name, value = line.split(None, 1)[1].split("=", 1)
            defaults[name.strip()] = value.strip().strip('"').strip("'")
    return defaults


def local_sources(lines, context, variables):
    files = set()
    for line in lines:
        instruction, _, rest = line.partition(" ")
        if instruction.upper() not in ("COPY", "ADD") or "--from=" in rest:
            continue
        tokens = json.loads(rest) if rest.lstrip().startswith("[") else shlex.split(rest)
        sources = [t for t in tokens if not t.startswith("--")][:-1]
        for source in sources:
            # Remote sources are pinned through build args, which are already fingerprinted
            if re.match(r"^[a-z][a-z0-9+.-]*://", source) or source.startswith("git@"):
                continue
            source = expand(source, variables)
            matches = glob.glob(os.path.join(context, source))
            if not matches:
                files.add(f"<missing>{source}")
            for match in matches:
                if os.path.isdir(match):
                    for root, _, names in os.walk(match):
                        files.update(os.path.join(root, n) for n in names)
                else:
                    files.add(match)
    return files


def hash_file(path):
    if path.startswith("<missing>"):
        return "missing"
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def build_inputs(target):
    """Normalized Dockerfile instructions and local files the target's stages depend on."""
    context = target.get("context", ".")
    dockerfile = os.path.join(context, target.get("dockerfile", "Dockerfile"))
    try:
        global_lines, stages = parse_dockerfile(dockerfile)
        closure = stage_closure(stages, target.get("target"))
        lines = [l for stage in closure for l in stage["lines"]]
        variables = {**arg_defaults(global_lines + lines), **target.get("args", {})}
        return global_lines + lines, local_sources(lines, context, variables)
    except (KeyError, ValueError, OSError) as e:
        # Unknown layout: fall back to everything in the build context
        print(f"::warning::{dockerfile}: {e}; fingerprinting the whole build context", file=sys.stderr)
        files = {p for p in glob.glob(os.path.join(context, "**"), recursive=True)
                 if os.path.isfile(p) and "/.git/" not in p}
        return [], files | {dockerfile}


# ==========================================
# Fingerprints
# ==========================================
def compute_fingerprints(targets):
    tag_owner = {tag: name for name, t in targets.items() for tag in t.get("tags", [])}
    deps = {name: sorted({tag_owner[v] for v in t.get("args", {}).values() if v in tag_owner} - {name})
            for name, t in targets.items()}
    fingerprints = {}

    def fingerprint(name, chain=()):
        if name in fingerprints:
            return fingerprints[name]
        if name in chain:
            sys.exit(f"Dependency cycle: {' -> '.join(chain + (name,))}")
        target = targets[name]
        definition = {k: v for k, v in target.items() if k not in IGNORED_TARGET_KEYS}
        lines, files = build_inputs(target)
        digest = hashlib.sha256(json.dumps(definition, sort_keys=True).encode())
        digest.update("\n".join(lines).encode())
        for path in sorted(files):
            digest.update(f"\n{os.path.normpath(path)}:{hash_file(path)}".encode())
        for dep in deps[name]:
            digest.update(f"\ndep {dep}:{fingerprint(dep, chain + (name,))}".encode())
        fingerprints[name] = digest.hexdigest()[:32]
        return fingerprints[name]

    for name in targets:
        fingerprint(name)
    return fingerprints, deps


def published_fingerprint(tag):
    """Fingerprint label of the published image, '' if unlabelled, None if the image is missing."""
    res = subprocess.run(["docker", "buildx", "imagetools", "inspect", tag, "--format", "{{json .Image}}"],
                         capture_output=True, text=True)
    if res.returncode != 0:
        return None
    image = json.loads(res.stdout)
    configs = [image] if "config" in image else list(image.values())
    values = {(c.get("config") or {}).get("Labels", {}).get(FINGERPRINT_LABEL, "") for c in configs}
    return values.pop() if len(values) == 1 else ""


# ==========================================
# Outputs
# ==========================================
def write_outputs(outputs):
    path = os.environ.get("GITHUB_OUTPUT")
    lines = [f"{k}={v if isinstance(v, str) else json.dumps(v, separators=(',', ':'))}" for k, v in outputs.items()]
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    else:
        print("\n".join(lines))


def write_summary(markdown):
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(markdown + "\n")
    print(markdown)


def matrix_entries(targets_by_unit, fingerprints):
    return [
        {
            "unit": unit,
            "targets": ",".join(names),
            "set": "\n".join(f"{n}.labels.{FINGERPRINT_LABEL}={fingerprints[n]}" for n in names),
        }
        for unit, names in targets_by_unit.items()
    ]


# ==========================================
# Commands
# ==========================================
def cmd_build(args):
    targets = bake_targets()
    images = load_images(targets)
    fingerprints, deps = compute_fingerprints(targets)
    catalog_targets = list(dict.fromkeys(i["target"] for i in images))

    uncatalogued = sorted(set(targets) - set(catalog_targets))
    if uncatalogued:
        print(f"::warning::Bake targets not listed in {RUNTIMES_FILE} are never built: {', '.join(uncatalogued)}")

    reasons = {}
    if args.mode == ["changed"]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
            tags = {name: targets[name]["tags"][0] for name in catalog_targets}
            published = dict(zip(tags, pool.map(published_fingerprint, tags.values())))
        for name in catalog_targets:
            if published[name] is None:
                reasons[name] = "image not published yet"
            elif published[name] != fingerprints[name]:
                reasons[name] = "build inputs changed" if published[name] else "no fingerprint on published image"
    elif args.mode == ["all"]:
        reasons = {name: "full rebuild requested" for name in catalog_targets}
    else:
        reasons = {i["target"]: "rebuild requested" for i in select(images, args.mode)}

    unit_of = {i["target"]: i["unit"] for i in images}
    stage1, stage2 = {}, {}
    for name in catalog_targets:
        if name not in reasons:
            continue
        waiting_on = [d for d in deps[name] if d in reasons]
        if any(deps[d] and set(deps[d]) & set(reasons) for d in waiting_on):
            sys.exit(f"{name}: dependency chains deeper than one level are not supported")
        (stage2 if waiting_on else stage1).setdefault(unit_of[name], []).append(name)

    rebuilt = [dict(i, fingerprint=fingerprints[i["target"]]) for i in images if i["target"] in reasons]
    attest = [{"image": i["tag"].rsplit(":", 1)[0], "tag": i["tag"].rsplit(":", 1)[1], "suffix": i["suffix"],
               "fingerprint": i["fingerprint"]} for i in rebuilt]

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"images": rebuilt}, f, indent=2)

    rows = ["| Image | Target | Status |", "| :--- | :--- | :--- |"]
    for image in images:
        status = f"🔨 rebuild ({reasons[image['target']]})" if image["target"] in reasons else "✅ up to date"
        rows.append(f"| `{image['tag']}` | `{image['target']}` | {status} |")
    write_summary(f"### Build plan: {len(rebuilt)} of {len(images)} images\n\n" + "\n".join(rows))

    write_outputs({
        "build": matrix_entries(stage1, fingerprints),
        "build_dependents": matrix_entries(stage2, fingerprints),
        "images": attest,
        "has_build": str(bool(stage1)).lower(),
        "has_dependents": str(bool(stage2)).lower(),
        "has_images": str(bool(attest)).lower(),
    })


def cmd_scan(args):
    images = load_images()
    chosen = {}

    if args.build_plan and os.path.exists(args.build_plan):
        with open(args.build_plan, encoding="utf-8") as f:
            for image in json.load(f)["images"]:
                chosen[image["tag"]] = "rebuilt"

    if args.mode == ["all"]:
        for image in images:
            chosen.setdefault(image["tag"], "full rescan requested")
    elif args.mode == ["missing"]:
        for image in images:
            if any(not os.path.exists(os.path.join(args.store, f"{image['report']}-{kind}.json")) for kind in REPORT_KINDS):
                chosen.setdefault(image["tag"], "no stored report")
    else:
        for image in select(images, args.mode):
            chosen.setdefault(image["tag"], "rescan requested")

    scans = [{"image": i["tag"], "report": i["report"], "suffix": i["suffix"]} for i in images if i["tag"] in chosen]
    rows = ["| Image | Reason |", "| :--- | :--- |"] + [f"| `{tag}` | {why} |" for tag, why in chosen.items()]
    write_summary(f"### Scan plan: {len(scans)} of {len(images)} images\n\n" + ("\n".join(rows) if scans else "Nothing to scan, the dashboard is rebuilt from stored reports."))
    write_outputs({"scans": scans, "has_scans": str(bool(scans)).lower()})


def cmd_verify(args):
    built = published_fingerprint(args.tag) == args.fingerprint
    if not built:
        print(f"::notice::{args.tag} was not rebuilt by this run (fingerprint mismatch), skipping")
    write_outputs({"built": str(built).lower()})


def cmd_prune(args):
    keep = {f"{i['report']}-{kind}.json" for i in load_images() for kind in REPORT_KINDS} | {"config.json"}
    for name in sorted(os.listdir(args.store)):
        if name.endswith(".json") and name not in keep:
            print(f"Removing stale report {name}")
            os.remove(os.path.join(args.store, name))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build")
    build.add_argument("--mode", nargs="+", default=["changed"])
    build.add_argument("--output", default="build-plan.json")

    scan = sub.add_parser("scan")
    scan.add_argument("--mode", nargs="+", default=["missing"])
    scan.add_argument("--store", required=True)
    scan.add_argument("--build-plan")

    verify = sub.add_parser("verify")
    verify.add_argument("--tag", required=True)
    verify.add_argument("--fingerprint", required=True)

    prune = sub.add_parser("prune")
    prune.add_argument("--store", required=True)

    args = parser.parse_args()
    if getattr(args, "mode", None):
        args.mode = " ".join(args.mode).replace(",", " ").split()
    {"build": cmd_build, "scan": cmd_scan, "verify": cmd_verify, "prune": cmd_prune}[args.command](args)


if __name__ == "__main__":
    main()
