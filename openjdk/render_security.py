#!/usr/bin/env python3
"""Render conf/java-<version>.security for every published Java version.

The Dockerfile copies conf/java-${JAVA_VERSION}.security into the JDK/JRE, so re-run
this script whenever templates/java.security.j2 or config/context.json changes:

    python openjdk/render_security.py
"""
import json
import os

from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKIPPED_KEYS = ("java", "images", "wolfi_packages")
# Versions built by docker-bake.hcl (context.json also tracks versions we do not publish)
BUILT_VERSIONS = ("8", "17", "21", "25")


def main():
    with open(os.path.join(BASE_DIR, "config", "context.json"), encoding="utf-8") as f:
        context = json.load(f)

    template = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "templates"))).get_template("java.security.j2")
    shared = {k: v for k, v in context.items() if k not in SKIPPED_KEYS}
    shared.update(context.get("images", {}))
    shared.update(context.get("wolfi_packages", {}))

    for version in BUILT_VERSIONS:
        version_data = context["java"][version]
        output = os.path.join(BASE_DIR, "conf", f"java-{version}.security")
        with open(output, "w", encoding="utf-8") as f:
            f.write(template.render(**shared, **version_data))
        print(f"Rendered {os.path.relpath(output, BASE_DIR)}")


if __name__ == "__main__":
    main()
