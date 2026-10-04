import { useEffect, useState } from 'react';

export type AsyncState<T> =
  | { status: 'missing' }
  | { status: 'loading' }
  | { status: 'ready'; value: T }
  | { status: 'error' };

/** Resolve a promise factory; a factory returning null means there is nothing to load. */
export function useAsync<T>(load: () => Promise<T> | null, deps: unknown[]): AsyncState<T> {
  const [state, setState] = useState<AsyncState<T>>({ status: 'loading' });

  useEffect(() => {
    const promise = load();
    if (!promise) {
      setState({ status: 'missing' });
      return;
    }
    let active = true;
    setState({ status: 'loading' });
    promise.then(
      (value) => active && setState({ status: 'ready', value }),
      () => active && setState({ status: 'error' }),
    );
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
