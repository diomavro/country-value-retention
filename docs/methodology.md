# Methodology

This is the technical specification. For the plain-language explanation of each
concept, read [`concepts.md`](concepts.md) first. Every rule below points to the
code that enforces it.

## 1. The object: V[i, j, k, t]

`V[i, j, k, t]` is the value added generated in country *i*, industry *k*, year
*t* that **accrues to residents of j after Cypriot taxes on production and on
income**. "Accrues" does not mean "is paid": profits reinvested in the Cypriot
firm still accrue to its foreign owner, as reinvested earnings do in the
balance of payments.

*i* is Cyprus in this release. *k* runs over CYSTAT's 65 product/industry
groups (A*64, with real estate split into imputed rent `L68A` and market real
estate `L68B`), plus the pseudo-industry `_PRODUCT_TAXES`. Every cell also
carries a **mechanism**, which records *why* the value accrues to *j*.

Two **identities** hold by construction. The retained cell is the residual, so
these are bookkeeping, not evidence:

```
Σ_j V[CY, j, k, t] = GVA_k,t          Σ_j Σ_k V[CY, j, k, t] = GDP_t
```

The evidence lies in the source checks of §5 and in the bridge of §6.

## 2. Frame A: who receives the value added generated in Cyprus

For each industry, `GVA_k = D1_k + D29X39_k + B2A3G_k` (compensation; other net
taxes on production; gross operating surplus and mixed income). Each outflow
mechanism may draw **only** on its own component, and never more than
`max(component, 0)`. `value_tensor` raises if it tries.

| Mechanism | Drawn from | Source and rule | Recipient | Industry allocation |
|---|---|---|---|---|
| `compensation_nonresident` | D1_k | CYSTAT S2 D1 received × (1 − employer social contributions share, `nasa_10_nf_tr` S1 D12/D1) | `bop_rem6` partner shares; unpublished → `CONFIDENTIAL_PARTNERS` | ∝ D1_k |
| `fdi_income` (FATS) | B2A3G_k | foreign-controlled GOS (`fats_activ` 2021–23; `fats_g1a_08` VA − personnel costs, 2010–20) at the **finest published code**; × (1 − CFC − interest per euro of corporate GOS) × (1 − τ) × θ | section × UCI economy: published cells fixed, the rest fitted to both margins (IPF) | finest code; a section's unpublished remainder ∝ B2A3G_k |
| `fdi_income` (banks, 2010–20 and consistent scope) | B2A3G_K64 | BoP FDI equity income (D4S, after interest and tax) paid by deposit-taking corporations (`bop_c6_a`, S122) | `CONFIDENTIAL_PARTNERS` | K64 |
| `fdi_debt_interest` | B2A3G_k | BoP intra-group interest paid by S1V (`D41__D__FLA`), **capped** at s × interest deducted from foreign-controlled firms' surplus, s = BoP FDI debt interest / S11 D41 paid | `WORLD_UNALLOCATED` | ∝ foreign-controlled FATS surplus |
| `other_investment_income`, `portfolio_income` | B2A3G_k | BoP interest (loans, deposits, debt securities), portfolio dividends and policyholder income paid by S1V; banks (S122) net of receipts | `WORLD_UNALLOCATED` | S1V: firms ∝ GOS, households' share (S14_S15 D41) to imputed rent L68A as mortgage interest; banks → K64 |
| `public_debt_interest` | product-tax pool | BoP interest paid by general government (S13) | `WORLD_UNALLOCATED` | `_PRODUCT_TAXES` |
| `taxes_to_eu_institutions` | product taxes | CYSTAT S2 D2 received | `EU_INST` | `_PRODUCT_TAXES` |
| `retained_domestic` | residual | GVA_k − Σ outflows | CY | — |

The balance of payments publishes investment income by resident sector for the
**world only**. There is no EU27 / extra-EU split for these items, so those
flows are `WORLD_UNALLOCATED`.

### Foreign-owned profit

FATS operating surplus is measured **before** depreciation, interest and
corporate tax. It is converted to what accrues to foreign owners:

```
fdi_income_k,j = GOS^FATS_k · (1 − c_s − ρ_s) · (1 − τ_t) · θ · σ_{s(k), j}
```

