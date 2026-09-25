"""Frame A for comparison countries, read from Eurostat with the Cyprus method unchanged.

    python -m cvr.compare        # -> data/processed/comparison.parquet, comparison_skipped.parquet

Inputs: `python -m cvr.ingest.eurostat --geo IE,LU,NL,EL,PT,MT --raw-dir data/raw/eurostat_eu
--only gva_a64,sector_nf,bop_pi_sector,bop_rem,fats_activ,fats_g1a_08 --no-eu-aggregate` and
`python -m cvr.ingest.oecd` (statutory corporate tax rates).

theta (the non-resident share of foreign-controlled firms' equity) is calibrated from Cypriot
ownership filings only.  Other countries are shown at theta = the Cyprus value (an assumption,
labelled as such) and at theta = 1 (all foreign-controlled profit owned abroad: lowest retention).
A country-year whose inputs are suppressed is skipped with the reason, never filled in.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .model import frame_a as fa

OUT = Path("data/processed")
COUNTRIES = ["CY", "MT", "IE", "LU", "NL", "EL", "PT"]
YEARS = list(range(2010, 2024))


BOP_ITEMS = {
    "D41__O__FLA": "loan and deposit interest",
    "D41__P__F3": "interest on debt securities",
    "D42__P__F51": "portfolio dividends",
    "D44P__O__F6": "policyholder income",
    "D41__D__FLA": "intra-group interest",
    "D4S__D__F5": "foreign-owned banks' profit",
}
BOP_SECTORS = {"S1V": "firms and households", "S122": "banks", "S13": "government"}


def incomplete_mechanisms(items) -> str:
    """Mechanisms whose value is incomplete because a suppressed BoP item feeds them."""
    out = set()
    for key in items:
        sector, item, *_ = key.split()
        if sector == "S13":
            out.add("public_debt_interest")
        elif item == "D41__D__FLA":
            out.add("fdi_debt_interest")
        elif item == "D4S__D__F5":
            out.add("fdi_income")
        elif item in ("D41__P__F3", "D42__P__F51"):
            out.add("portfolio_income" if sector == "S1V" else "other_investment_income")  # banks' lines are netted into one
        else:
            out.add("other_investment_income")
    return ",".join(sorted(out))


def missing_lines(items) -> str:
    """Suppressed balance-of-payments items in plain words, e.g. 'loan and deposit interest (government)'.
    Items paid are omitted (retention overstated); bank receipts not netted (retention understated)."""
    out = []
    for key in items:
        sector, item, *flow = key.split()
        text = f"{BOP_ITEMS.get(item, item)} ({BOP_SECTORS.get(sector, sector)}{', received' if flow == ['received'] else ''})"
        if text not in out:
            out.append(text)
    return "; ".join(out)


def run(countries=COUNTRIES, years=YEARS) -> tuple[pd.DataFrame, pd.DataFrame]:
    theta_cy = fa.calibrated_theta()
    rows, skipped = [], []
    for geo in countries:
        with fa.country(geo):
            for year in years:
                for variant, theta in (("theta_cyprus", theta_cy), ("theta_1", 1.0)):
                    try:
                        acc, d = fa.build_account(year, fa.Params(theta=theta))
                    except fa.SuppressedInput as e:  # a missing download must fail loudly, not look like suppression
                        skipped.append({"geo": geo, "year": year, "reason": str(e.args[0]).split(": ", 1)[-1]})
                        break
                    by = acc.outflows.groupby("mechanism")["value"].sum()
                    rows.append(
                        {
                            "geo": geo,
                            "year": year,
                            "variant": variant,
                            "theta": theta,
                            "theta_status": "calibrated"
                            if geo == "CY" and variant == "theta_cyprus"
                            else "assumed",
                            "tau": d["tau"],
                            "gdp": acc.gdp,
                            "foreign_value_leakage": by.sum() / acc.gdp,
                            "domestic_value_retention": 1 - by.sum() / acc.gdp,
                            **{f"share_{m}": v / acc.gdp for m, v in by.items()},
                            "primary_income_outflow_to_gdp": d[
                                "official_primary_income_paid"
                            ]
                            / acc.gdp,
                            "fats_scope": d["fats_scope"],
                            "collapsed_sections": ",".join(d["collapsed_sections"]),
                            # suppressed BoP items are omitted (paid) or not netted (bank receipts)
                            "confidential_bop_items": ";".join(d["confidential_items"]),
                            "missing_lines": missing_lines(d["confidential_items"]),
                            "incomplete_mechanisms": incomplete_mechanisms(d["confidential_items"]),
                            "capped_industries": ",".join(d["capped"]),
                            "finance_level_factor": d["finance_level_factor"],  # FATS finance brought to the NA level
                        }
                    )
    res = pd.DataFrame(rows).fillna(
        {c: 0.0 for c in pd.DataFrame(rows).columns if c.startswith("share_")}
    )
    return res, pd.DataFrame(skipped)


def with_provenance(res: pd.DataFrame, skipped: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    from .pipeline import _provenance

    eu = "Eurostat nasa_10_nf_tr, nama_10_a64, fats_activ, fats_g1a_08, bop_c6_a, bop_rem6; OECD corporate tax statistics"
    res = res.assign(
        source=[("CYSTAT sector accounts; " if g == "CY" else "") + eu for g in res.geo],
        methodology="Frame A with the Cyprus method (src/cvr/compare.py, docs/methodology.md section 9); theta "
        + res.theta_status + "; suppressed BoP lines omitted: " + res.missing_lines.replace("", "none"),
        confidence_level="low",
        status="estimated",
    )
    skipped = skipped.assign(
        source="Eurostat nama_10_a64, fats_activ, fats_g1a_08",
        methodology="country-year not estimated: an input the estimator needs is suppressed by the statistical office",
        confidence_level="high",
        status="observed",
    )
    return _provenance(res), _provenance(skipped)


def main() -> int:
    res, skipped = with_provenance(*run())
    OUT.mkdir(parents=True, exist_ok=True)
    res.to_parquet(OUT / "comparison.parquet", index=False)
    skipped.to_parquet(OUT / "comparison_skipped.parquet", index=False)
    c = res[res.variant == "theta_cyprus"].pivot_table(
        index="year", columns="geo", values="domestic_value_retention"
    )
    print((100 * c).round(1).to_string())
    print(f"skipped country-years: {len(skipped)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
