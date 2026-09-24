'use client';
import { useEffect, useState } from 'react';
import { dataUrl } from './paths';

const cache = new Map<string, Promise<unknown>>();

export function fetchJson<T>(path: string): Promise<T> {
  if (!cache.has(path)) {
    cache.set(
      path,
      fetch(dataUrl(path)).then((r) => {
        if (!r.ok) throw new Error(`${r.status} ${path}`);
        return r.json();
      }),
    );
  }
  return cache.get(path) as Promise<T>;
}

/** Client-side fetch of a static JSON file under /data; keeps the previous value while loading. */
export function useJson<T>(path: string | null): { data: T | null; loading: boolean; error: string | null } {
  const [state, setState] = useState<{ data: T | null; loading: boolean; error: string | null }>({
    data: null,
    loading: !!path,
    error: null,
  });
  useEffect(() => {
    if (!path) return;
    let live = true;
    setState((s) => ({ ...s, loading: true }));
    fetchJson<T>(path)
      .then((d) => live && setState({ data: d, loading: false, error: null }))
      .catch((e) => live && setState((s) => ({ ...s, loading: false, error: String(e) })));
    return () => {
      live = false;
    };
  }, [path]);
  return state;
}
