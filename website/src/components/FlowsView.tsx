'use client';
import React, { useMemo, useState } from 'react';
import type { Headline } from '@/lib/types';
import { useFlows, foreignRows, sumBy, recipientGroups } from '@/lib/useFlows';
import { MECHANISMS, MECH_ORDER, SPECIAL_RECIPIENTS, aggregateProv, isSpecial } from '@/lib/concepts';
import { recipientName, industryName } from '@/lib/names';
import { eurM, pct } from '@/lib/format';
import YearSelect from './YearSelect';
import Sankey, { MECH_COLOR } from './Sankey';
import BarList from './BarList';
import Heatmap from './Heatmap';
import Drill from './Drill';

type Sel = { recipient: string; industry?: string } | null;

export default function FlowsView({ headline }: { headline: Headline }) {
  const [year, setYear] = useState(headline.years[headline.years.length - 1]);
  const [retained, setRetained] = useState(false);
  const [sel, setSel] = useState<Sel>(null);
  const { flows, rows, loading, error } = useFlows(year);
  const gdp = flows?.gdp || 1;

  const recips = useMemo(() => {
    const by = [...sumBy(foreignRows(rows), (r) => r.recipient).entries()].sort((a, b) => b[1].value - a[1].value);
    return by.map(([k, v]) => ({
      key: k,
      label: recipientName(k),
      value: v.value,
      display: `${eurM(v.value)} · ${pct(v.value / gdp)}`,
      color: isSpecial(k) ? 'var(--neutral)' : 'var(--s1)',
      prov: aggregateProv(v.rows, `${recipientName(k)}`),
      note: SPECIAL_RECIPIENTS[k],
    }));
  }, [rows, gdp]);

  const drillRows = useMemo(() => {
    if (!sel) return [];
    const { group } = recipientGroups(rows);
    return foreignRows(rows).filter(
      (r) => (sel.recipient === 'OTHER' ? group(r.recipient) === 'OTHER' : r.recipient === sel.recipient) && (!sel.industry || r.industry === sel.industry),
    );
  }, [rows, sel]);

  const pick = (s: Sel) => {
    setSel(s);
    setTimeout(() => document.getElementById('drill')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
  };
  const mechsPresent = ['retained_domestic', ...MECH_ORDER].filter((m) => rows.some((r) => r.mechanism === m));
  const totalForeign = foreignRows(rows).reduce((a, r) => a + r.value, 0);

  return (
    <>
      <h1>Where the income from Cypriot production goes</h1>
      <p className="lede">
        Frame A asks: of the value created in Cyprus this year, who receives it? Start from GDP and follow each
        income payment to non-residents (wages of non-resident workers, profits, dividends and interest paid to
        foreign owners and lenders, taxes paid to EU institutions). What remains is retained.
      </p>
      <div className="controls">
        <YearSelect years={headline.years} value={year} onChange={(y) => { setYear(y); setSel(null); }} />
        <label>
          View
          <span className="seg" role="group" aria-label="Sankey scope">
            <button aria-pressed={!retained} onClick={() => setRetained(false)}>Only income paid abroad</button>
            <button aria-pressed={retained} onClick={() => setRetained(true)}>All of GDP (incl. retained)</button>
          </span>
        </label>
        {loading && <span className="small muted">Loading {year}…</span>}
        {error && <span className="callout">Could not load data: {error}</span>}
      </div>
      <div className={loading ? 'loading' : ''}>
        <section className="card">
          <h2>GDP → mechanism → recipient, {year}</h2>
          <p className="explain">
            Width is EUR million. Of GDP of {eurM(gdp)}, {eurM(gdp - totalForeign)} ({pct(1 - totalForeign / gdp)}) is retained by residents and {eurM(totalForeign)} ({pct(totalForeign / gdp)} of GDP) is income generated in Cyprus that accrues to non-residents.
            Recipients that are not a single country (confidential, unallocated, regional aggregates) are shown in gray and never
            hidden. Click a recipient to see the rows behind it.
          </p>
          <div className="legend">
            {mechsPresent.filter((m) => retained || m !== 'retained_domestic').map((m) => (
              <span key={m} title={MECHANISMS[m].explain}>
                <span className="sw" style={{ background: MECH_COLOR[m] }} />
                {MECHANISMS[m].label}
              </span>
            ))}
          </div>
          <p className="small muted mobile-only">Wide chart: scroll sideways inside the frame.</p>
          {rows.length > 0 && <Sankey rows={rows} gdp={gdp} includeRetained={retained} onRecipient={(r) => pick({ recipient: r })} />}
        </section>

        <div className="grid2">
          <section className="card">
            <h2>Income paid abroad by recipient, {year}</h2>
            <p className="explain">
              EUR million and share of GDP. Gray bars (*) are not a single country: the source does not publish the
              partner, or it is a regional aggregate. Click a bar for the calculation behind it.
            </p>
            <BarList ariaLabel="Recipients" items={recips} selected={sel?.recipient ?? null} onSelect={(k) => pick({ recipient: k })} />
          </section>
          <section className="card">
            <h2>What the non-country recipients mean</h2>
            <dl className="small">
              {Object.entries(SPECIAL_RECIPIENTS)
                .filter(([k]) => recips.some((r) => r.key === k))
                .map(([k, v]) => (
                  <React.Fragment key={k}>
                    <dt><strong>{recipientName(k)}</strong> <span className="muted">({k})</span></dt>
                    <dd style={{ margin: '0 0 0.6rem' }}>{v}</dd>
                  </React.Fragment>
                ))}
            </dl>
          </section>
        </div>

        {sel && drillRows.length > 0 && (
          <Drill
            rows={drillRows}
            gdp={gdp}
            title={`${sel.recipient === 'OTHER' ? 'Other countries' : recipientName(sel.recipient)}${sel.industry ? ` from ${industryName(sel.industry)}` : ''}, ${year}`}
            onClose={() => setSel(null)}
          />
        )}

        <section className="card">
          <h2>Industry × recipient, {year}</h2>
          <p className="explain">
            Income paid abroad only (retained value is not shown here). Rows: industries with the largest payments abroad. Click a cell for its rows.
          </p>
          {rows.length > 0 && <Heatmap rows={rows} onCell={(i, r) => pick({ recipient: r, industry: i })} />}
        </section>
      </div>
    </>
  );
}
