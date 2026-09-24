'use client';
import { useState } from 'react';
import Link from 'next/link';
import type { Headline } from '@/lib/types';
import { pct } from '@/lib/format';
import Kpis from './Kpis';
import Contrast from './Contrast';
import TimeSeries from './TimeSeries';
import YearSelect from './YearSelect';

export const defaultYear = (h: Headline) => h.io_years[h.io_years.length - 1];

export default function Overview({ headline }: { headline: Headline }) {
  const [year, setYear] = useState(defaultYear(headline));
  const h = headline.series.find((r) => r.year === year)!;
  const s = headline.series;
  const dvr = s.map((r) => r.domestic_value_retention);
  return (
    <>
      <h1>Of the value generated in Cyprus, where does it ultimately accrue?</h1>
      <p className="lede">
        Official statistics show very large income payments abroad. Most of that money only passes through Cypriot
        holding companies. Following the income that Cypriot production actually generates, between{' '}
        <strong>
          {pct(Math.min(...dvr), 0)} and {pct(Math.max(...dvr), 0)}
        </strong>{' '}
        of GDP stays with residents in every year from {s[0].year} to {s[s.length - 1].year}.
      </p>
      <div className="controls">
        <YearSelect years={headline.years} value={year} onChange={setYear} />
        <span className="small muted">
          Hover or tap any number for its status, confidence, source and method.
        </span>
      </div>
      <Kpis h={h} />
      <p className="small muted">
        Revenue is not value: the project works in value added (revenue minus intermediate inputs), never revenue.
        &ldquo;Foreign&rdquo; means not resident in Cyprus, not nationality.{' '}
        <Link href="/country/cyprus/flows/">See where the {pct(h.foreign_value_leakage)} goes →</Link>
      </p>
      <Contrast headline={headline} year={year} />
      <TimeSeries headline={headline} year={year} />
    </>
  );
}
