"""IO identities.  Each test protects a specific accounting rule from the brief."""

import numpy as np
import pytest

from cvr.io_model import AccountingIdentityError, IOTable, decompose_final_demand, solve


def toy() -> IOTable:
    # 3 industries; numbers chosen so each column balances exactly.
    Zd = np.array([[10.0, 20, 5], [15, 5, 10], [5, 10, 20]])
    Zm = np.array([[5.0, 10, 0], [0, 5, 5], [5, 0, 15]])
    t = np.array([2.0, 3, 1])
    v = np.array([58.0, 47, 44])
    x = Zd.sum(0) + Zm.sum(0) + t + v
    return IOTable(["A", "B", "C"], Zd, Zm, t, v, x)


def test_column_identity_detects_missing_value_added():
    # Revenue (output) must be fully explained by inputs + VA; dropping a VA euro must fail loudly.
    tb = toy()
    broken = IOTable(tb.labels, tb.Zd, tb.Zm, tb.t, tb.v - np.array([0, 1.0, 0]), tb.x)
    with pytest.raises(AccountingIdentityError):
        broken.check_column_identity()


def test_each_euro_of_final_demand_is_exhausted():
    # VA + imported inputs + product taxes = 1 per euro: nothing created or lost by propagation.
    r = solve(toy())
    np.testing.assert_allclose(
        r.total_va_content + r.total_import_content + r.total_tax_content,
        1.0,
        atol=1e-10,
    )


def test_total_import_content_exceeds_direct_when_domestic_suppliers_import():
    # Supply-chain propagation must add the imports embodied in domestic inputs.
    r = solve(toy())
    assert np.all(r.total_import_content >= r.direct_import_intensity - 1e-12)
    assert np.any(r.total_import_content > r.direct_import_intensity + 1e-6)


def test_no_imports_means_all_final_demand_is_domestic_value_or_tax():
    tb = toy()
    x = tb.Zd.sum(0) + tb.t + tb.v
    r = solve(IOTable(tb.labels, tb.Zd, np.zeros((3, 3)), tb.t, tb.v, x))
    np.testing.assert_allclose(r.total_import_content, 0.0)
    np.testing.assert_allclose(r.total_va_content + r.total_tax_content, 1.0)


def test_final_demand_decomposition_is_value_added_not_revenue():
    # A €20 purchase must split into parts summing to €20 — never €20 of "leakage" plus VA on top.
    r = solve(toy())
    d = decompose_final_demand(r, np.array([0, 20.0, 0]))
    assert d["imported_inputs"] < 20
    assert d["domestic_value_added"] + d["imported_inputs"] + d[
        "product_taxes_on_inputs"
    ] == pytest.approx(20)


def test_direct_import_share_is_share_of_intermediates():
    tb = toy()
    r = solve(tb)
    expected = tb.Zm.sum(0) / (tb.Zm.sum(0) + tb.Zd.sum(0))
    np.testing.assert_allclose(r.direct_import_share, expected)


def test_unproductive_matrix_rejected():
    Zd = np.array([[60.0, 0], [0, 10]])
    x = np.array([50.0, 50])
    tb = IOTable(["A", "B"], Zd, np.zeros((2, 2)), np.zeros(2), x - Zd.sum(0), x)
    with pytest.raises(AccountingIdentityError):
        solve(tb, check=False)
