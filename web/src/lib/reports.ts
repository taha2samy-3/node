import reportSummaries from 'virtual:report-summaries';
import { allFlavors, reportBase, type Flavor, type Runtime, type RuntimeVersion } from './catalog';

// Reports live in <repo>/reports (written by the dashboard workflow). Only per-image vulnerability
// counts (built by the trivy-reports plugin in vite.config.ts) and image metadata are bundled;
// full vulnerability, CIS and SBOM reports load when their tab is opened.
const REPORT_DIR = '../../../reports/';
const vulnLoaders = import.meta.glob('../../../reports/*-vuln.json', { import: 'default' }) as Record<string, () => Promise<TrivyReport>>;
const metaFiles = import.meta.glob('../../../reports/config.json', { eager: true, import: 'default' }) as Record<string, Record<string, ImageMeta>>;
const cisLoaders = import.meta.glob('../../../reports/*-cis.json', { import: 'default' }) as Record<string, () => Promise<ComplianceReport>>;
const sbomLoaders = import.meta.glob('../../../reports/*-sbom.json', { import: 'default' }) as Record<string, () => Promise<CycloneDx>>;

// ==========================================
// Report formats (the parts the dashboard reads)
// ==========================================
export interface TrivyVulnerability {
  VulnerabilityID: string;
  PkgName: string;
  InstalledVersion?: string;
  FixedVersion?: string;
  Status?: string;
  Severity?: string;
  Title?: string;
  PrimaryURL?: string;
}

export interface TrivyReport {
  CreatedAt?: string;
  Results?: { Target?: string; Vulnerabilities?: TrivyVulnerability[] | null }[] | null;
}

// Trivy writes the summary format by default (SummaryControls); --report all adds per-check Results
export interface ComplianceReport {
  SummaryControls?: { ID: string; Name: string; Severity?: string; TotalFail?: number }[] | null;
  Results?: {
    ID: string;
    Name: string;
    Severity?: string;
    Results?: {
      Misconfigurations?: { ID?: string; Title?: string; Message?: string; Status?: string }[] | null;
      Vulnerabilities?: unknown[] | null;
      Secrets?: { Title?: string }[] | null;
    }[] | null;
  }[] | null;
}

export interface CycloneDx {
  components?: {
    name: string;
    version?: string;
    type?: string;
    purl?: string;
    licenses?: { license?: { id?: string; name?: string }; expression?: string }[];
  }[];
}

export interface ImageMeta {
  size?: string;
  digest?: string;
}

// ==========================================
// Image metadata (config.json)
// ==========================================
const imageMeta: Record<string, ImageMeta> = metaFiles[`${REPORT_DIR}config.json`] ?? {};

export function getImageMeta(tag: string): ImageMeta {
  const meta = imageMeta[tag] ?? {};
  const known = (value?: string) => (value && value !== 'N/A' ? value : undefined);
  return { size: known(meta.size), digest: known(meta.digest) };
}

// ==========================================
// Vulnerabilities
// ==========================================
export const SEVERITIES = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'] as const;
export type Severity = (typeof SEVERITIES)[number];

export interface Vulnerability {
  id: string;
  pkg: string;
  installed?: string;
  fixed?: string;
  status?: string;
  severity: Severity;
  title?: string;
  url?: string;
}

export interface VulnSummary {
  total: number;
  fixable: number;
  counts: Record<Severity, number>;
  scannedAt?: string;
}

const summaries = reportSummaries as Record<string, VulnSummary>;

function toSeverity(value?: string): Severity {
  const upper = (value ?? '').toUpperCase();
  if (upper === 'MODERATE') return 'MEDIUM';
  return (SEVERITIES as readonly string[]).includes(upper) ? (upper as Severity) : 'UNKNOWN';
}

/** Vulnerability counts for a flavor, or null when the image has not been scanned yet. */
export function vulnSummary(flavor: Flavor): VulnSummary | null {
  return summaries[reportBase(flavor)] ?? null;
}

/** Full vulnerability list, most severe first. */
export function loadVulns(flavor: Flavor): Promise<Vulnerability[]> | null {
  const loader = vulnLoaders[`${REPORT_DIR}${reportBase(flavor)}-vuln.json`];
  if (!loader) return null;
  return loader().then((report) => {
    const items: Vulnerability[] = (report.Results ?? []).flatMap((result) =>
      (result.Vulnerabilities ?? []).map((v) => ({
        id: v.VulnerabilityID,
        pkg: v.PkgName,
        installed: v.InstalledVersion,
        fixed: v.FixedVersion || undefined,
        status: v.Status,
        severity: toSeverity(v.Severity),
        title: v.Title,
        url: v.PrimaryURL,
      })),
    );
    return items.sort((a, b) => SEVERITIES.indexOf(a.severity) - SEVERITIES.indexOf(b.severity) || a.id.localeCompare(b.id));
  });
}

