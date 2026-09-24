import Link from 'next/link';
import { notFound } from 'next/navigation';
import { readData } from '@/lib/server';
import type { Ownership, OwnNode } from '@/lib/types';
import { edgeProv, firmProv, UCI_STATUS } from '@/lib/ownership';
import { SPECIAL_RECIPIENTS, splitUrls } from '@/lib/concepts';
import { recipientName } from '@/lib/names';
import { eurM, pct } from '@/lib/format';
import { Num } from '@/components/Prov';

const load = () => readData<Ownership>('cy/ownership.json');

export function generateStaticParams() {
  return load().firms.map((f) => ({ company: f.entity_id }));
}

export async function generateMetadata({ params }: { params: Promise<{ company: string }> }) {
  const { company } = await params;
  const f = load().firms.find((x) => x.entity_id === company);
  return { title: f ? f.legal_name : 'Company' };
}

function Chain({ o, id, seen }: { o: Ownership; id: string; seen: Set<string> }) {
  const parents = o.edges.filter((e) => e.to === id);
  const unpriced = o.unpriced_edges.filter((e) => e.child_entity_id === id);
  if (!parents.length && !unpriced.length) return null;
  const byId = new Map(o.nodes.map((n) => [n.id, n]));
  const name = (n?: OwnNode, fid?: string) => (n ? `${n.name} (${n.country === 'UNRESOLVED' ? 'UNRESOLVED' : recipientName(n.country)})` : fid);
  return (
    <ul className="chain">
      {parents.map((e, i) => {
        const n = byId.get(e.from);
        const loop = seen.has(e.from);
        return (
          <li key={i}>
            <Num prov={edgeProv(e)} title={`${n?.name} holds in ${byId.get(e.to)?.name}`}>{`${e.share_pct}%`}</Num> {e.share_type} held by{' '}
            <strong>{name(n, e.from)}</strong>
            <div className="small muted">
              {e.source} · as of {e.as_of_date} · source tier {e.source_tier} · confidence {e.confidence}
              {e.presumption && ` · ${e.presumption}`} ·{' '}
              <a href={e.source_url} target="_blank" rel="noopener noreferrer">source</a>
            </div>
            {n?.country === 'UNRESOLVED' && <div className="callout small">{SPECIAL_RECIPIENTS.UNRESOLVED}</div>}
            {loop ? <div className="small muted">(cross-holding: already shown above)</div> : <Chain o={o} id={e.from} seen={new Set([...seen, e.from])} />}
          </li>
        );
      })}
      {unpriced.map((e, i) => (
        <li key={`u${i}`}>
          <em>share not disclosed</em> ({e.share_type}) held by <strong>{name(byId.get(e.parent_entity_id), e.parent_entity_id)}</strong>
          <div className="small muted">
            {e.notes} · <a href={e.source_url} target="_blank" rel="noopener noreferrer">source</a>
          </div>
        </li>
      ))}
    </ul>
  );
}

