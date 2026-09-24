import type { Firm, Ownership, OwnEdge, Prov } from './types';

export const OWN_COLORS: Record<string, string> = {
  CY: 'var(--s1)',
  US: 'var(--s2)',
  GR: 'var(--s3)',
  FR: 'var(--s4)',
  DE: 'var(--s5)',
  AE: 'var(--s6)',
  IE: 'var(--s7)',
};
export const ownColor = (c: string) => (c === 'UNRESOLVED' ? 'var(--surface)' : OWN_COLORS[c] || 'var(--neutral)');

export const UCI_STATUS: Record<string, string> = {
  uncontrolled_company: 'Ultimate controlling entity is a company with no controlling shareholder (e.g. listed, widely held).',
  controlled_by_persons_of_unknown_residence: 'A majority is held by individuals or families whose residence is not documented, so the controlling country is unresolved (nationality is never used).',
  terminal_owner: 'Chain ends at an identified final owner (person, family, state or fund).',
  undocumented_owners: 'Owners above this point are not documented in public sources; the rest is unresolved.',
};

export function firmProv(f: Firm, o: Ownership): Prov {
  const es = o.edges.filter((e) => e.to === f.entity_id);
  const urls = [...new Set(es.map((e) => e.source_url).filter(Boolean))];
  return {
    status: 'modelled',
    confidence_level: f.confidence,
    source: es.length ? [...new Set(es.map((e) => e.source))].join('; ') : 'Company ownership layer (entities.csv, ownership_edges.csv)',
    source_url: urls.join(' ; '),
    methodology:
      'Ownership represented as a directed graph and followed recursively to the ultimate owners; cross-holdings summed once each (same algebra as the Leontief inverse). Where the records run out, the remaining share is labelled unresolved, never assigned a guessed country.',
  };
}

export function edgeProv(e: OwnEdge): Prov {
  return {
    status: 'observed',
    confidence_level: e.confidence,
    source: `${e.source} (tier ${e.source_tier}, as of ${e.as_of_date})`,
    source_url: e.source_url,
    methodology: `${e.share_pct}% ${e.share_type} held by the parent.${e.presumption ? ` Presumption: ${e.presumption}.` : ''}`,
  };
}

/** Longest-path layer from operating firms (0) up to owners; back edges from cross-holdings are ignored. */
export function layers(o: Ownership): Map<string, number> {
  const kids = new Map<string, string[]>();
  const add = (p: string, c: string) => kids.set(p, [...(kids.get(p) || []), c]);
  o.edges.forEach((e) => add(e.from, e.to));
  o.unpriced_edges.forEach((e) => add(e.parent_entity_id, e.child_entity_id));
  const memo = new Map<string, number>();
  const stack = new Set<string>();
  const f = (n: string): number => {
    if (memo.has(n)) return memo.get(n)!;
    if (stack.has(n)) return -1;
    stack.add(n);
    let d = 0;
    for (const c of kids.get(n) || []) {
      const v = f(c);
      if (v >= 0) d = Math.max(d, v + 1);
    }
    stack.delete(n);
    memo.set(n, d);
    return d;
  };
  o.nodes.forEach((n) => f(n.id));
  return memo;
}

export function ancestors(o: Ownership, id: string): Set<string> {
  const out = new Set<string>([id]);
  const q = [id];
  while (q.length) {
    const c = q.pop()!;
    o.edges.filter((e) => e.to === c).forEach((e) => !out.has(e.from) && (out.add(e.from), q.push(e.from)));
    o.unpriced_edges.filter((e) => e.child_entity_id === c).forEach((e) => !out.has(e.parent_entity_id) && (out.add(e.parent_entity_id), q.push(e.parent_entity_id)));
  }
  return out;
}
