import { Link } from 'react-router-dom';
import { motion } from 'motion/react';
import { ArrowRight, FileCheck, Lock, PackageCheck, ScanSearch } from 'lucide-react';
import Github from '../components/GithubIcon';
import { LogoMark } from '../components/Logo';
import RuntimeIcon from '../components/RuntimeIcon';
import { Badge, Card, EASE_OUT, Reveal, Stagger, StaggerItem, StatTile, StatusDot } from '../components/ui';
import { REPO_URL, runtimePath, runtimes } from '../lib/catalog';
import { runtimeCounts, versionStatus } from '../lib/reports';

const PRINCIPLES = [
  {
    icon: PackageCheck,
    title: 'Pinned Wolfi packages',
    text: 'Base image digests and package versions are pinned in docker-bake.hcl and refreshed by an automated pull request.',
  },
  {
    icon: FileCheck,
    title: 'Signed provenance and SBOM',
    text: 'GitHub Actions attests every image with SLSA build provenance and a CycloneDX SBOM, verifiable with gh attestation verify.',
  },
  {
    icon: ScanSearch,
    title: 'Scanned on every rebuild',
    text: 'Only images whose inputs changed are rebuilt; each one is scanned with Trivy for vulnerabilities, Docker CIS and its SBOM.',
  },
];

const FLAVORS = [
  { id: 'dev', name: 'Development', text: 'Language runtime with package manager and build tools, for CI and local work.' },
  { id: 'standard', name: 'Standard', text: 'Runtime with a minimal non-root busybox shell, for workloads that need basic tooling. FIPS runtimes only.' },
  { id: 'prod', name: 'Production', text: 'Smallest runtime copied onto scratch: no package manager, and no shell in the distroless flavors.' },
];

