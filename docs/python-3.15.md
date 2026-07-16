---
hide:
  - navigation
  - toc
---

# :fontawesome-brands-python: Python {{ python_3_15.prod.tags[0].split(':')[-1].split('-')[0] }}

<div class="hero-arch-badges" markdown>
<span class="arch-badge">:material-memory: linux/amd64</span>
<span class="arch-badge">:material-memory: linux/arm64</span>
</div>

{% set flavors = [
  ('dev', 'Development Builder (with Pip)', 'material-toolbox-outline', 'Full Developer Suite', 'Contains Python, Pip, Pipenv, and essential build utilities.'),
  ('prod', 'Production Runtime (Scratch)', 'material-shield-check', 'Hardened Minimal Runtime', 'Minimal, secure, minimal-compat runtime directly from scratch with no extra tools.')
] %}

{% for key, title, icon, policy_header, policy_text in flavors %}
=== ":{{ icon }}: {{ title }}"

    !!! success "{{ policy_header }}"
        **Security Policy:** {{ policy_text }}

    <div style="font-size: 1.35rem; font-weight: bold; margin-top: 25px; margin-bottom: 10px;">:material-docker: Artifact Registry</div>

    **Pull by Version Tag**
    ```bash
    docker pull {{ python_3_15[key].tags[0] }}
    ```

    **Pull by Floating Tag**
    ```bash
    docker pull {{ python_3_15[key].tags[1] }}
    ```

    ---

    <div style="font-size: 1.2rem; font-weight: bold; margin-top: 25px; margin-bottom: 15px; border-bottom: 1px solid var(--md-default-fg-color--lightest); padding-bottom: 8px;">:material-file-chart-outline: Security & Compliance Reports</div>

    === ":material-shield-search: Vulnerability Scan"

        {% set scan_data = python_3_15[key]['security'] %}
        {% set ns = namespace(vulns=[], critical=0, high=0, medium=0, low=0, pkg_count=0) %}

        {% if 'Results' in scan_data %}
          {% for res in scan_data['Results'] %}
            {% if 'Packages' in res and res['Packages'] %}
              {% set ns.pkg_count = ns.pkg_count + (res['Packages'] | length) %}
            {% endif %}
            {% if 'Vulnerabilities' in res and res['Vulnerabilities'] %}
              {% set ns.vulns = ns.vulns + res['Vulnerabilities'] %}
              {% for v in res['Vulnerabilities'] %}
                {% set sev = (v['Severity'] | upper) if 'Severity' in v else 'UNKNOWN' %}
                {% if sev == "CRITICAL" %}
                  {% set ns.critical = ns.critical + 1 %}
                {% elif sev == "HIGH" %}
                  {% set ns.high = ns.high + 1 %}
                {% elif sev == "MEDIUM" or sev == "MODERATE" %}
                  {% set ns.medium = ns.medium + 1 %}
                {% else %}
                  {% set ns.low = ns.low + 1 %}
                {% endif %}
              {% endfor %}
            {% endif %}
          {% endfor %}
        {% endif %}
        {% set total_vulns = ns.vulns | length %}

        <div class="grid cards" markdown>

        -   :material-shield-bug: **Total CVEs Found**
            <span style="color: {{ '#00c853' if total_vulns == 0 else '#d50000' }}; font-size: 2.2em; font-weight: 900;">{{ total_vulns }}</span>
            <br>*Detected in Image Layers*

        -   :material-package-variant-closed: **Packages Analyzed**
            <span style="font-size: 2.2em; font-weight: bold;">{{ ns.pkg_count }}</span>
            <br>*Verified Dependencies*

        -   :material-lightning-bolt: **Critical / High**
            <span style="color: {{ '#00c853' if (ns.critical + ns.high) == 0 else '#d50000' }}; font-size: 2.2em; font-weight: 900;">{{ ns.critical + ns.high }}</span>
            <br>*Immediate Action*

        -   :material-information: **Medium / Low**
            <span style="color: {{ '#00c853' if (ns.medium + ns.low) == 0 else '#ffb300' }}; font-size: 2.2em; font-weight: bold;">{{ ns.medium + ns.low }}</span>
            <br>*Risk Mitigation*

        </div>

        {% if total_vulns == 0 %}
        !!! success "Zero-CVE State Confirmed :material-check-decagram:"
            **Impeccable Security Posture:** No known vulnerabilities were detected in the `{{ ns.pkg_count }}` analyzed packages. 
        {% else %}
        !!! warning "Vulnerability Remediation Required :material-alert:"
            **{{ total_vulns }} security exception(s)** identified.

        #### :material-chart-donut: Severity Distribution

        ```vegalite
        {
          "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
          "data": {
            "values": [
              {"category": "Critical", "value": {{ ns.critical }}, "color": "#d32f2f"},
              {"category": "High", "value": {{ ns.high }}, "color": "#f57c00"},
              {"category": "Medium", "value": {{ ns.medium }}, "color": "#fbc02d"},
              {"category": "Low", "value": {{ ns.low }}, "color": "#1976d2"}
            ]
          },
          "transform": [ { "filter": "datum.value > 0" } ],
          "mark": {"type": "arc", "innerRadius": 60, "tooltip": true, "stroke": "#fff", "strokeWidth": 2},
          "encoding": {
            "theta": {"field": "value", "type": "quantitative"},
            "color": {
              "field": "category", "type": "nominal",
              "scale": {
                "domain": ["Critical", "High", "Medium", "Low"], 
                "range": ["#d32f2f", "#f57c00", "#fbc02d", "#1976d2"]
              }
            }
          },
          "width": 250, "height": 250
        }
        ```

        #### :material-table-eye: Forensic Vulnerability Log

        | Severity | CVE ID | Affected Package | Status |
        | :---: | :--- | :--- | :--- |
        {% for v in ns.vulns -%}

        | {% if v['Severity'] == 'CRITICAL' %}:material-lightning-bolt:{ .md-typeset__error }{% elif v['Severity'] == 'HIGH' %}:material-alert:{ style="color: #f57c00" }{% else %}:material-alert-circle:{ style="color: #fbc02d" }{% endif %} | [`{{ v['VulnerabilityID'] }}`]({{ v['PrimaryURL'] | default('#') }}) | `{{ v['PkgName'] }}` | {{ v['Status'] | title }} |
        {% endfor %}
        {% endif %}

        #### :material-package-variant-closed: Software Bill of Materials (SBOM)

        | Component Name | Version | License | Classification |
        | :--- | :--- | :--- | :--- |
        {% if 'Results' in scan_data -%}
          {% for res in scan_data['Results'] -%}
            {% if 'Packages' in res and res['Packages'] -%}
              {% for p in res['Packages'] -%}

        | **`{{ p['Name'] }}`** | `{{ p['Version'] }}` | {{ p['Licenses'] | join(', ') if p['Licenses'] is iterable and p['Licenses'] is not string else p['Licenses'] | default('N/A') }} | {% if res['Class'] == 'os-pkgs' %}:material-linux: System (Wolfi){% else %}:fontawesome-brands-python: Python Package{% endif %} |
              {% endfor -%}
            {% endif -%}
          {% endfor -%}
        {% endif -%}
