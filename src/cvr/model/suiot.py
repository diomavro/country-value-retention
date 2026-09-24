"""Build IOTable objects from CYSTAT's symmetric product-by-product tables.

Domestic block Zd  <- 0640050E (use of domestic output) product rows
Imported block Zm  <- 0640055E (use of imports) product rows
t, v, x            <- 0640050E rows D21X31, B1G, P1
The imported block's column totals must equal the IMP row of 0640050E; the
builder checks this so the domestic/imported split is never double counted.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from ..io_model import AccountingIdentityError, IOTable

SUIOT = Path("data/interim/cystat/suiot_cp.parquet")
FINAL_DEMAND = ["P3-S14", "P3-S15", "P3-S13", "P51G", "P5M", "P6"]
VA_ROWS = [
    "D1",
    "D11",
    "D29X39",
    "P51C",
    "B2A3N",
    "B2A3G",
    "B1G",
    "P1",
    "D21X31",
    "IMP",
]


@lru_cache(maxsize=1)
def _suiot() -> pd.DataFrame:
    # model needs only the cell coordinates; provenance strings stay in the parquet file
    cols = ["table_id", "reference_year", "row_code", "col_code", "value", "flag"]
    d = pd.read_parquet(SUIOT, columns=cols)
    for c in ("table_id", "row_code", "col_code", "flag"):
        d[c] = d[c].astype("category")
    return d


def _block(table: str, year: int) -> pd.DataFrame:
    d = _suiot()
    d = d[(d.table_id == table) & (d.reference_year == year)]
    if d.flag.eq("confidential").any():
        raise AccountingIdentityError(
            f"{table} {year} has confidential cells; use the SIOT"
        )
    return d.pivot(index="row_code", columns="col_code", values="value")


def products(year: int) -> list[str]:
    b = _block("0640050E", year)
    return [c for c in b.columns if c.startswith("CPA_")]


def build(
    year: int, rel_tol: float = 2e-3
) -> tuple[IOTable, pd.DataFrame, pd.DataFrame]:
    """Return (IOTable, value-added rows by product, final demand for domestic output)."""
    dom = _block("0640050E", year)
    imp = _block("0640055E", year)
    labels = products(year)
    Zd = dom.loc[labels, labels].to_numpy(float)
    Zm = imp.loc[labels, labels].to_numpy(float)
    imp_row = dom.loc["IMP", labels].to_numpy(float)
    gap = Zm.sum(0) - imp_row
    if np.abs(gap).max() > 0.05:
        raise AccountingIdentityError(
            f"{year}: imports block != IMP row (max gap {np.abs(gap).max():.3f})"
        )
    t = dom.loc["D21X31", labels].to_numpy(float)
    v = dom.loc["B1G", labels].to_numpy(float)
    x = dom.loc["P1", labels].to_numpy(float)
    # Published rounding (0.001 EUR m per cell) leaves column gaps ~1e-2; absorb them in
    # a documented residual only if they are within tolerance, never silently.
    resid = x - (Zd.sum(0) + Zm.sum(0) + t + v)
    if np.any(np.abs(resid) > rel_tol * np.maximum(x, 1.0)):
        raise AccountingIdentityError(
            f"{year}: SIOT column identity fails beyond rounding"
        )
    table = IOTable(labels, Zd, Zm, t, v + resid, x)
    va = dom.loc[[r for r in VA_ROWS if r in dom.index], labels].T
    va["rounding_residual"] = resid
    fd = dom.loc[labels, [c for c in FINAL_DEMAND if c in dom.columns]]
    return table, va, fd


def available_years() -> list[int]:
    return sorted(_suiot().reference_year.unique().tolist())


def product_taxes_total(year: int) -> float:
    """D21X31 on all uses (intermediate + final), i.e. the GDP-GVA wedge."""
    return float(_block("0640050E", year).loc["D21X31", "TU"])
