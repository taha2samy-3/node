import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


PR_BRANCH = "automation/base-image-locks"
PR_LABEL = "dependencies"
LEGACY_BRANCH_PREFIX = "chore/security-updates-"
PR_MARKER = "<!-- automation:base-image-locks -->"

BAKE_FILE = "docker-bake.hcl"
RUNNER_IMAGE = "cgr.dev/chainguard/wolfi-base:latest"
WOLFI_RECIPE_URL = "https://github.com/wolfi-dev/os/blob/main/{package}.yaml"

NODE_NOTES = "https://github.com/nodejs/node/releases/tag/v{version}"
PYTHON_NOTES = "https://www.python.org/downloads/release/python-{version_nodots}/"
BUN_NOTES = "https://github.com/oven-sh/bun/releases/tag/bun-v{version}"

IMAGE_LOCKS = {
    "BASE_IMAGE": {
        "ref": "cgr.dev/chainguard/wolfi-base:latest",
        "name": "wolfi-base",
        "runtime": "Base image",
        "notes": "https://images.chainguard.dev/directory/image/wolfi-base/versions",
    },
}

PACKAGE_LOCKS = {
    "NODE_20_FULL_VERSION": {"package": "nodejs-20", "runtime": "Node.js 20", "images": ["node:20", "node:20-dev"], "notes": NODE_NOTES},
    "NODE_22_FULL_VERSION": {"package": "nodejs-22", "runtime": "Node.js 22", "images": ["node:22", "node:22-dev"], "notes": NODE_NOTES},
    "NODE_24_FULL_VERSION": {"package": "nodejs-24", "runtime": "Node.js 24", "images": ["node:24", "node:24-dev"], "notes": NODE_NOTES},
    "PYTHON_3_10_FULL_VERSION": {"package": "python-3.10", "runtime": "Python 3.10", "images": ["python:3.10", "python:3.10-dev"], "notes": PYTHON_NOTES},
    "PYTHON_3_11_FULL_VERSION": {"package": "python-3.11", "runtime": "Python 3.11", "images": ["python:3.11", "python:3.11-dev"], "notes": PYTHON_NOTES},
    "PYTHON_3_12_FULL_VERSION": {"package": "python-3.12", "runtime": "Python 3.12", "images": ["python:3.12", "python:3.12-dev"], "notes": PYTHON_NOTES},
    "PYTHON_3_13_FULL_VERSION": {"package": "python-3.13", "runtime": "Python 3.13", "images": ["python:3.13", "python:3.13-dev"], "notes": PYTHON_NOTES},
    "PYTHON_3_14_FULL_VERSION": {"package": "python-3.14", "runtime": "Python 3.14", "images": ["python:3.14", "python:3.14-dev"], "notes": PYTHON_NOTES},
    "BUN_1_FULL_VERSION": {"package": "bun", "runtime": "Bun 1", "images": ["bun:1", "bun:1-dev"], "notes": BUN_NOTES},
}

TOTAL_IMAGES = sum(len(spec["images"]) for spec in PACKAGE_LOCKS.values())

APK_LINE_RE = re.compile(r"^(?P<name>.+)-(?P<version>\d[^-\s]*-r\d+)$")
APK_VERSION_RE = re.compile(r"^(?P<upstream>[\d.]+)(?P<suffix>[^-]*)-r(?P<revision>\d+)$")

CHANGE_TYPES = {
    "major": ("🔴", "major"),
    "minor": ("🟠", "minor"),
    "patch": ("🟢", "patch"),
    "rebuild": ("⚪", "rebuild"),
    "digest": ("🔵", "digest"),
}
CHANGE_ORDER = ["major", "minor", "patch", "rebuild", "digest"]


def run(cmd, check=True, capture=False):
    return subprocess.run(cmd, check=check, capture_output=capture, text=True)


def variable_pattern(var_name):
    return re.compile(r'(variable\s+"' + re.escape(var_name) + r'"\s*\{\s*default\s*=\s*")([^"\r\n]+)(")')


# ==========================================
# Resolution
# ==========================================
def get_image_digest(image_name):
    try:
        res = run(["docker", "buildx", "imagetools", "inspect", image_name, "--format", "{{json .Manifest}}"], capture=True)
        digest = json.loads(res.stdout)["digest"]
        if not digest.startswith("sha256:"):
            raise ValueError(f"Unexpected digest: {digest}")
        repository = image_name.split("@", 1)[0]
        if ":" in repository.rsplit("/", 1)[-1]:
            repository = repository.rsplit(":", 1)[0]
        return f"{repository}@{digest}"
    except Exception as e:
        print(f"Error fetching digest for {image_name}: {e}")
        sys.exit(1)


