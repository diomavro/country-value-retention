"""Provenance contract for every row of the processed database.

Every processed table carries these columns; ``require`` fails the build if any
are missing or blank.  ``status`` separates what an official source printed
from what this project computed, so no assumption can pass as an observation.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

PROVENANCE_COLUMNS = [
    "source",
    "source_url",
    "reference_year",
    "retrieval_date",
    "methodology",
    "confidence_level",
    "status",
]

STATUS = {
    "observed",  # printed by a Tier-1/2 source, only unit/label transformations applied
    "modelled",  # deterministic computation from observed inputs (e.g. Leontief propagation)
    "estimated",  # requires an allocation key or assumption documented in `methodology`
    "illustrative",  # worked example only; never enters headline results
}
CONFIDENCE = {"high", "medium", "low"}


class ProvenanceError(ValueError):
    pass


def require(df: pd.DataFrame, name: str) -> pd.DataFrame:
    missing = [c for c in PROVENANCE_COLUMNS if c not in df.columns]
    if missing:
        raise ProvenanceError(f"{name}: missing provenance columns {missing}")
    blank = df[PROVENANCE_COLUMNS].isna() | (
        df[PROVENANCE_COLUMNS].astype(str).apply(lambda s: s.str.strip()) == ""
    )
    if blank.any().any():
        cols = blank.any()[lambda s: s].index.tolist()
        raise ProvenanceError(f"{name}: blank provenance in {cols}")
    bad_status = set(df["status"]) - STATUS
    if bad_status:
        raise ProvenanceError(f"{name}: unknown status {bad_status}")
    bad_conf = set(df["confidence_level"]) - CONFIDENCE
    if bad_conf:
        raise ProvenanceError(f"{name}: unknown confidence {bad_conf}")
    return df


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def retrieval_date(file_name: str | None = None) -> str:
    """Download date of a raw file from its manifest; with no name, the latest date of any input.

    Dates are never hard-coded: a re-download rewrites the manifest and every date follows.
    """
    rows = []
    for man in Path("data/raw").glob("*/MANIFEST.csv"):
        m = pd.read_csv(man)
        if "download_date" in m:
            rows.append(m[["file", "download_date"]])
    if not rows:
        raise ProvenanceError("no manifests found under data/raw")
    allm = pd.concat(rows, ignore_index=True).dropna()
    if file_name is None:
        return str(allm["download_date"].max())
    hit = allm[allm["file"].astype(str).str.endswith(file_name)]
    if hit.empty:
        raise ProvenanceError(f"{file_name} is not in any manifest")
    return str(hit["download_date"].iloc[0])
