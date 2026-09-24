"""Ownership graph and recursive ultimate-owner resolution.

Edges point parent -> child with the parent's equity share in the child.
Integrated (ultimate) ownership is W = S (I - S)^-1 restricted to terminal
owners, where S[p, c] is the direct share of p in c.  Cross-holdings are
handled by the matrix inverse rather than by path enumeration, so no chain
is counted twice.

Any part of an entity whose owners are not documented (direct shares summing
to less than 100%) is assigned to an explicit terminal node
``UNRESOLVED::<entity>``.  Its country is ``UNRESOLVED``; it is never guessed.
"""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np
import pandas as pd

UNRESOLVED = "UNRESOLVED"
SHARE_TOL = 1e-6


class OwnershipError(ValueError):
    pass


@dataclass(frozen=True)
class UltimateOwnership:
    entity_id: str
    owner_id: str
    owner_country: str
    share: float  # 0..1 integrated share of entity ultimately held by owner


def _truthy(v: object) -> bool:
    """CSV-safe boolean: blank/NaN cells are False (bool(float('nan')) is True)."""
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in {"true", "1", "1.0", "yes", "y"}


def build_graph(entities: pd.DataFrame, edges: pd.DataFrame) -> nx.DiGraph:
    """entities: entity_id, country (+ any attributes); edges: parent_entity_id, child_entity_id, share_pct."""
    dup = edges.duplicated(["parent_entity_id", "child_entity_id"], keep=False)
    if dup.any():
        raise OwnershipError(
            f"duplicate ownership edges: {edges.loc[dup, ['parent_entity_id', 'child_entity_id']].values.tolist()}"
        )
    if (edges["share_pct"] <= 0).any() or (edges["share_pct"] > 100 + SHARE_TOL).any():
        raise OwnershipError("share_pct must lie in (0, 100]")
    if (edges["parent_entity_id"] == edges["child_entity_id"]).any():
        raise OwnershipError(
            "self-ownership edge (treasury shares must be netted out before loading)"
        )
    known = set(entities["entity_id"])
    missing = (set(edges["parent_entity_id"]) | set(edges["child_entity_id"])) - known
    if missing:
        raise OwnershipError(f"edges reference unknown entities: {sorted(missing)}")

    g = nx.DiGraph()
    for rec in entities.to_dict("records"):
        rec["is_terminal"] = _truthy(rec.get("is_terminal"))
        rec["is_dispersed"] = _truthy(rec.get("is_dispersed"))
        g.add_node(rec["entity_id"], **rec)
    for rec in edges.to_dict("records"):
        g.add_edge(
            rec["parent_entity_id"],
            rec["child_entity_id"],
            share=rec["share_pct"] / 100.0,
            **rec,
        )

    for node in g.nodes:
        if g.nodes[node].get("is_terminal", False) and g.in_degree(node) > 0:
            raise OwnershipError(f"{node} is flagged terminal but has recorded owners")
        total = sum(d["share"] for _, _, d in g.in_edges(node, data=True))
        if total > 1 + SHARE_TOL:
            raise OwnershipError(f"direct owners of {node} hold {total:.4%} > 100%")
    return g


def _with_unresolved(g: nx.DiGraph) -> nx.DiGraph:
    """Add an UNRESOLVED terminal for every entity whose documented owners hold < 100%.

    Entities with no recorded owners at all are terminal *only* if flagged
    ``is_terminal`` (states, natural persons, dispersed-float nodes); otherwise
    100% of them is unresolved.
    """
    h = g.copy()
    for node in list(g.nodes):
        attrs = g.nodes[node]
        if bool(attrs.get("is_terminal", False)):
            continue
        total = sum(d["share"] for _, _, d in g.in_edges(node, data=True))
        residual = 1.0 - total
        if residual > SHARE_TOL:
            u = f"{UNRESOLVED}::{node}"
            h.add_node(
                u,
                entity_id=u,
                country=UNRESOLVED,
                is_terminal=True,
                legal_name=f"Undocumented owners of {node}",
            )
            h.add_edge(
                u,
                node,
                share=residual,
                share_pct=residual * 100,
                source="derived: residual of documented owners",
            )
    return h


