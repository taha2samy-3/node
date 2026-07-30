import { Routes, Route } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import DashboardView from './pages/DashboardView';

export default function App() {
  const [isDark, setIsDark] = useState(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('theme');
      if (stored) return stored === 'dark';
      return true; // Default to dark mode for Chainguard aesthetic
    }
    return true;
  });

  useEffect(() => {
    if (isDark) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [isDark]);

  const toggleTheme = (e?: React.MouseEvent) => {
    const nextIsDark = !isDark;

    if (typeof document !== 'undefined' && 'startViewTransition' in document) {
      const x = e?.clientX ?? window.innerWidth / 2;
      const y = e?.clientY ?? window.innerHeight / 2;
      const endRadius = Math.hypot(
        Math.max(x, window.innerWidth - x),
        Math.max(y, window.innerHeight - y)
      );

      const transition = (document as any).startViewTransition(() => {
        setIsDark(nextIsDark);
      });

      transition.ready.then(() => {
        const clipPath = [
          `circle(0px at ${x}px ${y}px)`,
          `circle(${endRadius}px at ${x}px ${y}px)`,
        ];
        document.documentElement.animate(
          {
            clipPath: nextIsDark ? clipPath : clipPath.reverse(),
          },
          {
            duration: 700,
            easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
            pseudoElement: nextIsDark
              ? '::view-transition-new(root)'
              : '::view-transition-old(root)',
          }
        );
      });
    } else {
      setIsDark(nextIsDark);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-50 dark:bg-bg-dark text-slate-900 dark:text-slate-50 font-sans selection:bg-brand-mint/30 selection:text-brand-mint transition-colors duration-300">
      <Sidebar isDark={isDark} toggleTheme={toggleTheme} />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/runtime/:runtimeId/:version" element={<DashboardView />} />
        </Routes>
      </main>
    </div>
  );
}
