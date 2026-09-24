# Sources: hotels, construction/real estate, professional services (Cyprus)

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
