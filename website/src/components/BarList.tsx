'use client';
import React from 'react';
import type { Prov } from '@/lib/types';
import { usePopHandlers, ProvCard } from './Prov';

export interface BarItem {
  key: string;
  label: string;
  value: number;
  display: string;
  color?: string;
  prov: Prov;
  note?: string;
}

function Row({ it, max, selected, onSelect }: { it: BarItem; max: number; selected: boolean; onSelect?: (k: string) => void }) {
  const h = usePopHandlers(
    () => <ProvCard value={it.display} title={it.label} prov={it.prov} extra={it.note ? <p className="small">{it.note}</p> : undefined} />,
    onSelect ? () => onSelect(it.key) : undefined,
  );
  return (
    <>
      <div className={`bl-name${selected ? ' row-sel' : ''}`} title={it.label} style={selected ? { color: 'var(--ink)', fontWeight: 600 } : undefined}>
        {it.label}
        {it.note ? ' *' : ''}
      </div>
      <button type="button" className="bl-bar mark" aria-pressed={onSelect ? selected : undefined} aria-label={`${it.label}: ${it.display}`} {...h} style={{ background: 'none', border: 'none', padding: 0, font: 'inherit', color: 'inherit', textAlign: 'left' }}>
        <span className="bl-fill" style={{ width: `${Math.max(0.3, (it.value / max) * 78)}%`, background: it.color || 'var(--s1)', outline: selected ? '2px solid var(--ink)' : undefined }} />
        <span className="bl-val">{it.display}</span>
      </button>
    </>
  );
}

/** Horizontal bar list: one hue, sorted, direct value labels; each bar carries provenance and can select. */
export default function BarList({ items, selected, onSelect, ariaLabel }: { items: BarItem[]; selected?: string | null; onSelect?: (k: string) => void; ariaLabel: string }) {
  const max = Math.max(...items.map((i) => i.value), 1e-9);
  return (
    <div className="barlist" role="group" aria-label={ariaLabel}>
      {items.map((it) => (
        <Row key={it.key} it={it} max={max} selected={selected === it.key} onSelect={onSelect} />
      ))}
    </div>
  );
}
