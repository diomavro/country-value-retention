'use client';
import { useState } from 'react';
import type { PerEuroProduct } from '@/lib/types';
import { FRAME_B_PROV, SPECIAL_RECIPIENTS, isSpecial } from '@/lib/concepts';
import { recipientName } from '@/lib/names';
import { cents } from '@/lib/format';
import { useJson } from '@/lib/useJson';
import StackBar from './StackBar';
import BarList from './BarList';
import YearSelect from './YearSelect';

export default function PerEuro({ years }: { years: number[] }) {
  const [year, setYear] = useState(years[years.length - 1]);
  const [prod, setProd] = useState('I');
  const { data } = useJson<{ year: number; products: Record<string, PerEuroProduct> }>(`cy/per_euro_${year}.json`);
  const p = data?.products[prod];
  const products = data ? Object.entries(data.products).sort((a, b) => a[1].name.localeCompare(b[1].name)) : [];
  const abroadVA = p ? p.channels.domestic_value_added - p.domestic_va_retained : 0;
  const foreignTotal = p ? abroadVA + p.channels.imported_inputs : 0;
  const top = p ? Object.entries(p.recipients) : [];
  const topSum = top.reduce((a, [, v]) => a + v, 0);
  return (
    <section className="card">
      <h2>Where €1 spent on a Cypriot product ends up (Frame B)</h2>
      <p className="explain">
        Every €1 of final spending on domestic output ends up as exactly one of three things: domestic value added +
        imported inputs + taxes on products = €1. The Cypriot value added is then sent through Frame A&apos;s recipient
        shares, and the imported inputs to the countries they came from.
      </p>
      <div className="controls">
        <YearSelect years={years} value={year} onChange={setYear} />
        <label>
          Product
          <select value={prod} onChange={(e) => setProd(e.target.value)}>
            {products.map(([k, v]) => (
              <option key={k} value={k}>{v.name}</option>
            ))}
          </select>
        </label>
      </div>
      {p && (
        <>
          <h3>{p.name}, {year}: €1 of final spending</h3>
          <StackBar
            segs={[
              { key: 'ret', label: 'Cypriot value added, stays with residents', value: p.domestic_va_retained, display: cents(p.domestic_va_retained), color: 'var(--retained)', prov: FRAME_B_PROV },
              { key: 'abr', label: 'Cypriot value added, accrues abroad', value: abroadVA, display: cents(abroadVA), color: 'var(--s1)', prov: FRAME_B_PROV },
              { key: 'imp', label: 'Imported inputs (foreign value added)', value: p.channels.imported_inputs, display: cents(p.channels.imported_inputs), color: 'var(--s2)', prov: FRAME_B_PROV, note: 'Imported inputs are the foreign producers’ value added, not leakage of the Cypriot industry, and are not part of Cyprus’s GDP.' },
              { key: 'tax', label: 'Taxes on products', value: p.channels.product_taxes_on_inputs, display: cents(p.channels.product_taxes_on_inputs), color: 'var(--s3)', prov: FRAME_B_PROV },
            ]}
          />
          <h3>Largest foreign recipients of that €1</h3>
          <p className="explain">
            Top 8 recipients of the {cents(foreignTotal)} that goes abroad (Cypriot value added accruing to non-residents plus imported inputs).
            The remaining {cents(Math.max(0, foreignTotal - topSum))} goes to other recipients.
          </p>
          <BarList
            ariaLabel="Recipients per euro"
            items={top.map(([k, v]) => ({
              key: k,
              label: recipientName(k),
              value: v,
              display: cents(v),
              color: isSpecial(k) ? 'var(--neutral)' : 'var(--s1)',
              prov: FRAME_B_PROV,
              note: SPECIAL_RECIPIENTS[k],
            }))}
          />
        </>
      )}
    </section>
  );
}
