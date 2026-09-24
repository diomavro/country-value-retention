"""Reconcile model aggregates against official national accounts (brief §9).

Every row: check, year, official, model, difference, pct_difference, tolerance,
passes, explanation.  Residuals are reported, never forced to zero.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .model.suiot import available_years, build, product_taxes_total

INTERIM = Path("data/interim/cystat")


def _sector() -> pd.DataFrame:
    s = pd.read_parquet(INTERIM / "sector_accounts.parquet")
    return s.pivot_table(
        index=["reference_year", "sector"], columns="item", values="value"
    )


def _gdp_gni() -> pd.DataFrame:
    g = pd.read_parquet(INTERIM / "gdp_gni.parquet")
    keep = {
        "B1GQ Gross Domestic Product at current prices (Million Euro)": "GDP",
        "B5G Gross National Income at current prices (Million Euro)": "GNI",
    }
    g = g[g.item_label.isin(keep)]
    return g.assign(item=g.item_label.map(keep)).pivot(
        index="reference_year", columns="item", values="value"
    )


def _row(check, year, official, model, tol, explanation):
    diff = model - official
    return {
        "check": check,
        "year": year,
        "official": official,
        "model": model,
        "difference": diff,
        "pct_difference": 100 * diff / official if official else float("nan"),
        "tolerance_pct": 100 * tol,
        "passes": abs(diff) <= tol * abs(official),
        "explanation": explanation,
    }


def reconcile(tensor_totals: dict[int, float] | None = None) -> pd.DataFrame:
    na = _gdp_gni()
    sec = _sector()
    rows = []
    for y in available_years():
        table, va, _ = build(y)
        gdp_model = table.v.sum() + product_taxes_total(y)
        rows.append(
            _row(
                "GDP = sum of GVA + taxes less subsidies on products",
                y,
                na.loc[y, "GDP"],
                gdp_model,
                0.005,
                "SUIOT (Mar-2026 vintage) vs annual NA (Apr-2026 vintage); differences reflect vintage/rounding",
            )
        )
        rows.append(
            _row(
                "Compensation of employees (SIOT vs sector accounts S1 D1 paid)",
                y,
                sec.loc[(y, "S1"), "D1PAY"],
                va["D1"].sum(),
                0.005,
                "Resident employers' D1 in sector accounts vs SIOT D1 row",
            )
        )
    for y in sorted(set(na.index) & set(sec.index.get_level_values(0))):
        s2 = sec.loc[(y, "S2")]
        gni_model = (
            sec.loc[(y, "S1"), "B1GQ"]
            + (s2["D1PAY"] - s2["D1REC"])
            + (s2["D4PAY"] - s2["D4REC"])
            - (0 if pd.isna(s2["D2REC"]) else s2["D2REC"])
            + (0 if pd.isna(s2["D3PAY"]) else s2["D3PAY"])
        )
        rows.append(
            _row(
                "GNI = GDP + primary income received - primary income paid (rest of world)",
                y,
                na.loc[y, "GNI"],
                gni_model,
                0.001,
                "S2 rows: REC = paid by Cyprus, PAY = received by Cyprus; D2 to / D3 from EU institutions",
            )
        )
    for y, total in (tensor_totals or {}).items():
        rows.append(
            _row(
                "Recipient tensor sums to GDP",
                y,
                na.loc[y, "GDP"],
                total,
                0.005,
                "sum over recipients and industries of V[CY, j, k, t]",
            )
        )
    return pd.DataFrame(rows)


if __name__ == "__main__":
    r = reconcile()
    print(r.groupby("check")[["pct_difference"]].agg(["min", "max"]).round(3))
    print("all pass:", bool(r.passes.all()))
