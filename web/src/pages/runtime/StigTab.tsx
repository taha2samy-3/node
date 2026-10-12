import { useState, type ReactElement } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { BadgeCheck, CheckCircle2, ChevronDown, MinusCircle, ShieldCheck, XCircle } from 'lucide-react';
import { Badge, Card, EmptyState, SearchInput, Stagger, StaggerItem, StatTile, type Tone } from '../../components/ui';
import { useAsync } from '../../hooks/useAsync';
import type { Flavor } from '../../lib/catalog';
import { loadStig, reportUrl, type Arch, type Severity, type StigRule } from '../../lib/reports';
import { LoadingRows, ReportFooter } from './shared';
import { cn } from '../../utils';

const STATUS_ICON: Record<StigRule['status'], ReactElement> = {
  pass: <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" aria-label="Passed" />,
  fail: <XCircle className="h-4 w-4 shrink-0 text-red-500" aria-label="Failed" />,
  notapplicable: <MinusCircle className="h-4 w-4 shrink-0 text-slate-400" aria-label="Not Applicable" />,
  manual: <MinusCircle className="h-4 w-4 shrink-0 text-slate-400" aria-label="Manual Review" />,
};

const SEV_BADGE: Record<Severity, { label: string; tone: Tone }> = {
  CRITICAL: { label: 'CAT I (HIGH)', tone: 'danger' },
  HIGH: { label: 'CAT I (HIGH)', tone: 'danger' },
  MEDIUM: { label: 'CAT II (MED)', tone: 'warning' },
  LOW: { label: 'CAT III (LOW)', tone: 'info' },
  UNKNOWN: { label: 'INFO', tone: 'neutral' },
};

type FilterStatus = 'all' | 'fail' | 'pass' | 'notapplicable';
type FilterSev = 'ALL' | 'HIGH' | 'MEDIUM' | 'LOW';

