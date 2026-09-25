'use client';
import React from 'react';
import type { Prov } from '@/lib/types';
import { pct } from '@/lib/format';
import LineChart from './LineChart';
import { Num } from './Prov';

export interface CompareRow {
  year: number;
  dvr: number;
  dvr_theta_1: number;
  official_outflow: number;
  theta: number;
  theta_status: string;
  tau: number;
  missing_lines: string;
  incomplete: string[];
  collapsed_sections: string;
  shares: Record<string, number>;
}
export interface CompareData {
  countries: { geo: string; rows: CompareRow[] }[];
  skipped: { geo: string; year: number; reason: string }[];
  gaps: { geo: string; line: string; years: number[] }[];
  prov: Prov;
}

// fixed order = fixed colour: a country keeps its colour whatever else is shown
const COUNTRIES: [string, string, string][] = [
  ['CY', 'Cyprus', 'var(--s1)'],
  ['IE', 'Ireland', 'var(--s2)'],
  ['LU', 'Luxembourg', 'var(--s3)'],
  ['NL', 'Netherlands', 'var(--s4)'],
  ['EL', 'Greece', 'var(--s5)'],
  ['PT', 'Portugal', 'var(--s6)'],
];
const MECHS: [string, string][] = [
  ['fdi_income', 'Foreign-owned profit'],
  ['compensation_nonresident', 'Pay to non-resident employees'],
  ['public_debt_interest', 'Public debt interest'],
  ['other_investment_income', 'Loans, deposits and other investment income'],
  ['portfolio_income', 'Portfolio income'],
  ['fdi_debt_interest', 'Intra-group interest'],
  ['taxes_to_eu_institutions', 'Taxes to EU institutions'],
];

/** [2010, 2011, 2012, 2015] -> "2010–2012, 2015" */
function ranges(ys: number[]): string {
  const out: string[] = [];
  let start = ys[0];
  ys.forEach((y, i) => {
    if (ys[i + 1] !== y + 1) {
      out.push(start === y ? String(y) : `${start}–${y}`);
      start = ys[i + 1];
    }
  });
  return out.join(', ');
}

