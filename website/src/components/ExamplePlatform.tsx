import StackBar from './StackBar';
import type { Prov } from '@/lib/types';

interface Summary { fee_eur: number; year: number; stays_in_cyprus: number; foreign_capital_income_platform_owner: number; foreign_income_via_suppliers: number; imported_inputs: number; cyprus_labour_platform: number; cyprus_rent_real_estate: number; status: string }

export default function ExamplePlatform({ s }: { s: Summary }) {
  const prov: Prov = {
    status: 'illustrative',
    confidence_level: 'low (teaching example)',
    source: 'example_platform.json: industry-average cost structure + documented ownership chain',
    source_url: null,
    methodology: s.status,
  };
  const e = (v: number) => `€${v.toFixed(2)}`;
  return (
    <section className="card" style={{ borderStyle: 'dashed' }}>
      <h2>
        <span className="illustrative-tag">Illustrative</span> Worked example: a €{s.fee_eur} delivery-platform fee
      </h2>
      <p className="callout">
        ILLUSTRATIVE ONLY. This is a teaching example built from an industry-average cost structure and one documented
        ownership chain ({s.year}). It is not part of the headline results.
      </p>
      <p className="explain">
        When you pay a delivery platform €{s.fee_eur}, it is tempting to say &ldquo;€{s.fee_eur} left Cyprus&rdquo; if the
        platform is foreign. That is wrong: most of the fee pays for things other people produced.
      </p>
      <StackBar
        segs={[
          { key: 'cy', label: 'Stays in Cyprus', value: s.stays_in_cyprus, display: e(s.stays_in_cyprus), color: 'var(--retained)', prov, note: `Includes platform staff ${e(s.cyprus_labour_platform)} and rent ${e(s.cyprus_rent_real_estate)}.` },
          { key: 'own', label: 'Foreign owner of the platform', value: s.foreign_capital_income_platform_owner, display: e(s.foreign_capital_income_platform_owner), color: 'var(--s1)', prov },
          { key: 'sup', label: 'Foreign income via Cypriot suppliers', value: s.foreign_income_via_suppliers, display: e(s.foreign_income_via_suppliers), color: 'var(--s3)', prov },
          { key: 'imp', label: 'Imported inputs', value: s.imported_inputs, display: e(s.imported_inputs), color: 'var(--s2)', prov },
        ]}
      />
    </section>
  );
}
