import { ExternalLink, Info, Lock, TriangleAlert } from 'lucide-react';
import { Badge, Card, Command } from '../../components/ui';
import { getCertificate } from '../../lib/reports';
import { formatDate } from './shared';
import type { FipsInfo, Flavor } from '../../lib/catalog';

export default function FipsTab({ fips, flavor }: { fips: FipsInfo; flavor: Flavor }) {
  const command = fips.verify.replace('{tag}', flavor.tags[0]);
  const cert = getCertificate(fips.certificate);

  return (
    <div className="space-y-4">
      <Card className="space-y-4 p-5">
        <div className="flex items-start gap-3">
          <div className="rounded-xl bg-emerald-500/10 p-2.5 text-emerald-600 dark:text-brand-mint">
            <Lock className="h-5 w-5" />
          </div>
          <div>
            <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">Cryptographic module</div>
            <div className="text-lg font-bold text-slate-900 dark:text-white">{fips.module}</div>
          </div>
        </div>
        {fips.certificate && (
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <a
              href={cert?.url ?? `https://csrc.nist.gov/projects/cryptographic-module-validation-program/certificate/${fips.certificate}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1 font-semibold text-emerald-700 hover:underline dark:text-brand-mint"
            >
              CMVP certificate #{fips.certificate} <ExternalLink className="h-3.5 w-3.5" />
            </a>
            {cert?.standard && <Badge>{cert.standard}</Badge>}
            {cert?.status && <Badge tone={cert.status === 'Active' ? 'success' : 'danger'}>{cert.status}</Badge>}
            {cert?.sunset && <Badge>Sunset {new Date(cert.sunset).toLocaleDateString(undefined, { dateStyle: 'medium' })}</Badge>}
            {cert?.versions.length ? <Badge>Covers {cert.versions.join(', ')}</Badge> : null}
          </div>
        )}
        {cert?.alerts.length ? (
          <div className="space-y-1 rounded-xl border border-amber-300 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
            {cert.alerts.map((alert) => (
              <div key={alert} className="flex items-start gap-2"><TriangleAlert className="mt-0.5 h-4 w-4 shrink-0" />{alert}</div>
            ))}
          </div>
        ) : null}
        <div>
          <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">How FIPS mode is enforced</div>
          <p className="mt-1 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{fips.enforcement}</p>
        </div>
      </Card>

      <Card className="space-y-3 p-5">
        <div>
          <h3 className="font-semibold text-slate-900 dark:text-white">Check it yourself</h3>
          <p className="text-sm text-slate-500 dark:text-slate-400">Runs the image and prints the evidence that FIPS mode is active.</p>
        </div>
        <Command command={command} />
      </Card>

      <p className="flex items-start gap-2 text-xs text-slate-500 dark:text-slate-400">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        The image uses a FIPS 140-3 validated cryptographic module. Validation applies to the module, not to the image as a whole.
        {cert && <> Certificate data checked {formatDate(cert.checkedAt)}.</>}
      </p>
    </div>
  );
}
