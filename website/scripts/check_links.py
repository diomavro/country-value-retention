"""Check the static export: every internal href/src and every data file the pages
reference must exist in website/out.  Exit 1 on any broken link.

    python website/scripts/check_links.py [--base /country-value-retention]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

OUT = Path(__file__).resolve().parents[1] / "out"
ATTR = re.compile(r'(?:href|src)="([^"#?]+)')
DATA = re.compile(r"data/(cy/[\w./-]+\.json|catalogue\.json|names\.json)")


def resolve(path: str, base: str) -> Path | None:
    if not path.startswith(base + "/") and path != base:
        return None  # external or not under the site
    rel = unquote(path[len(base) :]).lstrip("/")
    target = OUT / rel
    if target.is_dir() or rel.endswith("/") or rel == "":
        target = target / "index.html"
    return target


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="")
    base = ap.parse_args().base.rstrip("/")
    pages = sorted(OUT.rglob("*.html"))
    broken, checked = [], 0
    for page in pages:
        text = page.read_text(errors="ignore")
        for url in set(ATTR.findall(text)):
            if urlparse(url).scheme or url.startswith("//") or not url.startswith("/"):
                continue
            target = resolve(url, base)
            if target is None:
                broken.append((page.relative_to(OUT), url, "outside base path"))
                continue
            checked += 1
            if not target.exists():
                broken.append((page.relative_to(OUT), url, "missing"))
        for rel in set(DATA.findall(text)):
            checked += 1
            if not (OUT / "data" / rel).exists():
                broken.append(
                    (page.relative_to(OUT), f"data/{rel}", "missing data file")
                )
    for b in broken[:50]:
        print("BROKEN", *b)
    print(f"{len(pages)} pages, {checked} internal references, {len(broken)} broken")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
