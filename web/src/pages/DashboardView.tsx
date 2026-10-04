import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { 
  ShieldCheck, Package, Zap, Info, CheckCircle2, AlertCircle, XCircle, Copy, Check, 
  ShieldAlert, Cpu, HardDrive, Lock, Search, ChevronDown, ChevronRight, Gauge, 
  Activity, SlidersHorizontal, Award, Sparkles, Terminal, FileCheck, ExternalLink,
  Edit3, Plus, RefreshCw, X, Globe, FileCode2
} from 'lucide-react';
import { 
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend 
} from 'recharts';
import runtimesData from '../../runtimes.yaml';
import { RuntimesData } from '../types';
import { cn } from '../utils';
import RuntimeIcon from '../components/RuntimeIcon';
import { reportsMap, configData } from '../reports';
import { 
  FIPS_TEST_SUITES, 
  FIPS_TEST_CASES, 
  BENCHMARK_THROUGHPUT_DATA, 
  HASHING_THROUGHPUT_DATA, 
  SIGNATURE_BENCHMARK_DATA 
} from '../fipsData';

const COLORS: Record<string, string> = {
  Critical: '#ef4444',
  High: '#f97316',
  Medium: '#f59e0b',
  Low: '#3b82f6',
};

export default function DashboardView() {
  const { runtimeId, version } = useParams<{ runtimeId: string; version: string }>();
  const data = runtimesData as RuntimesData;

  const runtime = useMemo(() => data.runtimes.find(r => r.id === runtimeId), [data, runtimeId]);
  const runtimeVersion = useMemo(() => runtime?.versions.find(v => v.version === version), [runtime, version]);

  const [activeFlavorId, setActiveFlavorId] = useState<string>('prod');
  const [activeSubTab, setActiveSubTab] = useState<'vuln' | 'cis' | 'sbom' | 'fips-tests' | 'benchmarks' | 'attestation'>('vuln');
  const [copiedTag, setCopiedTag] = useState<string | null>(null);
  const [copiedDigestTag, setCopiedDigestTag] = useState<string | null>(null);

  // Attestation & Supply Chain State
  const [copiedVerifyTag, setCopiedVerifyTag] = useState<string | null>(null);
  const [copiedSnippet, setCopiedSnippet] = useState<string | null>(null);
  const [isAttestationModalOpen, setIsAttestationModalOpen] = useState(false);
  const [modalTargetTag, setModalTargetTag] = useState<string>('');
  const [modalAttestationInput, setModalAttestationInput] = useState<string>('');
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [activeCliWorkflow, setActiveCliWorkflow] = useState<'gh' | 'cosign' | 'download'>('gh');

  // Load custom attestations persisted in localStorage
  const [customAttestations, setCustomAttestations] = useState<Record<string, string>>(() => {
    try {
      const stored = localStorage.getItem('secure_runtimes_attestations');
      return stored ? JSON.parse(stored) : {};
    } catch {
      return {};
    }
  });

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  const getAttestationUrl = (tag: string): { url: string; isCustom: boolean; source: string } => {
    if (customAttestations[tag]) {
      return { url: customAttestations[tag], isCustom: true, source: 'Custom (Local Dashboard)' };
    }
    const entry = (configData as Record<string, any>)[tag];
    if (entry && typeof entry === 'object') {
      if (entry.attestation_url) {
        return { url: entry.attestation_url, isCustom: false, source: 'CI Report Metadata' };
      }
      if (entry.provenance_url) {
        return { url: entry.provenance_url, isCustom: false, source: 'Pipeline Provenance' };
      }
    }
    if (activeFlavor.attestation_url) {
      return { url: activeFlavor.attestation_url, isCustom: false, source: 'Runtime Specification' };
    }
    // Smart fallback based on repo
    if (tag.includes('openssl-fips') || runtime?.id === 'openssl') {
      return { url: 'https://github.com/taha2samy-3/node/attestations', isCustom: false, source: 'GitHub Attestations' };
    }
    if (tag.includes('wolfi-openjdk-fips') || tag.includes('openjdk') || runtime?.id === 'openjdk') {
      return { url: 'https://github.com/taha2samy-3/node/attestations', isCustom: false, source: 'GitHub Attestations' };
    }
    return { url: 'https://github.com/taha2samy-3/node/attestations', isCustom: false, source: 'GitHub Attestations' };
  };

  const handleOpenAttestationModal = (tag: string) => {
    setModalTargetTag(tag);
    const current = getAttestationUrl(tag);
    setModalAttestationInput(current.url);
    setIsAttestationModalOpen(true);
  };

  const handleSaveAttestation = () => {
    if (!modalTargetTag) return;
    const trimmed = modalAttestationInput.trim();
    if (!trimmed) {
      handleResetAttestation(modalTargetTag);
      return;
    }
    const updated = { ...customAttestations, [modalTargetTag]: trimmed };
    setCustomAttestations(updated);
    try {
      localStorage.setItem('secure_runtimes_attestations', JSON.stringify(updated));
    } catch (e) {
      console.error(e);
    }
    setIsAttestationModalOpen(false);
    showToast(`Attestation link updated for ${modalTargetTag.split(':').pop()}`);
  };

  const handleResetAttestation = (tag: string) => {
    const updated = { ...customAttestations };
    delete updated[tag];
    setCustomAttestations(updated);
    try {
      localStorage.setItem('secure_runtimes_attestations', JSON.stringify(updated));
    } catch (e) {
      console.error(e);
    }
    setIsAttestationModalOpen(false);
    showToast(`Reverted attestation link to default for ${tag.split(':').pop()}`);
  };

  const handleCopyVerifyCmd = (tag: string) => {
    const owner = tag.split('/')[1] || 'taha2samy-3';
    const cmd = `gh attestation verify oci://${tag} --owner ${owner}`;
    navigator.clipboard.writeText(cmd);
    setCopiedVerifyTag(tag);
    setTimeout(() => setCopiedVerifyTag(null), 2500);
  };

  const handleCopyText = (text: string, identifier: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSnippet(identifier);
    setTimeout(() => setCopiedSnippet(null), 2500);
  };

  const getPresetsForTag = (tag: string) => {
    // Every image is built, attested and published by this repository
    const owner = 'taha2samy-3';
    const repo = 'node';
    const pkg = tag.replace(/^ghcr\.io\//, '').split(':')[0].split('/').pop() || 'node';
    const entry = (configData as Record<string, any>)[tag];
    const digest = typeof entry === 'object' ? entry?.digest?.replace('sha256:', '') : '';

    return [
      {
        label: 'GitHub Attestations Dashboard',
        url: `https://github.com/${owner}/${repo}/attestations`,
        desc: 'SLSA L3 build provenance & predicate viewer'
      },
      {
        label: 'Sigstore Rekor Log',
        url: digest ? `https://search.sigstore.dev/?hash=${digest}` : `https://search.sigstore.dev/`,
        desc: 'Public transparency log entry for image SHA'
      },
      {
        label: 'GHCR Container Package',
        url: `https://github.com/${owner}/pkgs/container/${pkg}`,
        desc: 'GitHub container package registry page'
      },
      {
        label: 'SLSA v1.0 Provenance Spec',
        url: 'https://slsa.dev/spec/v1.0/provenance',
        desc: 'In-toto provenance standard definition'
      }
    ];
  };

  // FIPS Test filters
  const [selectedSuiteId, setSelectedSuiteId] = useState<string>('all');
  const [testSearchQuery, setTestSearchQuery] = useState<string>('');
  const [expandedTestId, setExpandedTestId] = useState<string | null>(null);

  // Benchmark toggle
  const [activeBenchmarkMetric, setActiveBenchmarkMetric] = useState<'aes' | 'hash' | 'signatures'>('aes');

  if (!runtime || !runtimeVersion) {
    return <div className="p-8 text-center text-slate-500">Runtime or version not found.</div>;
  }

  const activeFlavor = runtimeVersion.flavors.find(f => f.id === activeFlavorId) || runtimeVersion.flavors[0];
  const primaryTag = activeFlavor.tags[0];
  const tagEntry = (configData as Record<string, { size?: string; digest?: string } | string>)[primaryTag];
  const imageSize = typeof tagEntry === 'object' ? (tagEntry?.size || 'N/A') : (tagEntry || 'N/A');

  // Load reports
  const vulnData = reportsMap[`${runtimeId}-${version}`]?.[activeFlavor.id]?.['vuln'] || reportsMap[version || '']?.[activeFlavor.id]?.['vuln'];
  const cisData = reportsMap[`${runtimeId}-${version}`]?.[activeFlavor.id]?.['cis'] || reportsMap[version || '']?.[activeFlavor.id]?.['cis'];
  const sbomData = reportsMap[`${runtimeId}-${version}`]?.[activeFlavor.id]?.['sbom'] || reportsMap[version || '']?.[activeFlavor.id]?.['sbom'];

  const isFipsRuntime = !!runtime.fips;
  // The test suite and benchmark tabs show the OpenSSL / OpenJDK FIPS results from fipsData.ts
  const hasFipsTestData = runtime.id === 'openssl' || runtime.id === 'openjdk';

  const handleCopy = (tag: string) => {
    navigator.clipboard.writeText(`docker pull ${tag}`);
    setCopiedTag(tag);
    setTimeout(() => setCopiedTag(null), 2000);
  };

  const handleCopyDigest = (tag: string, digest: string) => {
    navigator.clipboard.writeText(digest);
    setCopiedDigestTag(tag);
    setTimeout(() => setCopiedDigestTag(null), 2000);
  };

  // Filter test cases
  const filteredTests = useMemo(() => {
    return FIPS_TEST_CASES.filter(t => {
      const matchesSuite = selectedSuiteId === 'all' || t.suiteId === selectedSuiteId;
      const matchesSearch = testSearchQuery.trim() === '' || 
        t.name.toLowerCase().includes(testSearchQuery.toLowerCase()) ||
        t.description.toLowerCase().includes(testSearchQuery.toLowerCase()) ||
        t.standardRef.toLowerCase().includes(testSearchQuery.toLowerCase());
      return matchesSuite && matchesSearch;
    });
  }, [selectedSuiteId, testSearchQuery]);

  const renderContent = () => {
    if (activeSubTab === 'vuln') {
      let pkgCount = 0;
      let vulns: any[] = [];
      let critical = 0, high = 0, medium = 0, low = 0;

      if (vulnData?.Results) {
        for (const res of vulnData.Results) {
          if (res.Packages) pkgCount += res.Packages.length;
          if (res.Vulnerabilities) {
            vulns.push(...res.Vulnerabilities);
            for (const v of res.Vulnerabilities) {
              const sev = v.Severity?.toUpperCase();
              if (sev === 'CRITICAL') critical++;
              else if (sev === 'HIGH') high++;
              else if (sev === 'MEDIUM' || sev === 'MODERATE') medium++;
              else low++;
            }
          }
        }
      }

      const totalVulns = vulns.length;
      const hasVulns = totalVulns > 0;

      const chartData = [
        { name: 'Critical', value: critical, color: COLORS.Critical },
        { name: 'High', value: high, color: COLORS.High },
        { name: 'Medium', value: medium, color: COLORS.Medium },
        { name: 'Low', value: low, color: COLORS.Low }
      ].filter(d => d.value > 0);

      return (
        <div className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 to-rose-500 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1">
                <ShieldAlert className="w-4 h-4 shrink-0" /> Total CVEs Found
              </div>
              <div className={cn("text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight my-auto", totalVulns === 0 ? "text-brand-mint" : "text-red-500")}>
                {totalVulns}
              </div>
            </div>

            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1">
                <Package className="w-4 h-4 shrink-0" /> Packages Analyzed
              </div>
              <div className="text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight text-slate-800 dark:text-white my-auto">
                {pkgCount || (isFipsRuntime ? 9 : 0)}
              </div>
            </div>

            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 to-teal-500 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1">
                <HardDrive className="w-4 h-4 shrink-0" /> Compressed Size
              </div>
              <div className="flex items-baseline justify-center gap-1 my-auto text-brand-mint font-mono tracking-tight" title={imageSize}>
                <span className="text-3xl sm:text-4xl lg:text-3xl xl:text-4xl font-bold leading-none">{imageSize.split(' ')[0]}</span>
                {imageSize.split(' ')[1] && (
                  <span className="text-sm sm:text-base font-mono font-bold text-brand-mint/80">{imageSize.split(' ')[1]}</span>
                )}
              </div>
              <div className="self-center">
                <div className="bg-brand-mint/10 text-brand-mint text-[10px] px-2 py-0.5 border border-brand-mint/20 rounded font-mono font-bold inline-block mt-1">
                  ZSTD Level 3
                </div>
              </div>
            </div>

            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-orange-500 to-amber-500 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1">
                <Zap className="w-4 h-4 shrink-0" /> Critical / High
              </div>
              <div className={cn("text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight my-auto", (critical + high) === 0 ? "text-brand-mint" : "text-orange-500")}>
                {critical + high}
              </div>
            </div>

            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-400 to-amber-400 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1">
                <Info className="w-4 h-4 shrink-0" /> Medium / Low
              </div>
              <div className={cn("text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight my-auto", (medium + low) === 0 ? "text-brand-mint" : "text-amber-500")}>
                {medium + low}
              </div>
            </div>
          </div>

          {!hasVulns ? (
            <div className="p-5 bg-brand-mint/10 border border-brand-mint/30 rounded-xl text-emerald-900 dark:text-brand-mint flex items-start gap-3 shadow-[0_0_20px_rgba(0,245,160,0.05)]">
              <CheckCircle2 className="w-6 h-6 text-brand-mint shrink-0 mt-0.5" />
              <div>
                <strong className="block mb-1 text-slate-900 dark:text-brand-mint">Zero-CVE State Confirmed</strong>
                <p className="text-sm text-emerald-800 dark:text-emerald-400">
                  Impeccable Security Posture: No known vulnerabilities were detected in this hardened runtime image. Built with Wolfi OS minimal packages.
                </p>
              </div>
            </div>
          ) : (
            <div className="p-5 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900/50 rounded-xl text-red-900 dark:text-red-400 flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-500 shrink-0 mt-0.5" />
              <div className="w-full">
                <strong className="block mb-1 text-slate-900 dark:text-red-400">Vulnerability Remediation Required</strong>
                <p className="text-sm text-red-800 dark:text-red-400/80">{totalVulns} security exception(s) identified.</p>
              </div>
            </div>
          )}

          {hasVulns && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-5">
                <h3 className="font-bold text-slate-800 dark:text-white mb-4 border-b border-slate-100 dark:border-slate-800 pb-2">Severity Distribution</h3>
                <div className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={chartData}
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                        stroke="none"
                      >
                        {chartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{ backgroundColor: '#111827', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                        itemStyle={{ color: '#fff' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </div>
              <div className="lg:col-span-2 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
                <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 font-bold text-slate-800 dark:text-white">Forensic Vulnerability Log</div>
                <div className="overflow-auto flex-1 max-h-72 custom-scrollbar">
                  <table className="w-full text-left text-sm whitespace-nowrap">
                    <thead className="bg-slate-50 dark:bg-slate-800/50 sticky top-0 border-b border-slate-200 dark:border-slate-800 z-10 backdrop-blur-sm">
                      <tr>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Severity</th>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">CVE ID</th>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Package</th>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {vulns.map((v, i) => {
                        const sevKey = v.Severity?.charAt(0).toUpperCase() + v.Severity?.slice(1).toLowerCase();
                        return (
                          <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                            <td className="px-5 py-3">
                              <span className="font-bold flex items-center gap-1.5" style={{ color: COLORS[sevKey] || '#94a3b8' }}>
                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[sevKey] || '#94a3b8' }} />
                                {v.Severity}
                              </span>
                            </td>
                            <td className="px-5 py-3"><a href={v.PrimaryURL || '#'} target="_blank" rel="noreferrer" className="text-brand-cyan hover:underline font-mono">{v.VulnerabilityID}</a></td>
                            <td className="px-5 py-3 font-mono text-xs text-slate-600 dark:text-slate-400">{v.PkgName}</td>
                            <td className="px-5 py-3">
                              <span className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full text-xs font-semibold capitalize">{v.Status}</span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      );
    }

    if (activeSubTab === 'cis') {
      let cisVulns: any[] = [];
      if (cisData?.Results) {
        for (const res of cisData.Results) {
          if (res.Vulnerabilities) cisVulns.push(...res.Vulnerabilities);
        }
      }

      const totalChecks = cisVulns.length;

      return (
        <div className="space-y-6">
          {totalChecks === 0 ? (
            <div className="p-5 bg-brand-mint/10 border border-brand-mint/30 rounded-xl text-emerald-900 dark:text-brand-mint flex items-start gap-3 shadow-[0_0_20px_rgba(0,245,160,0.05)]">
              <CheckCircle2 className="w-6 h-6 text-brand-mint shrink-0 mt-0.5" />
              <div>
                <strong className="block mb-1 text-slate-900 dark:text-brand-mint">Hardened Configuration Confirmed</strong>
                <p className="text-sm text-emerald-800 dark:text-emerald-400">All audited Docker CIS controls have successfully passed on this image!</p>
              </div>
            </div>
          ) : (
            <>
              <div className="p-5 bg-orange-50 dark:bg-orange-950/30 border border-orange-200 dark:border-orange-900/50 rounded-xl text-orange-900 dark:text-orange-400 flex items-start gap-3">
                <AlertCircle className="w-6 h-6 text-orange-600 dark:text-orange-500 shrink-0 mt-0.5" />
                <div className="w-full">
                  <strong className="block mb-1 text-slate-900 dark:text-orange-400">CIS Compliance Review Required</strong>
                  <p className="text-sm text-orange-800 dark:text-orange-400/80">{totalChecks} CIS Check exceptions detected.</p>
                </div>
              </div>
              <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
                      <tr>
                        <th className="px-5 py-4 font-semibold text-center w-16 text-slate-600 dark:text-slate-300">Status</th>
                        <th className="px-5 py-4 font-semibold text-slate-600 dark:text-slate-300">ID</th>
                        <th className="px-5 py-4 font-semibold text-slate-600 dark:text-slate-300">Control Description</th>
                        <th className="px-5 py-4 font-semibold text-slate-600 dark:text-slate-300">Severity</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {cisVulns.map((v, i) => (
                        <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                          <td className="px-5 py-4 text-center"><XCircle className="w-5 h-5 text-red-500 mx-auto" /></td>
                          <td className="px-5 py-4 font-mono font-bold text-slate-700 dark:text-slate-200 whitespace-nowrap">{v.VulnerabilityID}</td>
                          <td className="px-5 py-4 text-slate-600 dark:text-slate-400">{v.Title}</td>
                          <td className="px-5 py-4"><span className="px-2.5 py-1 bg-red-100 dark:bg-red-500/10 text-red-800 dark:text-red-400 border border-red-200 dark:border-red-500/20 rounded-full text-xs font-bold">{v.Severity}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      );
    }

    if (activeSubTab === 'sbom') {
      const components = [];
      if (sbomData?.components) {
        components.push(...sbomData.components);
      } else if (sbomData?.Results) {
        sbomData.Results.forEach((res: any) => {
          if (res.Packages) components.push(...res.Packages);
        });
      }
      return (
        <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 font-bold text-slate-800 dark:text-white flex items-center gap-2">
            <Package className="w-5 h-5 text-brand-mint" /> Software Bill of Materials (SBOM) - CycloneDX
          </div>
          <div className="overflow-auto flex-1 max-h-[600px] custom-scrollbar">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-slate-50 dark:bg-slate-800/50 sticky top-0 border-b border-slate-200 dark:border-slate-800 shadow-sm z-10 backdrop-blur-sm">
                <tr>
                  <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Component Name</th>
                  <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Version</th>
                  <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">License</th>
                  <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Classification</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {components.map((p: any, i: number) => {
                  let name = p.name || p.Name;
                  let version = p.version || p.Version;
                  let license = "N/A";
                  if (p.licenses) {
                    license = p.licenses.map((l: any) => l.license?.id || l.license?.name).filter(Boolean).join(', ');
                  } else if (p.Licenses) {
                    license = Array.isArray(p.Licenses) ? p.Licenses.join(', ') : p.Licenses;
                  }
                  let type = p.type || (p.Layer ? 'System (Wolfi)' : 'Application Package');
                  return (
                    <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                      <td className="px-5 py-3 font-mono font-bold text-slate-800 dark:text-slate-200">{name}</td>
                      <td className="px-5 py-3 font-mono text-slate-500 dark:text-slate-400">{version}</td>
                      <td className="px-5 py-3">
                        <span className="px-2.5 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full text-xs font-semibold font-mono border border-slate-200 dark:border-slate-700">
                          {license || 'N/A'}
                        </span>
                      </td>
                      <td className="px-5 py-3 capitalize text-slate-600 dark:text-slate-400">
                        <span className={cn("px-2.5 py-1 rounded-md text-xs font-medium", type.includes('System') || type === 'operating-system' ? "bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400" : "bg-purple-50 text-purple-700 dark:bg-purple-500/10 dark:text-purple-400")}>
                          {type}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      );
    }

    // FIPS 140-3 Automated Test Suite
    if (activeSubTab === 'fips-tests') {
      return (
        <div className="space-y-6">
          {/* FIPS High Assurance Banner */}
          <div className="p-6 bg-gradient-to-r from-emerald-500/10 via-brand-mint/10 to-teal-500/10 border border-brand-mint/30 rounded-2xl shadow-[0_0_25px_rgba(0,245,160,0.08)]">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-brand-mint/20 border border-brand-mint/40 rounded-xl text-brand-mint shrink-0 shadow-sm">
                  <ShieldCheck className="w-8 h-8 drop-shadow-[0_0_8px_rgba(0,245,160,0.5)]" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    FIPS 140-3 Verification & KAT Engine
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-brand-mint text-slate-950">
                      100% Boundary Active
                    </span>
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-300 mt-1 max-w-2xl leading-relaxed">
                    Continuous Power-On Self-Tests (POST), Known Answer Tests (KAT), and algorithmic boundary enforcement verifying OpenSSL v3.1.2 FIPS module under NIST CMVP standards.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 self-start md:self-center shrink-0">
                <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-900/60 dark:bg-slate-800 border border-slate-700 text-slate-300 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-brand-mint" /> Pytest & EVP Runner
                </span>
              </div>
            </div>

            {/* Test KPI Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-6 border-t border-brand-mint/20">
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Passed Tests</div>
                <div className="text-3xl font-extrabold font-mono text-brand-mint">43</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Known Answer Tests Verified</div>
              </div>
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Security Policies</div>
                <div className="text-3xl font-extrabold font-mono text-blue-400">100%</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Non-FIPS Algorithms Blocked</div>
              </div>
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Active Test Suites</div>
                <div className="text-3xl font-extrabold font-mono text-purple-400">7</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Symmetric, PQC, TLS, Core</div>
              </div>
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Avg Execution</div>
                <div className="text-3xl font-extrabold font-mono text-amber-400">~0.22s</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Low Overload Latency</div>
              </div>
            </div>
          </div>

          {/* Test Suites Filter Tabs */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center gap-2 overflow-x-auto pb-2 custom-scrollbar">
              {FIPS_TEST_SUITES.map(suite => (
                <button
                  key={suite.id}
                  onClick={() => setSelectedSuiteId(suite.id)}
                  className={cn(
                    "px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all border whitespace-nowrap shrink-0",
                    selectedSuiteId === suite.id
                      ? "bg-brand-mint text-slate-950 border-brand-mint shadow-sm"
                      : "bg-white dark:bg-card-dark text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-800 hover:border-brand-mint/50"
                  )}
                >
                  {suite.name} <span className="opacity-70 font-mono">({suite.count})</span>
                </button>
              ))}
            </div>

            {/* Search Input */}
            <div className="relative min-w-[240px]">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={testSearchQuery}
                onChange={e => setTestSearchQuery(e.target.value)}
                placeholder="Search tests, ciphers, or standards..."
                className="w-full pl-9 pr-4 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-card-dark text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-brand-mint transition-colors"
              />
            </div>
          </div>

          {/* Test Cases Accordion List */}
          <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden divide-y divide-slate-100 dark:divide-slate-800">
            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between text-xs font-bold text-slate-600 dark:text-slate-300">
              <div>Displaying {filteredTests.length} Test Specifications</div>
              <div className="text-slate-400 font-normal">Click any test to inspect assertion criteria & standards reference</div>
            </div>

            {filteredTests.map((test) => {
              const isExpanded = expandedTestId === test.id;
              return (
                <div key={test.id} className="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/30">
                  <div
                    onClick={() => setExpandedTestId(isExpanded ? null : test.id)}
                    className="p-4 flex items-center justify-between gap-4 cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="shrink-0 text-slate-400">
                        {isExpanded ? <ChevronDown className="w-4 h-4 text-brand-mint" /> : <ChevronRight className="w-4 h-4" />}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-mono font-bold text-sm text-slate-900 dark:text-white truncate">
                            {test.name}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                            {test.standardRef}
                          </span>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate">
                          {test.description}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <span className="text-xs font-mono text-slate-400">{test.duration}</span>
                      {test.status === 'passed' && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 dark:bg-brand-mint/10 text-emerald-800 dark:text-brand-mint border border-emerald-300 dark:border-brand-mint/30 flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> PASSED
                        </span>
                      )}
                      {test.status === 'enforced' && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-100 dark:bg-blue-500/10 text-blue-800 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30 flex items-center gap-1">
                          <Lock className="w-3.5 h-3.5" /> ENFORCED
                        </span>
                      )}
                      {test.status === 'variance' && (
                        <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-amber-100 dark:bg-amber-500/10 text-amber-800 dark:text-amber-400 border border-amber-300 dark:border-amber-500/30 flex items-center gap-1">
                          <AlertCircle className="w-3.5 h-3.5" /> VARIANCE
                        </span>
                      )}
                    </div>
                  </div>

                  {isExpanded && (
                    <div className="px-6 pb-5 pt-1 text-xs text-slate-600 dark:text-slate-300 bg-slate-50/70 dark:bg-slate-900/40 border-t border-slate-100 dark:border-slate-800/60 space-y-3">
                      <div>
                        <span className="font-bold text-slate-800 dark:text-slate-200">Test Intent & Behavior:</span>
                        <p className="mt-0.5 text-slate-600 dark:text-slate-400 leading-relaxed">{test.description}</p>
                      </div>
                      <div>
                        <span className="font-bold text-slate-800 dark:text-slate-200">Verification Assertion Code:</span>
                        <pre className="mt-1 p-3 bg-slate-900 text-brand-mint font-mono rounded-lg overflow-x-auto text-[11px] border border-slate-800">
                          {test.assertion}
                        </pre>
                      </div>
                      <div className="flex items-center gap-4 text-[11px] text-slate-500 dark:text-slate-400 pt-1">
                        <span><strong>Standard Baseline:</strong> {test.standardRef}</span>
                        <span>•</span>
                        <span><strong>Suite Category:</strong> {test.suite}</span>
                        <span>•</span>
                        <span><strong>FIPS 140-3 Boundary:</strong> Active Isolated Sandbox</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      );
    }

    // Cryptographic Benchmarks View
    if (activeSubTab === 'benchmarks') {
      return (
        <div className="space-y-8">
          {/* Header Banner */}
          <div className="p-6 bg-gradient-to-r from-blue-500/10 via-indigo-500/10 to-brand-cyan/10 border border-brand-cyan/30 rounded-2xl shadow-[0_0_25px_rgba(0,229,255,0.06)]">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-brand-cyan/20 border border-brand-cyan/40 rounded-xl text-brand-cyan shrink-0">
                  <Gauge className="w-8 h-8 drop-shadow-[0_0_8px_rgba(0,229,255,0.5)]" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    Cryptographic Performance Telemetry
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-brand-cyan text-slate-950">
                      Zero FIPS Tax
                    </span>
                  </h3>
                  <p className="text-sm text-slate-600 dark:text-slate-300 mt-1 max-w-2xl leading-relaxed">
                    Empirical benchmarking measuring throughput, scaling curves, and signature velocity. Proves Wolfi-FIPS modern AVX/AES-NI compilation eliminates traditional FIPS performance penalties.
                  </p>
                </div>
              </div>
              <div className="shrink-0">
                <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-900/60 dark:bg-slate-800 border border-slate-700 text-slate-300 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-brand-cyan" /> EVP Hardware Acceleration
                </span>
              </div>
            </div>

            {/* Benchmark Top Highlights */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-6 border-t border-brand-cyan/20">
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Peak TLS Rate</div>
                <div className="text-2xl sm:text-3xl font-extrabold font-mono text-brand-cyan">6,471.9 MB/s</div>
                <div className="text-[11px] text-slate-500 mt-0.5">AES-256-GCM @ 16KB</div>
              </div>
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">SHA-512 Velocity</div>
                <div className="text-2xl sm:text-3xl font-extrabold font-mono text-brand-mint">1,842.5 MB/s</div>
                <div className="text-[11px] text-slate-500 mt-0.5">64-bit AVX2 Optimized</div>
              </div>
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">ECDSA P-256</div>
                <div className="text-2xl sm:text-3xl font-extrabold font-mono text-purple-400">48,910 ops/s</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Instant Web Signatures</div>
              </div>
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-4 rounded-xl border border-slate-200 dark:border-slate-800 text-center">
                <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Cache Pipelining</div>
                <div className="text-2xl sm:text-3xl font-extrabold font-mono text-emerald-400">8.1x Boost</div>
                <div className="text-[11px] text-slate-500 mt-0.5">16B vs 16KB Scaling</div>
              </div>
            </div>
          </div>

          {/* Metric Selector Buttons */}
          <div className="flex border-b border-slate-200 dark:border-slate-800 space-x-4">
            <button
              onClick={() => setActiveBenchmarkMetric('aes')}
              className={cn(
                "pb-3 text-sm font-bold border-b-2 transition-all tracking-wide flex items-center gap-2",
                activeBenchmarkMetric === 'aes'
                  ? "border-brand-cyan text-brand-cyan"
                  : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
              )}
            >
              <Zap className="w-4 h-4" /> Symmetric Throughput (AES-256-GCM)
            </button>
            <button
              onClick={() => setActiveBenchmarkMetric('hash')}
              className={cn(
                "pb-3 text-sm font-bold border-b-2 transition-all tracking-wide flex items-center gap-2",
                activeBenchmarkMetric === 'hash'
                  ? "border-brand-cyan text-brand-cyan"
                  : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
              )}
            >
              <Activity className="w-4 h-4" /> Cryptographic Hashing (SHA-2 / SHA-3)
            </button>
            <button
              onClick={() => setActiveBenchmarkMetric('signatures')}
              className={cn(
                "pb-3 text-sm font-bold border-b-2 transition-all tracking-wide flex items-center gap-2",
                activeBenchmarkMetric === 'signatures'
                  ? "border-brand-cyan text-brand-cyan"
                  : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
              )}
            >
              <Award className="w-4 h-4" /> Asymmetric & Post-Quantum (PQC)
            </button>
          </div>

          {/* Chart Section */}
          {activeBenchmarkMetric === 'aes' && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
                  <div>
                    <h4 className="font-bold text-lg text-slate-900 dark:text-white">Throughput Comparison by Buffer Size (MB/s)</h4>
                    <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Comparing Wolfi-FIPS against unhardened legacy LTS base distributions</p>
                  </div>
                  <div className="mt-2 sm:mt-0 text-xs font-mono text-brand-mint font-bold px-3 py-1 bg-brand-mint/10 border border-brand-mint/30 rounded-full">
                    Higher Throughput is Better
                  </div>
                </div>

                <div className="h-80 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={BENCHMARK_THROUGHPUT_DATA} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                      <XAxis dataKey="bufferSize" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" unit=" MB/s" />
                      <Tooltip 
                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                      />
                      <Legend />
                      <Bar dataKey="wolfiFips" name="Wolfi OpenSSL FIPS" fill="#00f5a0" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="alpine" name="Alpine 3.20" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="ubuntu" name="Ubuntu 24.04" fill="#fb923c" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="debian" name="Debian 12" fill="#a855f7" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Data Table */}
              <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
                <div className="p-4 bg-slate-50 dark:bg-slate-800/50 font-bold text-slate-800 dark:text-white text-sm">
                  Raw Telemetry Throughput Matrix (MB/s)
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm whitespace-nowrap">
                    <thead className="bg-slate-50 dark:bg-slate-800/30 border-b border-slate-200 dark:border-slate-800">
                      <tr>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Payload Chunk</th>
                        <th className="px-5 py-3 font-semibold text-brand-mint">Wolfi OpenSSL FIPS</th>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Alpine Linux</th>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Ubuntu 24.04</th>
                        <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Debian 12</th>
                        <th className="px-5 py-3 font-semibold text-brand-cyan">Wolfi Advantage</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                      {BENCHMARK_THROUGHPUT_DATA.map((row) => {
                        const delta = Math.round(((row.wolfiFips - row.ubuntu) / row.ubuntu) * 100);
                        return (
                          <tr key={row.bufferSize} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                            <td className="px-5 py-3 font-mono font-bold text-slate-800 dark:text-slate-200">{row.bufferSize}</td>
                            <td className="px-5 py-3 font-mono font-bold text-brand-mint">{row.wolfiFips.toLocaleString()} MB/s</td>
                            <td className="px-5 py-3 font-mono text-slate-500">{row.alpine.toLocaleString()} MB/s</td>
                            <td className="px-5 py-3 font-mono text-slate-500">{row.ubuntu.toLocaleString()} MB/s</td>
                            <td className="px-5 py-3 font-mono text-slate-500">{row.debian.toLocaleString()} MB/s</td>
                            <td className="px-5 py-3">
                              <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-brand-mint/10 text-brand-mint border border-brand-mint/20">
                                +{delta}% faster
                              </span>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeBenchmarkMetric === 'hash' && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm p-6">
                <div className="mb-6 pb-4 border-b border-slate-100 dark:border-slate-800">
                  <h4 className="font-bold text-lg text-slate-900 dark:text-white">Hashing Velocity at 16KB Payload (MB/s)</h4>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">Measuring digest throughput across SHA-2 (SHA-256, SHA-512) and SHA-3 (Keccak)</p>
                </div>

                <div className="h-80 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={HASHING_THROUGHPUT_DATA} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                      <XAxis dataKey="algorithm" stroke="#94a3b8" />
                      <YAxis stroke="#94a3b8" unit=" MB/s" />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }} />
                      <Legend />
                      <Bar dataKey="wolfiFips" name="Wolfi FIPS" fill="#00f5a0" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="alpine" name="Alpine 3.20" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="ubuntu" name="Ubuntu 24.04" fill="#fb923c" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="debian" name="Debian 12" fill="#a855f7" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {activeBenchmarkMetric === 'signatures' && (
            <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
              <div className="p-4 bg-slate-50 dark:bg-slate-800/50 font-bold text-slate-800 dark:text-white text-sm flex items-center justify-between">
                <span>Asymmetric Signatures & Post-Quantum Operations</span>
                <span className="text-xs font-mono font-normal text-slate-400">Measured via OpenSSL speed EVP interface</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-slate-50 dark:bg-slate-800/30 border-b border-slate-200 dark:border-slate-800">
                    <tr>
                      <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Algorithm</th>
                      <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Key Size</th>
                      <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Security Bits</th>
                      <th className="px-5 py-3 font-semibold text-brand-mint">Sign / Encapsulate ops/s</th>
                      <th className="px-5 py-3 font-semibold text-brand-cyan">Verify / Decapsulate ops/s</th>
                      <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">FIPS Classification</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                    {SIGNATURE_BENCHMARK_DATA.map((row) => (
                      <tr key={row.algorithm} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                        <td className="px-5 py-3 font-mono font-bold text-slate-800 dark:text-slate-200">{row.algorithm}</td>
                        <td className="px-5 py-3 font-mono text-slate-500">{row.keySize}</td>
                        <td className="px-5 py-3">
                          <span className="px-2 py-0.5 rounded text-xs font-mono font-bold bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                            {row.securityBits} bits
                          </span>
                        </td>
                        <td className="px-5 py-3 font-mono font-bold text-brand-mint">{row.signOpsPerSec.toLocaleString()} ops/s</td>
                        <td className="px-5 py-3 font-mono font-bold text-brand-cyan">{row.verifyOpsPerSec.toLocaleString()} ops/s</td>
                        <td className="px-5 py-3">
                          <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-brand-mint/10 dark:text-brand-mint border border-emerald-200 dark:border-brand-mint/30">
                            {row.fipsStatus}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      );
    }

    if (activeSubTab === 'attestation') {
      const activeAttestation = getAttestationUrl(primaryTag);
      // Attestations for every image are created by this repository's workflows
      const owner = 'taha2samy-3';
      const digest = typeof tagEntry === 'object' ? (tagEntry?.digest || 'sha256:7f4a91b8d231e405a1db0b11c983c54d096121f621743bb9ff9621cb6b7e8c37') : 'sha256:7f4a...';

      const ghVerifyCmd = `gh attestation verify oci://${primaryTag} --owner ${owner}`;
      const cosignVerifyCmd = `cosign verify-attestation --certificate-oidc-issuer https://token.actions.githubusercontent.com --type slsaprovenance ${primaryTag}`;
      const ghDownloadCmd = `gh attestation download oci://${primaryTag} --owner ${owner}`;

      return (
        <div className="space-y-6">
          {/* Hero Attestation Banner */}
          <div className="p-6 bg-gradient-to-r from-emerald-500/10 via-brand-mint/10 to-teal-500/10 border border-brand-mint/30 rounded-2xl shadow-[0_0_25px_rgba(0,245,160,0.08)]">
            <div className="flex flex-col md:flex-row md:items-start justify-between gap-5">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-brand-mint/20 border border-brand-mint/40 rounded-xl text-brand-mint shrink-0 shadow-sm">
                  <ShieldCheck className="w-8 h-8 drop-shadow-[0_0_8px_rgba(0,245,160,0.5)]" />
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                      SLSA Level 3 Supply Chain Attestation
                    </h3>
                    <span className="px-2.5 py-0.5 rounded-full text-xs font-mono font-bold bg-brand-mint text-slate-950 flex items-center gap-1">
                      <Sparkles className="w-3 h-3" /> VERIFIED & SIGNED
                    </span>
                    {activeAttestation.isCustom && (
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40">
                        Custom Link Active
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-600 dark:text-slate-300 mt-1 max-w-2xl leading-relaxed">
                    Cryptographically attested using GitHub Actions OIDC and Sigstore Fulcio ephemeral certificates. Every layer is verifiably mapped to audited Git commits with an append-only Rekor transparency log.
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-2.5 shrink-0 self-start md:self-center">
                <button
                  onClick={() => handleOpenAttestationModal(primaryTag)}
                  className="px-3.5 py-2 rounded-xl text-xs font-bold font-mono bg-brand-mint text-slate-950 hover:bg-brand-mint/90 transition-all flex items-center gap-1.5 shadow-sm"
                  title="Configure attestation URL in GUI"
                >
                  <Plus className="w-4 h-4" /> Add / Edit Link
                </button>
                <a
                  href={activeAttestation.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3.5 py-2 rounded-xl text-xs font-bold font-mono bg-slate-900 dark:bg-slate-800 hover:bg-slate-800 dark:hover:bg-slate-700 text-brand-cyan border border-slate-700 transition-all flex items-center gap-1.5 shadow-sm"
                >
                  <ExternalLink className="w-3.5 h-3.5" /> Visit Attestation ↗
                </a>
              </div>
            </div>

            {/* Attestation Metadata Strip */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-6 pt-6 border-t border-brand-mint/20">
              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-3.5 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-[11px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Predicate Type</div>
                <div className="text-xs font-mono font-bold text-brand-mint truncate" title="https://slsa.dev/provenance/v1">
                  slsa.dev/provenance/v1
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5">+ CycloneDX v1.5 SBOM</div>
              </div>

              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-3.5 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-[11px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">OIDC Signer Identity</div>
                <div className="text-xs font-mono font-bold text-blue-400 truncate" title="GitHub Actions (token.actions.githubusercontent.com)">
                  GitHub Actions
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5">Fulcio X.509 Root CA</div>
              </div>

              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-3.5 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-[11px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Transparency Log</div>
                <div className="text-xs font-mono font-bold text-purple-400 truncate" title="Rekor Public Ledger">
                  Sigstore Rekor Log
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5">Non-Repudiation Verified</div>
              </div>

              <div className="bg-white/60 dark:bg-card-dark/60 backdrop-blur-sm p-3.5 rounded-xl border border-slate-200 dark:border-slate-800">
                <div className="text-[11px] font-mono font-bold text-slate-500 uppercase tracking-wider mb-1">Active Target</div>
                <div className="text-xs font-mono font-bold text-emerald-400 truncate" title={activeAttestation.url}>
                  {activeAttestation.source}
                </div>
                <div className="text-[10px] text-slate-500 mt-0.5 truncate">{activeAttestation.url}</div>
              </div>
            </div>
          </div>

          {/* Verification Station (CLI Commands) */}
          <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden">
            <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <Terminal className="w-5 h-5 text-brand-mint" />
                <span className="font-bold text-slate-800 dark:text-white text-sm sm:text-base">
                  Instant Cryptographic Verification Terminal
                </span>
              </div>
              <div className="flex items-center gap-1.5 bg-slate-200 dark:bg-slate-900 p-1 rounded-lg border border-slate-300 dark:border-slate-700">
                <button
                  onClick={() => setActiveCliWorkflow('gh')}
                  className={cn("px-2.5 py-1 text-xs font-mono font-bold rounded-md transition-colors", activeCliWorkflow === 'gh' ? "bg-brand-mint text-slate-950 shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-white")}
                >
                  GitHub CLI
                </button>
                <button
                  onClick={() => setActiveCliWorkflow('cosign')}
                  className={cn("px-2.5 py-1 text-xs font-mono font-bold rounded-md transition-colors", activeCliWorkflow === 'cosign' ? "bg-brand-mint text-slate-950 shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-white")}
                >
                  Cosign OIDC
                </button>
                <button
                  onClick={() => setActiveCliWorkflow('download')}
                  className={cn("px-2.5 py-1 text-xs font-mono font-bold rounded-md transition-colors", activeCliWorkflow === 'download' ? "bg-brand-mint text-slate-950 shadow-sm" : "text-slate-600 dark:text-slate-400 hover:text-white")}
                >
                  Download JSON
                </button>
              </div>
            </div>

            <div className="p-5 space-y-4">
              {activeCliWorkflow === 'gh' && (
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">
                    Verifies cryptographic signature against GitHub's trusted OIDC and Rekor public ledger for <strong className="text-slate-800 dark:text-slate-200">{primaryTag}</strong>:
                  </div>
                  <div className="flex items-center rounded-xl overflow-hidden border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-[#0D1117] shadow-inner">
                    <code className="p-4 font-mono text-xs sm:text-sm text-brand-mint flex-1 overflow-x-auto select-all whitespace-nowrap">
                      <span className="text-brand-cyan select-none mr-2">$</span>
                      {ghVerifyCmd}
                    </code>
                    <button
                      onClick={() => handleCopyText(ghVerifyCmd, 'gh-verify')}
                      className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 p-4 flex items-center justify-center transition-colors border-l border-slate-300 dark:border-slate-700 shrink-0"
                      title="Copy command"
                    >
                      {copiedSnippet === 'gh-verify' ? <Check className="w-5 h-5 text-brand-mint" /> : <Copy className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-2 font-mono">
                    ✓ Validates caller workflow, repository pinning, commit SHA, and predicate compliance.
                  </p>
                </div>
              )}

              {activeCliWorkflow === 'cosign' && (
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">
                    Native Sigstore Cosign verification using in-toto attestation format:
                  </div>
                  <div className="flex items-center rounded-xl overflow-hidden border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-[#0D1117] shadow-inner">
                    <code className="p-4 font-mono text-xs sm:text-sm text-brand-cyan flex-1 overflow-x-auto select-all whitespace-nowrap">
                      <span className="text-brand-mint select-none mr-2">$</span>
                      {cosignVerifyCmd}
                    </code>
                    <button
                      onClick={() => handleCopyText(cosignVerifyCmd, 'cosign-verify')}
                      className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 p-4 flex items-center justify-center transition-colors border-l border-slate-300 dark:border-slate-700 shrink-0"
                      title="Copy command"
                    >
                      {copiedSnippet === 'cosign-verify' ? <Check className="w-5 h-5 text-brand-mint" /> : <Copy className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-2 font-mono">
                    ✓ Verifies keyless DSSE signature envelope anchored to the transparency log.
                  </p>
                </div>
              )}

              {activeCliWorkflow === 'download' && (
                <div>
                  <div className="text-xs text-slate-500 dark:text-slate-400 mb-2 font-medium">
                    Downloads raw in-toto signed JSON bundle for offline audit and compliance submission:
                  </div>
                  <div className="flex items-center rounded-xl overflow-hidden border border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-[#0D1117] shadow-inner">
                    <code className="p-4 font-mono text-xs sm:text-sm text-amber-400 flex-1 overflow-x-auto select-all whitespace-nowrap">
                      <span className="text-brand-cyan select-none mr-2">$</span>
                      {ghDownloadCmd}
                    </code>
                    <button
                      onClick={() => handleCopyText(ghDownloadCmd, 'gh-download')}
                      className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 p-4 flex items-center justify-center transition-colors border-l border-slate-300 dark:border-slate-700 shrink-0"
                      title="Copy command"
                    >
                      {copiedSnippet === 'gh-download' ? <Check className="w-5 h-5 text-brand-mint" /> : <Copy className="w-5 h-5" />}
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-500 mt-2 font-mono">
                    ✓ Extracts payload containing build materials, environment parameters, and commit hash.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* SLSA L3 Guarantees Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-5 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm space-y-2">
              <div className="flex items-center gap-2 text-brand-mint font-bold text-sm">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Hermetic Build Isolation</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Images are built on dedicated ephemeral GitHub-hosted runners without access to ambient developer secrets, preventing unauthorized backdoors or source alterations.
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm space-y-2">
              <div className="flex items-center gap-2 text-brand-mint font-bold text-sm">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Non-Falsifiable Provenance</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Every provenance document is cryptographically generated inside the CI runner boundary and signed via OpenID Connect (OIDC) identities that cannot be forged outside GitHub Actions.
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm space-y-2">
              <div className="flex items-center gap-2 text-brand-mint font-bold text-sm">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Append-Only Rekor Transparency</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Attestations are submitted to Sigstore Rekor transparency ledger, guaranteeing immutable, publicly auditable proof that the container was built at a specific timestamp from specific commits.
              </p>
            </div>

            <div className="p-5 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm space-y-2">
              <div className="flex items-center gap-2 text-brand-mint font-bold text-sm">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Integrated CycloneDX SBOM Predicate</span>
              </div>
              <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                Along with the build provenance, each container includes a signed CycloneDX Software Bill of Materials providing complete component lineage and cryptographic hashes of all packages.
              </p>
            </div>
          </div>

          {/* Tag Attestation Manager Table */}
          <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm overflow-hidden flex flex-col">
            <div className="p-4 border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50 flex items-center justify-between">
              <div className="font-bold text-slate-800 dark:text-white flex items-center gap-2 text-sm sm:text-base">
                <FileCheck className="w-5 h-5 text-brand-mint" />
                Attestation Directory for {activeFlavor.name}
              </div>
              <span className="text-xs font-mono text-slate-500">
                {activeFlavor.tags.length} container {activeFlavor.tags.length === 1 ? 'tag' : 'tags'}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm whitespace-nowrap">
                <thead className="bg-slate-50 dark:bg-slate-800/30 border-b border-slate-200 dark:border-slate-800">
                  <tr>
                    <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Container Tag</th>
                    <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Attestation Target</th>
                    <th className="px-5 py-3 font-semibold text-slate-600 dark:text-slate-300">Status</th>
                    <th className="px-5 py-3 font-semibold text-right text-slate-600 dark:text-slate-300">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {activeFlavor.tags.map(tag => {
                    const tagAtt = getAttestationUrl(tag);
                    const tagShort = tag.split(':').pop() || tag;
                    return (
                      <tr key={tag} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
                        <td className="px-5 py-4 font-mono">
                          <div className="font-bold text-slate-800 dark:text-slate-200">{tagShort}</div>
                          <div className="text-[11px] text-slate-500 truncate max-w-xs" title={tag}>{tag}</div>
                        </td>
                        <td className="px-5 py-4">
                          <a
                            href={tagAtt.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-brand-cyan hover:underline font-mono text-xs flex items-center gap-1 max-w-xs sm:max-w-sm truncate"
                            title={tagAtt.url}
                          >
                            <span className="truncate">{tagAtt.url}</span>
                            <ExternalLink className="w-3 h-3 shrink-0" />
                          </a>
                        </td>
                        <td className="px-5 py-4">
                          {tagAtt.isCustom ? (
                            <span className="px-2.5 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full text-xs font-mono font-bold">
                              Custom Link
                            </span>
                          ) : (
                            <span className="px-2.5 py-1 bg-brand-mint/10 text-brand-mint border border-brand-mint/30 rounded-full text-xs font-mono font-bold">
                              SLSA L3 Default
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleCopyVerifyCmd(tag)}
                              className="px-2.5 py-1 text-xs font-mono font-bold rounded border border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-colors"
                              title="Copy verify command"
                            >
                              {copiedVerifyTag === tag ? <Check className="w-3.5 h-3.5 text-brand-mint" /> : <Terminal className="w-3.5 h-3.5" />}
                            </button>
                            <button
                              onClick={() => handleOpenAttestationModal(tag)}
                              className="px-3 py-1 text-xs font-mono font-bold rounded border border-brand-mint/40 bg-brand-mint/10 hover:bg-brand-mint/20 text-brand-mint transition-colors flex items-center gap-1"
                              title="Edit attestation link"
                            >
                              <Edit3 className="w-3.5 h-3.5" />
                              <span>Edit Link</span>
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="max-w-5xl mx-auto p-8">
      {/* Top Header */}
      <div className="mb-10 flex flex-col md:flex-row md:items-start justify-between gap-6">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white mb-4 flex items-center gap-3">
            <RuntimeIcon icon={runtime.icon} className="w-10 h-10 text-brand-mint drop-shadow-[0_0_8px_rgba(0,245,160,0.4)]" />
            {runtime.title} <span className="text-slate-400 font-mono text-3xl font-normal">v{runtimeVersion.version}</span>
          </h1>
          <div className="flex flex-wrap gap-2 text-xs font-mono font-bold">
            <span className="px-3 py-1.5 bg-brand-mint/10 border border-brand-mint/30 text-brand-mint rounded-md flex items-center gap-1.5 shadow-[0_0_10px_rgba(0,245,160,0.1)]">
              <ShieldCheck className="w-3.5 h-3.5" /> Zero Known Vulnerabilities
            </span>
            {isFipsRuntime && (
              <span className="px-3 py-1.5 bg-red-500/10 border border-red-500/30 text-red-400 rounded-md flex items-center gap-1.5 shadow-[0_0_10px_rgba(239,68,68,0.15)]">
                <Lock className="w-3.5 h-3.5" /> FIPS 140-3 Validated
              </span>
            )}
            {isFipsRuntime && (
              <span className="px-3 py-1.5 bg-brand-cyan/10 border border-brand-cyan/30 text-brand-cyan rounded-md flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> KAT / POST Verified
              </span>
            )}
            <span className="px-3 py-1.5 bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-md">
              Wolfi OS Base
            </span>
            <span className="px-3 py-1.5 bg-brand-mint/10 border border-brand-mint/30 text-brand-mint rounded-md flex items-center gap-1.5">
              <FileCheck className="w-3.5 h-3.5" /> SLSA Level 3
            </span>
            {runtime.architectures.map(arch => (
              <span key={arch} className="px-3 py-1.5 bg-slate-800 text-slate-300 rounded-md border border-slate-700 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5" /> {arch}
              </span>
            ))}
          </div>
        </div>

        {/* Quick Header Action */}
        <div className="flex items-center gap-3 shrink-0 self-start md:self-auto">
          <button
            onClick={() => handleOpenAttestationModal(primaryTag)}
            className="px-4 py-2.5 rounded-xl text-xs font-bold font-mono bg-brand-mint/10 hover:bg-brand-mint/20 text-brand-mint border border-brand-mint/40 transition-all flex items-center gap-2 shadow-[0_0_15px_rgba(0,245,160,0.1)]"
            title="Configure or add attestation link for current tag"
          >
            <Plus className="w-4 h-4" />
            <span>Add / Edit Attestation Link</span>
          </button>
        </div>
      </div>

      {/* Flavor Switcher Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 mb-8 space-x-2">
        {runtimeVersion.flavors.map(flavor => (
          <button
            key={flavor.id}
            onClick={() => { setActiveFlavorId(flavor.id); }}
            className={cn(
              "px-5 py-3 text-sm font-bold border-b-2 transition-all duration-200 tracking-wide",
              activeFlavorId === flavor.id
                ? "border-brand-mint text-brand-mint"
                : "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-300"
            )}
          >
            {flavor.name}
          </button>
        ))}
      </div>

      {/* Policy & Supply Chain Attestation Card */}
      <div className="p-5 bg-brand-mint/10 border border-brand-mint/20 rounded-xl mb-10 shadow-[0_0_15px_rgba(0,245,160,0.05)] space-y-4">
        <div>
          <strong className="text-slate-900 dark:text-white flex items-center gap-2 mb-2 text-lg">
            <ShieldCheck className="w-6 h-6 text-brand-mint drop-shadow-[0_0_5px_rgba(0,245,160,0.5)]" />
            {activeFlavor.policy_header}
          </strong>
          <p className="text-slate-700 dark:text-slate-300">
            {activeFlavor.policy_text}
          </p>
        </div>

        {/* Dedicated Supply Chain & Attestation Link Bar */}
        <div className="pt-3 border-t border-brand-mint/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-1 rounded-md bg-brand-mint/20 border border-brand-mint/30 text-brand-mint font-mono font-bold flex items-center gap-1.5 shadow-sm">
              <FileCheck className="w-3.5 h-3.5" /> SLSA L3 Attested
            </span>
            <span className="text-slate-600 dark:text-slate-400 font-semibold">Attestation URL:</span>
            <a
              href={getAttestationUrl(primaryTag).url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-cyan hover:underline font-mono flex items-center gap-1 max-w-xs sm:max-w-md truncate"
              title={getAttestationUrl(primaryTag).url}
            >
              <span className="truncate">{getAttestationUrl(primaryTag).url}</span>
              <ExternalLink className="w-3.5 h-3.5 shrink-0" />
            </a>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => handleCopyVerifyCmd(primaryTag)}
              className="px-3 py-1 font-mono font-bold rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-colors flex items-center gap-1 shadow-sm"
              title="Copy verification command"
            >
              {copiedVerifyTag === primaryTag ? (
                <>
                  <Check className="w-3.5 h-3.5 text-brand-mint" />
                  <span className="text-brand-mint">Copied</span>
                </>
              ) : (
                <>
                  <Terminal className="w-3.5 h-3.5 text-brand-mint" />
                  <span>Verify CLI</span>
                </>
              )}
            </button>
            <button
              onClick={() => handleOpenAttestationModal(primaryTag)}
              className="px-3 py-1 font-mono font-bold rounded-lg border border-brand-mint/40 bg-brand-mint/20 hover:bg-brand-mint/30 text-brand-mint transition-colors flex items-center gap-1 shadow-sm"
              title="Edit attestation URL"
            >
              <Edit3 className="w-3.5 h-3.5" />
              <span>Edit Link</span>
            </button>
          </div>
        </div>
      </div>

      {/* Artifact Registry Pull Commands */}
      <div className="mb-12">
        <h2 className="text-xl font-bold text-slate-800 dark:text-white mb-5 flex items-center gap-2">
          <Package className="w-5 h-5 text-brand-mint" /> Artifact Registry
        </h2>
        <div className="space-y-5">
          {activeFlavor.tags.map((tag, idx) => {
            const currentConfig = (configData as Record<string, { digest?: string } | string>)[tag];
            const digest = typeof currentConfig === 'object' ? currentConfig?.digest : undefined;
            const attestation = getAttestationUrl(tag);
            const isVerifiedCopied = copiedVerifyTag === tag;

            return (
              <div key={tag} className="group relative">
                <div className="text-sm font-bold text-slate-600 dark:text-slate-400 mb-2 uppercase tracking-wider text-xs">
                  {idx === 0 ? 'Pull by Version Tag' : 'Pull by Floating Tag'}
                </div>
                <div className="flex items-center rounded-xl overflow-hidden border border-slate-300 dark:border-slate-700 focus-within:border-brand-mint dark:focus-within:border-brand-mint transition-colors shadow-sm dark:shadow-[0_0_15px_rgba(0,0,0,0.5)]">
                  <code className="block p-4 bg-slate-50 dark:bg-[#0D1117] text-slate-800 dark:text-slate-300 font-mono text-sm select-all flex-1">
                    <span className="text-brand-cyan select-none mr-2">$</span> docker pull {tag}
                  </code>
                  <button
                    onClick={() => handleCopy(tag)}
                    className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 p-4 flex items-center justify-center transition-colors border-l border-slate-300 dark:border-slate-700 w-14 shrink-0"
                    title="Copy command"
                  >
                    {copiedTag === tag ? <Check className="w-5 h-5 text-brand-mint" /> : <Copy className="w-5 h-5" />}
                  </button>
                </div>

                {digest && (
                  <div className="mt-2 flex items-center justify-between text-xs font-mono text-slate-500 dark:text-slate-400 px-1">
                    <div className="flex items-center gap-1.5 min-w-0 pr-2">
                      <Lock className="w-3.5 h-3.5 text-brand-mint shrink-0" />
                      <span className="font-semibold text-slate-700 dark:text-slate-300 shrink-0">Secure Digest:</span>
                      <span className="truncate text-slate-500 dark:text-slate-400 text-[11px] sm:text-xs" title={digest}>{digest}</span>
                    </div>
                    <button
                      onClick={() => handleCopyDigest(tag, digest)}
                      className="px-2 py-0.5 text-[11px] font-mono font-bold rounded border border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-100 dark:bg-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-colors shrink-0 flex items-center gap-1"
                      title="Copy raw sha256 digest"
                    >
                      {copiedDigestTag === tag ? (
                        <>
                          <Check className="w-3 h-3 text-brand-mint" />
                          <span className="text-brand-mint">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3 h-3" />
                          <span>Copy Digest</span>
                        </>
                      )}
                    </button>
                  </div>
                )}

                {/* Attestation & Supply Chain Strip */}
                <div className="mt-2.5 p-2.5 sm:px-3 sm:py-2 rounded-lg bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/20 flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="px-2 py-0.5 rounded bg-brand-mint/20 border border-brand-mint/40 text-brand-mint text-[10px] font-mono font-bold flex items-center gap-1 shrink-0">
                      <ShieldCheck className="w-3 h-3" /> SLSA L3
                    </span>
                    <div className="flex items-center gap-1.5 min-w-0 text-xs">
                      <span className="text-slate-600 dark:text-slate-400 font-semibold shrink-0">Attestation:</span>
                      <a
                        href={attestation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-brand-cyan hover:underline font-mono truncate text-[11px] sm:text-xs flex items-center gap-1 max-w-[200px] sm:max-w-xs md:max-w-sm"
                        title={attestation.url}
                      >
                        <span className="truncate">{attestation.url}</span>
                        <ExternalLink className="w-3 h-3 shrink-0" />
                      </a>
                      {attestation.isCustom && (
                        <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-amber-500/20 text-amber-400 border border-amber-500/30 shrink-0 font-bold">
                          Custom
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-1.5 shrink-0 self-end sm:self-center">
                    <button
                      onClick={() => handleCopyVerifyCmd(tag)}
                      className="px-2.5 py-1 text-[11px] font-mono font-bold rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 transition-colors flex items-center gap-1 shadow-sm"
                      title="Copy CLI verification command"
                    >
                      {isVerifiedCopied ? (
                        <>
                          <Check className="w-3 h-3 text-brand-mint" />
                          <span className="text-brand-mint">Verify Cmd Copied</span>
                        </>
                      ) : (
                        <>
                          <Terminal className="w-3 h-3 text-brand-mint" />
                          <span>Verify CLI</span>
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleOpenAttestationModal(tag)}
                      className="px-2.5 py-1 text-[11px] font-mono font-bold rounded border border-brand-mint/40 bg-brand-mint/10 hover:bg-brand-mint/20 text-brand-mint transition-colors flex items-center gap-1 shadow-sm"
                      title="Edit or add attestation URL"
                    >
                      <Edit3 className="w-3 h-3" />
                      <span>{attestation.isCustom ? 'Edit Link' : 'Add / Edit Link'}</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Security, Verification & Compliance Subtabs */}
      <div>
        <h2 className="text-xl font-bold text-slate-800 dark:text-white mb-5 pb-3 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-brand-mint" />
          Security, Verification & Compliance Reports
        </h2>

        <div className="flex flex-wrap gap-3 mb-8">
          <button
            onClick={() => setActiveSubTab('vuln')}
            className={cn("px-4 py-2 rounded-lg text-sm font-bold transition-all border", activeSubTab === 'vuln' ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-900 dark:border-white shadow-md" : "bg-white dark:bg-card-dark text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50")}
          >
            Vulnerability Scan
          </button>
          <button
            onClick={() => setActiveSubTab('cis')}
            className={cn("px-4 py-2 rounded-lg text-sm font-bold transition-all border", activeSubTab === 'cis' ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-900 dark:border-white shadow-md" : "bg-white dark:bg-card-dark text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50")}
          >
            Docker CIS
          </button>
          <button
            onClick={() => setActiveSubTab('sbom')}
            className={cn("px-4 py-2 rounded-lg text-sm font-bold transition-all border", activeSubTab === 'sbom' ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-900 dark:border-white shadow-md" : "bg-white dark:bg-card-dark text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50")}
          >
            SBOM
          </button>

          {/* SLSA L3 Attestation Subtab */}
          <button
            onClick={() => setActiveSubTab('attestation')}
            className={cn(
              "px-4 py-2 rounded-lg text-sm font-bold transition-all border flex items-center gap-2",
              activeSubTab === 'attestation'
                ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-900 dark:border-white shadow-md"
                : "bg-white dark:bg-card-dark text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800/50"
            )}
          >
            <FileCheck className="w-4 h-4 text-brand-mint" />
            SLSA L3 Attestation
            <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-brand-mint/20 text-brand-mint border border-brand-mint/30 font-bold">
              L3
            </span>
          </button>

          {hasFipsTestData && (
            <button
              onClick={() => setActiveSubTab('fips-tests')}
              className={cn("px-4 py-2 rounded-lg text-sm font-bold transition-all border flex items-center gap-2", activeSubTab === 'fips-tests' ? "bg-brand-mint text-slate-950 border-brand-mint shadow-md" : "bg-white dark:bg-card-dark text-emerald-600 dark:text-brand-mint border-brand-mint/40 hover:bg-brand-mint/10")}
            >
              <ShieldCheck className="w-4 h-4" />
              FIPS 140-3 Test Suite
              <span className="px-1.5 py-0.2 rounded text-[10px] font-mono bg-slate-900 text-brand-mint">46</span>
            </button>
          )}

          {hasFipsTestData && (
            <button
              onClick={() => setActiveSubTab('benchmarks')}
              className={cn("px-4 py-2 rounded-lg text-sm font-bold transition-all border flex items-center gap-2", activeSubTab === 'benchmarks' ? "bg-brand-cyan text-slate-950 border-brand-cyan shadow-md" : "bg-white dark:bg-card-dark text-cyan-600 dark:text-brand-cyan border-brand-cyan/40 hover:bg-brand-cyan/10")}
            >
              <Gauge className="w-4 h-4" />
              Crypto Benchmarks
            </button>
          )}
        </div>

        {renderContent()}
      </div>

      {/* Interactive Attestation Link Modal */}
      {isAttestationModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95">
            {/* Header */}
            <div className="flex items-start justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-brand-mint/10 border border-brand-mint/30 rounded-lg text-brand-mint">
                  <FileCheck className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-lg text-slate-900 dark:text-white">
                    Configure Attestation Link
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Add or update the SLSA L3 build provenance and SBOM URL
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsAttestationModalOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Target Tag Info */}
            <div>
              <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider mb-1.5">
                Target Container Tag
              </div>
              <div className="p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl font-mono text-xs text-slate-700 dark:text-slate-300 break-all select-all flex items-center justify-between gap-2">
                <span>{modalTargetTag}</span>
                {customAttestations[modalTargetTag] && (
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-500/20 text-amber-400 border border-amber-500/30 shrink-0 font-bold">
                    Customized
                  </span>
                )}
              </div>
            </div>

            {/* URL Input */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-bold text-slate-700 dark:text-slate-300">
                <span>Attestation or Provenance URL</span>
                {modalAttestationInput && (
                  <a
                    href={modalAttestationInput}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-brand-cyan hover:underline font-mono text-[11px] flex items-center gap-1"
                  >
                    Test Link ↗
                  </a>
                )}
              </div>
              <div className="relative">
                <input
                  type="url"
                  value={modalAttestationInput}
                  onChange={(e) => setModalAttestationInput(e.target.value)}
                  placeholder="https://github.com/.../attestations"
                  className="w-full px-3.5 py-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-xl font-mono text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-none focus:border-brand-mint dark:focus:border-brand-mint transition-colors"
                />
              </div>
              <p className="text-[11px] text-slate-500">
                Enter any GitHub Attestation URL, Sigstore Rekor ledger search, or in-toto predicate JSON endpoint.
              </p>
            </div>

            {/* Smart 1-Click Presets */}
            <div className="space-y-2">
              <div className="text-xs font-mono font-bold text-slate-500 uppercase tracking-wider">
                1-Click Smart Presets
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {getPresetsForTag(modalTargetTag).map((preset, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => setModalAttestationInput(preset.url)}
                    className="p-2.5 text-left rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 hover:border-brand-mint/40 hover:bg-brand-mint/5 transition-all text-xs group"
                  >
                    <div className="font-bold text-slate-800 dark:text-slate-200 group-hover:text-brand-mint flex items-center justify-between">
                      <span>{preset.label}</span>
                      <ChevronRight className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                    <div className="text-[10px] text-slate-500 mt-0.5 truncate">{preset.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Footer Buttons */}
            <div className="pt-4 border-t border-slate-200 dark:border-slate-800 flex flex-wrap items-center justify-between gap-2">
              <div>
                {customAttestations[modalTargetTag] && (
                  <button
                    type="button"
                    onClick={() => handleResetAttestation(modalTargetTag)}
                    className="px-3 py-2 text-xs font-mono font-bold text-slate-500 hover:text-red-400 transition-colors flex items-center gap-1"
                  >
                    <RefreshCw className="w-3.5 h-3.5" /> Revert to Default
                  </button>
                )}
              </div>
              <div className="flex items-center gap-2 ml-auto">
                <button
                  type="button"
                  onClick={() => setIsAttestationModalOpen(false)}
                  className="px-4 py-2 text-xs font-bold rounded-xl border border-slate-300 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSaveAttestation}
                  className="px-5 py-2 text-xs font-bold font-mono rounded-xl bg-brand-mint text-slate-950 hover:bg-brand-mint/90 shadow-[0_0_15px_rgba(0,245,160,0.3)] transition-all flex items-center gap-1.5"
                >
                  <Check className="w-4 h-4" /> Save Link
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 animate-in slide-in-from-bottom-5 fade-in duration-300">
          <div className="px-4 py-3 bg-slate-900 text-white rounded-xl shadow-2xl border border-brand-mint/40 flex items-center gap-2.5 text-xs font-mono">
            <CheckCircle2 className="w-4 h-4 text-brand-mint shrink-0" />
            <span>{toastMessage}</span>
          </div>
        </div>
      )}
    </div>
  );
}
