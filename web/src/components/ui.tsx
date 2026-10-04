import { useEffect, type ReactNode } from 'react';
import { animate, motion, useMotionValue, useTransform } from 'motion/react';
import { Check, Copy, Search } from 'lucide-react';
import { PendingMark } from './Logo';
import { useCopy } from '../hooks/useCopy';
import type { ScanStatus, Severity } from '../lib/reports';
import { cn } from '../utils';

export const EASE_OUT = [0.22, 1, 0.36, 1] as const;

// ==========================================
// Layout
// ==========================================
export function Card({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <div className={cn('rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-800 dark:bg-card-dark', className)}>
      {children}
    </div>
  );
}

/** Children fade and rise in one after another when the group scrolls into view. */
export function Stagger({ className, children, delay = 0 }: { className?: string; children: ReactNode; delay?: number }) {
  return (
    <motion.div
      className={className}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.1 }}
      variants={{ hidden: {}, show: { transition: { staggerChildren: 0.07, delayChildren: delay } } }}
    >
      {children}
    </motion.div>
  );
}

/** A block that slides up into place the first time it scrolls into view. */
export function Reveal({ id, className, children }: { id?: string; className?: string; children: ReactNode }) {
  return (
    <motion.section
      id={id}
      className={className}
      initial={{ opacity: 0, y: 28 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.15 }}
      transition={{ duration: 0.55, ease: EASE_OUT }}
    >
      {children}
    </motion.section>
  );
}

/** Table row that cascades in; only the first rows animate so long tables stay fast. */
export function AnimatedRow({ index, className, children }: { index: number; className?: string; children: ReactNode }) {
  const animated = index < 24;
  return (
    <motion.tr
      className={className}
      initial={animated ? { opacity: 0, x: -8 } : false}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: animated ? index * 0.025 : 0, ease: EASE_OUT }}
    >
      {children}
    </motion.tr>
  );
}

export function StaggerItem({ className, children }: { className?: string; children: ReactNode }) {
  return (
    <motion.div
      className={className}
      variants={{
        hidden: { opacity: 0, y: 14 },
        show: { opacity: 1, y: 0, transition: { duration: 0.45, ease: EASE_OUT } },
      }}
    >
      {children}
    </motion.div>
  );
}

// ==========================================
// Badges and status
// ==========================================
export type Tone = 'neutral' | 'success' | 'warning' | 'danger' | 'info' | 'brand';

const TONES: Record<Tone, string> = {
  neutral: 'border-slate-200 bg-slate-100 text-slate-700 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-300',
  warning: 'border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300',
  danger: 'border-red-200 bg-red-50 text-red-700 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300',
  info: 'border-sky-200 bg-sky-50 text-sky-700 dark:border-sky-500/30 dark:bg-sky-500/10 dark:text-sky-300',
  brand: 'border-emerald-300/60 bg-brand-mint/10 text-emerald-700 dark:border-brand-mint/30 dark:text-brand-mint',
};

export function Badge({ tone = 'neutral', className, children }: { tone?: Tone; className?: string; children: ReactNode }) {
  return (
    <span className={cn('inline-flex items-center gap-1.5 rounded-md border px-2 py-0.5 text-xs font-semibold', TONES[tone], className)}>
      {children}
    </span>
  );
}

export const STATUS_META: Record<ScanStatus, { label: string; dot: string; tone: Tone }> = {
  clean: { label: 'No known vulnerabilities', dot: 'bg-emerald-500', tone: 'success' },
  low: { label: 'Medium / low vulnerabilities', dot: 'bg-amber-400', tone: 'warning' },
  high: { label: 'Critical / high vulnerabilities', dot: 'bg-red-500', tone: 'danger' },
  unscanned: { label: 'Not scanned yet', dot: 'bg-slate-400 dark:bg-slate-600', tone: 'neutral' },
};

