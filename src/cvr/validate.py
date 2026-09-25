"""Validation suite over the processed database (brief §24).  Exit code 1 on any failure.

python -m cvr.validate
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .model import frame_a
from .model.ownership_data import load
from .ownership import build_graph
from .io_model import solve
from .model.suiot import build
from .provenance import require

P = Path("data/processed")

# Methodological breaks known in advance; detected jumps must be explained by one of these.
KNOWN_BREAKS = {
    2021: "FATS changes dataset (fats_g1a_08 -> fats_activ) and adds finance (K) and sections P-R; section J about doubles at the switch",
    2022: "Foreign-controlled surplus +59% (FATS 2022 vs 2021): observed, no method change identified; interpretation not verified",
    2023: "Observed in the BoP: FDI equity income paid by banks x4.4 (EUR 269m -> 1,198m, capped at K64 surplus in the consistent-scope series) and interest paid abroad by firms x3; coincides with the 2023 interest-rate rise (interpretation not verified)",
}


def _load(name: str) -> pd.DataFrame:
    return pd.read_parquet(P / f"{name}.parquet")


def checks() -> list[tuple[str, bool, str]]:
    out: list[tuple[str, bool, str]] = []

    def add(name, ok, detail=""):
        out.append((name, bool(ok), detail))

    t = _load("recipient_tensor")
    m = _load("headline_metrics")

    # 1. national-account identities
    tot = t.groupby("year")["value"].sum()
    gdp = m.set_index("year")["gdp"]
    gap = (tot - gdp).abs() / gdp
    add(
        "[identity] tensor sums to GDP every year",
        (gap < 1e-6).all(),
        f"max rel gap {gap.max():.2e}",
    )

    for y in sorted(t.year.unique()):
        na = frame_a.na_industry(int(y))
        by = (
            t[(t.year == y) & (t.industry != "_PRODUCT_TAXES")]
            .groupby("industry")["value"]
            .sum()
        )
        g = (by - na["B1G"].reindex(by.index)).abs().max()
        if g > 1e-6:
            add(f"{y}: industry rows sum to GVA", False, f"max gap {g:.4f}")
    add(
        "[identity] industry rows sum to GVA (all years)",
        not any("sum to GVA" in n and not ok for n, ok, _ in out),
    )

    # 2. no negative outflows; negative retained only where GVA itself is negative
    add(
        "no negative outflows", (t[t.mechanism != "retained_domestic"].value >= 0).all()
    )
    neg = t[(t.mechanism == "retained_domestic") & (t.value < 0)]
    unexplained = []
    for _, r in neg.iterrows():
        if (
            r.industry != "_PRODUCT_TAXES"
            and frame_a.na_industry(int(r.year)).loc[r.industry, "B1G"] >= 0
        ):
            unexplained.append((int(r.year), r.industry, round(r.value, 2)))
    add("no negative unexplained retained flows", not unexplained, str(unexplained[:5]))

    # 3. metric complements and bounds
    add(
        "[identity] DVR + FVL = 1",
        ((m.domestic_value_retention + m.foreign_value_leakage - 1).abs() < 1e-9).all(),
    )
    add("0 <= FVL <= 1", m.foreign_value_leakage.between(0, 1).all())

    # 4. Frame B: every euro exhausted; economy-wide domestic VA equals GVA (imports counted once)
    pe = _load("frame_b_per_euro")
    s = pe.groupby(["year", "product"])["value"].sum()
    add(
        "[identity] Frame B: each euro sums to 1",
        ((s - 1).abs() < 1e-9).all(),
        f"max gap {(s - 1).abs().max():.2e}",
    )
    ec = _load("frame_b_economy")
    io = _load("io_indicators")
    dva = ec[ec.channel == "domestic_value_added"].groupby("year")["value"].sum()
    gva = io.groupby("year")["gva"].sum()
    # Tolerance 0.1 EUR m: published final demand and output are each rounded to 0.001 EUR m
    # over 65 products, so the row identity x = Zd 1 + f holds only to a few hundredths.
    add(
        "[identity] Frame B: domestic VA of all final demand = GVA",
        ((dva - gva).abs() < 0.1).all(),
        f"max gap {(dva - gva).abs().max():.3f} EUR m",
    )
    imp = ec[ec.channel == "imported_inputs"].groupby("year")["value"].sum()
    imp_io = io.groupby("year")["imported_intermediates"].sum()
    add(
        "Frame B: imported inputs counted once (= total imported intermediates)",
        ((imp - imp_io).abs() < 0.1).all(),
        f"max gap {(imp - imp_io).abs().max():.3f} EUR m",
    )

    # 5. IO identities, recomputed here rather than trusted from the model run
    worst = 0.0
    for y in sorted(io.year.unique()):
        table, _, _ = build(int(y))
        r = solve(table, check=False)
        active = table.x > 0
        tot = (r.total_va_content + r.total_import_content + r.total_tax_content)[
            active
        ]
        worst = max(worst, float(abs(tot - 1).max()))
    add(
        "IO: VA + import + tax content = 1 (every product, every year)",
        worst < 1e-9,
        f"max gap {worst:.2e}",
    )
    add(
        "IO: direct import share within [0,1]",
        io.direct_foreign_input_exposure.between(0, 1).all(),
    )

    # 6. ownership
    e, d, _ = load()
    try:
        build_graph(e, d)
        add("ownership: no duplicate edges, shares <= 100%", True)
    except Exception as ex:  # noqa: BLE001
        add("ownership: no duplicate edges, shares <= 100%", False, str(ex))
    ou = _load("ownership_ultimate")
    ss = ou.groupby("entity_id")["share"].sum()
    add(
        "ownership: ultimate shares sum to 100% per firm", ((ss - 1).abs() < 1e-6).all()
    )

    # 7. reconciliation to official aggregates
    rec = _load("reconciliation")
    add(
        "reconciliation: all checks within tolerance",
        rec.passes.all(),
        rec.loc[~rec.passes, ["check", "year"]].to_string()
        if not rec.passes.all()
        else "",
    )

    # 8. provenance on every processed table
    for f in sorted(P.glob("*.parquet")):
        try:
            require(pd.read_parquet(f), f.stem)
        except Exception as ex:  # noqa: BLE001
            add(f"provenance: {f.stem}", False, str(ex))
    add(
        "provenance complete on all tables",
        not any(n.startswith("provenance:") for n, _, _ in out),
    )

    # 9. each mechanism against its own source, recomputed here from raw data (not trusted
    #    from the model run): these fail if an outflow is dropped, doubled or mis-scaled.
    sec = pd.read_parquet("data/interim/cystat/sector_accounts.parquet")
    sec = sec.pivot_table(index=["reference_year", "sector"], columns="item", values="value")
    fails = {"labour": [], "eu": [], "gov": [], "fats": [], "banks": []}
    for y in sorted(t.year.unique()):
        ty = t[t.year == y]
        mech = ty.groupby("mechanism").value.sum()
        s2 = sec.loc[(y, "S2")]
        ssc = frame_a._nasa_val(int(y), "S1", "D12") / frame_a._nasa_val(int(y), "S1", "D1")
        if abs(mech.get("compensation_nonresident", 0) - s2["D1REC"] * (1 - ssc)) > 0.01:
            fails["labour"].append(int(y))
        if abs(mech.get("taxes_to_eu_institutions", 0) - (0 if pd.isna(s2["D2REC"]) else s2["D2REC"])) > 0.01:
            fails["eu"].append(int(y))
        gov = sum(v for v in (frame_a._bop_raw(int(y), "S13", i, "DEB") for i in ("D41__O__FLA", "D41__P__F3")) if pd.notna(v))
        if abs(mech.get("public_debt_interest", 0) - gov) > 0.01:
            fails["gov"].append(int(y))
        # FATS: the pre-conversion base of all FATS rows equals the published foreign-controlled
        # total less owners' losses (sections or sub-codes with negative surplus)
        f = ty[(ty.mechanism == "fdi_income") & ty.gross_base.notna()]
        g = frame_a.fats_foreign_gos(int(y), na_level=frame_a.Params().fats_na_level)
        losses = float(-g["sections"].clip(upper=0).sum())
        diag = m.set_index("year").loc[y, "negative_fats_sections"]
        sub_losses = sum(-v for k, v in __import__("json").loads(diag).items() if len(k) > 1 and v < 0)
        # less what the finance NA-level rule removed, recomputed here from the raw FATS and national
        # accounts files (not taken from the model's own function)
        expect = g["total"] - _finance_level_removed(int(y))
        lo, hi = expect - 0.05, expect + losses + sub_losses + 0.05
        if not (lo <= f.gross_base.sum() <= hi):
            fails["fats"].append((int(y), round(f.gross_base.sum(), 1), round(expect, 1)))
        # banks counted exactly once: BoP bank FDI rows (no gross_base) only before 2021
        bop_bank = ty[(ty.mechanism == "fdi_income") & (ty.industry == "K64") & ty.gross_base.isna()]
        if (y >= 2021 and len(bop_bank)) or (y < 2021 and not len(bop_bank)):
            fails["banks"].append(int(y))
    stray = []
    for y in sorted(t.year.unique()):
        ty = t[t.year == y]
        has_fdi = set(ty[(ty.mechanism == "fdi_income") & ty.gross_base.notna()].industry)
        debt = set(ty[ty.mechanism == "fdi_debt_interest"].industry)
        if debt - has_fdi:
            stray.append((int(y), sorted(debt - has_fdi)[:3]))
    add("intra-group interest only on industries with foreign-controlled surplus", not stray, str(stray[:3]))
    # FATS rows and intra-group interest recomputed from raw nasa_10_nf_tr, statutory tax and the
    # recorded theta (independent of the model's helper functions)
    import glob

    nasa = pd.concat([pd.read_parquet(f) for f in glob.glob("data/raw/eurostat/nasa_10_nf_tr__geo-CY*.parquet")])
    nasa = nasa[nasa.unit == "CP_MEUR"]

    def nv(y, sec_, item, direct="PAID"):
        x = nasa[(nasa.TIME_PERIOD.astype(int) == y) & (nasa.sector == sec_) & (nasa.na_item == item) & (nasa.direct == direct)].OBS_VALUE
        return float(x.iloc[0])

    bop = pd.concat([pd.read_parquet(f) for f in glob.glob("data/raw/eurostat/bop_c6_a__*.parquet")])
    mis_fats, mis_debt = [], []
    mt = m.set_index("year")
    for y in sorted(t.year.unique()):
        y = int(y)
        g11 = nv(y, "S11", "B2A3G")
        c, cf = nv(y, "S11", "P51C") / g11, nv(y, "S12", "P51C") / nv(y, "S12", "B2A3G")
        rho = nv(y, "S11", "D41") / g11  # central basis: S11 interest paid, gross
        tau = 0.10 if y <= 2012 else 0.125
        th = float(mt.loc[y, "theta"])
        capped = set(__import__("json").loads(mt.loc[y, "capped_industries"]))
        ty = t[(t.year == y) & (t.mechanism == "fdi_income") & t.gross_base.notna() & ~t.industry.isin(capped)]
        keep = ty.industry.str.startswith("K").map({True: 1 - cf, False: 1 - c - rho}).clip(lower=0)
        exp = ty.gross_base * keep * (1 - tau) * th
        if (exp - ty.value).abs().max() > 1e-6:
            mis_fats.append((y, round(float((exp - ty.value).abs().max()), 3)))
        b = bop[(bop.sector10 == "S1V") & (bop.sectpart == "S1") & (bop.bop_item == "D41__D__FLA") & (bop.stk_flow == "DEB") & (bop.partner == "WRL_REST") & (bop.TIME_PERIOD.astype(int) == y)].OBS_VALUE.dropna()
        if len(b):
            s_share = min(float(b.iloc[0]) / nv(y, "S11", "D41"), 1.0)
            nonfin = t[(t.year == y) & (t.mechanism == "fdi_income") & t.gross_base.notna() & ~t.industry.str.startswith("K")].gross_base.sum()
            exp_debt = min(float(b.iloc[0]), s_share * rho * nonfin)
            got = t[(t.year == y) & (t.mechanism == "fdi_debt_interest")].value.sum()
            if abs(exp_debt - got) > 0.01 and not capped:
                mis_debt.append((y, round(exp_debt, 1), round(got, 1)))
    # banks' non-FDI interest = max(paid - received, 0) from raw BoP; households' share of
    # S1V loan interest on imputed rent = S14_S15 D41 / (S14_S15 + S11 D41), from raw nasa
    items = ("D41__O__FLA", "D41__P__F3", "D42__P__F51", "D44P__O__F6")
    mis_bank, mis_hh = [], []

    def braw(y, sec_, item, flow):
        x = bop[(bop.sector10 == sec_) & (bop.sectpart == "S1") & (bop.bop_item == item) & (bop.stk_flow == flow) & (bop.partner == "WRL_REST") & (bop.TIME_PERIOD.astype(int) == y)].OBS_VALUE.dropna()
        return float(x.iloc[0]) if len(x) else 0.0

    for y in sorted(t.year.unique()):
        y = int(y)
        ty = t[t.year == y]
        net = sum(braw(y, "S122", i, "DEB") for i in items) - sum(braw(y, "S122", i, "CRE") for i in items)
        got = ty[(ty.mechanism == "other_investment_income") & (ty.industry == "K64")].value.sum()
        if abs(max(net, 0.0) - got) > 0.01:
            mis_bank.append((y, round(max(net, 0.0), 1), round(got, 1)))
        hh = nv(y, "S14_S15", "D41")
        share = hh / (hh + nv(y, "S11", "D41"))
        loan = braw(y, "S1V", "D41__O__FLA", "DEB")
        got_hh = ty[(ty.mechanism == "other_investment_income") & (ty.industry == "L68A")].value.sum()
        if abs(share * loan - got_hh) > 0.01:
            mis_hh.append((y, round(share * loan, 1), round(got_hh, 1)))
    # creditor share recomputed (firms and banks only) and fitted-cell flags vs raw FATS suppression
    mis_cred, mis_flag = [], []
    for y in sorted(t.year.unique()):
        y = int(y)
        ty = t[t.year == y]
        cred = ty[ty.mechanism.isin(["other_investment_income", "portfolio_income"]) & (ty.industry != "L68A")].value.sum()
        nos = nv(y, "S11", "B2A3G") - nv(y, "S11", "P51C")
        if abs(cred / nos - float(mt.loc[y, "foreign_creditor_income_share_of_nos"])) > 1e-9:
            mis_cred.append(y)
        cells = frame_a.fats_foreign_gos(y)["cells"]
        f = ty[(ty.mechanism == "fdi_income") & ty.gross_base.notna() & (ty.recipient != "CONFIDENTIAL_PARTNERS")]
        for r in f.itertuples():
            sec_ = r.industry[0]
            suppressed = r.recipient not in cells.columns or sec_ not in cells.index or pd.isna(cells.loc[sec_, r.recipient])
            flagged = "cell suppressed" in r.methodology
            if suppressed != flagged or (flagged and r.confidence_level != "low"):
                mis_flag.append((y, r.industry, r.recipient))
    add("source: creditor share = firms' and banks' interest abroad / S11 NOS", not mis_cred, str(mis_cred[:3]))
    add("fitted-cell flag and low confidence exactly where the FATS cell is suppressed", not mis_flag, str(mis_flag[:3]))
    add("source: banks' interest = max(BoP paid - received, 0)", not mis_bank, str(mis_bank[:3]))
    add("source: households' loan interest on imputed rent = their D41 share x S1V loan interest", not mis_hh, str(mis_hh[:3]))
    add("source: every FATS row = base x (1 - CFC - interest) x (1 - tau) x theta (raw S11/S12 ratios)", not mis_fats, str(mis_fats[:3]))
    from .model.ownership_data import theta_central

    th_cal = round(theta_central(), 3)
    add("theta used = theta recalibrated from the company layer", bool((mt["theta"] - th_cal).abs().max() < 1e-9), f"used {sorted(set(mt['theta']))}, calibrated {th_cal}")
    add("source: intra-group interest = min(BoP FDI debt interest, s x interest deducted)", not mis_debt, str(mis_debt[:3]))
    add("source: non-resident pay = S2 D1 x (1 - employer SSC share)", not fails["labour"], str(fails["labour"]))
    add("source: EU taxes = S2 D2", not fails["eu"], str(fails["eu"]))
    add("source: public-debt interest = BoP S13 interest paid", not fails["gov"], str(fails["gov"]))
    add("source: FATS base of foreign-owned profit = published FATS total (less losses)", not fails["fats"], str(fails["fats"]))
    add("source: foreign-owned banks counted once (BoP before 2021, FATS K from 2021)", not fails["banks"], str(fails["banks"]))
    br = _load("bridge")
    gaps = []
    for y, x in br.groupby("year"):
        body, tot = x[x.line != "Total"], x[x.line == "Total"]
        if abs(body.official.sum() - tot.official.iloc[0]) > 2 or abs(body.model.sum() - tot.model.iloc[0]) > 0.5:
            gaps.append(int(y))
    add("bridge: official lines add up to official outflow; model lines to model outflow", not gaps, str(gaps))

    # 10. time-series breaks: large jumps in the FDI mechanism must match a documented break
    flagged, undocumented = [], []
    cons = _load("headline_metrics_consistent_scope").set_index("year")
    for name, fdi in (
        ("central", t[t.mechanism == "fdi_income"].groupby("year")["value"].sum()),
        ("consistent scope", cons["foreign_value_leakage"] * cons["gdp"]),
    ):
        jumps = fdi.pct_change().abs()
        for y, v in jumps.items():
            if v > 0.5:
                flagged.append(f"{name} {int(y)}")
                if int(y) not in KNOWN_BREAKS:
                    undocumented.append(f"{name} {int(y)}")
    add(
        "time-series breaks identified and documented",
        not undocumented,
        f"jumps >50% in foreign-owned surplus: {flagged}; undocumented: {undocumented} (each must have a KNOWN_BREAKS entry)",
    )
    return out


def _finance_level_removed(y: int) -> float:
    """Foreign-controlled finance surplus above the national-accounts level, from raw files."""
    if y < 2021 or not frame_a.Params().fats_na_level:
        return 0.0
    d = frame_a._one("fats_activ__*.parquet")
    d = d[(d.TIME_PERIOD.astype(int) == y) & (d.indic_sbs == "GOS_MEUR") & (d.nace_r2 == "K")].set_index("c_ctrl")["OBS_VALUE"]
    world, foreign = d.get("WORLD", float("nan")), d.get("WRL_REST", float("nan"))
    n = frame_a._nama()
    n = n[(n.TIME_PERIOD == y) & n.nace_r2.isin(["K64", "K65", "K66"]) & n.na_item.isin(["B2A3N", "P51C"])]
    na_k = float(n.OBS_VALUE.sum())
    if not (world > na_k > 0) or pd.isna(foreign):
        return 0.0
    return float(foreign) * (1 - na_k / world)


def main() -> int:
    res = checks()
    width = max(len(n) for n, _, _ in res)
    for name, ok, detail in res:
        print(f"{'PASS' if ok else 'FAIL'}  {name:<{width}}  {detail}")
    failed = [n for n, ok, _ in res if not ok]
    print(f"\n{len(res) - len(failed)}/{len(res)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
