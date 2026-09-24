import namesJson from '../../public/data/names.json';
import type { FlowRow, Names } from './types';

const NAMES = namesJson as Names;
let dn: Intl.DisplayNames | null = null;
try {
  dn = new Intl.DisplayNames(['en'], { type: 'region' });
} catch {
  dn = null;
}

export function recipientName(code: string): string {
  if (NAMES.recipients[code]) return NAMES.recipients[code];
  if (code === 'UNRESOLVED') return 'Unresolved';
  if (/^[A-Z]{2}$/.test(code) && dn) {
    try {
      return dn.of(code === 'EL' ? 'GR' : code === 'UK' ? 'GB' : code) || code;
    } catch {
      return code;
    }
  }
  return code;
}

export function industryName(code: string): string {
  return NAMES.industries[code] || code;
}

export function normaliseRows(rows: FlowRow[]): FlowRow[] {
  rows.forEach((r) => {
    r.recipient_name = recipientName(r.recipient);
    if (!r.industry_name) r.industry_name = industryName(r.industry);
  });
  return rows;
}
