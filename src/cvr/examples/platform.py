"""ILLUSTRATIVE worked example (brief §8): a Cypriot restaurant pays a platform EUR 20.

Not a headline result.  No company accounts for Wolt Cyprus are public (Registrar
filings are paywalled), so the platform's own cost structure is the industry
average for information services (CPA J62-63, the product of NACE 63 where Wolt
Cyprus is registered).  What *is* company-specific is the ownership chain:
Wolt Cyprus Ltd -> Wolt Enterprises Oy (FI) -> DoorDash Inc (US), 100% (see
data/raw/companies).  Stage 1 (the platform itself) therefore sends its net
operating surplus after Cypriot corporate tax to the US; every other stage uses
Frame A's industry-average recipient shares.

Delivery fees paid by customers and couriers' earnings (couriers are mostly
self-employed) are outside this example: it follows only the restaurant's
commission.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ..accounts import industry_recipient_shares
from ..io_model import solve
from ..model import frame_a
from ..model.frame_b import import_origin
from ..model.suiot import build

YEAR = 2022
FEE = 20.0
PRODUCT = "CPA_J62-63"
OWNER_COUNTRY = "US"  # ultimate controlling unit of Wolt Cyprus (company layer)
THETA_FIRM = 1.0


def run(tensor: pd.DataFrame) -> pd.DataFrame:
    table, va_rows, _ = build(YEAR)
    res = solve(table)
    i = res.labels.index(PRODUCT)
    f = np.zeros(len(res.labels))
    f[i] = FEE
    x = res.L @ f  # output needed along the chain
    direct = np.zeros_like(x)
    direct[i] = FEE  # stage 1: the platform's own output
    indirect = x - direct

    rows = []
    # Stage 1: the platform.  Split its value added with the industry's income components.
    comp = va_rows.loc[PRODUCT]
    va1 = res.va_coef[i] * FEE
    b1g = comp["B1G"]
    d1, otp, cfc = comp["D1"] / b1g, comp["D29X39"] / b1g, comp["P51C"] / b1g
    gos = 1.0 - d1 - otp  # residual, so the published (rounded) components exhaust GVA exactly
    tau = frame_a.STATUTORY_CIT[YEAR]
    nos = va1 * (gos - cfc)
    rows += [
        ("1 platform", "Cyprus labour (platform staff)", "CY", va1 * d1),
        ("1 platform", "Cyprus taxes on production", "CY", va1 * otp),
        ("1 platform", "Cyprus: depreciation of platform capital", "CY", va1 * cfc),
        (
            "1 platform",
            "Cyprus corporate income tax on platform profit",
            "CY",
            nos * tau,
        ),
        (
            "1 platform",
            "Foreign capital income (ultimate owner)",
            OWNER_COUNTRY,
            nos * (1 - tau) * THETA_FIRM,
        ),
        (
            "1 platform",
            "Profit to non-foreign owners",
            "CY",
            nos * (1 - tau) * (1 - THETA_FIRM),
        ),
    ]
    # Stage 2+: suppliers along the chain, with industry-average recipient shares.
    shares = industry_recipient_shares(tensor)
    shares.index = ["CPA_" + k for k in shares.index]
    shares = shares.reindex(res.labels).fillna(0.0)
    shares.loc[shares.sum(axis=1) == 0, "CY"] = 1.0  # no GVA in Frame A: nothing routed abroad
    va_ind = res.va_coef * indirect
    for lab, v in zip(res.labels, va_ind):
        if abs(v) <= 1e-12:  # keep negative VA (e.g. loss-making H51): skipping it would overstate the fee
            continue
        for p, s in shares.loc[lab].items():
            if abs(s) > 1e-12:
                who = (
                    "Cyprus suppliers' value added"
                    if p == "CY"
                    else "Foreign income from Cypriot suppliers"
                )
                rows.append(
                    ("2 suppliers", f"{who} ({lab.removeprefix('CPA_')})", p, v * s)
                )
    imp = res.Am @ x
    origin = import_origin(YEAR, res.labels)
    for lab, v in zip(res.labels, imp):
        if v <= 1e-12:
            continue
        for p, s in origin.loc[lab].items():
            if s > 0:
                rows.append(
                    (
                        "3 imports",
                        f"Imported inputs ({lab.removeprefix('CPA_')})",
                        p,
                        v * s,
                    )
                )
    rows.append(
        ("4 taxes", "Taxes on products paid on inputs", "CY", float(res.tax_coef @ x))
    )
    out = pd.DataFrame(rows, columns=["stage", "component", "recipient", "eur"])
    total = out.eur.sum()
    if abs(total - FEE) > 1e-9:
        raise AssertionError(f"platform example does not exhaust the fee: {total}")
    out["status"] = "illustrative"
    return out


def summary(out: pd.DataFrame) -> dict:
    s = {
        "fee_eur": FEE,
        "year": YEAR,
        "stays_in_cyprus": round(out[out.recipient == "CY"].eur.sum(), 2),
        "foreign_capital_income_platform_owner": round(
            out[out.component.str.startswith("Foreign capital income")].eur.sum(), 2
        ),
        "foreign_income_via_suppliers": round(
            out[(out.stage == "2 suppliers") & (out.recipient != "CY")].eur.sum(), 2
        ),
        "imported_inputs": round(out[out.stage == "3 imports"].eur.sum(), 2),
        "cyprus_labour_platform": round(
            out[out.component.str.startswith("Cyprus labour")].eur.sum(), 2
        ),
        "cyprus_rent_real_estate": round(
            out[out.component.str.contains(r"\(L68")]
            .query("recipient == 'CY'")
            .eur.sum(),
            2,
        ),
        "status": "illustrative — industry-average cost structure + documented ownership chain; not in headline results",
    }
    s["check_sum"] = round(
        s["stays_in_cyprus"]
        + s["foreign_capital_income_platform_owner"]
        + s["foreign_income_via_suppliers"]
        + s["imported_inputs"],
        2,
    )
    return s


if __name__ == "__main__":
    t = pd.read_parquet("data/processed/recipient_tensor.parquet").rename(
        columns={"recipient": "partner"}
    )
    t = t[t.year == YEAR]
    out = run(t)
    Path("data/processed").mkdir(exist_ok=True, parents=True)
    out.to_csv("data/processed/example_platform_fee.csv", index=False)
    s = summary(out)
    Path("data/processed/example_platform_fee.json").write_text(json.dumps(s, indent=2))
    print(json.dumps(s, indent=2))
