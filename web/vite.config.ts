import { defineConfig, type Plugin } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import yaml from '@rollup/plugin-yaml';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const REPORTS_DIR = fileURLToPath(new URL('../reports', import.meta.url));
const SUMMARY_ID = 'virtual:report-summaries';
const SEVERITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'];
const VULN_FIELDS = ['VulnerabilityID', 'PkgName', 'InstalledVersion', 'FixedVersion', 'Status', 'Severity', 'Title', 'PrimaryURL'];

type Vuln = Record<string, unknown> & { Severity?: string; FixedVersion?: string };
type TrivyReport = { CreatedAt?: string; Results?: { Target?: string; Vulnerabilities?: Vuln[] | null }[] | null };

function severityOf(value?: string) {
  const upper = (value ?? '').toUpperCase();
  if (upper === 'MODERATE') return 'MEDIUM';
  return SEVERITIES.includes(upper) ? upper : 'UNKNOWN';
}

/**
 * Trivy reports carry full CVE descriptions, references and CVSS data. The dashboard bundles only
 * a per-image count index (virtual:report-summaries) and slims each vulnerability report to the
 * fields its table shows; the slimmed report is loaded when the tab opens.
 */
function trivyReports(): Plugin {
  return {
    name: 'trivy-reports',
    // Must see the raw JSON, before Vite's JSON plugin turns it into a module
    enforce: 'pre',
    resolveId(id) {
      return id === SUMMARY_ID ? `\0${SUMMARY_ID}` : undefined;
    },
    load(id) {
      if (id !== `\0${SUMMARY_ID}`) return undefined;
      const summaries: Record<string, unknown> = {};
      if (fs.existsSync(REPORTS_DIR)) {
        this.addWatchFile(REPORTS_DIR);
        for (const file of fs.readdirSync(REPORTS_DIR).filter((f) => f.endsWith('-vuln.json'))) {
          const report: TrivyReport = JSON.parse(fs.readFileSync(path.join(REPORTS_DIR, file), 'utf8'));
          const vulns = (report.Results ?? []).flatMap((r) => r.Vulnerabilities ?? []);
          const counts = Object.fromEntries(SEVERITIES.map((s) => [s, 0]));
          vulns.forEach((v) => counts[severityOf(v.Severity)]++);
          summaries[file.replace(/-vuln\.json$/, '')] = {
            total: vulns.length,
            fixable: vulns.filter((v) => v.FixedVersion).length,
            counts,
            scannedAt: report.CreatedAt,
          };
        }
      }
      return `export default ${JSON.stringify(summaries)};`;
    },
    transform(code, id) {
      if (!/[\\/]reports[\\/][^\\/]+-vuln\.json$/.test(id)) return undefined;
      const report: TrivyReport = JSON.parse(code);
      const slim = {
        CreatedAt: report.CreatedAt,
        Results: (report.Results ?? []).map((r) => ({
          Target: r.Target,
          Vulnerabilities: (r.Vulnerabilities ?? []).map((v) => Object.fromEntries(VULN_FIELDS.filter((k) => v[k] !== undefined).map((k) => [k, v[k]]))),
        })),
      };
      return { code: JSON.stringify(slim), map: null };
    },
  };
}

export default defineConfig({
  base: './',
  plugins: [
    trivyReports(),
    yaml(),
    tailwindcss()
  ],
  define: {
    __BUILD_DATE__: JSON.stringify(new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }))
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    allowedHosts: 'all'
  }
});
