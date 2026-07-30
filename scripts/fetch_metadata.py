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

def get_compressed_image_size(tag_url, gh_token=None):
    match = re.match(r'^(?:https://)?([^/]+)/([^:]+):(.+)$', tag_url)
    if not match:
        return None
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
            manifest = json.loads(resp.read().decode())
        
        if "manifests" in manifest:
            digest = manifest["manifests"][0]["digest"]
            digest_url = f"https://{registry}/v2/{repo}/manifests/{digest}"
            req_digest = urllib.request.Request(digest_url, headers=headers)
            with urllib.request.urlopen(req_digest) as resp_digest:
                manifest = json.loads(resp_digest.read().decode())
                
        layers = manifest.get("layers", [])
        total_bytes = sum(layer.get("size", 0) for layer in layers)
        if total_bytes == 0:
            return "N/A"
        size_mb = total_bytes / (1024 * 1024)
        return f"{size_mb:.1f} MB"
    except Exception as e:
        print(f"⚠️ Error fetching size for {tag_url}: {e}")
        return "N/A"

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
                        size_str = get_compressed_image_size(tag, gh_token) or "N/A"
                        metadata_map[tag] = {
                            "size": size_str,
                            "compression": "zstd",
                            "compression_level": 3
                        }
                        print(f"\r   ↳ ✅ Done: {tag} ({size_str})")

    os.makedirs(args.output_dir, exist_ok=True)
    output_path = os.path.join(args.output_dir, "config.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata_map, f, indent=2, ensure_ascii=False)
    
    print(f"\n🎉 Metadata process complete! File saved at: {output_path}\n")

if __name__ == "__main__":
    main()