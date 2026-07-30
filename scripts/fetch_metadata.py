#!/usr/bin/env python3
import os
import sys
import re
import json
import argparse
import urllib.request
import urllib.error
import subprocess

try:
    import yaml
except ImportError:
    print("⚠️ Installing PyYAML...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml"])
    import yaml

def get_gh_token():
    try:
        token = subprocess.check_output(["gh", "auth", "token"]).decode().strip()
        print("🔑 GitHub CLI Token resolved successfully.")
        return token
    except Exception:
        print("ℹ️ GitHub CLI Token not found. Using anonymous request.")
        return None

def get_gh_package_version_url(registry, repo, tag, root_digest, gh_token=None):
    try:
        parts = repo.split('/')
        if len(parts) < 2:
            return f"https://github.com/{repo}"
        owner, package_name = parts[0], parts[1]
        
        url = f"https://api.github.com/users/{owner}/packages/container/{package_name}/versions?per_page=100"
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if gh_token:
            req.add_header("Authorization", f"Bearer {gh_token}")
            
        with urllib.request.urlopen(req) as resp:
            versions = json.loads(resp.read().decode())
        
        for v in versions:
            v_name = v.get("name", "")
            tags = v.get("metadata", {}).get("container", {}).get("tags", [])
            
            if (root_digest and root_digest == v_name) or (tag in tags):
                return v.get("html_url")
    except Exception:
        pass
    return f"https://github.com/{repo}/pkgs/container/{package_name}"

def get_image_metadata(tag_url, gh_token=None):
    match = re.match(r'^(?:https://)?([^/]+)/([^:]+):(.+)$', tag_url)
    if not match:
        return "N/A", "N/A", "N/A"
    registry, repo, tag = match.groups()
    try:
        token_url = f"https://{registry}/token?service={registry}&scope=repository:{repo}:pull"
        req_token = urllib.request.Request(token_url)
        
        if gh_token:
            import base64
            username = repo.split('/')[0]
            auth_str = base64.b64encode(f"{username}:{gh_token}".encode()).decode()
            req_token.add_header("Authorization", f"Basic {auth_str}")
            
        with urllib.request.urlopen(req_token) as resp:
            token_data = json.loads(resp.read().decode())
            token = token_data.get("token")
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.docker.distribution.manifest.v2+json, "
                      "application/vnd.oci.image.manifest.v1+json, "
                      "application/vnd.docker.distribution.manifest.list.v2+json, "
                      "application/vnd.oci.image.index.v1+json"
        }
        
        manifest_url = f"https://{registry}/v2/{repo}/manifests/{tag}"
        req = urllib.request.Request(manifest_url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            root_digest = resp.headers.get("Docker-Content-Digest", "N/A")
            manifest = json.loads(resp.read().decode())
        
        if "manifests" in manifest:
            digest = manifest["manifests"][0]["digest"]
            digest_url = f"https://{registry}/v2/{repo}/manifests/{digest}"
            req_digest = urllib.request.Request(digest_url, headers=headers)
            with urllib.request.urlopen(req_digest) as resp_digest:
                manifest = json.loads(resp_digest.read().decode())
                
        layers = manifest.get("layers", [])
        total_bytes = sum(layer.get("size", 0) for layer in layers)
        
        provenance_url = get_gh_package_version_url(registry, repo, tag, root_digest, gh_token)
        
        if total_bytes == 0:
            return "N/A", root_digest, provenance_url
        size_mb = total_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB", root_digest, provenance_url
    except Exception as e:
        print(f"⚠️ Error fetching metadata for {tag_url}: {e}")
        return "N/A", "N/A", "N/A"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="runtimes.yaml")
    parser.add_argument("-o", "--output-dir", default="reports")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        print(f"❌ Error: Config file not found at {args.config}")
        sys.exit(1)

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    gh_token = get_gh_token()
    metadata_map = {}
    runtimes = config.get("runtimes", [])
    
    print("\n🚀 Starting metadata resolution process...")
    for runtime in runtimes:
        print(f"\n📦 Processing Runtime: {runtime.get('title')}")
        for version_info in runtime.get("versions", []):
            for flavor in version_info.get("flavors", []):
                for tag in flavor.get("tags", []):
                    if tag not in metadata_map:
                        print(f"   ↳ ⏳ Fetching metadata for: {tag} ...", end="", flush=True)
                        size_str, root_digest, provenance_url = get_image_metadata(tag, gh_token)
                        metadata_map[tag] = {
                            "size": size_str,
                            "digest": root_digest,
                            "provenance_url": provenance_url,
                            "compression": "zstd",
                            "compression_level": 3
                        }
                        print(f"\r   ↳ ✅ Done: {tag} ({size_str} | {root_digest[:18]}... | {provenance_url[:30]}...)")

    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, "config.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata_map, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Metadata process complete! File saved at: {output_path}\n")

if __name__ == "__main__":
    main()