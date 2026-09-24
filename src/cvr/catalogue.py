"""Build data_catalogue.csv (brief §19) from the per-source manifests.

Also writes data/raw/cbc/MANIFEST.csv for the Central Bank of Cyprus files,
which were fetched by URL (see CBC_FILES) rather than by an API client.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from .provenance import sha256

COLS = [
    "dataset",
    "provider",
    "URL",
    "reference_year",
    "publication_date",
    "download_date",
    "license",
    "geographic_scope",
    "industry_resolution",
    "variables",
    "processing_script",
    "checksum",
]
EUROSTAT_LICENSE = "Eurostat reuse policy (CC BY 4.0), Commission Decision 2011/833/EU"
CYSTAT_LICENSE = "CYSTAT terms of use - reuse terms NOT verified for this release; raw files are not redistributed (re-downloaded by make ingest)"
CBC_LICENSE = "Central Bank of Cyprus website terms - NOT verified for this release; raw files are not redistributed (re-downloaded by URL)"
CBC = Path("data/raw/cbc")
CBC_FILES = {
    "bop_annual.xls": (
        "Balance of payments, annual, BPM6 (2008-2025)",
        "https://www.centralbank.cy/images/media/xls/STTBG__BOP__2008-2025_ANNUAL__EN.xls",
    ),
    "QIIP_2008-2025_ANNUAL_EN.xlsx": (
        "International investment position, annual",
        "https://www.centralbank.cy/images/media/xls/QIIP_2008-2025_ANNUAL_EN.xlsx",
    ),
    "Annual_Transactions_Data_by_Country_EN0011.xlsx": (
        "FDI transactions by country",
        "https://www.centralbank.cy/images/media/xls/Annual_Transactions_Data_by_Country_EN0011.xlsx",
    ),
    "Annual_Transactions_Data_by_Economic_Activity_EN0007.xlsx": (
        "FDI transactions by economic activity",
        "https://www.centralbank.cy/images/media/xls/Annual_Transactions_Data_by_Economic_Activity_EN0007.xlsx",
    ),
    "Annual_Stock_Data_by_Country_EN0010.xlsx": (
        "FDI positions by country",
        "https://www.centralbank.cy/images/media/xls/Annual_Stock_Data_by_Country_EN0010.xlsx",
    ),
    "Annual_Stock_Data_by_Economic_Activity_EN0009.xlsx": (
        "FDI positions by economic activity",
        "https://www.centralbank.cy/images/media/xls/Annual_Stock_Data_by_Economic_Activity_EN0009.xlsx",
    ),
    "Annual_UIE_Stock_Data_by_Country_EN0002.xlsx": (
        "FDI positions by ultimate investing economy",
        "https://www.centralbank.cy/images/media/xls/Annual_UIE_Stock_Data_by_Country_EN0002.xlsx",
    ),
    "spe_def.pdf": (
        "Definition for the identification of SPEs",
        "https://www.centralbank.cy/images/media/redirectfile/External%20Statistics/External%20Statistics/Definition_of_SPEs_EN.pdf",
    ),
}


def cbc_manifest() -> pd.DataFrame:
    """Rewrite data/raw/cbc/MANIFEST.csv from the files present.

    A file whose checksum is unchanged keeps its recorded download date; a new or changed file
    gets today's date.  Rows for files not present locally (clean clone) are kept as they are.
    """
    path = CBC / "MANIFEST.csv"
    old = pd.read_csv(path) if path.exists() and path.stat().st_size > 0 else pd.DataFrame(columns=["file", "sha256", "download_date"])
    prev = old.set_index("file")
    rows = []
    for f, (title, url) in CBC_FILES.items():
        p = CBC / f
        if not p.exists():
            continue
        digest = sha256(p)
        same = str(p) in prev.index and prev.loc[str(p), "sha256"] == digest
        rows.append(
            {
                "file": str(p),
                "dataset": title,
                "provider": "Central Bank of Cyprus",
                "url": url,
                "download_date": prev.loc[str(p), "download_date"] if same else str(date.today()),
                "sha256": digest,
            }
        )
    df = pd.DataFrame(rows)
    df = pd.concat([df, old[~old["file"].isin(df.get("file", pd.Series(dtype=str)))]], ignore_index=True)
    df.to_csv(path, index=False)
    return df


def build() -> pd.DataFrame:
    rows = []
    cy = pd.read_csv("data/raw/cystat/MANIFEST.csv")
    for _, r in cy.iterrows():
        rows.append(
            {
                "dataset": f"{r.dataset}: {r.description}",
                "provider": "CYSTAT (Statistical Service of Cyprus)",
                "URL": r.url,
                "reference_year": r.reference_year,
                "publication_date": r.publication_date,
                "download_date": r.download_date,
                "license": CYSTAT_LICENSE,
                "geographic_scope": "Cyprus (government-controlled area)",
                "industry_resolution": "64 CPA/NACE (A*64 with CYSTAT merges)"
                if "0640" in str(r.file)
                else "A*64 / sectors",
                "variables": r.description,
                "processing_script": "src/cvr/ingest/cystat_fetch.py -> src/cvr/ingest/cystat.py",
                "checksum": r.sha256,
            }
        )
    es = pd.read_csv("data/raw/eurostat/MANIFEST.csv")
    for _, r in es.iterrows():
        rows.append(
            {
                "dataset": f"{r.dataset_code}: {r.dataset_title}",
                "provider": "Eurostat",
                "URL": r.url,
                "reference_year": "see filters",
                "publication_date": r.last_update,
                "download_date": r.download_date,
                "license": EUROSTAT_LICENSE,
                "geographic_scope": "Cyprus (reporter); partners as listed",
                "industry_resolution": "FIGARO 64"
                if "fcp" in r.dataset_code or "naio_10_fg" in r.dataset_code
                else ("A64" if "a64" in r.dataset_code else "NACE aggregates / none"),
                "variables": r.filters,
                "processing_script": "src/cvr/ingest/eurostat.py",
                "checksum": r.sha256,
            }
        )
    for _, r in cbc_manifest().iterrows():
        rows.append(
            {
                "dataset": r.dataset,
                "provider": r.provider,
                "URL": r.url,
                "reference_year": "2008-2025",
                "publication_date": "2026-04-02 (BoP last update)",
                "download_date": r.download_date,
                "license": CBC_LICENSE,
                "geographic_scope": "Cyprus",
                "industry_resolution": "NACE sections"
                if "activity" in r.dataset.lower()
                else "none",
                "variables": r.dataset,
                "processing_script": "src/cvr/ingest/cbc.py; used for the SPE definition and cross-checks",
                "checksum": r.sha256,
            }
        )
    rows.append(
        {
            "dataset": "Company ownership layer (entities.csv, ownership_edges.csv)",
            "provider": "Compiled from company filings (Tier 1-4, per row)",
            "URL": "data/raw/companies/SOURCES.md",
            "reference_year": "2024-2026",
            "publication_date": "various",
            "download_date": "2026-09-24",
            "license": "Facts compiled from public filings; CC BY 4.0 for the compilation",
            "geographic_scope": "Cyprus operating firms and their owners",
            "industry_resolution": "NACE 2-digit",
            "variables": "shares, parents, financials where printed",
            "processing_script": "src/cvr/model/ownership_data.py",
            "checksum": sha256("data/raw/companies/ownership_edges.csv"),
        }
    )
    df = pd.DataFrame(rows, columns=COLS)
    df.to_csv("data_catalogue.csv", index=False)
    return df


if __name__ == "__main__":
    print(len(build()), "catalogue rows")
