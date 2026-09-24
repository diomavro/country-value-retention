'use client';
import type { HeadlineYear } from '@/lib/types';
import { METRICS } from '@/lib/concepts';
import { eurM, pct } from '@/lib/format';
import { Num } from './Prov';

export default function Kpis({ h }: { h: HeadlineYear }) {
  const tiles: { key: keyof typeof METRICS; value: string; sub: string }[] = [
    { key: 'gdp', value: eurM(h.gdp), sub: `Value created in Cyprus, ${h.year}` },
    { key: 'domestic_value_retention', value: pct(h.domestic_value_retention), sub: 'of GDP stays with residents' },
    {
      key: 'foreign_value_leakage',
      value: pct(h.foreign_value_leakage),
      sub: `of GDP accrues abroad (${eurM(h.foreign_value_leakage_eur_m)})`,
    },
    {
      key: 'foreign_input_exposure',
      value: pct(h.foreign_input_exposure),
      sub: h.foreign_input_exposure == null ? 'No input-output table published for this year' : 'of intermediate inputs are imported',
    },
    { key: 'foreign_ownership_capture', value: pct(h.foreign_ownership_capture), sub: 'of operating surplus accrues to foreign owners' },
  ];
  return (
    <div className="kpis" role="list">
      {tiles.map((t) => {
        const m = METRICS[t.key];
        return (
          <div className="kpi" role="listitem" key={t.key}>
            <div className="k-label">{m.label}</div>
            <div className="k-value">
              <Num prov={m.prov} title={`${m.label}, ${h.year}. ${m.question}`}>
                {t.value}
              </Num>
            </div>
            <div className="k-sub">{t.sub}</div>
          </div>
        );
      })}
    </div>
  );
}
