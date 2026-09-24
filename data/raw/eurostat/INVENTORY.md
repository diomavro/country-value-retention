# Eurostat raw-data inventory (reporter: Cyprus)

Downloaded 2026-09-24 by `python -m cvr.ingest.eurostat --figaro-year 2024`
(`src/cvr/ingest/eurostat.py`). Every file is listed with its URL, filters, SHA-256,
row count and Eurostat last-update date in `MANIFEST.csv`. Total on disk: about 32 MB.

## Flags and confidentiality

Every Parquet file keeps Eurostat's two status columns:

- `OBS_FLAG`: `p` provisional, `e` estimated, `b` break in series, `d` definition differs,
  `i` see metadata, `u` low reliability.
- `CONF_STATUS`: `C` means confidential. **`OBS_VALUE` is NaN for these cells. Do not treat them as zero.**
  `N` means not for publication (it appears only in the EU27 sector accounts).

For Cyprus, NaN values occur only where `CONF_STATUS = C`. The one exception is
`fats_g1b_08` (34% NaN against 22% `C`), where some cells are simply missing.

## Availability rules found by probing the API

- The SDMX 2.1 `data/` endpoint ignores dimension filters in the query string.
  The downloader therefore builds the positional key from the DSD.
- If any requested code is absent from a dataset, Eurostat rejects the whole query with HTTP 400.
  The downloader first checks each code against the dataset's `contentconstraint`, drops the
  absent ones and logs `WARN`.
- If the estimated extraction exceeds 5M cells, Eurostat returns HTTP 413.
  The downloader then splits the period range and retries.
- Large extractions are queued asynchronously. The downloader polls
  `https://ec.europa.eu/eurostat/api/dissemination/1.0/async/status/<id>` and then
  fetches the result from `.../1.0/async/data/<id>`.

## 1. National accounts

| Code | Title | CY coverage | Gaps / notes |
|---|---|---|---|
| `nama_10_gdp` | GDP and main components | 2010–2025, `CP_MEUR` + `CLV20_MEUR`, 39 items (B1GQ, B1G, D1, D11, D12, D2, D3, B2A3G, P6, P7 …). The EU27_2020 aggregate is also downloaded. | **No B5G/GNI in this dataset.** GNI (`B5GQ`) comes from `nasa_10_nf_tr` S1. 2024–25 are flagged `p`. |
| `nama_10_pp` | GNI per capita (PPS) | 2021–2024, 4 obs | The code exists but covers only 2021–2024. Use `nasa_10_nf_tr` B5GQ for levels. |
| `nasa_10_nf_tr` | Non-financial transactions (sector accounts) | 2010–2024; sectors S1, S11, S12, S13, S14_S15, S2; PAID/RECV; about 80 items, including D1, D4, D41, D42, D421, D422, D43, D44, D441–D443, D45, B5GQ. The EU27_2020 aggregate is also downloaded (2010–2025). | S2 is the rest of the world, recorded from the RoW's side: **S2 PAID = received by Cyprus.** Examples: 2024 S2 D4 PAID 33,560 / RECV 37,116 MEUR; 2024 B1GQ 34,770 vs B5GQ 31,017. S2 has no D45 rows. Flags: `p` 784 obs, `e` 60 obs. |
| `nama_10_a64` | GVA and income by A64 industry | 2010–2024; CP_MEUR + CLV20_MEUR; B1G, D1, D11, P1, P2, P51C, B2A3N, D29X39 | **CY publishes no D12 and no B2A3G at A64** (B2A3N only). No confidential cells. |
| `nama_10_a64_e` | Employment by A64 | 2010–2024; THS_PER and THS_HW; EMP_DC, SAL_DC, SELF_DC | Complete. |

## 2. National SUT / SIOT (CY, MIO_EUR)

The requested codes `naio_10_cp1500`/`cp1600` do not exist. The current codes are `cp15` and `cp16`.
Also, `cp1620` is the **trade and transport margins** table, not the use of imports.
The import split is carried by `stk_flow` = TOTAL / DOM / IMP inside `cp1610` and `cp1700`.

| Code | Title | CY years | Notes |
|---|---|---|---|
| `naio_10_cp15` | Supply table at basic prices + transformation to purchasers' prices | 2010–2022 | 5.4% `C` |
| `naio_10_cp16` | Use table at purchasers' prices | 2010–2022 | 5.0% `C` |
| `naio_10_cp1610` | Use table at basic prices (TOTAL/DOM/IMP) | 2010–2022 | 5.0% `C`. This is the domestic-vs-imported use split. |
| `naio_10_cp1620` | Trade and transport margins | 2010–2022 | — |
| `naio_10_cp1630` | Taxes less subsidies on products | 2010–2022 | — |
| `naio_10_cp1700` | SIOT product×product (TOTAL/DOM/IMP) | 2010–2022 | No `C`. Has B1G, B2A3G and D1 rows plus P6/P7 by EU/non-EU split. |
| `naio_10_cp1750` | SIOT industry×industry | **not published for CY** | The only reporters are BE, CZ, DK, EE, IT, HU, MT, NL, RO, FI (+ NO, AL, RS, TR, EU27, EA20). |

