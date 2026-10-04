import { motion } from 'motion/react';
import { Info } from 'lucide-react';
import { Card, EASE_OUT, EmptyState } from '../../components/ui';
import { useAsync } from '../../hooks/useAsync';
import type { RuntimeVersion } from '../../lib/catalog';
import { loadBench, type Arch } from '../../lib/reports';
import { LoadingRows, formatDate } from './shared';

function format(value: number | null, metric: string) {
  if (value === null) return '—';
  const digits = value >= 100 ? 0 : 1;
  return `${value.toLocaleString(undefined, { maximumFractionDigits: digits })} ${metric}`;
}

export default function BenchmarksTab({ runtimeVersion, arch }: { runtimeVersion: RuntimeVersion; arch: Arch }) {
  const standard = runtimeVersion.flavors.find((f) => f.id === 'standard') ?? runtimeVersion.flavors[0];
  const bench = useAsync(() => loadBench(standard, arch), [standard, arch]);

  if (bench.status === 'missing' || bench.status === 'error') {
    return (
      <EmptyState title={`No benchmark results for ${arch} yet`}>
        Benchmarks run every week on native amd64 and arm64 runners and compare this FIPS image with a non-FIPS baseline.
      </EmptyState>
    );
  }
  if (bench.status === 'loading') return <LoadingRows />;

  const run = bench.value;
  return (
    <div className="space-y-5">
      <p className="text-sm text-slate-600 dark:text-slate-400">
        <span className="font-mono">{run.image}</span> compared with <strong className="text-slate-800 dark:text-slate-200">{run.baseline.name}</strong>.
        The bar shows FIPS throughput as a share of the baseline.
      </p>

      <Card className="divide-y divide-slate-100 dark:divide-slate-800">
        {run.results.map((result, i) => {
          const ratio = result.fips !== null && result.baseline ? result.fips / result.baseline : null;
          const tone = ratio === null ? 'bg-slate-400' : ratio >= 0.9 ? 'bg-emerald-500' : ratio >= 0.6 ? 'bg-amber-400' : 'bg-red-500';
          return (
            <div key={result.name} className="grid gap-2 px-5 py-4 sm:grid-cols-[minmax(0,14rem)_minmax(0,1fr)_auto] sm:items-center sm:gap-5">
              <div className="font-semibold text-slate-800 dark:text-slate-200">{result.name}</div>
              <div className="h-2.5 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <motion.div
                  className={`h-full rounded-full ${tone}`}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(ratio ?? 0, 1) * 100}%` }}
                  transition={{ duration: 0.8, delay: i * 0.06, ease: EASE_OUT }}
                />
              </div>
              <div className="font-mono text-xs text-slate-600 dark:text-slate-400 sm:text-right">
                <div><span className="text-slate-900 dark:text-white">{format(result.fips, result.metric)}</span> FIPS</div>
                <div>{format(result.baseline, result.metric)} baseline{ratio !== null && <> · <strong>{Math.round(ratio * 100)}%</strong></>}</div>
              </div>
            </div>
          );
        })}
      </Card>

      <p className="flex items-start gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        {run.runs === 1 ? 'Single run' : `Median of ${run.runs} runs`} of {run.seconds}s per measurement on {run.cpu} (linux/{arch}), measured {formatDate(run.ran_at)}.
        Runners are shared and noisy: compare the FIPS / baseline ratio rather than absolute numbers.
      </p>
    </div>
  );
}
