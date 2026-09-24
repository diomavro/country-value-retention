'use client';
import type { Headline } from '@/lib/types';
import { METRICS } from '@/lib/concepts';
import { pct } from '@/lib/format';
import LineChart from './LineChart';

/** Small multiples: each measure on its own base, never on a shared axis or summed. */
export default function TimeSeries({ headline, year }: { headline: Headline; year: number }) {
  const s = headline.series;
  const panels: { key: keyof typeof METRICS; get: (r: (typeof s)[number]) => number | null }[] = [
    { key: 'domestic_value_retention', get: (r) => r.domestic_value_retention },
    { key: 'foreign_ownership_capture', get: (r) => r.foreign_ownership_capture },
    { key: 'foreign_input_exposure', get: (r) => r.foreign_input_exposure },
    { key: 'foreign_labour_income_share', get: (r) => r.foreign_labour_income_share },
    ...(s.some((r) => r.foreign_creditor_income_share_of_nos != null)
      ? [{ key: 'foreign_creditor_income_share_of_nos' as const, get: (r: (typeof s)[number]) => r.foreign_creditor_income_share_of_nos ?? null }]
      : []),
  ];
  return (
    <section>
      <h2>The measures over time</h2>
      <p className="explain">
        These describe different mechanisms measured on different bases (GDP, operating surplus, intermediate inputs,
        wages). Each has its own chart; adding them would mix denominators and double-count.
      </p>
      <div className="grid2">
        {panels.map((p) => {
          const m = METRICS[p.key];
          return (
            <div className="card" key={p.key}>
              <h3>{m.label}</h3>
              <p className="explain">{m.question}</p>
              <LineChart
                ariaLabel={`${m.label} by year`}
                height={200}
                fmt={(v) => pct(v, Math.max(...s.map((r) => p.get(r) ?? 0)) < 0.05 ? 1 : 0)}
                highlightX={year}
                yMax={p.key === 'domestic_value_retention' ? 1 : undefined}
                directLabels={false}
                series={[{ key: p.key, label: m.label, color: 'var(--s1)', prov: m.prov, points: s.map((r) => ({ x: r.year, y: p.get(r) })) }]}
              />
            </div>
          );
        })}
      </div>
    </section>
  );
}
