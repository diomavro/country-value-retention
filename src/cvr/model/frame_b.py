"""Frame B: where a euro spent on Cypriot output ultimately accrues.

For final demand f of domestic product k, the Leontief model splits each euro
into domestic value added (in every industry along the supply chain),
imported inputs, and product taxes on inputs (they sum to exactly 1).  Domestic
value added is then routed through Frame A's industry recipient shares and
imported inputs to the economy that produced them (FIGARO, direct supplier).

Imported inputs are attributed to the *direct* supplier economy.  Part of that
value was itself produced in third countries (or even in Cyprus); FIGARO's
published value-added-origin indicators (naio_10_fgfd) are the cross-check.
"""

from __future__ import annotations

import glob
from functools import lru_cache

import numpy as np
import pyarrow.parquet as pq
import pandas as pd

from ..accounts import industry_recipient_shares, value_chain_recipients
from ..io_model import solve
from .industries import from_nama
from .suiot import build

FIGARO_ROW = "WRL_REST"  # FIGARO rest-of-world block


@lru_cache(maxsize=None)
def _figaro_dest() -> pd.DataFrame:
    """Only the five needed columns, strings as categoricals: the full slices are ~4M rows."""
    cols = ["ind_use", "ind_ava", "c_orig", "TIME_PERIOD", "OBS_VALUE"]
    fs = sorted(glob.glob("data/raw/eurostat/naio_10_fcp_ii*__c_dest-CY.parquet"))
    parts = []
    for f in fs:
        tbl = pq.read_table(f, columns=cols, read_dictionary=["ind_use", "ind_ava", "c_orig"], filters=[("c_orig", "!=", "CY")])
        d = tbl.to_pandas()
        d["TIME_PERIOD"] = d.TIME_PERIOD.astype("int16")
        parts.append(d)
    return pd.concat(parts, ignore_index=True)


def import_origin(year: int, labels: list[str]) -> pd.DataFrame:
    return _origin_for(year, tuple(labels))


@lru_cache(maxsize=None)
def _origin_for(year: int, labels: tuple) -> pd.DataFrame:
    return _build_origin(year, list(labels))


def _build_origin(year: int, labels: list[str]) -> pd.DataFrame:
    """product x origin-economy shares of Cyprus's imported intermediate inputs (rows sum to 1)."""
    d = _figaro_dest()
    d = d[(d.TIME_PERIOD == year) & (d.c_orig != "CY")]
    uses = set(d.ind_use) - {"P3_S13", "P3_S14", "P3_S15", "P51G", "P5M"}
    d = d[
        d.ind_use.isin(uses)
        & ~d.ind_ava.isin(["B2A3G", "D1", "D21X31", "D29X39", "OP_NRES", "OP_RES"])
    ]
    m = d.pivot_table(
        observed=True,
        index="ind_ava",
        columns="c_orig",
        values="OBS_VALUE",
        aggfunc="sum",
        fill_value=0.0,
    )
    m.index = [from_nama(c) for c in m.index]
    if (
        "L" in m.index
    ):  # FIGARO does not split real estate; both halves share its origin mix
        m.loc["L68A"] = m.loc["L"]
        m.loc["L68B"] = m.loc["L"]
        m = m.drop(index="L")
    canon = [lab.removeprefix("CPA_") for lab in labels]
    missing = set(canon) - set(m.index)
    if missing:
        raise KeyError(f"{year}: FIGARO lacks origin data for {sorted(missing)}")
    m = m.loc[canon]
    shares = m.div(m.sum(axis=1).replace(0, np.nan), axis=0)
    # products never imported as intermediates: any share row works (zero weight); use world mix
    world = m.sum(axis=0) / m.values.sum()
    shares = shares.apply(lambda r: world if r.isna().all() else r, axis=1)
    shares.index = labels
    return shares.rename(columns={FIGARO_ROW: "ROW_FIGARO"})


def per_euro(year: int, tensor: pd.DataFrame) -> pd.DataFrame:
    """For each product k: recipients of EUR 1 of final demand for Cypriot k."""
    table, _, _ = build(year)
    res = solve(table)
    shares = industry_recipient_shares(tensor)
    shares.index = ["CPA_" + k for k in shares.index]
    shares = shares.reindex(res.labels).fillna(0.0)
    zero = shares.sum(axis=1) == 0
    shares.loc[zero, "CY"] = (
        1.0  # industries with no GVA in Frame A: nothing to route abroad
    )
    origin = import_origin(year, res.labels)
    rows = []
    for i, lab in enumerate(res.labels):
        if table.x[i] <= 0:
            continue  # no domestic output of this product (e.g. U), nothing to decompose
        f = np.zeros(len(res.labels))
        f[i] = 1.0
        r = value_chain_recipients(res, f, shares, origin, "CY")
        r.insert(0, "product", lab.removeprefix("CPA_"))
        rows.append(r)
    out = pd.concat(rows, ignore_index=True)
    out.insert(0, "year", year)
    return out


def economy_final_demand(year: int, tensor: pd.DataFrame) -> pd.DataFrame:
    """Recipients of all final demand for domestic output in the year (EUR m)."""
    table, _, fd = build(year)
    res = solve(table)
    shares = industry_recipient_shares(tensor)
    shares.index = ["CPA_" + k for k in shares.index]
    shares = shares.reindex(res.labels).fillna(0.0)
    zero = shares.sum(axis=1) == 0
    shares.loc[zero, "CY"] = 1.0
    f = fd.sum(axis=1).reindex(res.labels).fillna(0.0).to_numpy()
    r = value_chain_recipients(res, f, shares, import_origin(year, res.labels), "CY")
    r.insert(0, "year", year)
    return r
