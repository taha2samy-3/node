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
const testLoaders = import.meta.glob('../../../reports/*-tests-*.json', { import: 'default' }) as Record<string, () => Promise<TestRun>>;
const benchLoaders = import.meta.glob('../../../reports/*-bench-*.json', { import: 'default' }) as Record<string, () => Promise<BenchRun>>;

const certificateFiles = import.meta.glob('../../../reports/fips-certificates.json', { eager: true, import: 'default' }) as Record<string, CertificateData>;

export const ARCHES = ['amd64', 'arm64'] as const;
export type Arch = (typeof ARCHES)[number];

/** Report file base for an architecture: amd64 keeps the catalog name, arm64 adds a suffix. */
function archBase(flavor: Flavor, arch: Arch): string {
  return arch === 'amd64' ? reportBase(flavor) : `${reportBase(flavor)}-${arch}`;
}

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
  platforms?: Partial<Record<Arch, { size?: string; digest?: string }>>;
}

// NIST CMVP certificate data written by .github/scripts/cmvp_watch.py
export interface Certificate {
  certificate: number;
  url: string;
  module: string | null;
  standard: string | null;
  status: string | null;
  sunset: string | null;
  versions: string[];
  pinned_version: string;
  newer: { certificate: number; date: string; url: string }[];
  alerts: string[];
}

interface CertificateData {
  checked_at: string;
  modules: Certificate[];
}

export function getCertificate(number?: number): (Certificate & { checkedAt: string }) | undefined {
  const data = certificateFiles[`${REPORT_DIR}fips-certificates.json`];
  const cert = data?.modules.find((m) => m.certificate === number);
  return cert && { ...cert, checkedAt: data.checked_at };
}

// Benchmark results written by .github/scripts/run_benchmarks.py
export interface BenchRun {
  unit: string;
  arch: Arch;
  image: string;
  baseline: { name: string; image: string };
  cpu: string;
  runs: number;
  seconds: number;
  ran_at: string;
  results: { name: string; metric: string; fips: number | null; baseline: number | null }[];
}

// FIPS test results written by .github/scripts/fips_tests.py
export interface TestResult {
  name: string;
  classname: string;
  // xfail: a documented limitation of the certified module (strict xfail in the suite)
  outcome: 'passed' | 'failed' | 'xfail' | 'skipped';
  duration: number;
  message: string;
}

export interface TestRun {
  image: string;
  flavor: string;
  arch: Arch;
  suite: string;
  ran_at: string;
  summary: { passed: number; failed: number; xfail?: number; skipped: number; total: number; duration: number };
  tests: TestResult[];
}

// ==========================================
// Image metadata (config.json)
// ==========================================
const imageMeta: Record<string, ImageMeta> = metaFiles[`${REPORT_DIR}config.json`] ?? {};

const known = (value?: string) => (value && value !== 'N/A' ? value : undefined);

/** Size and digest of one architecture's image, plus the multi-platform index digest. */
export function getImageMeta(tag: string, arch: Arch = 'amd64'): { size?: string; digest?: string; indexDigest?: string } {
  const meta = imageMeta[tag] ?? {};
  const platform = meta.platforms?.[arch];
  return {
    size: known(platform?.size) ?? (arch === 'amd64' ? known(meta.size) : undefined),
    digest: known(platform?.digest),
    indexDigest: known(meta.digest),
  };
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

/** Vulnerability counts for a flavor, or null when that architecture has not been scanned yet. */
export function vulnSummary(flavor: Flavor, arch: Arch = 'amd64'): VulnSummary | null {
  return summaries[archBase(flavor, arch)] ?? null;
}

/** Full vulnerability list, most severe first. */
export function loadVulns(flavor: Flavor, arch: Arch = 'amd64'): Promise<Vulnerability[]> | null {
  const loader = vulnLoaders[`${REPORT_DIR}${archBase(flavor, arch)}-vuln.json`];
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

function summaryStatus(summary: VulnSummary): ScanStatus {
  if (summary.total === 0) return 'clean';
  return summary.counts.CRITICAL + summary.counts.HIGH > 0 ? 'high' : 'low';
}

const STATUS_RANK: ScanStatus[] = ['high', 'low', 'unscanned', 'clean'];

/** Worst result across the architectures that were scanned. */
export function flavorStatus(flavor: Flavor, arch?: Arch): ScanStatus {
  const scanned = (arch ? [arch] : ARCHES).map((a) => vulnSummary(flavor, a)).filter((s): s is VulnSummary => !!s);
  if (!scanned.length) return 'unscanned';
  const statuses = scanned.map(summaryStatus);
  return STATUS_RANK.find((s) => statuses.includes(s)) ?? 'clean';
}

/** Worst status across the given flavors. */
export function worstStatus(flavors: Flavor[]): ScanStatus {
  const statuses = flavors.map((f) => flavorStatus(f));
  return STATUS_RANK.find((s) => statuses.includes(s)) ?? 'unscanned';
}

export function versionStatus(version: RuntimeVersion): ScanStatus {
  return worstStatus(version.flavors);
}

export function runtimeCounts(runtime?: Runtime) {
  const flavors = runtime ? runtime.versions.flatMap((v) => v.flavors) : allFlavors.map((f) => f.flavor);
  const statuses = flavors.map((f) => flavorStatus(f));
  return {
    images: flavors.length,
    scanned: statuses.filter((s) => s !== 'unscanned').length,
    clean: statuses.filter((s) => s === 'clean').length,
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
export function loadCis(flavor: Flavor, arch: Arch = 'amd64'): Promise<ComplianceReport> | null {
  return cisLoaders[`${REPORT_DIR}${archBase(flavor, arch)}-cis.json`]?.() ?? null;
}

export function loadSbom(flavor: Flavor, arch: Arch = 'amd64'): Promise<CycloneDx> | null {
  return sbomLoaders[`${REPORT_DIR}${archBase(flavor, arch)}-sbom.json`]?.() ?? null;
}

export function loadTests(flavor: Flavor, arch: Arch): Promise<TestRun> | null {
  return testLoaders[`${REPORT_DIR}${reportBase(flavor)}-tests-${arch}.json`]?.() ?? null;
}

/** Architectures with published FIPS test results for a flavor (known at build time). */
export function testedArches(flavor: Flavor): Arch[] {
  return ARCHES.filter((arch) => `${REPORT_DIR}${reportBase(flavor)}-tests-${arch}.json` in testLoaders);
}

/** Benchmarks are measured on the standard flavor of a runtime version. */
export function loadBench(standard: Flavor, arch: Arch): Promise<BenchRun> | null {
  return benchLoaders[`${REPORT_DIR}${reportBase(standard)}-bench-${arch}.json`]?.() ?? null;
}

/** URL of a report file as published next to the site on GitHub Pages. */
export function reportUrl(flavor: Flavor, kind: 'vuln' | 'cis' | 'sbom', arch: Arch = 'amd64'): string {
  return `./reports/${archBase(flavor, arch)}-${kind}.json`;
}
