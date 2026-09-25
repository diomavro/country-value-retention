"""Frame A for other countries: the Eurostat route must reproduce Cyprus, and countries must never mix.

These tests read the downloaded raw data and are skipped in a clone without it.
"""

from pathlib import Path

import pandas as pd
import pytest

from cvr.model import frame_a as fa

needs_eu = pytest.mark.skipif(
    not any(Path("data/raw/eurostat_eu").glob("nasa_10_nf_tr__*.parquet")),
    reason="comparison-country inputs not downloaded",
)
needs_data = pytest.mark.skipif(
    not (
        Path("data/interim/cystat/sector_accounts.parquet").exists()
        and any(Path("data/raw/eurostat").glob("nasa_10_nf_tr__*.parquet"))
    ),
    reason="raw Cyprus inputs not downloaded",
)


def _by_mechanism(year: int) -> tuple[pd.Series, float]:
    acc, _ = fa.build_account(year, fa.Params())
    return acc.outflows.groupby("mechanism")["value"].sum(), acc.gdp


@needs_data
@pytest.mark.parametrize("year", [2015, 2020, 2023])
def test_eurostat_route_reproduces_cystat_for_cyprus(year):
    # Why: the comparison countries have no CYSTAT; their results are only credible if the
    # Eurostat sector-account route gives Cyprus's published results.  CYSTAT and Eurostat differ
    # by rounding (<= EUR 0.5m per item), so each mechanism must agree within EUR 1m.
    cystat, gdp_c = _by_mechanism(year)
    with fa.country("CY", sector_source="eurostat"):
        eurostat, gdp_e = _by_mechanism(year)
    assert abs(gdp_c - gdp_e) <= 1.0
    diff = cystat.sub(eurostat, fill_value=0).abs()
    assert (diff <= 1.0).all(), diff[diff > 1.0]
    assert abs(cystat.sum() / gdp_c - eurostat.sum() / gdp_e) < 1e-4


READERS = {
    "national accounts by industry": lambda: fa._nama(),
    "sector accounts": lambda: fa._nasa(),
    "BoP by sector": lambda: fa._bop_c6(),
    "BoP compensation": lambda: fa._one("bop_rem6__*.parquet"),
    "FATS 2021-": lambda: fa._one("fats_activ__*.parquet"),
    "FATS -2020": lambda: fa._one("fats_g1a_08__*.parquet"),
}


@needs_data
@pytest.mark.parametrize("reader", READERS)
def test_other_countries_never_read_cyprus_files(monkeypatch, reader):
    # Why: every reader globs a directory; if another country's reads fell through to Cyprus
    # files (or vice versa) the comparison would silently report Cyprus numbers.
    monkeypatch.setattr(fa, "EUROSTAT_EU", fa.EUROSTAT)  # a directory holding Cyprus data only
    with fa.country("PT"):
        with pytest.raises(FileNotFoundError, match="geo=PT"):
            READERS[reader]()


def test_conflicting_downloads_fail_loudly(tmp_path, monkeypatch):
    # Why: a re-download with a different --geo list leaves the old file beside the new one;
    # two values for one observation must stop the run, not be averaged.
    row = {"DATAFLOW": "x", "LAST_UPDATE": "", "unit": "CP_MEUR", "na_item": "B1G", "nace_r2": "TOTAL", "geo": "PT", "TIME_PERIOD": "2020", "OBS_FLAG": None, "CONF_STATUS": None}
    pd.DataFrame([{**row, "OBS_VALUE": 100.0}]).to_parquet(tmp_path / "nama_10_a64__a.parquet")
    pd.DataFrame([{**row, "OBS_VALUE": 100.0}]).to_parquet(tmp_path / "nama_10_a64__b.parquet")
    monkeypatch.setattr(fa, "EUROSTAT_EU", tmp_path)
    with fa.country("PT"):
        assert len(fa._one("nama_10_a64__*.parquet")) == 1  # identical repeats are harmless
    pd.DataFrame([{**row, "OBS_VALUE": 110.0}]).to_parquet(tmp_path / "nama_10_a64__b.parquet")
    with fa.country("PT"):
        with pytest.raises(ValueError, match="conflicting"):
            fa._one("nama_10_a64__*.parquet")


@needs_data
def test_country_context_restores_cyprus_after_an_error():
    before = fa.gdp(2020)
    with pytest.raises(RuntimeError):
        with fa.country("CY", sector_source="eurostat"):
            raise RuntimeError
    assert fa._GEO == "CY" and fa._SECTOR_SOURCE == "cystat"
    assert fa.gdp(2020) == before


