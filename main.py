import json
import os

repo_of_registry = "ghcr.io/taha2samy-3/node"
python_repo_of_registry = "ghcr.io/taha2samy-3/python"

def loadjson(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {}

def load_node_version(version):
    return {
        "dev": {
            "security": loadjson(f"reports/{version}-dev-vuln.json"),
            "docker-csi": loadjson(f"reports/{version}-dev-cis.json"),
            "tags": [f"{repo_of_registry}:{version}-dev", f"{repo_of_registry}:v{version}-dev"]
        },
        "prod": {
            "security": loadjson(f"reports/{version}-prod-vuln.json"),
            "docker-csi": loadjson(f"reports/{version}-prod-cis.json"),
            "tags": [f"{repo_of_registry}:{version}", f"{repo_of_registry}:v{version}"]
        }
    }

def load_python_version(version):
    return {
        "dev": {
            "security": loadjson(f"reports/{version}-dev-vuln.json"),
            "docker-csi": loadjson(f"reports/{version}-dev-cis.json"),
            "tags": [f"{python_repo_of_registry}:{version}-dev", f"{python_repo_of_registry}:v{version}-dev"]
        },
        "prod": {
            "security": loadjson(f"reports/{version}-prod-vuln.json"),
            "docker-csi": loadjson(f"reports/{version}-prod-cis.json"),
            "tags": [f"{python_repo_of_registry}:{version}", f"{python_repo_of_registry}:v{version}"]
        }
    }

def define_env(env):
    env.variables.update({
        "repo_of_registry": repo_of_registry,
        "node_22": load_node_version("22"),
        "node_24": load_node_version("24"),
        "python_3_10": load_python_version("3.10"),
        "python_3_11": load_python_version("3.11"),
        "python_3_12": load_python_version("3.12"),
        "python_3_13": load_python_version("3.13"),
        "python_3_14": load_python_version("3.14")
    })