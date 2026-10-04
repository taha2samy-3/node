import { useMemo, useState, type MouseEvent } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AnimatePresence, motion } from 'motion/react';
import { LayoutDashboard, Moon, Sun } from 'lucide-react';
import Github from './GithubIcon';
import { Logo } from './Logo';
import RuntimeIcon from './RuntimeIcon';
import { SearchInput, StatusDot } from './ui';
import { REPO_URL, runtimePath, runtimes } from '../lib/catalog';
import { versionStatus } from '../lib/reports';
import { cn } from '../utils';

declare const __BUILD_DATE__: string;

interface SidebarProps {
  isDark: boolean;
  toggleTheme: (event?: MouseEvent) => void;
  onNavigate?: () => void;
}

export default function Sidebar({ isDark, toggleTheme, onNavigate }: SidebarProps) {
  const location = useLocation();
  const [query, setQuery] = useState('');

  const groups = useMemo(() => {
    const q = query.trim().toLowerCase();
    return runtimes
      .map((runtime) => ({
        runtime,
        versions: runtime.versions.filter(
          (v) => !q || runtime.title.toLowerCase().includes(q) || runtime.id.includes(q) || v.version.includes(q),
        ),
      }))
      .filter((group) => group.versions.length > 0);
  }, [query]);

  const linkClass = (active: boolean) =>
    cn(
      'relative flex items-center gap-2.5 rounded-lg px-3 py-1.5 text-sm transition-colors',
      active ? 'font-semibold text-slate-900 dark:text-white' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/60 dark:hover:text-slate-100',
    );

  const activePill = (
    <motion.span
      layoutId="nav-active"
      className="absolute inset-0 -z-10 rounded-lg bg-emerald-500/10 ring-1 ring-emerald-500/30 dark:bg-brand-mint/10 dark:ring-brand-mint/25"
      transition={{ type: 'spring', stiffness: 450, damping: 38 }}
    />
  );

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between gap-2 px-5 pb-4 pt-5">
        <Link to="/" onClick={onNavigate} aria-label="Secure Runtimes overview">
          <motion.span className="block" whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
            <Logo animate />
          </motion.span>
        </Link>
      </div>

      <div className="px-4 pb-3">
        <SearchInput value={query} onChange={setQuery} placeholder="Filter runtimes" />
      </div>

      <nav className="custom-scrollbar flex-1 space-y-5 overflow-y-auto px-3 pb-6" aria-label="Runtimes">
        <Link to="/" onClick={onNavigate} className={cn(linkClass(location.pathname === '/'), 'isolate')}>
          {location.pathname === '/' && activePill}
          <LayoutDashboard className="h-4 w-4" />
          Overview
        </Link>

        <AnimatePresence initial={false}>
          {groups.map(({ runtime, versions }) => (
            <motion.div
              key={runtime.id}
              layout
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center gap-2 px-3 pb-1 text-[11px] font-bold uppercase tracking-wider text-slate-500">
                <RuntimeIcon icon={runtime.icon} className="h-3.5 w-3.5" />
                <span className="truncate">{runtime.title}</span>
                {runtime.fips && (
                  <span className="rounded bg-emerald-500/10 px-1 text-[9px] text-emerald-600 dark:text-brand-mint">FIPS</span>
                )}
              </div>
              <div className="space-y-0.5">
                {versions.map((version) => {
                  const path = runtimePath(runtime, version);
                  const active = location.pathname === path;
                  return (
                    <Link key={version.version} to={path} onClick={onNavigate} className={cn(linkClass(active), 'isolate justify-between')}>
                      {active && activePill}
                      <span>Version {version.version}</span>
                      <StatusDot status={versionStatus(version)} />
                    </Link>
                  );
                })}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {groups.length === 0 && <p className="px-3 text-sm text-slate-500">No runtime matches “{query}”.</p>}
      </nav>

      <div className="flex items-center justify-between gap-2 border-t border-slate-200 px-4 py-3 dark:border-slate-800">
        <div className="text-[11px] leading-tight text-slate-500">
          Reports built
          <div className="font-mono font-semibold text-slate-700 dark:text-slate-300">{__BUILD_DATE__}</div>
        </div>
        <div className="flex items-center gap-1">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="Source on GitHub"
            className="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
          >
            <Github className="h-4 w-4" />
          </a>
          <button
            type="button"
            onClick={(e) => toggleTheme(e)}
            aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
            className="overflow-hidden rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:hover:bg-slate-800 dark:hover:text-white"
          >
            <AnimatePresence mode="wait" initial={false}>
              <motion.span
                key={isDark ? 'sun' : 'moon'}
                className="block"
                initial={{ rotate: -90, opacity: 0, scale: 0.5 }}
                animate={{ rotate: 0, opacity: 1, scale: 1 }}
                exit={{ rotate: 90, opacity: 0, scale: 0.5 }}
                transition={{ duration: 0.25 }}
              >
                {isDark ? <Sun className="h-4 w-4 text-amber-400" /> : <Moon className="h-4 w-4 text-indigo-500" />}
              </motion.span>
            </AnimatePresence>
          </button>
        </div>
      </div>
    </div>
  );
}
