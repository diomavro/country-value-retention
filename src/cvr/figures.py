"""Paper figures -> paper/figures/*.pdf (static, light mode).

Palette: dataviz reference categorical order (fixed, never cycled); grey is
reserved for 'unknown' buckets (confidential / unallocated) so they never read
as a country.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

P = Path("data/processed")
F = Path("paper/figures")
C = [
    "#2a78d6",
    "#eb6834",
    "#1baf7a",
    "#eda100",
    "#e87ba4",
    "#008300",
    "#4a3aa7",
    "#e34948",
]
GREY, INK, INK2, GRID = "#a3a29d", "#0b0b0b", "#52514e", "#e4e3df"
UNKNOWN = {
    "CONFIDENTIAL_PARTNERS",
    "WORLD_UNALLOCATED",
    "EU27_UNALLOCATED",
    "EXTRA_EU_UNALLOCATED",
    "ROW_FIGARO",
}

plt.rcParams.update(
    {
        "font.size": 9,
        "axes.edgecolor": INK2,
        "axes.labelcolor": INK,
        "xtick.color": INK2,
        "ytick.color": INK2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "legend.frameon": False,
        "pdf.fonttype": 42,
    }
)


def source_caption(fig, text, y=-0.06):
    """Source caption below the figure in figure coords (clear of xlabel, tight-bbox safe)."""
    fig.text(0.02, y, text, fontsize=7, color="#444444", ha="left", va="top")


def _theta() -> float:
    return float(pd.read_parquet(P / "headline_metrics.parquet").theta.iloc[0])


def _names() -> dict:
    from .export_web import INDUSTRY_NAMES, RECIPIENT_NAMES

    return {**INDUSTRY_NAMES, **RECIPIENT_NAMES}


def fig_official_vs_model():
    m = pd.read_parquet(P / "headline_metrics.parquet")
    c = pd.read_parquet(P / "comparators.parquet").set_index("year")
    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    ax.plot(
        m.year,
        100 * m.primary_income_outflow_to_gdp,
        color=C[1],
        lw=2,
        marker="o",
        ms=4,
        label="Official: all primary income paid abroad",
    )
    nonspe = 100 * c.fdi_income_paid_non_spe / m.set_index("year").gdp
    ax.plot(
        nonspe.index,
        nonspe.values,
        color=C[3],
        lw=2,
        marker="s",
        ms=4,
        label="Official: FDI income paid, SPEs excluded",
    )
    ax.plot(
        m.year,
        100 * m.foreign_value_leakage,
        color=C[0],
        lw=2,
        marker="o",
        ms=4,
        label="This study: income from Cypriot production accruing abroad",
    )
    ax.set_ylabel("% of GDP")
    ax.set_ylim(0, 185)
    ax.set_xticks(range(2010, 2024, 2))
    ax.axvline(2020.5, color=GREY, lw=1, ls=":")
    ax.annotate("FATS adds finance\n(series break)", xy=(2020.5, 60), xytext=(6, 0), textcoords="offset points", ha="left", fontsize=7, color=INK2)
    ax.legend(loc="upper left", fontsize=7.5)
    source_caption(
        fig,
        "Sources: CYSTAT sector accounts (S2); Eurostat bop_fdi6_inc, fats_activ, fats_g1a_08; author's calculations.",
    )
    return fig


def fig_mechanisms():
    t = pd.read_parquet(P / "recipient_tensor.parquet")
    f = t[t.mechanism != "retained_domestic"].pivot_table(
        index="year", columns="mechanism", values="value", aggfunc="sum", fill_value=0
    )
    order = [
        ("fdi_income", "Profits of foreign-owned firms"),
        ("fdi_debt_interest", "Interest to foreign parent companies"),
        ("compensation_nonresident", "Non-resident employees"),
        ("other_investment_income", "Other interest (loans, deposits)"),
        ("portfolio_income", "Portfolio income"),
        ("public_debt_interest", "Interest on public debt"),
        ("taxes_to_eu_institutions", "Taxes to EU institutions"),
    ]
    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    bottom = pd.Series(0.0, index=f.index)
    for i, (k, lab) in enumerate(order):
        if k not in f:
            continue
        ax.bar(
            f.index,
            f[k],
            bottom=bottom,
            color=C[i],
            width=0.75,
            label=lab,
            edgecolor="white",
            linewidth=0.8,
        )
        bottom += f[k]
    ax.set_ylabel("EUR million")
    ax.set_xticks(range(2010, 2024, 2))
    ax.axvline(2020.5, color=GREY, lw=1, ls=":")
    ax.legend(loc="upper left", fontsize=7.5, ncol=2)
    ax.set_ylim(0, bottom.max() * 1.45)
    source_caption(
        fig,
        f"Foreign value leakage by mechanism (central estimate, theta = {_theta():.2f}, statutory corporate tax). Dotted line: FATS scope break.",
    )
    return fig


def fig_recipients(year: int):
    t = pd.read_parquet(P / "recipient_tensor.parquet")
    names = _names()
    f = (
        t[(t.year == year) & (t.mechanism != "retained_domestic")]
        .groupby("recipient")
        .value.sum()
        .sort_values()
    )
    f = f[f > 5]
    fig, ax = plt.subplots(figsize=(6.3, 0.22 * len(f) + 0.8))
    colors = [GREY if r in UNKNOWN else C[0] for r in f.index]
    ax.barh([names.get(r, r) for r in f.index], f.values, color=colors, height=0.7)
    for y, v in enumerate(f.values):
        ax.text(v + f.max() * 0.01, y, f"{v:,.0f}", va="center", fontsize=7, color=INK2)
    ax.set_xlabel(f"EUR million, {year}")
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, f.max() * 1.15)
    source_caption(
        fig,
        "Grey bars: amounts whose recipient country is not published (confidential or only regional totals). Recipients > EUR 5m shown.",
        y=-0.02,
    )
    return fig


def fig_per_euro(year: int):
    pe = pd.read_parquet(P / "frame_b_per_euro.parquet")
    pe = pe[pe.year == year]
    sel = [
        ("I", "Restaurants & hotels"),
        ("G47", "Retail"),
        ("F", "Construction"),
        ("L68B", "Real estate"),
        ("K64", "Banking"),
        ("K65", "Insurance"),
        ("J61", "Telecoms"),
        ("D35", "Energy"),
        ("H49", "Land transport"),
        ("M69-70", "Professional services"),
        ("C10-12", "Food manufacturing"),
        ("J62-63", "IT services"),
    ]
    rows = []
    for k, lab in sel:
        g = pe[pe["product"] == k]
        rows.append(
            {
                "label": lab,
                "Cypriot value added, retained": g[
                    (g.channel == "domestic_value_added") & (g.recipient == "CY")
                ].value.sum(),
                "Taxes on inputs": g[
                    g.channel == "product_taxes_on_inputs"
                ].value.sum(),
                "Cypriot value added, accruing abroad": g[
                    (g.channel == "domestic_value_added") & (g.recipient != "CY")
                ].value.sum(),
                "Imported inputs": g[g.channel == "imported_inputs"].value.sum(),
            }
        )
    d = pd.DataFrame(rows).set_index("label").iloc[::-1]
    fig, ax = plt.subplots(figsize=(6.3, 3.6))
    left = pd.Series(0.0, index=d.index)
    for i, col in enumerate(d.columns):
        ax.barh(
            d.index,
            d[col],
            left=left,
            color=[C[0], C[2], C[1], C[6]][i],
            height=0.7,
            label=col,
            edgecolor="white",
            linewidth=0.8,
        )
        left += d[col]
    ax.set_xlim(0, 1)
    ax.set_xlabel(f"Share of one euro of final demand for Cypriot output, {year}")
    ax.grid(axis="y", visible=False)
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, 1.16), ncol=2, fontsize=7.5)
    source_caption(
        fig,
        "Leontief decomposition of CYSTAT symmetric input-output table; imported inputs by direct supplier (FIGARO).",
    )
    return fig


def fig_input_exposure():
    io = pd.read_parquet(P / "io_indicators.parquet")
    g = io.groupby("year").apply(
        lambda d: pd.Series(
            {
                "direct": d.imported_intermediates.sum()
                / (d.imported_intermediates.sum() + d.domestic_intermediates.sum()),
                "total": (d.total_import_content * d.final_demand_domestic_output).sum()
                / d.final_demand_domestic_output.sum(),
            }
        )
    )
    fig, ax = plt.subplots(figsize=(6.3, 2.8))
    ax.plot(
        g.index,
        100 * g.direct,
        color=C[0],
        lw=2,
        marker="o",
        ms=4,
        label="Imported share of intermediate inputs (direct)",
    )
    ax.plot(
        g.index,
        100 * g.total,
        color=C[1],
        lw=2,
        marker="s",
        ms=4,
        label="Import content of final demand for Cypriot output (total, via L)",
    )
    ax.set_ylabel("%")
    ax.set_ylim(0, 60)
    ax.legend(loc="upper left", fontsize=7.5)
    source_caption(
        fig,
        "Source: CYSTAT symmetric input-output tables 2010-2022 (0640050E, 0640055E); author's calculations.",
    )
    return fig


def fig_sensitivity():
    s = pd.read_parquet(P / "sensitivity.parquet")
    s = s[(~s.include_ofc) & (~s.consistent_scope) & (~s.banks_gross) & (~s.bop_upper) & (s.rho_basis == "d41_gross") & (s.year.isin([2022, 2023]))]
    fig, ax = plt.subplots(figsize=(6.3, 2.8))
    i = 0
    for y in (2022, 2023):
        for tax, ls in (("statutory", "-"), ("none", "--")):
            d = s[(s.year == y) & (s.tax == tax)].sort_values("theta")
            ax.plot(
                d.theta,
                100 * d.domestic_value_retention,
                color=C[i // 2],
                ls=ls,
                lw=2,
                marker="o",
                ms=4,
                label=f"{y}, corporate tax {'deducted' if tax == 'statutory' else 'not deducted'}",
            )
            i += 1
    th = _theta()
    ax.axvline(th, color=GREY, lw=1, ls=":")
    ax.annotate(
        f"central theta = {th:.2f}",
        xy=(th, 89.2),
        xytext=(-6, 0),
        textcoords="offset points",
        ha="right",
        fontsize=7,
        color=INK2,
    )
    ax.set_xlabel("theta: non-resident share of equity in foreign-controlled firms")
    ax.set_ylabel("Domestic value retention, %")
    ax.set_ylim(88.5, 96)
    ax.legend(loc="lower left", fontsize=7.5)
    source_caption(
        fig,
        "Frame A re-estimated over the parameter grid; other assumptions at central values.",
    )
    return fig


FIGURES = {
    "official_vs_model": fig_official_vs_model,
    "mechanisms": fig_mechanisms,
    "recipients_2023": lambda: fig_recipients(2023),
    "per_euro_2022": lambda: fig_per_euro(2022),
    "input_exposure": fig_input_exposure,
    "sensitivity": fig_sensitivity,
}


def main() -> None:
    F.mkdir(parents=True, exist_ok=True)
    for name, fn in FIGURES.items():
        fig = fn()
        fig.savefig(F / f"{name}.pdf", bbox_inches="tight")
        fig.savefig(F / f"{name}.png", bbox_inches="tight", dpi=130)
        plt.close(fig)
    print("figures:", ", ".join(FIGURES))


if __name__ == "__main__":
    main()
