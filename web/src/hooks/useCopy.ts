import { useCallback, useEffect, useRef, useState } from 'react';

/** Copy text to the clipboard and remember which item was copied for a short time. */
export function useCopy(resetAfterMs = 1800) {
  const [copied, setCopied] = useState<string | null>(null);
  const timer = useRef<number | undefined>(undefined);

  useEffect(() => () => window.clearTimeout(timer.current), []);

  const copy = useCallback(
    async (text: string, key: string = text) => {
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        return;
      }
      setCopied(key);
      window.clearTimeout(timer.current);
      timer.current = window.setTimeout(() => setCopied(null), resetAfterMs);
    },
    [resetAfterMs],
  );

  return { copied, copy };
}
