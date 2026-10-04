#!/usr/bin/env python3
"""Render conf/java-<version>.security for every published Java version.

The Dockerfile copies conf/java-${JAVA_VERSION}.security into the JDK/JRE, so re-run this
script whenever templates/java.security.j2 changes or a Java version is added:

    python openjdk/render_security.py
"""
import os

from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Java versions built by docker-bake.hcl (target "openjdk")
BUILT_VERSIONS = ("8", "17", "21", "25")


def main():
    template = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "templates"))).get_template("java.security.j2")
    for version in BUILT_VERSIONS:
        output = os.path.join(BASE_DIR, "conf", f"java-{version}.security")
        with open(output, "w", encoding="utf-8") as f:
            f.write(template.render(version=version))
        print(f"Rendered {os.path.relpath(output, BASE_DIR)}")


if __name__ == "__main__":
    main()
