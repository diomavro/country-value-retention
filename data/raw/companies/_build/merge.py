"""Merge sector fragments into entities.csv / ownership_edges.csv and run integrity checks."""
import glob, pathlib, pandas as pd
H = pathlib.Path(__file__).resolve().parents[1]
E = pd.concat([pd.read_csv(f, dtype=str) for f in sorted(glob.glob(str(H/'_fragments/*_entities.csv')))])
D = pd.concat([pd.read_csv(f, dtype=str) for f in sorted(glob.glob(str(H/'_fragments/*_edges.csv')))])
E = E.drop_duplicates('entity_id', keep='first')          # identical STATE_CY / US_BLACKROCK rows
E = E[E.entity_id != 'FAMILY_PAPAELLINAS']                 # unsourced, unreferenced placeholder
ids = set(E.entity_id)
bad = (set(D.child_entity_id) | set(D.parent_entity_id)) - ids - {'UNRESOLVED'}
assert not bad, bad
assert E.source_url.notna().all()
# edges may lack a URL only if they merely flag an unresolved parent with no share
assert D[D.source_url.isna()].pipe(lambda x: (x.parent_entity_id == 'UNRESOLVED') & x.share_pct.isna()).all()
p = pd.to_numeric(D.share_pct, errors='coerce')
assert (D[p.notna()].source_url.notna()).all()
s = p[D.share_type == 'equity'].groupby(D.child_entity_id[D.share_type == 'equity']).sum()
assert (s <= 100.01).all(), s[s > 100.01]
E.to_csv(H/'entities.csv', index=False); D.to_csv(H/'ownership_edges.csv', index=False)
print(len(E), 'entities;', len(D), 'edges')
import runpy; runpy.run_path(str(H / "_build" / "corrections.py"))  # documented post-merge corrections
