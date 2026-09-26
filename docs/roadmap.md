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
| C1 | **All EU27 countries** in the comparison | Eurostat (same datasets, `--raw-dir data/raw/eurostat_eu`) | Comparison and map for every country whose inputs are published; skipped country-years listed | agent (Frame A inputs are about 1–2 MB per country; 7.7 MB for the six comparison countries) |
| C2 | **Malta** | `nama_10_a64` B–E aggregate | Mining and energy handled as one merged section; Malta in the comparison | agent |
| C3 | **Frame B (input–output) for other countries** | Eurostat `naio_10_cp1700` symmetric tables | Per-euro decomposition for each comparison country | agent |
| C4 | **Value-added origin of imports** (not only the direct supplier) | FIGARO full inter-country tables | Imported value added traced to the country that produced it | agent (needs disk space, see H1) |
| C5 | **θ for other countries** | GLEIF parent relationships; OECD AMNE database | θ calibrated per country, not borrowed from Cyprus | agent |
| C6 | **Luxembourg interest lines** | BCL publishes financial flows by sector (tables 07.05, 07.07) but no investment income by resident sector (checked 2026-09-26) | Suppressed lines obtained on request | human (H8) |

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
| H1 | **Free disk space** (the disk is 96% full, about 9 GB left) | FIGARO tables need several GB; a full disk corrupts downloads | C4 |
| H2 | **Email the Central Bank of Cyprus statistics department** asking for (a) the BoP excluding SPEs by sector and item, (b) investment income by sector and partner country, 2010–2023 | Only they hold it; a request from a named researcher is more likely to succeed | A8, A10 |
| H3 | **Apply for Eurostat/CYSTAT research access** to confidential FATS (through Milestone Institute) | Removes the fitted industry × country cells | A9 |
| H4 | **Link Zenodo to the GitHub account** (one click at zenodo.org, GitHub login) | Issues a DOI on each release | R5 |
| H5 | **Decide the SEC EDGAR contact** if US parent filings are used: EDGAR requires a User-Agent with a contact email | Your email is kept out of the repository; you choose what goes in the header | A4 (US parents) |
| H6 | **Optional: Orbis / BvD access** through a library, if Milestone has it | Best source for ownership shares; paid | A4, C5 |
| H7 | **Name one or two statisticians** to review | Outside check on the method | R6 |
| H8 | **Email the BCL statistics team (stat@bcl.lu)** for Luxembourg's investment income paid by resident sector, 2010–2023 | Not published; Eurostat marks it confidential | C6 |

## Done (2026-09-26)

Some items closed differently from their original target; the table rows above state the target.

- **A1, closed as a variant:** the effective rate on actual profits cannot be taken from the national accounts in hubs (firms' income tax also taxes income earned abroad). The central estimate keeps the statutory rate; the EC forward-looking effective rate is a sensitivity variant from 2017.
- **A2, A3, bounded rather than booked:** recorded real-estate FDI income, net of reverse investment, is about €12m a year or less in absolute value; minority stakes cannot be separated from pass-through by holding companies, and the balance-of-payments variant bounds both.
- **A5, not closed:** the ECB's consolidated banking data split bank profit into domestic and foreign-controlled groups; they are consistent with one explanation of the bank gap in 2023 but do not settle it. The gap remains.
- **A6, partly:** the paper reports EU / non-EU shares of the whole outflow; a recipient table by region for FDI income is still open.
- **R1, partly:** a test fails when one of the figures it lists in README or docs drifts from the generated data; figures not on its list are unchecked.
- **R2:** the sensitivity grid's variants, worst case and completeness are tested.

## Order of work

1. A6 recipient table by region; R1 coverage of remaining doc figures.
2. A4 (θ weighting), A5 (bank gap: banks' annual reports).
3. C2, C1, C3 (coverage; C4 after H1).
4. A7 when the 2024 data are complete; A8–A10 when H2/H3 come back.

Every item goes through the same loop as the release: build, validator, adversarial review rounds until one finds nothing significant, then commit.
