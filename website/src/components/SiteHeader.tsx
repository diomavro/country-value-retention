'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

const NAV = [
  ['/', 'Overview'],
  ['/country/cyprus/', 'Cyprus'],
  ['/country/cyprus/industries/', 'Industries'],
  ['/country/cyprus/flows/', 'Flows'],
  ['/country/cyprus/ownership/', 'Ownership'],
  ['/compare/', 'Compare'],
  ['/methodology/', 'Methodology'],
  ['/data/', 'Data'],
] as const;

export default function SiteHeader() {
  const path = usePathname() || '/';
  const norm = (p: string) => (p.endsWith('/') ? p : `${p}/`);
  const [theme, setTheme] = useState<string | null>(null);
  useEffect(() => {
    try {
      const t = localStorage.getItem('theme');
      if (t) {
        document.documentElement.dataset.theme = t;
        setTheme(t);
      }
    } catch {}
  }, []);
  const toggle = () => {
    const cur =
      theme ?? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    setTheme(next);
    try {
      localStorage.setItem('theme', next);
    } catch {}
  };
  return (
    <header className="site">
      <div className="wrap">
        <Link href="/" className="brand">
          Country Value Retention
        </Link>
        <nav className="main" aria-label="Main">
          {NAV.map(([href, label]) => {
            const active = href === '/' ? norm(path) === '/' : norm(path) === href;
            return (
              <Link key={href} href={href} className={active ? 'active' : ''} aria-current={active ? 'page' : undefined}>
                {label}
              </Link>
            );
          })}
        </nav>
        <button className="theme-btn" onClick={toggle} aria-label="Toggle light or dark theme">
          {theme === 'dark' ? 'Light' : theme === 'light' ? 'Dark' : 'Theme'}
        </button>
      </div>
    </header>
  );
}
