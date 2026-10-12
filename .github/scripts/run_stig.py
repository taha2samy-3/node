#!/usr/bin/env python3
"""Run Chainguard GPOS SRG STIG compliance scan against container images using OpenSCAP.

Evaluates an image against the official Chainguard STIG profile:
  Profile: xccdf_basic_profile_.check
  DataStream: /usr/share/xml/scap/ssg/content/ssg-chainguard-gpos-ds.xml
  Scanner: cgr.dev/chainguard/openscap:latest-dev

Parses the XCCDF 1.2 results into a structured JSON report consumed by the security dashboard.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

DEFAULT_PROFILE = "xccdf_basic_profile_.check"
DEFAULT_DATASTREAM = "/usr/share/xml/scap/ssg/content/ssg-chainguard-gpos-ds.xml"
DEFAULT_SCANNER = "cgr.dev/chainguard/openscap:latest-dev"

XCCDF_1_2_NS = "http://checklists.nist.gov/xccdf/1.2"
OVAL_DEF_NS = "http://oval.mitre.org/XMLSchema/oval-definitions-5"


def run_oscap_docker(image, output_dir, profile=DEFAULT_PROFILE, datastream=DEFAULT_DATASTREAM, scanner=DEFAULT_SCANNER):
    """Executes oscap-docker image evaluation inside the OpenSCAP container."""
    results_xml_host = os.path.join(output_dir, "results.xml")
    cmd = [
        "docker", "run", "--rm",
        "-u", "0:0",
        "--pid=host",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", f"{os.path.abspath(output_dir)}:/out",
        "--entrypoint", "/bin/sh",
        scanner,
        "-c",
        f"/usr/bin/oscap-docker image {image} xccdf eval --profile '{profile}' --results /out/results.xml '{datastream}'"
    ]

    print(f"[*] Running Chainguard STIG scan against {image}...")
    res = subprocess.run(cmd, capture_output=True, text=True)

    # oscap returns 0 (all pass), 2 (some rules failed or unknown), or >2 (runtime error)
    if not os.path.exists(results_xml_host):
        print(f"[!] Error: OpenSCAP did not produce results.xml (exit code {res.returncode}):\n{res.stderr or res.stdout}", file=sys.stderr)
        sys.exit(1)

    return results_xml_host


def normalize_severity(sev):
    s = (sev or "").lower()
    if s in ("high", "medium", "low"):
        return s
    return "medium"


def normalize_status(status):
    s = (status or "").lower()
    if s in ("pass", "passed"):
        return "pass"
    if s in ("fail", "failed"):
        return "fail"
    if s in ("notapplicable", "not_applicable", "notselected"):
        return "notapplicable"
    return "manual"


def parse_xccdf_results(xml_path, image, profile=DEFAULT_PROFILE):
    """Parses XCCDF 1.2 Benchmark XML results into structured JSON."""
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Namespace handling
    ns = {"xccdf": XCCDF_1_2_NS}

    # Extract rule definitions
    rule_defs = {}
    for r in root.iter(f"{{{XCCDF_1_2_NS}}}Rule"):
        rid = r.attrib.get("id")
        title_el = r.find(f"{{{XCCDF_1_2_NS}}}title")
        desc_el = r.find(f"{{{XCCDF_1_2_NS}}}description")
        rationale_el = r.find(f"{{{XCCDF_1_2_NS}}}rationale")
        severity = r.attrib.get("severity", "medium")
        idents = [i.text.strip() for i in r.findall(f"{{{XCCDF_1_2_NS}}}ident") if i.text]

        title = title_el.text.strip() if title_el is not None and title_el.text else rid
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
        rationale = rationale_el.text.strip() if rationale_el is not None and rationale_el.text else ""

        rule_defs[rid] = {
            "title": " ".join(title.split()),
            "description": " ".join(desc.split()),
            "rationale": " ".join(rationale.split()),
            "severity": normalize_severity(severity),
            "idents": idents,
        }

    # Extract rule evaluation results
    rules = []
    counts = {"pass": 0, "fail": 0, "notapplicable": 0, "manual": 0}

    for rr in root.iter(f"{{{XCCDF_1_2_NS}}}rule-result"):
        idref = rr.attrib.get("idref")
        res_el = rr.find(f"{{{XCCDF_1_2_NS}}}result")
        raw_status = res_el.text.strip() if res_el is not None and res_el.text else "unknown"
        status = normalize_status(raw_status)
        counts[status] = counts.get(status, 0) + 1

        rule_meta = rule_defs.get(idref, {
            "title": idref,
            "description": "",
            "rationale": "",
            "severity": "medium",
            "idents": [],
        })

        rules.append({
            "id": idref,
            "title": rule_meta["title"],
            "description": rule_meta["description"],
            "rationale": rule_meta["rationale"],
            "severity": rule_meta["severity"],
            "status": status,
            "idents": rule_meta["idents"],
        })

    # Sort rules: failed first, then pass, then notapplicable; secondary sort by ID
    order = {"fail": 0, "pass": 1, "manual": 2, "notapplicable": 3}
    rules.sort(key=lambda x: (order.get(x["status"], 9), x["id"]))

    total_evaluated = counts["pass"] + counts["fail"]
    score = round((counts["pass"] / total_evaluated * 100), 2) if total_evaluated > 0 else 100.0

    report = {
        "id": "chainguard-gpos-srg",
        "title": "Chainguard GPOS SRG STIG Profile",
        "profile": profile,
        "image": image,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "score": score,
            "passed": counts["pass"],
            "failed": counts["fail"],
            "notapplicable": counts["notapplicable"],
            "manual": counts["manual"],
            "total": len(rules),
        },
        "rules": rules,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Image reference to scan")
    parser.add_argument("--platform", default="linux/amd64", help="Platform of the image")
    parser.add_argument("--output", required=True, help="Path to output JSON report")
    parser.add_argument("--xml-output", help="Optional path to save raw OpenSCAP results XML")
    parser.add_argument("--profile", default=DEFAULT_PROFILE, help="XCCDF Profile ID")
    parser.add_argument("--datastream", default=DEFAULT_DATASTREAM, help="DataStream path in scanner container")
    parser.add_argument("--scanner", default=DEFAULT_SCANNER, help="Scanner container image")

    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as tmp_dir:
        results_xml = run_oscap_docker(
            image=args.image,
            output_dir=tmp_dir,
            profile=args.profile,
            datastream=args.datastream,
            scanner=args.scanner,
        )

        if args.xml_output:
            os.makedirs(os.path.dirname(os.path.abspath(args.xml_output)), exist_ok=True)
            with open(results_xml, "r", encoding="utf-8") as src, open(args.xml_output, "w", encoding="utf-8") as dst:
                dst.write(src.read())

        report = parse_xccdf_results(results_xml, image=args.image, profile=args.profile)

        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        print(f"[+] Scan completed successfully!")
        print(f"    Passed: {report['summary']['passed']}")
        print(f"    Failed: {report['summary']['failed']}")
        print(f"    Not Applicable: {report['summary']['notapplicable']}")
        print(f"    Compliance Score: {report['summary']['score']}%")
        print(f"    Saved report to: {args.output}")


if __name__ == "__main__":
    main()
