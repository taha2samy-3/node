import runtimesData from '../../runtimes.yaml';

export interface FipsInfo {
  module: string;
  // NIST CMVP certificate of the module
  certificate?: number;
  enforcement: string;
  // Command that proves FIPS mode, with {tag} standing for the image reference
  verify: string;
}

export interface Flavor {
  id: string;
  name: string;
  policy_header: string;
  policy_text: string;
  tags: string[];
  reports: {
    vuln: string;
    cis: string;
    sbom: string;
  };
}

export interface RuntimeVersion {
  version: string;
  flavors: Flavor[];
}

export interface Runtime {
  id: string;
  title: string;
  icon: string;
  fips?: FipsInfo;
  architectures: string[];
  versions: RuntimeVersion[];
}

export const OWNER = 'taha2samy-3';
export const REPO_URL = `https://github.com/${OWNER}/node`;
export const ATTESTATIONS_URL = `${REPO_URL}/attestations`;

export const runtimes: Runtime[] = (runtimesData as { runtimes: Runtime[] }).runtimes;

export function findRuntime(id: string | undefined): Runtime | undefined {
  return runtimes.find((r) => r.id === id);
}

export function findVersion(runtime: Runtime | undefined, version: string | undefined): RuntimeVersion | undefined {
  return runtime?.versions.find((v) => v.version === version);
}

export function runtimePath(runtime: Runtime, version: RuntimeVersion | string): string {
  return `/runtime/${runtime.id}/${typeof version === 'string' ? version : version.version}`;
}

// "./../reports/openjdk-21-prod-vuln.json" -> "openjdk-21-prod"
export function reportBase(flavor: Flavor): string {
  return flavor.reports.vuln.split('/').pop()!.replace(/-vuln\.json$/, '');
}

// "ghcr.io/taha2samy-3/node-fips:22-dev" -> "node-fips"
export function packageName(tag: string): string {
  return tag.replace(/^[^/]+\//, '').split(':')[0].split('/').pop() ?? tag;
}

export function packageUrl(tag: string): string {
  return `${REPO_URL}/pkgs/container/${packageName(tag)}`;
}

export const FLAVOR_LABELS: Record<string, string> = {
  dev: 'Development',
  standard: 'Standard',
  prod: 'Production',
};

export const allFlavors = runtimes.flatMap((runtime) =>
  runtime.versions.flatMap((version) => version.flavors.map((flavor) => ({ runtime, version, flavor }))),
);
