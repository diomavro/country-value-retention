'use client';
import type { Prov } from '@/lib/types';
import { usePopHandlers, ProvCard } from './Prov';

export interface Seg { key: string; label: string; value: number; display: string; color: string; prov: Prov; note?: string }

function Part({ s, total }: { s: Seg; total: number }) {
  const h = usePopHandlers(() => <ProvCard value={s.display} title={s.label} prov={s.prov} extra={s.note ? <p className="small">{s.note}</p> : undefined} />);
  return <div className="mark" tabIndex={0} role="img" aria-label={`${s.label}: ${s.display}`} style={{ width: `${(s.value / total) * 100}%`, background: s.color }} {...h} />;
}

/** One 100% stacked bar with a legend that doubles as direct labels (value + label). */
export default function StackBar({ segs, height = 26 }: { segs: Seg[]; height?: number }) {
  const total = segs.reduce((a, s) => a + Math.max(0, s.value), 0) || 1;
  return (
    <div>
      <div className="stackbar" style={{ height }}>
        {segs.filter((s) => s.value > 0).map((s) => (
          <Part key={s.key} s={s} total={total} />
        ))}
      </div>
      <div className="legend">
        {segs.map((s) => (
          <span key={s.key}>
            <span className="sw" style={{ background: s.color }} />
            {s.label}: <strong>{s.display}</strong>
          </span>
        ))}
      </div>
    </div>
  );
}
