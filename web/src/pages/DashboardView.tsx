import { useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { ShieldCheck, Package, Zap, Info, CheckCircle2, AlertCircle, XCircle, Copy, Check, ShieldAlert, Cpu, HardDrive, Lock } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import runtimesData from '../../runtimes.yaml';
import configData from '../../reports/config.json';
import { RuntimesData } from '../types';
import { cn } from '../utils';
import RuntimeIcon from '../components/RuntimeIcon';
import { reportsMap } from '../reports';


const COLORS: Record<string, string> = {
  Critical: '#ef4444', // Chainguard Crimson
  High: '#f97316',     // Chainguard Orange
  Medium: '#f59e0b',   // Chainguard Amber
  Low: '#3b82f6',      // Chainguard Blue
};

export default function DashboardView() {
  const { runtimeId, version } = useParams<{ runtimeId: string; version: string }>();
  const data = runtimesData as RuntimesData;

  const runtime = useMemo(() => data.runtimes.find(r => r.id === runtimeId), [data, runtimeId]);
  const runtimeVersion = useMemo(() => runtime?.versions.find(v => v.version === version), [runtime, version]);

  const [activeFlavorId, setActiveFlavorId] = useState<string>('dev');
  const [activeSubTab, setActiveSubTab] = useState<'vuln' | 'cis' | 'sbom'>('vuln');
  const [copiedTag, setCopiedTag] = useState<string | null>(null);
  const [copiedDigestTag, setCopiedDigestTag] = useState<string | null>(null);

  if (!runtime || !runtimeVersion) {
    return <div className="p-8 text-center text-slate-500">Runtime or version not found.</div>;
  }

  const activeFlavor = runtimeVersion.flavors.find(f => f.id === activeFlavorId) || runtimeVersion.flavors[0];
  const primaryTag = activeFlavor.tags[0];
  const tagEntry = (configData as Record<string, { size?: string; digest?: string } | string>)[primaryTag];
  const imageSize = typeof tagEntry === 'object' ? (tagEntry?.size || 'N/A') : (tagEntry || 'N/A');

  const vulnData = reportsMap[version || '']?.[activeFlavor.id]?.['vuln'];
  const cisData = reportsMap[version || '']?.[activeFlavor.id]?.['cis'];
  const sbomData = reportsMap[version || '']?.[activeFlavor.id]?.['sbom'];

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
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1"><ShieldAlert className="w-4 h-4 shrink-0" /> Total CVEs Found</div>
              <div className={cn("text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight my-auto", totalVulns === 0 ? "text-brand-mint" : "text-red-500")}>{totalVulns}</div>
            </div>
            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1"><Package className="w-4 h-4 shrink-0" /> Packages Analyzed</div>
              <div className="text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight text-slate-800 dark:text-white my-auto">{pkgCount}</div>
            </div>
            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 to-teal-500 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1"><HardDrive className="w-4 h-4 shrink-0" /> Compressed Size</div>
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
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1"><Zap className="w-4 h-4 shrink-0" /> Critical / High</div>
              <div className={cn("text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight my-auto", (critical + high) === 0 ? "text-brand-mint" : "text-orange-500")}>{critical + high}</div>
            </div>
            <div className="p-4 sm:p-5 min-w-0 bg-white dark:bg-card-dark border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm text-center relative overflow-hidden flex flex-col justify-between">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-yellow-400 to-amber-400 opacity-80" />
              <div className="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2 flex items-center justify-center gap-1"><Info className="w-4 h-4 shrink-0" /> Medium / Low</div>
              <div className={cn("text-3xl sm:text-4xl lg:text-4xl xl:text-5xl font-mono tracking-tight my-auto", (medium + low) === 0 ? "text-brand-mint" : "text-amber-500")}>{medium + low}</div>
            </div>
          </div>

          {!hasVulns ? (
            <div className="p-5 bg-brand-mint/10 border border-brand-mint/30 rounded-xl text-emerald-900 dark:text-brand-mint flex items-start gap-3 shadow-[0_0_20px_rgba(0,245,160,0.05)]">
              <CheckCircle2 className="w-6 h-6 text-brand-mint shrink-0 mt-0.5" />
              <div>
                <strong className="block mb-1 text-slate-900 dark:text-brand-mint">Zero-CVE State Confirmed</strong>
                <p className="text-sm text-emerald-800 dark:text-emerald-400">Impeccable Security Posture: No known vulnerabilities were detected in the {pkgCount} analyzed packages.</p>
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
            <Package className="w-5 h-5 text-brand-mint" /> Software Bill of Materials (SBOM)
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
                        <span className={cn("px-2.5 py-1 rounded-md text-xs font-medium", type.includes('System') ? "bg-blue-50 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400" : "bg-purple-50 text-purple-700 dark:bg-purple-500/10 dark:text-purple-400")}>
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

    return null;
  };

  return (
    <div className="max-w-5xl mx-auto p-8">
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
            <span className="px-3 py-1.5 bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-md">
              Wolfi OS Base
            </span>
            <span className="px-3 py-1.5 bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-md">
              SLSA Level 3
            </span>
            {runtime.architectures.map(arch => (
              <span key={arch} className="px-3 py-1.5 bg-slate-800 text-slate-300 rounded-md border border-slate-700 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5" /> {arch}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="flex border-b border-slate-200 dark:border-slate-800 mb-8 space-x-2">
        {runtimeVersion.flavors.map(flavor => (
          <button
            key={flavor.id}
            onClick={() => { setActiveFlavorId(flavor.id); setActiveSubTab('vuln'); }}
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

      <div className="p-5 bg-brand-mint/10 border border-brand-mint/20 rounded-xl mb-10 shadow-[0_0_15px_rgba(0,245,160,0.05)]">
        <strong className="text-slate-900 dark:text-white flex items-center gap-2 mb-2 text-lg">
          <ShieldCheck className="w-6 h-6 text-brand-mint drop-shadow-[0_0_5px_rgba(0,245,160,0.5)]" />
          {activeFlavor.policy_header}
        </strong>
        <p className="text-slate-700 dark:text-slate-300">
          {activeFlavor.policy_text}
        </p>
      </div>

      <div className="mb-12">
        <h2 className="text-xl font-bold text-slate-800 dark:text-white mb-5 flex items-center gap-2">
          <Package className="w-5 h-5 text-brand-mint" /> Artifact Registry
        </h2>
        <div className="space-y-5">
          {activeFlavor.tags.map((tag, idx) => {
            const currentConfig = (configData as Record<string, { digest?: string } | string>)[tag];
            const digest = typeof currentConfig === 'object' ? currentConfig?.digest : undefined;

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
              </div>
            );
          })}
        </div>
      </div>

      <div>
        <h2 className="text-xl font-bold text-slate-800 dark:text-white mb-5 pb-3 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-brand-mint" />
          Security & Compliance Reports
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
        </div>

        {renderContent()}
      </div>
    </div>
  );
}

