#!/usr/bin/env python3
"""Watch the NIST CMVP certificates of the FIPS 140-3 modules pinned in .github/dependencies.yml.

Certified modules are never updated automatically; this is their lifecycle check:

  cmvp_watch.py --json reports/fips-certificates.json   certificate data for the dashboard
  cmvp_watch.py --issue                                  open / update / close the tracking issue

Something needs attention when a certificate is no longer Active, its sunset date is less than
a year away, it does not list the pinned version, or the vendor published a newer certificate
for the same module.
"""
import argparse
import html
import json
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

import yaml

CONFIG_FILE = ".github/dependencies.yml"
CMVP = "https://csrc.nist.gov/projects/cryptographic-module-validation-program"
SUNSET_WARNING = timedelta(days=365)
ISSUE_LABEL = "fips-certificates"
ISSUE_TITLE = "FIPS 140-3 certificate watch"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (secure-runtimes certificate watch)"})
    with urllib.request.urlopen(request, timeout=60) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def text(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())


def field(page, label):
    match = re.search(r">\s*" + re.escape(label) + r"\s*</[^>]+>\s*<[^>]+>(.*?)</", page, re.S | re.I)
    return text(match.group(1)) if match else None


def certificate(number):
    page = fetch(f"{CMVP}/certificate/{number}")
    sunset = field(page, "Sunset Date")
    versions = field(page, "Software Versions") or field(page, "Software Version")
    return {
        "certificate": number,
        "url": f"{CMVP}/certificate/{number}",
        "module": field(page, "Module Name"),
        "vendor": field(page, "Vendor Name") or None,
        "standard": field(page, "Standard"),
        "status": field(page, "Status"),
        "sunset": datetime.strptime(sunset, "%m/%d/%Y").date().isoformat() if sunset else None,
        "versions": [v.strip() for v in re.split(r"[,;]", versions)] if versions else [],
    }


def newer_certificates(module, vendor, number):
    """Active certificates for the same module name and vendor issued after `number`."""
    query = urllib.parse.urlencode({"SearchMode": "Basic", "ModuleName": module, "CertificateStatus": "Active", "ValidationYear": 0})
    page = fetch(f"{CMVP}/validated-modules/search?{query}")
    found = []
    for row in re.findall(r'<tr[^>]*id="cert-row-\d+"[^>]*>(.*?)</tr>', page, re.S):
        cells = [text(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
        if len(cells) >= 3 and cells[0].isdigit() and int(cells[0]) > number and cells[1] == vendor and cells[2] == module:
            found.append({"certificate": int(cells[0]), "date": cells[-1], "url": f"{CMVP}/certificate/{cells[0]}"})
    return found


def check(module):
    info = certificate(module["certificate"])
    info.update({"name": module["name"], "pinned_version": module["version"], "used_by": module["used_by"]})
    info["newer"] = newer_certificates(module["name"], module["vendor"], module["certificate"])
    alerts = []
    if info["status"] != "Active":
        alerts.append(f"certificate #{module['certificate']} status is {info['status']}")
    if info["sunset"] and date.fromisoformat(info["sunset"]) - date.today() < SUNSET_WARNING:
        alerts.append(f"certificate #{module['certificate']} sunsets on {info['sunset']}")
    if info["versions"] and module["version"] not in info["versions"]:
        alerts.append(f"pinned version {module['version']} is not listed on certificate #{module['certificate']} ({', '.join(info['versions'])})")
    for newer in info["newer"]:
        alerts.append(f"newer certificate #{newer['certificate']} ({newer['date']}): review whether to move to it")
    info["alerts"] = alerts
    return info


def issue_body(results):
    rows = ["| Module | Pinned | Certificate | Status | Sunset | Needs attention |", "| :--- | :--- | :--- | :--- | :--- | :--- |"]
    for r in results:
        rows.append(f"| {r['name']} | `{r['pinned_version']}` | [#{r['certificate']}]({r['url']}) | {r['status']} | {r['sunset'] or '—'} | "
                    + ("<br>".join(r["alerts"]) or "—") + " |")
    return ("Certified FIPS 140-3 modules are never updated automatically. This issue is opened and updated by "
            "`.github/workflows/fips-certificates.yml` and closes itself once nothing needs attention.\n\n" + "\n".join(rows) +
            "\n\nTo move to a new certificate: update the version in `docker-bake.hcl` and the `certified` entry in "
            "`.github/dependencies.yml`, then let the pull request check run the FIPS test suites.\n")


def sync_issue(results):
    alerts = [a for r in results for a in r["alerts"]]
    found = subprocess.run(["gh", "issue", "list", "--label", ISSUE_LABEL, "--state", "open", "--json", "number", "--limit", "1"],
                           capture_output=True, text=True, check=True)
    existing = json.loads(found.stdout)
    if not alerts:
        if existing:
            subprocess.run(["gh", "issue", "close", str(existing[0]["number"]), "--comment", "Every certified module is current again."], check=True)
        print("No certificate needs attention")
        return
    body = issue_body(results)
    if existing:
        subprocess.run(["gh", "issue", "edit", str(existing[0]["number"]), "--body", body], check=True)
    else:
        subprocess.run(["gh", "label", "create", ISSUE_LABEL, "--color", "d93f0b", "--description", "FIPS 140-3 certificate lifecycle"], capture_output=True)
        subprocess.run(["gh", "issue", "create", "--title", ISSUE_TITLE, "--label", ISSUE_LABEL, "--body", body], check=True)
    print("\n".join(alerts))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", help="write certificate data for the dashboard to this file")
    parser.add_argument("--issue", action="store_true", help="open, update or close the tracking issue")
    args = parser.parse_args()

    with open(CONFIG_FILE, encoding="utf-8") as f:
        certified = yaml.safe_load(f)["certified"]
    results = [check(module) for module in certified]
    for r in results:
        print(f"#{r['certificate']} {r['name']} {r['pinned_version']}: {r['status']}, sunset {r['sunset']}, "
              f"versions {r['versions'] or 'not listed'}, {len(r['alerts'])} alert(s)")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"checked_at": datetime.now().astimezone().isoformat(timespec="seconds"), "modules": results}, f, indent=1)
    if args.issue:
        sync_issue(results)
    if not args.json and not args.issue:
        json.dump(results, sys.stdout, indent=1)


if __name__ == "__main__":
    main()
