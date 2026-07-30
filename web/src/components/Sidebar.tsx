import { Link, useLocation } from 'react-router-dom';
import { Moon, Sun, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { cn } from '../utils';
import runtimesData from '../../runtimes.yaml';
import RuntimeIcon from './RuntimeIcon';
import ProjectLogo from './ProjectLogo';
import { RuntimesData } from '../types';
import { reportsMap } from '../reports';

interface SidebarProps {
  isDark: boolean;
  toggleTheme: (e?: React.MouseEvent) => void;
}

export default function Sidebar({ isDark, toggleTheme }: SidebarProps) {
  const location = useLocation();
  const data = runtimesData as RuntimesData;

  return (
    <aside className="w-64 bg-slate-900 dark:bg-card-dark border-r border-slate-800 flex flex-col shrink-0 text-slate-300 transition-colors duration-300">
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 overflow-hidden hover:opacity-90 transition-opacity">
          <ProjectLogo isDark={true} className="h-7 w-auto" />
        </Link>
        <motion.button 
          whileHover={{ scale: 1.08 }}
          whileTap={{ scale: 0.92 }}
          onClick={(e) => toggleTheme(e)} 
          className="relative p-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-300 hover:text-amber-400 dark:hover:text-amber-300 transition-colors shrink-0 overflow-hidden border border-slate-700/50 shadow-sm"
          title="Toggle Theme"
        >
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={isDark ? 'sun' : 'moon'}
              initial={{ rotate: -120, opacity: 0, scale: 0.4 }}
              animate={{ rotate: 0, opacity: 1, scale: 1 }}
              exit={{ rotate: 120, opacity: 0, scale: 0.4 }}
              transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            >
              {isDark ? (
                <Sun className="w-4 h-4 text-amber-400" />
              ) : (
                <Moon className="w-4 h-4 text-indigo-400" />
              )}
            </motion.div>
          </AnimatePresence>
        </motion.button>
      </div>
      <nav className="p-4 space-y-6 overflow-y-auto flex-1 custom-scrollbar">
        <div>
          <Link
            to="/"
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors border-l-2',
              location.pathname === '/'
                ? 'bg-brand-mint/10 border-brand-mint text-brand-mint'
                : 'border-transparent text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
            )}
          >
            <RuntimeIcon icon="shield" className={cn('w-5 h-5', location.pathname === '/' ? 'text-brand-mint' : 'text-slate-500')} />
            Dashboard Home
          </Link>
        </div>
        
        {data.runtimes.map((runtime) => (
          <div key={runtime.id} className="space-y-1">
            <div className="px-3 py-2 text-xs font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
              <RuntimeIcon icon={runtime.icon} className="w-4 h-4" />
              {runtime.title}
            </div>
            {runtime.versions.map((v) => {
              const path = `/runtime/${runtime.id}/${v.version}`;
              const active = location.pathname === path;
              
              let hasZeroCve = false;
              const prodVulnData = reportsMap[v.version]?.['prod']?.['vuln'];
              
              if (prodVulnData?.Results) {
                let totalVulns = 0;
                for (const res of prodVulnData.Results) {
                  if (res.Vulnerabilities) {
                    totalVulns += res.Vulnerabilities.length;
                  }
                }
                hasZeroCve = totalVulns === 0;
              } else if (prodVulnData) {
                // If the report exists but has no Results/Vulnerabilities, it's zero
                hasZeroCve = true;
              }

              return (
                <Link
                  key={v.version}
                  to={path}
                  className={cn(
                    'flex items-center justify-between px-3 py-2 rounded-r-lg text-sm font-medium transition-colors border-l-2',
                    active
                      ? 'bg-brand-mint/10 border-brand-mint text-brand-mint shadow-[inset_2px_0_10px_rgba(0,245,160,0.1)]'
                      : 'border-transparent text-slate-400 hover:bg-slate-800/50 hover:text-slate-200'
                  )}
                >
                  <span className="flex items-center gap-2">
                    Version {v.version}
                  </span>
                  {hasZeroCve && (
                    <CheckCircle2 className={cn("w-4 h-4", active ? "text-brand-mint" : "text-emerald-500/70")} />
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500 font-mono text-center">
        v2.4.1 • Chainguard Spec
      </div>
    </aside>
  );
}
