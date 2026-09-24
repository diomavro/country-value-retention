"""Documented corrections applied after merge.py (adversarial review, 2026-09-24).

1. The shareholders of Hellenic Supermarkets Sklavenitis S.A. (a private company) were taken from
   a press article (Tier 3) naming private individuals; those rows were removed from the source
   fragments themselves.  Its owners are left undocumented (UNRESOLVED), not guessed.
2. EPIC's remaining 10% is held by "NJJ affiliates" (NJJ Continental annual report), a group of
   companies, not a natural person: re-coded to an unresolved holding node.
3. Eurobank Cyprus Ltd was dissolved in December 2025: marked 'dissolved' so it is not treated as
   an operating firm (it stays in the graph as a historical node).
"""
import pathlib

import pandas as pd

H = pathlib.Path(__file__).resolve().parents[1]
E = pd.read_csv(H / "entities.csv", dtype=str)
D = pd.read_csv(H / "ownership_edges.csv", dtype=str)

E.loc[E.entity_id == "GR_SKLAVENITIS", "notes"] = "Shareholders not documented in Tier 1-2 sources; a 2016 press split was removed (source quality, privacy)."

if "XX_NJJ_AFFILIATES" not in set(E.entity_id):
    niel = E[E.entity_id == "PERSON_NIEL_FAMILY"].iloc[0].copy()
    niel["entity_id"], niel["legal_name"], niel["sector"], niel["country_of_incorporation"] = "XX_NJJ_AFFILIATES", "NJJ affiliates (companies of the NJJ group, not itemised)", "holding", "UNRESOLVED"
    niel["notes"] = "NJJ Continental annual report: 'remaining 10% are held by NJJ affiliates'."
    E = pd.concat([E, niel.to_frame().T], ignore_index=True)
D.loc[(D.child_entity_id == "CY_EPIC") & (D.parent_entity_id == "PERSON_NIEL_FAMILY"), "parent_entity_id"] = "XX_NJJ_AFFILIATES"

E.loc[E.entity_id == "CY_EUROBANK_CYPRUS_LTD", "sector"] = "dissolved"

assert not (set(D.child_entity_id) | set(D.parent_entity_id)) - set(E.entity_id) - {"UNRESOLVED"}
E.to_csv(H / "entities.csv", index=False)
D.to_csv(H / "ownership_edges.csv", index=False)
print("corrections applied:", len(E), "entities;", len(D), "edges")