def get_wolfi_package_versions(runner_image, package_names):
    script = "apk update > /dev/null && apk search -x " + " ".join(package_names)
    try:
        res = run(["docker", "run", "--rm", "--pull", "always", runner_image, "sh", "-c", script], capture=True)
    except subprocess.CalledProcessError as e:
        print(f"Error querying Wolfi packages: {e.stderr}")
        sys.exit(1)

    versions = {}
    for line in res.stdout.splitlines():
        match = APK_LINE_RE.match(line.strip())
        if match:
            versions[match.group("name")] = match.group("version")

    missing = [name for name in package_names if name not in versions]
    if missing:
        print(f"Error: packages not found in Wolfi index: {', '.join(missing)}")
        sys.exit(1)
    return versions


# ==========================================
# Change classification
# ==========================================
def parse_apk_version(value):
    match = APK_VERSION_RE.match(value)
    if not match:
        return None
    parts = [int(p) for p in match.group("upstream").split(".") if p]
    return {
        "upstream": match.group("upstream"),
        "parts": (parts + [0, 0, 0])[:3],
        "suffix": match.group("suffix"),
        "revision": int(match.group("revision")),
    }


def classify_change(old, new):
    old_v, new_v = parse_apk_version(old), parse_apk_version(new)
    if not old_v or not new_v:
        return "patch"
    for index, kind in enumerate(("major", "minor", "patch")):
        if old_v["parts"][index] != new_v["parts"][index]:
            return kind
    if old_v["suffix"] != new_v["suffix"]:
        return "patch"
    return "rebuild"


def short_value(value):
    if "@sha256:" in value:
        return "sha256:" + value.split("@sha256:", 1)[1][:12]
    return value


def release_notes_url(template, version):
    parsed = parse_apk_version(version)
    upstream = parsed["upstream"] if parsed else version
    return template.format(version=upstream, version_nodots=upstream.replace(".", ""))


# ==========================================
# Pull request content
# ==========================================
def ordered_updates(updates):
    return sorted(updates.items(), key=lambda item: (CHANGE_ORDER.index(item[1]["change"]), item[1]["runtime"]))


def build_title(updates):
    if len(updates) == 1:
        info = next(iter(updates.values()))
        return f"chore(deps): bump {info['name']} from {short_value(info['old'])} to {short_value(info['value'])}"
    return f"chore(deps): bump {len(updates)} runtime dependencies in {BAKE_FILE}"


def build_commit_message(updates):
    lines = [build_title(updates), ""]
    for var_name, info in ordered_updates(updates):
        lines.append(f"- {info['name']} ({var_name}): {short_value(info['old'])} -> {short_value(info['value'])} [{info['change']}]")
    return "\n".join(lines)


def build_overview(updates):
    counts = {kind: 0 for kind in CHANGE_ORDER}
    for info in updates.values():
        counts[info["change"]] += 1
    badges = [f"{CHANGE_TYPES[k][0]} {counts[k]} {CHANGE_TYPES[k][1]}" for k in CHANGE_ORDER if counts[k]]
    return " · ".join(badges)


def build_alert(updates):
    risky = [info for info in updates.values() if info["change"] in ("major", "minor")]
    if risky:
        names = ", ".join(f"`{info['name']}`" for info in risky)
        return (
            "> [!WARNING]\n"
            f"> This update includes **{len(risky)} minor/major version bump(s)** ({names}). "
            "Review the upstream release notes below for behavioural changes before merging."
        )
    return (
        "> [!NOTE]\n"
        "> Only patch-level, rebuild or digest updates are included. These are typically security and bug-fix releases "
        "and are considered low risk."
    )


def build_updates_table(updates):
    rows = [
        "| Dependency | Runtime | From | To | Type | Affected images |",
        "| :--- | :--- | :--- | :--- | :---: | :--- |",
    ]
    for _, info in ordered_updates(updates):
        icon, label = CHANGE_TYPES[info["change"]]
        images = " ".join(f"`{tag}`" for tag in info["images"]) if info["images"] else f"All {TOTAL_IMAGES} images"
        rows.append(
            f"| **{info['name']}** | {info['runtime']} | `{short_value(info['old'])}` | `{short_value(info['value'])}` "
            f"| {icon} {label} | {images} |"
        )
    return "\n".join(rows)


def build_references(updates):
    lines = []
    for var_name, info in ordered_updates(updates):
        if info["change"] == "digest":
            lines.append(
                f"- **{info['name']}** · [Image versions]({info['notes']})\n"
                f"  - From: `{info['old']}`\n"
                f"  - To: `{info['value']}`"
            )
        else:
            links = [
                f"[Release notes]({release_notes_url(info['notes'], info['value'])})",
                f"[Wolfi package recipe]({WOLFI_RECIPE_URL.format(package=info['name'])})",
            ]
            lines.append(f"- **{info['name']} {info['value']}** (`{var_name}`) · " + " · ".join(links))
    return "\n".join(lines)


