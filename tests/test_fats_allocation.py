"""FATS allocation: conserve the published total, use the finest code, respect scope."""

import pandas as pd
import pytest

from cvr.model.frame_a import allocate_fats

IND = ["G45", "G46", "G47", "J58", "J59-60", "J61", "J62-63", "L68A", "L68B"]


def na():
    gos = pd.Series([10.0, 40, 50, 20, 5, 30, 25, 100, 60], index=IND)
    return pd.DataFrame({"B2A3G": gos})


def test_section_total_conserved_even_with_a_loss_making_subcode():
    # G = 100 published, G45 = -5 (loss), G46 = 60: G47 must get 40, not 45 (no value created).
    sec = pd.Series({"G": 100.0})
    codes = pd.Series({"G": 100.0, "G45": -5.0, "G46": 60.0})
    out, used, losses = allocate_fats(sec, codes, na())
    assert out[["G45", "G46", "G47"]].sum() == pytest.approx(100.0)
    assert out["G46"] == pytest.approx(60.0) and out["G47"] == pytest.approx(40.0)
    assert losses == {"G45": -5.0}


def test_finest_published_code_beats_section_share():
    # J58 published: its value is used as is, not a GOS share of the J total.
    sec = pd.Series({"J": 100.0})
    codes = pd.Series({"J": 100.0, "J58": 70.0, "J62_J63": 10.0})
    out, used, _ = allocate_fats(sec, codes, na())
    assert out["J58"] == pytest.approx(70.0) and used["J58"] == "J58"
    assert out["J62-63"] == pytest.approx(10.0)
    # remainder 20 split over J59-60 and J61 by GOS (5:30)
    assert out["J61"] == pytest.approx(20 * 30 / 35)


def test_virtual_code_from_complete_child_divisions():
    sec = pd.Series({"J": 50.0})
    codes = pd.Series({"J": 50.0, "J62": 12.0, "J63": 8.0})
    out, used, _ = allocate_fats(sec, codes, na())
    assert out["J62-63"] == pytest.approx(20.0) and used["J62-63"] == "J62+J63"


def test_imputed_rent_never_receives_foreign_surplus():
    sec = pd.Series({"L": 30.0})
    out, _, _ = allocate_fats(sec, pd.Series({"L": 30.0}), na())
    assert out["L68A"] == 0 and out["L68B"] == pytest.approx(30.0)


def test_ipf_never_inflates_published_cells():
    # Row fully published but below its total: the gap is unpublished, so it goes to the
    # confidential bucket; the published cells keep their values.
    from cvr.model.frame_a import section_country_shares

    # No confidential remainder in the column margins, so the leftover branch itself must act.
    sections = pd.Series({"J": 100.0, "G": 50.0})
    cols = pd.Series({"US": 70.0, "EL": 80.0})
    cells = pd.DataFrame({"US": [40.0, float("nan")], "EL": [30.0, float("nan")]}, index=["J", "G"])
    sh = section_country_shares(sections, cols, cells)
    assert sh.loc["J", "US"] * 100 == pytest.approx(40.0)
    assert sh.loc["J", "EL"] * 100 == pytest.approx(30.0)
    assert sh.loc["J"].sum() == pytest.approx(1.0)
