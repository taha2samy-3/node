#!/usr/bin/env python3
"""Join per-architecture builds into multi-platform images.

Each build job pushes its images by digest only (no tags). Then:

  merge_manifests.py record --arch amd64 --out digests      # bake metadata in $BAKE_METADATA
  merge_manifests.py merge --targets a,b --digests digests  # create the tagged multi-platform images

`merge` reads each target's tags and index annotations from docker-bake.hcl, so the final
image looks exactly like a single multi-platform build.
"""
import argparse
import json
import os
import subprocess
import sys

ARCHES = ("amd64", "arm64")


def run(cmd):
    print("+ " + " ".join(cmd))
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def cmd_record(args):
    metadata = json.loads(os.environ["BAKE_METADATA"])
    os.makedirs(args.out, exist_ok=True)
    for target, meta in metadata.items():
        digest = meta.get("containerimage.digest")
        if not digest:
            continue
        with open(os.path.join(args.out, f"{target}-{args.arch}"), "w", encoding="utf-8") as f:
            f.write(digest)
        print(f"{target} [{args.arch}] {digest}")


def cmd_merge(args):
    targets = [t for t in args.targets.split(",") if t]
    recorded = [t for t in targets if any(os.path.exists(os.path.join(args.digests, f"{t}-{a}")) for a in ARCHES)]
    if not recorded:
        print(f"::notice::{args.targets}: not built in this run, nothing to merge")
        return
    bake = json.loads(run(["docker", "buildx", "bake", "--print", *targets]))["target"]
    for target in targets:
        definition = bake[target]
        tags = definition["tags"]
        repository = tags[0].rsplit(":", 1)[0]
        sources = []
        for arch in ARCHES:
            path = os.path.join(args.digests, f"{target}-{arch}")
            if not os.path.exists(path):
                sys.exit(f"{target}: no {arch} build was recorded")
            with open(path, encoding="utf-8") as f:
                sources.append(f"{repository}@{f.read().strip()}")
        # Per-architecture builds carry manifest annotations; the multi-platform index gets them too,
        # which is where GHCR reads the source repository and description from
        annotations = []
        for annotation in definition.get("annotations", []):
            _, _, value = annotation.partition(":")
            annotations += ["--annotation", f"index:{value}"]
        cmd = ["docker", "buildx", "imagetools", "create"]
        for tag in tags:
            cmd += ["--tag", tag]
        run(cmd + annotations + sources)

        manifest = json.loads(run(["docker", "buildx", "imagetools", "inspect", tags[0], "--format", "{{json .Manifest}}"]))
        platforms = {f"{m['platform']['os']}/{m['platform']['architecture']}" for m in manifest.get("manifests", []) if m.get("platform", {}).get("os") != "unknown"}
        expected = {f"linux/{arch}" for arch in ARCHES}
        if not expected <= platforms:
            sys.exit(f"{tags[0]}: merged image has {sorted(platforms)}, expected {sorted(expected)}")
        print(f"{tags[0]}: {', '.join(sorted(platforms))} -> {manifest['digest']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    record = sub.add_parser("record")
    record.add_argument("--arch", required=True, choices=ARCHES)
    record.add_argument("--out", required=True)
    merge = sub.add_parser("merge")
    merge.add_argument("--targets", required=True)
    merge.add_argument("--digests", required=True)
    args = parser.parse_args()
    {"record": cmd_record, "merge": cmd_merge}[args.command](args)


if __name__ == "__main__":
    main()
