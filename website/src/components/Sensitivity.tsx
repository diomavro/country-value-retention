'use client';
import { useMemo, useState } from 'react';
import type { SensRow, Prov } from '@/lib/types';
import { pct } from '@/lib/format';
import LineChart from './LineChart';
import YearSelect from './YearSelect';
import { Num } from './Prov';

export default function Sensitivity({ rows, headlineTheta }: { rows: SensRow[]; headlineTheta: number }) {
  const years = [...new Set(rows.map((r) => r.year))].sort();
  const [year, setYear] = useState(years.includes(2022) ? 2022 : years[years.length - 1]);
  const [ofc, setOfc] = useState(false);
  const [scope, setScope] = useState(false);
  const sel = useMemo(() => rows.filter(
        (r) =>
          r.year === year &&
          r.include_ofc === ofc &&
          r.consistent_scope === scope &&
          // theta x tax grid only: one-at-a-time variants share its theta values
          !r.banks_gross &&
          !r.bop_upper &&
          r.rho_basis === 'd41_gross' &&
          r.tax !== 'eatr' &&
          r.fats_na_level !== false,
      ), [rows, year, ofc, scope]);
  const thetas = [...new Set(sel.map((r) => r.theta))].sort();
  const prov = (r?: SensRow): Prov => ({
    status: r?.status || 'estimated',
    confidence_level: r?.confidence_level || 'medium',
    source: r?.source || 'model output',
    source_url: null,
    methodology: `${r?.methodology || 'Frame A re-run over parameter grid'}. theta = share of foreign-controlled firms' equity held by non-residents; tax = corporate income tax deducted (statutory) or not (none); OFC investment income ${ofc ? 'included' : 'excluded'}; ${scope ? 'consistent FATS scope across years' : 'FATS scope as published each year'}.`,
  });
  const pt = (tax: string) => thetas.map((t) => ({ x: t, y: sel.find((r) => r.theta === t && r.tax === tax)?.domestic_value_retention ?? null }));
  return (
    <section className="card">
      <h2>How sure are we? Domestic Value Retention across assumptions</h2>
      <p className="explain">
        Where an assumption drives a result (what share of a sector&apos;s profits goes abroad), the result is shown
        across a range of values rather than as a single falsely precise number. Note the vertical axis starts above zero to show the spread. The headline uses theta = {headlineTheta}.
      </p>
      <div className="controls">
        <YearSelect years={years} value={year} onChange={setYear} />
        <label className="check"><input type="checkbox" checked={ofc} onChange={(e) => setOfc(e.target.checked)} /> Include offshore-centre (OFC) investment income</label>
        <label className="check"><input type="checkbox" checked={scope} onChange={(e) => setScope(e.target.checked)} /> Consistent FATS scope</label>
      </div>
      <LineChart
        ariaLabel="Domestic value retention by theta, with and without corporate tax"
        fmt={(v) => pct(v, 0)}
        xFmt={(x) => x.toFixed(2)}
        xLabel="theta"
        yMin={Math.floor(Math.min(...sel.map((r) => r.domestic_value_retention), 0.9) * 20) / 20}
        yMax={1}
        series={[
          { key: 'stat', label: 'Tax on (statutory rate)', color: 'var(--s1)', prov: prov(sel.find((r) => r.tax === 'statutory')), points: pt('statutory') },
          { key: 'none', label: 'Tax off', color: 'var(--s2)', dashed: true, prov: prov(sel.find((r) => r.tax === 'none')), points: pt('none') },
        ]}
      />
      <div className="table-scroll">
        <table className="data">
          <thead>
            <tr><th>theta</th>{thetas.map((t) => <th key={t} className="r">{t}</th>)}</tr>
          </thead>
          <tbody>
            {['statutory', 'none'].map((tax) => (
              <tr key={tax}>
                <td>Tax {tax === 'statutory' ? 'on' : 'off'}</td>
                {thetas.map((t) => {
                  const r = sel.find((x) => x.theta === t && x.tax === tax);
                  return <td key={t} className="r">{r ? <Num prov={prov(r)} title={`DVR ${year}, theta ${t}, tax ${tax}`}>{pct(r.domestic_value_retention)}</Num> : 'n/a'}</td>;
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
