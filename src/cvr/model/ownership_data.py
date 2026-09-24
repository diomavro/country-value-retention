"""Load the company layer and resolve ultimate ownership of Cyprus operating firms.

Terminal owners (ownership chains stop here): states, natural persons, families,
partnerships, pension funds, foundations, dispersed free float, and investment
funds/fund managers (their end investors are not observable; a fund is
attributed to its domicile, as in FDI statistics).  A holding company with no
documented owners is *not* terminal: it resolves to UNRESOLVED.

Edges without a published percentage are excluded from the arithmetic (the
share they represent stays UNRESOLVED) and are listed in the output so the
missing figure is visible rather than guessed.

Country of a natural person is UNRESOLVED unless residence is documented;
nationality is never used.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..ownership import (
    UNRESOLVED,
    build_graph,
    country_shares,
    ultimate_controlling_unit,
    resolve,
)

RAW = Path("data/raw/companies")
TERMINAL_SECTORS = {
    "person",
    "family",
    "state",
    "free_float",
    "partners",
    "pension_fund",
    "foundation",
    "fund",
    "fund_manager",
}
# Firms whose activity is outside the territory covered by Cyprus national accounts.
EXCLUDE = {"CY_FOOD_BASKET"}
HOME = "CY"


def load() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return (entities, edges carrying economic ownership, edges without a usable share)."""
    e, d, unpriced, _ = _load_all()
    return e, d, unpriced


def _load_all() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """(entities, economic edges, edges without a usable share, control edges)."""
    e = pd.read_csv(RAW / "entities.csv")
    d = pd.read_csv(RAW / "ownership_edges.csv")
    d["share_pct"] = pd.to_numeric(d["share_pct"], errors="coerce").astype(float)
    e = e.rename(columns={"country_of_incorporation": "country"})
    e["country"] = e["country"].fillna(UNRESOLVED)
    e["is_terminal"] = e["sector"].isin(TERMINAL_SECTORS)
    e["is_dispersed"] = e["sector"] == "free_float"
    # Explicit "UNRESOLVED" parent rows mark gaps; the resolver derives the same residual
    # from documented shares, so keeping them would count the gap twice.
    d = d[d["parent_entity_id"] != UNRESOLVED].copy()
    # An entity with ANY recorded owner (even with no published share) is not a terminal owner:
    # its undocumented share must resolve to UNRESOLVED, not to the entity's own country
    # (e.g. the EY partnership, whose equity parent EY Europe has no published share).
    has_owner = set(d["child_entity_id"])
    e.loc[e["entity_id"].isin(has_owner), "is_terminal"] = False
    unpriced = d[d["share_pct"].isna()].copy()
    d = d[d["share_pct"].notna()].copy()
    # Income follows economic rights.  Voting-rights disclosures (TR-1 notifications,
    # statutory bodies without share capital) are presumed economic under one-share-one-vote
    # UNLESS equity + voting stakes in the same firm exceed 100%, which reveals that
    # economic and voting rights are held separately (e.g. EY Cyprus: economic rights with
    # the Cypriot partnership, votes with EY Europe SRL).  Then only equity counts.
    tot = d.groupby(["child_entity_id", "share_type"])["share_pct"].sum().unstack(fill_value=0.0)
    split = set(tot.index[(tot.get("equity", 0) > 0) & (tot.get("equity", 0) + tot.get("voting", 0) > 100 + 1e-6)])
    separated = (d["share_type"] == "voting") & d["child_entity_id"].isin(split)
    unpriced = pd.concat([unpriced, d[separated]])
    # Control graph (OECD UCI): the same stakes, except where voting and economic rights are
    # separated - there the votes decide control (e.g. EY Cyprus: EY Europe SRL holds the votes;
    # DoorDash: the founder's super-voting shares).  Free float and other equity stay in.
    control = pd.concat([d[~d["child_entity_id"].isin(split)], d[separated]], ignore_index=True)
    control = control.sort_values("share_type").drop_duplicates(["parent_entity_id", "child_entity_id"], keep="first")
    d = d[~separated].copy()
    d["presumption"] = (d["share_type"] == "voting").map({True: "voting rights presumed economic (one share, one vote)", False: ""})
    # Same parent disclosed under both types: keep the equity figure once.
    d = d.sort_values("share_type").drop_duplicates(["parent_entity_id", "child_entity_id"], keep="first")
    return e, d, unpriced, control


