# Limitations and uncertainty report

Each limitation says what it biases, in which direction if known, and what data would remove it.

## A. What the estimates can get wrong

| # | Limitation | Effect on results | Data that would fix it |
|---|---|---|---|
| 1 | **Retention is an upper bound.** "Retained" is GDP minus measured outflows, so every unmeasured outflow counts as retained: rent earned by non-resident owners of Cypriot dwellings (FDI income under BPM6), FDI income from 10–50% stakes in domestically controlled firms. Confidential BoP cells are omitted and listed in `headline_metrics.confidential_items`, with an upper bound (sector total minus published components) in `confidential_upper_bound`. | DVR overstated, FVL understated; size unknown for dwellings | CBC real-estate FDI income; BoP by sector without suppression |
| 2 | **θ is calibrated, not measured, and unweighted** (a surplus-weighted θ would be close to 1 and lower retention by up to about 0.5 pp). Integrated non-resident share of documented firms more than half non-resident-owned (so θ > 0.5 by construction), each group counted once (`theta_calibration`). Most are wholly owned, so θ ≈ 1 is close to an assumption. | Retention moves by about 1.7 pp of GDP in 2023 over θ ∈ [0.6, 1.0] (`sensitivity.parquet`) | FATS/FDI micro-data on equity shares of foreign affiliates |
| 3 | **Corporate tax is statutory, not effective.** Deductions such as the IP box and notional interest lower the effective rate. | The deduction is an upper bound on tax; the no-tax case bounds leakage from above | Corporate tax paid by foreign-controlled firms |
| 4 | **Foreign-owned insurers and auxiliary financial firms are missing before 2021.** FATS covers finance only from 2021; before, only banks enter (BoP). | 2010–2020 leakage understated by about 0.3% of GDP (their 2021 value, an allocated share of FATS finance at the national-accounts level) | FDI income by NACE excluding holding companies, or FATS K before 2021 |
| 5 | **FATS vs national-accounts concepts; interest.** SBS operating surplus differs from B2A3G (financial intermediation services, capitalised software and R&D, statistical units). Depreciation and interest use economy-wide S11 ratios, not foreign-controlled firms' own; the interest basis is a choice (gross, after FISIM), shown with net, pre-FISIM and zero-interest variants. Interest is not deducted for finance. | Level of foreign-owned profit uncertain by a few tenths of a pp of GDP; in 2023 the consistent-scope and BoP-upper variants both give lower retention than the central estimate (in 2021–2022 the consistent-scope variant gives higher retention; see sensitivity) | SBS interest paid by foreign-controlled firms |
| 6 | **FATS confidentiality.** 14–23% of FATS cells are suppressed (13.8% in `fats_g1a_08`, 2008–2020; 22.8% in `fats_activ`, 2021–2023), and 27% of FDI-income cells in 2013–2023 (26% by industry, 43% by partner); suppressed UCI economies stay in `CONFIDENTIAL_PARTNERS` (never imputed into named countries, to avoid residual disclosure). | Country split only; totals unaffected | Confidential FATS under a research agreement |
| 7 | **Industry × country is fitted, not observed.** Published section × country cells are fixed and the rest fitted to margins (IPF); industries within a section share its country mix. | Industry × country cells are low confidence | FATS by NACE × UCI |
| 8 | **Interest and government flows have no country.** The BoP by resident sector is published for the world only (`WORLD_UNALLOCATED`). | Country split only | BoP by sector × partner (CBC internal) |
| 9 | **SPE exclusion is a sector rule.** S12M is excluded wholesale (except FATS insurers and auxiliaries from 2021); SPEs classified elsewhere stay in; non-SPE S12M units are removed. | Direction ambiguous; `include_ofc` sensitivity | CBC SPE-adjusted BoP by sector and item |
| 10 | **Pass-through by non-SPE firms.** Holding and trading companies with staff pass on foreign-earned income. The model avoids it by using FATS for profits and capping intra-group interest; the bridge shows the size of the excluded flow. | Excluded by design; `bop_upper` sensitivity shows the bound | Enterprise-level BoP with employment |
| 11 | **Bank interest is netted.** Banks' non-FDI interest paid abroad is counted net of receipts; before 2013 Cypriot banks funded domestic lending partly with non-resident deposits. | `banks_gross` sensitivity lowers early-year retention | Banks' interest by counterpart and use of funds |
| 12 | **Foreign bank profit: two official sources disagree.** BoP FDI equity income paid by banks (after interest and tax) exceeds the FATS-based estimate for foreign-owned banks by about 2.2% of GDP in 2023. Candidate causes: FATS may treat Bank of Cyprus (Irish-incorporated holding) as domestically controlled (Irish-controlled finance is confidential in FATS; all confidential EU controllers of finance together hold €40–92m a year, net, in 2021–2023); BoP includes 10–50% stakes; provisioning differences. The central estimate uses FATS; the consistent-scope series uses the BoP. | The sources agree in 2021–2022 and diverge in 2023; the gap is ~2.2 pp of GDP against the allocated banks' share and ~1.7 pp against all FATS finance. The central series splices BoP (to 2020) and FATS (from 2021) | CYSTAT/CBC reconciliation of FATS K and BoP bank income |
| 13 | **Profit shifting and intra-group services.** IP-intensive industries (publishing incl. software, IT) may book profit shifted into Cyprus; intra-group service imports may move profit out as costs. | "Value generated by production" is an accounting label for these industries | Country-by-country reports |
| 14 | **Frame B uses direct supplier origin and industry-average cost structures.** | Country split of imports and the worked example only | Full FIGARO ICIO inversion; firm accounts |
| 15 | **Company layer coverage.** About 40 operating firms; some ownership links have no published percentage; no residence data for natural persons; press-sourced splits of private companies removed (`_build/corrections.py`). | Firm layer calibrates θ and illustrates; never enters headline totals | Beneficial ownership register |

## B. What this release does not claim

- **No causal claims.** The accounting says where income accrues. It does not say whether foreign ownership raised or lowered Cypriot income, wages or investment. Leakage is not a cost: the counterfactual without foreign capital is unobserved.
- **No welfare ranking of countries.** A high retention share is not "better". It describes a structure.

## C. Uncertainty classification of headline numbers

| Number | Status | Confidence |
|---|---|---|
| GDP, GVA by industry, compensation, official outflows | observed | high |
| Input exposure (direct and total) | modelled | high |
| Foreign value leakage total | estimated | medium (θ, τ, SPE sector rule); a lower bound (limitation 1) |
| Foreign value leakage by recipient country | estimated | medium for published section × country cells; low where the cell is fitted or the country confidential |
| Industry × country cells | estimated | low |
| Platform example | illustrative | not a result |

## D. To extend coverage (next data to acquire, in priority order)

1. The CBC SPE-adjusted BoP by item and sector, which would replace the S12M rule.
2. FIGARO full ICIO files for 2010–2022, for value-added origin of imports (the ingest supports `--figaro-year`).
3. Confidential FATS (NACE × UCI) through a Eurostat/CYSTAT research agreement.
4. For other EU countries: Frame A already runs for Ireland, Luxembourg, the Netherlands, Greece and Portugal (methodology §9). What is missing there is θ (ownership filings; the Cyprus value is assumed), Luxembourg's BoP by resident sector (confidential), Malta's separate mining and energy accounts, and Frame B (national SIOTs `naio_10_cp1700`).
