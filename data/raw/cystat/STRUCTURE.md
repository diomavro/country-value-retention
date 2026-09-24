# CYSTAT raw files — layout for parsers

Source: CYSTAT PxWeb database (`https://cystatdb.cystat.gov.cy`, folder *National Accounts*), pulled via the PxWeb API as xlsx on 2026-09-24 by `python -m cvr.ingest.cystat_fetch` (then `src/cvr/ingest/cystat_fetch.py`).
SUIOT tables were last updated 2026-03-26; annual NA tables 2026-04-20; sector accounts 2025-10-31.
Provenance and hashes: `MANIFEST.csv`. PxWeb variable metadata: `pxweb_meta/<table>.json`.

## 1. SUIOT files (`0640xxxE_CP.xlsx`, `0640xxxE_PYP.xlsx`)

Reference years **2010–2022** (13 annual tables, 2018–2021 revised). No SUIOT for 2023+ is published.
`_CP` = current prices. `_PYP` = previous-year prices, which is `...` for **all cells in 2010–2014**; only 2015–2022 have values.
Units: **EUR million**. Exception: use-table row `EMP_DC` = hours worked, **thousands**.
Classification: **64 CPA 2.1 products** (row codes `CPA_A01` … `CPA_U`) × **64 NACE Rev.2 industries** (A*64 minus a few merges: `C10-12`, `C13-15`, `C31-32`, `E37-39`, `J59-60`, `J62-63`, `M69-70`, `M74-75`, `N80-82`, `Q87-88`, `R90-92`; real estate split into `L68B` (excl. imputed rent) and `L68A` (imputed rent)).
Order note: `L68B` comes **before** `L68A` in both rows and columns.

### Common layout (every SUIOT file, both measures)
- One worksheet, named after the table id (e.g. `0640010E`).
- `A1`: table title. Row 2 is empty.
- **Row 3 = column header**, labels in `D3:<lastcol>3`, formatted as `"[CODE] Label"`. Parse the code with regex `^\[([^\]]+)\]`.
- **Data start at row 4.** Years are stacked vertically in blocks of **B** rows. Block for year `y` starts at row `r0(y) = 4 + (y-2010)*B` and ends at `r0(y)+B-1`.
  - Col A: the year string (e.g. `'2022'`), present **only on the first row of each block** (blank below). Col B: measure text (`Current Prices`/`Previous Year Prices`), also first row only.
  - Col C: row label `"[CODE] Label"`, on every row.
  - Cols D…: values. Numeric cells are int/float. String cells are symbols: `c` = confidential, `N.A.` = not applicable, `...` = not available. Treat all three as missing, but do not treat them as zero.
- Row order within a block is identical for every year. Product rows are always offsets 0–64 (`CPA_A01`…`CPA_U`), and the remaining rows are listed per table below.
- After the last block there is a footer: symbol legend, prose table description, `Latest update:` (e.g. `20260326 08:00`), `Units:` / `Million Euro`, contact details, and `Internal reference code:`. Stop at `r0(2022)+B-1`.
- Industry/product columns: **D:BO** are the 64 industry codes (supply/use) or 64 CPA products (SIOT: headers `CPA_A01`…). **BP** = `U`/`CPA_U` (the 64th), and **BQ = `TOTAL`** (sum of the 64).
  So the intermediate block is `D:BP` (64 columns: D is col 4, BP is col 68).

### Final-demand columns (all use tables 0640015/20/25/30/35/40 and SIOTs 0640045/50/55; last col `CG`)
| Col | Code | Meaning |
|---|---|---|
| BR | P3-S14 | HH final consumption (SIOT 0640045 header spells it `P3_S14` — normalise) |
| BS | P3-S15 | NPISH final consumption |
| BT | P3-S13 | Government final consumption |
| BU | P3 | Total final consumption |
| BV | P51G | GFCF |
| BW | P53 | Valuables |
| BX | P52 | Changes in inventories |
| BY | P5M | P52+P53 |
| BZ | P5 | Gross capital formation |
| CA | P6-B0 | Exports fob to EU |
| CB | P6-U2 | Exports to euro area (alternative split) |
| CC | P6-U3 | Exports to non-euro-area |
| CD | P6-D0 | Exports to non-EU |
| CE | P6 | Total exports (= B0+D0 = U2+U3) |
| CF | TFU | Total final uses |
| CG | TU | Total use (= TOTAL + TFU) |