No CY tables exist before 2010, and none after 2022 (2023–2024 are not yet transmitted).

## 3. FIGARO (EU inter-country SUIOT, 2026 edition, 2010–2024, 50 economies incl. rest of world, 64 industries)

**API slices downloaded** (industry×industry, `naio_10_fcp_ii1..4`: 2010–13, 2014–17, 2018–21, 2022–24):

- `*__c_dest-CY`: every column of the Cypriot economy (64 industries + 5 final-demand categories), by origin country × origin industry.
  This includes the value-added and tax rows (`c_orig = DOM`; `ind_ava` = D1, B2A3G, D21X31, D29X39, OP_RES, OP_NRES).
  → **(a) Cyprus's imported intermediate inputs by origin country and industry.**
- `*__c_orig-CY`: every row of Cypriot output, by destination country × using industry / final demand.

**Ready-made trade-in-value-added indicators exist.** You do not need to invert the ICIO for the headline measures.
All cover CY for 2010–2024 with no confidential cells:

| Code | Content |
|---|---|
| `naio_10_fgfd` | Foreign VA in CY domestic final use by origin country & industry (THS_EUR, PC_FUSE) |
| `naio_10_fgdf` | CY domestic VA in foreign final use by destination & industry (THS_EUR, PC_GDP, PC_GVA) |
| `naio_10_fgdm` | CY domestic VA in exports, by importing country (EU-country perspective) |
| `naio_10_fgfoem` | Foreign VA in CY exports by country of origin |
| `naio_10_fgti` / `naio_10_fgte` | Imports / exports by industry |
| `naio_10_fggvcm` | GVC participation (45 obs) |

The same folder also holds the not-yet-downloaded `naio_10_fgfeim`, `fgfoim`, `fgtex`
(trading-partner exposure), `fgdfi` and the employment variants (`fgdem`, `fgdfe`, `fgdfef`).

**Full ICIO (needed for our own Leontief inverse):**

- The API route is impractical: each `naio_10_fcp_ii*` block holds about 33–44M cells, against the 5M cap.
- The files are on CIRCABC, in the public group "Integrated Global Accounts Expert Group" › Library › FIGARO database › 2026 edition.
  Folders can be listed with the guest REST API (`https://circabc.europa.eu/service/circabc/spaces/<folder-id>/children?guest=true`),
  and files download from `https://circabc.europa.eu/rest/download/<node-id>`.
  The folder id for the IxI CSV matrix is `e6896a70-5dbf-479c-8852-94b5dd1e3952`.
  - IxI CSV matrix, `matrix_eu-ic-io_ind-by-ind_26ed_<year>.csv`: 46–49 MB per year.
  - IxI CSV flat, `flatfile_eu-ic-io_ind-by-ind_26ed_<year>.zip`: 63–65 MB zipped.
  - PxP flat zip: 65–67 MB.
- **Downloaded:** 2024 IxI matrix → `figaro/matrix_eu-ic-io_ind-by-ind_26ed_2024.parquet` (23 MB).
  It has 3,206 rows (50 economies × 64 industries + 6 value-added/tax rows `W2_*`) × 3,450 columns (50 × (64 + 5 final demand)).
  Other years: `python -m cvr.ingest.eurostat --only none --figaro-year <Y>`.
- **Not downloaded, possibly useful:** the 2025-edition "National Accounting Matrices" (`FIGARO_NAM_<year>.csv`, about 150 MB each, 2010–2023, same CIRCABC folder).
  Its content (possibly inter-country distribution of income) has not been inspected.

## 4. BoP primary income by partner

| Code | CY coverage | Notes |
|---|---|---|
| `bop_c6_a` (sector S1×S1) | 2010–2025; 50 partners; CRE/DEB/BAL; CA, IN1, IN2, D1, D4P__F, direct (D4P__D__F, D4S, D42S dividends, D43S reinvested earnings, D4Q/D41 interest), portfolio (D4P__P__F, D42__P__F51, D443, D41__P__F3), other investment (D4P__O__F, D41__O__FLA, D44P), reserves, D4O, D2, D3, D45 | 19.1% `C`. Partner list: 50 codes, including OFFSHO (offshore centres), RU, CH, US, LU, NL. 2023 examples: D4P__D__F debit 30,907 MEUR (US 5,435, RU 5,155, CH 4,866, LU 3,711, OFFSHO 3,663); reinvested earnings debit 12,946. |
| `bop_c6_a` (sector split) | 2010–2025; partners WRL_REST / EU27 / EXT_EU27 only; sector10 = S1, S121, S122, S123, S12M, S12T, S13, S1P, S1V, S1W | 7.5% `C` |
| `bop_eu6_q` | EU27_2020 aggregate, annual, 2010–2025, 27 partners | `bop_c6_a` has no EU27 geo. This is the extra-EU BoP. |
| `bop_rem6` | 2010–2024; 113 partners; D1 (compensation of employees), D5Z, D61Z, D752, D752W, R1 … | 10.9% `C`. Compensation of employees by partner. |
| `bop_fdi6_inc` | 2013–2024; 294 partners; CRE/DEB/II/IO; 22 FDI income items (dividends, reinvested earnings, debt income, split by direct/reverse/fellow) | 26.4% `C` (44% in the NACE × aggregate-partner file) |
| `bop_fdi6_geo` | 2013–2024; stocks/flows/income, DI & DO totals, 294 partners | 23.8% `C` |