def build_run_metadata(base, base_sha):
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    rows = [
        "| Field | Value |",
        "| :--- | :--- |",
        f"| Refreshed | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} |",
        f"| Base | `{base}` @ `{base_sha}` |",
        f"| Package index | Wolfi (`{RUNNER_IMAGE}`) |",
    ]
    if repository and run_id:
        rows.append(f"| Workflow run | [#{run_id}]({server}/{repository}/actions/runs/{run_id}) |")
    return "\n".join(rows)


def render_pr_body(updates, base, base_sha):
    count = len(updates)
    noun = "dependency" if count == 1 else "dependencies"
    repository = os.environ.get("GITHUB_REPOSITORY")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    bake_link = f"[`{BAKE_FILE}`]({server}/{repository}/blob/{PR_BRANCH}/{BAKE_FILE})" if repository else f"`{BAKE_FILE}`"
    return f"""{PR_MARKER}
## 📦 Runtime dependency updates

Bumps **{count}** pinned {noun} in {bake_link} to the latest releases published in the [Wolfi](https://github.com/wolfi-dev/os) package repository and the Chainguard registry.

**Overview:** {build_overview(updates)}

{build_alert(updates)}

### Updates

{build_updates_table(updates)}

### Release notes & sources

{build_references(updates)}

### After merging

1. **Build and Push Images** rebuilds the affected images for `linux/amd64` and `linux/arm64`, signs build provenance attestations and uploads SBOMs to the dependency graph.
2. **Generate Security Dashboard and Deploy** rescans the published images with Trivy and refreshes the dashboard.

<details>
<summary>About this pull request</summary>

<br>

- This PR is maintained automatically by `.github/workflows/daily-image-update.yml` and is **refreshed in place** on every run; the branch `{PR_BRANCH}` is force-pushed, so manual commits to it will be overwritten.
- It is **closed automatically** once `{base}` already contains every locked version.
- If you close it without merging, it will be **recreated** on the next run while updates are still pending.

**Change types:** 🔴 major · 🟠 minor · 🟢 patch · ⚪ rebuild (same upstream version, new Wolfi package revision) · 🔵 digest (base image refresh)

{build_run_metadata(base, base_sha)}

</details>
"""


# ==========================================
# Pull request lifecycle
# ==========================================
def remote_branch_exists(branch):
    return run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch], check=False, capture=True).returncode == 0


def delete_remote_branch(branch):
    if remote_branch_exists(branch):
        print(f"Deleting remote branch {branch}")
        run(["git", "push", "origin", "--delete", branch], check=False)


def find_open_pr(branch, base):
    res = run(
        ["gh", "pr", "list", "--head", branch, "--base", base, "--state", "open", "--json", "number,url", "--limit", "1"],
        capture=True,
    )
    prs = json.loads(res.stdout)
    return prs[0] if prs else None


def remote_tree_matches_head(branch):
    if not remote_branch_exists(branch):
        return False
    run(["git", "fetch", "--depth=1", "origin", branch], capture=True)
    remote_tree = run(["git", "rev-parse", "FETCH_HEAD^{tree}"], capture=True).stdout.strip()
    local_tree = run(["git", "rev-parse", "HEAD^{tree}"], capture=True).stdout.strip()
    return remote_tree == local_tree


def ensure_label():
    run(
        ["gh", "label", "create", PR_LABEL, "--color", "0366d6", "--description", "Pull requests that update a dependency file"],
        check=False, capture=True,
    )


def close_legacy_pull_requests(superseded_by=None):
    res = run(["gh", "pr", "list", "--state", "open", "--json", "number,headRefName", "--limit", "200"], capture=True)
    if superseded_by:
        comment = f"Superseded by #{superseded_by}, which now tracks all runtime dependency updates in a single pull request."
    else:
        comment = "Closing: all runtime dependencies are already up to date. Future updates are tracked in a single pull request."
    for pr in json.loads(res.stdout):
        if pr["headRefName"].startswith(LEGACY_BRANCH_PREFIX):
            print(f"Closing legacy PR #{pr['number']} ({pr['headRefName']})")
            run(["gh", "pr", "close", str(pr["number"]), "--comment", comment, "--delete-branch"], check=False)

    res = run(["git", "ls-remote", "--heads", "origin", f"{LEGACY_BRANCH_PREFIX}*"], capture=True)
    leftovers = [line.split("refs/heads/", 1)[1] for line in res.stdout.splitlines() if "refs/heads/" in line]
    if leftovers:
        print(f"Deleting {len(leftovers)} leftover legacy branches")
        run(["git", "push", "origin", "--delete", *leftovers], check=False)


