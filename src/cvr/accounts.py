"""Recipient-country accounting: V[i, j, k, t] and the headline metrics.

Frame A — value added generated in country i (the GDP concept) is split by
the residence j of whoever ultimately receives the primary income it pays:

    GVA_k = D1_k (compensation) + D29X39_k (other net taxes on production)
            + B2A3G_k (gross operating surplus / mixed income)

    V[i, j, k] = income flows from industry k to residents of j, by mechanism
    V[i, i, k] = GVA_k - sum_{j != i} V[i, j, k]         (retained)

Only three primary-income mechanisms leave the country: compensation of
non-resident employees (bounded by D1_k), property income paid to non-residents
(bounded by B2A3G_k), and taxes on production paid to EU institutions.  Taxes
paid to the domestic government and wages paid to resident workers can never
be recorded as foreign, whatever the owner's country, because outflows are
bounded by and drawn only from the matching income component.  Product taxes
(D21X31) form the pseudo-industry ``_PRODUCT_TAXES`` so that sum_{j,k} V = GDP.

Frame B — a euro of final demand for domestic output is exhausted by domestic
value added (propagated through L), imported inputs and product taxes on
inputs.  Domestic VA is passed through Frame A's industry recipient shares;
imported inputs through import-origin shares.  Imports are counted once.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .io_model import AccountingIdentityError, IOResult

PRODUCT_TAXES = "_PRODUCT_TAXES"

# mechanism -> national-accounts component it is drawn from
MECHANISMS = {
    "compensation_nonresident": "D1",
    "fdi_income": "B2A3G",
    "fdi_debt_interest": "B2A3G",  # intra-group interest to foreign parents
    "portfolio_income": "B2A3G",
    "other_investment_income": "B2A3G",
    "public_debt_interest": "D21X31",  # government external interest, financed from the tax pool
    "taxes_to_eu_institutions": "D21X31",  # customs duties etc.; drawn from product taxes only
}
RETAINED = "retained_domestic"


@dataclass
class IncomeAccount:
    """Production-side income account of one country-year, by industry (same units throughout)."""

    country: str
    year: int
    gva: pd.Series  # GVA at basic prices by industry
    coe: pd.Series  # D1 by industry
    other_taxes: pd.Series  # D29X39 by industry
    gos: pd.Series  # B2A3G by industry
    product_taxes: float  # D21X31, economy-wide
    outflows: pd.DataFrame = field(default_factory=pd.DataFrame)
    # outflows columns: mechanism, partner, industry, value, status, methodology

    def __post_init__(self) -> None:
        idx = self.gva.index
        for s in (self.coe, self.other_taxes, self.gos):
            if not s.index.equals(idx):
                raise ValueError("income components must share the GVA industry index")

    def check_gva_identity(self, rel_tol: float = 5e-3, abs_tol: float = 0.25) -> pd.Series:
        """Published components are rounded to 0.1 EUR m: four terms each off by <= 0.05 can
        miss by 0.2, hence the absolute floor of 0.25."""
        gap = self.gva - (self.coe + self.other_taxes + self.gos)
        bad = gap.abs() > np.maximum(rel_tol * self.gva.abs(), abs_tol)
        if bad.any():
            raise AccountingIdentityError(
                f"GVA != D1 + D29X39 + B2A3G for {gap[bad].round(2).to_dict()}"
            )
        return gap

    @property
    def gdp(self) -> float:
        return float(self.gva.sum() + self.product_taxes)


def _component(acc: IncomeAccount, comp: str) -> pd.Series:
    if comp == "D21X31":
        return pd.Series({PRODUCT_TAXES: acc.product_taxes})
    return {"D1": acc.coe, "B2A3G": acc.gos}[comp]


def value_tensor(acc: IncomeAccount, check: bool = True) -> pd.DataFrame:
    """Long table: industry, partner, mechanism, value.  Retained rows use partner = acc.country."""
    if check:
        acc.check_gva_identity()
    out = acc.outflows.copy()
    if out.empty:
        out = pd.DataFrame(
            columns=[
                "mechanism",
                "partner",
                "industry",
                "value",
                "status",
                "methodology",
            ]
        )
    unknown = set(out["mechanism"]) - set(MECHANISMS)
    if unknown:
        raise AccountingIdentityError(f"unknown mechanisms {unknown}")
    if (out["partner"] == acc.country).any():
        raise AccountingIdentityError("an outflow cannot be paid to the home country")
    if (out["value"] < 0).any():
        raise AccountingIdentityError(
            "negative outflow; record receipts separately, never net them here"
        )
    if out.duplicated(["mechanism", "partner", "industry"]).any():
        raise AccountingIdentityError(
            "duplicate (mechanism, partner, industry) outflow rows"
        )
    stray = set(out["industry"]) - set(acc.gva.index) - {PRODUCT_TAXES}
    if stray:
        raise AccountingIdentityError(f"outflows reference unknown industries {stray}")

    # Each mechanism may only draw on its own income component.
    for comp in ("D1", "B2A3G", "D21X31"):
        mechs = [m for m, c in MECHANISMS.items() if c == comp]
        drawn = out[out["mechanism"].isin(mechs)].groupby("industry")["value"].sum()
        cap = _component(acc, comp).reindex(drawn.index)
        if cap.isna().any():
            raise AccountingIdentityError(
                f"{comp} outflows booked against the wrong industry: {cap[cap.isna()].index.tolist()}"
            )
        over = drawn - cap.clip(lower=0)  # a loss-making industry can pay out nothing, not less than nothing
        if (over > 1e-6 * cap.abs().clip(lower=1.0)).any():
            raise AccountingIdentityError(
                f"outflows exceed {comp} in industries {over[over > 0].round(2).to_dict()}"
            )

    drawn_by_ind = out.groupby("industry")["value"].sum()
    retained = acc.gva - drawn_by_ind.reindex(acc.gva.index, fill_value=0.0)
    retained_product_taxes = acc.product_taxes - float(drawn_by_ind.get(PRODUCT_TAXES, 0.0))
    ret = pd.DataFrame(
        {
            "industry": retained.index,
            "partner": acc.country,
            "mechanism": RETAINED,
            "value": retained.values,
            "status": "modelled",
            "methodology": "GVA minus attributed outflows",
        }
    )
    tax = pd.DataFrame(
        [
            {
                "industry": PRODUCT_TAXES,
                "partner": acc.country,
                "mechanism": RETAINED,
                "value": retained_product_taxes,
                # observed D21X31 unless outflows were subtracted from it
                "status": "observed" if retained_product_taxes == acc.product_taxes else "modelled",
                "methodology": "D21X31 accrues to general government; EU-institution share, if any, recorded as outflow",
            }
        ]
    )
    tensor = pd.concat([out, ret, tax], ignore_index=True)
    if check and abs(tensor["value"].sum() - acc.gdp) > 1e-6 * max(1.0, abs(acc.gdp)):
        raise AccountingIdentityError("recipient tensor does not sum to GDP")
    tensor.insert(0, "year", acc.year)
    tensor.insert(0, "country", acc.country)
    return tensor


def recipient_matrix(tensor: pd.DataFrame) -> pd.DataFrame:
    return tensor.pivot_table(
        index="industry",
        columns="partner",
        values="value",
        aggfunc="sum",
        fill_value=0.0,
    )


def headline_metrics(
    acc: IncomeAccount,
    tensor: pd.DataFrame,
    direct_import_share_total: float | None = None,
    official_primary_income_paid: float | None = None,
) -> dict[str, float]:
    """Metrics are reported side by side and never summed: they measure different mechanisms.

    foreign_value_leakage is the model concept: income attributed to *domestic
    production* and bounded by the matching income component.
    primary_income_outflow_to_gdp is the unadjusted official BoP debit over GDP;
    it includes pass-through (e.g. SPE) income and is shown for comparison only.
    """
    foreign = tensor[tensor["mechanism"] != RETAINED]
    cap_out = foreign[_mask("B2A3G", foreign)]["value"].sum()
    lab_out = foreign[foreign["mechanism"] == "compensation_nonresident"]["value"].sum()
    m = {
        "gdp": acc.gdp,
        "domestic_value_retention": 1 - foreign["value"].sum() / acc.gdp,
        "foreign_value_leakage": foreign["value"].sum() / acc.gdp,
        "foreign_labour_income_share": lab_out / acc.coe.sum(),
    }
    if official_primary_income_paid is not None:
        m["primary_income_outflow_to_gdp"] = official_primary_income_paid / acc.gdp
    if direct_import_share_total is not None:
        m["foreign_input_exposure"] = direct_import_share_total
    return m


def _mask(comp: str, df: pd.DataFrame) -> pd.Series:
    return df["mechanism"].isin([m for m, c in MECHANISMS.items() if c == comp])


def industry_recipient_shares(tensor: pd.DataFrame) -> pd.DataFrame:
    """s[k, j] = share of industry k's GVA accruing to j (rows sum to 1)."""
    t = tensor[tensor["industry"] != PRODUCT_TAXES]
    mat = recipient_matrix(t)
    return mat.div(mat.sum(axis=1), axis=0)


