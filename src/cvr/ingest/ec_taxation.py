"""European Commission (DG TAXUD) effective average tax rates (Devereux/Griffith method; sheet source: KPMG) -> data/raw/ec_taxation.

    python -m cvr.ingest.ec_taxation

Forward-looking EATR for a hypothetical domestic investment of a non-financial firm, 2012-2024.
Used only as a sensitivity variant for tau (the central estimate keeps the statutory rate).
"""

from __future__ import annotations

import csv
import datetime as dt
import sys
import urllib.request
from pathlib import Path

import pandas as pd

from ..provenance import sha256

RAW = Path("data/raw/ec_taxation")
URL = "https://taxation-customs.ec.europa.eu/document/download/3f815f4c-5bc1-4eac-9a5a-83310b75dc72_en"
PAGE = "https://taxation-customs.ec.europa.eu/taxation/economic-analysis/data-taxation-trends_en"
UA = {
    "User-Agent": "country-value-retention/0.1 (+https://github.com/diomavro/country-value-retention)"
}


def eatr() -> pd.Series:
    """EATR (share, not %) indexed by (country name, year)."""
    d = pd.read_excel(RAW / "effective_tax_rates.xlsx", "EATR", header=None)
    years = [int(v) for v in d.iloc[2, 1:] if isinstance(v, (int, float)) and v == v]
    body = (
        d.iloc[3:, : len(years) + 1]
        .set_axis(["country"] + years, axis=1)
        .dropna(subset=["country"])
    )
    body = body[body.country.astype(str).str.strip().ne("")]
    s = body.melt(id_vars="country", var_name="year", value_name="eatr").dropna()
    s = s[pd.to_numeric(s.eatr, errors="coerce").notna()]
    return (
        s.assign(eatr=s.eatr.astype(float) / 100, country=s.country.str.strip())
        .set_index(["country", "year"])
        .eatr
    )


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    out = RAW / "effective_tax_rates.xlsx"
    with urllib.request.urlopen(
        urllib.request.Request(URL, headers=UA), timeout=120
    ) as r:
        out.write_bytes(r.read())
    n = len(eatr())
    if n == 0:
        print("FAIL: no EATR rows parsed", file=sys.stderr)
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
                "effective_tax_rates",
                "Effective average tax rates, non-financial sector (Taxation Trends)",
                "European Commission DG TAXUD",
                f"{URL} | {PAGE}",
                dt.date.today().isoformat(),
                sha256(out),
                n,
            ]
        )
    print(f"OK   {out} ({n} country-years)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
