import META from '../generated/metric_meta.json';
import type { Prov, FlowRow } from './types';

/** Plain-language labels for the income mechanisms in the flow tensor. */
export const MECHANISMS: Record<string, { label: string; explain: string }> = {
  retained_domestic: {
    label: 'Retained in Cyprus',
    explain: 'Value added whose income stays with residents: GVA minus the income attributed to non-residents.',
  },
  compensation_nonresident: {
    label: 'Wages of non-resident workers',
    explain: 'Compensation paid to workers who are not resident in Cyprus (residence, not nationality).',
  },
  fdi_income: {
    label: 'Profits to foreign owners (FDI)',
    explain: "The foreign owner's share of operating surplus, followed to the ultimate owner's country where the source allows.",
  },
  portfolio_income: {
    label: 'Portfolio income to non-residents',
    explain: 'Dividends and interest paid to foreign portfolio investors, drawn only from operating surplus.',
  },
  other_investment_income: {
    label: 'Interest to foreign lenders',
    explain: 'Interest on loans and deposits paid to non-resident lenders, drawn only from operating surplus.',
  },
  public_debt_interest: {
    label: 'Interest on public debt held abroad',
    explain: 'Interest the Cypriot government pays to non-resident holders of its debt.',
  },
  taxes_to_eu_institutions: {
    label: 'Taxes paid to EU institutions',
    explain: 'Taxes collected in Cyprus that accrue to the EU budget (e.g. customs duties).',
  },
};

export const MECH_ORDER = [
  'compensation_nonresident',
  'fdi_income',
  'portfolio_income',
  'other_investment_income',
  'public_debt_interest',
  'taxes_to_eu_institutions',
];

/** Recipients that are not a single country. Shown honestly, never hidden. */
export const SPECIAL_RECIPIENTS: Record<string, string> = {
  CONFIDENTIAL_PARTNERS:
    'Amounts the official source publishes only in the total, not by partner country, for confidentiality. They are real payments abroad; only the country is not published.',
  WORLD_UNALLOCATED:
    'Payments abroad known in total but not broken down by country in the source. They are not assigned a guessed country.',
  EU27_UNALLOCATED: 'Payments to EU countries known in total but not broken down by country in the source.',
  EXTRA_EU_UNALLOCATED: 'Payments to non-EU countries known in total but not broken down by country in the source.',
  OFFSHO: "Eurostat's aggregate for offshore financial centres; the source does not name the individual jurisdiction.",
  ROW_FIGARO:
    'The residual "rest of world" region of the FIGARO inter-country input-output table: countries not modelled individually.',
  EU_INST: 'EU institutions (the EU budget), not a country.',
  UNRESOLVED:
    'Where the ownership records run out, the remaining share is labelled unresolved, never assigned a guessed country.',
};

export const isSpecial = (r: string) => r in SPECIAL_RECIPIENTS || r.endsWith('_UNALLOCATED');

export const STATUS_EXPLAIN: Record<string, string> = {
  observed: 'printed by an official source (only units/labels changed)',
  modelled: 'computed deterministically from observed inputs',
  estimated: 'needed an allocation key or assumption, written down next to it',
  illustrative: 'a teaching example; never part of the results',
};

const CYSTAT = 'https://cystatdb.cystat.gov.cy/pxweb/en/8.CYSTAT-DB/';

