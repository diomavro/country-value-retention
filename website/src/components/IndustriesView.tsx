'use client';
import React, { useMemo, useState } from 'react';
import type { Headline, Industry, Prov } from '@/lib/types';
import { useJson } from '@/lib/useJson';
import { useFlows, foreignRows, sumBy } from '@/lib/useFlows';
import { METRICS, MECHANISMS, MECH_ORDER, aggregateProv, SPECIAL_RECIPIENTS } from '@/lib/concepts';
import { recipientName } from '@/lib/names';
import { eurM, pct } from '@/lib/format';
import { Num, usePopHandlers, ProvCard } from './Prov';
import { MECH_COLOR } from './Sankey';
import YearSelect from './YearSelect';

type Col = 'name' | 'gva' | 'direct_foreign_input_exposure' | 'foreign_ownership_capture' | 'domestic_retention';

const GVA_PROV: Prov = {
  status: 'observed',
  confidence_level: 'high',
  source: 'CYSTAT/Eurostat national accounts (nama_10_a64)',
  source_url: 'https://ec.europa.eu/eurostat/databrowser/view/nama_10_a64/default/table',
  methodology: 'Gross value added at basic prices by industry, current prices, EUR million.',
};

function Seg({ w, color, tip }: { w: number; color: string; tip: () => React.ReactNode }) {
  const h = usePopHandlers(tip);
  return <div className="mark" tabIndex={0} style={{ width: `${w}%`, background: color, height: '100%' }} {...h} />;
}