export function StatusDot({ status, className }: { status: ScanStatus; className?: string }) {
  return (
    <span className={cn('relative inline-flex h-2 w-2 shrink-0', className)} title={STATUS_META[status].label}>
      {status === 'high' && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-red-500 opacity-60" />}
      <span className={cn('relative inline-flex h-2 w-2 rounded-full', STATUS_META[status].dot)} />
    </span>
  );
}

export const SEVERITY_META: Record<Severity, { label: string; bar: string; tone: Tone }> = {
  CRITICAL: { label: 'Critical', bar: 'bg-red-600', tone: 'danger' },
  HIGH: { label: 'High', bar: 'bg-orange-500', tone: 'danger' },
  MEDIUM: { label: 'Medium', bar: 'bg-amber-400', tone: 'warning' },
  LOW: { label: 'Low', bar: 'bg-sky-500', tone: 'info' },
  UNKNOWN: { label: 'Unknown', bar: 'bg-slate-400', tone: 'neutral' },
};

// ==========================================
// Numbers
// ==========================================
/** Counts up from 0 to the value. */
export function Counter({ value }: { value: number }) {
  const count = useMotionValue(0);
  const text = useTransform(count, (v) => Math.round(v).toLocaleString());

  useEffect(() => {
    const controls = animate(count, value, { duration: 0.9, ease: EASE_OUT });
    return () => controls.stop();
  }, [count, value]);

  return <motion.span>{text}</motion.span>;
}

export function StatTile({ label, value, hint, accent }: { label: string; value: number | string; hint?: string; accent?: string }) {
  return (
    <Card className="p-4">
      <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">{label}</div>
      <div className={cn('mt-1 font-mono text-3xl font-bold tracking-tight text-slate-900 dark:text-white', accent)}>
        {typeof value === 'number' ? <Counter value={value} /> : value}
      </div>
      {hint && <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">{hint}</div>}
    </Card>
  );
}

// ==========================================
// Copyable commands
// ==========================================
export function CopyButton({ text, label = 'Copy', className }: { text: string; label?: string; className?: string }) {
  const { copied, copy } = useCopy();
  const done = copied === text;

  return (
    <button
      type="button"
      onClick={() => copy(text)}
      aria-label={done ? 'Copied' : label}
      title={done ? 'Copied' : label}
      className={cn(
        'inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-slate-500 transition-colors hover:bg-slate-200 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-white',
        className,
      )}
    >
      <motion.span key={done ? 'done' : 'idle'} initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.2 }}>
        {done ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
      </motion.span>
    </button>
  );
}

export function Command({ command, prompt = true }: { command: string; prompt?: boolean }) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-slate-50 py-1.5 pl-4 pr-1.5 dark:border-slate-800 dark:bg-[#0D1117]">
      <code className="min-w-0 flex-1 overflow-x-auto whitespace-nowrap font-mono text-[13px] text-slate-800 dark:text-slate-200">
        {prompt && <span className="mr-2 select-none text-emerald-600 dark:text-brand-mint">$</span>}
        {command}
      </code>
      <CopyButton text={command} label="Copy command" />
    </div>
  );
}

// ==========================================
// Tabs
// ==========================================
export interface TabItem<T extends string> {
  id: T;
  label: string;
  count?: number;
  icon?: ReactNode;
}

/** Underlined tabs whose indicator slides to the active tab. */
export function Tabs<T extends string>({ id, items, active, onChange }: { id: string; items: TabItem<T>[]; active: T; onChange: (tab: T) => void }) {
  return (
    <div role="tablist" className="flex gap-1 overflow-x-auto border-b border-slate-200 dark:border-slate-800">
      {items.map((item) => {
        const selected = item.id === active;
        return (
          <button
            key={item.id}
            role="tab"
            type="button"
            aria-selected={selected}
            onClick={() => onChange(item.id)}
            className={cn(
              'relative flex shrink-0 items-center gap-2 px-3.5 py-2.5 text-sm font-semibold transition-colors',
              selected ? 'text-slate-900 dark:text-white' : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200',
            )}
          >
            {item.icon}
            {item.label}
            {item.count !== undefined && (
              <span className="rounded-full bg-slate-100 px-1.5 py-px font-mono text-[11px] text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                {item.count}
              </span>
            )}
            {selected && (
              <motion.span
                layoutId={`${id}-indicator`}
                className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-emerald-500 dark:bg-brand-mint"
                transition={{ type: 'spring', stiffness: 500, damping: 40 }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
}

/** Pill selector whose highlight slides to the chosen option. */
export function Segmented<T extends string>({ id, label, options, value, onChange }: {
  id: string;
  label: string;
  options: { id: T; label: ReactNode }[];
  value: T;
  onChange: (value: T) => void;
}) {
  return (
    <div className="inline-flex flex-wrap gap-1 rounded-xl border border-slate-200 bg-white p-1 dark:border-slate-800 dark:bg-card-dark" role="radiogroup" aria-label={label}>
      {options.map((option) => {
        const selected = option.id === value;
        return (
          <button
            key={option.id}
            type="button"
            role="radio"
            aria-checked={selected}
            onClick={() => onChange(option.id)}
            className={cn(
              'relative isolate flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-semibold transition-colors',
              selected ? 'text-white dark:text-slate-900' : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white',
            )}
          >
            {selected && (
              <motion.span
                layoutId={`${id}-pill`}
                className="absolute inset-0 -z-10 rounded-lg bg-slate-900 dark:bg-white"
                transition={{ type: 'spring', stiffness: 450, damping: 38 }}
              />
            )}
            {option.label}
          </button>
        );
      })}
    </div>
  );
}

// ==========================================
// Inputs and empty states
// ==========================================
export function SearchInput({ value, onChange, placeholder, className }: { value: string; onChange: (v: string) => void; placeholder: string; className?: string }) {
  return (
    <label className={cn('relative block', className)}>
      <span className="sr-only">{placeholder}</span>
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-900 placeholder-slate-400 outline-none transition-colors focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-brand-mint"
      />
    </label>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <Card className="flex flex-col items-center gap-3 px-6 py-12 text-center">
      <PendingMark className="h-14 w-14 text-slate-400 dark:text-slate-600" />
      <div className="font-semibold text-slate-800 dark:text-slate-200">{title}</div>
      {children && <div className="max-w-md text-sm text-slate-500 dark:text-slate-400">{children}</div>}
    </Card>
  );
}