// ==========================================
// Status roll-ups for navigation and overview
// ==========================================
export type ScanStatus = 'clean' | 'low' | 'high' | 'unscanned';

export function flavorStatus(flavor: Flavor): ScanStatus {
  const summary = vulnSummary(flavor);
  if (!summary) return 'unscanned';
  if (summary.total === 0) return 'clean';
  return summary.counts.CRITICAL + summary.counts.HIGH > 0 ? 'high' : 'low';
}

const STATUS_RANK: ScanStatus[] = ['high', 'low', 'unscanned', 'clean'];

/** Worst status across the given flavors. */
export function worstStatus(flavors: Flavor[]): ScanStatus {
  const statuses = flavors.map(flavorStatus);
  return STATUS_RANK.find((s) => statuses.includes(s)) ?? 'unscanned';
}

export function versionStatus(version: RuntimeVersion): ScanStatus {
  return worstStatus(version.flavors);
}

export function runtimeCounts(runtime?: Runtime) {
  const flavors = runtime ? runtime.versions.flatMap((v) => v.flavors) : allFlavors.map((f) => f.flavor);
  const summaries = flavors.map(vulnSummary);
  return {
    images: flavors.length,
    scanned: summaries.filter(Boolean).length,
    clean: summaries.filter((s) => s && s.total === 0).length,
    vulnerabilities: summaries.reduce((sum, s) => sum + (s?.total ?? 0), 0),
  };
}

// ==========================================
// CIS benchmark (Trivy docker-cis compliance report)
// ==========================================
export interface CisControl {
  id: string;
  name: string;
  severity: Severity;
  status: 'pass' | 'fail' | 'manual';
  findings: string[];
}

export function cisControls(report: ComplianceReport): CisControl[] {
  if (report.SummaryControls) {
    // TotalFail is only present for automated controls; its absence means manual review
    return report.SummaryControls.map((control) => ({
      id: control.ID,
      name: control.Name.replace(/\s*\(Manual\)$/, ''),
      severity: toSeverity(control.Severity),
      status: control.TotalFail === undefined ? 'manual' : control.TotalFail > 0 ? 'fail' : 'pass',
      findings: control.TotalFail ? [`${control.TotalFail} failed ${control.TotalFail === 1 ? 'check' : 'checks'}`] : [],
    }));
  }
  return (report.Results ?? []).map((control) => {
    const checks = control.Results ?? [];
    const findings = checks.flatMap((check) => [
      ...(check.Misconfigurations ?? []).filter((m) => m.Status === 'FAIL').map((m) => m.Title || m.Message || m.ID || 'Failed check'),
      ...(check.Vulnerabilities ?? []).map(() => 'Vulnerability found'),
      ...(check.Secrets ?? []).map((s) => s.Title || 'Secret found'),
    ]);
    const status = findings.length ? 'fail' : checks.length ? 'pass' : 'manual';
    return { id: control.ID, name: control.Name, severity: toSeverity(control.Severity), status, findings };
  });
}

// ==========================================
// SBOM (CycloneDX)
// ==========================================
export interface Component {
  name: string;
  version: string;
  type: string;
  licenses: string[];
  purl?: string;
}

export function sbomComponents(report: CycloneDx): Component[] {
  return (report.components ?? [])
    .map((c) => ({
      name: c.name,
      version: c.version ?? '',
      type: c.type ?? 'library',
      purl: c.purl,
      licenses: (c.licenses ?? []).map((l) => l.license?.id ?? l.license?.name ?? l.expression ?? '').filter(Boolean),
    }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

// ==========================================
// Lazy loading
// ==========================================
export function loadCis(flavor: Flavor): Promise<ComplianceReport> | null {
  return cisLoaders[`${REPORT_DIR}${reportBase(flavor)}-cis.json`]?.() ?? null;
}

export function loadSbom(flavor: Flavor): Promise<CycloneDx> | null {
  return sbomLoaders[`${REPORT_DIR}${reportBase(flavor)}-sbom.json`]?.() ?? null;
}

/** URL of a report file as published next to the site on GitHub Pages. */
export function reportUrl(flavor: Flavor, kind: 'vuln' | 'cis' | 'sbom'): string {
  return `./reports/${reportBase(flavor)}-${kind}.json`;
}
