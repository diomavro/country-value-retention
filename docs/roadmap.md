# Roadmap: more accurate, more complete

What would make the estimates more accurate (A), more complete (C), or easier to trust and reuse (R).
Each item names the gap it closes (limitation numbers refer to `docs/limitations.md`), the data, and how we know it is done.
Items marked **agent** can be done from public data in this repository; items marked **human** need an account, a request under the author's name, or a decision.

## Accuracy: fix what the current numbers get wrong

| # | Item | Gap closed | Data | Done when | Who |
|---|---|---|---|---|---|
| A1 | **Effective corporate tax rate** instead of the statutory rate | Limitation 3 (tax overstated: IP box, notional interest) | Eurostat `nasa_10_nf_tr`, S11 D51 paid / S11 net operating surplus (already downloaded) | Central series uses the effective rate, statutory becomes a variant; validator recomputes the rate | agent |
| A2 | **Rent of dwellings owned by non-residents** | Limitation 1 (unmeasured outflow counted as retained) | Eurostat `bop_fdi6_inc`, real estate (NACE L); CYSTAT dwelling statistics | New mechanism booked to L68, bounded by its surplus; retention falls or the bound is shown to be small | agent |
| A3 | **FDI income from 10–50% stakes** | Limitation 1 | `bop_fdi6_inc` by industry vs FATS (majority control) | Bounded estimate or sensitivity variant with a documented range | agent |
| A4 | **Surplus-weighted θ and more firms** | Limitation 2, 15 | GLEIF API (legal-entity parents, free), company filings | θ weighted by operating surplus; calibration sample at least doubled; sensitivity updated | agent |
| A5 | **Bank profit: reconcile BoP and FATS** | Limitation 12 (2.2% of GDP gap in 2023) | ECB data API (supervisory banking statistics for CY), banks' annual reports | Gap explained line by line or narrowed; bank row cites the reconciled source | agent |
| A6 | **EU / extra-EU split of FDI income** | Recipient country detail | `bop_fdi6_inc` by partner (downloaded) | Recipient table shows EU vs non-EU for FDI income with its own provenance | agent |
| A7 | **2024 vintage** | Timeliness | Eurostat 2024 national accounts and BoP when FATS 2024 appears | Pipeline runs to 2024; vintage changes reported in a diff table | agent |
| A8 | **SPE-adjusted balance of payments** to replace the sector rule | Limitation 9 | Central Bank of Cyprus: BoP excluding SPEs by sector and item | S12M rule becomes a sensitivity variant | human (request), then agent |
| A9 | **Confidential FATS by industry × country** | Limitations 6, 7 | Eurostat/CYSTAT research access | Fitted cells replaced by observed ones | human (research access) |
| A10 | **Interest by counterpart country** | Limitation 8 | Central Bank of Cyprus: BoP by sector × partner | `WORLD_UNALLOCATED` interest split by country | human (request), then agent |

## Coverage: more countries, more of the chain

| # | Item | Data | Done when | Who |
|---|---|---|---|---|
| C1 | **All EU27 countries** in the comparison | Eurostat (same datasets, `--raw-dir data/raw/eurostat_eu`) | Comparison and map for every country whose inputs are published; skipped country-years listed | agent (needs disk space, see H1) |
| C2 | **Malta** | `nama_10_a64` B–E aggregate | Mining and energy handled as one merged section; Malta in the comparison | agent |
| C3 | **Frame B (input–output) for other countries** | Eurostat `naio_10_cp1700` symmetric tables | Per-euro decomposition for each comparison country | agent |
| C4 | **Value-added origin of imports** (not only the direct supplier) | FIGARO full inter-country tables | Imported value added traced to the country that produced it | agent (needs disk space, see H1) |
| C5 | **θ for other countries** | GLEIF parent relationships; OECD AMNE database | θ calibrated per country, not borrowed from Cyprus | agent |
| C6 | **Luxembourg interest lines** | STATEC / BCL sector BoP (to be checked) | Luxembourg's suppressed lines filled from an official national source, or confirmed unavailable | agent (check), human if a request is needed |

## Reliability and reuse

| # | Item | Done when | Who |
|---|---|---|---|
| R1 | Numbers in README and docs generated or checked against `data/processed` | A check fails when a hand-written figure drifts from the data | agent |
| R2 | Tests for the sensitivity grid and pipeline wiring | A variant leaking into the θ grid, or a missing variant, fails a test | agent |
| R3 | CI runs the validator on a small committed fixture | Pull requests run identity and source checks, not only unit tests | agent |
| R4 | Dashboard: map, one page per comparison country, CSV downloads | Every table on the site downloadable with provenance columns | agent |
| R5 | Citable release with a DOI | Zenodo DOI in `CITATION.cff` and README | human (link Zenodo to GitHub), then agent |
| R6 | Outside review by a national-accounts statistician | Written comments addressed in a revision note | human |

## Human to-do

| # | What | Why | Unblocks |
|---|---|---|---|
| H1 | **Free disk space** (the disk is 96% full, about 9 GB left) | EU27 downloads and FIGARO tables need several GB; a full disk corrupts downloads | C1, C4 |
| H2 | **Email the Central Bank of Cyprus statistics department** asking for (a) the BoP excluding SPEs by sector and item, (b) investment income by sector and partner country, 2010–2023 | Only they hold it; a request from a named researcher is more likely to succeed | A8, A10 |
| H3 | **Apply for Eurostat/CYSTAT research access** to confidential FATS (through Milestone Institute) | Removes the fitted industry × country cells | A9 |
| H4 | **Link Zenodo to the GitHub account** (one click at zenodo.org, GitHub login) | Issues a DOI on each release | R5 |
| H5 | **Decide the SEC EDGAR contact** if US parent filings are used: EDGAR requires a User-Agent with a contact email | Your email is kept out of the repository; you choose what goes in the header | A4 (US parents) |
| H6 | **Optional: Orbis / BvD access** through a library, if Milestone has it | Best source for ownership shares; paid | A4, C5 |
| H7 | **Name one or two statisticians** to review | Outside check on the method | R6 |

## Order of work

1. A1, A2, A6 (data already downloaded; each changes or bounds a headline number).
2. R1, R2 (stop regressions before the numbers move again).
3. A4, A5, A3 (need new public data; moderate effort).
4. C2, C1, C3 (coverage; C1 after H1).
5. A7 when the 2024 data are complete; A8–A10 when H2/H3 come back.

Every item goes through the same loop as the release: build, validator, adversarial review rounds until one finds nothing significant, then commit.
