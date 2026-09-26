"""End-to-end model run: writes data/processed/*.parquet and data/cvr.duckdb.

python -m cvr.pipeline            # everything
"""

from __future__ import annotations

import itertools
import json
from datetime import date
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from .accounts import headline_metrics, value_tensor
from .io_model import solve
from .model import frame_a, frame_b
from .model.ownership_data import resolve_cyprus, theta_calibration
from .model.suiot import available_years, build
from .provenance import require, retrieval_date
from .reconcile import reconcile

OUT = Path("data/processed")
DB = Path("data/cvr.duckdb")
FRAME_A_YEARS = list(range(2010, 2024))

MODEL_VERSION = "0.1.0"

REPO = "https://github.com/diomavro/country-value-retention/blob/main/"
SOURCE_URLS = {
    "CYSTAT": "https://cystatdb.cystat.gov.cy/pxweb/en/8.CYSTAT-DB/",
    "fats_activ": "https://ec.europa.eu/eurostat/databrowser/view/fats_activ/default/table",
    "fats_g1a_08": "https://ec.europa.eu/eurostat/databrowser/view/fats_g1a_08/default/table",
    "bop_c6_a": "https://ec.europa.eu/eurostat/databrowser/view/bop_c6_a/default/table",
    "bop_rem6": "https://ec.europa.eu/eurostat/databrowser/view/bop_rem6/default/table",
    "bop_fdi6_inc": "https://ec.europa.eu/eurostat/databrowser/view/bop_fdi6_inc/default/table",
    "nama_10_a64": "https://ec.europa.eu/eurostat/databrowser/view/nama_10_a64/default/table",
    "nasa_10_nf_tr": "https://ec.europa.eu/eurostat/databrowser/view/nasa_10_nf_tr/default/table",
    "naio_10_fcp": "https://ec.europa.eu/eurostat/databrowser/view/naio_10_fcp_ii4/default/table",
    "OECD": "https://data-explorer.oecd.org/vis?df[ds]=DisseminateFinalDMZ&df[id]=DSD_TAX_CIT%40DF_CIT&df[ag]=OECD.CTP.TPS",
    "company filings": REPO + "data/raw/companies/SOURCES.md",
    "model output": REPO + "docs/methodology.md",
}


def _url(source: str) -> str:
    """URLs of every source named in `source`; an unrecognised source is an error, not CYSTAT."""
    hits = [u for k, u in SOURCE_URLS.items() if k in source]
    if not hits:
        raise ValueError(f"no source URL known for {source!r}; add it to SOURCE_URLS")
    return " ; ".join(hits)


def _provenance(df: pd.DataFrame, year_col: str = "year") -> pd.DataFrame:
    df = df.copy()
    if "source" not in df:
        df["source"] = "model output (cvr " + MODEL_VERSION + ")"
    df["source"] = df["source"].fillna("model output")
    df["source_url"] = df["source"].map(_url)
    df["reference_year"] = df[year_col]
    df["retrieval_date"] = retrieval_date()  # latest download date among the inputs
    if "methodology" not in df:
        df["methodology"] = "see docs/methodology.md"
    df["methodology"] = df["methodology"].fillna("see docs/methodology.md")
    if "confidence_level" not in df:
        df["confidence_level"] = "medium"
    df["confidence_level"] = df["confidence_level"].fillna("medium")
    if "status" not in df:
        df["status"] = "modelled"
    return df