def test_theta_must_be_explicit_outside_cyprus():
    # Why: theta is calibrated from Cypriot ownership filings; silently reusing it elsewhere would
    # present a Cyprus parameter as another country's estimate.
    with fa.country("MT"):
        with pytest.raises(ValueError, match="theta"):
            fa.build_account(2020, fa.Params())


@needs_eu
def test_missing_download_is_not_reported_as_suppression(monkeypatch):
    # Why: a file that was never downloaded is our failure, not the statistical office's; recording
    # it as "suppressed" would silently drop a country from the comparison.
    from cvr import compare

    monkeypatch.setattr(fa, "OECD_CIT", Path("data/raw/oecd/does_not_exist.csv"))
    fa._oecd_cit.cache_clear()
    try:
        with pytest.raises(FileNotFoundError, match="does_not_exist"):
            compare.run(["PT"], [2020])
    finally:
        fa._oecd_cit.cache_clear()


def test_incomplete_mechanisms_follow_the_booking_rules():
    # Why: the dashboard marks a line as incomplete from this mapping; it must name the mechanism
    # the suppressed item would have been booked to (frame_a.m2_foreign_owned / m3_other).
    from cvr.compare import incomplete_mechanisms

    assert incomplete_mechanisms(["S1V D41__O__FLA"]) == "other_investment_income"
    assert incomplete_mechanisms(["S1V D42__P__F51"]) == "portfolio_income"
    assert incomplete_mechanisms(["S122 D42__P__F51 paid"]) == "other_investment_income"  # banks: netted
    assert incomplete_mechanisms(["S1V D41__D__FLA"]) == "fdi_debt_interest"
    assert incomplete_mechanisms(["S13 D41__O__FLA"]) == "public_debt_interest"
    assert incomplete_mechanisms(["S122 D4S__D__F5"]) == "fdi_income"


def test_imputed_rent_never_counts_as_firms_surplus():
    # Why: owner-occupiers' imputed rent is earned by households, not by any firm, so it must not
    # attract foreign-owned profit or firms' interest, whether published (L68A) or inside a collapsed L.
    na = pd.DataFrame({"B2A3G": [100.0, 40.0, 60.0]}, index=["C", "L68A", "L68B"])
    assert "L68A" not in fa.market_gos(na).index
    collapsed = pd.DataFrame({"B2A3G": [100.0, 100.0]}, index=["C", "L"])
    collapsed.attrs["imputed_rent_in_L"] = 70.0
    assert fa.market_gos(collapsed)["L"] == 30.0


@needs_eu
@needs_data
def test_suppressed_bank_profit_is_listed():
    # Why: before 2021 foreign-owned banks' profit comes from the BoP; when that is suppressed the
    # line is missing and the reader must be told (Luxembourg).
    with fa.country("LU"):
        _, d = fa.build_account(2015, fa.Params(theta=0.9))
    assert "S122 D4S__D__F5" in d["confidential_items"]
    assert any(k.startswith("S1V") for k in d["confidential_items"])  # m3 items survive the merge


def test_finance_level_factor_only_scales_down():
    # Why: the rule corrects FATS finance that is wider than the national accounts; it must never
    # raise foreign surplus, and must leave finance alone when FATS is within the NA level.
    assert fa.finance_level_factor(150.0, 100.0) == pytest.approx(100 / 150)
    assert fa.finance_level_factor(80.0, 100.0) == 1.0
    assert fa.finance_level_factor(float("nan"), 100.0) == 1.0
    assert fa.finance_level_factor(150.0, 0.0) == 1.0


def test_central_estimate_uses_the_national_accounts_level_for_finance():
    # Why: the central estimate was chosen to cap finance at the national-accounts level (2026-09-25).
    assert fa.Params().fats_na_level is True


def test_imputed_rent_surplus_prefers_published_surplus():
    # Why: removing imputed rent from a collapsed real-estate row must use its operating surplus
    # where published, and its value added (an upper bound) only where nothing else is.
    assert fa.imputed_rent_gos(pd.Series({"B1G": 50.0, "B2A3N": 30.0, "P51C": 10.0})) == 40.0
    assert fa.imputed_rent_gos(pd.Series({"B1G": 50.0, "B2A3N": float("nan"), "P51C": float("nan")})) == 50.0
    assert fa.imputed_rent_gos(pd.Series({"B1G": float("nan"), "B2A3N": float("nan"), "P51C": float("nan")})) == 0.0


