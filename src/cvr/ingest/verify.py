"""Check raw files against their manifest checksums before any processing.

    python -m cvr.ingest.verify          # exit 1 on a missing file or a checksum mismatch

A mismatch means the provider published a new vintage since the manifest was
written: the published numbers would change silently.  Re-run the downloader
(which rewrites the manifest) deliberately, then rebuild.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

from ..provenance import sha256

RAW = Path("data/raw")


def is_model_input(p: Path) -> bool:
    """Only files the model reads must exist; reference downloads may be absent in a clone."""
    if p.parent.name == "cystat":
        return re.fullmatch(r"06\d{5}E(_CP|_PYP)?\.xlsx", p.name) is not None
    if p.parts[:3] in {("data", "raw", "eurostat_eu"), ("data", "raw", "oecd")}:
        return True  # comparison countries (cvr.compare)
    return p.parts[:3] == ("data", "raw", "eurostat") and "figaro" not in p.parts


def main() -> int:
    changed, missing, optional, ok = [], [], [], 0
    for sub in ("cystat", "eurostat", "cbc", "eurostat_eu", "oecd"):
        man = RAW / sub / "MANIFEST.csv"
        if not man.exists():
            missing.append(str(man))
            continue
        for _, r in pd.read_csv(man).iterrows():
            p = Path(r["file"])
            p = p if p.parts[:2] == ("data", "raw") else RAW / sub / p
            if not p.exists():
                (missing if is_model_input(p) else optional).append(str(p))
            elif sha256(p) != r["sha256"]:
                changed.append(str(p))
            else:
                ok += 1
    for m in missing:
        print("MISSING ", m)
    for c in changed:
        print("CHANGED ", c)
    print(f"{ok} files match their manifest; {len(changed)} changed; {len(missing)} missing model inputs; {len(optional)} optional reference files absent")
    return 1 if (changed or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
