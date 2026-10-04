import { useEffect, useMemo, useState } from 'react';
import { motion } from 'motion/react';
import { CheckCircle2, ExternalLink } from 'lucide-react';
import { AnimatedRow, Badge, Card, EASE_OUT, EmptyState, SEVERITY_META, SearchInput, Stagger, StaggerItem, StatTile } from '../../components/ui';
import type { Flavor } from '../../lib/catalog';
import { useAsync } from '../../hooks/useAsync';
import { SEVERITIES, loadVulns, reportUrl, vulnSummary, type Arch, type Severity } from '../../lib/reports';
import { cn } from '../../utils';
import { LoadingRows, ReportFooter } from './shared';

const PAGE_SIZE = 200;

export default function VulnerabilitiesTab({ flavor, arch }: { flavor: Flavor; arch: Arch }) {
  const summary = vulnSummary(flavor, arch);
  const details = useAsync(() => (summary && summary.total > 0 ? loadVulns(flavor, arch) : null), [flavor, arch]);
  const [query, setQuery] = useState('');
  const [severity, setSeverity] = useState<Severity | 'ALL'>('ALL');
  const [fixableOnly, setFixableOnly] = useState(false);
  const [limit, setLimit] = useState(PAGE_SIZE);

  const rows = useMemo(() => {
    if (details.status !== 'ready') return [];
    const q = query.trim().toLowerCase();
    return details.value.filter(
      (v) =>
        (severity === 'ALL' || v.severity === severity) &&
        (!fixableOnly || v.fixed) &&
        (!q || v.id.toLowerCase().includes(q) || v.pkg.toLowerCase().includes(q)),
    );
  }, [details, query, severity, fixableOnly]);

  // Large reports (thousands of CVEs) are rendered a page at a time
  useEffect(() => setLimit(PAGE_SIZE), [query, severity, fixableOnly]);

  if (!summary) {
    return (
      <EmptyState title="Not scanned yet">
        The {arch} image has no vulnerability report yet. Reports are published after the image is built and scanned.
      </EmptyState>
    );
  }

  const present = SEVERITIES.filter((s) => summary.counts[s] > 0);

  return (
    <div className="space-y-6">
      <Stagger className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        <StaggerItem>
          <StatTile
            label="Total"
            value={summary.total}
            hint={`${summary.fixable} with a fix available`}
            accent={summary.total === 0 ? 'text-emerald-600 dark:text-brand-mint' : undefined}
          />
        </StaggerItem>
        {(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((s) => (
          <StaggerItem key={s}>
            <StatTile
              label={SEVERITY_META[s].label}
              value={summary.counts[s] + (s === 'LOW' ? summary.counts.UNKNOWN : 0)}
              hint={s === 'LOW' && summary.counts.UNKNOWN ? `incl. ${summary.counts.UNKNOWN} unknown` : undefined}
            />
          </StaggerItem>
        ))}
      </Stagger>

      {summary.total === 0 ? (
        <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4, ease: EASE_OUT }}>
          <Card className="flex items-start gap-3 border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-500/20 dark:bg-emerald-500/5">
            <motion.span initial={{ scale: 0, rotate: -90 }} animate={{ scale: 1, rotate: 0 }} transition={{ type: 'spring', stiffness: 260, damping: 14, delay: 0.25 }}>
              <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600 dark:text-brand-mint" />
            </motion.span>
            <div>
              <div className="font-semibold text-slate-900 dark:text-white">No known vulnerabilities</div>
              <p className="text-sm text-slate-600 dark:text-slate-400">Trivy found no vulnerabilities in the packages of this image at scan time.</p>
            </div>
          </Card>
        </motion.div>
      ) : (
        <>
          {/* Severity distribution */}
          <div className="space-y-2">
            <div className="flex h-3 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
              {present.map((s, i) => (
                <motion.div
                  key={s}
                  className={SEVERITY_META[s].bar}
                  initial={{ width: 0 }}
                  animate={{ width: `${(summary.counts[s] / summary.total) * 100}%` }}
                  transition={{ duration: 0.8, delay: 0.1 + i * 0.08, ease: EASE_OUT }}
                  title={`${SEVERITY_META[s].label}: ${summary.counts[s]}`}
                />
              ))}
            </div>
          </div>

          {details.status === 'loading' && <LoadingRows />}
          {details.status === 'ready' && (
          <Card className="overflow-hidden">
            <div className="flex flex-col gap-3 border-b border-slate-200 p-4 dark:border-slate-800 md:flex-row md:items-center md:justify-between">
              <div className="flex flex-wrap gap-1.5">
                {(['ALL', ...present] as const).map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setSeverity(s)}
                    className={cn(
                      'rounded-lg px-2.5 py-1 text-xs font-semibold transition-colors',
                      severity === s
                        ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                        : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
                    )}
                  >
                    {s === 'ALL' ? `All ${summary.total}` : `${SEVERITY_META[s].label} ${summary.counts[s]}`}
                  </button>
                ))}
                <label className="ml-1 flex cursor-pointer items-center gap-1.5 text-xs font-semibold text-slate-600 dark:text-slate-300">
                  <input type="checkbox" checked={fixableOnly} onChange={(e) => setFixableOnly(e.target.checked)} className="accent-emerald-500" />
                  Fixable only
                </label>
              </div>
              <SearchInput value={query} onChange={setQuery} placeholder="Search CVE or package" className="md:w-64" />
            </div>

            <div className="custom-scrollbar max-h-[560px] overflow-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 z-10 bg-slate-50 text-xs uppercase tracking-wider text-slate-500 dark:bg-slate-900 dark:text-slate-400">
                  <tr>
                    <th className="px-4 py-2.5 font-semibold">Severity</th>
                    <th className="px-4 py-2.5 font-semibold">Vulnerability</th>
                    <th className="px-4 py-2.5 font-semibold">Package</th>
                    <th className="px-4 py-2.5 font-semibold">Installed</th>
                    <th className="px-4 py-2.5 font-semibold">Fixed in</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                  {rows.slice(0, limit).map((v, i) => (
                    <AnimatedRow key={`${v.id}-${v.pkg}-${i}`} index={i} className="align-top transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="px-4 py-3"><Badge tone={SEVERITY_META[v.severity].tone}>{SEVERITY_META[v.severity].label}</Badge></td>
                      <td className="max-w-md px-4 py-3">
                        {v.url ? (
                          <a href={v.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 font-mono font-semibold text-sky-700 hover:underline dark:text-sky-400">
                            {v.id} <ExternalLink className="h-3 w-3" />
                          </a>
                        ) : (
                          <span className="font-mono font-semibold">{v.id}</span>
                        )}
                        {v.title && <div className="mt-0.5 line-clamp-2 text-xs text-slate-500 dark:text-slate-400">{v.title}</div>}
                      </td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-300">{v.pkg}</td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-500">{v.installed}</td>
                      <td className="px-4 py-3 font-mono text-xs">
                        {v.fixed ? <span className="text-emerald-700 dark:text-emerald-400">{v.fixed}</span> : <span className="text-slate-400">not fixed</span>}
                      </td>
                    </AnimatedRow>
                  ))}
                </tbody>
              </table>
              {rows.length === 0 && <p className="p-6 text-center text-sm text-slate-500">No vulnerability matches these filters.</p>}
              {rows.length > limit && (
                <div className="border-t border-slate-100 p-3 text-center dark:border-slate-800">
                  <button
                    type="button"
                    onClick={() => setLimit((l) => l + PAGE_SIZE)}
                    className="rounded-lg px-3 py-1.5 text-sm font-semibold text-emerald-700 hover:bg-emerald-500/10 dark:text-brand-mint"
                  >
                    Show {Math.min(PAGE_SIZE, rows.length - limit)} more of {rows.length - limit} remaining
                  </button>
                </div>
              )}
            </div>
          </Card>
          )}
        </>
      )}

      <ReportFooter scannedAt={summary.scannedAt} href={reportUrl(flavor, 'vuln', arch)} label="Trivy JSON" />
    </div>
  );
}