export default function IndustriesView({ headline }: { headline: Headline }) {
  const [year, setYear] = useState(headline.io_years[headline.io_years.length - 1]);
  const [sort, setSort] = useState<{ col: Col; asc: boolean }>({ col: 'gva', asc: false });
  const { data } = useJson<{ year: number; industries: Industry[] }>(`cy/industries_${year}.json`);
  const { rows } = useFlows(year);
  const byInd = useMemo(() => sumBy(rows, (r) => r.industry), [rows]);

  const list = useMemo(() => {
    const l = [...(data?.industries || [])];
    l.sort((a, b) => {
      const va = a[sort.col], vb = b[sort.col];
      if (va == null) return 1;
      if (vb == null) return -1;
      const d = typeof va === 'string' ? va.localeCompare(vb as string) : (va as number) - (vb as number);
      return sort.asc ? d : -d;
    });
    return l;
  }, [data, sort]);

  const decomp = useMemo(() => {
    if (!data) return [];
    const gva = new Map(data.industries.map((i) => [i.industry, i]));
    return [...sumBy(foreignRows(rows), (r) => r.industry).entries()]
      .filter(([k]) => gva.get(k)?.gva)
      .map(([k, v]) => {
        const g = gva.get(k)!.gva;
        const mech = sumBy(v.rows, (r) => r.mechanism);
        return { k, name: gva.get(k)!.name, g, share: v.value / g, mech };
      })
      .sort((a, b) => b.share - a.share)
      .slice(0, 20);
  }, [data, rows]);
  const maxShare = Math.max(...decomp.map((d) => d.share), 1e-9);

  const th = (col: Col, label: string, right = true) => (
    <th className={right ? 'r' : ''} aria-sort={sort.col === col ? (sort.asc ? 'ascending' : 'descending') : 'none'}>
      <button className="sort" onClick={() => setSort({ col, asc: sort.col === col ? !sort.asc : col === 'name' })}>
        {label} {sort.col === col ? (sort.asc ? '▲' : '▼') : ''}
      </button>
    </th>
  );
  const ioMissing = !headline.io_years.includes(year);

  return (
    <>
      <h1>Industries</h1>
      <p className="lede">
        How much each industry adds, how much of its inputs are imported, how much of its operating surplus goes to
        foreign owners, and how much of its value added stays with residents. These are different bases and are never
        added together.
      </p>
      <div className="controls">
        <YearSelect years={headline.years} value={year} onChange={setYear} />
        {ioMissing && <span className="callout">No input-output table is published for {year}: input exposure is not available.</span>}
      </div>
      <section className="card">
        <h2>Industry table, {year}</h2>
        <p className="explain">
          Foreign input exposure: share of inputs that are imported (direct; total including suppliers in the tooltip).
          Foreign ownership capture: share of operating surplus accruing to foreign owners. Domestic retention: share of
          the industry&apos;s value added whose income stays with residents. Click a column to sort.
        </p>
        <div className="table-scroll tall">
          <table className="data">
            <thead>
              <tr>
                {th('name', 'Industry', false)}
                {th('gva', 'GVA')}
                {th('direct_foreign_input_exposure', 'Foreign input exposure')}
                {th('foreign_ownership_capture', 'Foreign ownership capture')}
                {th('domestic_retention', 'Domestic retention')}
                <th>Main recipient countries</th>
              </tr>
            </thead>
            <tbody>
              {list.map((i) => {
                const ir = byInd.get(i.industry)?.rows || [];
                const fr = foreignRows(ir);
                const capRows = fr.filter((r) => r.mechanism === 'fdi_income');
                return (
                  <tr key={i.industry}>
                    <td>{i.name}</td>
                    <td className="r"><Num prov={GVA_PROV} title={`${i.name} GVA, ${year}`}>{eurM(i.gva)}</Num></td>
                    <td className="r">
                      <Num
                        prov={{ ...METRICS.foreign_input_exposure.prov, note: `Direct ${pct(i.direct_foreign_input_exposure)}; total import content incl. suppliers ${pct(i.total_import_content)}.` }}
                        title={`${i.name}: imported share of inputs, ${year}`}
                      >
                        {pct(i.direct_foreign_input_exposure)}
                      </Num>
                    </td>
                    <td className="r">
                      <Num prov={capRows.length ? { ...aggregateProv(capRows, 'Foreign owners’ income'), methodology: `Foreign-owned net operating surplus before corporate tax / the industry's net operating surplus. ` + aggregateProv(capRows, 'FDI income').methodology } : METRICS.foreign_ownership_capture.prov} title={`${i.name}: foreign ownership capture, ${year}`}>
                        {pct(i.foreign_ownership_capture)}
                      </Num>
                    </td>
                    <td className="r">
                      <Num prov={fr.length ? { ...aggregateProv(fr, 'Income paid abroad'), methodology: `1 − (income paid abroad ${eurM(i.foreign_outflow)} / GVA). ` + aggregateProv(fr, 'Income paid abroad').methodology } : METRICS.domestic_value_retention.prov} title={`${i.name}: domestic retention, ${year}`}>
                        {pct(i.domestic_retention)}
                      </Num>
                    </td>
                    <td className="small">
                      {i.main_recipients.map((r) => {
                        const rr = fr.filter((x) => x.recipient === r.recipient);
                        return (
                          <div key={r.recipient} style={{ whiteSpace: 'nowrap' }}>
                            <Num prov={rr.length ? { ...aggregateProv(rr, recipientName(r.recipient)), note: SPECIAL_RECIPIENTS[r.recipient] } : METRICS.foreign_value_leakage.prov} title={`${i.name} → ${recipientName(r.recipient)}`}>
                              {recipientName(r.recipient)} {eurM(r.value)}
                            </Num>
                          </div>
                        );
                      })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <h2>What each industry pays abroad, by mechanism, {year}</h2>
        <p className="explain">
          Income paid to non-residents as a share of the industry&apos;s own value added, split by mechanism. The 20
          industries with the highest share are shown; bars share one scale.
        </p>
        <div className="legend">
          {MECH_ORDER.filter((m) => decomp.some((d) => d.mech.has(m))).map((m) => (
            <span key={m}><span className="sw" style={{ background: MECH_COLOR[m] }} />{MECHANISMS[m].label}</span>
          ))}
        </div>
        <div className="barlist">
          {decomp.map((d) => (
            <React.Fragment key={d.k}>
              <div className="bl-name" title={d.name}>{d.name}</div>
              <div className="bl-bar">
                <div className="stackbar" style={{ width: `${(d.share / maxShare) * 75}%`, height: 16, minWidth: 3 }}>
                  {MECH_ORDER.filter((m) => d.mech.has(m)).map((m) => {
                    const e = d.mech.get(m)!;
                    return (
                      <Seg
                        key={m}
                        w={(e.value / (d.share * d.g)) * 100}
                        color={MECH_COLOR[m]}
                        tip={() => <ProvCard value={`${eurM(e.value)} · ${pct(e.value / d.g)} of GVA`} title={`${d.name}: ${MECHANISMS[m].label}`} prov={aggregateProv(e.rows, MECHANISMS[m].label)} />}
                      />
                    );
                  })}
                </div>
                <span className="bl-val"><Num prov={aggregateProv([...d.mech.values()].flatMap((e) => e.rows), `${d.name}: income paid abroad`)} title={`${d.name}: income paid abroad ÷ GVA (${eurM(d.g)})`}>{pct(d.share)}</Num></span>
              </div>
            </React.Fragment>
          ))}
        </div>
      </section>
    </>
  );
}
