# SOURCES — Cyprus company-ownership dataset

Access date for every document below: **2026-09-24**. Built by `_build/banking.py` (banking rows, hand-transcribed) and `_build/merge.py` (merges `_fragments/*` and runs integrity checks: every edge id exists in `entities.csv`, every entity has a source URL, equity shares per child sum to <=100%). Plain-text extracts of most documents are in `docs/` (PDFs deleted for disk space).

## Conventions and caveats (read before using)
- `parent_entity_id = UNRESOLVED` is a sentinel (not an entities row): the owner could not be documented.
- `DISPERSED_FREE_FLOAT_<id>` = computed residual (100 − documented holders), country `UNRESOLVED`. No company consulted publishes a shareholder-by-residence breakdown (checked explicitly for Bank of Cyprus: AFR 2025, FY2025 results presentation, IR shareholder pages — none).
- Fund managers (Senvest, Wellington, Eaton Vance, BlackRock, Vanguard…) are coded at the manager's country; the beneficial owners of the managed funds are unresolved.
- No natural person's country of residence was documented in any source; all persons are `UNRESOLVED` with nationality noted where known. Big-4 partner groups coded CY by inference (partners practise in Cyprus) — flagged in notes, medium confidence.
- Banks: `operating_profit_eur_m` holds **profit before tax** (no operating-profit line in bank accounts); `revenue_eur_m` = total operating income/revenue. Stated in each row's notes.
- Group vs Cyprus: Louis plc and Petrolina figures include Greek operations (notes give Cyprus split where printed); Eurobank Ltd figures are the Cyprus segment of Eurobank S.A.; BoC group is ~all Cyprus.
- `CY_FOOD_BASKET` (Delivery Hero subsidiary reporting in TRY) is almost certainly in the Turkish-Cypriot north — exclude from Republic of Cyprus totals.
- Naspers ↔ Prosus is a cross-holding cycle; chain-resolution code must handle cycles.
- Pending/changing: Uber takeover offer for Delivery Hero (open to 5 Nov 2026); Fairfax acquisition of 45% of ERB Asfalistiki; Alpha Bank / Universal Life deal (completion not checked).
- Hermes Airports financials are from its sustainability report (company-published, not audited accounts). EKO Cyprus FY2025 figures were read by eye from page images of a scanned filing (no OCR).

## Banking (Bank of Cyprus, Eurobank Ltd ex-Hellenic Bank, Eurobank Cyprus, Alpha Bank Cyprus, AstroBank)
| Document | URL | Used for |
|---|---|---|
| Bank of Cyprus Holdings plc, Annual Financial Report 2025 (31 Mar 2026) | https://www.bankofcyprus.com/globalassets/group/investor-relations/annual-reports/english/20260331-afr-boch-group-31.12.2025.pdf | Major holders at 31 Dec 2025 and 11 Mar 2026 (p.31); incorporation (Ireland, tax-resident Cyprus); subsidiaries (BOC PCL, EuroLife, GIC 100%); income statement, staff, FTE by country, dividends |
| BoC IR page "Major Holders of shares and financial instruments" | https://www.bankofcyprus.com/en-gb/group/investor-relations/shareholder-information/major-holders-of-shares-and-financial-instruments/ | Cross-check (Senvest 9.68% incl. instruments; shares outstanding 435,962,305) |
| BoC FY2025 results presentation (18 Feb 2026) | https://www.bankofcyprus.com/globalassets/group/investor-relations/presentations/gr/20260218-fy2025-financial-results-presentation_final.pdf | Checked for shareholder geography — none published |
| Lamesa Investments Ltd v Cynergy Bank Ltd [2019] EWHC 1877 (Comm), 12 Sep 2019 | https://www.brickcourt.co.uk/images/uploads/documents/CL-2018-000826_Lamesa_v_Cynergy_Final_Judgment-11.pdf | Lamesa (CY) → Lamesa Group Inc (BVI) → V. Vekselberg (Russian national; residence undocumented). As of 2019. |
| Eurobank S.A. Annual Financial Report FY2025 (Stockwatch mirror of exchange announcement; eurobank.gr copy returned HTTP 403) | https://www.stockwatch.com.cy/storage/symbol_announcements/69ae62e6d9336.pdf | Hellenic Bank 93.47%→97.994%→100%; merger with Eurobank Cyprus, renaming to Eurobank Limited; CNP Cyprus acquisition (16 Apr 2025); Fairfax 32.67%; Cyprus segment (revenue 994, PBT 579, assets 28,742); Cyprus headcount 2,905 |
| Retail Banker International, 28 Feb 2025 | https://www.retailbankerinternational.com/news/alpha-bank-cyprus-buy-astrobank/ | Alpha Bank Cyprus "fully owned subsidiary"; AstroBank deal €205m |
| Cyprus Mail, 3 Nov 2025 | https://cyprus-mail.com/2025/11/03/alpha-bank-completes-astrobank-deal-forming-cyprus-third-largest-lender | AstroBank transfer effective 31 Oct 2025; post-deal size |
| Cyprus Mail, 27 Feb 2026 | https://cyprus-mail.com/2026/02/27/alpha-bank-income-boosted-by-astrobank-acquisition-in-cyprus | Checked — group figures only, no Cyprus split |
| MarketScreener relaying Alpha Bank announcement on UniCredit holding | https://www.marketscreener.com/news/alpha-bank-says-unicredit-has-29-8-in-voting-rights-and-financial-instruments-which-potentially-giv-ce7e59d3db80f023 | UniCredit 29.8% voting + 2.27% instruments |

**Unresolvable (banking):** Alpha Bank S.A. Annual Report 2025 and Alpha Bank Cyprus financial statements (alpha.gr, alphabank.com.cy return HTTP 403 to curl, WebFetch and Playwright; Wayback has no copy) → no Alpha Bank Cyprus financials, other Alpha >5% holders unverified. UniCredit press release (Jan 2026) also 403. Osome Investments (3.40% of BoC): incorporation and owner not found. Fairfax and UniCredit shareholder bases not researched. No residence breakdown of any bank's free float.


---

## Insurance and telecoms fragment: sources

All documents were accessed on 2026-09-24. Text extracts are saved in `data/raw/companies/docs/`. The PDFs themselves were deleted after extraction.

## Market-size ranking (which insurers are the largest)

- **Insurance Association of Cyprus, Annual Statistics 2025** (`Annual_Statistics_2025_Final.xlsx`), https://www.iac.org.cy/en/statistics/iac-statistical-results. Extract: `docs/iac_annual_statistics_2025.txt`.
  - Used for gross premiums by company in 2025.
  - Ranking of groups by combined life (incl. A&H) and non-life gross premiums:
    1. Eurobank group: ERB Cyprialife €247.7m + ERB Asfalistiki €121.9m.
    2. Bank of Cyprus group: EuroLife €257.6m + GIC €73.7m.
    3. Universal Life: €130.1m.
    4. MetLife branch: €77.5m.
    5. Ancoria: €65.5m.
    6. Trust: €59.2m.
  - Atlantic had €27.0m and ranks about 9th in non-life. It is included only because it is CSE-listed and was named in the brief.
  - The life table in this file is in €000s. The non-life table is in €.
