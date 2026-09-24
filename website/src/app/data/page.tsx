import { readData, listDataFiles } from '@/lib/server';
import type { CatalogueRow, Headline, ReconRow, SensRow } from '@/lib/types';
import { dataUrl } from '@/lib/paths';
import { eurM, pct } from '@/lib/format';
import Sensitivity from '@/components/Sensitivity';
import { Num } from '@/components/Prov';

export const metadata = { title: 'Data' };

export default function Page() {
  const cat = readData<CatalogueRow[]>('catalogue.json');
  const rec = readData<ReconRow[]>('cy/reconciliation.json');
  const sens = readData<SensRow[]>('cy/sensitivity.json');
  const h = readData<Headline>('cy/headline.json');
  const files = listDataFiles();
  const recProv = (r: ReconRow) => ({ status: r.status, confidence_level: r.confidence_level, source: r.source, source_url: r.source_url, methodology: `${r.check}. ${r.explanation}` });
  return (
    <>
      <h1>Data</h1>
      <p className="lede">
        Every dataset used, where it came from, and checks that the model reproduces the official totals. All files the
        dashboard reads can be downloaded below.
      </p>

      <Sensitivity rows={sens} headlineTheta={h.series[h.series.length - 1].theta} />

      <section className="card">
        <h2>Reconciliation with official totals</h2>
        <p className="explain">The model is checked against published aggregates every year; differences reflect data vintages and rounding.</p>
        <div className="table-scroll tall">
          <table className="data">
            <thead>
              <tr><th>Year</th><th>Check</th><th className="r">Official</th><th className="r">Model</th><th className="r">Difference</th><th>Passes</th><th>Explanation</th></tr>
            </thead>
            <tbody>
              {rec.map((r, i) => (
                <tr key={i}>
                  <td>{r.year}</td>
                  <td>{r.check}</td>
                  <td className="r"><Num prov={recProv(r)}>{eurM(r.official)}</Num></td>
                  <td className="r"><Num prov={{ ...recProv(r), status: 'modelled' }}>{eurM(r.model)}</Num></td>
                  <td className="r">{pct(r.pct_difference, 3)}</td>
                  <td>{r.passes ? '✓ yes' : '✗ no'}</td>
                  <td className="small">{r.explanation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <h2>Download the data</h2>
        <p className="explain">JSON files exported by the project pipeline (<code>python -m cvr.export_web</code>). Values are EUR million unless stated.</p>
        <div className="table-scroll tall">
          <table className="data">
            <thead><tr><th>File</th><th className="r">Size</th></tr></thead>
            <tbody>
              {files.map((f) => (
                <tr key={f.name}>
                  <td><a href={dataUrl(f.name)} download>{f.name}</a>{f.name.includes('example_platform') && <> <span className="illustrative-tag">Illustrative</span></>}</td>
                  <td className="r">{(f.bytes / 1024).toFixed(0)} KB</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <h2>Data catalogue ({cat.length} datasets)</h2>
        <div className="table-scroll tall">
          <table className="data">
            <thead>
              <tr><th>Dataset</th><th>Provider</th><th>Reference years</th><th>Published</th><th>Downloaded</th><th>Licence</th><th>Processing</th></tr>
            </thead>
            <tbody>
              {cat.map((c, i) => (
                <tr key={i}>
                  <td style={{ minWidth: '16rem' }}>{/^https?:/.test(c.URL) ? <a href={c.URL} target="_blank" rel="noopener noreferrer">{c.dataset}</a> : c.dataset}</td>
                  <td>{c.provider}</td>
                  <td>{c.reference_year}</td>
                  <td>{c.publication_date}</td>
                  <td>{c.download_date}</td>
                  <td className="small" style={{ minWidth: '14rem' }}>{c.license}</td>
                  <td className="small"><code>{c.processing_script}</code></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
