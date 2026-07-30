import { Shield, MemoryStick as Memory, FileCheck, Search } from 'lucide-react';
import ProjectLogo from '../components/ProjectLogo';

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto p-8 space-y-12">
      <header className="space-y-4">
        <div className="flex justify-center my-6">
          <ProjectLogo className="h-20 sm:h-24 md:h-28 w-auto" />
        </div>
        <h1 className="text-4xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Secure Runtimes Environment Dashboard
        </h1>
        <p className="text-xl text-brand-mint font-medium">
          High-Assurance Cryptographic Foundation & Vulnerability Tracking
        </p>
        <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg">
          Welcome to the Secure Runtimes Environment Dashboard. This platform tracks the vulnerability status, compliance standards, and continuous hardening reports of our golden base images across the organization.
        </p>
      </header>

      <section className="space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 text-slate-800 dark:text-slate-200">
          <Shield className="w-6 h-6 text-brand-mint" />
          Core Architecture & Security Controls
        </h2>
        <p className="text-slate-700 dark:text-slate-400">
          Our custom runtime images are built on top of the <strong className="text-slate-900 dark:text-slate-200">Wolfi OS</strong> ecosystem to provide a minimal attack surface, rolling updates, and strict Zero-CVE compliance.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="p-6 bg-white dark:bg-card-dark border border-slate-200 dark:border-emerald-500/20 rounded-xl shadow-sm hover:shadow-[0_0_15px_rgba(0,245,160,0.1)] transition-shadow">
            <h3 className="font-bold mb-2 text-slate-800 dark:text-white">Zero-CVE Base (Wolfi OS)</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">Standard glibc-based secure foundation designed for the container era, eliminating unnecessary OS packages.</p>
          </div>
          <div className="p-6 bg-white dark:bg-card-dark border border-slate-200 dark:border-emerald-500/20 rounded-xl shadow-sm hover:shadow-[0_0_15px_rgba(0,245,160,0.1)] transition-shadow">
            <h3 className="font-bold mb-2 text-slate-800 dark:text-white">Non-Root Execution</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">All images strictly run under non-privileged users with UID 1000 to prevent container escape.</p>
          </div>
          <div className="p-6 bg-white dark:bg-card-dark border border-slate-200 dark:border-emerald-500/20 rounded-xl shadow-sm hover:shadow-[0_0_15px_rgba(0,245,160,0.1)] transition-shadow">
            <h3 className="font-bold mb-2 text-slate-800 dark:text-white">Process Management (Tini)</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">Integrated tini as ENTRYPOINT (PID 1) to handle system signals and prevent zombie processes.</p>
          </div>
          <div className="p-6 bg-white dark:bg-card-dark border border-slate-200 dark:border-emerald-500/20 rounded-xl shadow-sm hover:shadow-[0_0_15px_rgba(0,245,160,0.1)] transition-shadow">
            <h3 className="font-bold mb-2 text-slate-800 dark:text-white">Minimalist Footprint</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">Production images are built directly FROM scratch, copying only the required runtime binaries.</p>
          </div>
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 text-slate-800 dark:text-slate-200">
          <Memory className="w-6 h-6 text-brand-mint" />
          Artifact Tiers
        </h2>
        <div className="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-card-dark shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th className="px-5 py-4 font-semibold text-slate-800 dark:text-slate-200">Flavor</th>
                <th className="px-5 py-4 font-semibold text-slate-800 dark:text-slate-200">Target Stage</th>
                <th className="px-5 py-4 font-semibold text-slate-800 dark:text-slate-200">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800/50">
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/20 transition-colors">
                <td className="px-5 py-4 font-mono font-medium text-brand-cyan">dev-builder</td>
                <td className="px-5 py-4 text-slate-700 dark:text-slate-300">CI/CD & Dev</td>
                <td className="px-5 py-4 text-slate-600 dark:text-slate-400">Contains full language runtime, package managers, and build utilities.</td>
              </tr>
              <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/20 transition-colors">
                <td className="px-5 py-4 font-mono font-medium text-brand-mint">production</td>
                <td className="px-5 py-4 text-slate-700 dark:text-slate-300">Production</td>
                <td className="px-5 py-4 text-slate-600 dark:text-slate-400">Strict, highly secure, minimal-compat runtime from scratch.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-2xl font-bold flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2 text-slate-800 dark:text-slate-200">
          <Search className="w-6 h-6 text-brand-mint" />
          Continuous Security Validation
        </h2>
        <ul className="space-y-4 text-slate-700 dark:text-slate-300">
          <li className="flex items-start gap-3 bg-white dark:bg-card-dark p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <FileCheck className="w-6 h-6 text-brand-mint shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900 dark:text-white block mb-1">Vulnerability Scanning</strong>
              <span className="text-sm text-slate-600 dark:text-slate-400">Continuous package and layer inspection using Trivy.</span>
            </div>
          </li>
          <li className="flex items-start gap-3 bg-white dark:bg-card-dark p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <FileCheck className="w-6 h-6 text-brand-mint shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900 dark:text-white block mb-1">Docker CIS Benchmarks</strong>
              <span className="text-sm text-slate-600 dark:text-slate-400">Verification against CIS Docker hardening guidelines.</span>
            </div>
          </li>
          <li className="flex items-start gap-3 bg-white dark:bg-card-dark p-4 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm">
            <FileCheck className="w-6 h-6 text-brand-mint shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900 dark:text-white block mb-1">Supply Chain Attestation</strong>
              <span className="text-sm text-slate-600 dark:text-slate-400">Full SLSA Build Provenance and CycloneDX SBOM generated natively in our pipeline.</span>
            </div>
          </li>
        </ul>
      </section>
    </div>
  );
}