- Politis, "Banks Reshape Cyprus' Insurance Market as Dominant Players" (31.12.2025), https://en.politis.com.cy/economy/economy-business-finance/977483/banks-reshape-cyprus-insurance-market-as-dominant-players. Used as context only (9M-2025 shares).
- The CBN article on H1-2025 shares (https://www.cbn.com.cy/article/119956/...) could not be read (no article body). Not used.

## Insurance ownership and financials

- **Eurobank S.A. Annual Financial Report 2025**, https://www.stockwatch.com.cy/storage/symbol_announcements/69ae62e6d9336.pdf. Extract: `docs/eurobank_holdings_afr_2025_stockwatch.txt`, downloaded by the banking agent.
  - Used for the CNP Cyprus acquisition on 16 Apr 2025 (EUR182m) and the rename to ERB Cyprus Insurance Holdings.
  - Used for the Group-companies table (ERB Cyprialife and ERB Asfalistiki at 100%, footnote (2)).
  - Used for the merger of Hellenic Life and Pancyprian into the ERB companies (Oct 2025).
  - Used for the pending sale of 45% of ERB Asfalistiki to Fairfax.
  - The banking agent sent a course correction that pointed to this source. I checked it against the text before using it.
- **Bank of Cyprus Holdings plc AFR 2025**, https://www.bankofcyprus.com/globalassets/group/investor-relations/annual-reports/english/20260331-afr-boch-group-31.12.2025.pdf. Extract: `docs/boch_afr_2025.txt`, downloaded by the banking agent.
  - Note 49: EuroLife Ltd and General Insurance of Cyprus Ltd are held 100% (directly or indirectly).
  - Note 49 also records the Ethniki Insurance acquisition and its merger in Dec 2025.
- **Universal Life, Annual Report 2025**, https://www.universallife.com.cy/library/download/MTE2Mg==. Extract: `docs/universal_life_annual_report_2025.txt`. Used for FY2025 group insurance revenue, profit before tax, total assets, and the chairman's statement on the Alpha Bank deal.
- **Universal Life, Financial Report 2024** (English translation of the audited consolidated FS), https://www.universallife.com.cy/library/download/NjY3. Extract: `docs/universal_life_financial_report_2024.txt`.
  - Used for the major shareholders at 31 Dec 2024 and 7 Apr 2025.
  - Used for note 34 (Photos Photiades Group Ltd, registered in Cyprus, is the controlling parent) and the 2024 employee count.
- Cyprus Mail, "Alpha Bank moves to create top-tier insurance group in Cyprus" (19.12.2025), https://cyprus-mail.com/2025/12/19/alpha-bank-moves-to-create-top-tier-insurance-group-in-cyprus, together with other search-result summaries (CBN, Stockwatch). Used as context for the pending Altius and Universal merger.
- **Atlantic Insurance, Extract from the Consolidated Financial Statements 2025**, https://www.atlantic.com.cy/assets/mainmenu/1025/docs/annual_report_2026.pdf. Extract: `docs/atlantic_annual_report_2025.txt`. Used for all FY2025 financial fields.
- **Atlantic Insurance IR, Main Shareholders** (ref. date 31/12/25), https://www.atlantic.com.cy/en/investor-relations/shareholders. Used for the shareholder edges.
- Cyprus Mail, "Atlantic Insurance reports €20.18 million profit for 2025" (07.04.2026), https://cyprus-mail.com/2026/04/07/atlantic-insurance-reports-e20-18-million-profit-for-2025. Used to cross-check only.
- **MetLife Europe d.a.c. SFCR 2025**, https://www.metlife.eu/content/dam/metlifecom/eu/solvency-financial-condition-reports/2025/MetLife_Europe_dac_2025_SFCR.pdf. Extract: `docs/metlife_europe_dac_sfcr_2025.txt`. Used for the Cyprus branch, the 100% holding by MetLife EU Holding, and the Cyprus A&H premiums.
- **MetLife EU Holding Company Ltd SFCR 2025**, https://www.metlife.eu/content/dam/metlifecom/eu/solvency-financial-condition-reports/2025/2025_MetLife_EU_Holding_Company_Solvency_and_Financial_Condition_Report.pdf. Extract: `docs/metlife_eu_holding_sfcr_2025.txt`. Used for "wholly owned by MGHC II (Switzerland)" and the ultimate parent MetLife, Inc.
- **MetLife, Inc. DEF 14A** (filed 2026-04-29), https://www.sec.gov/Archives/edgar/data/1099219/000109921926000026/met-20260429.htm. Extract: `docs/metlife_def14a_2026_5pct_holders.txt`. Used for the holders above 5% at 31 Mar 2026.
- MetLife Cyprus FAQ, https://www.metlife.com.cy/en/faqs/. Confirms only the Cyprus address of MetLife Europe d.a.c. Not used for any value.

## Telecoms

- **Cyta Annual Report 2025** (Greek; includes audited FS for FY2025), https://www.cyta.com.cy/mp/informational/docs/annualreports/AnnualReport_2025_el.pdf. Extract: `docs/cyta_annual_report_2025_el.txt`.
  - Used for all FY2025 financials.
  - Used for the legal status: public-law body under Law 67/1954, Cap. 302.
  - Used for dividends paid to the Republic of Cyprus.
- **Cyta Financial Report 2024 extract** (sworn English translation, scanned), https://www.cyta.com.cy/mp/informational/docs/annualreports/Financial_Report_2024_extract_en.pdf.
  - Read visually because the PDF has no text layer. No extract was saved.
  - Used for the FY2024 figures quoted in the notes.
- **Cyta Annual & Sustainability Report 2024**, https://www.cyta.com.cy/mp/informational/docs/annualreports/AnnualReport_2024_en.pdf. Extract: `docs/cyta_annual_report_2024.txt`. Used for FY2024 EBITDA (€143m) and 1,932 direct employees (notes only).
- **Cablenet Communication Systems plc, FY2025 audited FS**, https://cablenet.com.cy/wp-content/uploads/2025-Full-Year-final.pdf. Extract: `docs/cablenet_2025-Full-Year-final.txt`. Used for all financials, the shareholding split (GO 70.61% and N. Shiacolas 29.39%), and "ultimate controlling party Tunisie Telecom".
- Cablenet FAS 2025 (09.05.2025), https://cablenet.com.cy/wp-content/uploads/Cablenet-Communication-Systems-plc-FAS-2025.pdf. Used to cross-check the shareholding chart. Its extract was deleted as superseded.
- Cablenet Company Announcement 045, Class 1 Transaction (19.08.2026), https://cablenet.com.cy/wp-content/uploads/Company-Announcement-045-Class1Transaction-19Aug26.pdf. Extract: `docs/cablenet_Company-Announcement-045-Class1Transaction-19Aug26.txt`. Used for context: sale of the IRU to a BMIT affiliate.
- Cablenet FAS 2026, https://cablenet.com.cy/wp-content/uploads/Cablenet-Communication-Systems-FAS-2026.pdf. Downloaded as `docs/cablenet_Cablenet-Communication-Systems-FAS-2026.txt`. Not needed beyond the audited FS.
- **GO p.l.c. Annual Financial Report 2025 (ESEF xhtml)**, https://prodcms.go.com.mt/wp-content/uploads/2026/03/Financial-Statements-2025-12-31-1-en-InlineViewer.xhtml. Extract: `docs/go_plc_annual_report_2025.txt`.
  - Used for TT ML Limited at 65.42% (the only holder above 5%) and TT ML as fully owned by Tunisie Telecom.
  - Used for Tunisie Telecom's owners: 65% Tunisian Government and 35% EIT, a subsidiary of Dubai Holding.
  - Used for Cablenet at 70.6%.
- GO company-structure page, https://www.go.com.mt/investor-centre/company-structure/. Cross-check: it says "Tunisie Telecom holds 66%", which is rounded.
- Rizzo, Farrugia & Co., "GO plc – Publication of Offer Document" (2016), https://rizzofarrugia.com/malta-market-news/2016/publication-of-offer-document-go1610/. The page returned 404. Only the search-result summary was seen ("wholly owned subsidiary in Malta, TT ML Limited"), and it is used only for TT ML's country.
- **NJJ Continental Holding S.A. Annual Report 2025**, https://www.salt.ch/sites/default/files/2026-08/Annual_Report_NJJ_Continental_Holding_S.A._December_31_2025.pdf. Extract: `docs/njj_continental_holding_ar_2025.txt`.
  - Used for the organisation structure: 90% of GP Holding SAS (France), 100% of Compagnie Monégasque de Communication, 50.01% of Monaco Telecom, and 90% of Epic Cyprus indirectly with 10% held by NJJ affiliates.
  - Used for the Government of Monaco as holding "minority control".
  - Used for the Niel family as ultimate controlling party.
  - Used for the Luxembourg registration (B195766).
  - Used for Cyprus revenue in CHF.
- **Matterhorn Telecom S.A. PR, 17 Sep 2025**, https://www.salt.ch/sites/default/files/2025-09/20250917-Launch%20of%20Senior%20Secured%20Debt-EN.pdf. Extract: `docs/salt_20250917_launch.txt`. Used for the deal terms and "co-owned by NJJ and the Government of Monaco since 2014".
- **NJJ Continental FY2025 PR, 31 Mar 2026**, https://www.salt.ch/sites/default/files/2026-07/NJJ%20Continental_FY25_260331_Press%20Release_Holding_Level%20EN_accessible.pdf. Extract: `docs/njj_continental_fy25_pr.txt`. Used for completion on 2 Oct 2025 and footnote 1 ("co-owns ... alongside the Government of Monaco").
- NJJ Continental launch PR (06.07.2026) and Q2-2026 PR (27.08.2026). Extracts: `docs/njj_continental_20260706_launch.txt` and `docs/njj_continental_q2_2026.txt`. Used for context only.
- Monaco Telecom legal information page, https://monaco-telecom.mc/informations-legales/. Used for the RCI number.
- Wikidata Q935874 (Monaco Telecom) and Monaco Hebdo (30.05.2014), https://monaco-hebdo.com/economie/faire-de-monaco-telecom-le-numero/. These are Tier 4 and inconsistent (49.9% vs 45%), so neither is used for a percentage.
- Epic website, https://www.epic.com.cy/en/page/BJNrroGA/epic-ltd. Used for "Epic belongs to Monaco Telecom" and ">300 employees" (notes only).
- PrimeTel corporate announcements, https://primetel.com.cy/corporate-announcements. Includes the delisting memorandum (https://primetel.com.cy/uploads/originals/1/memorandum-for-egm-en-final.pdf) and the 2021/2022 AGM notes. Extracts: `docs/primetel_*.txt`. The only holder named is Lametus Holdings Ltd at 8.88% (c.2017).
- Wikipedia, PrimeTel, https://en.wikipedia.org/wiki/PrimeTel. Tier 4. Names shareholders without percentages.
- Wikipedia, Dubai Holding, https://en.wikipedia.org/wiki/Dubai_Holding. Tier 4. Owner is ambiguous.
- Dubai Holding "who we are" page, https://www.dubaiholding.com/en/who-we-are. No ownership statement.

## IDs used from other fragments (no duplicate rows written)

- `CY_EUROBANK_LTD`, `IE_BOC_HOLDINGS` and `CY_ALPHA_BANK_CYPRUS` are defined in the banking fragment.
- `STATE_CY` and `US_BLACKROCK` also appear in `energy_retail_entities.csv`, with the same meaning. Deduplicate them when merging.

## Unresolved items

1. **PrimeTel.** Ownership percentages and financials are not available: the company is delisted and has no public FS.
2. **Monaco Telecom.** The state stake of 49.99% is derived as the residual. The Government of Monaco co-ownership is documented, but the exact percentage and holding vehicle (possibly Société Nationale de Financement) are not.
3. **GP Holding SAS.** The holder of the remaining 10% is not disclosed.
4. **NJJ Continental Holding to the Niel family.** Percentages and the intermediates (OCH-AT Holding S.A. and NJJ Telecom Europe SAS) are not disclosed. The Niel family's residence is not documented.
5. **Epic Cyprus.** Statutory FS were not retrieved. Only Cyprus geographic revenue in CHF is available.
6. **Dubai Holding.** It is unclear whether the ultimate owner is the Government of Dubai or the Ruler personally. The EIT to Dubai Holding percentage is not stated.
7. **Tunisie Telecom's 65/35 split.** This comes only from GO's annual report; Tunisie Telecom's own filing was not checked.
8. **MetLife.** The MGHC II to MetLife, Inc. percentage and any intermediates are not disclosed.
9. **Universal Life.**
   - The shareholders of Photos Photiades Group are not disclosed.
   - The owners of Magnum Investments are not disclosed.
   - Whether Eurobank Ltd still held the 18.58% stake at end-2025 is not verified.
   - Completion of the Alpha Bank/Altius merger is not verified as of 2026-09-24.
10. **Residence of persons.** The residence of all natural persons (the Photiades, Pyrishis and Frangoullis families, Marathovouniotou and Shiacolas) is not documented.
11. **Upstream chain of Piraeus Bank S.A.** This minority holder of Atlantic was not researched.
12. **Insurer financials.** Financials for the bank-owned insurers (ERB Cyprialife, ERB Asfalistiki, EuroLife, GIC) and the MetLife branch were not retrieved. Only IAC gross premiums are given, in the notes, because GWP is not IFRS 17 revenue.

---

## Energy & retail (Cyprus) — sources log

Access date for all items: 2026-09-24. Tiers: 1 = filings/registries/gazette, 2 = company sites, 3 = press, 4 = Wikipedia. Text extracts of downloaded PDFs are in `data/raw/companies/docs/`; the PDFs were deleted.

## Energy — documents consulted (all accessed 2026-09-24)

| # | Document | URL | Used for |
|---|----------|-----|----------|
| E1 | Petrolina (Holdings) Public Ltd, Ετήσια Έκθεση 2025 (Annual Report 2025, Greek, 127 pp) | https://www.petrolina.com.cy/library/download/MjAzNQ== (text kept: docs/petrolina_ar2025.txt) | Consolidated P&L, balance sheet, cash flow, EBITDA (note 35.5), staff costs (note 10), geographic split (note 5), >5% holders and director holdings at 31.12.2025 / 24.04.2026, subsidiaries (note 37), ExxonMobil Cyprus acquisition (note 38) |
| E2 | Petrolina investors page | https://www.petrolina.com.cy/en/investors | Link to AR2025 |
| E3 | Petrolina announcement: Completion of the acquisition of ExxonMobil Cyprus Limited | https://www.petrolina.com.cy/en/news/completion-of-the-acquisition-of-exxonmobil-cyprus-limited | 100% of ExxonMobil Cyprus Ltd via Med Energywise, EUR 45.1m, renamed eWise Cyprus Ltd |
| E4 | CBN, "Petrolina acquires ExxonMobil Cyprus and takes over 68 Esso stations for €48.6m" (search result only) | https://www.cbn.com.cy/article/86795/petrolina-acquires-exxonmobil-cyprus-and-takes-over-68-esso-stations-for-48-6m | 68 Esso stations; initial price (not independently fetched) |
| E5 | HELLENiQ ENERGY Holdings S.A., 2025 Annual Financial Report (EN) | https://www.helleniqenergy.com/sites/default/files/2026-02/helleniq-energy_2025-annual-financial-report-en.pdf (text kept: docs/helleniq_afr2025.txt) | Shareholding at 31.12.2025 (Paneuropean 40.41, HCAP 31.18, free float 28.41); HRADF→HCAP merger; Paneuropean (Cyprus) Ltd ex-S.A.; Paneuropean–Greek State shareholder agreement 30.05.2003; consolidation table (EKO Cyprus Ltd U.K. 100%, R.A.M. Oil Cyprus 100%, etc.); EKO Cyprus goodwill |
| E6 | HELLENiQ ENERGY regulatory announcement 16.12.2023, Notification of important changes concerning voting rights (L.3556/2007) | https://www.helleniqenergy.com/en/media/regulatory-announcements/notification-important-changes-concerning-voting-rights-under-0 | POIH Investments Ltd holds 100% of POIH; 40.41% after 8.12.2023 |
| E7 | UK Companies House, EKO Cyprus Limited (00454043): overview + PSC register | https://find-and-update.company-information.service.gov.uk/company/00454043/persons-with-significant-control | Incorporated 1948 in UK, SIC 46711; PSC = HELLENiQ ENERGY Holdings S.A. (>=75%) |
| E8 | EKO Cyprus Limited, Annual Report and Financial Statements y/e 31.12.2025 (scanned, 53 pp) | https://find-and-update.company-information.service.gov.uk/company/00454043/filing-history/MzUzMzM2ODAzNGFkaXF6a2N4/document?format=pdf&download=0 (transcription kept: docs/eko_cyprus_fs2025.txt) | Revenue, operating profit, tax, total assets, dividends paid, staff costs, average employees (read visually from page images; no OCR) |
| E9 | cyprusregistry.com, PANEUROPEAN OIL AND INDUSTRIAL HOLDINGS (CYPRUS) LIMITED HE 456073 | https://cyprusregistry.com/companies/HE/456073 | Registered 05/02/2024, directors; shareholders paywalled |
| E10 | cyprusregistry.com, POIH INVESTMENTS LIMITED HE 252404 | https://cyprusregistry.com/companies/HE/252404 | Status "Dissolved due to merger"; Spiro J. Latsis director |
| E11 | Energy Press, tag page "Latsis group" (articles 25.04.2024, 19.04.2024, 06.05.2021) | https://energypress.eu/tag/latsis-group/ | "Paneuropean Oil & Industrial Holdings, a member of the Latsis group" (Tier 3) |
| E12 | Wikipedia, Spiros Latsis | https://en.wikipedia.org/wiki/Spiros_Latsis | Corroboration only: owner of Paneuropean; Geneva family office (Tier 4) |
| E13 | EAC, Χωριστοί Λογαριασμοί 31.12.2024 (audited separated accounts, 51 pp, dated 15.07.2025), Wayback snapshot 20260120022317 | https://www.eac.com.cy/EL/EAC/FinancialInformation/PublishingImages/Pages/separatedaccounts/%CE%A7%CF%89%CF%81%CE%B9%CF%83%CF%84%CE%BF%CE%AF%20%CE%9B%CE%BF%CE%B3%CE%B1%CF%81%CE%B9%CE%B1%CF%83%CE%BC%CE%BF%CE%AF%202024.pdf (archived: https://web.archive.org/web/20260120022317/ + URL; text kept: docs/eac_separated_accounts_2024.txt) | EAC FY2024 total revenue, operating profit, tax, total assets; legal status (Cap.171 public-law body, board appointed by Council of Ministers) |
| E14 | EAC Annual Reports page (live site) | https://www.eac.com.cy/EN/EAC/FinancialInformation/Pages/AnnualReports.aspx | Connection refused on 2026-09-24 |
| E15 | EAC Annual Report 2023 (Wayback 20260307154436) | https://www.eac.com.cy/EN/EAC/FinancialInformation/PublishingImages/Pages/AnnualReports/Annual%20Report%202023.pdf | Archived copy truncated at 5 MiB — unreadable; not used |
| E16 | Compass Lexecon case note: Petrolina conditional clearance for ExxonMobil Cyprus (search result only) | https://www.compasslexecon.com/cases/petrolina-group-secures-conditional-clearance-for-the-acquisition-of-exxonmobil-cyprus | CPC conditional clearance (context only; CPC decision itself not fetched) |
| E17 | Staroil Cyprus website / TotalEnergies Cyprus page (search results only) | https://en.staroilcyprus.com/ ; https://totalenergies.com/cyprus | Checked other retailers; nothing sourceable quickly |

### Energy — unresolved / doubts
- **Petrolina Ltd** shareholders beyond "Dinos Lefkaritis controls >20%" are not disclosed; registry extract is paywalled.
- **Lefkaritis persons / Iliana Theofanous**: residence not documented (country UNRESOLVED). Almost certainly Cypriot-resident family, but that's an assumption.
- **FAMILY_LEFKARITIS 14.8270%** and **Petrolina free float 36.2332%** are computed from AR disclosures (assuming no overlap between director-group totals).
- **Petrolina financials are group-level** (Greece = 160.4m of 559.4m revenue in 2025). Employee headcount not printed.
- **Paneuropean (Cyprus) Ltd** current parent: last Tier-1 statement (Dec 2023) names POIH Investments Ltd (100% of the then-S.A.); POIH Investments is now "dissolved due to merger" (per registry mirror), so the post-2024 chain is unverified. Latsis family link is Tier 3/4 only; the natural-person UBO %, and family residence (Geneva suggested by Tier 4 only) are unresolved.
- **eWise Cyprus (ex-ExxonMobil Cyprus)**: no financials; completion date given as 30 Jan 2026 in AR note 38 vs 31 Jan 2026 in the web announcement summary.
- **EAC**: FY2025 accounts and headcount not obtained (site down); FY2024 figures from separated accounts (sum = statutory totals presumably, not cross-checked with statutory FS). Personnel total not printed as a single line.
- **R.A.M. Oil Cyprus**: immediate parent unknown; only effective 100% group interest.
- **Other fuel retailers** (TotalEnergies/Staroil/Agip): not covered. Agip-branded stations in Cyprus are run by the Petrolina group under an Eni franchise (AR2025 mentions the Lefkaritis Oils–Agip Petroli agreement); Staroil ownership not sourced.

## Retail / supermarkets — documents consulted (all accessed 2026-09-24)

| # | Document | URL | Used for |
|---|----------|-----|----------|
| R1 | Cyprus Official Gazette No. 5507 (26.07.2024), Part B, notice 3523 — CPC concentration notification (Sklavenitis / Papantoniou via Guedo) | https://www.mof.gov.cy/mof/gpo/gazette.nsf/61F7F0D1F9FDA09BC2258B660021B1E7/$file/5507%2026%207%202024%20KYRIO%20MEROS%20TMIMA%20B.pdf (text kept: docs/gazette_5507_2024-07-26.txt) | Guedo = 100% subsidiary of Ellinikes Yperagores Sklavenitis AEE, only holds shares in Sklavenitis Kyprou Ltd; target C.A.C. Papantoniou Trading Ltd |
| R2 | inbusinessnews, 17.07.2024 | https://inbusinessnews.reporter.com.cy/article/409161/sto-mikroskopio-tis-epa-i-exagra-ton-yperagron-papantonioy-apo-tin-sklabenitis | Corroborates parties |
| R3 | ot.gr, 06.11.2024 (CPC approval) | https://www.ot.gr/2024/11/06/epixeiriseis/sklavenitis-egkrithike-apo-tin-kypriaki-epitropi-antagonismou-i-apoktisi-ton-yperagoron-papantoniou/ | CPC approval, 27 stores, 2,350 staff (CPC decision date 17.10.2024 from search snippet only) |
| R4 | Cyprus Mail, 06.11.2024 | https://cyprus-mail.com/2024/11/06/sklavenitis-completes-acquisition-of-papantoniou-supermarkets | Completion; staff counts |
| R5 | CBN, 04.02.2025 | https://www.cbn.com.cy/article/106393/sklavenitis-cyprus-completing-papantoniou-supermarkets-absorption | Integration; "close to €400m" combined turnover (estimate, notes only) |
| R9 | el.wikipedia, Σκλαβενίτης | https://el.wikipedia.org/wiki/%CE%A3%CE%BA%CE%BB%CE%B1%CE%B2%CE%B5%CE%BD%CE%AF%CF%84%CE%B7%CF%82 | Conflicting "95% bought by four children in 2006" (Tier 4) |
| R10 | sklavenitis.gr company & history pages (Wayback, 2026) | https://web.archive.org/web/2026/https://www.sklavenitis.gr/about/i-etaireia/ ; https://web.archive.org/web/2026/https://www.sklavenitis.gr/about/i-etaireia/istoria/ | Group companies; 2006 family buyout; Papantoniou integration. Live site 403; financial-statement PDFs on Wayback truncated |
| R11 | cyprusregistry.com, LIDL CYPRUS S 10823 | https://cyprusregistry.com/companies/S/10823 | Partnership, registered 25.09.2003, general partners Lidl Ventures Cyprus Ltd + Lidl Holding Ltd (verified by me) |
| R12 | companiesregistry.cy, LIDL HOLDING LIMITED HE 140701 | https://companiesregistry.cy/company-details/lidl-holding-limited-140701/ | Registration; shareholders paywalled |
| R13 | cyprusregistry.com, LIDL VENTURES CYPRUS LIMITED HE 297758 (search snippet only) | https://cyprusregistry.com/companies/HE/297758 | HE number |
| R14 | Lidl Cyprus corporate site + legal page | https://corporate.lidl.com.cy/en ; https://corporate.lidl.com.cy/en/legal-information | "member of the Schwarz Group based in Neckarsulm"; 20 stores; S 10823 |
| R15 | Business Insider DE via Yahoo Finanzen, 05.05.2026 (citing Handelsblatt) | https://de.finance.yahoo.com/nachrichten/reichste-deutsche-steckt-lidl-kaufland-104430093.html | 99.9% of Schwarz-Gruppe shares with Dieter-Schwarz-Stiftung; Schwarz veto (verified by me) |
| R16 | de.wikipedia, Schwarz-Gruppe; Dieter Schwarz Stiftung | https://de.wikipedia.org/wiki/Schwarz-Gruppe ; https://de.wikipedia.org/wiki/Dieter_Schwarz_Stiftung | Tier 4 corroboration of Unternehmenstreuhand/Beteiligungs structure (not used for edges) |
| R17 | inbusinessnews, 25.11.2024 (Alphamega / Papamichael CPC notice) | https://inbusinessnews.reporter.com.cy/article/2024/11/25/807794/uperagores-alphamega-endunamose-parousias-sten-papho-me-exagora-p-mm-papamichael-supermarket/ | Alphamega legal entity Χ.Α. Παπαέλληνας Εμπορική Λτδ |
| R18 | talanews reprint of Filenews, 14.04.2024 | https://talanews.blogspot.com/2024/04/the-map-of-supermarkets-in-cyprus-is.html | Alphamega "of the Papaellinas Group"; turnover estimates (notes only) |
| R19 | cyprusregistry.com, METRO SUPERMARKET EE 28879; METRO FOODS TRADING LIMITED HE 180802 | https://cyprusregistry.com/companies/EE/28879 ; https://cyprusregistry.com/companies/HE/180802 | Business-name owner; directors; shareholders paywalled |
| R20 | METRO Supermarkets, "Our philosophy" | https://www.metro.com.cy/en/about/our-philosophy | Founded Larnaca 1982; 7 stores; 650 employees; no METRO AG link (verified by me) |
| R21 | Bloomberg LEI 529900HSOVCXN27EZA04 (search snippet only) | https://lei.bloomberg.com/leis/view/529900HSOVCXN27EZA04 | Alphamega LEI (unverified) |

### Retail — unresolved / doubts
- **No Cyprus retail financials** from any filing (Lidl, Alphamega, Sklavenitis Cyprus, Metro, Papantoniou): all financial columns blank; press turnover estimates are in notes only.
- **Lidl**: shareholders of Lidl Holding Ltd / Lidl Ventures Cyprus Ltd not retrieved (paywall); the link to Schwarz Group is Tier 2 (group membership), and Lidl Stiftung & Co. KG as the intermediate owner is NOT documented in fetched sources. Schwarz 99.9%/0.1% split is Tier 3 (press citing Handelsblatt); voting control (Schwarz Unternehmenstreuhand KG) is Tier 4 only.
- **Sklavenitis**: Guedo's % in Sklavenitis Cyprus not stated; Guedo's country not stated; shareholders of the Greek parent (a private company) are not documented in Tier 1-2 sources, so they are left UNRESOLVED (press-reported splits were not used).
- **Papantoniou**: 100% acquisition inferred from "acquisition of the share capital"; post-integration legal status unknown.
- **Alphamega**: controller only Tier 3 ("Papaellinas Group"); Papaellinas Group shareholders unresolved.
- **Metro**: Cypriot-owned per company history; shareholders unresolved. Confirmed not METRO AG (no link found — absence of evidence).
- **Athienitis**: not covered.

---

## Sources: food delivery platforms and transport (Cyprus)

All documents accessed 2026-09-24. Text extracts (PDFs deleted after extraction) are in `data/raw/companies/docs/`.

## Documents consulted

| # | Document | URL | Used for |
|---|----------|-----|----------|
| 1 | DoorDash Inc. Form 10-K FY2025 (filed 2026-02-18). Extract: `doordash_10k_fy2025.txt` | https://www.sec.gov/Archives/edgar/data/1792789/000179278926000013/dash-20251231.htm | Group revenue USD 13,717m; revenue by geography (US 11,460 / International 2,257; no non-US country ≥10%); income from operations USD 723m; tax USD 7m; total assets USD 19,659m; >31,400 employees; Wolt Enterprises Oy acquired 31 May 2022 |
| 2 | DoorDash 10-K FY2025 Exhibit 21.1. Extract: `doordash_fy2025_ex21.txt` | https://www.sec.gov/Archives/edgar/data/1792789/000179278926000013/dash-fy2510xkxexx211.htm | "Wolt Oy (46)" in Finland, with 46 omitted wholly-owned direct subsidiaries abroad. **Wolt Cyprus Ltd is NOT named.** |
| 3 | DoorDash 2026 Proxy (DEF 14A, filed 2026-04-20). Extract: `doordash_def14a_2026.txt` | https://www.sec.gov/Archives/edgar/data/1792789/000179278926000018/dash-20260420.htm | Beneficial ownership at 2026-03-01: Vanguard, Sequoia entities, BlackRock, Tony Xu (55.5% of the vote), share counts |
| 4 | GLEIF LEI API, Wolt Oy (74370029CGDFPB7BUN89) and direct-parent record | https://api.gleif.org/api/v1/lei-records/74370029CGDFPB7BUN89 | Previous name Wolt Enterprises Oy; business ID 2646674-9; direct parent DoorDash, Inc. |
| 5 | Wolt Cyprus User Terms of Service (updated 06.08.2026) | https://explore.wolt.com/en/cyp/terms | Wolt Cyprus Limited HE 404490 / VAT CY10404490R; Wolt Oy 2646674-9 named as the group payment/claims entity |
| 6 | Wolt Country Entities List (Cyprus) | https://explore.wolt.com/en/cyp/wolt-entities-list | Wolt Cyprus Limited is the local joint controller within the Wolt group |
| 7 | Wolt Cyprus "About" page | https://explore.wolt.com/en/cyp/about | Launched in Cyprus in 2020; DoorDash deal closed 31 May 2022. Only global figures. |
| 8 | cyprusregistry.com, companiesregistry.cy, i-cyprus.com and northdata.com pages for HE 404490 | https://cyprusregistry.com/companies/%CE%97%CE%95/404490 ; https://companiesregistry.cy/company-details/wolt-cyprus-limited-404490/ ; https://i-cyprus.com/company/563709 ; https://www.northdata.com/Wolt+Cyprus+Ltd.,+%CE%9B%CE%B5%CF%85%CE%BA%CF%89%CF%83%CE%AF%CE%B1/MCIT+%CE%97%CE%95+404490 | Incorporated 26/11/2019, Active, directors. **Shareholders redacted; filings paywalled** (EUR 49 to 65 per report) |
| 9 | Wolt merchant pages for Cyprus: sign-up, self-delivery, fees and commissions explainer | https://merchant.wolt.com/en/cyp ; https://merchant.wolt.com/el-cy/cyp/product/self-delivery ; https://merchant.wolt.com/el-cy/cyp/learning-center/wolt-merchant-fees-and-commissions | Fee types only, with **no percentages** (see worked example) |
| 10 | Wolt "10 years" courier page (Cyprus site) | https://life.wolt.com/en/cyp/moments/10-years/courier-stories | Global figures only (EUR 3bn cumulative courier earnings, 450,000 couriers) |
| 11 | InBusinessNews, "Η μάχη του e-food delivery" (E. Antoniou, 21 Mar 2022) | https://inbusinessnews.reporter.com.cy/article/303890/i-machi-toy-e-food-delivery | Wolt: 1,000+ couriers, 20+ staff, up to 1,500 partners. Foody: 130 staff, 500+ riders, 2,100+ stores, >600k orders a month. No revenue or commission figures. |
| 12 | Nomisma.com.cy, "Wolt Consumer Report 2025" (9 Jun 2025) | https://nomisma.com.cy/business-category/wolt-consumer-report-2025-burgers-%CE%BA%CE%B1%CE%B9-%CE%BA%CE%B1%CF%86%CE%AD%CF%82-%CF%80%CF%81%CF%8E%CF%84%CE%B1-%CF%83%CF%84%CE%B9%CF%82-%CF%80%CF%81%CE%BF%CF%84%CE%B9%CE%BC%CE%AE%CF%83%CE%B5/ | Consumer trivia only. No business metrics. |
| 13 | BHRRC summary of Jacobin (Jan 2023) on the Dec 2022 Wolt strike | https://www.business-humanrights.org/en/latest-news/cyprus-migrant-workers-for-food-delivery-company-wolt-strike-over-pay-and-commission-charged-by-middlemen/ | ~2,800 couriers; EUR 2.26 per delivery; 41% fleet-manager cut. **Not verifiable in the original, which is paywalled.** |
| 14 | Jacobin, R. Stochita (8 Jan 2023) | https://jacobin.com/2023/01/cyprus-wolt-gig-delivery-workers-migrants-students-strike | Paywalled, so the figures in #13 could not be confirmed |
| 15 | Delivery Hero SE Annual Financial Statement 2025 (HGB), Annex I List of Shareholdings, plus management report section on holdings above 10%. Extract: `dh_se_afs2025.txt` | https://ir.deliveryhero.com/media/document/d7cd8a32-bb5e-48d0-a416-c38f9cad59e0/assets/DeliveryHeroSE_Annual_Financial.pdf | Delivery Hero (Cyprus) Ltd 100% (equity EUR 0.87m, 2025 result EUR -2.26m); Food Basket ... Ltd, Nicosia (TRY) 100%; Naspers via MIH Food Holdings B.V.; EC M.11936 voting restriction |
| 16 | EQS News DH reports list | https://www.eqs-news.com/company/delivery-hero-se/reports/5c0f63cc-ea7c-11e8-902f-2c44fd856d8c | Locating the FY2025 report URLs |
| 17 | Foody Delivery Services Terms of Service (27 Jul 2023) | https://blog.foody.com.cy/delivery-services-terms-of-service/ | Delivery Hero (Cyprus) Ltd, HE369772, operates Foody |
| 18 | Foody blog: "Foody joins the Delivery Hero family" (4 Sep 2019) | https://blog.foody.com.cy/foody-joins-the-delivery-hero-family-2/ | Acquisition announcement; no % given |
| 19 | Delivery Hero IR, Shareholder Structure (rendered via browser, last update Aug 2026) | https://ir.deliveryhero.com/shareholder-structure/ | Uber 20-25%; Naspers Group 16.83%; Aspex, Morgan Stanley, Conifer and UBS as ranges |
| 20 | Uber 8-K Ex.99.1 (16 Jul 2026). Extract: `uber_8k_2026-07-16_ex99-1.txt` | https://www.sec.gov/Archives/edgar/data/1543151/000155278126000382/e26302_ex99-1.htm | Uber 24.77% direct + 11.74% derivatives; Prosus irrevocable commitment (~17%); offer at EUR 41.50 |
| 21 | Uber 2026 Proxy (DEF 14A). Extract: `uber_def14a_2026.txt` | https://www.sec.gov/Archives/edgar/data/1543151/000130817926000125/uber014597-def14a.htm | Vanguard 9.34%, BlackRock 6.82%, Capital Research 5.78%, PIF 3.57% (2026-03-02) |
| 22 | Prosus, Shares in issue | https://www.prosus.com/investors/share-information/shares-in-issue | Naspers holds 901,813k of 2,093,576k net N shares (18 Sep 2026), i.e. 43.075% |
| 23 | Naspers, Group structure | https://www.naspers.com/the-group/group-structure | Prosus holds ~52.46% economic interest in Naspers (undated); Keerom/Nasbel voting control |
| 24 | North Data search snippet for Bolt Support Services CY Ltd (HE 427356) | https://www.northdata.com/Bolt%20Support%20Services%20CY%20Ltd.,%20%CE%9B%CE%B5%CF%85%CE%BA%CF%89%CF%83%CE%AF%CE%B1/MCIT%20%CE%97%CE%95%20427356 | Existence of a Bolt Cyprus entity. Page not fetched, so low confidence. |
| 25 | Hermes Airports Sustainability Report 2025. Extract: `hermes_sustainability_report_2025.txt` | https://www.hermesairports.com/media/cms/Sustainability_Report_2025_F4E1D035361C2.pdf | Shareholder table (9 holders, 100%); 2025 gross revenues EUR 275.1m, EBITDA EUR 118.5m, current tax EUR 12.1m, total tax charge EUR 10.1m, 162 employees |
| 26 | Hermes Airports Sustainability Report 2024. Extract: `hermes_sustainability_report_2024.txt` | https://www.hermesairports.com/media/cms/HermesSustainabilityReport2024_D170323A2BE23.pdf | 2024 cross-check: revenue 245.1 (table) vs 245.2 (chart), EBITDA 101.9, current tax 8.1, 158 employees; same shareholder %s |
| 27 | Hermes Airports, Who We Are | https://www.hermesairports.com/corporate/who-we-are | Shareholder list with descriptors (French, Irish and so on) |
| 28 | GLEIF records for Hermes (213800T6H1JEJR59A434), Charlie Airlines (213800S14PT3E5HGAL23) and East Med Holdings Ltd (984500VE5446054A3C11) | https://api.gleif.org/api/v1/lei-records/213800T6H1JEJR59A434 | Registration numbers; parent reporting exceptions |
| 29 | Bouygues, Ownership structure (Wayback snapshot, data at 31 Dec 2025) | https://www.bouygues.com/en/ownership-structure/ | SCDM 28.30 / employees 19.20 / other French 10.60 / foreign 41.60 / treasury 0.30 |
| 30 | Cyprus Airways, Our Story | https://www.cyprusairways.com/en/our-story | Ownership history: Arcosjet 2021-22; local investor minority 2024 and majority 2025 |
| 31 | CBN, interview with Nicos Ioannou (27 Mar 2026) | https://www.cbn.com.cy/article/127391/nicos-ioannou-in-2026-cyprus-airways-is-dynamically-entering-a-period-of-developing-partnerships-with-other-high-profile-airlines-video | >600,000 passengers in 2025; "new shareholders" not named |
| 32 | FlightGlobal (1 Jul 2021) | https://www.flightglobal.com/strategy/cyprus-airways-unveils-new-ownership-and-chief-executive/144421.article | Historical: SJC Group (Malta) acquisition |
| 33 | DP World Annual Report 2025. Extract: `dpworld_ar2025.txt` | https://dpw-p-001.sitecorecontenthub.cloud/api/public/content/58b211cb1aad4263be87f0d33fd0993f?v=b2febf77 | DP World Limassol Limited 75%; chain PFZW → Dubai World → Government of Dubai; Bamardo Limited (CY) 100% |
| 34 | P&O Maritime press release (27 Apr 2016) | https://pomaritime.com/news/dp-world-and-po-maritime-win-cyprus-port-consession-agreements/ | JV with G.A.P. Vassilopoulos Public Ltd, 75% DP World; P&O Maritime Cyprus |
| 35 | EUROGATE CTL introduction presentation. Extract: `eurogate_ctl_intro_presentation_2024.txt` | https://www1.eurogate.de/wp-content/uploads/2024/01/introduction_presentation_eurogate_container_terminal_limassol.pdf | EUROGATE International GmbH 60 / Interorient Navigation 20 / East Med Holdings S.A. 20 |
| 36 | EUROGATE, About us | https://www1.eurogate.de/en/about-us/ | EUROGATE owned 50/50 by EUROKAI and BLG |
| 37 | Cyprus Mail Wolt strike coverage, Dec 2022 (search listing only) | https://cyprus-mail.com/2022/12/16/wolt-strike-continues-deliveries-unavailable-in-parts-of-limassol-and-nicosia/ | Context only (100 to 200 strikers). Not used for data. |
| 38 | Kluwer Competition Law Blog, "Main Developments ... 2024 / 2025 Cyprus" | https://legalblogs.wolterskluwer.com/competition-blog/main-developments-in-competition-law-and-policy-2025-cyprus/ | Neither year mentions a food-delivery case |
| 39 | Cyprus Commission for the Protection of Competition website (decisions pages) | https://www.competition.gov.cy/competition/competition.nsf/desicions_en/desicions_en?OpenDocument= | Searched; site search not machine-queryable (Notes DB 404s). **No Wolt/Foody decision located.** |

Tried but blocked or unusable: D&B profile of Wolt Cyprus (Cloudflare 403); opencorporates (captcha); b2bhint (403); Foody terms PDFs on foody.com.cy (403 or HTML); ctcgroup.com (403); bouygues.com PDFs (403); cyprustimes.com (403). Search-result summaries (for example "D&B: ultimate parent Wolt Enterprises Oy" and "Arcosjet 100% owner") were **not** used as data unless confirmed by fetching the page.

## Wolt Cyprus worked example

- **Legal entity:** Wolt Cyprus Limited, HE 404490, VAT CY10404490R, Digeni Akrita 26, Nicosia. Incorporated 26 Nov 2019; the service launched in 2020 (Wolt About page).
- **Ownership chain:** Wolt Cyprus Ltd → Wolt Oy (FI; formerly Wolt Enterprises Oy, 2646674-9) → DoorDash, Inc. (US) → dispersed holders (Vanguard 9.1%, Sequoia 7.3%, BlackRock 5.5%, Tony Xu 2.5% of equity but 55.5% of the vote).
  - The Wolt Oy → DoorDash link is Tier 1 (Exhibit 21.1 plus GLEIF).
  - **The Wolt Cyprus → Wolt Oy link is inferred (100%, low confidence).** Exhibit 21.1 does not name Wolt Cyprus. It is covered only by "Wolt Oy (46)", meaning 46 omitted wholly-owned direct subsidiaries. The Cyprus registrar's shareholder data is redacted or paywalled, and Wolt Cyprus has no LEI.
- **Financial statements:** Not available.
  - Registrar filings (HE 404490) cost EUR 49 to 65 through third-party resellers.
  - No Stockwatch, Phileleftheros, Cyprus Mail or CBN article quoting Wolt Cyprus revenue, profit or tax was found.
  - DoorDash does not disclose Cyprus separately. International revenue is only reported in aggregate: USD 2,257m in 2025, 16.5% of the total, with no single non-US country at 10% or more.
- **Couriers and scale:**
  - 1,000+ couriers, 20+ staff and up to 1,500 partner venues in March 2022 (InBusinessNews, Tier 3).
  - ~2,800 couriers, EUR 2.26 per delivery and a 41% fleet-manager cut in December 2022 (BHRRC citing a paywalled Jacobin article; unverified).
  - No 2024 or 2025 courier count was found.
- **Restaurant commission rates:** **Not published for Cyprus.**
  - Wolt's Cyprus merchant pages list the fee types without percentages: standard delivery commission, a "slightly higher" Wolt+ commission, reduced pickup and self-delivery commissions, a platform fee, and device reimbursement. Enquiries go to info@wolt.com.
  - The 27% to 30% figures found in the press refer to Wolt and efood in **Greece**, not Cyprus, and were not used.
- **CPC (Commission for the Protection of Competition) investigation:** **Not found.**
  - Neither the CPC website, Kluwer's 2024 and 2025 Cyprus reviews, nor English or Greek searches surfaced a CPC decision or investigation on Wolt, Foody or Bolt.
  - The Greek "Επιτροπή Ανταγωνισμού" Delivery Hero case (decision 775/2022, epant.gr) concerns **Greece** and is not relevant.
  - Recent Cyprus coverage (Cyprus Mail, 12 Jun 2026) concerns food-hygiene complaints handled by the health services, not competition.
  - If the brief's premise of a CPC case is correct, it has to be retrieved manually from competition.gov.cy (the decisions register or the Official Gazette).

## Unresolved items

1. Wolt Cyprus: the immediate shareholder is not verified (a registrar extract is needed) and no financials are available.
2. Delivery Hero (Cyprus) Ltd (Foody): revenue and employee numbers are not disclosed. Only equity (EUR 0.87m) and the 2025 result (EUR -2.26m) are available.
3. Delivery Hero ownership is in flux. Uber's takeover offer (acceptance period to 5 Nov 2026) would take Uber to about 53% economic ownership with the Prosus stake. The Aspex, Morgan Stanley, Conifer and UBS holdings are disclosed as ranges only.
4. Naspers and Prosus hold economic stakes in each other (Prosus ~52.46% of Naspers N shares). The edge is included and flagged CIRCULAR.
5. Bolt Food: the Cypriot operating entity and its owner are unresolved. Bolt Support Services CY Ltd (HE 427356) is taken from a search snippet only.
6. Hermes shareholders' own owners are unresolved: Egis Investment Partners S.C.A. (jurisdiction unknown), Halpi Alpha Ltd, Hellenic Mining, AER Rianta International (Middle East) WLL, Vantage Airport Group (Cyprus) Ltd, Iacovou Brothers, Charilaos Apostolides, and Nice Airports Engineering. The Bouygues Construction Airport Concessions Europe → Bouygues SA link is inferred.
7. Hermes financials come from the company's sustainability report, not audited statements. Operating profit, total assets, personnel costs and dividends are missing.
8. Cyprus Airways (Charlie Airlines Ltd): the majority "local investor group" (2025) and the remaining Arcosjet stake are unidentified, and there are no financials.
9. Limassol port:
   - The G.A.P. Vassilopoulos 25% is implied from a 2016 press release.
   - P&O Maritime Cyprus's ownership is internally inconsistent in the source (wholly-owned versus the 75/25 JV).
   - EUROGATE International GmbH's parent percentage, and the owners of Interorient and East Med Holdings S.A., are unresolved.
   - None of the Limassol operators' financials were found.
10. Food Basket Elektronik Iletisim Gida Ticaret Ltd (DH, "Nicosia (CY)", TRY currency) is very probably in the north of the island. Exclude it from Republic of Cyprus aggregates unless confirmed otherwise.

---

## Sources: hotels, construction/real estate, professional services (Cyprus)

All accessed 2026-09-24. PDFs were converted to text (kept in `../docs/*.txt`), and the PDFs were then deleted.

## Tier 1: filings, audited reports, transparency reports
| Document | URL | Used for |
|---|---|---|
| KPMG in Cyprus Transparency Report 2025 (FY to 31 Dec 2025) | https://assets.kpmg.com/content/dam/kpmgsites/cy/pdf/2026/transparency-report-2025.pdf.coredownload.inline.pdf | Legal structure (owned by partners), revenue EUR 50.878m, 730 staff (`docs/kpmg_cy_tr2025.txt`) |
| PwC Cyprus Transparency Report 1 Jul 2024 to 30 Jun 2025 | https://www.pwc.com.cy/en/publications/assets/fy25-transparency-report.pdf | Owned by partners, 35 partners, turnover EUR 86.0m (`docs/pwc_cy_tr_fy25.txt`). The site returns 403 to curl's default UA; the download worked with a HeadlessChrome UA |
| Deloitte Limited 2025 Transparency Report (FY to 31 May 2025) | https://www.deloitte.com/content/dam/assets-zone2/cy/en/docs/about/2025/deloitte-transparency-report-2025.pdf | Chain Deloitte Ltd, then DHL, then IE CLG / GG LLP / CY partnership; turnover EUR 58.8m (`docs/deloitte_cy_tr2025.txt`) |
| EY Cyprus Transparency Report 2025 (FY to 30 Jun 2025) | https://www.ey.com/content/dam/ey-unified-site/ey-com/en-cy/services/audit-quality/documents/ey-cyprus-transparency-report-fy25.pdf | Economic rights held by EY partnership, voting rights held by EY Europe SRL (BE); revenue EUR 55.6m (`docs/ey_cy_tr_fy25.txt`) |
| Louis plc Annual Report & FS 2025 (Greek) | https://www.louisplc.com/wp-content/uploads/2026/05/Louis-plc-FS25.pdf | Clin Company 66.968%; ultimate controlling person Kostakis Loizou; P&L, geography split, headcount (`docs/louis_plc_fs2025.txt`) |
| Leptos Calypso Hotels FS 2025 (Greek, full) | https://leptoscalypso.com.cy/wp-content/uploads/2026/05/Leptos-Calypso-Hotels-Public-Limited-Consolidated-FS-2025-Greek.pdf | >5% holders, ultimate parent Armonia Estates (CY), staff costs/avg staff, dividends (`docs/leptos_calypso_fs2025_gr.txt`) |
| Leptos Calypso Hotels FS 2025 (English extract) | https://leptoscalypso.com.cy/wp-content/uploads/2026/05/Leptos-Calypso-Hotels-Public-Limited-Consolidated-FS-2025-English.pdf | Cross-check of P&L and balance sheet (`docs/leptos_calypso_fs2025.txt`) |
| Vassiliko Cement Works Annual Report 2025 | https://www.vassiliko.com/images/media/redirectfile/Financial%20Reports/2025/Annual_Report_2025_ENG_WS_VR_compressed.pdf | Note 30 >5% holders (incl. Heidelberg and Archbishopric attribution notes), P&L, staff, dividends (`docs/vassiliko_ar2025.txt`) |
| Cyprus Cement Public Co. FS 2025 (Greek) | https://www.galatariotisgroup.com/wp-content/uploads/2026/04/Financial-Statements-2025-1.pdf | >5% holders at 29 Apr 2026; parent C.C.C. Holdings; ultimate parent G.S. Galatariotis & Sons (both CY) (`docs/cyprus_cement_fs2025.txt`) |
| Pandora Investments Public Ltd FS 2025 (English extract of audited FS) | https://pandora.com.cy/download/1685/ | Revenue, operating profit, tax, total assets (`docs/pandora_fs2025.txt`) |
| Heidelberg Materials IR: shareholder structure | https://www.heidelbergmaterials.com/en/investor-relations/share/shareholder-structure | Spohn Cement (L. Merckle) 28.40%, free float 71.60% (verified in the raw HTML) |
| Heidelberg Materials AG Annual Financial Statements 2024 | https://www.heidelbergmaterials.com/sites/default/files/2025-03/HM_Annual_Financial_Statements_2024_ujAOdfIEBXpZLqw0.pdf | "Italmed Cement Company Ltd., Cyprus" listed as a group mandate, which gives Italmed's country (`docs/heidelberg_afs2024.txt`) |

## Tier 2: company websites / publications
| Document | URL | Used for |
|---|---|---|
| PwC Cyprus Annual Review 2025 (Wayback copy 20251014) | https://www.pwc.com.cy/en/publications/assets/annual-review-2025.pdf | ">1,100 people", EUR 28.9m contribution to government revenues (context only) (`docs/pwc_cy_ar2025.txt`) |
| Lanitis E.C. Holdings: Cybarco Holdings page | https://www.lanitis.com/en/companies/subsidiaries/cybarco-holdings-ltd | Cybarco Holdings listed as a subsidiary of Lanitis E.C. Holdings |
| Lanitis E.C. Holdings: Brief history | https://www.lanitis.com/en/lanitis-e-c-holdings/brief-history | Lanitis E.C. Holdings is the group holding company; family leadership |

## Tier 3: press / registry mirrors
| Document | URL | Used for |
|---|---|---|
| Reporter.com.cy, 24 Jan 2026, "Major shareholders of 40 Cypriot companies" (CSE dispersion statements at 31 Dec 2025) | https://www.reporter.com.cy/article/1379146/oi-meglometochoi-40-etaireion-tis-kyproy-oi-anakatataxeis-sta-metochika-kefalaia-ton-eisigenon | A. Tsokkos Hotels holders; Pandora holders; KEO holders; free-float cross-checks (verified in the raw HTML) |
| i-cyprus.com: CLIN COMPANY LIMITED | https://i-cyprus.com/company/27382 | Clin Company registered in Cyprus, HE 1378 |

## Consulted, not used for data
- PwC Cyprus FY24 transparency report (superseded by FY25); Leptos Calypso announcements page (index only); Tsokkos website (no IR PDFs found); Stockwatch symbol pages (404); galatariotisgroup.com announcement page (index); Simply Wall St / MarketScreener / search snippets (not used for numbers).

## Unresolved items
1. **Individuals' residence**: Kostakis Loizou, George M. and Pantelis M. Leptos, George St. Galatariotis, the Tsokkos family, and Ludwig Merckle. The filings don't state residence or nationality, so all are set to `UNRESOLVED`.
2. **Partner nodes for KPMG, PwC and EY** are coded CY by inference: they are practitioners working in the Cyprus firm, but the reports don't state their residence. Confidence is medium.
3. **Deloitte**: the % split of Deloitte Holdings Ltd among the IE CLG (majority voting), the GG LLP and the CY partnership isn't printed. Members of the CLG and the LLP aren't disclosed.
4. **EY**: EY Europe SRL's owners aren't disclosed. The economic vs. voting split is recorded as two separate 100% edges (equity to the partnership, voting to EY Europe).
5. **Holding %s not disclosed**: Clin Company owned by Loizou, Armonia and M Leptos Holdings owned by the Leptos brothers, Italmed and CFP owned by Heidelberg, C.C.C. Holdings owned by G.S. Galatariotis & Sons, and G.S. Galatariotis & Sons / K+G Complex owned by George St. Galatariotis. All are recorded as control edges with a blank share_pct.
6. **Countries unverified**: M Leptos Holdings and the A.G. Leventis Foundation are coded `XX_`/UNRESOLVED. CFP S.a.s is coded FR, inferred from its legal form. K+G Complex, KEO, Pandora and A. Tsokkos Hotels are coded CY, inferred from their CSE listing.
7. **Leptos Calypso**: the three >5% holders total 56.52%. The directors' table attributes 37.45% and 37.49% to the two brothers, and the press reports a free float of 30.38%. These don't reconcile, so the residual 43.48% may include more Leptos-linked holdings.
8. **Missing financials**: A. Tsokkos Hotels (no FS obtained) and Cybarco (private) have no financials. EBITDA isn't printed for Vassiliko, Leptos Calypso or Pandora. The Big-4 "contribution to government revenues" figures aren't corporate tax, so they are left blank.
9. **Not covered**: J&P Avax (Greek, ATHEX), Pafilia, Leptos Estates, Imperio, Trust International and Constantinou Bros. None was researched. The last five are private, and no Tier-1 ownership or financial source was attempted for them.
10. **Group vs. Cyprus scope**: Louis plc figures are group-level, including Greece; the Cyprus segment revenue is EUR 115.493m (noted). Pandora's extract isn't geographically segmented.
