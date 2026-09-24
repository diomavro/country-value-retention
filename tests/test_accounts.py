"""Double-counting and misattribution guards for the recipient tensor (brief §2, §10)."""

import numpy as np
import pandas as pd
import pytest

from cvr.accounts import (
    PRODUCT_TAXES,
    RETAINED,
    IncomeAccount,
    headline_metrics,
    industry_recipient_shares,
    value_chain_recipients,
    value_tensor,
)
from cvr.io_model import AccountingIdentityError, IOTable, solve

IND = ["A", "B", "C"]


def account(outflows=None) -> IncomeAccount:
    coe = pd.Series([30.0, 20, 10], index=IND)
    otp = pd.Series([2.0, 1, 1], index=IND)
    gos = pd.Series([26.0, 26, 33], index=IND)
    return IncomeAccount(
        "CY",
        2022,
        gva=coe + otp + gos,
        coe=coe,
        other_taxes=otp,
        gos=gos,
        product_taxes=15.0,
        outflows=pd.DataFrame(
            outflows or [],
            columns=[
                "mechanism",
                "partner",
                "industry",
                "value",
                "status",
                "methodology",
            ],
        ),
    )


def row(mech, partner, ind, value):
    return (mech, partner, ind, value, "estimated", "test")


def test_fully_foreign_owned_industry_keeps_wages_and_taxes_at_home():
    # 100% foreign-owned industry B: only its operating surplus can leave, never D1 or D29.
    acc = account([row("fdi_income", "US", "B", 26.0)])
    t = value_tensor(acc)
    b_home = t[(t.industry == "B") & (t.mechanism == RETAINED)]["value"].sum()
    assert b_home == pytest.approx(acc.coe["B"] + acc.other_taxes["B"])


def test_capital_income_cannot_exceed_operating_surplus():
    # Counting revenue (or wages) as foreign capital income must be impossible.
    with pytest.raises(AccountingIdentityError, match="exceed B2A3G"):
        value_tensor(account([row("fdi_income", "US", "B", 30.0)]))


def test_foreign_labour_income_bounded_by_compensation():
    with pytest.raises(AccountingIdentityError, match="exceed D1"):
        value_tensor(account([row("compensation_nonresident", "GR", "C", 10.5)]))


def test_taxes_cannot_be_booked_as_capital_income():
    with pytest.raises(AccountingIdentityError, match="wrong industry"):
        value_tensor(account([row("fdi_income", "US", PRODUCT_TAXES, 1.0)]))


def test_eu_customs_duties_drawn_from_product_taxes_only():
    t = value_tensor(
        account([row("taxes_to_eu_institutions", "EU_INST", PRODUCT_TAXES, 3.0)])
    )
    home_tax = t[(t.industry == PRODUCT_TAXES) & (t.partner == "CY")]["value"].sum()
    assert home_tax == pytest.approx(12.0)
    with pytest.raises(AccountingIdentityError):
        value_tensor(account([row("taxes_to_eu_institutions", "EU_INST", "A", 1.0)]))


def test_duplicate_flow_rejected():
    # The same ownership chain / flow must not be counted twice.
    with pytest.raises(AccountingIdentityError, match="duplicate"):
        value_tensor(
            account(
                [row("fdi_income", "US", "B", 5.0), row("fdi_income", "US", "B", 5.0)]
            )
        )


def test_home_country_outflow_rejected():
    with pytest.raises(AccountingIdentityError):
        value_tensor(account([row("fdi_income", "CY", "B", 5.0)]))


def test_negative_outflow_rejected():
    # Receipts must not be netted against payments inside the production-side tensor.
    with pytest.raises(AccountingIdentityError):
        value_tensor(account([row("fdi_income", "US", "B", -5.0)]))


