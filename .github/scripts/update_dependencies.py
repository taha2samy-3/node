#!/usr/bin/env python3
"""Keep every pinned version in docker-bake.hcl up to date, one pull request per group.

The pins and where their updates come from are declared in .github/dependencies.yml.
FIPS 140-3 certified modules are listed there under `certified` and are never touched here;
their lifecycle is tracked by cmvp_watch.py.

  update_dependencies.py --dry-run          print the updates each group would get
  update_dependencies.py --pull-request     open / refresh / close one PR per group

Each group's pull request is refreshed in place (force-pushed branch automation/deps-<group>),
recreated if it was closed while updates are still pending, and closed once main already
has every version.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from datetime import datetime, timezone

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan_images  # noqa: E402  (fingerprints tell which images an update rebuilds)

CONFIG_FILE = ".github/dependencies.yml"
BAKE_FILE = "docker-bake.hcl"
RUNNER_IMAGE = "cgr.dev/chainguard/wolfi-base:latest"
PR_LABEL = "dependencies"
BRANCH_PREFIX = "automation/deps-"
# Branches used by earlier versions of this automation; their PRs are closed as superseded
LEGACY_BRANCHES = ["automation/base-image-locks"]
LEGACY_BRANCH_PREFIX = "chore/security-updates-"

ADOPTIUM_API = "https://api.adoptium.net/v3/assets/latest/{feature}/hotspot?os=linux&image_type={kind}&architecture={arch}&vendor=eclipse"
ADOPTIUM_ARCH = {"AMD64": "x64", "ARM64": "aarch64"}
MAVEN = "https://repo1.maven.org/maven2"

CHANGE_TYPES = {
    "major": ("🔴", "major"),
    "minor": ("🟠", "minor"),
    "patch": ("🟢", "patch"),
    "rebuild": ("⚪", "rebuild"),
    "digest": ("🔵", "digest"),
}
CHANGE_ORDER = ["major", "minor", "patch", "rebuild", "digest"]
APK_VERSION_RE = re.compile(r"^(?P<upstream>[\d.]+)(?P<suffix>[^-]*)-r(?P<revision>\d+)$")


def run(cmd, check=True, capture=False):
    return subprocess.run(cmd, check=check, capture_output=capture, text=True)


def http(url, binary=False):
    headers = {"User-Agent": "secure-runtimes-dependency-updater"}
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as resp:
        data = resp.read()
    return data if binary else data.decode()


def numbers(version):
    return [int(n) for n in re.findall(r"\d+", version)]


def same_line(candidate, current, depth=2):
    """True when candidate keeps current's first `depth` version numbers (e.g. 3.5.x)."""
    return numbers(candidate)[:depth] == numbers(current)[:depth]


# ==========================================
# docker-bake.hcl variables
# ==========================================
def variable_pattern(name):
    return re.compile(r'(variable\s+"' + re.escape(name) + r'"\s*\{\s*default\s*=\s*")([^"\r\n]*)(")')


def read_variables(content):
    return {m.group(1): m.group(2) for m in re.finditer(r'variable\s+"([A-Z0-9_]+)"\s*\{\s*default\s*=\s*"([^"\r\n]*)"', content)}


def write_variable(content, name, value):
    pattern = variable_pattern(name)
    if not pattern.search(content):
        sys.exit(f"{BAKE_FILE}: variable {name} not found")
    return pattern.sub(lambda m: m.group(1) + value + m.group(3), content, count=1)


# ==========================================
# Change classification
# ==========================================
def classify(old, new, source):
    if source == "image":
        return "digest"
    old_apk, new_apk = APK_VERSION_RE.match(old), APK_VERSION_RE.match(new)
    if old_apk and new_apk and old_apk.group("upstream") == new_apk.group("upstream") and old_apk.group("suffix") == new_apk.group("suffix"):
        return "rebuild"
    old_n, new_n = numbers(old), numbers(new)
    if old_n and old_n[0] >= 1000:
        # Date-based versions (ca-certificates 20260413, tzdata 2026b) are data refreshes, not API changes
        return "patch"
    for index, kind in enumerate(("major", "minor", "patch")):
        if old_n[index:index + 1] != new_n[index:index + 1]:
            return kind
    return "patch"


def short(value):
    return "sha256:" + value.split("@sha256:", 1)[1][:12] if "@sha256:" in value else value


