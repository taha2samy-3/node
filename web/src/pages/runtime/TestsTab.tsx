import { useMemo, useState, type ReactElement } from 'react';
import { CheckCircle2, CircleSlash, TriangleAlert, XCircle } from 'lucide-react';
import { Card, EmptyState, SearchInput, Stagger, StaggerItem, StatTile, AnimatedRow } from '../../components/ui';
import { useAsync } from '../../hooks/useAsync';
import type { Flavor } from '../../lib/catalog';
import { loadTests, type Arch, type TestResult } from '../../lib/reports';
import { cn } from '../../utils';
import { LoadingRows, formatDate } from './shared';

const OUTCOME_ICON: Record<TestResult['outcome'], ReactElement> = {
  passed: <CheckCircle2 className="h-4 w-4 text-emerald-500" aria-label="Passed" />,
  failed: <XCircle className="h-4 w-4 text-red-500" aria-label="Failed" />,
  xfail: <TriangleAlert className="h-4 w-4 text-amber-500" aria-label="Known limitation" />,
  skipped: <CircleSlash className="h-4 w-4 text-slate-400" aria-label="Skipped" />,
};

type Filter = 'all' | TestResult['outcome'];

const OUTCOME_ORDER: TestResult['outcome'][] = ['failed', 'xfail', 'passed', 'skipped'];
const FILTER_LABEL: Record<Filter, string> = { all: 'All', failed: 'Failed', xfail: 'Known limitations', passed: 'Passed', skipped: 'Skipped' };

// "test_rsa_1024_is_rejected" -> "RSA 1024 is rejected"
function humanize(name: string) {
  const text = name.replace(/^test_/, '').replace(/\[(.+)\]$/, ' ($1)').replace(/_/g, ' ');
  return text.charAt(0).toUpperCase() + text.slice(1);
}

export default function TestsTab({ flavor, arch }: { flavor: Flavor; arch: Arch }) {
  const run = useAsync(() => loadTests(flavor, arch), [flavor, arch]);
  const [filter, setFilter] = useState<Filter>('all');
  const [query, setQuery] = useState('');

  const rows = useMemo(() => {
    if (run.status !== 'ready') return [];
    const q = query.trim().toLowerCase();
    return run.value.tests
      .filter((t) => (filter === 'all' || t.outcome === filter) && (!q || t.name.toLowerCase().includes(q) || t.classname.toLowerCase().includes(q)))
      .sort((a, b) => OUTCOME_ORDER.indexOf(a.outcome) - OUTCOME_ORDER.indexOf(b.outcome));
  }, [run, filter, query]);

  if (run.status === 'missing' || run.status === 'error') {
    return (
      <EmptyState title={`No FIPS test results for ${arch} yet`}>
        The FIPS test suites run on amd64 and arm64 after each build of this image, and on every pull request that changes it.
      </EmptyState>
    );
  }
  if (run.status === 'loading') return <LoadingRows />;

  const { summary, suite, image, ran_at } = run.value;
  return (
    <div className="space-y-6">
      <Stagger className="grid grid-cols-2 gap-3 md:grid-cols-5">
        <StaggerItem><StatTile label="Passed" value={summary.passed} accent="text-emerald-600 dark:text-brand-mint" /></StaggerItem>
        <StaggerItem><StatTile label="Failed" value={summary.failed} accent={summary.failed ? 'text-red-500' : undefined} /></StaggerItem>
        <StaggerItem>
          <StatTile label="Known limitations" value={summary.xfail ?? 0} hint="Expected behaviour of the certified module" accent={summary.xfail ? 'text-amber-500' : undefined} />
        </StaggerItem>
        <StaggerItem><StatTile label="Skipped" value={summary.skipped} hint="Not applicable to this flavor" /></StaggerItem>
        <StaggerItem><StatTile label="Duration" value={`${summary.duration.toFixed(1)}s`} /></StaggerItem>
      </Stagger>

      <Card className="overflow-hidden">
        <div className="flex flex-col gap-3 border-b border-slate-200 p-4 dark:border-slate-800 md:flex-row md:items-center md:justify-between">
          <div className="flex flex-wrap gap-1.5">
            {(['all', 'failed', 'xfail', 'passed', 'skipped'] as const).map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => setFilter(f)}
                className={cn(
                  'rounded-lg px-2.5 py-1 text-xs font-semibold transition-colors',
                  filter === f
                    ? 'bg-slate-900 text-white dark:bg-white dark:text-slate-900'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700',
                )}
              >
                {FILTER_LABEL[f]} {f === 'all' ? summary.total : summary[f] ?? 0}
              </button>
            ))}
          </div>
          <SearchInput value={query} onChange={setQuery} placeholder="Search tests" className="md:w-64" />
        </div>
        <div className="custom-scrollbar max-h-[560px] overflow-auto">
          <table className="w-full text-left text-sm">
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {rows.map((test, i) => (
                <AnimatedRow key={`${test.classname}-${test.name}`} index={i} className="align-top transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/40">
                  <td className="w-8 py-3 pl-4">{OUTCOME_ICON[test.outcome]}</td>
                  <td className="px-3 py-3">
                    <div className="font-medium text-slate-800 dark:text-slate-200">{humanize(test.name)}</div>
                    <div className="font-mono text-[11px] text-slate-500">{test.classname}::{test.name}</div>
                    {test.outcome !== 'passed' && test.message && (
                      <pre className="mt-1.5 max-h-40 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-2 font-mono text-[11px] text-slate-600 dark:bg-slate-900 dark:text-slate-400">
                        {test.message}
                      </pre>
                    )}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-right font-mono text-xs text-slate-500">{test.duration.toFixed(2)}s</td>
                </AnimatedRow>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && <p className="p-6 text-center text-sm text-slate-500">No test matches these filters.</p>}
        </div>
      </Card>

      <div className="text-xs text-slate-500 dark:text-slate-400">
        <span className="font-mono">{suite}</span> against <span className="font-mono">{image}</span> on linux/{arch}
        {formatDate(ran_at) && <> · {formatDate(ran_at)}</>}
      </div>
    </div>
  );
}