def run_frame_a(prm: frame_a.Params) -> tuple[pd.DataFrame, pd.DataFrame]:
    tensors, metrics = [], []
    for y in FRAME_A_YEARS:
        acc, diag = frame_a.build_account(y, prm)
        t = value_tensor(acc)
        # retained rows carry high confidence: they are GVA (observed) minus estimated outflows
        t["confidence_level"] = t.get(
            "confidence_level", pd.Series(index=t.index, dtype=object)
        ).fillna("medium")
        t["source"] = t.get("source", pd.Series(index=t.index, dtype=object)).fillna(
            "CYSTAT/Eurostat national accounts (nama_10_a64) minus outflows"
        )
        m = headline_metrics(
            acc, t, official_primary_income_paid=diag["official_primary_income_paid"]
        )
        # Foreign Ownership Capture: foreign-owned share of corporate net operating surplus, both
        # before interest and corporate tax (like-for-like); creditor share on the same base.
        cnos = frame_a.corporate_nos(y)
        # creditor share: interest and portfolio income paid abroad by firms and banks (households'
        # mortgage interest, booked to L68A, is excluded: the denominator is corporate surplus)
        cred = float(t.loc[t.mechanism.isin(["other_investment_income", "portfolio_income"]) & (t.industry != "L68A"), "value"].sum())
        m.update(
            foreign_ownership_capture=diag["foreign_owned_nos"] / cnos,
            foreign_creditor_income_share_of_nos=cred / cnos,
            corporate_net_operating_surplus=cnos,
            fdi_fitted_cell_share=diag["imputed_country_value"] / max(float(t.loc[t.mechanism == "fdi_income", "value"].sum()), 1e-9),
            labour_gross=diag["labour_gross"],
            employer_ssc_share=diag["employer_ssc_share"],
            interest_ratio_nonfin=diag["interest_ratio_nonfin"],
            intra_group_share=diag["intra_group_share"],
            cfc_ratio_nonfin=diag["cfc_ratio_nonfin"],
            cfc_ratio_fin=frame_a.corporate_ratios(y)["cfc_fin"],
            confidential_items=json.dumps(diag["confidential_items"]),
            confidential_upper_bound=json.dumps(diag.get("confidential_upper_bound", {})),
            intra_group_interest_bop=diag.get("intra_group_interest_bop", float("nan")),
            banks_interest_paid=diag["banks_interest_paid"],
            banks_interest_received=diag["banks_interest_received"],
        )
        m.update(
            year=y,
            official_gni=diag["official_gni"],
            official_primary_income_paid=diag["official_primary_income_paid"],
            ofc_investment_income_paid=diag["ofc_investment_income_paid"],
            fats_foreign_gos=diag["fats_foreign_gos"],
            fats_scope=diag["fats_scope"],
            tau=diag["tau"],
            theta=prm.theta if prm.theta is not None else frame_a.calibrated_theta(),
            capped_industries=json.dumps(diag["capped"]),
            negative_fats_sections=json.dumps(diag["negative_sections"]),
        )
        tensors.append(t)
        metrics.append(m)
    return pd.concat(tensors, ignore_index=True), pd.DataFrame(metrics)


def comparators() -> pd.DataFrame:
    """Official series the model is contrasted with (not model outputs)."""
    f = pd.read_parquet(
        sorted(
            Path("data/raw/eurostat").glob(
                "bop_fdi6_inc__currency-MIO_EUR_geo-CY_partner-*.parquet"
            )
        )[0]
    )
    x = f[
        (f.partner == "WRL_REST")
        & (f.nace_r2 == "FDI")
        & (f.stk_flow == "DEB")
        & (f.fdi_item == "DI__D4P__D__F")
    ]
    p = x.pivot_table(index="TIME_PERIOD", columns="entity", values="OBS_VALUE")
    p.index = p.index.astype(int)
    out = pd.DataFrame(
        {
            "year": p.index,
            "fdi_income_paid_total": p.get("TOTAL"),
            "fdi_income_paid_spe": p.get("SPE"),
            "fdi_income_paid_non_spe": p.get("TOTAL") - p.get("SPE"),
        }
    ).reset_index(drop=True)
    out["source"] = (
        "Eurostat bop_fdi6_inc (DI__D4P__D__F, DEB, WRL_REST); non-SPE = TOTAL - SPE"
    )
    out["methodology"] = "official BoP; blank where Eurostat marks a cell confidential"
    out["status"] = np.where(
        out["fdi_income_paid_non_spe"].notna(), "modelled", "observed"
    )
    out["confidence_level"] = "high"
    return out