# ==========================================
# Resolvers: each returns {variable: new value} plus display info
# ==========================================
def resolve_wolfi(packages):
    """Newest version of each exact Wolfi package name (apk policy lists versions oldest first)."""
    script = "apk update >/dev/null 2>&1; for p in " + " ".join(sorted(set(packages.values()))) + '; do echo "@@ $p"; apk policy "$p"; done'
    out = run(["docker", "run", "--rm", "--pull", "always", RUNNER_IMAGE, "sh", "-c", script], capture=True).stdout
    latest, current = {}, None
    for line in out.splitlines():
        if line.startswith("@@ "):
            current = line[3:].strip()
        elif current and re.match(r"^\s{2}\S+:$", line):
            latest[current] = line.strip()[:-1]
    missing = sorted(set(packages.values()) - set(latest))
    if missing:
        sys.exit(f"Wolfi packages not found: {', '.join(missing)}")
    return {var: latest[pkg] for var, pkg in packages.items()}


def resolve_image(ref):
    res = run(["docker", "buildx", "imagetools", "inspect", ref, "--format", "{{json .Manifest}}"], capture=True)
    digest = json.loads(res.stdout)["digest"]
    repository = ref.split("@", 1)[0]
    if ":" in repository.rsplit("/", 1)[-1]:
        repository = repository.rsplit(":", 1)[0]
    return f"{repository}@{digest}"


def resolve_openssl(dep, current):
    releases = json.loads(http("https://api.github.com/repos/openssl/openssl/releases?per_page=100"))
    versions = [r["tag_name"].removeprefix("openssl-") for r in releases if not r["prerelease"] and r["tag_name"].startswith("openssl-")]
    candidates = sorted((v for v in versions if same_line(v, current) and re.fullmatch(r"[\d.]+", v)), key=numbers)
    newest = candidates[-1] if candidates else current
    updates = {dep["variable"]: newest}
    if newest != current:
        sha = http(f"https://github.com/openssl/openssl/releases/download/openssl-{newest}/openssl-{newest}.tar.gz.sha256").split()[0]
        if not re.fullmatch(r"[0-9a-f]{64}", sha):
            sys.exit(f"openssl {newest}: unexpected checksum file content")
        updates[dep["sha256_variable"]] = sha
    return updates, f"https://github.com/openssl/openssl/releases/tag/openssl-{newest}"


def resolve_adoptium(dep):
    prefix, updates, release = dep["prefix"], {}, None
    for kind in ("jdk", "jre"):
        for arch, api_arch in ADOPTIUM_ARCH.items():
            asset = json.loads(http(ADOPTIUM_API.format(feature=dep["feature"], kind=kind, arch=api_arch)))[0]
            package = asset["binary"]["package"]
            updates[f"{prefix}_{kind.upper()}_{arch}_URL"] = package["link"]
            updates[f"{prefix}_{kind.upper()}_{arch}_SHA"] = package["checksum"]
            version = asset["version"]["openjdk_version"]
            if release and release != version:
                sys.exit(f"Temurin {dep['feature']}: assets disagree on the version ({release} vs {version})")
            release, release_name = version, asset["release_name"]
    updates[f"{prefix}_FULL_VERSION"] = release
    return updates, f"https://adoptium.net/temurin/release-notes/?version={release_name}"


def resolve_maven(dep, current):
    group, artifact = dep["artifact"].split(":")
    base = f"{MAVEN}/{group.replace('.', '/')}/{artifact}"
    versions = re.findall(r"<version>([^<]+)</version>", http(f"{base}/maven-metadata.xml"))
    candidates = sorted((v for v in versions if re.fullmatch(r"[\d.]+", v) and same_line(v, current)), key=numbers)
    newest = candidates[-1] if candidates else current
    jar = f"{base}/{newest}/{artifact}-{newest}.jar"
    updates = {dep["variable"]: newest}
    if newest != current:
        jar_bytes = http(jar, binary=True)
        sha = hashlib.sha256(jar_bytes).hexdigest()
        published = http(f"{jar}.sha256").split()[0]
        if published != sha:
            sys.exit(f"{artifact} {newest}: downloaded jar does not match the published SHA-256")
        updates[dep["url_variable"]] = jar
        updates[dep["sha256_variable"]] = sha
    return updates, f"{base}/{newest}/"