/** Headline measures: one plain sentence each (wording from docs/concepts.md) plus provenance. */
export const METRICS: Record<string, { label: string; question: string; prov: Prov }> = {
  gdp: {
    label: 'GDP',
    question: 'All value added in Cyprus in the year: the value created by Cypriot production.',
    prov: META.gdp as Prov,
  },
  domestic_value_retention: {
    label: 'Domestic Value Retention',
    question: 'Share of GDP whose income stays with residents.',
    prov: META.domestic_value_retention as Prov,
  },
  foreign_value_leakage: {
    label: 'Foreign Value Leakage',
    question: 'Share of GDP whose income accrues to non-residents: 1 minus Domestic Value Retention.',
    prov: META.foreign_value_leakage as Prov,
  },
  foreign_input_exposure: {
    label: 'Foreign Input Exposure',
    question: 'Share of intermediate inputs that are imported.',
    prov: META.foreign_input_exposure as Prov,
  },
  foreign_ownership_capture: {
    label: 'Foreign Ownership Capture',
    question: 'Share of operating surplus accruing to foreign owners.',
    prov: META.foreign_ownership_capture as Prov,
  },
  foreign_creditor_income_share_of_nos: {
    label: 'Foreign creditor income share',
    question: 'Share of net operating surplus paid to foreign lenders and portfolio investors as interest and portfolio income.',
    prov: META.foreign_creditor_income_share_of_nos as Prov,
  },
  foreign_labour_income_share: {
    label: 'Foreign Labour Income',
    question: 'Share of compensation paid to non-resident workers.',
    prov: META.foreign_labour_income_share as Prov,
  },
  official_primary_income_outflow_to_gdp: {
    label: 'Official primary income paid abroad',
    question:
      'The official, unadjusted balance-of-payments figure. It includes income that only passes through Cypriot special purpose entities and was never generated by Cypriot production.',
    prov: META.official_primary_income_outflow_to_gdp as Prov,
  },
  fdi_income_paid_non_spe: {
    label: 'FDI income paid, excluding SPEs',
    question: 'Direct-investment income paid abroad by resident firms other than special purpose entities.',
    prov: META.fdi_income_paid_non_spe as Prov,
  },
};

export const FRAME_B_PROV: Prov = {
  status: 'modelled',
  confidence_level: 'medium',
  source: 'Model output (Frame B): CYSTAT symmetric input-output tables, Leontief inverse, FIGARO for import origin',
  source_url: CYSTAT,
  methodology:
    'Every EUR 1 of final spending on a Cypriot product = domestic value added + imported inputs + taxes on products (checked for every industry and year). Cypriot value added is then sent through Frame A recipient shares; imported inputs go to the countries they came from.',
};

export function splitUrls(u?: string | null): string[] {
  if (!u) return [];
  return u
    .split(/\s*;\s*/)
    .map((s) => s.trim())
    .filter((s) => /^https?:\/\//.test(s));
}

function mix(rows: FlowRow[], key: 'status' | 'confidence_level'): string {
  const tot = rows.reduce((a, r) => a + r.value, 0);
  const m = new Map<string, number>();
  rows.forEach((r) => m.set(r[key], (m.get(r[key]) || 0) + r.value));
  const parts = [...m.entries()].sort((a, b) => b[1] - a[1]);
  if (parts.length === 1) return parts[0][0];
  return parts.map(([k, v]) => `${k} ${tot > 0 ? ((v / tot) * 100).toFixed(0) : '0'}%`).join(', ') + ' (value-weighted)';
}

/** Provenance of a total built from flow rows: value-weighted mix of status/confidence, union of sources. */
export function aggregateProv(rows: FlowRow[], what: string): Prov {
  const sources = [...new Set(rows.map((r) => r.source))];
  const urls = [...new Set(rows.flatMap((r) => splitUrls(r.source_url)))];
  const meths = [...new Set(rows.map((r) => r.methodology.replace(/\s*\[.*\]$/, '')))];
  return {
    status: rows.length ? mix(rows, 'status') : 'n/a',
    confidence_level: rows.length ? mix(rows, 'confidence_level') : 'n/a',
    source: sources.join('; '),
    source_url: urls.join(' ; '),
    methodology:
      `${what}: sum of ${rows.length.toLocaleString('en-GB')} rows of the flow table (industry x recipient x mechanism). ` +
      (meths.length <= 3
        ? `Methods: ${meths.join(' | ')}`
        : `${meths.length} distinct methods, e.g. ${meths.slice(0, 2).join(' | ')}. Click for the row-level drill-down.`),
  };
}