def resolve(g: nx.DiGraph) -> list[UltimateOwnership]:
    h = _with_unresolved(g)
    nodes = list(h.nodes)
    idx = {n: i for i, n in enumerate(nodes)}
    S = np.zeros((len(nodes), len(nodes)))
    for p, c, d in h.edges(data=True):
        S[idx[p], idx[c]] = d["share"]
    try:
        T = np.linalg.inv(np.eye(len(nodes)) - S)  # sum over all path lengths
    except np.linalg.LinAlgError as e:  # only if a cycle holds 100% of itself
        raise OwnershipError("ownership cycle with no outside owners") from e
    terminals = [n for n in nodes if h.in_degree(n) == 0]
    out: list[UltimateOwnership] = []
    for ent in g.nodes:
        if h.in_degree(ent) == 0:
            continue  # terminal owner itself
        j = idx[ent]
        for tnode in terminals:
            share = float(T[idx[tnode], j])
            if share > SHARE_TOL:
                out.append(
                    UltimateOwnership(
                        ent,
                        tnode,
                        str(h.nodes[tnode].get("country", UNRESOLVED)),
                        share,
                    )
                )
    _check_integrated(out, g)
    missing = [n for n in g.nodes if h.in_degree(n) > 0 and n not in {o.entity_id for o in out}]
    if missing:  # an entity must never silently drop out of the results
        raise OwnershipError(f"no ultimate owners resolved for {missing[:5]}")
    return out


def _check_integrated(out: list[UltimateOwnership], g: nx.DiGraph) -> None:
    tot: dict[str, float] = {}
    for o in out:
        tot[o.entity_id] = tot.get(o.entity_id, 0.0) + o.share
    for ent, s in tot.items():
        if abs(s - 1.0) > 1e-6:
            raise OwnershipError(f"ultimate owners of {ent} sum to {s:.6f}, not 1")


def country_shares(out: list[UltimateOwnership]) -> pd.DataFrame:
    df = pd.DataFrame([o.__dict__ for o in out])
    if df.empty:
        return pd.DataFrame(columns=["entity_id", "owner_country", "share"])
    return df.groupby(["entity_id", "owner_country"], as_index=False)["share"].sum()


def _unknown_residence_bloc(g: nx.DiGraph, node: str) -> float:
    """Share of `node` held directly by natural persons or families whose residence is unknown."""
    return sum(
        d["share"]
        for p, _, d in g.in_edges(node, data=True)
        if g.nodes[p].get("sector") in {"person", "family"} and g.nodes[p].get("country", UNRESOLVED) == UNRESOLVED
    )


def ultimate_controlling_unit(g: nx.DiGraph, entity: str, home: str) -> dict[str, object]:
    """Follow majority (>50%) ownership upward to the unit no one else controls (OECD UCI).

    The stopping unit's country is used only if its own ownership is documented as
    uncontrolled (a terminal owner, or documented owners covering >= 50% with none
    holding a majority).  A firm whose owners are simply unknown resolves to UNRESOLVED.
    Also reports the first foreign parent met on the way (to contrast immediate vs
    ultimate attribution).
    """
    node, first_foreign, seen = entity, None, {entity}
    while True:
        parents = [(p, d["share"]) for p, _, d in g.in_edges(node, data=True)]
        # Dispersed free float is many small holders: it never controls, whatever its total.
        maj = [(p, s) for p, s in parents if s > 0.5 and not _truthy(g.nodes[p].get("is_dispersed"))]
        if not maj or maj[0][0] in seen:
            break
        p = maj[0][0]
        seen.add(p)
        if first_foreign is None and g.nodes[p].get("country") not in (home, UNRESOLVED):
            first_foreign = g.nodes[p].get("country")
        node = p
    attrs = g.nodes[node]
    documented = sum(s for _, s in [(p, d["share"]) for p, _, d in g.in_edges(node, data=True)])
    if attrs.get("is_terminal", False):
        status, country = "terminal_owner", attrs.get("country", UNRESOLVED)
    elif _unknown_residence_bloc(g, node) >= 0.5:
        # persons/families of undocumented residence jointly hold a majority: the controller's
        # country is unknown (never the firm's own country by default)
        status, country = "controlled_by_persons_of_unknown_residence", UNRESOLVED
    elif documented >= 0.5:
        status, country = "uncontrolled_company", attrs.get("country", UNRESOLVED)
    else:
        status, country = "undocumented_owners", UNRESOLVED
    return {
        "uci_entity": node,
        "uci_country": country,
        "uci_status": status,
        "first_foreign_parent_country": first_foreign,
        "control_depth": len(seen) - 1,
    }
