'use client';
import { useState } from 'react';
import Link from 'next/link';
import type { Ownership } from '@/lib/types';
import { firmProv, UCI_STATUS } from '@/lib/ownership';
import { SPECIAL_RECIPIENTS } from '@/lib/concepts';
import { recipientName } from '@/lib/names';
import { pct } from '@/lib/format';
import OwnershipGraph from './OwnershipGraph';
import { Num } from './Prov';

export default function OwnershipView({ o }: { o: Ownership }) {
  const [focus, setFocus] = useState('');
  const firms = [...o.firms].sort((a, b) => a.legal_name.localeCompare(b.legal_name));
  const unresolvedN = o.firms.filter((f) => f.uci_country === 'UNRESOLVED').length;
  return (
    <>
      <h1>Who owns the large firms operating in Cyprus</h1>
      <p className="lede">
        Company ownership is often layered: a Cypriot subsidiary is owned by a holding company abroad, which is owned
        by a parent, which is owned by many shareholders. Stopping at the first foreign company would name the wrong
        country, so the chain is followed to the end. Where the records run out, the remaining share is labelled{' '}
        <strong>unresolved</strong>, never assigned a guessed country.
      </p>
      <p className="callout">
        {o.note} Ownership moves only the owners&apos; share, and only operating surplus: wages of Cypriot staff and
        taxes paid in Cyprus stay. For {unresolvedN} of {o.firms.length} firms the ultimate owner&apos;s country is UNRESOLVED.
      </p>
      <section className="card">
        <h2>Ownership network</h2>
        <div className="controls">
          <label>
            Firm
            <select value={focus} onChange={(e) => setFocus(e.target.value)}>
              <option value="">All firms ({o.firms.length})</option>
              {firms.map((f) => (
                <option key={f.entity_id} value={f.entity_id}>{f.legal_name}</option>
              ))}
            </select>
          </label>
          {focus && <Link href={`/company/${focus}/`}>Open company page →</Link>}
        </div>
        <OwnershipGraph o={o} focus={focus} />
      </section>
      <section className="card">
        <h2>Firms and their ultimate controlling country</h2>
        <p className="explain">
          Domestic / foreign / unresolved: the share of each firm&apos;s ownership that ends with Cypriot residents,
          with non-residents, or where the records run out. {SPECIAL_RECIPIENTS.UNRESOLVED}
        </p>
        <div className="table-scroll tall">
          <table className="data">
            <thead>
              <tr>
                <th>Firm</th>
                <th>Sector</th>
                <th>Ultimate controlling country</th>
                <th>Status</th>
                <th className="r">Domestic</th>
                <th className="r">Foreign</th>
                <th className="r">Unresolved</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {firms.map((f) => {
                const p = firmProv(f, o);
                return (
                  <tr key={f.entity_id}>
                    <td><Link href={`/company/${f.entity_id}/`}>{f.legal_name}</Link></td>
                    <td>{f.sector.replace(/_/g, ' ')}</td>
                    <td>{f.uci_country === 'UNRESOLVED' ? <strong>UNRESOLVED</strong> : recipientName(f.uci_country)}</td>
                    <td className="small" title={UCI_STATUS[f.uci_status]}>{f.uci_status.replace(/_/g, ' ')}</td>
                    <td className="r"><Num prov={p} title={`${f.legal_name}: domestic share`}>{pct(f.domestic)}</Num></td>
                    <td className="r"><Num prov={p} title={`${f.legal_name}: foreign share`}>{pct(f.foreign)}</Num></td>
                    <td className="r"><Num prov={p} title={`${f.legal_name}: unresolved share`}>{pct(f.unresolved)}</Num></td>
                    <td>{f.confidence}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
      <section className="card">
        <h2>Calibrating theta: the non-resident share of equity</h2>
        <p className="explain">
          The company layer calibrates theta, the share of a foreign-controlled firm&apos;s equity held by non-residents
          (traced through Cypriot holding companies to the first non-resident owner). Firms of the same group count once;
          the headline uses the mean over groups. The Data page shows results for theta from 0.6 to 1.0.
        </p>
        <div className="table-scroll">
          <table className="data">
            <thead><tr><th>Firm</th><th>Group (largest parent)</th><th className="r">theta</th></tr></thead>
            <tbody>
              {o.theta_calibration.map((t) => (
                <tr key={t.entity_id}>
                  <td><Link href={`/company/${t.entity_id}/`}>{o.firms.find((f) => f.entity_id === t.entity_id)?.legal_name || t.entity_id}</Link></td>
                  <td>{o.nodes.find((n) => n.id === t.group)?.name || t.group}</td>
                  <td className="r">
                    {(() => { const f = o.firms.find((x) => x.entity_id === t.entity_id); return f ? <Num prov={firmProv(f, o)} title="theta from the documented chain">{t.theta.toFixed(2)}</Num> : t.theta.toFixed(2); })()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
