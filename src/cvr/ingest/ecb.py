"""ECB consolidated banking data (CBD2): profit of banks in Cyprus, domestic vs all -> data/raw/ecb.

    python -m cvr.ingest.ecb

Used to reconcile the two official measures of foreign-owned bank profit (limitation 12):
foreign-controlled subsidiaries and branches = all banks (sector 67) - domestic banking groups (11).
"""

from __future__ import annotations

import csv
import datetime as dt
import sys
import urllib.request
from pathlib import Path

import pandas as pd

from ..provenance import sha256

RAW = Path("data/raw/ecb")
UA = {
    "User-Agent": "country-value-retention/0.1 (+https://github.com/diomavro/country-value-retention)"
}
# profit or (-) loss for the year, all accounting frameworks, EUR thousands
SERIES = {
    "domestic": "A.CY.W0.11._Z._Z.A.A.P0000._X.ALL.CP._Z.T._T.EUR",
    "all": "A.CY.W0.67._Z._Z.A.A.P0000._X.ALL.CP._Z.T._T.EUR",
}
BASE = "https://data-api.ecb.europa.eu/service/data/CBD2/"


def bank_profit() -> pd.DataFrame:
    """Profit for the year of banks in Cyprus (EUR m): domestic, all, foreign-controlled."""
    d = pd.read_csv(RAW / "cbd2_bank_profit.csv")
    p = (
        d.pivot_table(index="TIME_PERIOD", columns="group", values="OBS_VALUE")
        * 10.0**-3
    )  # UNIT_MULT 3
    p["foreign_controlled"] = p["all"] - p["domestic"]
    return p


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    frames, urls = [], []
    for group, key in SERIES.items():
        url = f"{BASE}{key}?format=csvdata"
        with urllib.request.urlopen(
            urllib.request.Request(url, headers=UA), timeout=120
        ) as r:
            d = pd.read_csv(r)
        if d.empty or not (d.UNIT_MULT == 3).all():
            print(f"FAIL: unexpected CBD2 response for {key}", file=sys.stderr)
            return 1
        frames.append(
            d[["KEY", "TIME_PERIOD", "OBS_VALUE", "UNIT_MULT", "TITLE"]].assign(
                group=group
            )
        )
        urls.append(url)
    out = RAW / "cbd2_bank_profit.csv"
    pd.concat(frames, ignore_index=True).to_csv(out, index=False)
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
                "CBD2",
                "Consolidated banking data: profit or loss for the year, banks in Cyprus",
                "European Central Bank",
                " | ".join(urls),
                dt.date.today().isoformat(),
                sha256(out),
                sum(len(x) for x in frames),
            ]
        )
    print(f"OK   {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
