'use client';
import React, { useMemo, useState } from 'react';
import type { FlowRow } from '@/lib/types';
import { aggregateProv, isSpecial } from '@/lib/concepts';
import { foreignRows, recipientGroups, sumBy } from '@/lib/useFlows';
import { recipientName } from '@/lib/names';
import { eurM } from '@/lib/format';
import { usePop, ProvCard } from './Prov';

const STEPS = ['var(--seq-1)', 'var(--seq-2)', 'var(--seq-3)', 'var(--seq-4)', 'var(--seq-5)', 'var(--seq-6)', 'var(--seq-7)'];

/** Industry x recipient, foreign income only. Sequential one-hue ramp on a square-root scale. */
export default function Heatmap({ rows, onCell }: { rows: FlowRow[]; onCell: (industry: string, recipient: string) => void }) {
  const [all, setAll] = useState(false);
  const { show, hide } = usePop();
  const { cols, inds, cell, max } = useMemo(() => {
    const fr = foreignRows(rows);
    const { top, special, group } = recipientGroups(rows);
    const cols = [...top, ...special, 'OTHER'];
    const byInd = [...sumBy(fr, (r) => r.industry).entries()].sort((a, b) => b[1].value - a[1].value);
    const cell = sumBy(fr, (r) => `${r.industry}|${group(r.recipient)}`);
    const max = Math.max(...[...cell.values()].map((c) => c.value), 1e-9);
    return { cols, inds: byInd.map(([k, v]) => ({ k, name: v.rows[0].industry_name, total: v.value })), cell, max };
  }, [rows]);
  const shown = all ? inds : inds.slice(0, 20);
  const color = (v: number) => STEPS[Math.min(STEPS.length - 1, Math.floor(Math.sqrt(v / max) * STEPS.length))];
  const colName = (c: string) => (c === 'OTHER' ? 'Other countries' : recipientName(c));
  return (
    <div>
      <div className="legend" aria-hidden>
        <span>Smaller</span>
        {STEPS.map((s) => (
          <span key={s} className="sw" style={{ background: s, margin: 0 }} />
        ))}
        <span>Larger (EUR m, square-root scale)</span>
        <span>· empty cell = no recorded flow</span>
      </div>
      <div className="table-scroll">
        <table className="data" style={{ width: 'auto', borderCollapse: 'separate', borderSpacing: 2 }}>
          <thead>
            <tr>
              <th className="hm-name">Industry</th>
              {cols.map((c) => (
                <th key={c} className="small" style={{ writingMode: 'vertical-rl', transform: 'rotate(180deg)', height: '9.5rem', whiteSpace: 'nowrap', verticalAlign: 'bottom', fontWeight: isSpecial(c) ? 400 : 600 }} title={colName(c)}>
                  {colName(c).length > 24 ? `${colName(c).slice(0, 23)}…` : colName(c)}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {shown.map((i) => (
              <tr key={i.k}>
                <td className="small hm-name" style={{ border: 'none' }}>{i.name}</td>
                {cols.map((c) => {
                  const e = cell.get(`${i.k}|${c}`);
                  if (!e) return <td key={c} style={{ border: 'none', background: 'var(--surface-2)', minWidth: 30 }} />;
                  const tip = <ProvCard value={eurM(e.value)} title={`${i.name} → ${colName(c)}`} prov={aggregateProv(e.rows, 'Cell')} />;
                  return (
                    <td
                      key={c}
                      className="mark"
                      tabIndex={0}
                      aria-label={`${i.name} to ${colName(c)}: ${eurM(e.value)}`}
                      style={{ background: color(e.value), border: 'none', minWidth: 30, height: 22, borderRadius: 3, padding: 0 }}
                      onPointerMove={(ev) => ev.pointerType === 'mouse' && show(ev, tip)}
                      onPointerLeave={hide}
                      onClick={(ev) => {
                        show(ev, tip, true);
                        onCell(i.k, c);
                      }}
                      onKeyDown={(ev) => ev.key === 'Enter' && onCell(i.k, c)}
                    />
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {inds.length > 20 && (
        <button className="theme-btn" style={{ marginTop: '0.5rem' }} onClick={() => setAll(!all)}>
          {all ? 'Show top 20 industries' : `Show all ${inds.length} industries`}
        </button>
      )}
    </div>
  );
}
