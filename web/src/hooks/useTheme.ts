import { useEffect, useState, type MouseEvent } from 'react';

const STORAGE_KEY = 'theme';

function initialTheme(): boolean {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored === 'dark';
  } catch {
    // Storage can be unavailable (private windows); fall back to dark
  }
  return true;
}

/** Dark / light theme with a circular reveal when the browser supports view transitions. */
export function useTheme() {
  const [isDark, setIsDark] = useState(initialTheme);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark);
    try {
      localStorage.setItem(STORAGE_KEY, isDark ? 'dark' : 'light');
    } catch {
      // Not persisted, the theme still applies for this visit
    }
  }, [isDark]);

  const toggleTheme = (event?: MouseEvent) => {
    const next = !isDark;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!('startViewTransition' in document) || reduceMotion) {
      setIsDark(next);
      return;
    }

    const x = event?.clientX ?? window.innerWidth / 2;
    const y = event?.clientY ?? window.innerHeight / 2;
    const radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
    const transition = (document as Document & { startViewTransition: (cb: () => void) => { ready: Promise<void> } })
      .startViewTransition(() => setIsDark(next));

    transition.ready.then(() => {
      const clipPath = [`circle(0px at ${x}px ${y}px)`, `circle(${radius}px at ${x}px ${y}px)`];
      document.documentElement.animate(
        { clipPath: next ? clipPath : [...clipPath].reverse() },
        {
          duration: 600,
          easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
          pseudoElement: next ? '::view-transition-new(root)' : '::view-transition-old(root)',
        },
      );
    });
  };

  return { isDark, toggleTheme };
}