def sync_pull_request(file_path, updates, base):
    """Dependabot-style single PR: refresh it if open, recreate it if closed."""
    try:
        base_sha = run(["git", "rev-parse", "--short", "HEAD"], capture=True).stdout.strip()
        title = build_title(updates)
        body = render_pr_body(updates, base, base_sha)

        run(["git", "config", "user.name", "github-actions[bot]"])
        run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])

        run(["git", "checkout", "-B", PR_BRANCH])
        run(["git", "add", file_path])
        run(["git", "commit", "-m", build_commit_message(updates)])

        open_pr = find_open_pr(PR_BRANCH, base)

        if open_pr:
            pr_number = open_pr["number"]
            if remote_tree_matches_head(PR_BRANCH):
                print(f"PR #{pr_number} is already up to date: {open_pr['url']}")
            else:
                print(f"Refreshing existing PR #{pr_number}")
                run(["git", "push", "--force", "origin", PR_BRANCH])
                run(["gh", "pr", "edit", str(pr_number), "--title", title, "--body", body])
                print(f"Updated Pull Request: {open_pr['url']}")
        else:
            # A closed or merged PR may still own the branch; start over from a clean branch.
            delete_remote_branch(PR_BRANCH)
            run(["git", "push", "origin", PR_BRANCH])
            ensure_label()
            res = run(
                ["gh", "pr", "create", "--title", title, "--body", body, "--base", base, "--head", PR_BRANCH, "--label", PR_LABEL],
                capture=True,
            )
            url = res.stdout.strip().splitlines()[-1]
            print(f"Created Pull Request: {url}")
            pr_number = url.rstrip("/").rsplit("/", 1)[-1]

        close_legacy_pull_requests(superseded_by=pr_number)
    except subprocess.CalledProcessError as e:
        print(f"Failed to automate Git/PR process: {e}\n{e.stderr or ''}")
        sys.exit(1)


def close_stale_pull_request(base):
    """Nothing left to update: close the open PR, like Dependabot does when a dependency is already current."""
    try:
        open_pr = find_open_pr(PR_BRANCH, base)
        if open_pr:
            print(f"Closing PR #{open_pr['number']}: {base} is already up to date")
            run([
                "gh", "pr", "close", str(open_pr["number"]), "--delete-branch",
                "--comment", f"All runtime dependencies on `{base}` are already locked to their latest versions, so this pull request is no longer needed.",
            ])
        close_legacy_pull_requests()
    except subprocess.CalledProcessError as e:
        print(f"Failed to clean up pull requests: {e}\n{e.stderr or ''}")
        sys.exit(1)


# ==========================================
# Lock file update
# ==========================================
def apply_update(content, var_name, new_value, file_path):
    pattern = variable_pattern(var_name)
    match = pattern.search(content)
    if not match:
        print(f" -> WARNING: variable {var_name} not found in {file_path}, skipping.")
        return content, None
    old_value = match.group(2)
    if old_value == new_value:
        return content, None
    print(f" -> Updating {var_name}: {old_value} -> {new_value}")
    content = pattern.sub(lambda m: m.group(1) + new_value + m.group(3), content, count=1)
    return content, old_value


def lock_dependencies(file_path, runner_image, enable_pr, base):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    updates_made = {}

    for var_name, spec in IMAGE_LOCKS.items():
        print(f"Resolving Docker Image: {spec['ref']}")
        locked_value = get_image_digest(spec["ref"])
        content, old_value = apply_update(content, var_name, locked_value, file_path)
        if old_value is not None:
            updates_made[var_name] = {
                "name": spec["name"], "runtime": spec["runtime"], "images": [], "notes": spec["notes"],
                "old": old_value, "value": locked_value, "change": "digest",
            }

    package_names = [spec["package"] for spec in PACKAGE_LOCKS.values()]
    print(f"Resolving Wolfi Packages: {', '.join(package_names)}")
    package_versions = get_wolfi_package_versions(runner_image, package_names)
    for var_name, spec in PACKAGE_LOCKS.items():
        locked_value = package_versions[spec["package"]]
        content, old_value = apply_update(content, var_name, locked_value, file_path)
        if old_value is not None:
            updates_made[var_name] = {
                "name": spec["package"], "runtime": spec["runtime"], "images": spec["images"], "notes": spec["notes"],
                "old": old_value, "value": locked_value, "change": classify_change(old_value, locked_value),
            }

    if not updates_made:
        print("All dependencies are already locked to the latest versions. No changes detected.")
        if enable_pr:
            close_stale_pull_request(base)
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated {file_path} successfully.")

    if enable_pr:
        print("Changes detected. Syncing Pull Request...")
        sync_pull_request(file_path, updates_made, base)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pull-request", action="store_true")
    parser.add_argument("--base", default="main")
    args = parser.parse_args()

    lock_dependencies(BAKE_FILE, RUNNER_IMAGE, args.pull_request, args.base)


if __name__ == "__main__":
    main()
