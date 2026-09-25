# Contributing

Contributions are welcome, especially new countries, better sources and corrections to the ownership data.

## Ground rules

1. **Never fabricate data.** Every observation needs a source URL, reference year, retrieval date, method and confidence level (`src/cvr/provenance.py` enforces this). If something is unknown, record it as unresolved.
2. **Residence, not nationality.** Do not infer an owner's country from their name or citizenship.
3. **Identities are tests.** Any change must keep `make validate` green. A new mechanism needs a unit test that fails when the accounting rule it protects is broken.
4. **One source of truth.** Numbers in the paper and on the website are generated. Do not type them by hand.

## Adding a country

Frame A already runs for other EU countries from Eurostat (`src/cvr/compare.py`, methodology §9).

1. Add the country code in five places: the `--geo` list of the comparison download in the `Makefile`; `COUNTRIES` in `src/cvr/compare.py`; the OECD tax-rate query in `src/cvr/ingest/oecd.py` and its code map in `frame_a._oecd_cit` (every country other than Cyprus needs a statutory rate); `COUNTRY_NAMES` in `src/cvr/paper_tables.py`; and `COUNTRIES` in `website/src/components/CompareView.tsx`.
2. Changing the `--geo` list writes new file names; delete the old files in `data/raw/eurostat_eu/` and their manifest rows first (the estimator stops if two files disagree). Then run `make ingest process` and `python -m cvr.compare`. Suppressed inputs are reported in `data/processed/comparison_skipped.parquet`; do not fill them in.
3. Update the prose that names the comparison countries (the `src/cvr/compare.py` docstring, the introduction in `CompareView.tsx`, the country list in `src/cvr/paper_numbers.py` and the paper section), then run `make paper dashboard`.
4. θ stays an assumption unless you add the country's ownership filings. Frame B (input–output) is still Cyprus-only.

## Correcting ownership data

Edit the sector fragments in `data/raw/companies/_fragments/` (never `entities.csv` / `ownership_edges.csv` directly: `_build/merge.py` and `_build/corrections.py` regenerate them). Include the document URL, the date, the source tier (1 = official filing … 4 = secondary) and a confidence level. Name natural persons only when a Tier 1–2 filing discloses them. Run `python data/raw/companies/_build/merge.py`, `pytest tests/test_ownership.py` and `make model`.

## Development

```bash
uv sync
env -u PYTHONPATH uv run pytest -q
```