**SPE availability:**

- `bop_fdi6_inc` and `bop_fdi6_pos` have an `entity` dimension (`TOTAL`, `SPE`), so non-SPE = TOTAL − SPE.
  Both have CY SPE data for 2013–2024. SPEs dominate: SPE inward immediate positions (stk_flow LIAB, from the `bop_fdi6_pos` pivot) were 433.8 bn of 518.3 bn in 2023.
  Subtraction is impossible wherever either term is `C`. For example, TOTAL LIAB vs WRL_REST is `C` for 2019–2022.
- `bop_c6_a` / `bop_rem6` have **no SPE breakdown** (they have sector only).
- The Central Bank of Cyprus publishes an SPE-adjusted current account, IIP and external debt (SPEs treated as non-residents).
  This has not been downloaded and needs a separate CBC ingest.

## 5. FDI positions: immediate vs ultimate

`bop_fdi6_pos` covers 2013–2024 and 301 partners. The `counterp` dimension is IMM (immediate) or ULT (ultimate investing country).
ULT exists **only for stk_flow = NI (net inward), from 2017**, for DI__D__F, DI__D__F5 and DI__D__FL, with TOTAL and SPE.
2023 net inward from the rest of the world: 394.0 bn by ULT vs 400.9 bn by IMM.
By ULT, the US gets 81.7 bn, RU 89.1 bn and OFFSHO 48.5 bn. By IMM, OFFSHO is 111.6 bn and LU 91.5 bn.
Confidentiality is 37.9% `C` overall and 58.6% among ULT cells.
`fdi_pos_nace` has the NACE breakdown for aggregate partners only.

## 6. Inward FATS (c_ctrl = country of the ultimate controlling institutional unit)

| Code | CY coverage | Notes |
|---|---|---|
| `fats_activ` | 2021–2023; 48 NACE aggregates; 49 c_ctrl; 19 indicators, incl. AV_MEUR (value added), EXPN_SAL_BEN_MEUR (personnel costs), NETTUR_MEUR, EMP_NR, GOS_MEUR | 22.8% `C` |
| `fats_ctrl` | 2021–2023; business-economy total (B-S_X_O_S94); 249 c_ctrl | 22.5% `C`. 2023: foreign-controlled VA 4,458 of 20,579 MEUR; personnel costs 1,698 of 10,341; employment 38.5k of 401k. |
| `fats_g1a_08` | 2008–2020; 130 NACE; 54 c_ctrl; old SBS variable codes (V12150 = VA, V13310 = personnel costs, V16110 = persons employed …) | 13.8% `C`. Flags `d`/`b`/`p`. The 2021+ series (`fats_activ`) uses different variable codes, so the two need linking. |
| `fats_g1b_08` | 2008–2020; total economy; 254 c_ctrl | 21.7% `C` + other NaN |

From 2021, FATS includes finance (K). In 2023, foreign-controlled K accounted for 1,416 of 3,007 MEUR of value added. Holding-company SPEs create little value added, so FATS value added is far smaller than the FDI income flows: 2023 foreign-controlled VA was 4.5 bn, against a 2023 BoP direct-investment income debit of 30.9 bn.

## 7. Cross-border workers / employment

- `lfst_r_lfe2ecomm` (1999–2025): for CY, only `c_work = INR` (working in the reporting country) is published.
  **Residents working abroad are not available.** Flag `b` 27 obs.
- `lfsa_egan` (2010–2025): resident employment by citizenship (NAT, FOR, EU27_2020_FOR, NEU27_2020_FOR, STLS, NRP, TOTAL).
  **Citizenship ≠ residence.** The LFS covers residents only, so cross-border in-commuters are absent.
- The best money-flow proxy for cross-border labour income is BoP D1 by partner (`bop_rem6`, `bop_c6_a`).
  It is small for CY: 2024 S2 D1 was 102 MEUR paid by the RoW (received by CY) vs 295 MEUR received by the RoW (paid by CY).
