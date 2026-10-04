import { Download } from 'lucide-react';
import { Card } from '../../components/ui';

export function formatDate(iso?: string) {
  if (!iso) return undefined;
  const date = new Date(iso);
  return Number.isNaN(date.getTime()) ? undefined : date.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

export function ReportFooter({ scannedAt, href, label }: { scannedAt?: string; href: string; label: string }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400">
      <span>{scannedAt ? `Scanned ${formatDate(scannedAt)} with Trivy` : 'Scanned with Trivy'}</span>
      <a href={href} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 font-semibold hover:text-slate-900 dark:hover:text-white">
        <Download className="h-3.5 w-3.5" /> {label}
      </a>
    </div>
  );
}

/** Placeholder rows while a lazily loaded report is fetched. */
export function LoadingRows({ rows = 6 }: { rows?: number }) {
  return (
    <Card className="space-y-3 p-5" aria-busy="true">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="h-4 animate-pulse rounded bg-slate-200 dark:bg-slate-800" style={{ width: `${90 - (i % 3) * 15}%` }} />
      ))}
    </Card>
  );
}
