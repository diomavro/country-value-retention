"""Banking-sector rows (hand-transcribed from the cited documents; see SOURCES.md)."""
import csv, pathlib
OUT = pathlib.Path(__file__).resolve().parents[1] / "_fragments"
EC = ["entity_id","legal_name","country_of_incorporation","nace_code","sector","fiscal_year","revenue_eur_m","operating_profit_eur_m","ebitda_eur_m","employees","total_assets_eur_m","personnel_costs_eur_m","taxes_eur_m","dividends_paid_eur_m","source","source_url","source_tier","confidence","notes"]
ED = ["child_entity_id","parent_entity_id","share_pct","share_type","as_of_date","source","source_url","source_tier","confidence","notes"]

BOC_AFR = ("Bank of Cyprus Holdings plc, Annual Financial Report 2025 (published 31 Mar 2026)",
           "https://www.bankofcyprus.com/globalassets/group/investor-relations/annual-reports/english/20260331-afr-boch-group-31.12.2025.pdf")
BOC_MH = ("Bank of Cyprus IR web page 'Major Holders of shares and financial instruments'",
          "https://www.bankofcyprus.com/en-gb/group/investor-relations/shareholder-information/major-holders-of-shares-and-financial-instruments/")
LAM = ("Lamesa Investments Ltd v Cynergy Bank Ltd [2019] EWHC 1877 (Comm), judgment 12 Sep 2019, para on parties",
       "https://www.brickcourt.co.uk/images/uploads/documents/CL-2018-000826_Lamesa_v_Cynergy_Final_Judgment-11.pdf")
ERB = ("Eurobank S.A. Annual Financial Report for the year ended 31 Dec 2025 (Report of the Directors; note 44 operating segments), mirror of ATHEX/CSE announcement",
       "https://www.stockwatch.com.cy/storage/symbol_announcements/69ae62e6d9336.pdf")
ABC_RBI = ("Retail Banker International, 'Alpha Bank Cyprus to buy AstroBank in EUR205m deal', 28 Feb 2025",
           "https://www.retailbankerinternational.com/news/alpha-bank-cyprus-buy-astrobank/")
ABC_CM = ("Cyprus Mail, 'Alpha Bank completes AstroBank deal, forming Cyprus' third-largest lender', 3 Nov 2025",
          "https://cyprus-mail.com/2025/11/03/alpha-bank-completes-astrobank-deal-forming-cyprus-third-largest-lender")
UC = ("MarketScreener (relaying Alpha Bank regulatory announcement): 'Alpha Bank says Unicredit has 29.8% in voting rights and financial instruments which potentially give it another 2.27%'; UniCredit press release Jan 2026 (403 to automated fetch)",
      "https://www.marketscreener.com/news/alpha-bank-says-unicredit-has-29-8-in-voting-rights-and-financial-instruments-which-potentially-giv-ce7e59d3db80f023")

def e(id_, name, ctry, nace, sector, src, tier, conf, notes, fy="", **fin):
    r = dict.fromkeys(EC, ""); r.update(entity_id=id_, legal_name=name, country_of_incorporation=ctry, nace_code=nace,
        sector=sector, fiscal_year=fy, source=src[0], source_url=src[1], source_tier=tier, confidence=conf, notes=notes); r.update(fin); return r
def g(c, p, pct, typ, asof, src, tier, conf, notes=""):
    return dict(zip(ED, [c, p, pct, typ, asof, src[0], src[1], tier, conf, notes]))