- `GOS^FATS_k`: the finest published FATS code covering industry k (`allocate_fats`). A code that covers several industries, or a section's unpublished remainder, is split ∝ B2A3G. A section's published total is conserved, and any leftover is recorded, never dropped.
- `c_s`: consumption of fixed capital per euro of gross operating surplus of the **corporate** sector: S11 for non-financial industries, S12 for finance (`nasa_10_nf_tr`). Industry ratios are not used because industry B2A3G includes self-employed mixed income.
- `ρ_s`: S11 interest paid (D41, after FISIM, **gross**) per euro of S11 GOS, for non-financial industries only. Interest received is not netted: receipts from abroad are not value generated in Cyprus. The deduction removes interest owed to *all* lenders. The share owed to Cypriot lenders stays in Cyprus. The share owed to foreign third-party lenders is counted once, in the BoP S1V interest lines. The intra-group share s (BoP FDI debt interest / S11 D41 paid, on the same gross basis) goes to `fdi_debt_interest`. Variants: net of receipts, actual interest before FISIM (c + ρ ≥ 1 in 2010–2015, i.e. no profit; 11–29% of surplus left in 2016–2020; close to the central ratio from 2021), and ρ = 0. Ratios by year: `data/processed/interest_ratios.parquet`. For finance ρ = 0 (limitation).
- `τ_t`: statutory corporate income tax, 10% to 2012 and 12.5% from 2013. Effective rates are lower, so this deduction is an upper bound on the tax (and the no-tax case is shown).
- `θ`: the non-resident share of equity in foreign-controlled firms, calibrated in `ownership_data.theta_calibration` as the integrated non-resident share. It traces through Cypriot holdings and stops at the first non-resident owner on every path, over documented foreign-controlled firms, with each group counted once. The value is computed at run time and recorded in `headline_metrics.theta`; the grid 0.6–1.0 is reported.
- `σ_{s,j}`: UCI economy j's share of section s. It is fitted by iterative proportional fitting: published section × country cells are fixed, rows sum to section totals, and columns sum to the published business-economy country totals, with the unpublished remainder in `CONFIDENTIAL_PARTNERS`. A suppressed economy's total is never assigned to a named country. Within a published country total, suppressed section cells are fitted from published margins; those rows are flagged and carry low confidence (the fit uses only published margins, so it discloses nothing beyond them).

Sections or codes with negative foreign-controlled GOS are owners' losses, not
outflows, and are listed in `headline_metrics.negative_fats_sections`.

### Special purpose entities

Income paid by financial corporations other than MFIs (`S12M`) is excluded,
except the FATS profit of foreign-owned insurers and auxiliary financial firms
(K65/K66, from 2021). S12M holds Cyprus's SPEs and captive financial units. The
Central Bank of Cyprus's operational SPE criterion is at most three employees,
little physical presence or production, control by non-residents, and
transactions almost entirely with non-residents. The exclusion is a *sector*
rule. It removes non-SPE insurers, pension and investment funds too, and misses
SPEs classified elsewhere. Note that the gap between the official outflow and
this study's estimate is driven mainly by using FATS instead of BoP FDI income,
and only partly by the SPE rule (see the bridge).

### Capping

A capital-income mechanism may not exceed its industry's B2A3G. Allocated
outflows above it are scaled down, the scaling is written into the row's
`methodology`, the row's status becomes `estimated`, and the amount is listed in
`headline_metrics.capped_industries`.

## 3. Frame B: where a euro of spending on Cypriot output goes

The model uses CYSTAT's symmetric product-by-product tables at basic prices,
with the domestic block from 0640050E and the imported block from 0640055E:

```
A_d = Z_d diag(x)^-1,  A_m = Z_m diag(x)^-1,  L = (I − A_d)^-1
value-added content = (v/x) L,  import content = 1'A_m L,  tax content = (t/x) L;  they sum to 1
```

A euro of final demand is valued at basic prices, so taxes on the final sale
(such as VAT) are outside it. Domestic value added along the chain is routed
with Frame A's industry recipient shares. Imported inputs go to the *direct
supplier* economy in FIGARO (not the economy where their value was added). An
import is counted once.

## 4. Headline metrics (never summed)

