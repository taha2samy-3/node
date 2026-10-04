import { ExternalLink, HardDrive, Hash } from 'lucide-react';
import { Badge, Card, Command, CopyButton, type Tone } from '../../components/ui';
import { packageUrl, type Flavor } from '../../lib/catalog';
import { getImageMeta } from '../../lib/reports';

export default function ImageCard({ flavor, statusLabel, statusTone }: { flavor: Flavor; statusLabel: string; statusTone: Tone }) {
  const primary = flavor.tags[0];
  const meta = getImageMeta(primary);

  return (
    <Card className="overflow-hidden">
      <div className="space-y-2 border-b border-slate-200 p-5 dark:border-slate-800">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="text-lg font-bold text-slate-900 dark:text-white">{flavor.policy_header}</h2>
          <Badge tone={statusTone}>{statusLabel}</Badge>
        </div>
        <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">{flavor.policy_text}</p>
      </div>

      <div className="space-y-4 p-5">
        <div className="space-y-2">
          {flavor.tags.map((tag, i) => (
            <div key={tag}>
              <div className="mb-1 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                {i === 0 ? 'Pull' : 'Alias'}
              </div>
              <Command command={`docker pull ${tag}`} />
            </div>
          ))}
        </div>

        <div className="grid gap-3 text-sm sm:grid-cols-[minmax(0,1fr)_auto_auto] sm:items-center">
          <div className="flex min-w-0 items-center gap-2 text-slate-600 dark:text-slate-400">
            <Hash className="h-4 w-4 shrink-0 text-slate-400" />
            {meta.digest ? (
              <>
                <code className="truncate font-mono text-xs" title={meta.digest}>{meta.digest}</code>
                <CopyButton text={meta.digest} label="Copy digest" />
              </>
            ) : (
              <span className="text-xs">Digest available after the first publish</span>
            )}
          </div>
          <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400" title="Compressed size of the linux/amd64 image">
            <HardDrive className="h-4 w-4 text-slate-400" />
            <span className="font-mono text-xs">{meta.size ?? 'n/a'}</span>
            <span className="text-xs text-slate-400">amd64</span>
          </div>
          <a
            href={packageUrl(primary)}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-700 hover:underline dark:text-brand-mint"
          >
            Package page <ExternalLink className="h-3.5 w-3.5" />
          </a>
        </div>
      </div>
    </Card>
  );
}