def resolve_github_release(dep):
    release = json.loads(http(f"https://api.github.com/repos/{dep['repo']}/releases/latest"))
    tag = release["tag_name"]
    sums = http(f"https://github.com/{dep['repo']}/releases/download/{tag}/{dep['checksum_file']}")
    by_file = {line.split()[1].lstrip("*"): line.split()[0] for line in sums.splitlines() if len(line.split()) == 2}
    updates = {dep["variable"]: tag}
    for variable, filename in dep["checksums"].items():
        if filename not in by_file:
            sys.exit(f"{dep['repo']} {tag}: {filename} missing from {dep['checksum_file']}")
        updates[variable] = by_file[filename]
    return updates, release["html_url"]


def resolve_group(deps, variables):
    """All updates for one group: [{name, variable, old, new, change, link, extra}]."""
    updates = []
    wolfi = {}
    for dep in deps:
        if dep["source"] == "wolfi":
            wolfi.update(dep["packages"])
    if wolfi:
        print(f"  resolving {len(wolfi)} Wolfi packages")
        for var, new in resolve_wolfi(wolfi).items():
            if variables[var] != new:
                updates.append({"name": wolfi[var], "variable": var, "old": variables[var], "new": new, "source": "wolfi",
                                "link": f"https://github.com/wolfi-dev/os/blob/main/{wolfi[var]}.yaml", "extra": {}})

    for dep in deps:
        source = dep["source"]
        if source == "wolfi":
            continue
        print(f"  resolving {dep['name']} ({source})")
        if source == "image":
            values, link = {dep["variable"]: resolve_image(dep["ref"])}, dep["ref"]
        elif source == "openssl":
            values, link = resolve_openssl(dep, variables[dep["variable"]])
        elif source == "adoptium":
            values, link = resolve_adoptium(dep)
        elif source == "maven":
            values, link = resolve_maven(dep, variables[dep["variable"]])
        elif source == "github-release":
            values, link = resolve_github_release(dep)
        else:
            sys.exit(f"{dep['name']}: unknown source {source}")

        main_var = dep.get("variable") or f"{dep['prefix']}_FULL_VERSION"
        changed = {k: v for k, v in values.items() if variables.get(k) != v}
        if changed:
            updates.append({
                "name": dep["name"], "variable": main_var, "old": variables[main_var], "new": values[main_var],
                "source": source, "link": link, "extra": {k: v for k, v in changed.items() if k != main_var},
            })
    for update in updates:
        update["change"] = classify(update["old"], update["new"], update["source"])
    return sorted(updates, key=lambda u: (CHANGE_ORDER.index(u["change"]), u["name"]))


PIN_LIKE = re.compile(r"(_VER|_VERSION|_SHA|_SHA256|_URL|_IMAGE)$")


def managed_variables(dep):
    names = set(dep.get("packages", {})) | set(dep.get("checksums", {}))
    names |= {dep[k] for k in ("variable", "sha256_variable", "url_variable") if dep.get(k)}
    if dep["source"] == "adoptium":
        prefix = dep["prefix"]
        names.add(f"{prefix}_FULL_VERSION")
        names |= {f"{prefix}_{kind}_{arch}_{part}" for kind in ("JDK", "JRE") for arch in ADOPTIUM_ARCH for part in ("URL", "SHA")}
    return names


def check_coverage(config, variables):
    """Every pin in docker-bake.hcl must have an update rule, be a certified module, or say why it is not pinned."""
    certified = {v for c in config["certified"] for v in c["variables"]}
    managed = set().union(*(managed_variables(d) for d in config["dependencies"]))
    overlap = managed & certified
    if overlap:
        sys.exit(f"{CONFIG_FILE}: {sorted(overlap)} belong to a certified module and cannot be auto-updated")
    unknown = sorted(n for n in managed | certified if n not in variables)
    uncovered = sorted(n for n in variables if PIN_LIKE.search(n) and n not in managed | certified | set(config.get("not_pinned", {})))
    if unknown or uncovered:
        sys.exit(f"{CONFIG_FILE} is out of sync with {BAKE_FILE}:\n"
                 + (f"  declared but missing from {BAKE_FILE}: {unknown}\n" if unknown else "")
                 + (f"  pins without an update rule: {uncovered}\n" if uncovered else ""))
    print(f"Coverage: {len(managed)} pins updated automatically, {len(certified)} certified, {len(config.get('not_pinned', {}))} not pinned")


def apply(content, updates):
    for update in updates:
        content = write_variable(content, update["variable"], update["new"])
        for var, value in update["extra"].items():
            content = write_variable(content, var, value)
    return content


