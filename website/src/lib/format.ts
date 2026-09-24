const eurFmt = new Intl.NumberFormat('en-GB', { maximumFractionDigits: 0 });
const eurFmt1 = new Intl.NumberFormat('en-GB', { minimumFractionDigits: 1, maximumFractionDigits: 1 });

/** EUR millions with thousands separators; one decimal only below 10 (no false precision). */
export function eurM(v: number | null | undefined): string {
  if (v == null || !Number.isFinite(v)) return 'n/a';
  const a = Math.abs(v);
  if (a > 0 && a < 0.05) return '<€0.1m';
  return `€${a < 10 ? eurFmt1.format(v) : eurFmt.format(v)}m`;
}

/** Share (0-1) formatted as percent with one decimal. */
export function pct(v: number | null | undefined, digits = 1): string {
  if (v == null || !Number.isFinite(v)) return 'n/a';
  const lim = 0.5 * Math.pow(10, -digits) / 100;
  if (v !== 0 && Math.abs(v) < lim) return `<${(lim * 200).toFixed(digits)}%`;
  return `${(v * 100).toFixed(digits)}%`;
}

/** Euro-cent amount of a €1 decomposition, e.g. 0.64 -> "64.0c". */
export function cents(v: number | null | undefined): string {
  if (v == null || !Number.isFinite(v)) return 'n/a';
  return `${(v * 100).toFixed(1)}c`;
}

export function int(v: number | null | undefined): string {
  if (v == null || !Number.isFinite(v)) return 'n/a';
  return eurFmt.format(v);
}
