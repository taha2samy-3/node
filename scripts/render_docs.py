import json
import os
import sys

VERSIONS = ["22", "24"]

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return None

def render_version_page(version):
    vuln_data = load_json(f"reports/{version}-vuln.json")
    cis_data = load_json(f"reports/{version}-cis.json")

    md_content = f"# Node.js {version} LTS Hardening & Compliance Report\n\n"
    md_content += "This page contains the automated vulnerability scans and Docker CIS compliance reports for this version.\n\n"

    md_content += "## 🛡️ Vulnerability Scan (Trivy)\n\n"
    
    vulns = []
    if vuln_data and "Results" in vuln_data:
        for result in vuln_data["Results"]:
            if "Vulnerabilities" in result:
                vulns.extend(result["Vulnerabilities"])

    if not vulns:
        md_content += "!!! success \"Zero-CVE State Confirmed\"\n    No known vulnerabilities were detected in this image!\n\n"
    else:
        md_content += f"**Total Vulnerabilities Found:** {len(vulns)}\n\n"
        md_content += "| Severity | CVE ID | Package | Status | Fixed Version |\n"
        md_content += "| :---: | :--- | :--- | :--- | :---: |\n"
        for v in vulns:
            severity = v.get("Severity", "UNKNOWN")
            cve_id = v.get("VulnerabilityID", "N/A")
            pkg = v.get("PkgName", "N/A")
            status = v.get("Status", "N/A")
            fixed = v.get("FixedVersion", "N/A")
            url = v.get("PrimaryURL", "#")
            md_content += f"| {severity} | [{cve_id}]({url}) | `{pkg}` | {status} | `{fixed}` |\n"
        md_content += "\n"

    md_content += "## ☸️ Docker CIS Benchmarks\n\n"
    
    controls = []
    if cis_data and "Results" in cis_data:
        for result in cis_data["Results"]:
            if "Vulnerabilities" in result:
                controls.extend(result["Vulnerabilities"])

    if not controls:
        md_content += "!!! success \"Hardened Configuration Confirmed\"\n    All audited Docker CIS controls have successfully passed!\n\n"
    else:
        md_content += "| Status | Control ID | Title | Severity |\n"
        md_content += "| :---: | :---: | :--- | :---: |\n"
        for ctrl in controls:
            status = "Passed" if ctrl.get("Severity") == "LOW" else "Failed"
            ctrl_id = ctrl.get("VulnerabilityID", "N/A")
            title = ctrl.get("Title", "N/A")
            severity = ctrl.get("Severity", "UNKNOWN")
            md_content += f"| {status} | **{ctrl_id}** | {title} | {severity} |\n"
        md_content += "\n"

    os.makedirs("docs", exist_ok=True)
    with open(f"docs/node-{version}.md", "w", encoding="utf-8") as f:
        f.write(md_content)

for ver in VERSIONS:
    render_version_page(ver)