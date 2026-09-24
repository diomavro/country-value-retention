'use client';
import { useMemo } from 'react';
import type { Flows, FlowRow } from './types';
import { useJson } from './useJson';
import { normaliseRows } from './names';
import { isSpecial } from './concepts';

export function useFlows(year: number) {
  const { data, loading, error } = useJson<Flows>(`cy/flows_${year}.json`);
  const rows = useMemo(() => (data ? normaliseRows(data.rows) : []), [data]);
  return { flows: data, rows, loading, error };
}

export function sumBy(rows: FlowRow[], key: (r: FlowRow) => string): Map<string, { value: number; rows: FlowRow[] }> {
  const m = new Map<string, { value: number; rows: FlowRow[] }>();
  rows.forEach((r) => {
    const k = key(r);
    const e = m.get(k) || { value: 0, rows: [] };
    e.value += r.value;
    e.rows.push(r);
    m.set(k, e);
  });
  return m;
}

export const foreignRows = (rows: FlowRow[]) => rows.filter((r) => r.mechanism !== 'retained_domestic');

/** Recipients shown individually: every non-country aggregate (never folded away) plus the top-N countries. */
export function recipientGroups(rows: FlowRow[], topN = 8) {
  const by = [...sumBy(foreignRows(rows), (r) => r.recipient).entries()].sort((a, b) => b[1].value - a[1].value);
  const special = by.filter(([k]) => isSpecial(k)).map(([k]) => k);
  const countries = by.filter(([k]) => !isSpecial(k)).map(([k]) => k);
  const top = countries.slice(0, topN);
  const other = countries.slice(topN);
  const group = (r: string) => (r === 'CY' ? 'CY' : other.includes(r) ? 'OTHER' : r);
  return { top, special, other, group };
}