| Metric | Definition | Denominator |
|---|---|---|
| Domestic Value Retention (DVR) | Σ_k V[CY, CY, k] / GDP; an **upper bound**, because unmeasured outflows count as retained | GDP |
| Foreign Value Leakage (FVL) | 1 − DVR | GDP |
| Foreign Input Exposure | imported / (domestic + imported) intermediate inputs; total version via L | intermediate inputs |
| Foreign Ownership Capture | θ × net operating surplus of foreign-controlled firms in sections B–N (FATS, after S11 depreciation), before interest and tax / net operating surplus of non-financial corporations (S11). Finance and P–R are excluded because FATS covers them only from 2021. Includes what those firms owe lenders | S11 NOS |
| Foreign creditor income share | non-FDI interest and portfolio income paid abroad by firms and banks (households' mortgage interest excluded) / S11 NOS; overlaps with the capture share | S11 NOS |
| Foreign Labour Income | compensation paid to non-residents, net of employer social contributions / D1 | compensation |
| Primary-income outflow / GDP | **official** S2 D1 + D2 + D4, including SPEs | GDP (comparator only) |

## 5. Checks (`src/cvr/reconcile.py`, `src/cvr/validate.py`)

**Checks against independent sources** (they fail if an outflow is dropped,
doubled or mis-scaled):
- SIOT GDP and D1 against the annual national accounts
- non-resident pay against S2 D1 × (1 − employer SSC share)
- EU taxes against S2 D2
- public-debt interest against BoP S13
- the FATS base of foreign-owned profit against the published FATS total (less owners' losses)
- banks counted exactly once
- the bridge lines add up

**Identities** (labelled `[identity]`): Σ V = GDP, industry rows = GVA, DVR + FVL = 1, Frame B exhaustion.

The official aggregates satisfy the GNI identity (GDP + primary income received
− paid = GNI to 0.01%). That checks the data used, not the model.

## 6. Bridge from the official outflow (`data/processed/bridge.parquet`)

For every year, the official primary income paid abroad is split by paying
resident sector (BoP) and set against the model's outflow line by line:
- employees
- EU taxes
- the national-accounts/BoP gap
- S12M
- the central bank
- banks
- government
- firms and households, split into FDI equity income, intra-group interest, and other interest

The official lines add up to the official total in every year (validated). The
largest difference is S12M (pass-through). The second is firms' FDI equity
income paid (BoP) against FATS-based profit, which is income passed on by
non-SPE holding and trading companies plus FATS/BPM6 concept differences.

## 7. Breaks and versions

- **2021:** FATS changes dataset (`fats_g1a_08` → `fats_activ`) and adds finance (K) and sections P, Q and R; section J roughly doubles at the switch. `headline_metrics_consistent_scope` uses sections B–N only in every year (banks via the BoP), which removes the scope change. The dataset switch remains.
- **2013:** the statutory corporate tax rate rises from 10% to 12.5%.
- **Input-output tables end in 2022:** Frame B stops there, and Frame A continues from national accounts.

`src/cvr/validate.py` fails the build on any jump above 50% in the FDI
mechanism, in the central or the consistent-scope series, that has no entry in
`KNOWN_BREAKS`. Raw files are checked against their manifest checksums before
processing (`python -m cvr.ingest.verify`). The check catches files changed outside
the downloaders; a deliberate re-download rewrites the manifests, so a new data vintage
shows up as a change to the tracked `MANIFEST.csv` files, and `retrieval_date` in
processed tables is the latest download date among all inputs.

## 8. Ownership layer

The ownership graph uses NetworkX with edges parent → child and shares
(`src/cvr/ownership.py`, `src/cvr/model/ownership_data.py`).

- **Look-through (who ultimately owns the equity).** `W = S (I − S)^-1` assigns every euro of equity once, cross-holdings included. Undocumented shares go to `UNRESOLVED::<entity>`. An entity with any recorded owner, even one without a published share, is never treated as a terminal owner. Every non-terminal entity must appear in the results (the resolver raises otherwise).
- **Control (UCI, OECD/FATS concept).** Follow majority holders in the **control graph** (votes where disclosed, equity otherwise), never through dispersed free float, up to a unit nobody controls. A firm with undocumented owners, or one whose majority is held by persons or families of undocumented residence, resolves to `UNRESOLVED`, never to its own country.
- **Income rights.** Voting disclosures count as economic stakes (one share, one vote) unless equity and voting stakes in the same firm exceed 100%, which reveals separated rights.
- **Residence.** A natural person's country is `UNRESOLVED` unless residence is documented; nationality is never used. A legal entity is resident where it is incorporated (BPM6): the holding company of Bank of Cyprus is incorporated in Ireland, so at company level Bank of Cyprus is Irish-controlled. FATS does not publish Ireland as an ultimate controlling economy in these years, so the aggregate accounting cannot show it.
- **Data corrections** are applied by `data/raw/companies/_build/corrections.py`, which documents each one.

The firm layer calibrates θ and illustrates chains. Headline results use the
official aggregates, because firm coverage is partial.
