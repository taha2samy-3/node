export interface RuntimeFlavor {
  id: string;
  name: string;
  policy_header: string;
  policy_text: string;
  tags: string[];
  attestation_url?: string;
  reports: {
    vuln: string;
    cis: string;
    sbom: string;
  };
}

export interface RuntimeVersion {
  version: string;
  flavors: RuntimeFlavor[];
}

export interface RuntimeConfig {
  id: string;
  title: string;
  icon: string;
  // Runtime enforces a FIPS 140-3 validated cryptographic module
  fips?: boolean;
  architectures: string[];
  versions: RuntimeVersion[];
}

export interface RuntimesData {
  runtimes: RuntimeConfig[];
}