### 0640010E — Supply table at basic prices + transformation to purchasers' prices (B = 72, 939 data rows ending at row 939, last col BZ)
Production matrix: rows are products and columns are industries, `D:BP`. Column `BQ TOTAL` = domestic output by product.
Extra columns: `BR P7-B0`, `BS P7-U2`, `BT P7-U3`, `BU P7-D0`, `BV P7` (total imports cif), `BW TS-BP` (total supply at basic prices), `BX OTTM` (trade and transport margins, which sum to 0 over products), `BY D21X31` (taxes less subsidies on products), `BZ TS-PP` (total supply at purchasers' prices).
Rows at offsets 65–71: `TOTAL`, `ADJ_P7` (cif/fob adjustment on imports), `OP_RES` (direct purchases abroad by residents), `TOTADJ`, `P11` market output, `P12` output for own final use, `P13` non-market output (P11–P13 split industry output).

### 0640015E — Use table at purchasers' prices (B = 82, data rows 4–1069)
Intermediate use at purchasers' prices is `D:BP` × product rows. Final demand is in `BR:CG`.
Rows at offsets 65–81: `TOTAL`, `ADJ_P6` (cif/fob on exports), `OP_RES`, `OP_NRES` (purchases by non-residents in territory), `P2_ADJ` (total intermediate consumption/final use, adjusted), then the **value-added block**: `D1` CoE, `D11` wages and salaries, `D29X39` other net taxes on production, `P51C` CFC, `B2A3N` net OS+MI, `B2A3G` gross OS+MI, `B3G` mixed income (`...` throughout), `B1G` GVA, `P1` output. Supplementary rows follow: `P51G` GFCF by industry, `LE` closing stocks, `EMP_DC` hours worked (thousands).

### 0640020E — Use table at basic prices (B = 81, rows 4–1056)
Same columns as 0640015. Rows at offsets 65–80: `TOTAL`, **`D21X31`** (taxes less subsidies on products, a row by use column), `P2` (= TOTAL + D21X31, purchasers' prices), `ADJ_P6`, `OP_RES`, `OP_NRES`, `P2_ADJ`, `D1`, `D11`, `D29X39`, `P51C`, `B2A3N`, `B2A3G`, `B3G`, `B1G`, `P1`.

### 0640025E — Use table for domestic output at basic prices (B = 82, rows 4–1069)
Same columns. Rows at offsets 65–81: `TOTAL`, **`IMP`** (use of imported products cif, a row by column), `D21X31`, `P2`, `ADJ_P6`, `OP_RES`, `OP_NRES`, `P2_ADJ`, `D1`, `D11`, `D29X39`, `P51C`, `B2A3N`, `B2A3G`, `B3G`, `B1G`, `P1`.

### 0640030E — Use table for imports at basic prices (B = 66, rows 4–861)
Same columns. Rows: 65 products + `TOTAL` (offset 65). There are no VA rows.

### 0640035E trade and transport margins / 0640040E taxes less subsidies on products (B = 66, rows 4–861)
These have the same shape as 0640030: products × (industries + final uses), plus a `TOTAL` row. They contain no confidential cells.

### 0640045E — SIOT product × product at basic prices (B = 83, rows 4–1082)
Columns `D:BP` = 64 CPA products (headers `CPA_A01`…`CPA_U`), `BQ TOTAL`, and final demand `BR:CG` as above.
Rows at offsets 65–82: `TOTAL`, `D21X31`, `P2`, `D1`, `D11`, `D29X39`, `P51C`, `B2A3N`, `B2A3G`, `B3G` (`...`), `B1G`, `P1`, then the **imports rows** `P7-B0`, `P7-U2`, `P7-U3`, `P7-D0`, `P7`, and `TS-BP` (total supply = P1 + P7, by product column).
The rows from `D21X31` down to `TS-BP` are `N.A.` in final-demand columns `BR:CG`, except that `D21X31` and `P2` are filled there.
**The SIOTs contain no `c` cells. They are the complete, unsuppressed tables** (see Confidentiality).

### 0640050E — SIOT for domestic production (B = 78, rows 4–1017)
Same columns. Rows at offsets 65–77: `TOTAL`, **`IMP`**, `D21X31`, `P2`, `D1`, `D11`, `D29X39`, `P51C`, `B2A3N`, `B2A3G`, `B3G`, `B1G`, `P1`.

### 0640055E — SIOT for imports (B = 66, rows 4–861)
Products × (products + final uses), plus a `TOTAL` row.

### Confidentiality (`c`) — supply/use tables only
Industry columns **C26 and C27** are suppressed (checked for 2010 and 2022) (including their VA rows), so in the SUTs the `TOTAL` row entries for C26/C27 are `c`.
Some product rows are also suppressed in the import/export and total columns: 2022 → `CPA_C33`, `CPA_G46`, `CPA_H53`; 2010 → `CPA_H53`, `CPA_O84` (and some C10-12/C19 cells). The set varies by year.
Column and grand totals (e.g. supply `TOTAL`/`P7` on the TOTAL row) are still published.
Implication: use the SIOTs (0640045/50/55) when you need a complete matrix. Use the SUTs for industry-level VA/CoE, accepting the gaps for C26/C27.

### Identity checks (verified on the CP files for 2010, 2015 and 2022; max abs error in brackets)
- Supply: `TS-BP = TOTAL + P7` per product (1e-13). `TS-PP = TS-BP + OTTM + D21X31` per product (all years, rows without `c`).
- Supply `TS-PP` (col BZ) = use-PP `TU` (col CG) per product (0.0).
- Use BP = use-domestic + use-imports, cell by cell over products × all columns (1e-13). The same holds for SIOT 45 = 50 + 55 (0.0).
- Use PP = use BP + margins (0640035) + product taxes (0640040), cell by cell (≤0.002, rounding).
- Industry column: `P2_ADJ + B1G = P1` in 0640015 (0.0). Supply TOTAL row = use `P1` row by industry (0.0).
- SIOT: `TU` column per product = `TS-BP` row per product (≤0.004). By product column, `P2 + B1G = P1` (0.0).
- Grand totals, 2022 CP: output P1 = 64,381.745; imports P7 = 28,931.951; TS-BP = 93,313.696; D21X31 = 3,344.834; TS-PP = 96,658.53; intermediate consumption at purchasers' prices = 38,081.181; **GVA B1G = 26,300.563**; **D1 = 12,777.45**; B2A3G = 12,948.638; D29X39 = 574.475; exports P6 = 28,506.078; P3 = 23,965.774; P5 = 6,105.494.
- 2010 CP: P1 = 34,768.702; P7 = 10,603.276; B1G = 17,160.453; D1 = 9,257.844.
- Cross-check with annual NA (0610020E/0610040E, April 2026 vintage): 2022 B1G _T = 26,300.6 and D1 _T = 12,777.4. **The SUT and NA vintages agree to rounding.**
- Rounding: the SIOT B1G total differs from the SUT B1G by about 0.02, so use tolerances of about 0.05 on totals.

## 2. Annual national accounts (PxWeb, 1995–2025; 2024–2025 provisional)

Each file is one sheet: `A1` title, the header in row 3 (and row 4 where there are two header levels), then data. The footer (units, update date) follows the data.

- **0610010E** GDP & GNI. Rows 4–16 hold labels in col A, and years are in cols **B:AF** (1995…2025, row 3). Rows: 4 GDP CP (€m), 5 %, 6 real (€m), 7 %, 8 PYP (€m), 9 %, **10 B5G GNI CP (€m)**, 11 %, 12 average population (000s), 13–16 per-capita GDP/GNI. Units: €m, €, %.
- **0610020E** GDP production approach. Row 3 = measure, row 4 = year. Measure column blocks: **B:AF CP €m**, AG:BK real €m, BL:CP PYP €m, CQ:DU CP % change, DV:EZ real % change (each 1995–2025).
  Rows 5–84: 5 B1GQ, 6 D21, 7 D31, 8 B1G `_T`, and 9–84 B1G by 76 NACE items. The labels are `"B1G Gross Value Added, <code>, <name>"` and mix sections (A, C, G, …) with A*64 detail (A01…U), so do not double-count sections.
- **0610040E** GDP income approach. Row 3 = measure (B:AF CP €m; AG:BK % of GDP), row 4 = year. Rows 5–13 are totals: B1GQ, B2A3G, net OS+MI, net OS, net MI, CFC, D2, D3, D2−D3. Rows **14–90 D1 CoE** (`_T` + 76 NACE items, same code list as 0610020), rows 91–167 D11, rows 168–244 D12. Recent years may show `...` in some cells.
- **0610030E** GDP expenditure approach. Rows are year × measure: col A = year (first row of each block), col B = measure (CP €m, real, PYP, % of GDP, % changes…). Cols C:V are aggregates (B1GQ, P3, P31…, P5, P6, P7…; see row 3).
- **0610060E** Employment. Col A = unit (`Persons` from row 4, `Hours (Thousand)` from row 232). Col B = concept (employment / employees / self-employed, domestic concept, in blocks of 76 rows starting at rows 4, 80, 156, 232, 308, 384). Col C = activity (76 items, named in capitals without codes). Years are in D:AH (1995–2025). The data end at row 459.

## 3. Institutional sector accounts — `0630030E.xlsx` (2010–2024)
Rows 4–108 = 15 years × 7 sectors (`S1`, `S11`, `S12`, `S13`, `S14`, `S15`, `S2` rest of world). Col A = year (first row of each 7-row block), col B = sector.
Cols C:BO hold 65 transactions and balancing items (header row 3). Useful columns: `W` D1REC, `AH` D4REC (property income received), `AN` D1PAY, `AU` D4PAY, and `BH` B5G (national income, gross).
Many cells are `N.A.` where a transaction does not apply to a sector.
Units: €m. Last update: 2025-10-31.
The primary-income flows with the rest of the world come from the S2 rows (D1/D4 REC and PAY).

## 4. Other file
`NATIONAL_ACCOUNTS-A95_25-EN-200426.xls` is the key-figures workbook (sheets: Main Variables, Production Approach, Expenditure Approach, Income Approach). It has the same vintage as the 0610xxx tables and is kept as the official release artifact. It is not mapped here; prefer the PxWeb tables.

## Not found on CYSTAT
- **FATS (foreign affiliates statistics):** there is no table in the CYSTAT PxWeb tree (walked the full tree, ~1,100 folder/table entries) and no mention on any of the 25 subtheme pages. It is presumably only reported to Eurostat (`fats_*`), which was not downloaded here.
- **SUIOT for years before 2010 or after 2022:** not published in PxWeb, and there are no SUIOT files in the key-figures or publications lists.
- **Institutional-sector financial accounts** (0630010E/0630020E) exist in PxWeb but were not downloaded because they are not needed for value retention.
