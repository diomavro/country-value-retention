import fs from 'node:fs';
import path from 'node:path';

const DATA = path.join(process.cwd(), 'public', 'data');

export function readData<T>(rel: string): T {
  return JSON.parse(fs.readFileSync(path.join(DATA, rel), 'utf8')) as T;
}

export function listDataFiles(): { name: string; bytes: number }[] {
  const out: { name: string; bytes: number }[] = [];
  const walk = (dir: string, pre: string) => {
    for (const f of fs.readdirSync(dir).sort()) {
      const p = path.join(dir, f);
      if (fs.statSync(p).isDirectory()) walk(p, `${pre}${f}/`);
      else if (f.endsWith('.json')) out.push({ name: `${pre}${f}`, bytes: fs.statSync(p).size });
    }
  };
  walk(DATA, '');
  return out;
}

/** Read a Markdown file from the repository's docs/ folder; null if it does not exist. */
export function readDoc(name: string): string | null {
  const p = path.join(process.cwd(), '..', 'docs', name);
  return fs.existsSync(p) ? fs.readFileSync(p, 'utf8') : null;
}
