"""Write paper/tables/*.tex from processed data (booktabs, no hand-typed numbers)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .export_web import RECIPIENT_NAMES
from .accounts import industry_ownership_capture
from .model.frame_a import na_industry

P = Path("data/processed")
T = Path("paper/tables")

# Industries named in the brief (§12), in the brief's order, then the largest others.
BRIEF = [
    ("I", "Restaurants and accommodation"),
    ("G47", "Retail"),
    ("K64", "Banking"),
    ("K65", "Insurance"),
    ("J61", "Telecommunications"),
    ("D35", "Energy"),
    ("H49", "Land transport"),
    ("H50", "Water transport (shipping)"),
    ("F", "Construction"),
    ("L68B", "Real estate (market)"),
    ("M69-70", "Professional services"),
    ("C10-12", "Manufacturing: food"),
    ("J62-63", "Technology (IT services)"),
    ("J58", "Publishing incl. software"),
    ("K66", "Auxiliary financial services"),
    ("G46", "Wholesale trade"),
]


def _tex(s: str) -> str:
    return s.replace("&", "\\&").replace("%", "\\%").replace("_", "\\_")


def pc(x) -> str:
    return "--" if x is None or pd.isna(x) else f"{100 * x:.1f}"


def industries() -> str:
    t = pd.read_parquet(P / "recipient_tensor.parquet")
    io = pd.read_parquet(P / "io_indicators.parquet")
    m = pd.read_parquet(P / "headline_metrics.parquet").set_index("year")
    L, IOL = int(t.year.max()), int(io.year.max())
    na = na_industry(L)
    tl = t[t.year == L]
    foc = industry_ownership_capture(tl, na["B2A3N"], m.loc[L, "cfc_ratio_nonfin"], m.loc[L, "cfc_ratio_fin"], m.loc[L, "theta"])
    iol = io[io.year == IOL].set_index("product")
    rows = []
    for k, lab in BRIEF:
        f = tl[(tl.industry == k) & (tl.mechanism != "retained_domestic")]
        gva = na.loc[k, "B1G"]
        rows.append(
            f"{_tex(lab)} & {gva:,.0f} & {pc(iol.loc[k, 'direct_foreign_input_exposure'])} & {pc(iol.loc[k, 'total_import_content'])} & "
            f"{pc(foc.get(k))} & {pc(1 - f.value.sum() / gva if gva > 0 else None)} \\\\"
        )
    return (
        "\\begin{table}[!htbp]\n\\centering\n\\small\n"
        f"\\caption{{Industry decomposition: GVA and retention {L}; input exposure {IOL}}}\n\\label{{tab:industries}}\n"
        "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{0.30\\textwidth}rrrrr}\n\\toprule\n"
        f"Industry & GVA {L} & \\multicolumn{{2}}{{c}}{{Input exposure {IOL}}} & Foreign & Domestic \\\\\n"
        f" & EUR m & direct & total & own. {L} & retention {L} \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n\n\\smallskip\n\\begin{minipage}{0.95\\textwidth}\\footnotesize\n"
        "Notes: percentages. Direct foreign input exposure = imported share of the industry's intermediate inputs. Total = imports embodied in one euro of final demand for the product, through the whole supply chain (Leontief inverse); the two have different denominators and are not comparable by subtraction. "
        "Foreign ownership capture = foreign-owned net operating surplus before interest and corporate tax (FATS, after corporate depreciation, times theta) as a share of the industry's net operating surplus, which also includes self-employed income. "
        "Domestic retention = share of the industry's GVA accruing to residents. "
        "From 2021 FATS publishes finance (K), trade (G) and most of transport (H) only at section level, so industries within these sections share one foreign share. "
        "Recipient countries are not shown by industry: FATS publishes the ultimate controlling economy mostly for whole sections, so industry-by-country cells are fitted, not observed (see the dashboard, flagged low confidence).\n"
        "\\end{minipage}\n\\end{table}\n"
    )


def bridge() -> str:
    b = pd.read_parquet(P / "bridge.parquet")
    L = int(b.year.max())
    x = b[b.year == L]
    rows = "\n".join(
        f"{_tex(r.line)} & {r.official:,.0f} & {r.model:,.0f} & {_tex(r.explanation)} \\\\" if pd.notna(r.official) else f"{_tex(r.line)} & n.p. & {r.model:,.0f} & {_tex(r.explanation)} \\\\"
        for r in x.itertuples()
    )
    return (
        "\\begin{table}[!htbp]\n\\centering\n\\footnotesize\n"
        f"\\caption{{From the official outflow to this study's estimate, {L} (EUR m)}}\n\\label{{tab:bridge}}\n"
        "\\setlength{\\tabcolsep}{3pt}\n"
        "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{0.34\\textwidth}rr>{\\raggedright\\arraybackslash}p{0.40\\textwidth}}\n\\toprule\n"
        "Line (resident sector paying) & Official & This study & Reason for the difference \\\\\n\\midrule\n"
        + rows
        + "\n\\bottomrule\n\\end{tabular}\n\n\\smallskip\n\\begin{minipage}{0.95\\textwidth}\\footnotesize Notes: official = CYSTAT rest-of-world account (D1, D2, D4 received by the rest of the world) and the balance of payments by paying resident sector (Eurostat bop\\_c6\\_a). The official lines add up to the official total in every year 2010--2023; the full series is in \\texttt{data/processed/bridge.parquet}.\\end{minipage}\n\\end{table}\n"
    )


def interest_ratios() -> str:
    r = pd.read_parquet(P / "interest_ratios.parquet")
    rows = "\n".join(
        f"{int(x.year)} & {x.cfc_nonfin:.2f} & {x.rho_d41_gross:.2f} & {x.rho_d41_net:.2f} & {x.rho_d41g_gross:.2f} & {x.intra_group_share:.2f} \\\\" for x in r.itertuples()
    )
    return (
        "\\begin{table}[!htbp]\n\\centering\n\\small\n\\caption{Depreciation, interest and intra-group share per euro of non-financial corporations' surplus}\n\\label{tab:rho}\n"
        "\\begin{tabular}{lrrrrr}\n\\toprule\nYear & $c$ & $\\rho$ (central) & $\\rho$ net & $\\rho$ pre-FISIM & $s$ \\\\\n\\midrule\n"
        + rows
        + "\n\\bottomrule\n\\end{tabular}\n\n\\smallskip\n\\begin{minipage}{0.9\\textwidth}\\footnotesize Notes: ratios to S11 gross operating surplus (Eurostat \\texttt{nasa\\_10\\_nf\\_tr}). Central $\\rho$ = interest paid after the FISIM adjustment; net = paid minus received; pre-FISIM = actual interest paid. $s$ = FDI debt interest paid by firms and households (BoP) / S11 interest paid.\\end{minipage}\n\\end{table}\n"
    )


COUNTRY_NAMES = {"CY": "Cyprus", "IE": "Ireland", "LU": "Luxembourg", "NL": "Netherlands", "EL": "Greece", "PT": "Portugal"}
MECH_SHORT = {
    "share_compensation_nonresident": "non-resident employees",
    "share_fdi_income": "foreign-owned profit",
    "share_fdi_debt_interest": "intra-group interest",
    "share_other_investment_income": "loan and deposit interest",
    "share_portfolio_income": "portfolio income",
    "share_public_debt_interest": "public debt interest",
    "share_taxes_to_eu_institutions": "taxes to EU",
}


def comparison(years=(2015, 2019, 2023)) -> str:
    r = pd.read_parquet(P / "comparison.parquet")
    c = r[r.variant == "theta_cyprus"].set_index(["geo", "year"])
    one = r[r.variant == "theta_1"].set_index(["geo", "year"])
    last = max(years)

    def cell(frame, g, y, col="domestic_value_retention"):
        return pc(frame.loc[(g, y), col]) if (g, y) in frame.index else "--"

    rows = []
    for g, name in COUNTRY_NAMES.items():
        if (g, last) in c.index:
            x = c.loc[(g, last)]
            m = max(MECH_SHORT, key=lambda k: x.get(k, 0.0))
            top = f"{MECH_SHORT[m]} ({pc(x[m])})"
        else:
            top = "--"
        rows.append(
            f"{name} & " + " & ".join(cell(c, g, y) for y in years) + f" & {cell(one, g, last)} & {cell(c, g, last, 'primary_income_outflow_to_gdp')} & {top} \\\\"
        )
    skipped = pd.read_parquet(P / "comparison_skipped.parquet")
    miss = "; ".join(f"{COUNTRY_NAMES.get(g, g)} {', '.join(str(y) for y in sorted(v) if y in years)}" for g, v in skipped[skipped.year.isin(years)].groupby("geo").year if g != "MT")
    head = " & ".join(str(y) for y in years)
    mt = skipped[skipped.geo == "MT"]
    malta = f"Malta is omitted in every year ({_tex(mt.reason.iloc[0])}). " if len(mt) == r.year.nunique() else ""
    shown_rows = c[c.index.get_level_values("year").isin(years)].reset_index()
    shown_rows = shown_rows[shown_rows.missing_lines != ""]
    lines = shown_rows.assign(line=shown_rows.missing_lines.str.split("; ")).explode("line")
    parts = []
    for g, grp in lines.groupby("geo", sort=False):  # each country once, each line with its years
        if g not in COUNTRY_NAMES:
            continue
        items = [f"{line} ({', '.join(str(y) for y in sorted(ly.year))})" for line, ly in grp.groupby("line", sort=False)]
        parts.append(f"{COUNTRY_NAMES[g]}: {', '.join(items)}")
    gaps = "; ".join(parts) or "none"
    return (
        "\\begin{table}[!htbp]\n\\centering\n\\small\n\\caption{Domestic value retention in Cyprus and five EU economies (\\% of GDP)}\n\\label{tab:comparison}\n"
        "\\begin{tabular}{lrrrrr>{\\raggedright\\arraybackslash}p{0.27\\textwidth}}\n\\toprule\n"
        f" & \\multicolumn{{{len(years)}}}{{c}}{{Retention, Cyprus $\\theta$}} & $\\theta=1$ & Official & Largest outflow \\\\\n"
        f"\\cmidrule(lr){{2-{len(years) + 1}}}\n"
        f"Country & {head} & {last} & outflow {last} & line, {last} \\\\\n\\midrule\n"
        + "\n".join(rows)
        + "\n\\bottomrule\n\\end{tabular}\n\n\\smallskip\n\\begin{minipage}{0.95\\textwidth}\\footnotesize Notes: Frame A with the Cyprus method; other countries from Eurostat (\\texttt{nasa\\_10\\_nf\\_tr}, \\texttt{nama\\_10\\_a64}, FATS, \\texttt{bop\\_c6\\_a}, \\texttt{bop\\_rem6}) and OECD statutory tax rates. "
        "$\\theta$ is calibrated for Cyprus only and assumed elsewhere; $\\theta=1$ gives the lowest retention. Official outflow: primary income paid abroad (S2), which includes pass-through income. "
        f"-- = inputs suppressed ({_tex(miss) if miss else 'none'}). {malta}"
        "From 2021 FATS covers finance; before, foreign-owned banks' profit comes from the balance of payments, so columns before and after 2021 differ in scope. "
        f"Suppressed balance-of-payments items are omitted (a suppressed bank receipt is not netted): {_tex(gaps)}.\\end{{minipage}}\n\\end{{table}}\n"
    )


def data_appendix() -> str:
    cat = pd.read_csv("data_catalogue.csv")
    g = cat.groupby("provider").agg(n=("dataset", "size")).reset_index()
    rows = "\n".join(f"{_tex(r.provider)} & {r.n} \\\\" for r in g.itertuples())
    return (
        "Every dataset is listed in \\texttt{data\\_catalogue.csv} with provider, URL, reference period, publication and download dates, licence, scope, resolution, variables, processing script and SHA-256 checksum. "
        "Raw files are not redistributed; \\texttt{make ingest} downloads them again, and checksums confirm that the same vintage is used.\n\n"
        "\\begin{table}[h]\n\\centering\n\\small\n\\caption{Datasets in the catalogue by provider}\n\\label{tab:catalogue}\n"
        "\\begin{tabular}{lr}\n\\toprule\nProvider & Datasets \\\\\n\\midrule\n"
        + rows
        + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )


def reconciliation() -> str:
    r = pd.read_parquet(P / "reconciliation.parquet")
    g = (
        r.groupby("check")
        .agg(
            years=("year", lambda s: f"{s.min()}--{s.max()}"),
            maxabs=("pct_difference", lambda s: s.abs().max()),
            tol=("tolerance_pct", "first"),
            ok=("passes", "all"),
        )
        .reset_index()
    )
    rows = "\n".join(
        f"{_tex(x.check)} & {x.years} & {x.maxabs:.4f} & {x.tol:.2f} & {'\\checkmark' if x.ok else '$\\times$'} \\\\"
        for x in g.itertuples()
    )
    return (
        "\\begin{table}[h]\n\\centering\n\\small\n\\caption{Reconciliation with official aggregates}\n\\label{tab:recon}\n"
        "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{0.5\\textwidth}lrrc}\n\\toprule\nCheck & Years & Max $|$diff.$|$ \\% & Tol. \\% & Pass \\\\\n\\midrule\n"
        + rows
        + "\n\\bottomrule\n\\end{tabular}\n\n\\smallskip\n\\begin{minipage}{0.9\\textwidth}\\footnotesize Notes: official values from CYSTAT annual national accounts (April 2026 vintage) and sector accounts; model values from the input--output tables and the recipient accounting. Residuals are reported, not forced to zero.\\end{minipage}\n\\end{table}\n"
    )


def validation() -> str:
    from .validate import checks

    res = checks()
    rows = "\n".join(
        f"{{}}{_tex(n)} & {'\\checkmark' if ok else '$\\times$'} \\\\" for n, ok, _ in res
    )
    return (
        "The validation suite (\\texttt{python -m cvr.validate}) runs after every model build and exits with an error if any check fails. "
        f"In this release {sum(ok for _, ok, _ in res)} of {len(res)} checks pass; unit tests add further guards on synthetic data.\n\n"
        "\\begin{table}[h]\n\\centering\n\\small\n\\caption{Automated validation checks}\n\\label{tab:validation}\n"
        "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{0.75\\textwidth}c}\n\\toprule\nCheck & Pass \\\\\n\\midrule\n"
        + rows
        + "\n\\bottomrule\n\\end{tabular}\n\\end{table}\n"
    )


def main() -> None:
    T.mkdir(parents=True, exist_ok=True)
    (T / "industries.tex").write_text(industries())
    (T / "data_appendix.tex").write_text(data_appendix())
    (T / "reconciliation.tex").write_text(reconciliation())
    (T / "bridge.tex").write_text(bridge())
    (T / "interest_ratios.tex").write_text(interest_ratios())
    (T / "validation.tex").write_text(validation())
    (T / "comparison.tex").write_text(comparison())
    print("tables written")


if __name__ == "__main__":
    main()