def io_indicators() -> pd.DataFrame:
    rows = []
    for y in available_years():
        table, _, fd = build(y)
        r = solve(table)
        for i, lab in enumerate(r.labels):
            rows.append(
                {
                    "year": y,
                    "product": lab.removeprefix("CPA_"),
                    "output": table.x[i],
                    "gva": table.v[i],
                    "imported_intermediates": table.Zm[:, i].sum(),
                    "domestic_intermediates": table.Zd[:, i].sum(),
                    "direct_foreign_input_exposure": r.direct_import_share[i],
                    "direct_import_intensity": r.direct_import_intensity[i],
                    "total_import_content": r.total_import_content[i],
                    "total_domestic_va_content": r.total_va_content[i],
                    "final_demand_domestic_output": float(fd.iloc[i].sum()),
                }
            )
    df = pd.DataFrame(rows)
    df["source"] = "CYSTAT SIOT 0640050E/0640055E"
    df["methodology"] = (
        "Leontief model, domestic and imported blocks separate (src/cvr/io_model.py)"
    )
    df["status"] = "modelled"
    df["confidence_level"] = "high"
    return df


ONE_AT_A_TIME = [
    dict(banks_gross=True),
    dict(fats_na_level=False),
    dict(tax="eatr"),
    dict(bop_upper=True),
    dict(rho_basis="none"),
    dict(rho_basis="d41_net"),
    dict(rho_basis="d41g_gross"),
]
# every assumption at the end that lowers retention, at once
WORST_CASE = dict(banks_gross=True, bop_upper=True, include_ofc=True, consistent_scope=True, tax="none", theta=1.0, rho_basis="none", fats_na_level=False)


def sensitivity_grid() -> list:
    """theta x tax x SPE-sector x scope, then one-at-a-time variants and the combined worst case."""
    grid = [
        frame_a.Params(theta=th, tax=tx, include_ofc=ofc, consistent_scope=cons)
        for th, tx, ofc, cons in itertools.product([0.6, 0.7, 0.8, 0.9, frame_a.calibrated_theta(), 1.0], ["statutory", "none"], [False, True], [False, True])
    ]
    grid += [frame_a.Params(**kw) for kw in ONE_AT_A_TIME]
    grid.append(frame_a.Params(**WORST_CASE))
    return grid


def sensitivity() -> pd.DataFrame:
    """Frame A re-run over `sensitivity_grid()`."""
    grid = sensitivity_grid()
    rows = []
    for prm in grid:
        _, m = run_frame_a(prm)
        rows.append(
            m[["year", "domestic_value_retention", "foreign_value_leakage", "foreign_ownership_capture"]].assign(
                theta=prm.theta if prm.theta is not None else frame_a.calibrated_theta(), tax=prm.tax, include_ofc=prm.include_ofc, consistent_scope=prm.consistent_scope, banks_gross=prm.banks_gross, bop_upper=prm.bop_upper, rho_basis=prm.rho_basis, fats_na_level=prm.fats_na_level
            )
        )
    df = pd.concat(rows, ignore_index=True)
    df["source"] = "model output"
    df["methodology"] = "Frame A re-run over parameter grid"
    df["status"] = "estimated"
    df["confidence_level"] = "medium"
    return df


def interest_ratios() -> pd.DataFrame:
    """rho (all bases) and the intra-group share s by year, for transparency (referee R1)."""
    rows = []
    for y in FRAME_A_YEARS:
        r = {b: frame_a.corporate_ratios(y, b)["interest_nonfin"] for b in ("d41_gross", "d41_net", "d41g_gross")}
        c = frame_a.corporate_ratios(y)
        rows.append({"year": y, "rho_d41_gross": r["d41_gross"], "rho_d41_net": r["d41_net"], "rho_d41g_gross": r["d41g_gross"], "cfc_nonfin": c["cfc_nonfin"], "intra_group_share": c["intra_group_share"]})
    df = pd.DataFrame(rows)
    df["source"] = "Eurostat nasa_10_nf_tr (S11); bop_c6_a (S1V FDI debt interest)"
    df["methodology"] = "ratios to S11 gross operating surplus; s = BoP FDI debt interest / S11 D41 paid"
    df["status"] = "modelled"
    df["confidence_level"] = "high"
    return df