def operating_firms(e: pd.DataFrame) -> pd.DataFrame:
    non_operating = TERMINAL_SECTORS | {"holding", "state_holding", "dissolved"}
    ops = e[
        (e["country"] == HOME)
        & ~e["sector"].isin(non_operating)
        & ~e["entity_id"].isin(EXCLUDE)
    ]
    return ops


def resolve_cyprus() -> tuple[pd.DataFrame, pd.DataFrame]:
    e, d, unpriced, control = _load_all()
    g = build_graph(e, d)
    gc = build_graph(e, control)  # control graph (votes where disclosed) for the UCI walk
    shares = country_shares(resolve(g))
    ops = operating_firms(e)
    s = shares[shares.entity_id.isin(ops.entity_id)].copy()
    s["class"] = s["owner_country"].map(
        lambda c: (
            "domestic"
            if c == HOME
            else ("unresolved" if c == UNRESOLVED else "foreign")
        )
    )
    summary = s.pivot_table(
        index="entity_id",
        columns="class",
        values="share",
        aggfunc="sum",
        fill_value=0.0,
    )
    for c in ("domestic", "foreign", "unresolved"):
        if c not in summary:
            summary[c] = 0.0
    chains = pd.DataFrame(
        [
            {"entity_id": x, **ultimate_controlling_unit(gc, x, HOME)}
            for x in ops.entity_id
        ]
    )
    summary = (
        ops[["entity_id", "legal_name", "sector", "nace_code", "confidence"]]
        .merge(summary.reset_index(), on="entity_id", how="left")
        .merge(chains, on="entity_id", how="left")
    )
    summary["unpriced_parent_edges"] = (
        summary.entity_id.map(unpriced.groupby("child_entity_id").size())
        .fillna(0)
        .astype(int)
    )
    return summary, s


if __name__ == "__main__":
    summ, detail = resolve_cyprus()
    pd.set_option("display.width", 220)
    cols = ["entity_id", "sector", "domestic", "foreign", "unresolved", "uci_country", "uci_status", "first_foreign_parent_country"]
    print(summ[cols].round(3).to_string())


def theta_calibration() -> pd.DataFrame:
    """Non-resident share of equity in foreign-controlled Cypriot firms (calibrates theta).

    theta_firm = integrated share of the firm held by non-resident units: ownership is traced
    through Cypriot holding companies and stops at the first non-resident owner on every path
    (all minority foreign holders count, not only the controlling chain).  Undocumented shares
    count as not foreign, so theta_firm is a lower bound.
    Sample: operating firms more than 50% held by non-residents, excluding dissolved firms and
    firms whose foreign stake rests on a low-confidence edge; firms of the same group are
    averaged first so a group counts once.
    """
    e, d, _ = load()
    stop = e.copy()
    stop.loc[~stop["country"].isin([HOME, UNRESOLVED]), "is_terminal"] = True
    d_stop = d[~d["child_entity_id"].isin(stop.loc[stop.is_terminal & ~stop.country.isin([HOME, UNRESOLVED]), "entity_id"])]
    shares = country_shares(resolve(build_graph(stop, d_stop)))
    ops = operating_firms(e)
    low = set(d.loc[d["confidence"].astype(str).str.lower().eq("low"), "child_entity_id"])
    rows = []
    for x in ops.entity_id:
        sx = shares[shares.entity_id == x]
        th = float(sx[~sx.owner_country.isin([HOME, UNRESOLVED])].share.sum())
        if th <= 0.5 or x in low:
            continue
        group = _first_nonresident_parent(d, e, x)
        rows.append({"entity_id": x, "group": group, "theta": th})
    t = pd.DataFrame(rows)
    return t.assign(group_theta=t.groupby("group").theta.transform("mean"))


def _first_nonresident_parent(d: pd.DataFrame, e: pd.DataFrame, x: str) -> str:
    """Group key for theta: the first non-resident owner on the largest-holder path, so firms held
    through Cypriot intermediate holdings of the same foreign group count once."""
    country = e.set_index("entity_id")["country"]
    node, seen = x, {x}
    while True:
        top = d[d.child_entity_id == node].sort_values("share_pct", ascending=False)
        if top.empty:
            return node
        node = top.parent_entity_id.iloc[0]
        if node in seen or country.get(node) not in (HOME, UNRESOLVED):
            return node
        seen.add(node)


def theta_central() -> float:
    t = theta_calibration()
    return float(t.drop_duplicates("group").group_theta.mean())
