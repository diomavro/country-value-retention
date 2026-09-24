"""Ownership resolution: recursive, no double counting, never invents a country."""

import pandas as pd
import pytest

from cvr.ownership import (
    UNRESOLVED,
    OwnershipError,
    build_graph,
    country_shares,
    ultimate_controlling_unit,
    resolve,
)


def ents(rows):
    cols = ["entity_id", "country", "is_terminal", "is_dispersed"]
    return pd.DataFrame([r + ("",) * (4 - len(r)) for r in rows], columns=cols)


def edges(rows):
    return pd.DataFrame(
        rows, columns=["parent_entity_id", "child_entity_id", "share_pct"]
    )


def shares(g):
    cs = country_shares(resolve(g))
    return {(r.entity_id, r.owner_country): round(r.share, 10) for r in cs.itertuples()}


def test_resolves_through_foreign_holding_to_ultimate_owner():
    # CY sub -> NL holding -> US parent (public): attribute to US, not NL.
    g = build_graph(
        ents(
            [
                ("cy", "CY", ""),
                ("nl", "NL", ""),
                ("us", "US", ""),
                ("float_us", "US", "true"),
            ]
        ),
        edges([("nl", "cy", 100), ("us", "nl", 100), ("float_us", "us", 100)]),
    )
    s = shares(g)
    assert s[("cy", "US")] == 1.0
    assert ("cy", "NL") not in s
    u = ultimate_controlling_unit(g, "cy", "CY")
    assert (u["uci_country"], u["first_foreign_parent_country"], u["uci_status"]) == ("US", "NL", "terminal_owner")


def test_undocumented_owners_become_unresolved_not_a_guess():
    g = build_graph(
        ents([("cy", "CY", ""), ("gr", "GR", "true")]),
        edges([("gr", "cy", 60)]),
    )
    s = shares(g)
    assert s[("cy", "GR")] == 0.6
    assert s[("cy", UNRESOLVED)] == 0.4


def test_blank_terminal_flag_is_not_truthy():
    # An entity with no owners and a blank flag is 100% unresolved, not a terminal owner.
    g = build_graph(ents([("cy", "CY", float("nan"))]), edges([]))
    assert shares(g) == {("cy", UNRESOLVED): 1.0}


def test_diamond_ownership_counted_once():
    # Two routes to the same ultimate owner must add, not duplicate beyond 100%.
    g = build_graph(
        ents(
            [("cy", "CY", ""), ("a", "GR", ""), ("b", "GR", ""), ("top", "DE", "true")]
        ),
        edges([("a", "cy", 50), ("b", "cy", 50), ("top", "a", 100), ("top", "b", 100)]),
    )
    assert {k: v for k, v in shares(g).items() if k[0] == "cy"} == {("cy", "DE"): 1.0}


def test_cross_holding_cycle_resolves_to_outside_owners():
    # a owns 20% of b, b owns 20% of a; remaining shares held by X (a) and Y (b).
    g = build_graph(
        ents(
            [("a", "CY", ""), ("b", "CY", ""), ("x", "RU", "true"), ("y", "US", "true")]
        ),
        edges([("b", "a", 20), ("x", "a", 80), ("a", "b", 20), ("y", "b", 80)]),
    )
    s = shares(g)
    assert s[("a", "RU")] + s[("a", "US")] == pytest.approx(1.0)
    assert s[("a", "RU")] == pytest.approx(0.8 / 0.96)


def test_overallocated_owners_rejected():
    with pytest.raises(OwnershipError):
        build_graph(
            ents([("c", "CY", ""), ("p", "GR", "1"), ("q", "GR", "1")]),
            edges([("p", "c", 70), ("q", "c", 40)]),
        )


def test_duplicate_edge_rejected():
    with pytest.raises(OwnershipError):
        build_graph(
            ents([("c", "CY", ""), ("p", "GR", "1")]),
            edges([("p", "c", 30), ("p", "c", 30)]),
        )


