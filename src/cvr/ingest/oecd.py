"""OECD combined statutory corporate income tax rates (Corporate Tax Statistics) -> data/raw/oecd.

    python -m cvr.ingest.oecd

Used as the tax parameter tau for the comparison countries (Cyprus is not an OECD
member; its rates come from the Income Tax Law, see model.frame_a.STATUTORY_CIT).
"""

from __future__ import annotations

import csv
import datetime as dt
import sys
import urllib.request
from pathlib import Path

from ..provenance import sha256

RAW = Path("data/raw/oecd")
URL = (
    "https://sdmx.oecd.org/public/rest/data/OECD.CTP.TPS,DSD_TAX_CIT@DF_CIT,/"
    "IRL+LUX+NLD+GRC+PRT+MLT........?startPeriod=2010&format=csvfilewithlabels"
)


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / "cit_rates.csv"
    with urllib.request.urlopen(
        urllib.request.Request(URL, headers={"User-Agent": "country-value-retention/0.1 (+https://github.com/diomavro/country-value-retention)"}), timeout=120
    ) as r:
        out.write_bytes(r.read())
    rows = sum(1 for _ in open(out)) - 1
    if rows <= 0:
        print("FAIL: OECD returned no rows", file=sys.stderr)
        return 1
    with open(RAW / "MANIFEST.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "file",
                "dataset_code",
                "dataset_title",
                "provider",
                "url",
                "download_date",
                "sha256",
                "rows",
            ]
        )
        w.writerow(
            [
                str(out),
                "DSD_TAX_CIT@DF_CIT",
                "Corporate income tax (CIT) - statutory and targeted small business rates",
                "OECD",
                URL,
                dt.date.today().isoformat(),
                sha256(out),
                rows,
            ]
        )
    print(f"OK   {out} ({rows} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
