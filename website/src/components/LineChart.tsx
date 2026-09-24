'use client';
import React from 'react';
import type { Prov } from '@/lib/types';
import { usePop, ProvCard } from './Prov';
import { linear, niceTicks, useWidth } from './useWidth';

export interface Series {
  key: string;
  label: string;
  short?: string;
  color: string;
  dashed?: boolean;
  points: { x: number; y: number | null }[];
  prov: Prov;
}

export default function LineChart({
  series,
  fmt,
  height = 260,
  xLabel,
  yMax,
  yMin = 0,
  directLabels = true,
  highlightX,
  ariaLabel,
  xFmt = (x: number) => String(x),
}: {
  series: Series[];
  fmt: (v: number) => string;
  height?: number;
  xLabel?: string;
  yMax?: number;
  yMin?: number;
  directLabels?: boolean;
  highlightX?: number;
  ariaLabel: string;
  xFmt?: (x: number) => string;
}) {
  const [ref, width] = useWidth<HTMLDivElement>();
  const { show, hide } = usePop();
  const [hx, setHx] = React.useState<number | null>(null);
  const xs = [...new Set(series.flatMap((s) => s.points.map((p) => p.x)))].sort((a, b) => a - b);
  const allY = series.flatMap((s) => s.points.map((p) => p.y).filter((v): v is number => v != null));
  const ticks = niceTicks((yMax ?? Math.max(...allY, 0)) - yMin, width < 480 ? 4 : 5).map((t) => +(t + yMin).toFixed(10));
  const top = ticks[ticks.length - 1];
  const labelW = directLabels && width >= 560 ? 150 : 0;
  const m = { l: 48, r: 12 + labelW, t: 12, b: 28 };
  const x = linear(xs[0], xs[xs.length - 1], m.l, width - m.r);
  const y = linear(yMin, top, height - m.b, m.t);

  const tooltip = (xv: number) => (
    <div>
      <div className="prov-title">
        <strong>{xFmt(xv)}</strong>
      </div>
      <div className="tt-rows">
        {series.map((s) => {
          const p = s.points.find((q) => q.x === xv);
          return (
            <React.Fragment key={s.key}>
              <span className="tt-key" style={{ background: s.color }} />
              <span>{s.label}</span>
              <strong>{p?.y != null ? fmt(p.y) : 'n/a'}</strong>
            </React.Fragment>
          );
        })}
      </div>
      {series.map((s) => (
        <details key={s.key} open={series.length === 1}>
          <summary className="small">Provenance: {s.label}</summary>
          <ProvCard prov={s.prov} />
        </details>
      ))}
    </div>
  );

  const onMove = (e: React.PointerEvent<SVGRectElement>, pin = false) => {
    const r = (e.currentTarget.ownerSVGElement as SVGSVGElement).getBoundingClientRect();
    const px = e.clientX - r.left;
    let best = xs[0];
    xs.forEach((v) => {
      if (Math.abs(x(v) - px) < Math.abs(x(best) - px)) best = v;
    });
    setHx(best);
    show(e, tooltip(best), pin);
  };

  const ends = series
    .map((s) => {
      const last = [...s.points].reverse().find((p) => p.y != null);
      return last ? { s, y: y(last.y as number), x: x(last.x) } : null;
    })
    .filter((v): v is { s: Series; y: number; x: number } => !!v)
    .sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) if (ends[i].y - ends[i - 1].y < 14) ends[i].y = ends[i - 1].y + 14;

  return (
    <div ref={ref}>
      {series.length > 1 && (
        <div className="legend">
          {series.map((s) => (
            <span key={s.key}>
              <span className="ln" style={{ background: s.color }} />
              {s.label}
            </span>
          ))}
        </div>
      )}
      <svg className="chart" width={width} height={height} role="img" aria-label={ariaLabel}>
        <g className="grid">
          {ticks.map((t) => (
            <g key={t}>
              <line x1={m.l} x2={width - m.r} y1={y(t)} y2={y(t)} />
              <text x={m.l - 6} y={y(t) + 4} textAnchor="end">
                {fmt(t)}
              </text>
            </g>
          ))}
        </g>
        <g className="axis">
          <line x1={m.l} x2={width - m.r} y1={y(yMin)} y2={y(yMin)} />
          {(() => {
            const keep: number[] = [];
            xs.forEach((v, i) => {
              const px = x(v);
              if (i === xs.length - 1) {
                while (keep.length && px - x(keep[keep.length - 1]) < 38) keep.pop();
                keep.push(v);
              } else if (!keep.length || px - x(keep[keep.length - 1]) >= 38) keep.push(v);
            });
            return keep.map((v) => (
              <text key={v} x={x(v)} y={height - m.b + 16} textAnchor="middle">
                {xFmt(v)}
              </text>
            ));
          })()}
          {xLabel && (
            <text x={width - m.r} y={height - 2} textAnchor="end">
              {xLabel}
            </text>
          )}
        </g>
        {highlightX != null && xs.includes(highlightX) && (
          <line x1={x(highlightX)} x2={x(highlightX)} y1={m.t} y2={height - m.b} stroke="var(--axis)" strokeDasharray="3 3" />
        )}
        {series.map((s) => {
          let d = '';
          let pen = false;
          s.points.forEach((p) => {
            if (p.y == null) {
              pen = false;
              return;
            }
            d += `${pen ? 'L' : 'M'}${x(p.x).toFixed(1)},${y(p.y).toFixed(1)}`;
            pen = true;
          });
          return (
            <g key={s.key}>
              <path d={d} fill="none" stroke={s.color} strokeWidth={2} strokeDasharray={s.dashed ? '5 4' : undefined} strokeLinejoin="round" strokeLinecap="round" />
              {s.points.length < 20 &&
                s.points.map((p) =>
                  p.y != null ? <circle key={p.x} cx={x(p.x)} cy={y(p.y)} r={hx === p.x ? 4.5 : 2.5} fill={s.color} stroke="var(--surface)" strokeWidth={1.5} /> : null,
                )}
            </g>
          );
        })}
        {hx != null && <line x1={x(hx)} x2={x(hx)} y1={m.t} y2={height - m.b} stroke="var(--ink-2)" strokeWidth={1} pointerEvents="none" />}
        {labelW > 0 &&
          ends.map((e) => (
            <text key={e.s.key} x={e.x + 8} y={e.y + 4} className="lbl">
              {(e.s.short || e.s.label).length > 24 ? `${(e.s.short || e.s.label).slice(0, 23)}…` : e.s.short || e.s.label}
            </text>
          ))}
        <rect
          x={m.l}
          y={m.t}
          width={Math.max(0, width - m.l - m.r)}
          height={height - m.t - m.b}
          fill="transparent"
          style={{ cursor: 'crosshair' }}
          onPointerMove={(e) => onMove(e)}
          onPointerLeave={() => {
            setHx(null);
            hide();
          }}
          onClick={(e) => onMove(e as unknown as React.PointerEvent<SVGRectElement>, true)}
        />
      </svg>
    </div>
  );
}
