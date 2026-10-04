import { useEffect, useState } from 'react';
import { Route, Routes, useLocation } from 'react-router-dom';
import { AnimatePresence, MotionConfig, motion } from 'motion/react';
import { Menu, X } from 'lucide-react';
import Sidebar from './components/Sidebar';
import { Logo } from './components/Logo';
import { EASE_OUT } from './components/ui';
import { useTheme } from './hooks/useTheme';
import Home from './pages/Home';
import RuntimePage from './pages/RuntimePage';
import NotFound from './pages/NotFound';

export default function App() {
  const { isDark, toggleTheme } = useTheme();
  const location = useLocation();
  const [menuOpen, setMenuOpen] = useState(false);

  // New page: start at the top and close the mobile menu
  useEffect(() => {
    document.getElementById('main')?.scrollTo({ top: 0 });
    setMenuOpen(false);
  }, [location.pathname]);

  return (
    <MotionConfig reducedMotion="user">
      <div className="flex h-screen overflow-hidden bg-slate-50 text-slate-900 dark:bg-bg-dark dark:text-slate-50">
        <aside className="hidden w-72 shrink-0 border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-card-dark lg:block">
          <Sidebar isDark={isDark} toggleTheme={toggleTheme} />
        </aside>

        <AnimatePresence>
          {menuOpen && (
            <>
              <motion.div
                className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-sm lg:hidden"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setMenuOpen(false)}
              />
              <motion.aside
                className="fixed inset-y-0 left-0 z-50 w-80 max-w-[85vw] border-r border-slate-200 bg-white shadow-2xl dark:border-slate-800 dark:bg-card-dark lg:hidden"
                initial={{ x: '-100%' }}
                animate={{ x: 0 }}
                exit={{ x: '-100%' }}
                transition={{ duration: 0.3, ease: EASE_OUT }}
              >
                <button
                  type="button"
                  onClick={() => setMenuOpen(false)}
                  aria-label="Close menu"
                  className="absolute right-3 top-4 rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
                >
                  <X className="h-5 w-5" />
                </button>
                <Sidebar isDark={isDark} toggleTheme={toggleTheme} onNavigate={() => setMenuOpen(false)} />
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-card-dark/80 lg:hidden">
            <Logo />
            <button
              type="button"
              onClick={() => setMenuOpen(true)}
              aria-label="Open menu"
              className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            >
              <Menu className="h-5 w-5" />
            </button>
          </header>

          <main id="main" className="custom-scrollbar flex-1 overflow-y-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={location.pathname}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25, ease: EASE_OUT }}
              >
                <Routes location={location}>
                  <Route path="/" element={<Home />} />
                  <Route path="/runtime/:runtimeId/:version" element={<RuntimePage />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </motion.div>
            </AnimatePresence>
          </main>
        </div>
      </div>
    </MotionConfig>
  );
}
