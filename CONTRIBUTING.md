# Contributing

Contributions are welcome, especially new countries, better sources and corrections to the ownership data.

## Ground rules

1. **Never fabricate data.** Every observation needs a source URL, reference year, retrieval date, method and confidence level (`src/cvr/provenance.py` enforces this). If something is unknown, record it as unresolved.
2. **Residence, not nationality.** Do not infer an owner's country from their name or citizenship.
3. **Identities are tests.** Any change must keep `make validate` green. A new mechanism needs a unit test that fails when the accounting rule it protects is broken.
4. **One source of truth.** Numbers in the paper and on the website are generated. Do not type them by hand.

## Adding a country

1. `python -m cvr.ingest.eurostat --geo <CC>` downloads the Eurostat inputs.
2. Replace the CYSTAT-specific sector-account loader with `nasa_10_nf_tr` (rest-of-world sector S2), and the SIOT loader with `naio_10_cp1700` (domestic and imported blocks).
3. Run `make model validate` and add a reconciliation check for the country's GDP and GNI.

## Correcting ownership data

Edit the sector fragments in `data/raw/companies/_fragments/` (never `entities.csv` / `ownership_edges.csv` directly: `_build/merge.py` and `_build/corrections.py` regenerate them). Include the document URL, the date, the source tier (1 = official filing … 4 = secondary) and a confidence level. Name natural persons only when a Tier 1–2 filing discloses them. Run `python data/raw/companies/_build/merge.py`, `pytest tests/test_ownership.py` and `make model`.

## Development

```bash
uv sync
env -u PYTHONPATH uv run pytest -q
```
