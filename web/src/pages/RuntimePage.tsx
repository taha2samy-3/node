import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { AnimatePresence, motion } from 'motion/react';
import { ChevronRight, Cpu, FileCheck, Lock, Package, ScanSearch, ShieldCheck } from 'lucide-react';
import RuntimeIcon from '../components/RuntimeIcon';
import { Badge, EASE_OUT, STATUS_META, StatusDot, Tabs, type TabItem } from '../components/ui';
import { findRuntime, findVersion, runtimePath, type Runtime, type RuntimeVersion } from '../lib/catalog';
import { flavorStatus, vulnSummary } from '../lib/reports';
import { cn } from '../utils';
import NotFound from './NotFound';
import ImageCard from './runtime/ImageCard';
import VulnerabilitiesTab from './runtime/VulnerabilitiesTab';
import CisTab from './runtime/CisTab';
import SbomTab from './runtime/SbomTab';
import ProvenanceTab from './runtime/ProvenanceTab';
import FipsTab from './runtime/FipsTab';

type ReportTab = 'vuln' | 'cis' | 'sbom' | 'provenance' | 'fips';

export default function RuntimePage() {
  const { runtimeId, version } = useParams<{ runtimeId: string; version: string }>();
  const runtime = findRuntime(runtimeId);
  const runtimeVersion = findVersion(runtime, version);

  if (!runtime || !runtimeVersion) {
    return <NotFound message={`There is no runtime “${runtimeId} ${version}” in the catalog.`} />;
  }
  // Remount per version so the selected flavor and tab start fresh
  return <RuntimeView key={`${runtime.id}/${runtimeVersion.version}`} runtime={runtime} runtimeVersion={runtimeVersion} />;
}

function RuntimeView({ runtime, runtimeVersion }: { runtime: Runtime; runtimeVersion: RuntimeVersion }) {
  const flavors = runtimeVersion.flavors;
  const [flavorId, setFlavorId] = useState(flavors.find((f) => f.id === 'prod')?.id ?? flavors[0].id);
  const [tab, setTab] = useState<ReportTab>('vuln');
  const flavor = flavors.find((f) => f.id === flavorId) ?? flavors[0];
  const status = flavorStatus(flavor);
  const vulns = vulnSummary(flavor);

  const tabs: TabItem<ReportTab>[] = [
    { id: 'vuln', label: 'Vulnerabilities', count: vulns?.total, icon: <ScanSearch className="h-4 w-4" /> },
    { id: 'cis', label: 'Docker CIS', icon: <ShieldCheck className="h-4 w-4" /> },
    { id: 'sbom', label: 'SBOM', icon: <Package className="h-4 w-4" /> },
    { id: 'provenance', label: 'Provenance', icon: <FileCheck className="h-4 w-4" /> },
    ...(runtime.fips ? [{ id: 'fips' as const, label: 'FIPS 140-3', icon: <Lock className="h-4 w-4" /> }] : []),
  ];

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-5 py-8 sm:px-8 lg:py-10">
      {/* Header */}
      <header className="space-y-5">
        <nav className="flex items-center gap-1.5 text-sm text-slate-500" aria-label="Breadcrumb">
          <Link to="/" className="hover:text-slate-900 dark:hover:text-white">Overview</Link>
          <ChevronRight className="h-3.5 w-3.5" />
          <span className="text-slate-700 dark:text-slate-300">{runtime.title}</span>
        </nav>

        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div className="flex items-center gap-4">
            <motion.div
              initial={{ rotate: -12, scale: 0.8, opacity: 0 }}
              animate={{ rotate: 0, scale: 1, opacity: 1 }}
              transition={{ duration: 0.5, ease: EASE_OUT }}
              className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-card-dark"
            >
              <RuntimeIcon icon={runtime.icon} className="h-8 w-8" />
            </motion.div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
                {runtime.title} <span className="font-mono font-semibold text-slate-400">{runtimeVersion.version}</span>
              </h1>
              <div className="mt-2 flex flex-wrap gap-2">
                {runtime.fips && <Badge tone="brand"><Lock className="h-3 w-3" /> {runtime.fips.module}</Badge>}
                {runtime.architectures.map((arch) => (
                  <Badge key={arch}><Cpu className="h-3 w-3" /> {arch}</Badge>
                ))}
                <Badge>Wolfi base</Badge>
              </div>
            </div>
          </div>

          {runtime.versions.length > 1 && (
            <div className="flex flex-wrap gap-1.5" aria-label="Other versions">
              {runtime.versions.map((v) => (
                <Link
                  key={v.version}
                  to={runtimePath(runtime, v)}
                  className={cn(
                    'rounded-lg border px-2.5 py-1 font-mono text-sm transition-colors',
                    v.version === runtimeVersion.version
                      ? 'border-slate-900 bg-slate-900 text-white dark:border-white dark:bg-white dark:text-slate-900'
                      : 'border-slate-200 text-slate-600 hover:border-slate-400 dark:border-slate-700 dark:text-slate-300 dark:hover:border-slate-500',
                  )}
                >
                  {v.version}
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Flavor selector */}
        <div className="inline-flex flex-wrap gap-1 rounded-xl border border-slate-200 bg-white p-1 dark:border-slate-800 dark:bg-card-dark" role="radiogroup" aria-label="Image flavor">
          {flavors.map((f) => {
            const selected = f.id === flavor.id;
            return (
              <button
                key={f.id}
                type="button"
                role="radio"
                aria-checked={selected}
                onClick={() => setFlavorId(f.id)}
                className={cn(
                  'relative isolate flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-semibold transition-colors',
                  selected ? 'text-white dark:text-slate-900' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white',
                )}
              >
                {selected && (
                  <motion.span
                    layoutId="flavor-pill"
                    className="absolute inset-0 -z-10 rounded-lg bg-slate-900 dark:bg-white"
                    transition={{ type: 'spring', stiffness: 450, damping: 38 }}
                  />
                )}
                <StatusDot status={flavorStatus(f)} />
                {f.name}
              </button>
            );
          })}
        </div>
      </header>

      <AnimatePresence mode="wait">
        <motion.div
          key={flavor.id}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.2, ease: EASE_OUT }}
          className="space-y-8"
        >
          <ImageCard flavor={flavor} statusLabel={STATUS_META[status].label} statusTone={STATUS_META[status].tone} />

          <section className="space-y-5">
            <Tabs id="report-tabs" items={tabs} active={tab} onChange={setTab} />
            <AnimatePresence mode="wait">
              <motion.div
                key={tab}
                role="tabpanel"
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.18, ease: EASE_OUT }}
              >
                {tab === 'vuln' && <VulnerabilitiesTab flavor={flavor} />}
                {tab === 'cis' && <CisTab flavor={flavor} />}
                {tab === 'sbom' && <SbomTab flavor={flavor} />}
                {tab === 'provenance' && <ProvenanceTab flavor={flavor} />}
                {tab === 'fips' && runtime.fips && <FipsTab fips={runtime.fips} flavor={flavor} />}
              </motion.div>
            </AnimatePresence>
          </section>
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