<br>
    === ":fontawesome-brands-docker: Docker CIS"

        {% set cis_data = python_3_15[key]['docker-csi'] %}
        {% set cis_ns = namespace(vulnerabilities=[]) %}

        {% if 'Results' in cis_data %}
          {% for res in cis_data['Results'] %}
            {% if 'Vulnerabilities' in res %}
              {% set cis_ns.vulnerabilities = cis_ns.vulnerabilities + res['Vulnerabilities'] %}
            {% endif %}
          {% endfor %}
        {% endif %}

        {% set total_checks = cis_ns.vulnerabilities | length %}

        {% if total_checks == 0 %}
        !!! success "Hardened Configuration Confirmed :material-check-decagram:"
            All audited Docker CIS controls have successfully passed on this image!
        {% else %}
        !!! warning "CIS Compliance Review Required"
            **{{ total_checks }} CIS Check exceptions** detected.

        | Status | ID | Control Description | Severity |
        | :---: | :---: | :--- | :---: |
        {% for control in cis_ns.vulnerabilities -%}

        | :material-close-circle:{ style="color: #ff1744" } | **{{ control['VulnerabilityID'] }}** | {{ control['Title'] }} | {{ control['Severity'] }} |
        {% endfor %}
        {% endif %}

{% endfor %}