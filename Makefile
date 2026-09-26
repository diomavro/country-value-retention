# The user's shell may export PYTHONPATH pointing at ~/.local; unset it so the
# locked .venv is the only package source (reproducibility).
UV := env -u PYTHONPATH uv run

.PHONY: all ingest process model validate test paper dashboard figures clean

all: ingest process model validate paper

ingest:            ## download official sources (CYSTAT PxWeb, Eurostat API, CBC) -> data/raw
	$(UV) python -m cvr.ingest.cystat_fetch
	$(UV) python -m cvr.ingest.eurostat --geo CY
	$(UV) python -m cvr.ingest.eurostat --geo MT,IE,LU,NL,EL,PT --raw-dir data/raw/eurostat_eu --no-eu-aggregate \
		--only gva_a64,sector_nf,bop_pi_sector,bop_rem,fats_activ,fats_g1a_08
	$(UV) python -m cvr.ingest.oecd
	$(UV) python -m cvr.ingest.ec_taxation
	$(UV) python -m cvr.ingest.ecb
	$(UV) python -m cvr.ingest.cbc

process:           ## verify raw files against manifest checksums, then parse -> data/interim
	$(UV) python -m cvr.ingest.verify
	$(UV) python -m cvr.ingest.cystat

model:             ## Frame A/B, IO indicators, ownership, sensitivity -> data/processed + DuckDB
	$(UV) python -m cvr.catalogue
	$(UV) python -m cvr.pipeline
	$(UV) python -m cvr.compare
	$(UV) python -m cvr.examples.platform

validate:          ## accounting identities + unit tests; non-zero exit on any failure
	$(UV) pytest -q
	$(UV) python -m cvr.validate

figures:
	$(UV) python -m cvr.figures

paper: figures     ## numbers and tables -> paper/, then compile
	$(UV) python -m cvr.paper_numbers
	$(UV) python -m cvr.paper_tables
	cd paper && timeout 300 latexmk -pdf -quiet -interaction=nonstopmode main.tex
	$(UV) python -m cvr.paper_markdown

dashboard:         ## export JSON for the website and build it
	$(UV) python -m cvr.export_web
	cd website && npm install && npm run build

clean:
	rm -rf data/interim data/processed data/cvr.duckdb