export default function CompareView({ data }: { data: CompareData }) {
  const byGeo = new Map(data.countries.map((c) => [c.geo, c.rows]));
  const shown = COUNTRIES.filter(([g]) => byGeo.has(g));
  const years = [...new Set(data.countries.flatMap((c) => c.rows.map((r) => r.year)))].sort((a, b) => a - b);
  const [year, setYear] = React.useState(years[years.length - 1]);
  const at = (g: string) => byGeo.get(g)?.find((r) => r.year === year);
  const rowProv = (g: string, r: CompareRow, what: string): Prov => ({
    ...data.prov,
    methodology: `${what}. theta = ${r.theta.toFixed(3)} (${r.theta_status}); tax rate ${pct(r.tau)}.` +
      (r.collapsed_sections ? ` Sections shown as one row (industries suppressed): ${r.collapsed_sections}.` : '') +
      (r.missing_lines ? ` Suppressed, so omitted: ${r.missing_lines}.` : ''),
  });
  const skippedOther = data.skipped.filter((s) => s.geo !== 'MT');
  const malta = data.skipped.filter((s) => s.geo === 'MT');
  return (
    <>
      <h1>Cyprus among other economies</h1>
      <p className="explain">
        The same method, run on five other euro-area economies from Eurostat data. Three host many foreign firms
        (Ireland, Luxembourg, the Netherlands); two do not (Greece, Portugal). Run on Cyprus with the Eurostat
        sources, the method reproduces the Cyprus result to within rounding, so differences come from the
        economies or from suppressed data (listed at the bottom of the page), not from the change of source.
      </p>
      <p className="explain">
        One thing is assumed rather than measured: θ, the share of foreign-controlled firms&apos; equity held by
        non-residents, is calibrated from Cypriot company filings only. Other countries use the Cyprus value; the table
        also shows θ = 1, the lowest possible retention.
      </p>

      <section className="card">
        <h2>Domestic value retention, % of GDP</h2>
        <p className="explain">
          Share of the value added produced in the country that stays with residents. Gaps are years whose inputs the
          statistical office suppresses; nothing is filled in.
        </p>
        <LineChart
          ariaLabel="Domestic value retention by country and year"
          fmt={(v) => pct(v, 0)}
          yMin={0.6}
          yMax={1}
          highlightX={year}
          directLabels={false}
          series={shown.map(([g, name, color]) => ({
            key: g,
            label: name,
            color,
            prov: { ...data.prov, methodology: `${data.prov.methodology}. ${name}.` },
            points: years.map((y) => ({ x: y, y: byGeo.get(g)?.find((r) => r.year === y)?.dvr ?? null })),
          }))}
        />
      </section>

      <section className="card">
        <h2>Where the leakage goes, {year}</h2>
        <p className="explain">
          Each line as % of GDP. Leakage in a hub is not one thing: in Luxembourg most is the pay of cross-border
          commuters, who live in France, Belgium and Germany and are therefore non-residents; in Ireland it is the
          profit of foreign-controlled firms. The official outflow includes income that only passes through
          (special purpose entities) and is shown for contrast, not as part of the estimate.
        </p>
        <label>
          Year{' '}
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
            {years.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </label>
        <div className="table-scroll">
          <table className="data">
            <thead>
              <tr>
                <th>Line</th>
                {shown.map(([g, name]) => (
                  <th key={g} className="r">
                    {name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MECHS.map(([k, label]) => (
                <tr key={k}>
                  <td>{label}</td>
                  {shown.map(([g]) => {
                    const r = at(g);
                    return (
                      <td key={g} className="r">
                        {r ? <Num prov={rowProv(g, r, label)}>{pct(r.shares[k] ?? 0)}</Num> : '–'}
                        {r?.incomplete.includes(k) && <span title="incomplete: a suppressed input is omitted"> †</span>}
                      </td>
                    );
                  })}
                </tr>
              ))}
              <tr>
                <td>
                  <strong>Retention</strong>
                </td>
                {shown.map(([g]) => {
                  const r = at(g);
                  return (
                    <td key={g} className="r">
                      {r ? <Num prov={rowProv(g, r, 'Domestic value retention')}><strong>{pct(r.dvr)}</strong></Num> : '–'}
                    </td>
                  );
                })}
              </tr>
              <tr>
                <td>Retention if θ = 1</td>
                {shown.map(([g]) => {
                  const r = at(g);
                  return (
                    <td key={g} className="r">
                      {r ? pct(r.dvr_theta_1) : '–'}
                    </td>
                  );
                })}
              </tr>
              <tr>
                <td>Official primary income paid abroad</td>
                {shown.map(([g]) => {
                  const r = at(g);
                  return (
                    <td key={g} className="r">
                      {r ? pct(r.official_outflow, 0) : '–'}
                    </td>
                  );
                })}
              </tr>
            </tbody>
          </table>
        </div>
        <p className="explain">† Incomplete: an input to this line is suppressed and omitted (see below).</p>
      </section>

      <section className="card">
        <h2>What is missing, and why</h2>
        <ul className="explain">
          {malta.length > 0 && (
            <li>
              Malta is not shown ({malta.length === years.length ? 'any year' : ranges(malta.map((m) => m.year))}):{' '}
              {malta[0].reason}. The method places foreign-owned profit section by section, so the sections cannot be
              merged.
            </li>
          )}
          {shown.map(([g, name]) => {
            const lines = data.gaps.filter((x) => x.geo === g);
            if (!lines.length) return null;
            return (
              <li key={g}>
                {name}, balance-of-payments lines suppressed and so omitted (retention overstated; a suppressed bank
                receipt instead understates it):
                <ul>
                  {lines.map((x) => (
                    <li key={x.line}>
                      {x.line}: {ranges(x.years)}
                    </li>
                  ))}
                </ul>
              </li>
            );
          })}
          <li>
            From 2021 the data on foreign-controlled firms cover finance in every country; before, foreign-owned
            banks&apos; profit comes from the balance of payments. Years before and after 2021 therefore differ in
            scope. Where 2021–2022 are missing (Luxembourg), the step shows between 2020 and 2023.
          </li>
          {skippedOther.map((s) => (
            <li key={`${s.geo}${s.year}`}>
              {COUNTRIES.find(([g]) => g === s.geo)?.[1] ?? s.geo} {s.year} not shown: {s.reason}
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
