import { useMemo, useState } from 'react';
import { AnimatedRow, Card, EmptyState, SearchInput } from '../../components/ui';
import { useAsync } from '../../hooks/useAsync';
import type { Flavor } from '../../lib/catalog';
import { loadSbom, reportUrl, sbomComponents, type Arch } from '../../lib/reports';
import { LoadingRows, ReportFooter } from './shared';

export default function SbomTab({ flavor, arch }: { flavor: Flavor; arch: Arch }) {
  const report = useAsync(() => loadSbom(flavor, arch), [flavor, arch]);
  const [query, setQuery] = useState('');

  const components = useMemo(() => (report.status === 'ready' ? sbomComponents(report.value) : []), [report]);
  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return q ? components.filter((c) => c.name.toLowerCase().includes(q) || c.licenses.some((l) => l.toLowerCase().includes(q))) : components;
  }, [components, query]);

  if (report.status === 'missing' || report.status === 'error') {
    return <EmptyState title="No SBOM yet">The CycloneDX SBOM is generated with the vulnerability scan after each rebuild.</EmptyState>;
  }
  if (report.status === 'loading') return <LoadingRows />;

  return (
    <div className="space-y-4">
      <Card className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-200 p-4 dark:border-slate-800 sm:flex-row sm:items-center sm:justify-between">
          <div className="text-sm text-slate-600 dark:text-slate-400">
            <span className="font-mono font-bold text-slate-900 dark:text-white">{components.length}</span> components (CycloneDX)
          </div>
          <SearchInput value={query} onChange={setQuery} placeholder="Search component or license" className="sm:w-72" />
        </div>
        <div className="custom-scrollbar max-h-[560px] overflow-auto">
          <table className="w-full text-left text-sm">
            <thead className="sticky top-0 z-10 bg-slate-50 text-xs uppercase tracking-wider text-slate-500 dark:bg-slate-900 dark:text-slate-400">
              <tr>
                <th className="px-4 py-2.5 font-semibold">Component</th>
                <th className="px-4 py-2.5 font-semibold">Version</th>
                <th className="px-4 py-2.5 font-semibold">Type</th>
                <th className="px-4 py-2.5 font-semibold">License</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {rows.map((c, i) => (
                <AnimatedRow key={`${c.name}-${c.version}-${i}`} index={i} className="transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/40">
                  <td className="px-4 py-2.5 font-mono text-xs font-semibold text-slate-800 dark:text-slate-200" title={c.purl}>{c.name}</td>
                  <td className="px-4 py-2.5 font-mono text-xs text-slate-500">{c.version}</td>
                  <td className="px-4 py-2.5 text-xs text-slate-500">{c.type}</td>
                  <td className="px-4 py-2.5 text-xs text-slate-600 dark:text-slate-400">{c.licenses.join(', ') || '—'}</td>
                </AnimatedRow>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && <p className="p-6 text-center text-sm text-slate-500">No component matches “{query}”.</p>}
        </div>
      </Card>
      <ReportFooter href={reportUrl(flavor, 'sbom', arch)} label="CycloneDX JSON" />
    </div>
  );
}