def bridge(tensor: pd.DataFrame) -> pd.DataFrame:
    """Official primary income paid abroad -> this study's outflow, line by line (referee M6).

    Official side: CYSTAT S2 accounts (D1, D2, D4 received by the rest of the world) and the
    BoP by resident sector (Eurostat bop_c6_a).  Model side: the recipient tensor.  Every line
    states what the difference is; the NA/BoP vintage gap is reported, not hidden.
    """
    B = frame_a._bop
    rows = []
    for y in sorted(tensor.year.unique()):
        t = tensor[tensor.year == y]
        mech = t[t.mechanism != "retained_domestic"].groupby("mechanism").value.sum()
        s2 = frame_a._sector().loc[(y, "S2")]
        d4_na = float(s2["D4REC"])
        s1 = B(y, "S1", "D4P__F", "DEB")[0]
        by = {k: B(y, k, "D4P__F", "DEB")[0] for k in ("S121", "S122", "S12M", "S13", "S1V")}
        if pd.isna(by["S122"]):  # banks' total suppressed: MFIs other than the central bank (S12T =
            by["S122"] = B(y, "S12T", "D4P__F", "DEB")[0]  # S122 + money-market funds, which are nil in CY)
        v_eq, v_debt = B(y, "S1V", "D4S__D__F5", "DEB")[0], B(y, "S1V", "D41__D__FLA", "DEB")[0]
        fdi = t[t.mechanism == "fdi_income"]
        t_fdi_k64 = float(fdi[fdi.industry == "K64"].value.sum())  # banks (S122)
        t_fdi_k6566 = float(fdi[fdi.industry.isin(["K65", "K66"])].value.sum())  # insurers, auxiliaries (in S12M)
        t_fdi_k = t_fdi_k64 + t_fdi_k6566
        t_fdi_nonk = float(mech.get("fdi_income", 0)) - t_fdi_k
        t_bank_int = float(t[(t.mechanism == "other_investment_income") & (t.industry == "K64")].value.sum())
        t_s1v_other = float(mech.get("other_investment_income", 0) + mech.get("portfolio_income", 0)) - t_bank_int
        lines = [
            ("1 Compensation of employees paid (S2 D1)", float(s2["D1REC"]), float(mech.get("compensation_nonresident", 0)), "model is net of Cypriot employer social contributions"),
            ("2 Taxes on production to EU institutions (S2 D2)", float(s2["D2REC"]) if pd.notna(s2["D2REC"]) else 0.0, float(mech.get("taxes_to_eu_institutions", 0)), "identical"),
            ("3 Property income: NA (S2 D4) minus BoP total (S1)", d4_na - s1 if pd.notna(s1) else float("nan"), 0.0, "vintage/compilation gap between national accounts and BoP"),
            ("4 Non-bank financial corporations incl. SPEs (S12M)", by["S12M"], t_fdi_k6566, "excluded as pass-through, except the FATS profit of foreign-owned insurers and auxiliary financial firms (from 2021)"),
            ("5 Central bank (S121)", by["S121"], 0.0, "excluded: reserve management"),
            ("6 Banks (S122)", by["S122"], t_fdi_k64 + t_bank_int, "model: foreign-owned finance profit (FATS K from 2021; BoP bank FDI equity income before) + banks' interest net of receipts"),
            ("7 General government (S13)", by["S13"], float(mech.get("public_debt_interest", 0)), "identical (interest items)"),
            ("8a Firms and households: FDI equity income (S1V)", v_eq, t_fdi_nonk, "model uses FATS (production-based): the difference is income passed on by non-SPE holding and trading companies, plus FATS/BPM6 concept differences"),
            ("8b Firms and households: FDI debt interest (S1V)", v_debt, float(mech.get("fdi_debt_interest", 0)), "model caps intra-group interest at the interest deducted from foreign-controlled firms' surplus"),
            ("8c Firms and households: other interest and portfolio income (S1V)", (by["S1V"] - (v_eq if pd.notna(v_eq) else 0) - (v_debt if pd.notna(v_debt) else 0)) if pd.notna(by["S1V"]) else float("nan"), t_s1v_other, "identical where published; confidential items omitted (lower bound)"),
        ]
        for name, off, mod, why in lines:
            rows.append({"year": int(y), "line": name, "official": off, "model": mod, "difference": (off - mod) if pd.notna(off) else float("nan"), "explanation": why})
        rows.append({"year": int(y), "line": "Total", "official": float(s2["D1REC"]) + (float(s2["D2REC"]) if pd.notna(s2["D2REC"]) else 0) + d4_na, "model": float(mech.sum()), "difference": float("nan"), "explanation": "official primary income paid vs this study's outflow"})
    df = pd.DataFrame(rows)
    df["source"] = "CYSTAT 0630030E; Eurostat bop_c6_a; model output"
    df["methodology"] = "sector-by-sector bridge; see docs/methodology.md"
    df["status"] = "modelled"
    df["confidence_level"] = "high"
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    central = frame_a.Params()
    tensor, metrics = run_frame_a(central)
    tensor = tensor.rename(columns={"partner": "recipient"})
    _, metrics_cons = run_frame_a(frame_a.Params(consistent_scope=True))

    fb_rows, fb_econ = [], []
    for y in available_years():
        t = tensor[tensor.year == y].rename(columns={"recipient": "partner"})
        fb_rows.append(frame_b.per_euro(y, t))
        fb_econ.append(frame_b.economy_final_demand(y, t))
    per_euro = pd.concat(fb_rows, ignore_index=True).rename(
        columns={"partner": "recipient"}
    )
    econ = pd.concat(fb_econ, ignore_index=True).rename(
        columns={"partner": "recipient"}
    )

    own_summary, own_detail = resolve_cyprus()
    theta = theta_calibration()

    rec = reconcile({y: float(g.value.sum()) for y, g in tensor.groupby("year")})

    tables = {
        "recipient_tensor": _provenance(tensor),
        "headline_metrics": _provenance(
            metrics.assign(source="model output", status="estimated")
        ),
        "headline_metrics_consistent_scope": _provenance(
            metrics_cons.assign(source="model output", status="estimated")
        ),
        "frame_b_per_euro": _provenance(
            per_euro.assign(source="model output (Frame B): CYSTAT SIOT 0640050E/0640055E; Eurostat naio_10_fcp (FIGARO)", status="modelled")
        ),
        "frame_b_economy": _provenance(
            econ.assign(source="model output (Frame B): CYSTAT SIOT 0640050E/0640055E; Eurostat naio_10_fcp (FIGARO)", status="modelled")
        ),
        "io_indicators": _provenance(io_indicators()),
        "comparators": _provenance(comparators()),
        "sensitivity": _provenance(sensitivity()),
        "bridge": _provenance(bridge(tensor)),
        "interest_ratios": _provenance(interest_ratios()),
        "reconciliation": _provenance(
            rec.assign(
                source="CYSTAT national accounts vs model",
                status="modelled",
                confidence_level="high",
            )
        ),
        "ownership_firms": _provenance(
            own_summary.assign(
                year=2025,
                source="company filings (data/raw/companies)",
                status="estimated",
                confidence_level=own_summary["confidence"],
            )
        ),
        "ownership_ultimate": _provenance(
            own_detail.assign(
                year=2025,
                source="company filings (data/raw/companies)",
                status="estimated",
                confidence_level="medium",
            )
        ),
        "theta_calibration": _provenance(
            theta.assign(
                year=2025,
                source="company filings (data/raw/companies)",
                status="estimated",
                confidence_level="low",
            )
        ),
    }
    con = duckdb.connect(str(DB))
    for name, df in tables.items():
        require(df, name)
        df.to_parquet(OUT / f"{name}.parquet", index=False)
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM df")
    con.close()
    (OUT / "RUN.json").write_text(
        json.dumps(
            {
                "model_version": MODEL_VERSION,
                "run_date": str(date.today()),
                "tables": {k: len(v) for k, v in tables.items()},
            },
            indent=2,
        )
    )
    print(
        metrics[
            [
                "year",
                "gdp",
                "domestic_value_retention",
                "foreign_value_leakage",
                "primary_income_outflow_to_gdp",
            ]
        ]
        .round(4)
        .to_string()
    )
    print("reconciliation all pass:", bool(rec.passes.all()))


if __name__ == "__main__":
    main()
