'use client';
import { useMemo, useState } from 'react';
import type { Headline } from '@/lib/types';
import { useFlows, foreignRows, sumBy } from '@/lib/useFlows';
import { MECHANISMS, SPECIAL_RECIPIENTS, aggregateProv, isSpecial } from '@/lib/concepts';
import { recipientName, industryName } from '@/lib/names';
import { eurM, pct } from '@/lib/format';
import YearSelect from './YearSelect';
import Kpis from './Kpis';
import Contrast from './Contrast';
import TimeSeries from './TimeSeries';
import BarList from './BarList';
import Drill from './Drill';
import { Num } from './Prov';
import { MECH_COLOR } from './Sankey';
import { defaultYear } from './Overview';

export default function CountryDashboard({ headline }: { headline: Headline }) {
  const [year, setYear] = useState(defaultYear(headline));
  const [industry, setIndustry] = useState('');
  const [recipient, setRecipient] = useState('');
  const { flows, rows, loading } = useFlows(year);
  const gdp = flows?.gdp || 1;
  const h = headline.series.find((r) => r.year === year)!;

  const industries = useMemo(() => [...new Set(rows.map((r) => r.industry))].map((k) => ({ k, n: industryName(k) })).sort((a, b) => a.n.localeCompare(b.n)), [rows]);
  const recipients = useMemo(() => [...new Set(foreignRows(rows).map((r) => r.recipient))].map((k) => ({ k, n: recipientName(k) })).sort((a, b) => a.n.localeCompare(b.n)), [rows]);

  const slice = useMemo(() => rows.filter((r) => (!industry || r.industry === industry) && (!recipient || r.recipient === recipient)), [rows, industry, recipient]);
  const fslice = foreignRows(slice);
  const fTotal = fslice.reduce((a, r) => a + r.value, 0);
  const allInSlice = rows.filter((r) => !industry || r.industry === industry);
  const gva = allInSlice.reduce((a, r) => a + r.value, 0);
  const bars = (key: 'mechanism' | 'recipient' | 'industry') =>
    [...sumBy(fslice, (r) => r[key]).entries()]
      .sort((a, b) => b[1].value - a[1].value)
      .slice(0, key === 'industry' ? 15 : 40)
      .map(([k, v]) => {
        const label = key === 'mechanism' ? MECHANISMS[k]?.label || k : key === 'recipient' ? recipientName(k) : industryName(k);
        return {
          key: k,
          label,
          value: v.value,
          display: eurM(v.value),
          color: key === 'mechanism' ? MECH_COLOR[k] : key === 'recipient' && isSpecial(k) ? 'var(--neutral)' : 'var(--s1)',
          prov: aggregateProv(v.rows, label),
          note: key === 'mechanism' ? MECHANISMS[k]?.explain : key === 'recipient' ? SPECIAL_RECIPIENTS[k] : undefined,
        };
      });
  const sliceName = [industry && industryName(industry), recipient && `to ${recipientName(recipient)}`].filter(Boolean).join(' ') || 'All industries, all recipients';

  return (
    <>
      <h1>Cyprus</h1>
      <p className="lede">
        Choose a year, an industry and a recipient country. Every total below is built from rows of the flow table
        (industry × recipient × mechanism), and each row states its source and calculation.
      </p>
      <div className="controls">
        <YearSelect years={headline.years} value={year} onChange={setYear} />
        <label>
          Industry
          <select value={industry} onChange={(e) => setIndustry(e.target.value)}>
            <option value="">All industries</option>
            {industries.map((i) => (
              <option key={i.k} value={i.k}>{i.n}</option>
            ))}
          </select>
        </label>
        <label>
          Recipient
          <select value={recipient} onChange={(e) => setRecipient(e.target.value)}>
            <option value="">All recipients abroad</option>
            {recipients.map((i) => (
              <option key={i.k} value={i.k}>{i.n}</option>
            ))}
          </select>
        </label>
        {loading && <span className="small muted">Loading…</span>}
      </div>
      <Kpis h={h} />
      <section className={`card${loading ? ' loading' : ''}`}>
        <h2>{sliceName}, {year}</h2>
        {recipient && SPECIAL_RECIPIENTS[recipient] && <p className="callout">{SPECIAL_RECIPIENTS[recipient]}</p>}
        <p>
          Income paid to non-residents in this selection:{' '}
          <strong>
            <Num prov={aggregateProv(fslice, sliceName)} title={sliceName}>{eurM(fTotal)}</Num>
          </strong>{' '}
          = {pct(fTotal / gdp)} of GDP
          {industry && gva > 0 && (
            <>
              {' '}and {pct(fTotal / gva)} of the industry&apos;s value added (
              <Num prov={aggregateProv(allInSlice, `${industryName(industry)} value added`)} title="Industry value added (sum of retained and paid-abroad rows)">{eurM(gva)}</Num>)
            </>
          )}
          .
        </p>
        <div className="grid2">
          <div>
            <h3>By mechanism</h3>
            <BarList ariaLabel="By mechanism" items={bars('mechanism')} />
          </div>
          {!recipient && (
            <div>
              <h3>By recipient</h3>
              <BarList ariaLabel="By recipient" items={bars('recipient')} selected={recipient} onSelect={setRecipient} />
            </div>
          )}
          {!industry && (
            <div>
              <h3>By industry (largest 15)</h3>
              <BarList ariaLabel="By industry" items={bars('industry')} selected={industry} onSelect={setIndustry} />
            </div>
          )}
        </div>
      </section>
      {fslice.length > 0 && <Drill rows={fslice} gdp={gdp} title={`Rows behind: ${sliceName}, ${year}`} />}
      <Contrast headline={headline} year={year} />
      <TimeSeries headline={headline} year={year} />
    </>
  );
}
