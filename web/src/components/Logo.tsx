import { useId } from 'react';
import { motion } from 'motion/react';
import { BANDS, CHECK_PATH, CHECK_WIDTH, CUTS, SHIELD_PATH } from '../brand/geometry';
import { cn } from '../utils';

const EASE_OUT = [0.22, 1, 0.36, 1] as const;

interface LogoMarkProps {
  className?: string;
  // Slide the bands in and draw the check when mounted
  animate?: boolean;
}

/** The layered-shield mark, drawn from the same geometry as assets/brand. */
export function LogoMark({ className, animate = false }: LogoMarkProps) {
  const id = useId().replace(/:/g, '');

  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden="true">
      <defs>
        {BANDS.map((band, i) => (
          <linearGradient key={i} id={`${id}-b${i}`} x1="9" y1={band.top} x2="55" y2={band.bottom} gradientUnits="userSpaceOnUse">
            <stop offset="0" stopColor={band.from} />
            <stop offset="1" stopColor={band.to} />
          </linearGradient>
        ))}
        <mask id={`${id}-cut`} maskUnits="userSpaceOnUse" x="0" y="0" width="64" height="64">
          <rect width="64" height="64" fill="#fff" />
          {CUTS.map((cut) => (
            <rect key={cut.y} x="0" y={cut.y} width="64" height={cut.height} fill="#000" />
          ))}
          <motion.path
            d={CHECK_PATH}
            fill="none"
            stroke="#000"
            strokeWidth={CHECK_WIDTH}
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={animate ? { pathLength: 0 } : false}
            animate={{ pathLength: 1 }}
            transition={{ delay: 0.6, duration: 0.45, ease: 'easeOut' }}
          />
        </mask>
        <clipPath id={`${id}-shield`}>
          <path d={SHIELD_PATH} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${id}-shield)`} mask={`url(#${id}-cut)`}>
        {BANDS.map((band, i) => (
          <motion.rect
            key={i}
            x="0"
            y={band.top}
            width="64"
            height={band.bottom - band.top}
            fill={`url(#${id}-b${i})`}
            initial={animate ? { x: -64 } : false}
            animate={{ x: 0 }}
            transition={{ delay: 0.1 + i * 0.12, duration: 0.6, ease: EASE_OUT }}
          />
        ))}
      </g>
    </svg>
  );
}

/** Outline of the mark used for empty states ("not scanned yet"). */
export function PendingMark({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 64 64" className={className} aria-hidden="true" fill="none" stroke="currentColor">
      <motion.path
        d={SHIELD_PATH}
        strokeWidth="1.6"
        strokeDasharray="3 3"
        animate={{ strokeDashoffset: [0, -12] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: 'linear' }}
      />
      {CUTS.map((cut) => (
        <line key={cut.y} x1="12" x2="52" y1={cut.y + cut.height / 2} y2={cut.y + cut.height / 2} strokeWidth="1.6" opacity="0.5" />
      ))}
    </svg>
  );
}

/** Mark + wordmark. */
export function Logo({ className, animate = false }: { className?: string; animate?: boolean }) {
  return (
    <span className={cn('flex items-center gap-2.5', className)}>
      <LogoMark className="h-8 w-8 shrink-0" animate={animate} />
      <span className="text-[17px] font-extrabold leading-none tracking-tight">
        <span className="text-slate-900 dark:text-white">Secure</span>{' '}
        <span className="text-emerald-600 dark:text-brand-mint">Runtimes</span>
      </span>
    </span>
  );
}