def test_terminal_with_owners_rejected():
    with pytest.raises(OwnershipError):
        build_graph(ents([("c", "CY", "1"), ("p", "GR", "1")]), edges([("p", "c", 30)]))


def test_uci_stops_at_listed_parent_with_dispersed_owners():
    # Wolt-type chain: CY -> FI -> US listed company owned by dispersed float.
    # Control-level attribution is the US parent (OECD UCI), even though the
    # look-through beneficial owners (the float) are unresolved.
    g = build_graph(
        ents([("cy", "CY", ""), ("fi", "FI", ""), ("us", "US", ""), ("float", "UNRESOLVED", "1", "1")]),
        edges([("fi", "cy", 100), ("us", "fi", 100), ("float", "us", 85)]),
    )
    u = ultimate_controlling_unit(g, "cy", "CY")
    assert (u["uci_entity"], u["uci_country"], u["uci_status"]) == ("us", "US", "uncontrolled_company")
    assert shares(g)[("cy", UNRESOLVED)] == 1.0


def test_firm_with_unknown_owners_is_not_presumed_domestic():
    g = build_graph(ents([("cy", "CY", "")]), edges([]))
    assert ultimate_controlling_unit(g, "cy", "CY")["uci_country"] == UNRESOLVED


def _write_company_layer(tmp_path, entities, edges):
    import cvr.model.ownership_data as od

    ent = pd.DataFrame(entities, columns=["entity_id", "legal_name", "country_of_incorporation", "sector", "source_url", "confidence"]).assign(nace_code="")
    edg = pd.DataFrame(edges, columns=["child_entity_id", "parent_entity_id", "share_pct", "share_type", "confidence"])
    ent.to_csv(tmp_path / "entities.csv", index=False)
    edg.to_csv(tmp_path / "ownership_edges.csv", index=False)
    od.RAW = tmp_path
    return od


def test_voting_disclosures_do_not_drop_free_float_from_control(tmp_path, monkeypatch):
    # A listed holding: 64% free float (equity) + 36% in major-holder voting disclosures.
    # Control must see the whole register: no majority holder -> uncontrolled, country IE.
    import cvr.model.ownership_data as od

    monkeypatch.setattr(od, "RAW", tmp_path)
    _write_company_layer(
        tmp_path,
        [
            ("CY_BANK", "bank", "CY", "banking", "u", "high"),
            ("IE_HOLD", "holding", "IE", "holding", "u", "high"),
            ("FF", "float", "UNRESOLVED", "free_float", "u", "high"),
            ("US_FUND", "fund", "US", "fund", "u", "high"),
        ],
        [("CY_BANK", "IE_HOLD", 100, "equity", "high"), ("IE_HOLD", "FF", 64, "equity", "high"), ("IE_HOLD", "US_FUND", 36, "voting", "high")],
    )
    summ, _ = od.resolve_cyprus()
    row = summ.set_index("entity_id").loc["CY_BANK"]
    assert (row.uci_country, row.uci_status) == ("IE", "uncontrolled_company")


def test_separated_voting_rights_decide_control(tmp_path, monkeypatch):
    # Economic rights with a local partnership, votes with a foreign entity: control follows votes.
    import cvr.model.ownership_data as od

    monkeypatch.setattr(od, "RAW", tmp_path)
    _write_company_layer(
        tmp_path,
        [
            ("CY_FIRM", "firm", "CY", "professional_services", "u", "high"),
            ("CY_PARTNERS", "partnership", "CY", "partners", "u", "high"),
            ("BE_NET", "network", "BE", "holding", "u", "high"),
        ],
        [("CY_FIRM", "CY_PARTNERS", 100, "equity", "high"), ("CY_FIRM", "BE_NET", 100, "voting", "high")],
    )
    summ, detail = od.resolve_cyprus()
    row = summ.set_index("entity_id").loc["CY_FIRM"]
    assert row.uci_entity == "BE_NET"
    assert row.domestic == 1.0  # income still follows the economic rights