export default function Home() {
  const totals = runtimeCounts();

  return (
    <div className="mx-auto max-w-6xl space-y-14 px-5 py-10 sm:px-8 lg:py-14">
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl border border-slate-200 bg-white px-6 py-12 dark:border-slate-800 dark:bg-card-dark sm:px-12">
        <motion.div
          className="pointer-events-none absolute -left-24 -top-24 h-80 w-80 rounded-full bg-brand-mint/20 blur-3xl dark:bg-brand-mint/10"
          animate={{ x: [0, 60, 0], y: [0, 30, 0] }}
          transition={{ duration: 12, repeat: Infinity, ease: 'easeInOut' }}
        />
        <motion.div
          className="pointer-events-none absolute -bottom-32 right-0 h-80 w-80 rounded-full bg-brand-cyan/20 blur-3xl dark:bg-brand-cyan/10"
          animate={{ x: [0, -70, 0], y: [0, -25, 0] }}
          transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
        />
        <div className="relative flex flex-col items-start gap-8 md:flex-row md:items-center">
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, ease: EASE_OUT }}
            className="relative overflow-hidden rounded-3xl bg-slate-900 p-5 shadow-xl shadow-emerald-500/10 dark:bg-bg-dark"
          >
            <motion.div animate={{ y: [0, -4, 0] }} transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}>
              <LogoMark animate className="h-20 w-20 sm:h-24 sm:w-24" />
            </motion.div>
            {/* Scanner sweep: the images are scanned after every rebuild */}
            <motion.div
              aria-hidden="true"
              className="pointer-events-none absolute inset-x-0 h-10 bg-gradient-to-b from-transparent via-brand-mint/35 to-transparent"
              initial={{ top: '-30%' }}
              animate={{ top: ['-30%', '110%'] }}
              transition={{ duration: 2.2, delay: 1.1, repeat: Infinity, repeatDelay: 2.5, ease: 'easeInOut' }}
            />
            <motion.div
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 rounded-3xl ring-1 ring-brand-mint/40"
              animate={{ opacity: [0.2, 0.8, 0.2] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            />
          </motion.div>
          <Stagger className="space-y-4" delay={0.15}>
            <StaggerItem>
              <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white sm:text-5xl">
                Secure <span className="text-emerald-600 dark:text-brand-mint">Runtimes</span>
              </h1>
            </StaggerItem>
            <StaggerItem>
              <p className="max-w-2xl text-lg text-slate-600 dark:text-slate-300">
                Hardened container images for Node.js, Python, Java, Go and Bun, plus FIPS 140-3 builds of OpenSSL, OpenJDK and Node.js. Built on Wolfi, signed with build provenance and scanned after every rebuild.
              </p>
            </StaggerItem>
            <StaggerItem className="flex flex-wrap gap-3">
              <motion.button
                type="button"
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                onClick={() => document.getElementById('catalog')?.scrollIntoView({ behavior: 'smooth' })}
                className="group inline-flex items-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-slate-700 dark:bg-brand-mint dark:text-slate-950 dark:hover:bg-brand-mint/90"
              >
                Browse runtimes
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </motion.button>
              <motion.a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer"
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.96 }}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              >
                <Github className="h-4 w-4" /> Source
              </motion.a>
            </StaggerItem>
          </Stagger>
        </div>
      </section>

      {/* Totals from the published reports */}
      <Stagger className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <StaggerItem><StatTile label="Runtimes" value={runtimes.length} hint={`${runtimes.filter((r) => r.fips).length} with FIPS 140-3`} /></StaggerItem>
        <StaggerItem><StatTile label="Images" value={totals.images} hint="dev, standard and production flavors" /></StaggerItem>
        <StaggerItem><StatTile label="Scanned" value={totals.scanned} hint={`of ${totals.images} images have a report`} /></StaggerItem>
        <StaggerItem>
          <StatTile label="No known CVEs" value={totals.clean} hint={`of ${totals.scanned} scanned images`} accent="text-emerald-600 dark:text-brand-mint" />
        </StaggerItem>
      </Stagger>

      {/* Catalog */}
      <Reveal id="catalog" className="scroll-mt-6 space-y-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Runtimes</h2>
          <div className="flex flex-wrap gap-3 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1.5"><StatusDot status="clean" /> No known CVEs</span>
            <span className="flex items-center gap-1.5"><StatusDot status="low" /> Medium / low</span>
            <span className="flex items-center gap-1.5"><StatusDot status="high" /> Critical / high</span>
            <span className="flex items-center gap-1.5"><StatusDot status="unscanned" /> Not scanned</span>
          </div>
        </div>
        <Stagger className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {runtimes.map((runtime) => {
            const counts = runtimeCounts(runtime);
            return (
              <StaggerItem key={runtime.id}>
                <motion.div whileHover={{ y: -4 }} transition={{ type: 'spring', stiffness: 300, damping: 20 }} className="h-full">
                  <Card className="group flex h-full flex-col gap-4 p-5 transition-shadow hover:shadow-lg hover:shadow-emerald-500/10">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 transition-transform duration-300 group-hover:-rotate-6 group-hover:scale-110 dark:bg-slate-800">
                          <RuntimeIcon icon={runtime.icon} className="h-6 w-6" />
                        </div>
                        <div>
                          <div className="font-bold text-slate-900 dark:text-white">{runtime.title}</div>
                          <div className="text-xs text-slate-500">{runtime.architectures.join(' · ')}</div>
                        </div>
                      </div>
                      {runtime.fips && <Badge tone="brand"><Lock className="h-3 w-3" /> FIPS</Badge>}
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {runtime.versions.map((version) => (
                        <Link
                          key={version.version}
                          to={runtimePath(runtime, version)}
                          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-2.5 py-1 font-mono text-sm text-slate-700 transition-colors hover:border-emerald-500 hover:text-emerald-700 dark:border-slate-700 dark:text-slate-300 dark:hover:border-brand-mint dark:hover:text-brand-mint"
                        >
                          <StatusDot status={versionStatus(version)} />
                          {version.version}
                        </Link>
                      ))}
                    </div>
                    <div className="mt-auto text-xs text-slate-500 dark:text-slate-400">
                      {counts.scanned === 0
                        ? 'No reports published yet'
                        : `${counts.clean} of ${counts.scanned} scanned images have no known CVEs`}
                    </div>
                  </Card>
                </motion.div>
              </StaggerItem>
            );
          })}
        </Stagger>
      </Reveal>

      {/* How the images are produced */}
      <Reveal className="space-y-5">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">How images are built</h2>
        <Stagger className="grid gap-4 md:grid-cols-3">
          {PRINCIPLES.map(({ icon: Icon, title, text }) => (
            <StaggerItem key={title}>
              <Card className="group h-full p-5 transition-colors hover:border-emerald-400/60 dark:hover:border-brand-mint/30">
                <Icon className="h-6 w-6 text-emerald-600 transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:scale-110 dark:text-brand-mint" />
                <h3 className="mt-3 font-semibold text-slate-900 dark:text-white">{title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate-600 dark:text-slate-400">{text}</p>
              </Card>
            </StaggerItem>
          ))}
        </Stagger>
      </Reveal>

      <Reveal className="space-y-5">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Image flavors</h2>
        <Card className="divide-y divide-slate-200 dark:divide-slate-800">
          {FLAVORS.map((flavor) => (
            <div key={flavor.id} className="flex flex-col gap-1 px-5 py-4 sm:flex-row sm:items-center sm:gap-6">
              <div className="w-40 shrink-0">
                <div className="font-semibold text-slate-900 dark:text-white">{flavor.name}</div>
                <div className="font-mono text-xs text-slate-500">{flavor.id}</div>
              </div>
              <p className="text-sm text-slate-600 dark:text-slate-400">{flavor.text}</p>
            </div>
          ))}
        </Card>
      </Reveal>
    </div>
  );
}