def affected_images(before, after):
    """Image tags whose build fingerprint changes when docker-bake.hcl goes from before to after."""
    fingerprints = []
    for content in (before, after):
        with tempfile.NamedTemporaryFile("w", suffix=".hcl", dir=".", delete=False) as f:
            f.write(content)
        try:
            targets = json.loads(run(["docker", "buildx", "bake", "-f", f.name, "--print"], capture=True).stdout)["target"]
            fingerprints.append((targets, plan_images.compute_fingerprints(targets)[0]))
        finally:
            os.remove(f.name)
    (_, old), (targets, new) = fingerprints
    return sorted(targets[t]["tags"][0] for t in new if old.get(t) != new[t])


# ==========================================
# Pull request content
# ==========================================
def title(group_title, updates):
    if len(updates) == 1:
        u = updates[0]
        return f"chore(deps): bump {u['name']} from {short(u['old'])} to {short(u['new'])}"
    return f"chore(deps): update {len(updates)} {group_title} dependencies"


def commit_message(group_title, updates):
    lines = [title(group_title, updates), ""]
    lines += [f"- {u['name']} ({u['variable']}): {short(u['old'])} -> {short(u['new'])} [{u['change']}]" for u in updates]
    return "\n".join(lines)


def render_body(group, group_title, updates, images, certified, base, base_sha):
    marker = f"<!-- automation:deps-{group} -->"
    counts = {k: sum(1 for u in updates if u["change"] == k) for k in CHANGE_ORDER}
    overview = " · ".join(f"{CHANGE_TYPES[k][0]} {counts[k]} {CHANGE_TYPES[k][1]}" for k in CHANGE_ORDER if counts[k])
    risky = [u["name"] for u in updates if u["change"] in ("major", "minor")]
    alert = (
        f"> [!WARNING]\n> Includes minor/major version bumps ({', '.join(f'`{n}`' for n in risky)}). Review the release notes before merging."
        if risky else
        "> [!NOTE]\n> Only patch, rebuild or digest updates: security and bug-fix releases within the pinned release lines."
    )
    rows = ["| Dependency | Variable | From | To | Type |", "| :--- | :--- | :--- | :--- | :---: |"]
    for u in updates:
        icon, label = CHANGE_TYPES[u["change"]]
        rows.append(f"| [{u['name']}]({u['link']}) | `{u['variable']}` | `{short(u['old'])}` | `{short(u['new'])}` | {icon} {label} |")
    extra = [f"- `{var}` → `{short(value)}`" for u in updates for var, value in u["extra"].items()]
    fips_note = ""
    if certified:
        names = ", ".join(f"{c['name']} {c['version']} (certificate #{c['certificate']})" for c in certified)
        fips_note = f"\n### FIPS 140-3 modules\n\nNot changed by this PR: {names}. Certified modules are only changed by hand when NIST lists a new certificate.\n"
    image_list = "\n".join(f"- `{tag}`" for tag in images) or "- none"
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    repository, run_id = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GITHUB_RUN_ID")
    run_row = f"\n| Workflow run | [#{run_id}]({server}/{repository}/actions/runs/{run_id}) |" if repository and run_id else ""
    checksum_section = ("\n<details>\n<summary>Updated URLs and checksums</summary>\n\n" + "\n".join(extra) + "\n\n</details>\n") if extra else ""

    return f"""{marker}
## 📦 {group_title} dependency updates

**Overview:** {overview}

{alert}

### Updates

{chr(10).join(rows)}
{checksum_section}{fips_note}
### Images rebuilt after merging ({len(images)})

{image_list}

Only these images are rebuilt, re-attested and rescanned; every other image keeps its current build.

<details>
<summary>About this pull request</summary>

<br>

- Maintained by `.github/workflows/daily-image-update.yml` from `.github/dependencies.yml` and **refreshed in place** on every run; manual commits to `{BRANCH_PREFIX}{group}` are overwritten.
- **Closed automatically** once `{base}` has every version, and **recreated** if closed while updates are still pending.

| Field | Value |
| :--- | :--- |
| Refreshed | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} |
| Base | `{base}` @ `{base_sha}` |{run_row}

</details>
"""


# ==========================================
# Pull request lifecycle
# ==========================================
def remote_branch_exists(branch):
    return run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch], check=False, capture=True).returncode == 0


def find_open_pr(branch, base):
    res = run(["gh", "pr", "list", "--head", branch, "--base", base, "--state", "open", "--json", "number,url", "--limit", "1"], capture=True)
    prs = json.loads(res.stdout)
    return prs[0] if prs else None


