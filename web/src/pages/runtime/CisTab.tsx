import type { ReactElement } from 'react';
import { CheckCircle2, CircleHelp, XCircle } from 'lucide-react';
import { Badge, Card, EmptyState, SEVERITY_META, Stagger, StaggerItem, StatTile } from '../../components/ui';
import { useAsync } from '../../hooks/useAsync';
import type { Flavor } from '../../lib/catalog';
import { cisControls, loadCis, reportUrl, type CisControl } from '../../lib/reports';
import { LoadingRows, ReportFooter } from './shared';

const STATUS_ICON: Record<CisControl['status'], ReactElement> = {
  pass: <CheckCircle2 className="h-4 w-4 text-emerald-500" aria-label="Passed" />,
  fail: <XCircle className="h-4 w-4 text-red-500" aria-label="Failed" />,
  manual: <CircleHelp className="h-4 w-4 text-slate-400" aria-label="Needs manual review" />,
};

const ORDER: CisControl['status'][] = ['fail', 'pass', 'manual'];

export default function CisTab({ flavor }: { flavor: Flavor }) {
  const report = useAsync(() => loadCis(flavor), [flavor]);

  if (report.status === 'missing' || report.status === 'error') {
    return <EmptyState title="No CIS report yet">The Docker CIS benchmark runs together with the vulnerability scan after each rebuild.</EmptyState>;
  }
  if (report.status === 'loading') return <LoadingRows />;

  const controls = cisControls(report.value).sort((a, b) => ORDER.indexOf(a.status) - ORDER.indexOf(b.status) || a.id.localeCompare(b.id, undefined, { numeric: true }));
  const count = (status: CisControl['status']) => controls.filter((c) => c.status === status).length;

  return (
    <div className="space-y-6">
      <Stagger className="grid grid-cols-3 gap-3">
        <StaggerItem><StatTile label="Passed" value={count('pass')} accent="text-emerald-600 dark:text-brand-mint" /></StaggerItem>
        <StaggerItem><StatTile label="Failed" value={count('fail')} accent={count('fail') ? 'text-red-500' : undefined} /></StaggerItem>
        <StaggerItem><StatTile label="Manual review" value={count('manual')} hint="Not checkable from the image alone" /></StaggerItem>
      </Stagger>

      <Card className="divide-y divide-slate-100 overflow-hidden dark:divide-slate-800">
        {controls.map((control) => (
          <div key={control.id} className="flex items-start gap-3 px-4 py-3">
            <div className="mt-0.5">{STATUS_ICON[control.status]}</div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-xs font-semibold text-slate-500">{control.id}</span>
                <span className="text-sm text-slate-800 dark:text-slate-200">{control.name}</span>
              </div>
              {control.findings.length > 0 && (
                <ul className="mt-1 list-disc space-y-0.5 pl-5 text-xs text-red-600 dark:text-red-400">
                  {control.findings.map((finding, i) => <li key={i}>{finding}</li>)}
                </ul>
              )}
            </div>
            <Badge tone={SEVERITY_META[control.severity].tone}>{SEVERITY_META[control.severity].label}</Badge>
          </div>
        ))}
      </Card>

      <ReportFooter href={reportUrl(flavor, 'cis')} label="Compliance JSON" />
    </div>
  );
}
