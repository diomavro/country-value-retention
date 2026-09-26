"""The sensitivity grid: what each variant changes, and the tax variants."""

from dataclasses import asdict, fields
from pathlib import Path

import pytest

from cvr import pipeline
from cvr.model import frame_a as fa

CENTRAL = asdict(fa.Params())


def _changed(prm) -> dict:
    return {k: v for k, v in asdict(prm).items() if v != CENTRAL[k] and k != "theta"}


def test_one_at_a_time_variants_change_exactly_one_assumption():
    # Why: the paper reports each of these as "changing X gives Y"; a variant that also moves
    # another assumption would misattribute its effect.
    for kw in pipeline.ONE_AT_A_TIME:
        prm = fa.Params(**kw)
        assert set(_changed(prm)) == set(kw), kw


def test_worst_case_lowers_every_assumption_at_once():
    # Why: the envelope's lower end is reported as every assumption that lowers retention at once.
    worst = pipeline.WORST_CASE
    for key in ("banks_gross", "bop_upper", "include_ofc", "consistent_scope"):
        assert worst[key] is True, key
    assert worst["tax"] == "none" and worst["theta"] == 1.0 and worst["rho_basis"] == "none"
    assert worst["fats_na_level"] is False  # the FATS level of finance is the higher outflow


@pytest.mark.skipif(not Path("data/processed/sensitivity.parquet").exists(), reason="pipeline not run")
def test_worst_case_is_the_lowest_variant_in_every_year():
    # Why: if another variant falls below the combined worst case, the reported envelope is wrong.
    import pandas as pd

    s = pd.read_parquet("data/processed/sensitivity.parquet")
    w = pipeline.WORST_CASE
    central = asdict(fa.Params())
    is_worst = pd.Series(True, index=s.index)
    for k in central:  # every field at its worst-case value (or central, if WORST_CASE leaves it alone)
        v = w.get(k, central[k])
        is_worst &= s[k] == (fa.calibrated_theta() if k == "theta" and v is None else v)
    assert is_worst.groupby(s.year).sum().eq(1).all()
    lowest = s.groupby("year").domestic_value_retention.min()
    assert (s[is_worst].set_index("year").domestic_value_retention - lowest).abs().max() < 1e-12


def test_one_at_a_time_list_is_complete():
    # Why: dropping a variant from the grid silently removes a robustness check the paper reports.
    assert pipeline.ONE_AT_A_TIME == [
        dict(banks_gross=True),
        dict(fats_na_level=False),
        dict(tax="eatr"),
        dict(bop_upper=True),
        dict(rho_basis="none"),
        dict(rho_basis="d41_net"),
        dict(rho_basis="d41g_gross"),
    ]


def test_grid_has_no_duplicate_variants():
    # Why: two identical rows make paper macros that select one row ambiguous.
    keys = [tuple(sorted(asdict(p).items())) for p in pipeline.sensitivity_grid()]
    assert len(keys) == len(set(keys))


def test_params_fields_are_all_recorded_in_the_sensitivity_table():
    # Why: a Params field missing from the output table cannot be filtered on, so its variants
    # leak into selections of the central grid (as fats_na_level once did).
    import inspect

    src = inspect.getsource(pipeline.sensitivity)
    for f in fields(fa.Params):
        assert f"{f.name}=prm.{f.name}" in src or f.name == "theta", f.name


def test_tax_bases():
    # Why: the central estimate uses the statutory rate; "none" is the no-tax bound.
    assert fa.tax_rate(2020, "statutory") == 0.125
    assert fa.tax_rate(2020, "none") == 0.0
    with pytest.raises(ValueError):
        fa.tax_rate(2020, "effective")


@pytest.mark.skipif(
    not Path("data/raw/ec_taxation/effective_tax_rates.xlsx").exists(),
    reason="EC tax rates not downloaded",
)
def test_eatr_uses_published_rate_and_falls_back_before_2017():
    # Why: the variant must use the Commission's published rate (Cyprus 2023: 10.422%, from the
    # file) and the statutory rate before 2017, when the EATR includes property taxes already deducted.
    from cvr.ingest.ec_taxation import eatr

    rates = eatr()
    assert rates[("Cyprus", 2023)] == pytest.approx(0.10422)
    assert rates.between(0, 0.5).all()
    assert fa.tax_rate(2023, "eatr") == pytest.approx(0.10422)
    assert fa.tax_rate(2016, "eatr") == fa.statutory_cit(2016)
    assert fa.tax_rate(2017, "eatr") == pytest.approx(rates[("Cyprus", 2017)])
