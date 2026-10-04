import { Info, Lock } from 'lucide-react';
import { Card, Command } from '../../components/ui';
import type { FipsInfo, Flavor } from '../../lib/catalog';

export default function FipsTab({ fips, flavor }: { fips: FipsInfo; flavor: Flavor }) {
  const command = fips.verify.replace('{tag}', flavor.tags[0]);

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
      </p>
    </div>
  );
}
