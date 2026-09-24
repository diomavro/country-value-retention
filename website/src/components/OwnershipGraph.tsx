'use client';
import { useMemo } from 'react';
import type { Ownership } from '@/lib/types';
import { ancestors, edgeProv, layers, ownColor, OWN_COLORS } from '@/lib/ownership';
import { SPECIAL_RECIPIENTS } from '@/lib/concepts';
import { recipientName } from '@/lib/names';
import { eurM } from '@/lib/format';
import { usePop, ProvCard } from './Prov';
import { useWidth } from './useWidth';

export default function OwnershipGraph({ o, focus }: { o: Ownership; focus: string }) {
  const [ref, cw] = useWidth<HTMLDivElement>();
  const { show, hide } = usePop();
  const lay = useMemo(() => layers(o), [o]);
  const g = useMemo(() => {
    const keep = focus ? ancestors(o, focus) : new Set(o.nodes.map((n) => n.id));
    const nodes = o.nodes.filter((n) => keep.has(n.id));
    const maxL = Math.max(...nodes.map((n) => lay.get(n.id) || 0));
    const cols: (typeof nodes)[] = Array.from({ length: maxL + 1 }, () => []);
    nodes.forEach((n) => cols[lay.get(n.id) || 0].push(n));
    const y = new Map<string, number>();
    const rowH = 22;
    cols.forEach((col, li) => {
      if (li > 0) {
        const bary = (id: string) => {
          const ys = o.edges.filter((e) => e.from === id && y.has(e.to)).map((e) => y.get(e.to)!);
          return ys.length ? ys.reduce((a, b) => a + b, 0) / ys.length : 1e9;
        };
        col.sort((a, b) => bary(a.id) - bary(b.id));
      } else col.sort((a, b) => a.country.localeCompare(b.country) || a.name.localeCompare(b.name));
      col.forEach((n, i) => y.set(n.id, 16 + i * rowH));
    });
    const height = 16 + Math.max(...cols.map((c) => c.length)) * rowH + 10;
    return { nodes, cols, y, height, keep, maxL };
  }, [o, focus, lay]);

  const colW = 270;
  const width = Math.max(cw, (g.maxL + 1) * colW + 20);
  const step = Math.max(colW, (width - colW - 10) / Math.max(1, g.maxL));
  const x = (id: string) => 10 + (lay.get(id) || 0) * step;
  const byId = new Map(o.nodes.map((n) => [n.id, n]));
  const present = [...new Set(g.nodes.map((n) => n.country))];

  return (
    <div>
      <div className="legend">
        {Object.keys(OWN_COLORS).filter((c) => present.includes(c)).map((c) => (
          <span key={c}><span className="sw" style={{ background: OWN_COLORS[c] }} />{c === 'CY' ? 'Cyprus' : recipientName(c)}</span>
        ))}
        <span><span className="sw" style={{ background: 'var(--neutral)' }} />Other countries</span>
        <span><span className="sw" style={{ background: 'var(--surface)', border: '1.5px dashed var(--ink-2)' }} />UNRESOLVED</span>
        <span><span className="ln" style={{ background: 'var(--ink-2)' }} />documented share</span>
        <span>- - - share not disclosed</span>
      </div>
      <p className="small muted">Operating firms in Cyprus on the left; owners to the right, ending at ultimate owners.</p>
      <div ref={ref} className="chart-scroll" style={{ maxHeight: 900, overflowY: 'auto' }}>
        <svg className="chart" width={width} height={g.height} role="img" aria-label="Ownership network">
          <g fill="none">
            {o.edges.filter((e) => g.keep.has(e.from) && g.keep.has(e.to)).map((e, i) => {
              const x1 = x(e.to) + colW - 40, y1 = g.y.get(e.to)!, x2 = x(e.from), y2 = g.y.get(e.from)!;
              const tip = <ProvCard value={`${e.share_pct}%`} title={`${byId.get(e.from)?.name} → ${byId.get(e.to)?.name}`} prov={edgeProv(e)} />;
              return (
                <path key={i} className="mark" d={`M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}`} stroke="var(--ink-2)" strokeOpacity={0.35} strokeWidth={0.8 + (e.share_pct / 100) * 2.5}
                  onPointerMove={(ev) => show(ev, tip)} onPointerLeave={hide} onClick={(ev) => show(ev, tip, true)} />
              );
            })}
            {o.unpriced_edges.filter((e) => g.keep.has(e.parent_entity_id) && g.keep.has(e.child_entity_id)).map((e, i) => {
              const x1 = x(e.child_entity_id) + colW - 40, y1 = g.y.get(e.child_entity_id)!, x2 = x(e.parent_entity_id), y2 = g.y.get(e.parent_entity_id)!;
              const tip = (
                <ProvCard title={`${byId.get(e.parent_entity_id)?.name} → ${byId.get(e.child_entity_id)?.name}`} value="Share not disclosed"
                  prov={{ status: 'observed', confidence_level: 'low', source: 'See link', source_url: e.source_url, methodology: e.notes }} />
              );
              return <path key={`u${i}`} className="mark" d={`M${x1},${y1} C${(x1 + x2) / 2},${y1} ${(x1 + x2) / 2},${y2} ${x2},${y2}`} stroke="var(--ink-2)" strokeOpacity={0.5} strokeDasharray="4 3" onPointerMove={(ev) => show(ev, tip)} onPointerLeave={hide} onClick={(ev) => show(ev, tip, true)} />;
            })}
          </g>
          {g.nodes.map((n) => {
            const unres = n.country === 'UNRESOLVED';
            const fin = [n.revenue_eur_m != null && `Revenue ${eurM(n.revenue_eur_m)}`, n.operating_profit_eur_m != null && `Operating profit (as reported) ${eurM(n.operating_profit_eur_m)}`, n.employees != null && `Employees ${n.employees.toLocaleString('en-GB')}`].filter(Boolean).join(' · ');
            const tip = (
              <ProvCard
                title={`${n.name} (${unres ? 'UNRESOLVED' : recipientName(n.country)})`}
                prov={{ status: 'observed', confidence_level: 'see edges', source: 'Company ownership layer', source_url: n.source_url, methodology: n.notes || 'Entity record.' }}
                extra={<>{unres && <p className="small">{SPECIAL_RECIPIENTS.UNRESOLVED}</p>}{fin && <p className="small">{fin}{n.fiscal_year ? ` (FY${n.fiscal_year})` : ''}</p>}</>}
              />
            );
            const label = n.name.length > 22 ? `${n.name.slice(0, 21)}…` : n.name;
            return (
              <g key={n.id} className="mark" tabIndex={0} onPointerMove={(ev) => show(ev, tip)} onPointerLeave={hide} onClick={(ev) => show(ev, tip, true)}>
                <rect x={x(n.id)} y={g.y.get(n.id)! - 5} width={10} height={10} rx={2} fill={ownColor(n.country)} stroke={unres ? 'var(--ink-2)' : 'var(--surface)'} strokeDasharray={unres ? '2 2' : undefined} strokeWidth={1.5} />
                <text x={x(n.id) + 14} y={g.y.get(n.id)! + 4} className={n.id === focus ? 'lbl-strong' : 'lbl'}>
                  {label} · {unres ? 'UNRESOLVED' : n.country}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}
