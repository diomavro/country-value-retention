"""Download CYSTAT PxWeb tables into data/raw/cystat and refresh MANIFEST.csv.

    python -m cvr.ingest.cystat_fetch

SUIOT tables are fetched once per measure (current prices `_CP`, previous-year
prices `_PYP`); national and sector accounts as one file with all measures.
The manifest row of every file is updated with today's download date and the
file's SHA-256, so provenance never outlives the data it describes.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

from ..provenance import sha256

OUT = Path(__file__).resolve().parents[3] / "data" / "raw" / "cystat"
BASE = "https://cystatdb.cystat.gov.cy/api/v1/en/8.CYSTAT-DB/National%20Accounts/"
TABLES = {
    "Supply, Use and Input-Output Tables": (
        [
            "0640010E",
            "0640015E",
            "0640020E",
            "0640025E",
            "0640030E",
            "0640035E",
            "0640040E",
            "0640045E",
            "0640050E",
            "0640055E",
        ],
        True,
    ),
    "Annual National Accounts": (
        ["0610010E", "0610020E", "0610030E", "0610040E", "0610060E"],
        False,
    ),
    "Sector Accounts": (["0630030E"], False),
}


def _req(url: str, data: bytes | None = None) -> bytes:
    headers = {"User-Agent": "Mozilla/5.0"}
    if data:
        headers["Content-Type"] = "application/json"
    for _ in range(6):
        try:
            time.sleep(1.5)
            return urllib.request.urlopen(
                urllib.request.Request(url, data=data, headers=headers), timeout=120
            ).read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(10)
                continue
            raise
    raise RuntimeError(f"CYSTAT kept rate-limiting {url}")


def fetch_table(
    folder: str, tid: str, split_measure: bool
) -> list[tuple[str, str, str]]:
    url = BASE + urllib.parse.quote(f"{folder}/{tid}.px")
    meta = json.loads(_req(url))
    (OUT / "pxweb_meta").mkdir(parents=True, exist_ok=True)
    (OUT / "pxweb_meta" / f"{tid}.json").write_text(json.dumps(meta, indent=1))
    written_meta = [(f"pxweb_meta/{tid}.json", url, f"PxWeb metadata {tid}")]
    variables = meta["variables"]
    measure = [v for v in variables if v["code"] == "MEASURE"]
    groups = (
        list(zip(measure[0]["values"], measure[0]["valueTexts"]))
        if (split_measure and measure)
        else [(None, None)]
    )
    written = []
    for code, text in groups:
        query = [
            {"code": v["code"], "selection": {"filter": "item", "values": [code]}}
            if (v["code"] == "MEASURE" and code is not None)
            else {"code": v["code"], "selection": {"filter": "all", "values": ["*"]}}
            for v in variables
        ]
        suffix = (
            ""
            if code is None
            else ("_CP" if text.lower().startswith("current") else "_PYP")
        )
        name = f"{tid}{suffix}.xlsx"
        (OUT / name).write_bytes(
            _req(
                url,
                json.dumps({"query": query, "response": {"format": "xlsx"}}).encode(),
            )
        )
        written.append((name, url, meta["title"]))
        print(name, (OUT / name).stat().st_size, meta["title"], text or "")
    return written + written_meta


def update_manifest(written: list[tuple[str, str, str]]) -> None:
    path = OUT / "MANIFEST.csv"
    man = (
        pd.read_csv(path)
        if path.exists()
        else pd.DataFrame(
            columns=[
                "file",
                "dataset",
                "provider",
                "url",
                "reference_year",
                "publication_date",
                "download_date",
                "sha256",
                "description",
                "format_notes",
            ]
        )
    )
    today = str(date.today())
    for name, url, title in written:
        hit = man["file"] == name
        if hit.any():
            # refresh only what a re-download changes; keep curated labels and periods
            man.loc[hit, ["url", "download_date", "sha256"]] = [url, today, sha256(OUT / name)]
        else:
            row = {"file": name, "dataset": f"CYSTAT {Path(name).stem.split('_')[0]}", "provider": "CYSTAT (Statistical Service of Cyprus)", "url": url, "download_date": today, "sha256": sha256(OUT / name), "description": title}
            man = pd.concat([man, pd.DataFrame([row])], ignore_index=True)
    man.to_csv(path, index=False)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for folder, (tables, split) in TABLES.items():
        for tid in tables:
            written += fetch_table(folder, tid, split)
    update_manifest(written)
    print(f"{len(written)} files -> {OUT}")


if __name__ == "__main__":
    main()
