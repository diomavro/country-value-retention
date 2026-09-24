"""Offline tests for the Eurostat downloader's query construction.

Why these matter: the SDMX 2.1 endpoint silently ignores query-string filters,
so a key built in the wrong dimension order downloads the wrong (or the whole)
cube; and Eurostat rejects the *entire* query if any requested code is absent
from the dataset (e.g. geo=CY in naio_10_cp1750), which would break EU27 runs.
"""

import pytest

from cvr.ingest import eurostat as es


@pytest.fixture
def fake_dsd(monkeypatch):
    monkeypatch.setattr(
        es, "dimensions", lambda code: ("freq", "unit", "na_item", "geo")
    )
    monkeypatch.setattr(
        es,
        "available",
        lambda code: {
            "freq": frozenset({"A"}),
            "unit": frozenset({"CP_MEUR"}),
            "na_item": frozenset({"B1GQ", "D1"}),
            "geo": frozenset({"CY", "MT"}),
        },
    )


def test_key_follows_dsd_order_not_dict_order(fake_dsd):
    url = es.build_url("x", {"geo": ["CY", "MT"], "na_item": "D1"}, start=2010)
    assert "/data/x/..D1.CY+MT/" in url
    assert url.endswith("&startPeriod=2010")


def test_unknown_dimension_is_an_error(fake_dsd):
    with pytest.raises(ValueError):
        es.build_url("x", {"country": "CY"})


def test_constrain_drops_absent_codes_and_reports_them(fake_dsd):
    kept, dropped = es.constrain("x", {"geo": ["CY", "LU"], "na_item": "D1"})
    assert kept == {"geo": ["CY"], "na_item": ["D1"]}
    assert dropped == {"geo": ["LU"]}


def test_constrain_raises_nodata_when_nothing_survives(fake_dsd):
    with pytest.raises(es.NoData):
        es.constrain("x", {"geo": "LU"})


def test_slug_is_order_invariant_and_bounded():
    a = es.slugify({"geo": ["MT", "CY"], "unit": "X"})
    b = es.slugify({"unit": "X", "geo": ["CY", "MT"]})
    assert a == b
    assert len(es.slugify({"bop_item": [f"ITEM{i}" for i in range(50)]})) <= 71
