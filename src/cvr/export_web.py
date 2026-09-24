"""Export processed tables to static JSON for the website (website/public/data/cy/...).

Every number exported carries its provenance so the dashboard can show a
source/methodology tooltip and drill down (brief §20-21).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from .accounts import industry_ownership_capture
from .model.frame_a import na_industry
from .model.ownership_data import load
from .model.suiot import available_years, build

P = Path("data/processed")
W = Path("website/public/data/cy")
PROV = ["status", "methodology", "source", "source_url", "confidence_level"]

INDUSTRY_NAMES = {
    "A01": "Agriculture",
    "A02": "Forestry",
    "A03": "Fishing",
    "B": "Mining and quarrying",
    "C10-12": "Food, beverages, tobacco",
    "C13-15": "Textiles and apparel",
    "C16": "Wood products",
    "C17": "Paper",
    "C18": "Printing",
    "C19": "Refined petroleum",
    "C20": "Chemicals",
    "C21": "Pharmaceuticals",
    "C22": "Rubber and plastics",
    "C23": "Non-metallic minerals (cement)",
    "C24": "Basic metals",
    "C25": "Fabricated metals",
    "C26": "Electronics",
    "C27": "Electrical equipment",
    "C28": "Machinery",
    "C29": "Motor vehicles",
    "C30": "Other transport equipment",
    "C31-32": "Furniture, other manufacturing",
    "C33": "Repair and installation",
    "D35": "Energy (electricity, gas)",
    "E36": "Water supply",
    "E37-39": "Sewerage and waste",
    "F": "Construction",
    "G45": "Motor trade",
    "G46": "Wholesale trade",
    "G47": "Retail trade",
    "H49": "Land transport",
    "H50": "Water transport (shipping)",
    "H51": "Air transport",
    "H52": "Warehousing, transport support",
    "H53": "Postal and courier",
    "I": "Accommodation and restaurants",
    "J58": "Publishing (incl. software)",
    "J59-60": "Film, TV, broadcasting",
    "J61": "Telecommunications",
    "J62-63": "IT and information services (technology)",
    "K64": "Banking",
    "K65": "Insurance",
    "K66": "Auxiliary financial services",
    "L68A": "Imputed rent of owner-occupied housing",
    "L68B": "Real estate (market)",
    "M69-70": "Legal, accounting, management consulting",
    "M71": "Architecture and engineering",
    "M72": "Research and development",
    "M73": "Advertising",
    "M74-75": "Other professional services",
    "N77": "Rental and leasing",
    "N78": "Employment services",
    "N79": "Travel agencies",
    "N80-82": "Security, building, office support",
    "O84": "Public administration",
    "P85": "Education",
    "Q86": "Health",
    "Q87-88": "Social work",
    "R90-92": "Arts, gambling",
    "R93": "Sports, recreation",
    "S94": "Membership organisations",
    "S95": "Repair of household goods",
    "S96": "Other personal services",
    "T": "Households as employers",
    "U": "Extraterritorial organisations",
    "_PRODUCT_TAXES": "Taxes less subsidies on products",
}

RECIPIENT_NAMES = {
    "CY": "Cyprus (retained)",
    "EL": "Greece",
    "US": "United States",
    "UK": "United Kingdom",
    "OFFSHO": "Offshore financial centres",
    "EU_INST": "EU institutions",
    "CONFIDENTIAL_PARTNERS": "Confidential (not published by country)",
    "WORLD_UNALLOCATED": "Rest of world (not allocated by country)",
    "EU27_UNALLOCATED": "EU27 (not allocated by country)",
    "EXTRA_EU_UNALLOCATED": "Outside EU (not allocated by country)",
    "ROW_FIGARO": "Rest of world (FIGARO residual)",
    "RU": "Russia",
    "DE": "Germany",
    "LU": "Luxembourg",
    "CA": "Canada",
    "FR": "France",
    "IE": "Ireland",
    "NL": "Netherlands",
    "IL": "Israel",
    "CH": "Switzerland",
    "IT": "Italy",
    "SE": "Sweden",
    "MT": "Malta",
    "IN": "India",
    "TR": "Turkey",
    "CN": "China",
    "AE": "United Arab Emirates",
    "TN": "Tunisia",
    "AL": "Albania",
    "AR": "Argentina",
    "AT": "Austria",
    "AU": "Australia",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "BR": "Brazil",
    "CZ": "Czechia",
    "DK": "Denmark",
    "EE": "Estonia",
    "EG": "Egypt",
    "ES": "Spain",
    "FI": "Finland",
    "HK": "Hong Kong",
    "HR": "Croatia",
    "HU": "Hungary",
    "ID": "Indonesia",
    "JP": "Japan",
    "KR": "South Korea",
    "LT": "Lithuania",
    "LV": "Latvia",
    "ME": "Montenegro",
    "MK": "North Macedonia",
    "MX": "Mexico",
    "NO": "Norway",
    "PH": "Philippines",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "RS": "Serbia",
    "SA": "Saudi Arabia",
    "SI": "Slovenia",
    "SK": "Slovakia",
    "ZA": "South Africa",
    "LI": "Liechtenstein",
    "IS": "Iceland",
    "NZ": "New Zealand",
    "CN_X_HK": "China (excl. Hong Kong)",
}

CYSTAT_URL = "https://cystatdb.cystat.gov.cy/pxweb/en/8.CYSTAT-DB/"
ES = "https://ec.europa.eu/eurostat/databrowser/view/{}/default/table"

# Provenance of each headline measure: the single source for the dashboard's tooltips
# (written to website/src/generated/metric_meta.json and imported at build time).
METRIC_META = {
    "gdp": {
        "status": "observed",
        "confidence_level": "high",
        "source": "CYSTAT sector accounts 0630030E (S1 B1GQ); equal to annual national accounts 0610010E",
        "source_url": CYSTAT_URL,
        "methodology": "Gross domestic product at current prices, EUR million, as published.",
    },
    "domestic_value_retention": {
        "status": "estimated",
        "confidence_level": "medium",
        "source": "Model output (Frame A): national accounts (nama_10_a64, CYSTAT sector accounts), FATS, balance of payments (bop_c6_a, bop_rem6)",
        "source_url": " ; ".join(
            [CYSTAT_URL, ES.format("fats_activ"), ES.format("bop_c6_a")]
        ),
        "methodology": "Retained value / GDP (an upper bound: unmeasured outflows count as retained). Outflows: profits of foreign-owned firms (FATS operating surplus of foreign-controlled firms after corporate depreciation, interest and Cypriot corporate tax, x theta), interest to foreign parents (BoP, capped), other interest and portfolio income paid by firms, households and banks (BoP, banks net), government external interest, pay to non-resident workers net of employer social contributions, taxes to EU institutions. Income of non-bank financial corporations (S12M, where SPEs sit) is excluded. Each outflow is bounded by the income component it is drawn from.",
        "note": "Depends on theta and the tax assumption; see the sensitivity table on the Data page.",
    },
    "foreign_value_leakage": {
        "status": "estimated",
        "confidence_level": "medium",
        "source": "Model output (Frame A): sum of all non-retained rows of the flow table",
        "source_url": " ; ".join(
            [CYSTAT_URL, ES.format("fats_activ"), ES.format("bop_c6_a")]
        ),
        "methodology": "FVL = 1 - DVR: income generated by Cypriot production accruing to non-residents / GDP. Excludes SPE pass-through.",
    },
    "foreign_input_exposure": {
        "status": "modelled",
        "confidence_level": "high",
        "source": "CYSTAT symmetric input-output tables 0640050E / 0640055E",
        "source_url": CYSTAT_URL,
        "methodology": "Imported / (imported + domestic) intermediate inputs, all industries. Imports are not part of GDP, so this is never added to leakage. Last input-output year: 2022.",
    },
    "foreign_ownership_capture": {
        "status": "estimated",
        "confidence_level": "medium",
        "source": "Eurostat FATS (fats_activ / fats_g1a_08); nasa_10_nf_tr",
        "source_url": " ; ".join([ES.format("fats_activ"), ES.format("nasa_10_nf_tr")]),
        "methodology": "theta x net operating surplus of foreign-controlled non-financial firms (FATS sections B-N, after S11 depreciation; before interest and tax) / net operating surplus of non-financial corporations (S11). Finance and sections P-R are excluded because FATS covers them only from 2021.",
        "note": "Depends on theta; see the sensitivity table on the Data page.",
    },
    "foreign_creditor_income_share_of_nos": {
        "status": "estimated",
        "confidence_level": "low",
        "source": "Eurostat bop_c6_a; nasa_10_nf_tr",
        "source_url": ES.format("bop_c6_a"),
        "methodology": "Interest and portfolio income paid to non-residents by firms and banks (non-FDI; households' mortgage interest excluded) / net operating surplus of non-financial corporations (S11).",
    },
    "foreign_labour_income_share": {
        "status": "estimated",
        "confidence_level": "high",
        "source": "CYSTAT sector accounts 0630030E (S2 D1); Eurostat bop_rem6 for the partner split",
        "source_url": " ; ".join([CYSTAT_URL, ES.format("bop_rem6")]),
        "methodology": "Compensation received by the rest of the world (S2 D1) net of employers' social contributions (which go to Cypriot social insurance) / total compensation of employees.",
    },
    "official_primary_income_outflow_to_gdp": {
        "status": "modelled",
        "confidence_level": "high",
        "source": "CYSTAT sector accounts 0630030E (rest of the world, S2); ratio to GDP computed",
        "source_url": CYSTAT_URL,
        "methodology": "Compensation (D1) + taxes on production (D2) + property income (D4) received by the rest of the world, / GDP. Includes pass-through income of special purpose entities.",
    },
    "fdi_income_paid_non_spe": {
        "status": "modelled",
        "confidence_level": "high",
        "source": "Eurostat bop_fdi6_inc (DI__D4P__D__F, debit, world); non-SPE = TOTAL - SPE",
        "source_url": ES.format("bop_fdi6_inc"),
        "methodology": "Official BoP; blank where Eurostat marks a cell confidential.",
    },
}


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return None if not np.isfinite(o) else round(float(o), 6)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    return o


def _dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_clean(obj), ensure_ascii=False, separators=(",", ":")))


def main() -> None:
    t = pd.read_parquet(P / "recipient_tensor.parquet")
    m = pd.read_parquet(P / "headline_metrics.parquet")
    mc = pd.read_parquet(P / "headline_metrics_consistent_scope.parquet")
    comp = pd.read_parquet(P / "comparators.parquet")
    io = pd.read_parquet(P / "io_indicators.parquet")
    pe = pd.read_parquet(P / "frame_b_per_euro.parquet")
    sens = pd.read_parquet(P / "sensitivity.parquet")
    rec = pd.read_parquet(P / "reconciliation.parquet")
    firms = pd.read_parquet(P / "ownership_firms.parquet")
    theta = pd.read_parquet(P / "theta_calibration.parquet")

    years = sorted(t.year.unique().tolist())
    io_years = available_years()

    # --- headline time series
    fie = io.groupby("year").apply(
        lambda g: (
            g.imported_intermediates.sum()
            / (g.imported_intermediates.sum() + g.domestic_intermediates.sum())
        )
    )
    series = []
    for _, r in m.iterrows():
        y = int(r.year)
        c = comp[comp.year == y]
        series.append(
            {
                "year": y,
                "gdp": r.gdp,
                "domestic_value_retention": r.domestic_value_retention,
                "foreign_value_leakage": r.foreign_value_leakage,
                "foreign_value_leakage_eur_m": r.foreign_value_leakage * r.gdp,
                "foreign_ownership_capture": r.foreign_ownership_capture,
                "foreign_creditor_income_share_of_nos": r.foreign_creditor_income_share_of_nos,
                "foreign_labour_income_share": r.foreign_labour_income_share,
                "foreign_input_exposure": float(fie.get(y, np.nan)),
                "official_primary_income_outflow_to_gdp": r.primary_income_outflow_to_gdp,
                "official_gni": r.official_gni,
                "ofc_investment_income_paid": r.ofc_investment_income_paid,
                "fdi_income_paid_non_spe": float(c.fdi_income_paid_non_spe.iloc[0])
                if len(c)
                else None,
                "fdi_income_paid_total": float(c.fdi_income_paid_total.iloc[0])
                if len(c)
                else None,
                "dvr_consistent_scope": float(
                    mc.loc[mc.year == y, "domestic_value_retention"].iloc[0]
                ),
                "fats_scope": r.fats_scope,
                "theta": r.theta,
                "tau": r.tau,
            }
        )
    _dump(
        W / "headline.json",
        {
            "country": "CY",
            "name": "Cyprus",
            "years": years,
            "io_years": io_years,
            "series": series,
        },
    )

    # --- per-year recipient flows (drill-down rows keep provenance)
    for y in years:
        ty = t[t.year == y].copy()
        ty["industry_name"] = ty.industry.map(INDUSTRY_NAMES).fillna(ty.industry)
        ty["recipient_name"] = ty.recipient.map(RECIPIENT_NAMES).fillna(ty.recipient)
        rows = ty[
            [
                "industry",
                "industry_name",
                "recipient",
                "recipient_name",
                "mechanism",
                "value",
                *PROV,
            ]
        ].to_dict("records")
        _dump(
            W / f"flows_{y}.json",
            {"year": y, "gdp": float(m.loc[m.year == y, "gdp"].iloc[0]), "rows": rows},
        )

    # --- industry table per year
    for y in years:
        na = na_industry(y)
        my = m.set_index("year").loc[y]
        foc = industry_ownership_capture(t[t.year == y], na["B2A3N"], my["cfc_ratio_nonfin"], my["cfc_ratio_fin"], my["theta"])
        ty = t[t.year == y]
        ior = io[io.year == y].set_index("product") if y in io_years else None
        out = []
        for k in na.index:
            tk = ty[ty.industry == k]
            foreign = tk[tk.mechanism != "retained_domestic"]
            fdi = foreign[foreign.mechanism == "fdi_income"].value.sum()
            top = (
                foreign.groupby("recipient")
                .value.sum()
                .sort_values(ascending=False)
                .head(3)
            )
            gva = na.loc[k, "B1G"]
            out.append(
                {
                    "industry": k,
                    "name": INDUSTRY_NAMES.get(k, k),
                    "gva": gva,
                    "compensation": na.loc[k, "D1"],
                    "gross_operating_surplus": na.loc[k, "B2A3G"],
                    "foreign_outflow": foreign.value.sum(),
                    "foreign_capital_income": fdi
                    + foreign[
                        foreign.mechanism.isin(
                            ["portfolio_income", "other_investment_income"]
                        )
                    ].value.sum(),
                    "foreign_ownership_capture": None if pd.isna(foc.get(k)) else float(foc[k]),
                    "domestic_retention": (1 - foreign.value.sum() / gva)
                    if gva > 0
                    else None,
                    "direct_foreign_input_exposure": float(
                        ior.loc[k, "direct_foreign_input_exposure"]
                    )
                    if ior is not None and k in ior.index
                    else None,
                    "total_import_content": float(ior.loc[k, "total_import_content"])
                    if ior is not None and k in ior.index
                    else None,
                    "main_recipients": [
                        {"recipient": r, "name": RECIPIENT_NAMES.get(r, r), "value": v}
                        for r, v in top.items()
                    ],
                }
            )
        _dump(W / f"industries_{y}.json", {"year": y, "industries": out})

    # --- Frame B per euro (by channel and top recipients)
    for y in io_years:
        py = pe[pe.year == y]
        out = {}
        for k, g in py.groupby("product"):
            out[k] = {
                "name": INDUSTRY_NAMES.get(k, k),
                "channels": g.groupby("channel").value.sum().to_dict(),
                "domestic_va_retained": g[
                    (g.channel == "domestic_value_added") & (g.recipient == "CY")
                ].value.sum(),
                "recipients": g[g.recipient != "CY"]
                .groupby("recipient")
                .value.sum()
                .sort_values(ascending=False)
                .head(8)
                .to_dict(),
            }
        _dump(W / f"per_euro_{y}.json", {"year": y, "products": out})

    # --- IO network (largest domestic inter-industry flows)
    for y in io_years:
        table, _, _ = build(y)
        labs = [lab.removeprefix("CPA_") for lab in table.labels]
        Z = pd.DataFrame(table.Zd, index=labs, columns=labs)
        s = Z.stack()
        s = (
            s[(s.index.get_level_values(0) != s.index.get_level_values(1)) & (s > 0)]
            .sort_values(ascending=False)
            .head(120)
        )
        edges = [{"from": a, "to": b, "value": v} for (a, b), v in s.items()]
        imp = dict(zip(labs, table.Zm.sum(axis=0)))
        nodes = [
            {
                "id": k,
                "name": INDUSTRY_NAMES.get(k, k),
                "output": x,
                "imported_inputs": imp[k],
            }
            for k, x in zip(labs, table.x)
        ]
        _dump(
            W / f"io_network_{y}.json",
            {
                "year": y,
                "nodes": nodes,
                "edges": edges,
                "source": "CYSTAT SIOT 0640050E/0640055E",
                "unit": "EUR m",
            },
        )

    # --- ownership graph and firm pages
    e, d, unpriced = load()
    ents = e.set_index("entity_id")
    firm_rows = []
    for _, r in firms.iterrows():
        firm_rows.append(
            {
                k: r[k]
                for k in [
                    "entity_id",
                    "legal_name",
                    "sector",
                    "nace_code",
                    "domestic",
                    "foreign",
                    "unresolved",
                    "uci_entity",
                    "uci_country",
                    "uci_status",
                    "first_foreign_parent_country",
                    "unpriced_parent_edges",
                    "confidence",
                ]
                if k in r
            }
        )
    nodes = [
        {
            "id": i,
            "name": ents.loc[i, "legal_name"],
            "country": ents.loc[i, "country"],
            "sector": ents.loc[i, "sector"],
            "source_url": ents.loc[i, "source_url"],
        }
        for i in ents.index
    ]
    edges = d[
        [
            "parent_entity_id",
            "child_entity_id",
            "share_pct",
            "share_type",
            "as_of_date",
            "source",
            "source_url",
            "source_tier",
            "confidence",
        ]
    ].rename(columns={"parent_entity_id": "from", "child_entity_id": "to"})
    edges["presumption"] = d.get("presumption", "")
    fin_cols = [
        "revenue_eur_m",
        "operating_profit_eur_m",
        "employees",
        "fiscal_year",
        "notes",
        "source",
        "source_tier",
        "confidence",
    ]
    for c in fin_cols:
        if c in ents.columns:
            for n in nodes:
                n[c] = ents.loc[n["id"], c]
    _dump(
        W / "ownership.json",
        {
            "firms": firm_rows,
            "nodes": nodes,
            "edges": edges.to_dict("records"),
            "unpriced_edges": unpriced[
                [
                    "parent_entity_id",
                    "child_entity_id",
                    "share_type",
                    "source_url",
                    "notes",
                ]
            ].to_dict("records"),
            "theta_calibration": theta[["entity_id", "group", "theta", "group_theta"]].to_dict(
                "records"
            ),
            "note": "Company layer covers ~43 large operating firms; it calibrates theta and illustrates chains. Headline figures use FATS/BoP aggregates.",
        },
    )

    # --- sensitivity, reconciliation, example, catalogue
    _dump(
        W / "sensitivity.json",
        sens.drop(columns=["source_url", "retrieval_date"], errors="ignore").to_dict(
            "records"
        ),
    )
    _dump(
        W / "reconciliation.json",
        rec[
            [
                "check",
                "year",
                "official",
                "model",
                "difference",
                "pct_difference",
                "passes",
                "explanation",
                "status",
                "confidence_level",
                "source",
                "source_url",
            ]
        ].to_dict("records"),
    )
    ex = P / "example_platform_fee.json"
    if ex.exists():
        _dump(
            W / "example_platform.json",
            {
                "summary": json.loads(ex.read_text()),
                "rows": pd.read_csv(P / "example_platform_fee.csv").to_dict("records"),
            },
        )
    cat = Path("data_catalogue.csv")
    if cat.exists():
        _dump(
            W.parent / "catalogue.json", pd.read_csv(cat).fillna("").to_dict("records")
        )
    _dump(
        W.parent / "names.json",
        {"industries": INDUSTRY_NAMES, "recipients": RECIPIENT_NAMES},
    )
    gen = Path("website/src/generated")
    gen.mkdir(parents=True, exist_ok=True)
    (gen / "metric_meta.json").write_text(json.dumps(METRIC_META, indent=1))
    print("exported to", W)


if __name__ == "__main__":
    main()
