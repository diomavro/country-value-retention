'use client';
import React, { useMemo, useState } from 'react';
import type { FlowRow } from '@/lib/types';
import { MECHANISMS, SPECIAL_RECIPIENTS, splitUrls } from '@/lib/concepts';
import { eurM, pct } from '@/lib/format';

/** Country -> industry -> mechanism -> source -> calculation text, for the rows behind one total. */
export default function Drill({ rows, title, gdp, onClose }: { rows: FlowRow[]; title: string; gdp: number; onClose?: () => void }) {
  const [all, setAll] = useState(false);
  const sorted = useMemo(() => [...rows].sort((a, b) => b.value - a.value), [rows]);
  const total = rows.reduce((a, r) => a + r.value, 0);
  const byMech = useMemo(() => {
    const m = new Map<string, number>();
    rows.forEach((r) => m.set(r.mechanism, (m.get(r.mechanism) || 0) + r.value));
    return [...m.entries()].sort((a, b) => b[1] - a[1]);
  }, [rows]);
  const recips = [...new Set(rows.map((r) => r.recipient))];
  const shown = all ? sorted : sorted.slice(0, 40);
  return (
    <div className="card" id="drill" aria-live="polite">
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '1rem', alignItems: 'start' }}>
        <h3 style={{ margin: 0 }}>
          {title}: {eurM(total)} <span className="muted small">({pct(total / gdp)} of GDP)</span>
        </h3>
        {onClose && (
          <button className="theme-btn" onClick={onClose}>
            Close
          </button>
        )}
      </div>
      {recips
        .filter((r) => SPECIAL_RECIPIENTS[r])
        .map((r) => (
          <p className="callout" key={r}>
            <strong>{r}</strong>: {SPECIAL_RECIPIENTS[r]}
          </p>
        ))}
      <p className="small muted">
        By mechanism:{' '}
        {byMech.map(([k, v], i) => (
          <span key={k}>
            {i > 0 && ' · '}
            {MECHANISMS[k]?.label || k} {eurM(v)}
          </span>
        ))}
        . {rows.length.toLocaleString('en-GB')} rows; each row is industry × recipient × mechanism.
      </p>
      <div className="table-scroll tall">
        <table className="data">
          <thead>
            <tr>
              <th>Industry</th>
              <th>Recipient</th>
              <th>Mechanism</th>
              <th className="r">EUR m</th>
              <th>Status</th>
              <th>Confidence</th>
              <th>Source</th>
              <th style={{ minWidth: '22rem' }}>Calculation</th>
            </tr>
          </thead>
          <tbody>
            {shown.map((r, i) => (
              <tr key={i}>
                <td>{r.industry_name}</td>
                <td>{r.recipient_name}</td>
                <td>{MECHANISMS[r.mechanism]?.label || r.mechanism}</td>
                <td className="r">{eurM(r.value)}</td>
                <td>
                  <span className={`badge st-${r.status}`}>{r.status}</span>
                </td>
                <td>{r.confidence_level}</td>
                <td>
                  {r.source}{' '}
                  {splitUrls(r.source_url).map((u, j) => (
                    <a key={u} href={u} target="_blank" rel="noopener noreferrer">
                      [{j + 1}]
                    </a>
                  ))}
                </td>
                <td className="small">{r.methodology}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {sorted.length > 40 && (
        <button className="theme-btn" style={{ marginTop: '0.5rem' }} onClick={() => setAll(!all)}>
          {all ? 'Show largest 40 rows' : `Show all ${sorted.length.toLocaleString('en-GB')} rows`}
        </button>
      )}
    </div>
  );
}