def test_tensor_sums_to_gdp_and_metrics_are_complements():
    acc = account(
        [
            row("fdi_income", "US", "B", 10.0),
            row("compensation_nonresident", "GR", "A", 3.0),
        ]
    )
    t = value_tensor(acc)
    assert t["value"].sum() == pytest.approx(acc.gdp)
    m = headline_metrics(acc, t, official_primary_income_paid=40.0)
    assert m["domestic_value_retention"] + m["foreign_value_leakage"] == pytest.approx(
        1.0
    )
    assert m["foreign_value_leakage"] == pytest.approx(13.0 / acc.gdp)
    # Official BoP outflow is a separate, unadjusted comparator, not the model leakage.
    assert m["primary_income_outflow_to_gdp"] == pytest.approx(40.0 / acc.gdp)


def test_gva_identity_enforced():
    acc = account()
    acc.gva = acc.gva + pd.Series([0, 5.0, 0], index=IND)
    with pytest.raises(AccountingIdentityError):
        value_tensor(acc)


def io_toy():
    Zd = np.array([[10.0, 20, 5], [15, 5, 10], [5, 10, 20]])
    Zm = np.array([[5.0, 10, 0], [0, 5, 5], [5, 0, 15]])
    t = np.array([2.0, 3, 1])
    v = np.array([58.0, 47, 44])
    return solve(IOTable(IND, Zd, Zm, t, v, Zd.sum(0) + Zm.sum(0) + t + v))


def test_platform_fee_is_decomposed_not_classified_whole_as_leakage():
    # The €20 platform example: foreign share < €20 and all parts sum to €20.
    res = io_toy()
    acc = account([row("fdi_income", "US", "B", 20.0)])
    shares = industry_recipient_shares(value_tensor(acc))
    origin = pd.DataFrame({"DE": [1.0, 0.5, 0.0], "IT": [0.0, 0.5, 1.0]}, index=IND)
    out = value_chain_recipients(res, np.array([0, 20.0, 0]), shares, origin, "CY")
    assert out["value"].sum() == pytest.approx(20.0)
    foreign = out[out.partner != "CY"]["value"].sum()
    assert 0 < foreign < 20
    # Imported inputs are counted once: the import channel equals total import content.
    assert out[out.channel == "imported_inputs"]["value"].sum() == pytest.approx(
        20 * res.total_import_content[1]
    )


def test_import_origin_shares_must_sum_to_one():
    res = io_toy()
    shares = industry_recipient_shares(value_tensor(account()))
    bad = pd.DataFrame({"DE": [0.5, 0.5, 0.5]}, index=IND)
    with pytest.raises(AccountingIdentityError):
        value_chain_recipients(res, np.array([1.0, 1, 1]), shares, bad, "CY")


def test_aggregate_partner_codes_are_not_countries():
    # Franc Zone / EU / euro area are groups of economies: listing them beside members double counts.
    from cvr.model.frame_a import _is_country

    assert not any(_is_country(c) for c in ("FZ", "EU", "EA", "WRL_REST", "OFFSHO"))
    assert all(_is_country(c) for c in ("CY", "EL", "UK", "US", "RU"))


def test_industry_capture_only_where_fats_measures_the_industry():
    # A code shared by two industries (M69-M71 -> M69-70, M71) is an allocation: n.m.
    from cvr.accounts import industry_ownership_capture

    t = pd.DataFrame(
        {
            "mechanism": ["fdi_income"] * 4,
            "industry": ["J58", "M69-70", "M71", "G47"],
            "gross_base": [10.0, 6.0, 4.0, 5.0],
            "fats_code": ["J58", "M69-M71", "M69-M71", "G remainder"],
            "value": [1.0] * 4,
        }
    )
    nos = pd.Series({"J58": 20.0, "M69-70": 30.0, "M71": 10.0, "G47": 50.0})
    out = industry_ownership_capture(t, nos, cfc_nonfin=0.0, cfc_fin=0.0, theta=1.0)
    assert out["J58"] == pytest.approx(0.5)
    assert out[["M69-70", "M71", "G47"]].isna().all()