ents = [
 e("CY_BOC_PCL","Bank of Cyprus Public Company Ltd","CY","64","banking",BOC_AFR,1,"high",
   "Operating bank; 100% subsidiary of IE_BOC_HOLDINGS. Financials reported at BOCH group level (see IE_BOC_HOLDINGS row)."),
 e("IE_BOC_HOLDINGS","Bank of Cyprus Holdings Public Limited Company","IE","64","banking",BOC_AFR,1,"high",
   "Incorporated in Ireland (co. no. 585903), 'domiciled in Ireland and tax resident in Cyprus' (AFR note 1). Listed ATHEX/LSE. Group figures; AFR: 'Group's significant geographical area is Cyprus'; avg FTE 2,866 Cyprus + 7 other countries. revenue = total operating income EUR1,039.477m; operating_profit column holds PROFIT BEFORE TAX (EUR548.878m) - banks have no operating-profit line; taxes = income tax expense; dividends = cash dividend paid on ordinary shares in 2025 (EUR280.356m; excl. EUR30m buyback). Group includes EuroLife and General Insurance of Cyprus (100%). No shareholder-by-residence breakdown found in AFR 2025, FY2025 results presentation, or IR shareholder pages.",
   fy="2025", revenue_eur_m="1039.5", operating_profit_eur_m="548.9", employees="2873", total_assets_eur_m="28568.4",
   personnel_costs_eur_m="225.2", taxes_eur_m="65.8", dividends_paid_eur_m="280.4"),
 e("CY_LAMESA_INVESTMENTS","Lamesa Investments Limited","CY","64","holding",LAM,1,"medium",
   "Cyprus-incorporated holding; wholly owned by Lamesa Group Inc (BVI) per 2019 judgment. Ownership chain as of 2019; not re-verified for 2025-26. US-sanctioned (SDN-linked) since 2018."),
 e("VG_LAMESA_GROUP_INC","Lamesa Group Incorporated","VG","","holding",LAM,1,"medium","BVI company; wholly owned by Viktor Vekselberg per 2019 judgment."),
 e("PERSON_VEKSELBERG_VIKTOR","Viktor Vekselberg","UNRESOLVED","","person",LAM,1,"medium",
   "Judgment describes him as 'a Russian national' - nationality only: RU. Country of residence not documented in consulted sources."),
 e("US_SENVEST_MANAGEMENT","Senvest Management LLC","US","66","fund_manager",BOC_AFR,1,"medium",
   "Investment manager (New York); holding is on behalf of managed funds - beneficial owners' residence UNRESOLVED. Country = manager's location (not verified from a filing; widely reported as New York)."),
 e("US_WELLINGTON_MANAGEMENT","Wellington Management Group LLP","US","66","fund_manager",BOC_AFR,1,"medium",
   "Investment manager (Boston); holds for client funds - beneficial owners' residence UNRESOLVED. Country = manager's location (general knowledge, not from filing)."),
 e("US_EATON_VANCE_MANAGEMENT","Eaton Vance Management","US","66","fund_manager",BOC_AFR,1,"medium",
   "Investment manager (Morgan Stanley group); holds for client funds - beneficial owners' residence UNRESOLVED. Country = manager's location (general knowledge, not from filing)."),
 e("CY_BANK_EMPLOYEES_PROVIDENT_FUND","Provident Fund of the Cyprus Bank Employees","CY","65","pension_fund",BOC_AFR,1,"high",
   "Cypriot employee provident fund; beneficiaries are Cyprus bank employees (residence assumed CY - not documented)."),
 e("UNRESOLVED_OSOME_INVESTMENTS","Osome Investments (Limited)","UNRESOLVED","","holding",BOC_AFR,1,"low",
   "3.40% holder of BOCH. Country of incorporation and ultimate owner NOT found in any consulted source."),
 e("DISPERSED_FREE_FLOAT_IE_BOC_HOLDINGS","Dispersed free float of Bank of Cyprus Holdings","UNRESOLVED","","free_float",BOC_AFR,1,"medium",
   "Residual = 100 - sum of >=3% notified holders at 11 Mar 2026 (35.60%). No residence breakdown published."),
 e("CY_EUROBANK_LTD","Eurobank Limited (formerly Hellenic Bank Public Company Ltd)","CY","64","banking",ERB,1,"high",
   "Hellenic Bank renamed Eurobank Limited after 1 Sep 2025 transfer of Eurobank Cyprus Ltd's business to it; merger completed 3 Dec 2025. Figures = Eurobank S.A. note 44 'International' segment, Cyprus column = Eurobank Limited AND its insurance subsidiaries (incl. ex-CNP Cyprus, acquired 16 Apr 2025). revenue = total revenue EUR994m; operating_profit column holds PROFIT BEFORE TAX from continuing ops EUR579m (after EUR45m restructuring and EUR35m special bank levy); total_assets = segment assets EUR28,742m; employees = Cyprus headcount 2,905 (sustainability statement). Cyprus-only.",
   fy="2025", revenue_eur_m="994", operating_profit_eur_m="579", employees="2905", total_assets_eur_m="28742"),
 e("CY_EUROBANK_CYPRUS_LTD","Eurobank Cyprus Ltd (renamed ERB Cyprus Holdings Ltd; dissolved Dec 2025)","CY","64","banking",ERB,1,"high",
   "Banking business transferred to CY_EUROBANK_LTD effective 1 Sep 2025; entity dissolved after 3 Dec 2025. Kept only for historical linkage; do NOT add its financials to CY_EUROBANK_LTD (double count)."),
 e("GR_EUROBANK_SA","Eurobank S.A.","GR","64","banking",ERB,1,"high",
   "Greek bank; after 2025 merger with its former parent Eurobank Ergasias Services and Holdings S.A., Eurobank S.A. is the listed entity (ATHEX, parallel CSE listing). Group PBT 2025 EUR1,681m (continuing) - group level, not Cyprus."),
 e("CA_FAIRFAX_FINANCIAL","Fairfax Financial Holdings Limited","CA","65","holding",ERB,1,"high",
   "Canadian insurance holding (TSX-listed). Own shareholder structure not researched here (controlled via multiple-voting shares by its chairman per general knowledge - UNVERIFIED)."),
 e("DISPERSED_FREE_FLOAT_GR_EUROBANK_SA","Dispersed free float of Eurobank S.A.","UNRESOLVED","","free_float",ERB,1,"medium",
   "Residual 67.33% = 100 - Fairfax 32.67% (only >=5% holder reported). No residence breakdown found."),
 e("CY_ALPHA_BANK_CYPRUS","Alpha Bank Cyprus Ltd","CY","64","banking",ABC_CM,3,"medium",
   "Absorbed substantially all of AstroBank's assets, liabilities and personnel effective 31 Oct 2025 (EUR205m deal). Post-deal: total assets 'exceeding EUR6.6bn', loans >EUR2bn, deposits >EUR5.6bn (press, not audited statements). Audited 2025 statements not retrievable: alpha.gr and alphabank.com.cy return HTTP 403 to automated access (curl, WebFetch, Playwright)."),
 e("CY_ASTROBANK","AstroBank Public Company Ltd","CY","64","banking",ABC_RBI,3,"medium",
   "Banking business transferred to CY_ALPHA_BANK_CYPRUS on 31 Oct 2025; no longer a separate operating bank. Former owners (per press) BLC Bank / Sehnaoui family (Lebanon) - not needed for current attribution, not verified in a filing."),
 e("GR_ALPHA_BANK_SA","Alpha Bank S.A.","GR","64","banking",UC,3,"medium",
   "ATHEX-listed Greek bank (parent of Alpha Bank Cyprus). Annual Report 2025 (alpha.gr) blocked (HTTP 403) - major-holder list could not be read from the filing itself."),
 e("IT_UNICREDIT","UniCredit S.p.A.","IT","64","banking",UC,3,"medium","Italian listed bank; own shareholder structure not researched (dispersed)."),
 e("DISPERSED_FREE_FLOAT_GR_ALPHA_BANK_SA","Dispersed free float of Alpha Bank S.A.","UNRESOLVED","","free_float",UC,3,"low",
   "Residual 70.2% = 100 - UniCredit 29.8%; other >=5% holders not verified because the annual report was inaccessible."),
]
edges = [
 g("CY_BOC_PCL","IE_BOC_HOLDINGS","100","equity","2025-12-31",BOC_AFR,1,"high","AFR 2025 list of main subsidiaries."),
 g("IE_BOC_HOLDINGS","CY_LAMESA_INVESTMENTS","9.50","voting","2026-03-11",BOC_AFR,1,"high","41,383,699 shares of 435,962,305. Also on IR major-holders page."),
 g("IE_BOC_HOLDINGS","US_SENVEST_MANAGEMENT","9.25","voting","2026-03-11",BOC_AFR,1,"high","Shares; plus 0.36% via financial instruments (not included). 9.68% total on IR page (later notification)."),
 g("IE_BOC_HOLDINGS","US_WELLINGTON_MANAGEMENT","4.94","voting","2026-03-11",BOC_AFR,1,"high",""),
 g("IE_BOC_HOLDINGS","CY_BANK_EMPLOYEES_PROVIDENT_FUND","4.76","voting","2026-03-11",BOC_AFR,1,"high",""),
 g("IE_BOC_HOLDINGS","US_EATON_VANCE_MANAGEMENT","3.75","voting","2026-03-11",BOC_AFR,1,"high","3.35% at 31 Dec 2025; not listed on IR page at access date (may have fallen below 3%)."),
 g("IE_BOC_HOLDINGS","UNRESOLVED_OSOME_INVESTMENTS","3.40","voting","2026-03-11",BOC_AFR,1,"high",""),
 g("IE_BOC_HOLDINGS","DISPERSED_FREE_FLOAT_IE_BOC_HOLDINGS","64.40","equity","2026-03-11",BOC_AFR,1,"medium","Computed residual 100-35.60; holders below 3% threshold, residence unknown."),
 g("CY_LAMESA_INVESTMENTS","VG_LAMESA_GROUP_INC","100","equity","2019-09-12",LAM,1,"medium","'wholly owned by Lamesa Group Incorporated'. As of 2019."),
 g("VG_LAMESA_GROUP_INC","PERSON_VEKSELBERG_VIKTOR","100","equity","2019-09-12",LAM,1,"medium","'LGI is wholly owned by Mr. Viktor Vekselberg'. As of 2019."),
 g("CY_EUROBANK_LTD","GR_EUROBANK_SA","100","equity","2025-12-03",ERB,1,"high","93.47% (11 Feb 2025) -> 97.994% after takeover bid (25 Apr 2025) -> 100% after squeeze-out (11 Jun 2025); sole shareholder after 3 Dec 2025 merger steps."),
 g("CY_EUROBANK_CYPRUS_LTD","GR_EUROBANK_SA","100","equity","2025-08-29",ERB,1,"high","'wholly owned subsidiaries in Cyprus, i.e. Hellenic Bank and Eurobank Cyprus'. Dissolved Dec 2025."),
 g("GR_EUROBANK_SA","CA_FAIRFAX_FINANCIAL","32.67","voting","2025-12-12",ERB,1,"high","1,186,363,895 voting rights, direct and indirect; only >=5% holder reported."),
 g("GR_EUROBANK_SA","DISPERSED_FREE_FLOAT_GR_EUROBANK_SA","67.33","equity","2025-12-12",ERB,1,"medium","Computed residual."),
 g("CA_FAIRFAX_FINANCIAL","UNRESOLVED","","equity","",ERB,1,"low","Fairfax's own shareholders not researched; Canadian-listed."),
 g("CY_ALPHA_BANK_CYPRUS","GR_ALPHA_BANK_SA","100","equity","2025-02-28",ABC_RBI,3,"medium","'Alpha Bank Cyprus, a fully owned subsidiary of Alpha Holdings' (Alpha Services and Holdings, since merged into Alpha Bank S.A.). Tier 3 only: Alpha filings blocked."),
 g("GR_ALPHA_BANK_SA","IT_UNICREDIT","29.8","voting","2026-01-05",UC,3,"medium","Plus 2.27% via financial instruments (not included). Physical stake after conversion of synthetic position, per UniCredit PR (Jan 2026) as relayed."),
 g("GR_ALPHA_BANK_SA","DISPERSED_FREE_FLOAT_GR_ALPHA_BANK_SA","70.2","equity","2026-01-05",UC,3,"low","Computed residual; other holders unverified."),
 g("IT_UNICREDIT","UNRESOLVED","","equity","",UC,3,"low","UniCredit shareholder base not researched."),
]
with open(OUT/"banking_entities.csv","w",newline="") as f:
    w=csv.DictWriter(f,EC); w.writeheader(); w.writerows(ents)
with open(OUT/"banking_edges.csv","w",newline="") as f:
    w=csv.DictWriter(f,ED); w.writeheader(); w.writerows(edges)
print(len(ents), len(edges))