export default function StigTab({ flavor, arch }: { flavor: Flavor; arch: Arch }) {
  const report = useAsync(() => loadStig(flavor, arch), [flavor, arch]);
  const [statusFilter, setStatusFilter] = useState<FilterStatus>('all');
  const [sevFilter, setSevFilter] = useState<FilterSev>('ALL');
  const [search, setSearch] = useState('');
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  if (report.status === 'missing' || report.status === 'error') {
    return (
      <EmptyState title="No Chainguard STIG report yet">
        The Chainguard DISA STIG profile scan runs together with the security pipeline after each build.
      </EmptyState>
    );
  }
  if (report.status === 'loading') return <LoadingRows />;

  const stigData = report.value;
  const rules = stigData.rules ?? [];
  const summary = stigData.summary;

  const toggleExpand = (id: string) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const filteredRules = rules.filter((rule) => {
    if (statusFilter !== 'all' && rule.status !== statusFilter) return false;
    if (sevFilter !== 'ALL' && rule.severity !== sevFilter) return false;
    if (search.trim()) {
      const q = search.toLowerCase();
      const matchId = rule.id.toLowerCase().includes(q);
      const matchTitle = rule.title.toLowerCase().includes(q);
      const matchDesc = rule.description?.toLowerCase().includes(q);
      const matchIdent = rule.idents?.some((i) => i.toLowerCase().includes(q));
      if (!matchId && !matchTitle && !matchDesc && !matchIdent) return false;
    }
    return true;
  });

  const scoreAccent =
    summary.score >= 90
      ? 'text-emerald-600 dark:text-brand-mint'
      : summary.score >= 70
        ? 'text-amber-500'
        : 'text-red-500';

  return (
    <div className="space-y-6">
      {/* Profile Overview Banner */}
      <Card className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-emerald-500" />
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              DISA General Purpose OS (GPOS) SRG Baseline
            </h2>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Validated against the official Chainguard STIG Security Profile (<code className="font-mono text-[11px] text-slate-600 dark:text-slate-300">ssg-chainguard-gpos-ds.xml</code>) using OpenSCAP.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="brand"><BadgeCheck className="h-3.5 w-3.5" /> STIG Profile</Badge>
          <Badge tone="neutral">XCCDF 1.2</Badge>
          <Badge tone="neutral">OpenSCAP 1.3</Badge>
        </div>
      </Card>

      {/* Summary Stat Tiles */}
      <Stagger className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StaggerItem>
          <StatTile
            label="Compliance Score"
            value={`${summary.score}%`}
            accent={scoreAccent}
            hint="Applicable checks passing"
          />
        </StaggerItem>
        <StaggerItem>
          <StatTile
            label="Passed Rules"
            value={summary.passed}
            accent="text-emerald-600 dark:text-brand-mint"
            hint="Fully conforming"
          />
        </StaggerItem>
        <StaggerItem>
          <StatTile
            label="Failed Rules"
            value={summary.failed}
            accent={summary.failed > 0 ? 'text-red-500' : 'text-emerald-600 dark:text-brand-mint'}
            hint={summary.failed > 0 ? 'Requires attention' : 'Zero non-compliances'}
          />
        </StaggerItem>
        <StaggerItem>
          <StatTile
            label="Not Applicable"
            value={summary.notapplicable}
            hint="OS / service not in image"
          />
        </StaggerItem>
      </Stagger>

      {/* Filters & Search */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap items-center gap-1.5" role="group" aria-label="Status filter">
          <button
            type="button"
            id="filter-stig-all"
            onClick={() => setStatusFilter('all')}
            className={cn(
              'rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors',
              statusFilter === 'all'
                ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
            )}
          >
            All ({rules.length})
          </button>
          <button
            type="button"
            id="filter-stig-fail"
            onClick={() => setStatusFilter('fail')}
            className={cn(
              'rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors',
              statusFilter === 'fail'
                ? 'bg-red-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
            )}
          >
            Failed ({summary.failed})
          </button>
          <button
            type="button"
            id="filter-stig-pass"
            onClick={() => setStatusFilter('pass')}
            className={cn(
              'rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors',
              statusFilter === 'pass'
                ? 'bg-emerald-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
            )}
          >
            Passed ({summary.passed})
          </button>
          <button
            type="button"
            id="filter-stig-na"
            onClick={() => setStatusFilter('notapplicable')}
            className={cn(
              'rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors',
              statusFilter === 'notapplicable'
                ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
            )}
          >
            N/A ({summary.notapplicable})
          </button>
        </div>

        <div className="flex items-center gap-2">
          <select
            id="filter-stig-sev"
            aria-label="Filter by severity"
            value={sevFilter}
            onChange={(e) => setSevFilter(e.target.value as FilterSev)}
            className="rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-700 outline-none transition-colors dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300"
          >
            <option value="ALL">All Severities</option>
            <option value="HIGH">High (CAT I)</option>
            <option value="MEDIUM">Medium (CAT II)</option>
            <option value="LOW">Low (CAT III)</option>
          </select>
          <SearchInput
            placeholder="Search STIG rule or CCI..."
            value={search}
            onChange={setSearch}
            className="w-full sm:w-64"
          />
        </div>
      </div>

      {/* Rules List */}
      <Card className="divide-y divide-slate-100 overflow-hidden dark:divide-slate-800">
        {filteredRules.length === 0 ? (
          <div className="px-6 py-12 text-center text-sm text-slate-500 dark:text-slate-400">
            No STIG rules match the active filters.
          </div>
        ) : (
          filteredRules.map((rule) => {
            const isExpanded = !!expanded[rule.id];
            const sevMeta = SEV_BADGE[rule.severity] ?? SEV_BADGE.MEDIUM;

            return (
              <div key={rule.id} className="transition-colors hover:bg-slate-50/50 dark:hover:bg-slate-800/20">
                <div
                  role="button"
                  tabIndex={0}
                  onClick={() => toggleExpand(rule.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      toggleExpand(rule.id);
                    }
                  }}
                  className="flex cursor-pointer items-start gap-3 px-4 py-3 text-left focus:outline-none"
                >
                  <div className="mt-0.5">{STATUS_ICON[rule.status]}</div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-xs font-semibold text-slate-500 dark:text-slate-400">
                        {rule.id.replace(/^xccdf_mil\.disa\.stig_rule_/, '').replace(/_rule$/, '')}
                      </span>
                      {rule.idents && rule.idents.length > 0 && (
                        <span className="rounded bg-slate-100 px-1.5 py-0.5 font-mono text-[10px] font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                          {rule.idents.join(', ')}
                        </span>
                      )}
                    </div>
                    <div className="mt-1 text-sm font-medium text-slate-800 dark:text-slate-200">
                      {rule.title}
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-2">
                    <Badge tone={sevMeta.tone}>{sevMeta.label}</Badge>
                    <ChevronDown
                      className={cn(
                        'h-4 w-4 text-slate-400 transition-transform duration-200',
                        isExpanded && 'rotate-180',
                      )}
                    />
                  </div>
                </div>

                <AnimatePresence>
                  {isExpanded && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.2 }}
                      className="overflow-hidden border-t border-slate-100 bg-slate-50/50 px-5 py-3.5 text-xs text-slate-600 dark:border-slate-800/60 dark:bg-slate-900/40 dark:text-slate-400"
                    >
                      {rule.description && (
                        <div className="space-y-1">
                          <span className="font-semibold text-slate-700 dark:text-slate-300">Vulnerability Description:</span>
                          <p className="leading-relaxed">{rule.description}</p>
                        </div>
                      )}
                      {rule.rationale && (
                        <div className="mt-2.5 space-y-1">
                          <span className="font-semibold text-slate-700 dark:text-slate-300">Rationale:</span>
                          <p className="leading-relaxed">{rule.rationale}</p>
                        </div>
                      )}
                      <div className="mt-2.5 font-mono text-[11px] text-slate-400">
                        Full XCCDF Rule ID: {rule.id}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })
        )}
      </Card>

      <ReportFooter href={reportUrl(flavor, 'stig', arch)} label="STIG Compliance JSON" />
    </div>
  );
}
