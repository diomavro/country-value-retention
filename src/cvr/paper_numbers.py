"""Write paper/numbers.tex: every number quoted in the paper, as a LaTeX macro.

The paper never hard-codes a result; re-running the pipeline and this script
updates the text.  Macro names are letters only (LaTeX restriction).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from .export_web import INDUSTRY_NAMES, RECIPIENT_NAMES

P = Path("data/processed")
OUT = Path("paper/numbers.tex")
WORDS = {
    0: "Zero",
    1: "One",
    2: "Two",
    3: "Three",
    4: "Four",
    5: "Five",
    6: "Six",
    7: "Seven",
    8: "Eight",
}


def pct(x: float, d: int = 1) -> str:
    return f"{100 * x:.{d}f}\\%"


def eur(x: float, d: int = 0) -> str:
    return f"{x:,.{d}f}".replace(",", "{,}")


def bn(x: float, d: int = 1) -> str:
    return f"{x / 1000:.{d}f}"


def main() -> None:
    m = pd.read_parquet(P / "headline_metrics.parquet").set_index("year")
    mc = pd.read_parquet(P / "headline_metrics_consistent_scope.parquet").set_index(
        "year"
    )
    t = pd.read_parquet(P / "recipient_tensor.parquet")
    io = pd.read_parquet(P / "io_indicators.parquet")
    pe = pd.read_parquet(P / "frame_b_per_euro.parquet")
    ec = pd.read_parquet(P / "frame_b_economy.parquet")
    sens = pd.read_parquet(P / "sensitivity.parquet")
    rec = pd.read_parquet(P / "reconciliation.parquet")
    comp = pd.read_parquet(P / "comparators.parquet").set_index("year")
    theta = pd.read_parquet(P / "theta_calibration.parquet")
    firms = pd.read_parquet(P / "ownership_firms.parquet")
    ex = json.loads((P / "example_platform_fee.json").read_text())
    cat = pd.read_csv("data_catalogue.csv")

    L, IOL = int(m.index.max()), int(io.year.max())
    first = int(m.index.min())
    mac: dict[str, str] = {}

    def put(name, val):
        assert name.isalpha(), name
        mac[name] = val

    put("FirstYear", str(first))
    put("LastYear", str(L))
    put("IOLastYear", str(IOL))
    put("GDPLast", bn(m.loc[L, "gdp"]))
    put("DVRLast", pct(m.loc[L, "domestic_value_retention"]))
    put("FVLLast", pct(m.loc[L, "foreign_value_leakage"]))
    put("FVLLastEUR", bn(m.loc[L, "foreign_value_leakage"] * m.loc[L, "gdp"], 2))
    put("DVRMin", pct(m.domestic_value_retention.min()))
    put("DVRMax", pct(m.domestic_value_retention.max()))
    put("DVRMinYear", str(int(m.domestic_value_retention.idxmin())))
    put("DVRMaxYear", str(int(m.domestic_value_retention.idxmax())))
    put("FVLMin", pct(m.foreign_value_leakage.min()))
    put("FVLMax", pct(m.foreign_value_leakage.max()))
    put("OfficialOutMin", pct(m.primary_income_outflow_to_gdp.min(), 0))
    put("OfficialOutMax", pct(m.primary_income_outflow_to_gdp.max(), 0))
    put("OfficialOutLast", pct(m.loc[L, "primary_income_outflow_to_gdp"], 0))
    put("OfficialOutLastEUR", bn(m.loc[L, "official_primary_income_paid"]))
    put("GNILastEUR", bn(m.loc[L, "official_gni"]))
    for y, nm in ((2022, "TwentyTwo"), (L, "Last")):
        put(f"OFCPaid{nm}", bn(m.loc[y, "ofc_investment_income_paid"]))
    put("NonSPEFDILast", pct(comp.loc[L, "fdi_income_paid_non_spe"] / m.loc[L, "gdp"]))
    put("NonSPEFDILastEUR", bn(comp.loc[L, "fdi_income_paid_non_spe"]))
    put("TotalFDIPaidLastEUR", bn(comp.loc[L, "fdi_income_paid_total"]))
    put("FOCLast", pct(m.loc[L, "foreign_ownership_capture"]))
    put("FOCFirst", pct(m.loc[first, "foreign_ownership_capture"]))
    put("FCredLast", pct(m.loc[L, "foreign_creditor_income_share_of_nos"]))
    put("FLILast", pct(m.loc[L, "foreign_labour_income_share"]))
    put("FATSForeignGOSLast", bn(m.loc[L, "fats_foreign_gos"], 2))
    put("DVRConsLast", pct(mc.loc[L, "domestic_value_retention"]))
    put("DVRTwentyTwenty", pct(m.loc[2020, "domestic_value_retention"]))
    put("DVRTwentyTwentyTwo", pct(m.loc[2022, "domestic_value_retention"]))

    # mechanisms, last year
    f = t[(t.year == L) & (t.mechanism != "retained_domestic")]
    mech = f.groupby("mechanism").value.sum()
    for k, nm in (
        ("fdi_income", "MechFDI"),
        ("compensation_nonresident", "MechLabour"),
        ("other_investment_income", "MechOther"),
        ("portfolio_income", "MechPortfolio"),
        ("public_debt_interest", "MechGov"),
        ("taxes_to_eu_institutions", "MechEU"),
        ("fdi_debt_interest", "MechDebt"),
    ):
        put(nm, eur(mech.get(k, 0.0)))
    put("MechFDIShare", pct(mech.get("fdi_income", 0) / mech.sum(), 0))

    # recipients, last year
    rec_ = f.groupby("recipient").value.sum().sort_values(ascending=False)
    unknown = {
        "CONFIDENTIAL_PARTNERS",
        "WORLD_UNALLOCATED",
        "EU27_UNALLOCATED",
        "EXTRA_EU_UNALLOCATED",
    }
    known = rec_[~rec_.index.isin(unknown)]
    for i, (r, v) in enumerate(known.head(5).items(), 1):
        put(f"Rec{WORDS[i]}Name", RECIPIENT_NAMES.get(r, r))
        put(f"Rec{WORDS[i]}EUR", eur(v))
    put("RecUnknownEUR", eur(rec_[rec_.index.isin(unknown)].sum()))
    put("RecUnknownShare", pct(rec_[rec_.index.isin(unknown)].sum() / rec_.sum(), 0))
    put("RecConfEUR", eur(rec_.get("CONFIDENTIAL_PARTNERS", 0)))
    put("RecWorldEUR", eur(rec_.get("WORLD_UNALLOCATED", 0)))
    wu = t[(t.recipient == "WORLD_UNALLOCATED")].groupby("year").value.sum()
    put("WorldUnallocMin", eur(wu.min()))
    put("WorldUnallocMax", eur(wu.max()))

    # industries, last year: top 3 by foreign outflow and their retention
    na_f = (
        f.groupby("industry")
        .value.sum()
        .drop(index="_PRODUCT_TAXES", errors="ignore")
        .sort_values(ascending=False)
    )
    gva = (
        t[(t.year == L) & (t.industry != "_PRODUCT_TAXES")]
        .groupby("industry")
        .value.sum()
    )
    for i, (k, v) in enumerate(na_f.head(3).items(), 1):
        put(f"Ind{WORDS[i]}Name", INDUSTRY_NAMES.get(k, k))
        put(f"Ind{WORDS[i]}EUR", eur(v))
        put(f"Ind{WORDS[i]}DVR", pct(1 - v / gva[k]))

    gov = t[t.mechanism == "public_debt_interest"].groupby("year").value.sum()
    put("GovPeak", eur(gov.max()))
    put("GovPeakYear", str(int(gov.idxmax())))
    put("GovTwentyTwo", eur(gov.loc[2022]))
    put("GovLast", eur(gov.loc[L]))

    # input exposure
    g = io.groupby("year")
    fie = g.apply(
        lambda d: (
            d.imported_intermediates.sum()
            / (d.imported_intermediates.sum() + d.domestic_intermediates.sum())
        )
    )
    tic = g.apply(
        lambda d: (
            (d.total_import_content * d.final_demand_domestic_output).sum()
            / d.final_demand_domestic_output.sum()
        )
    )
    put("FIEFirst", pct(fie.loc[first]))
    put("FIELast", pct(fie.loc[IOL]))
    put("TICFirst", pct(tic.loc[first]))
    put("TICLast", pct(tic.loc[IOL]))
    put("ImpInterFirst", bn(g.imported_intermediates.sum().loc[first]))
    put("ImpInterLast", bn(g.imported_intermediates.sum().loc[IOL]))
    grow = io.pivot_table(index="product", columns="year", values="imported_intermediates")
    grow = (grow[IOL] - grow[first]).sort_values(ascending=False)
    put("ImpGrowthTotal", bn(grow.sum()))
    put("ImpGrowthFour", bn(grow.loc[["J62-63", "K64", "K66", "J58"]].sum()))
    last_io = io[io.year == IOL].set_index("product")
    for k, nm in (
        ("J62-63", "IT"),
        ("K66", "AuxFin"),
        ("J58", "Pub"),
        ("K64", "Bank"),
        ("I", "Rest"),
        ("F", "Constr"),
        ("G47", "Retail"),
    ):
        put(f"FIE{nm}", pct(last_io.loc[k, "direct_foreign_input_exposure"], 0))
    # Frame B per euro, IO last year
    pl = pe[pe.year == IOL]
    for k, nm in (
        ("I", "Rest"),
        ("G47", "Retail"),
        ("J62-63", "IT"),
        ("K64", "Bank"),
        ("F", "Constr"),
        ("L68B", "RealEst"),
    ):
        gk = pl[pl["product"] == k]
        put(
            f"PE{nm}Home",
            f"{100 * gk[(gk.channel == 'domestic_value_added') & (gk.recipient == 'CY')].value.sum():.0f}",
        )
        put(
            f"PE{nm}AbroadVA",
            f"{100 * gk[(gk.channel == 'domestic_value_added') & (gk.recipient != 'CY')].value.sum():.0f}",
        )
        put(
            f"PE{nm}Imp", f"{100 * gk[gk.channel == 'imported_inputs'].value.sum():.0f}"
        )
    e = ec[ec.year == IOL]
    put("EconDomVA", eur(e[e.channel == "domestic_value_added"].value.sum()))
    put("EconImp", eur(e[e.channel == "imported_inputs"].value.sum()))
    imp_by = (
        e[(e.channel == "imported_inputs")]
        .groupby("recipient")
        .value.sum()
        .sort_values(ascending=False)
    )
    imp_known = imp_by.drop(index="ROW_FIGARO", errors="ignore")
    for i, (r, v) in enumerate(imp_known.head(3).items(), 1):
        put(f"ImpSrc{WORDS[i]}Name", RECIPIENT_NAMES.get(r, r))
        put(f"ImpSrc{WORDS[i]}EUR", bn(v))

    # platform example (illustrative)
    put("PlatHome", f"{ex['stays_in_cyprus']:.2f}")
    put("PlatOwner", f"{ex['foreign_capital_income_platform_owner']:.2f}")
    put("PlatSuppAbroad", f"{ex['foreign_income_via_suppliers']:.2f}")
    put("PlatImp", f"{ex['imported_inputs']:.2f}")
    put("PlatLabour", f"{ex['cyprus_labour_platform']:.2f}")

    # sensitivity, last year: theta x tax (central scope), and the full envelope of all variants
    s = sens[(sens.year == L) & (~sens.include_ofc) & (~sens.consistent_scope) & (~sens.banks_gross) & (~sens.bop_upper) & (sens.rho_basis == "d41_gross") & sens.fats_na_level]
    th = s[s.tax == "statutory"].set_index("theta").domestic_value_retention
    assert not th.index.duplicated().any(), "theta grid: more than one row per theta (a variant leaked in)"
    put("SensThetaSpreadPP", f"{100 * (th.max() - th.min()):.1f}")
    put("SensDVRLow", pct(s.domestic_value_retention.min()))
    put("SensDVRHigh", pct(s.domestic_value_retention.max()))
    allL = sens[sens.year == L]
    put("SensAllLow", pct(allL.domestic_value_retention.min()))
    put("SensAllHigh", pct(allL.domestic_value_retention.max()))
    one = lambda **kw: allL.loc[np.logical_and.reduce([allL[k] == v for k, v in kw.items()]), "domestic_value_retention"].iloc[0]
    base = dict(theta=m.loc[L, "theta"], tax="statutory", include_ofc=False, consistent_scope=False, banks_gross=False, bop_upper=False, rho_basis="d41_gross", fats_na_level=True)
    put("SensOFCDVR", pct(one(**{**base, "include_ofc": True})))
    put("SensBopUpperDVR", pct(one(**{**base, "bop_upper": True})))
    put("SensBanksGrossDVR", pct(one(**{**base, "banks_gross": True})))
    put("SensNoTaxDVR", pct(one(**{**base, "tax": "none"})))
    put("SensFatsLevelDVR", pct(one(**{**base, "fats_na_level": False})))
    put("SensRhoNoneDVR", pct(one(**{**base, "rho_basis": "none"})))
    put("SensRhoGrossDVR", pct(one(**{**base, "rho_basis": "d41g_gross"})))
    put("SensRhoNetDVR", pct(one(**{**base, "rho_basis": "d41_net"})))
    fy = sens[sens.year == first]
    put("SensBanksGrossFirst", pct(fy.loc[np.logical_and.reduce([fy[k] == v for k, v in {**base, "theta": m.loc[first, "theta"], "banks_gross": True}.items()]), "domestic_value_retention"].iloc[0]))
    put("DVRFirst", pct(m.loc[first, "domestic_value_retention"]))

    # labour, interest, imputation, bridge
    put("LabourGrossLast", eur(m.loc[L, "labour_gross"]))
    put("SSCShareLast", pct(m.loc[L, "employer_ssc_share"]))
    put("InterestRatioLast", pct(m.loc[L, "interest_ratio_nonfin"], 0))
    put("IntraShareLast", pct(m.loc[L, "intra_group_share"], 0))
    put("IntraShareFirst", pct(m.loc[first, "intra_group_share"], 0))
    put("InterestRatioFirst", pct(m.loc[first, "interest_ratio_nonfin"], 0))
    tl = t[t.year == L]
    k64_fats = float(tl[(tl.mechanism == "fdi_income") & (tl.industry == "K64")].value.sum())
    from .model.frame_a import _bop

    put("BankBopLast", eur(_bop(L, "S122", "D4S__D__F5", "DEB")[0]))
    put("BankFatsLast", eur(k64_fats))

    def k_fdi(y, codes):
        ty = t[(t.year == y) & (t.mechanism == "fdi_income")]
        return float(ty[ty.industry.isin(codes)].value.sum())

    fats_years = [y for y in range(2021, L) if y in m.index]  # FATS covers banks from 2021
    put("BankAgreeGap", eur(max(abs(_bop(y, "S122", "D4S__D__F5", "DEB")[0] - k_fdi(y, ["K64"])) for y in fats_years)))
    put("InsAuxShareFirstFats", pct(k_fdi(2021, ["K65", "K66"]) / m.loc[2021, "gdp"]))
    from .model.frame_a import fats_foreign_gos

    put("FATSPublishedLast", bn(fats_foreign_gos(L)["total"], 2))  # as published, before the finance cap

    # upper bound on Irish-controlled finance: published EU-controlled K less the published EU member cells
    from .model.frame_a import _one

    eu27 = "AT BE BG CZ DE DK EE EL ES FI FR HR HU IE IT LT LU LV MT NL PL PT RO SE SI SK".split()
    fk = _one("fats_activ__*.parquet")
    fk = fk[(fk.indic_sbs == "GOS_MEUR") & (fk.nace_r2 == "K")]
    bound = {}
    for y in sorted(fk.TIME_PERIOD.astype(int).unique()):
        x = fk[fk.TIME_PERIOD.astype(int) == y].set_index("c_ctrl").OBS_VALUE
        bound[y] = float(x["INT_EU27_2020"] - x.reindex(eu27).dropna().sum())
    put("IrishFinBoundFirst", eur(min(bound.values())))
    put("IrishFinBoundLast", eur(max(bound.values())))

    # shares of confidential cells in the raw FATS and FDI-income files (data-table note)
    def conf(pattern, y0=None, y1=None):
        d = _one(pattern)
        yr = d.TIME_PERIOD.astype(int)
        d = d[(yr >= (y0 or yr.min())) & (yr <= (y1 or yr.max()))]
        return float((d.CONF_STATUS == "C").mean())

    put("ConfFatsLow", pct(conf("fats_g1a_08__*.parquet"), 0))
    put("ConfFatsHigh", pct(conf("fats_activ__*.parquet"), 0))
    put("ConfFdi", pct(conf("bop_fdi6_inc__*.parquet", None, L), 0))
    put("BanksPaidFirst", eur(m.loc[first, "banks_interest_paid"]))
    put("BanksRecvFirst", eur(m.loc[first, "banks_interest_received"]))
    br = pd.read_parquet(P / "bridge.parquet")
    bl = br[br.year == L].set_index("line")
    put("BridgeSpeLast", bn(bl.loc[[i for i in bl.index if i.startswith("4 ")][0], "official"]))
    fe = bl.loc[[i for i in bl.index if i.startswith("8a")][0]]
    put("BridgeFdiEqOfficialLast", bn(fe.official, 2))
    put("BridgeFdiEqModelLast", bn(fe.model, 2))
    put("BridgeFdiEqGapLast", bn(fe.official - fe.model, 2))

    # ownership / calibration
    put("ThetaN", str(len(theta)))
    put("ThetaGroups", str(theta.group.nunique()))
    put("ThetaMean", f"{m.loc[L, 'theta']:.2f}")
    put("FirmsN", str(len(firms)))
    put(
        "FirmsForeignUCI",
        str(int((~firms.uci_country.isin(["CY", "UNRESOLVED"])).sum())),
    )
    put("FirmsUnresolvedUCI", str(int((firms.uci_country == "UNRESOLVED").sum())))
    put("CatalogueN", str(len(cat)))
    r = rec[rec.check.str.startswith("GNI")]
    put("GNIMaxGap", f"{r.pct_difference.abs().max():.3f}\\%")

    # other countries (cvr.compare): Cyprus method, Eurostat inputs
    cr = pd.read_parquet(P / "comparison.parquet")
    cc = cr[cr.variant == "theta_cyprus"].set_index(["geo", "year"])
    CL = int(cc.index.get_level_values("year").max())
    put("CmpYear", str(CL))
    for g, name in {"IE": "IE", "LU": "LU", "NL": "NL", "EL": "EL", "PT": "PT"}.items():
        put(f"Cmp{name}", pct(cc.loc[(g, CL), "domestic_value_retention"]))
        put(f"Cmp{name}Official", pct(cc.loc[(g, CL), "primary_income_outflow_to_gdp"], 0))
    put("CmpIEProfit", pct(cc.loc[("IE", CL), "share_fdi_income"]))
    put("CmpLUCommuters", pct(cc.loc[("LU", CL), "share_compensation_nonresident"]))
    put("CmpELPublic", pct(cc.loc[("EL", CL), "share_public_debt_interest"]))
    gap = cr.pivot_table(index=["geo", "year"], columns="variant", values="domestic_value_retention")
    cy_last = cc.loc[("CY", CL), "domestic_value_retention"]
    # "at least N points": floor, so the rounded table values never contradict the text
    put("CmpHubGap", str(math.floor(100 * (cy_last - max(cc.loc[(g, CL), "domestic_value_retention"] for g in ("IE", "LU"))))))
    put("CmpThetaMaxGap", f"{100 * (gap.theta_cyprus - gap.theta_1).max():.1f}")
    cy_check = abs(cc.loc[("CY", CL), "domestic_value_retention"] - m.loc[CL, "domestic_value_retention"])
    assert cy_check < 1e-9, f"comparison Cyprus row differs from the headline by {cy_check}"

    OUT.parent.mkdir(exist_ok=True)
    body = "% Generated by src/cvr/paper_numbers.py -- do not edit by hand.\n"
    body += "\n".join(f"\\newcommand{{\\{k}}}{{{v}}}" for k, v in mac.items()) + "\n"
    OUT.write_text(body)
    print(f"{len(mac)} macros -> {OUT}")


if __name__ == "__main__":
    main()
