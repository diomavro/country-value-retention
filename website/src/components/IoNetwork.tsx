'use client';
import { useMemo, useState } from 'react';
import type { IoNetwork as Net, Prov } from '@/lib/types';
import { eurM, pct } from '@/lib/format';
import { useJson } from '@/lib/useJson';
import { usePop, ProvCard } from './Prov';
import { useWidth } from './useWidth';
import YearSelect from './YearSelect';

const STEPS = ['var(--seq-2)', 'var(--seq-3)', 'var(--seq-4)', 'var(--seq-5)', 'var(--seq-6)'];

export default function IoNetwork({ years }: { years: number[] }) {
  const [year, setYear] = useState(years[years.length - 1]);
  const [focus, setFocus] = useState<string | null>(null);
  const { data } = useJson<Net>(`cy/io_network_${year}.json`);
  const [ref, cw] = useWidth<HTMLDivElement>();
  const size = Math.max(Math.min(cw, 760), 560);
  const { show, hide } = usePop();
  const prov: Prov = {
    status: 'observed',
    confidence_level: 'high',
    source: data?.source || 'CYSTAT SIOT',
    source_url: 'https://cystatdb.cystat.gov.cy/pxweb/en/8.CYSTAT-DB/',
    methodology: 'Domestic intermediate flows between products from the symmetric input-output table for domestic production (EUR m). The largest 120 flows are drawn. Node colour: imported inputs / output.',
  };
  const layout = useMemo(() => {
    if (!data) return null;
    const nodes = data.nodes.filter((n) => n.output > 0);
    const r = size / 2 - 140;
    const c = size / 2;
    const pos = new Map(nodes.map((n, i) => {
      const a = (i / nodes.length) * Math.PI * 2 - Math.PI / 2;
      return [n.id, { x: c + r * Math.cos(a), y: c + r * Math.sin(a), a, n }];
    }));
    const maxOut = Math.max(...nodes.map((n) => n.output));
    const maxE = Math.max(...data.edges.map((e) => e.value));
    const labelled = new Set([...nodes].sort((a, b) => b.output - a.output).slice(0, 12).map((n) => n.id));
    return { nodes, pos, maxOut, maxE, c, labelled };
  }, [data, size]);

  return (
    <section className="card">
      <h2>Who buys from whom inside Cyprus (input-output network)</h2>
      <p className="explain">
        The input-output table records, for each industry, how much it buys from every other industry, from abroad,
        and how much value it adds. A Cypriot restaurant imports olive oil directly (a direct foreign input) and buys
        bread from a Cypriot bakery that imports flour (an indirect one). Lines are the largest domestic supplier →
        buyer flows; circle size is output; darker blue means a higher share of imported inputs.
      </p>
      <div className="controls">
        <YearSelect years={years} value={year} onChange={setYear} />
        {focus && <button className="theme-btn" onClick={() => setFocus(null)}>Clear highlight</button>}
      </div>
      <div className="legend">
        <span>Imported inputs ÷ output:</span>
        {STEPS.map((s, i) => (
          <span key={s}><span className="sw" style={{ background: s }} />{i * 20}–{(i + 1) * 20}%</span>
        ))}
      </div>
      <div ref={ref} className="chart-scroll">
        {layout && data && (
          <svg className="chart" width={size} height={size} role="img" aria-label={`Input-output network of Cyprus, ${year}`}>
            <g fill="none">
              {data.edges.map((e, i) => {
                const a = layout.pos.get(e.from), b = layout.pos.get(e.to);
                if (!a || !b) return null;
                const on = !focus || e.from === focus || e.to === focus;
                const tip = <ProvCard value={eurM(e.value)} title={`${a.n.name} → ${b.n.name}`} prov={prov} />;
                return (
                  <path
                    key={i}
                    className="mark"
                    d={`M${a.x},${a.y} Q${layout.c},${layout.c} ${b.x},${b.y}`}
                    stroke={on && focus ? 'var(--s2)' : 'var(--ink-2)'}
                    strokeOpacity={on ? (focus ? 0.8 : 0.28) : 0.05}
                    strokeWidth={0.6 + (e.value / layout.maxE) * 7}
                    onPointerMove={(ev) => show(ev, tip)}
                    onPointerLeave={hide}
                    onClick={(ev) => show(ev, tip, true)}
                  />
                );
              })}
            </g>
            {layout.nodes.map((n) => {
              const p = layout.pos.get(n.id)!;
              const share = n.imported_inputs / n.output;
              const rr = 3 + Math.sqrt(n.output / layout.maxOut) * 12;
              const deg = (p.a * 180) / Math.PI;
              const flip = deg > 90 && deg < 270;
              const tip = (
                <ProvCard
                  value={`Output ${eurM(n.output)}`}
                  title={n.name}
                  prov={prov}
                  extra={<p className="small">Imported inputs {eurM(n.imported_inputs)} ({pct(share)} of output). Click to highlight its flows.</p>}
                />
              );
              const show_label = layout.labelled.has(n.id) || focus === n.id;
              return (
                <g key={n.id}>
                  <circle
                    className="mark"
                    tabIndex={0}
                    cx={p.x}
                    cy={p.y}
                    r={rr}
                    fill={STEPS[Math.min(4, Math.floor(share * 5))]}
                    stroke={focus === n.id ? 'var(--ink)' : 'var(--surface)'}
                    strokeWidth={focus === n.id ? 2 : 1.5}
                    onPointerMove={(ev) => show(ev, tip)}
                    onPointerLeave={hide}
                    onClick={(ev) => {
                      setFocus(focus === n.id ? null : n.id);
                      show(ev, tip, true);
                    }}
                  />
                  {show_label && (
                    <text
                      className="lbl"
                      transform={`translate(${layout.c + (Math.hypot(p.x - layout.c, p.y - layout.c) + rr + 4) * Math.cos(p.a)},${layout.c + (Math.hypot(p.x - layout.c, p.y - layout.c) + rr + 4) * Math.sin(p.a)}) rotate(${flip ? deg + 180 : deg})`}
                      textAnchor={flip ? 'end' : 'start'}
                      dy="0.35em"
                      pointerEvents="none"
                    >
                      {n.name.length > 20 ? `${n.name.slice(0, 19)}…` : n.name}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        )}
      </div>
    </section>
  );
}
