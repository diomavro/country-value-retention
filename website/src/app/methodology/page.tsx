import { marked } from 'marked';
import { readDoc } from '@/lib/server';

export const metadata = { title: 'Methodology' };

export default function Page() {
  const methodology = readDoc('methodology.md');
  const concepts = readDoc('concepts.md');
  const limitations = readDoc('limitations.md');
  const html = (md: string) => marked.parse(md, { async: false }) as string;
  return (
    <>
      <h1>Methodology</h1>
      <p className="lede">
        The concepts first, in plain language, then the technical methodology. Both are rendered from the project
        repository&apos;s <code>docs/</code> folder at build time.
      </p>
      {concepts && <article className="md card" dangerouslySetInnerHTML={{ __html: html(concepts) }} />}
      {methodology ? (
        <article className="md card" dangerouslySetInnerHTML={{ __html: html(methodology) }} />
      ) : (
        <p className="callout">The technical methodology document (docs/methodology.md) has not been published yet.</p>
      )}
      {limitations && <article className="md card" dangerouslySetInnerHTML={{ __html: html(limitations) }} />}
    </>
  );
}