def remote_tree_matches_head(branch):
    if not remote_branch_exists(branch):
        return False
    run(["git", "fetch", "--depth=1", "origin", branch], capture=True)
    return run(["git", "rev-parse", "FETCH_HEAD^{tree}"], capture=True).stdout == run(["git", "rev-parse", "HEAD^{tree}"], capture=True).stdout


def sync_pull_request(branch, base, pr_title, body, message):
    run(["git", "checkout", "-B", branch])
    run(["git", "add", BAKE_FILE])
    run(["git", "commit", "-m", message])
    open_pr = find_open_pr(branch, base)
    if open_pr:
        if remote_tree_matches_head(branch):
            print(f"  PR #{open_pr['number']} is already up to date: {open_pr['url']}")
        else:
            run(["git", "push", "--force", "origin", branch])
            run(["gh", "pr", "edit", str(open_pr["number"]), "--title", pr_title, "--body", body])
            print(f"  refreshed PR #{open_pr['number']}: {open_pr['url']}")
        return
    if remote_branch_exists(branch):
        # A closed or merged PR may still own the branch: start over from a clean branch
        run(["git", "push", "origin", "--delete", branch], check=False)
    run(["git", "push", "origin", branch])
    run(["gh", "label", "create", PR_LABEL, "--color", "0366d6", "--description", "Pull requests that update a dependency file"], check=False, capture=True)
    url = run(["gh", "pr", "create", "--title", pr_title, "--body", body, "--base", base, "--head", branch, "--label", PR_LABEL], capture=True).stdout.strip()
    print(f"  created PR: {url}")


def close_pr(branch, base, comment):
    open_pr = find_open_pr(branch, base)
    if open_pr:
        print(f"  closing PR #{open_pr['number']} ({branch})")
        run(["gh", "pr", "close", str(open_pr["number"]), "--delete-branch", "--comment", comment], check=False)


def close_legacy(base):
    res = run(["gh", "pr", "list", "--state", "open", "--json", "number,headRefName", "--limit", "200"], capture=True)
    for pr in json.loads(res.stdout):
        branch = pr["headRefName"]
        if branch in LEGACY_BRANCHES or branch.startswith(LEGACY_BRANCH_PREFIX):
            close_pr(branch, base, "Superseded: dependency updates now come as one pull request per image family (`automation/deps-*`).")


# ==========================================
# Main
# ==========================================
def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--pull-request", action="store_true")
    parser.add_argument("--base", default="main")
    parser.add_argument("--group", action="append", help="limit to these groups")
    args = parser.parse_args()

    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    with open(BAKE_FILE, encoding="utf-8") as f:
        original = f.read()
    variables = read_variables(original)

    check_coverage(config, variables)

    if args.pull_request:
        run(["git", "config", "user.name", "github-actions[bot]"])
        run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"])
        base_sha = run(["git", "rev-parse", "--short", "HEAD"], capture=True).stdout.strip()

    failures = []
    for group, group_title in config["groups"].items():
        if args.group and group not in args.group:
            continue
        print(f"\n== {group_title}")
        deps = [d for d in config["dependencies"] if d["group"] == group]
        try:
            updates = resolve_group(deps, variables)
        except Exception as e:  # one unreachable source must not block the other groups
            print(f"::error::{group}: {e}")
            failures.append(group)
            continue

        branch = f"{BRANCH_PREFIX}{group}"
        if not updates:
            print("  up to date")
            if args.pull_request:
                close_pr(branch, args.base, f"Every {group_title} dependency on `{args.base}` is already up to date.")
            continue

        updated = apply(original, updates)
        images = affected_images(original, updated)
        for u in updates:
            print(f"  {u['name']:28} {short(u['old']):>34} -> {short(u['new']):34} [{u['change']}]")
        print(f"  rebuilds {len(images)} images")

        if args.pull_request:
            certified = [c for c in config["certified"] if any(i.split('/')[-1].split(':')[0] in c["used_by"] for i in images)]
            body = render_body(group, group_title, updates, images, certified, args.base, base_sha)
            with open(BAKE_FILE, "w", encoding="utf-8") as f:
                f.write(updated)
            try:
                sync_pull_request(branch, args.base, title(group_title, updates), body, commit_message(group_title, updates))
            finally:
                run(["git", "checkout", "-q", args.base])
                run(["git", "checkout", "-q", "--", BAKE_FILE])

    if args.pull_request:
        close_legacy(args.base)
    if failures:
        sys.exit(f"Could not resolve updates for: {', '.join(failures)}")


if __name__ == "__main__":
    main()