export default async function Company({ params }: { params: Promise<{ company: string }> }) {
  const { company } = await params;
  const o = load();
  const f = o.firms.find((x) => x.entity_id === company);
  if (!f) notFound();
  const node = o.nodes.find((n) => n.id === f.entity_id);
  const uci = o.nodes.find((n) => n.id === f.uci_entity);
  const theta = o.theta_calibration.find((t) => t.entity_id === f.entity_id);
  const p = firmProv(f, o);
  const fin = [node, uci].filter((n): n is OwnNode => !!n && (n.revenue_eur_m != null || n.operating_profit_eur_m != null || n.employees != null));
  const finProv = (n: OwnNode) => ({ status: 'observed', confidence_level: n.confidence || 'n/a', source: `${n.source || 'Company document'} (source tier ${n.source_tier ?? 'n/a'})`, source_url: n.source_url, methodology: n.notes || 'As reported in the source; group-level figures may include operations outside Cyprus (see notes).' });
  return (
    <>
      <p className="small"><Link href="/country/cyprus/ownership/">← Ownership</Link></p>
      <h1>{f.legal_name}</h1>
      <p className="muted">
        Sector: {f.sector.replace(/_/g, ' ')}{f.nace_code != null && ` (NACE ${f.nace_code})`} · Overall confidence: {f.confidence}
      </p>
      <div className="kpis">
        <div className="kpi"><div className="k-label">Ultimate controlling country</div><div className="k-value">{f.uci_country === 'UNRESOLVED' ? 'UNRESOLVED' : recipientName(f.uci_country)}</div><div className="k-sub">{uci ? uci.name : f.uci_entity}</div></div>
        <div className="kpi"><div className="k-label">Look-through: ultimate owners resident in Cyprus</div><div className="k-value"><Num prov={p} title="Share of equity whose ultimate owners are documented Cypriot residents">{pct(f.domestic)}</Num></div></div>
        <div className="kpi"><div className="k-label">Look-through: ultimate owners abroad</div><div className="k-value"><Num prov={p} title="Share of equity whose ultimate owners are documented non-residents">{pct(f.foreign)}</Num></div></div>
        <div className="kpi"><div className="k-label">Look-through: unresolved</div><div className="k-value"><Num prov={p} title="Share where the records run out (for listed parents, their dispersed shareholders)">{pct(f.unresolved)}</Num></div><div className="k-sub">never assigned a guessed country</div></div>
      </div>
      <section className="card">
        <h2>How the chain ends</h2>
        <p>
          Status: <strong>{f.uci_status.replace(/_/g, ' ')}</strong>. {UCI_STATUS[f.uci_status]}
          {f.first_foreign_parent_country && f.first_foreign_parent_country !== f.uci_country && (
            <> The first foreign parent is in {recipientName(f.first_foreign_parent_country)}; majority control continues up the chain to {f.uci_country === 'UNRESOLVED' ? 'a unit whose country is not documented' : recipientName(f.uci_country)}.</>
          )}
        </p>
        {f.unpriced_parent_edges > 0 && <p className="callout">{f.unpriced_parent_edges} parent link(s) have no disclosed share.</p>}
        {theta && <p>Share of this firm&apos;s equity held by non-residents (traced to the first non-resident owner on every path), used to calibrate theta: <Num prov={p} title="theta for this firm">{theta.theta.toFixed(2)}</Num>.</p>}
        <p className="small muted">Look-through shares follow equity to its ultimate owners; where a parent is a listed company, its dispersed shareholders are unresolved. The ultimate controlling country follows majority control instead, so the two can differ.</p>
      </section>
      <section className="card">
        <h2>Ownership chain (from the firm up to its ultimate owners)</h2>
        <p className="explain">Each link shows the share held, the source document, its date and tier, and confidence.</p>
        <Chain o={o} id={f.entity_id} seen={new Set([f.entity_id])} />
      </section>
      {fin.length > 0 && (
        <section className="card">
          <h2>Financials (only where published)</h2>
          <div className="table-scroll">
            <table className="data">
              <thead><tr><th>Entity</th><th className="r">Revenue</th><th className="r">Operating profit (as reported)</th><th className="r">Employees</th><th>Fiscal year</th><th>Notes</th></tr></thead>
              <tbody>
                {fin.map((n) => (
                  <tr key={n.id}>
                    <td>{n.name}</td>
                    <td className="r">{n.revenue_eur_m != null ? <Num prov={finProv(n)}>{eurM(n.revenue_eur_m)}</Num> : '—'}</td>
                    <td className="r">{n.operating_profit_eur_m != null ? <Num prov={finProv(n)}>{eurM(n.operating_profit_eur_m)}</Num> : '—'}</td>
                    <td className="r">{n.employees != null ? <Num prov={finProv(n)}>{n.employees.toLocaleString('en-GB')}</Num> : '—'}</td>
                    <td>{n.fiscal_year ?? '—'}</td>
                    <td className="small">{n.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="small muted">Revenue is not value added; these figures do not enter the headline results.</p>
        </section>
      )}
      <section className="card">
        <h2>Sources</h2>
        <ul>
          {[...new Set([node?.source_url, ...splitUrls(p.source_url)].filter((u): u is string => !!u))].map((u) => (
            <li key={u}><a href={u} target="_blank" rel="noopener noreferrer" style={{ overflowWrap: 'anywhere' }}>{u}</a></li>
          ))}
        </ul>
        {node?.notes && <p className="small">{node.notes}</p>}
      </section>
    </>
  );
}