def value_chain_recipients(
    res: IOResult,
    f: np.ndarray,
    va_shares: pd.DataFrame,
    import_origin: pd.DataFrame,
    home: str,
) -> pd.DataFrame:
    """Frame B: where a final-demand vector f (for domestic output) ultimately accrues.

    va_shares: industry x partner (rows sum to 1), aligned to res.labels.
    import_origin: product x partner shares of imported intermediates (rows sum to 1).
    Returns rows: channel, partner, value.  Sum equals f.sum().
    """
    f = np.asarray(f, dtype=float)
    labels = res.labels
    xL = res.L @ f  # output required, by industry
    va_by_ind = res.va_coef * xL
    imp_by_prod = res.Am @ xL  # imported inputs by product row
    tax = float(res.tax_coef @ xL)

    s = va_shares.reindex(labels)
    if s.isna().any().any():
        raise AccountingIdentityError("va_shares missing industries")
    o = import_origin.reindex(labels).fillna(0.0)
    rows_with_imports = imp_by_prod > 1e-12
    if not np.allclose(o.sum(axis=1).values[rows_with_imports], 1.0, atol=1e-6):
        raise AccountingIdentityError(
            "import-origin shares must sum to 1 for every imported product"
        )

    va_part = (s.mul(va_by_ind, axis=0)).sum(axis=0)
    imp_part = (o.mul(imp_by_prod, axis=0)).sum(axis=0)
    out = pd.concat(
        [
            pd.DataFrame(
                {
                    "channel": "domestic_value_added",
                    "partner": va_part.index,
                    "value": va_part.values,
                }
            ),
            pd.DataFrame(
                {
                    "channel": "imported_inputs",
                    "partner": imp_part.index,
                    "value": imp_part.values,
                }
            ),
            pd.DataFrame(
                [{"channel": "product_taxes_on_inputs", "partner": home, "value": tax}]
            ),
        ],
        ignore_index=True,
    )
    out = out[out["value"].abs() > 1e-12]
    if abs(out["value"].sum() - f.sum()) > 1e-6 * max(1.0, f.sum()):
        raise AccountingIdentityError("Frame B recipients do not exhaust final demand")
    return out