@needs_data
@pytest.mark.parametrize(
    "geo, year",
    [pytest.param("LU", 2023, marks=needs_eu), ("CY", 2023), ("CY", 2015), pytest.param("PT", 2022, marks=needs_eu)],
)
def test_only_finance_is_brought_to_the_national_accounts_level(geo, year):
    # Why: other sections differ from the national accounts by definition (value added minus
    # personnel costs before 2021), not by scope; scaling them would cut foreign profit one-sidedly.
    with fa.country(geo):
        wide = fa.fats_foreign_gos(year, na_level=False)
        f = fa.fats_foreign_gos(year, na_level=True)
        mg = fa.market_gos(fa.na_industry(year))
    assert set(f["level_scaled"]) <= {"K"}
    other = [s_ for s_ in wide["sections"].index if s_ != "K"]
    assert (f["sections"][other] == wide["sections"][other]).all()
    if "K" in f["level_scaled"]:
        # the factor is NA finance surplus / FATS all-owner finance surplus, applied to sections and sub-codes
        assert f["sections"]["K"] <= mg[[k for k in mg.index if k.startswith("K")]].sum() + 1e-6
        assert f["level_removed"] == pytest.approx(wide["sections"]["K"] - f["sections"]["K"])
        k_codes = [c for c in f["codes"].dropna().index if c.startswith("K")]
        assert list(f["codes"][k_codes]) == pytest.approx(list(wide["codes"][k_codes] * f["level_scaled"]["K"]))
        assert (f["sections_fats"] == wide["sections"]).all()  # country shares stay on the FATS basis


@needs_data
def test_finance_cap_keeps_the_country_split_of_finance():
    # Why: the cap changes how much foreign finance surplus there is, not who owns it; computing
    # the country split on the capped totals moved the whole cut onto unpublished partners.
    year = 2023
    f = fa.fats_foreign_gos(year, na_level=True)
    assert "K" in f["level_scaled"]  # Cyprus finance is capped in 2023
    expected = fa.section_country_shares(f["sections_fats"], f["col_totals"], f["cells"]).loc["K"]
    rows, _ = fa.m2_foreign_owned(year, fa.na_industry(year), fa.Params(theta=0.9))
    k = pd.DataFrame([r for r in rows if r["industry"].startswith("K") and r["gross_base"] == r["gross_base"]])
    booked = k.groupby("partner").gross_base.sum() / k.gross_base.sum()
    assert booked.to_dict() == pytest.approx(expected[expected > 0].to_dict())


@needs_eu
@needs_data
def test_remainder_filled_finance_is_capped_too():
    # Why: where FATS suppresses foreign-controlled finance (Ireland 2022) the remainder fill is on the
    # same wider FATS basis; left uncapped it was 2.7 times the national-accounts finance surplus.
    with fa.country("IE"):
        f = fa.fats_foreign_gos(2022, na_level=True)
        mg = fa.market_gos(fa.na_industry(2022))
    assert f["level_scaled"]["K"] < 1
    assert f["sections"]["K"] <= mg[[k for k in mg.index if k.startswith("K")]].sum() + 1e-6
    # the cut leaves the total: no other (confidential) section absorbs it
    assert (f["sections"].drop("K") == f["sections_fats"].drop("K")).all()
    assert f["level_removed"] == pytest.approx(f["sections_fats"]["K"] - f["sections"]["K"])


@needs_data
@pytest.mark.parametrize("year", [2021, 2022, 2023])
def test_validator_recomputes_the_finance_cut_independently(year):
    # Why: the build fails if the model's finance cut disagrees with one recomputed from the raw
    # files; the recomputation must itself match the model where both apply.
    from cvr.validate import _finance_level_removed

    model = fa.fats_foreign_gos(year, na_level=True)["level_removed"]
    assert model > 0  # Cyprus finance is capped in 2021-2023
    assert _finance_level_removed(year) == pytest.approx(model)


@needs_data
def test_consistent_scope_removes_no_finance():
    # Why: the consistent-scope series has no finance from FATS, so nothing can be cut from it.
    f = fa.fats_foreign_gos(2023, consistent_scope=True, na_level=True)
    assert "K" not in f["sections"].index and f["level_removed"] == 0.0
