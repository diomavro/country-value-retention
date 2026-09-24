# Insurance and telecoms fragment: sources

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