def industry_ownership_capture(tensor_year: pd.DataFrame, nos: pd.Series, cfc_nonfin: float, cfc_fin: float, theta: float) -> pd.Series:
    """Foreign Ownership Capture by industry: foreign-owned net operating surplus (FATS base after
    corporate depreciation, x theta; before interest and tax) / the industry's net operating
    surplus.  Published only where FATS publishes the industry's own code: a value built from a
    section remainder or a code shared with other industries is an allocation, not a measurement
    (NaN = "n.m.").  Values above 100% (FATS and national-accounts concepts differ) are also n.m.
    """
    f = tensor_year[(tensor_year.mechanism == "fdi_income") & tensor_year.gross_base.notna()]
    code = f.fats_code.fillna("")
    n_ind = f.groupby(code).industry.transform("nunique")  # a code shared by several industries is split, not measured
    own_section = code.eq(f.industry + " remainder")  # a single-industry section (e.g. I): its total is its own
    direct = f[(own_section | (~code.str.contains("remainder") & code.str.len().gt(1))) & n_ind.eq(1)]
    base = direct.groupby("industry").gross_base.sum()
    ratio = pd.Series({k: (1 - (cfc_fin if k.startswith("K") else cfc_nonfin)) * theta for k in base.index})
    out = base * ratio / nos.reindex(base.index).where(nos.reindex(base.index) > 0)
    return out.where(out <= 1.0).reindex(nos.index)
