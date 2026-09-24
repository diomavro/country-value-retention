'use client';
import React, { useMemo } from 'react';
import { sankey, sankeyLinkHorizontal, type SankeyGraph } from 'd3-sankey';
import type { FlowRow } from '@/lib/types';
import { MECHANISMS, MECH_ORDER, aggregateProv, SPECIAL_RECIPIENTS } from '@/lib/concepts';
import { recipientGroups } from '@/lib/useFlows';
import { eurM, pct } from '@/lib/format';
import { usePop, ProvCard } from './Prov';
import { useWidth } from './useWidth';

export const MECH_COLOR: Record<string, string> = {
  retained_domestic: 'var(--retained)',
  compensation_nonresident: 'var(--s1)',
  fdi_income: 'var(--s2)',
  fdi_debt_interest: 'var(--s7)',
  portfolio_income: 'var(--s3)',
  other_investment_income: 'var(--s4)',
  public_debt_interest: 'var(--s5)',
  taxes_to_eu_institutions: 'var(--s6)',
};

interface N { id: string; label: string; kind: 'src' | 'mech' | 'rec' }
interface L { source: string; target: string; value: number; mech: string; rows: FlowRow[] }

export default function Sankey({ rows, gdp, includeRetained, onRecipient }: { rows: FlowRow[]; gdp: number; includeRetained: boolean; onRecipient: (r: string) => void }) {
  const [ref, cw] = useWidth<HTMLDivElement>();
  const width = Math.max(cw, 620);
  const height = includeRetained ? 520 : 480;
  const { show, hide } = usePop();

  const graph = useMemo(() => {
    const use = includeRetained ? rows : rows.filter((r) => r.mechanism !== 'retained_domestic');
    const { group, other } = recipientGroups(rows);
    const nodes = new Map<string, N>();
    const links = new Map<string, L>();
    const src = 'SRC';
    nodes.set(src, { id: src, label: includeRetained ? 'Value added in Cyprus (GDP)' : 'Income paid to non-residents', kind: 'src' });
    use.forEach((r) => {
      const mid = `M:${r.mechanism}`;
      const g = group(r.recipient);
      const rid = `R:${g}`;
      if (!nodes.has(mid)) nodes.set(mid, { id: mid, label: MECHANISMS[r.mechanism]?.label || r.mechanism, kind: 'mech' });
      if (!nodes.has(rid))
        nodes.set(rid, {
          id: rid,
          label: g === 'OTHER' ? `Other countries (${other.length})` : g === 'CY' ? 'Cyprus residents' : r.recipient_name,
          kind: 'rec',
        });
      for (const [a, b] of [
        [src, mid],
        [mid, rid],
      ]) {
        const k = `${a}|${b}`;
        const l = links.get(k) || { source: a, target: b, value: 0, mech: r.mechanism, rows: [] };
        l.value += r.value;
        l.rows.push(r);
        links.set(k, l);
      }
    });
    const order = ['retained_domestic', ...MECH_ORDER];
    const nodeArr = [...nodes.values()];
    const gen = sankey<N, L>()
      .nodeId((d) => d.id)
      .nodeWidth(12)
      .nodePadding(includeRetained ? 10 : 12)
      .nodeSort((a, b) => {
        if (a.kind === 'mech' && b.kind === 'mech') return order.indexOf(a.id.slice(2)) - order.indexOf(b.id.slice(2));
        return (b.value || 0) - (a.value || 0);
      })
      .extent([
        [4, 8],
        [width - 4, height - 8],
      ]);
    return gen({ nodes: nodeArr.map((d) => ({ ...d })), links: [...links.values()].map((d) => ({ ...d })) } as SankeyGraph<N, L>);
  }, [rows, includeRetained, width, height]);

  const nodeRows = (id: string) => graph.links.filter((l) => (l.target as N).id === id || ((l.source as N).id === id && id === 'SRC')).flatMap((l) => l.rows);
  const nodeTip = (n: N & { value?: number }) => {
    const rs = n.kind === 'mech' ? graph.links.filter((l) => (l.target as N).id === n.id).flatMap((l) => l.rows) : n.kind === 'rec' ? graph.links.filter((l) => (l.target as N).id === n.id).flatMap((l) => l.rows) : nodeRows('SRC');
    const code = n.id.slice(2);
    const note = n.kind === 'mech' ? MECHANISMS[code]?.explain : SPECIAL_RECIPIENTS[code];
    return <ProvCard value={`${eurM(n.value)} · ${pct((n.value || 0) / gdp)} of GDP`} title={n.label} prov={aggregateProv(rs, n.label)} extra={note ? <p className="small">{note}</p> : undefined} />;
  };

  const lw = width < 700 ? 150 : 210;
  return (
    <div ref={ref} className="chart-scroll">
      <svg className="chart" width={width} height={height} role="img" aria-label="Sankey diagram: value added in Cyprus by mechanism and recipient">
        <g fill="none">
          {graph.links.map((l, i) => (
            <path
              key={i}
              className="mark"
              d={sankeyLinkHorizontal()(l) || ''}
              stroke={MECH_COLOR[l.mech]}
              strokeOpacity={0.45}
              strokeWidth={Math.max(1, l.width || 0)}
              tabIndex={0}
              onPointerMove={(e) =>
                show(e, <ProvCard value={`${eurM(l.value)} · ${pct(l.value / gdp)} of GDP`} title={`${(l.source as N).label} → ${(l.target as N).label}`} prov={aggregateProv(l.rows, 'Flow')} />)
              }
              onPointerLeave={hide}
              onClick={(e) => {
                const t = l.target as N;
                if (t.kind === 'rec') onRecipient(t.id.slice(2));
                show(e, <ProvCard value={eurM(l.value)} title={`${(l.source as N).label} → ${t.label}`} prov={aggregateProv(l.rows, 'Flow')} />, true);
              }}
            />
          ))}
        </g>
        {graph.nodes.map((n) => {
          const x0 = n.x0 || 0, x1 = n.x1 || 0, y0 = n.y0 || 0, y1 = n.y1 || 0;
          const right = n.kind === 'rec';
          const code = n.id.slice(2);
          const fill = n.kind === 'mech' ? MECH_COLOR[code] : n.kind === 'rec' && (SPECIAL_RECIPIENTS[code] || code === 'OTHER') ? 'var(--neutral)' : 'var(--ink-2)';
          return (
            <g key={n.id}>
              <rect
                className="mark"
                tabIndex={0}
                x={x0}
                y={y0}
                width={x1 - x0}
                height={Math.max(1, y1 - y0)}
                fill={fill}
                rx={2}
                onPointerMove={(e) => show(e, nodeTip(n))}
                onPointerLeave={hide}
                onClick={(e) => {
                  if (n.kind === 'rec' && code !== 'OTHER' && code !== 'CY') onRecipient(code);
                  show(e, nodeTip(n), true);
                }}
              />
              {(y1 - y0 > 7 || n.kind === 'src') && (
                <text
                  x={right ? x0 - 6 : x1 + 6}
                  y={(y0 + y1) / 2 + 4}
                  textAnchor={right ? 'end' : 'start'}
                  className={n.kind === 'src' ? 'lbl-strong' : 'lbl'}
                  pointerEvents="none"
                >
                  {(n.label.length > lw / 6.5 ? `${n.label.slice(0, Math.floor(lw / 6.5) - 1)}…` : n.label) + ` ${eurM(n.value)}`}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
