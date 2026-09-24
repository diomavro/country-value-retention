# Literature map — "Who captures the value generated in a country?"

Diomides Mavroyiannis (Milestone Institute). Built 2026-09-24 with `write-paper/subskills/literature-review.md`.
Bibliography: `paper/references.bib` (56 entries, all verified; see "Verification" at the end).

## 1. Contribution in one paragraph

The paper asks what share of the value added generated on a country's territory ends up as income of residents, and who (by country and institutional sector) receives the rest.
Methodologically nothing here is a new estimator: Leontief inversion with domestic and imported input blocks, value-added-in-trade from FIGARO/TiVA, foreign-owned capital income from FATS and BoP direct-investment income, and the GDP-to-GNI bridge are all standard.
The contribution is to **join three layers that the literature keeps separate** — (i) *residence* (SNA/BPM6 primary income flows), (ii) *ownership/control* (FATS, ultimate controlling investor, SPE look-through), and (iii) *value chains* (Leontief/VAX decomposition of final demand) — into **one auditable recipient-country × sector tensor** whose layers are guaranteed to add up to GDP without double counting, with an explicit SPE adjustment so that pass-through income in a conduit economy (Cyprus) is not recorded as either domestic retention or genuine foreign capture.

## 2. Strands and key papers

### S1. Input–output foundations and value added in trade (the value-chain layer)
What it establishes: gross trade double-counts; the value-added content of final demand can be traced exactly via the Leontief inverse; the decompositions agree on country totals but differ on bilateral/sector attribution.

| Key | Relevance |
|---|---|
| Leontief1936; MillerBlair2009 | Core accounting: domestic vs imported technical coefficients, `V(I-A_d)^{-1}` multipliers used for the single-country block. |
| HummelsIshiiYi2001 | Vertical specialisation (import content of exports) — the first "leakage via imported inputs" metric. |
| JohnsonNoguera2012 | VAX ratio; value added by source country absorbed in destination — our value-chain layer's baseline. |
| KoopmanWangWei2014; LosTimmerdeVries2016 | Gross-export decomposition and double-counting terms; Los et al. show a simpler hypothetical-extraction equivalent. Our double-counting guarantee borrows this logic. |
| LosTimmerdeVries2015 | "How global are GVCs": foreign value added in final products — the production-location share we contrast with income-recipient shares. |
| Johnson2018; AntrasChor2022 | Surveys; place our accounting within GVC measurement, and document that all these measures are *location*-based, not *ownership*-based. |
| Timmeretal2015; Yamanoetal2021; Eurostat2019FIGARO; Ahmadetal2017 | Data infrastructure (WIOD, OECD ICIO/TiVA, FIGARO) and indicator definitions we implement. |

Gap: all of these attribute value added to the country where the factor is *located*, so profits of a foreign-owned Cypriot affiliate count as "Cypriot value added".

### S2. Income-based value-chain accounting ("GVC income", trade in factor income)
What it establishes: value chains can be sliced by factor income (labour vs capital) and by country of production; capital/intangibles capture a rising share.

| Key | Relevance |
|---|---|
| Timmeretal2013 | Introduces "GVC income" — income generated in a country by final demand for manufactures; our income framing descends from it. |
| Timmeretal2014 | Slicing value chains into labour/capital income by country; capital share rising. |
| TimmerMiroudotdeVries2019 | Functional specialisation — which stages a country's income comes from. |
| ChenLosTimmer2018 | Residual income to intangibles in GVCs; notes that intangible returns are booked where IP is *registered* — exactly the SPE issue in Cyprus. |

Gap: capital income is still assigned to the country of production, not to the owner's residence; the step "capital income → who receives it" is left out.

### S3. Firm heterogeneity and ownership inside GVC accounting (extended SUTs, AMNE)
What it establishes: splitting industries by foreign vs domestic ownership changes TiVA measures materially; foreign affiliates are more import- and export-intensive.

| Key | Relevance |
|---|---|
| Cadestinetal2018 | OECD AMNE: ICIO split by ownership — the closest existing object to our tensor, but stops at *value added by owner type*, not at *income by recipient country*. |
| MiroudotYe2020 | Multinational production in value-added terms; decomposes value added by ownership of the producing firm. |
| Fetzeretal2018; Chongetal2019; UN2023GVC | Extended supply–use tables by ownership/size (US BEA, CBS Netherlands, UN handbook) — the compilation template our Cyprus build follows. |
| Lipsey2010; CasellaBorgaWacker2023 | Ownership vs residence: location of production is ambiguous when intangibles and FDI dominate; FDI statistics are a poor proxy for multinational production. |

Gap: ownership splits identify *foreign-controlled value added* but not whether the associated income leaves (retained earnings, reinvestment, SPE pass-through), nor which country ultimately receives it.

### S4. Residence vs ownership in national accounts; GDP vs GNI (the residence layer)
What it establishes: GNI = GDP + net primary income; in MNE-heavy economies GDP overstates resident income, motivating modified measures (Ireland's GNI*).

| Key | Relevance |
|---|---|
| UN2009SNA; IMF2009BPM6; OECD2008BMD | Definitions of residence, primary income, reinvested earnings, direct-investment relationships and SPEs that our accounting identities must respect. |
| Rassier2017; Guvenenetal2022 | MNE profit shifting distorts GDP, BoP and productivity by location; Guvenen et al. reattribute US MNE profits by labour/sales — a formulary alternative to our ownership-based allocation. |
| FitzGerald2018; ESRG2016 | Ireland's GNI* — the leading official precedent for adjusting headline aggregates for MNE/redomiciled income; we generalise to a recipient-country decomposition. |
| PikettySaezZucman2018 | Distributional national accounts: allocate 100% of national income to recipients consistently with totals — our "adds-up-to-GDP" discipline is the cross-border analogue. |

Gap: GNI–GDP gaps are aggregate scalars; they do not say *which* sectors' value added leaks, *to whom*, or how much of it is pass-through.

### S5. External positions, phantom FDI, SPEs and profit shifting (the SPE adjustment)
What it establishes: a large share of FDI and FDI income is routed through conduits with no real activity; immediate-counterpart statistics misstate ultimate ownership.

| Key | Relevance |
|---|---|
| LaneMilesiFerretti2018 | External wealth database; baseline for IIP-consistent investment-income flows. |
| DamgaardElkjaer2017; DamgaardElkjaerJohannesen2024 | ~40% of global FDI is "phantom" (SPE) investment; ultimate-investor look-through — the method we apply to Cyprus's inward FDI income. |
| Casella2019; BolwijnCasellaRigo2018 | Probabilistic look-through of conduit FDI; FDI-based estimates of BEPS. |
| BlanchardAcalin2016 | Measured FDI flows through hubs are largely pass-through — motivates netting SPE flows. |
| SanchezMunozetal2022 | IMF SPE data template — the definitional boundary we adopt for separating SPE flows. |
| Zucman2013; Coppolaetal2021 | Tax havens distort bilateral external statistics; nationality-based (vs residence-based) restatement of positions — same logic applied here to income flows. |
| TorslovWierZucman2023; HinesRice1994; JanskyPalansky2019; HebousKlemmWu2021 | Profit shifting inflates haven GDP and BoP income; Tørsløv et al. estimate ~36% of MNE profits are shifted to havens, and Cyprus is on their haven list (as in Hines–Rice). Hebous et al. trace the BoP footprint. Check the exact Cyprus figures before quoting them. |

Gap: this literature corrects *positions* and *profits* but does not integrate the correction into an IO-based decomposition of value added by final recipient.

### S6. Corporate ownership networks and ultimate control
| Key | Relevance |
|---|---|
| Vitalietal2011 | Network control computation (integrated ownership) — algorithmic basis for UCI attribution through chains. |
| GarciaBernardoetal2017 | Classifies jurisdictions as conduits vs sinks; Cyprus is identified as a sink OFC — directly relevant to how we treat Cyprus-registered holding entities. |

### S7. Cyprus-specific evidence
| Key | Relevance |
|---|---|
| Ledyaevaetal2015; RepousisLoisKougioumtsidis2019 | Russian capital round-tripping via Cyprus — why Cyprus inward/outward FDI and FDI income are dominated by pass-through. |
| IMF2023CyprusSI; IMF2024Cyprus | IMF surveillance documents covering Cyprus's SPE-heavy external accounts, primary income balance and current account. |
| CBC2026External | Central Bank of Cyprus BoP/IIP/FDI releases (with and without SPEs) — primary data source for the residence layer. |

Honest note: peer-reviewed academic work on Cyprus value retention is thin. We could not machine-verify any *Cyprus Economic Policy Review* (UCY Economics Research Centre) article — the site returned HTTP 403 and Semantic Scholar was rate-limited (429) throughout. Add CEPR/CBC Working Paper items manually after checking them on the UCY site.

### S8. Platforms, intermediation and tourism leakage (adjacent)
| Key | Relevance |
|---|---|
| RochetTirole2003 | Two-sided platform pricing — why commissions are levied on the local supplier side. |
| Hunoldetal2020 | Booking/Expedia commissions and channel pricing for hotels — an empirical anchor for the size of the platform wedge on Cypriot accommodation. |
| UNCTAD2019DER | Value creation vs capture in the digital economy; platform rents accrue to platform-owning countries. |
| Sinclair1998 | Classic tourism "leakage" concept (imports, foreign ownership, repatriated profits) — the pre-GVC version of our question for a tourism economy. |

Gap: platform commissions are recorded as imports of services (or netted in margins) and are invisible in ownership-based measures; our tensor gives them a recipient country.

## 3. Gap statement

Much of this is known accounting.
The value-chain literature (S1–S2) attributes value added to the country of *production*; the ownership literature (S3) splits it by *type of owner* but stops before the income leaves; the national-accounts and external-sector literature (S4–S5) measures how much income *crosses the border* but only as aggregates, and conduit (SPE) flows contaminate those aggregates.
No existing framework produces, for a single economy, a **recipient-country × institutional-sector × producing-industry tensor** that (a) sums exactly to GDP, (b) is consistent with BPM6 primary-income flows and FATS/UCI ownership, (c) contains no double counting between the imported-input leakage and the foreign-capital-income leakage, and (d) removes SPE pass-through explicitly rather than implicitly.
The paper supplies that joined, auditable object and implements it first for Cyprus, where the SPE problem is most severe.
The contribution is integration and auditability — not a new estimator — and should be stated that way.

## 4. Draft Related Literature (LaTeX, ~700 words)

```latex
\section{Related Literature}
\label{sec:literature}

This paper joins three literatures that measure the same object---the destination of value added generated on a territory---from different sides, and that have so far been kept apart.

The first is the input--output literature on value added in trade.
Building on \citet{Leontief1936} and the domestic/imported coefficient split in \citet{MillerBlair2009}, \citet{HummelsIshiiYi2001} measure the import content of exports, \citet{JohnsonNoguera2012} define value-added exports, and \citet{KoopmanWangWei2014} and \citet{LosTimmerdeVries2016} decompose gross exports into value-added and double-counted terms.
\citet{LosTimmerdeVries2015} show that the foreign value-added share of final manufactures has risen almost everywhere.
Surveys by \citet{Johnson2018} and \citet{AntrasChor2022} make clear that these measures, and the databases that implement them \citep{Timmeretal2015,Yamanoetal2021,Eurostat2019FIGARO,Ahmadetal2017}, attribute value added to the country where production takes place.
We borrow their double-counting logic but ask a different question: not where value is \emph{produced}, but who \emph{receives} it.

The second literature slices value chains by factor income.
\citet{Timmeretal2013} introduce ``GVC income'', \citet{Timmeretal2014} show that the capital share of value-chain income has risen, and \citet{TimmerMiroudotdeVries2019} document functional specialisation across countries.
\citet{ChenLosTimmer2018} attribute a large and growing residual to intangible capital and note that its location is recorded where intellectual property is registered.
This is exactly the case in a holding-company jurisdiction such as Cyprus, and it motivates the step these papers leave out: allocating capital income to the residence of its owner.

A closely related strand splits input--output tables by firm ownership.
The OECD AMNE database \citep{Cadestinetal2018} and \citet{MiroudotYe2020} separate value added of foreign affiliates from that of domestic firms.
Extended supply--use tables for the United States \citep{Fetzeretal2018} and the Netherlands \citep{Chongetal2019}, codified in \citet{UN2023GVC}, provide the compilation template we follow.
\citet{Lipsey2010} and \citet{CasellaBorgaWacker2023} warn that when intangibles and conduit FDI dominate, neither location nor immediate ownership identifies where production income accrues.
The ownership-split tables stop at foreign-\emph{controlled} value added.
They do not ask how much of it leaves the country, as distributed or reinvested earnings, or whether it only passes through on its way to a third country.

The third literature works from the residence side.
The SNA, BPM6 and the FDI benchmark definition \citep{UN2009SNA,IMF2009BPM6,OECD2008BMD} define the primary-income flows that bridge GDP and GNI.
\citet{Rassier2017} and \citet{Guvenenetal2022} show that profit shifting by multinationals distorts output, BoP and productivity by location.
Ireland's modified GNI* \citep{ESRG2016,FitzGerald2018} is the leading official response, but it is a single adjusted aggregate.
It does not decompose the leakage by sector or by recipient.
Our requirement that every euro of GDP be allocated to exactly one recipient is the cross-border counterpart of the distributional national accounts of \citet{PikettySaezZucman2018}.

Measuring these flows correctly requires dealing with special-purpose entities.
Investment-income flows are the counterpart of external positions \citep{LaneMilesiFerretti2018}, and those positions are heavily distorted by conduits.
\citet{DamgaardElkjaer2017} and \citet{DamgaardElkjaerJohannesen2024} estimate that a large share of global FDI is ``phantom'' investment in shell entities, and \citet{Casella2019} proposes a probabilistic look-through to ultimate investors.
\citet{BlanchardAcalin2016} and \citet{BolwijnCasellaRigo2018} show that hub FDI is largely pass-through.
\citet{Zucman2013} and \citet{Coppolaetal2021} demonstrate that restating external positions from residence to nationality changes bilateral patterns substantially.
Cyprus appears on the haven lists used to estimate shifted profits \citep{HinesRice1994,TorslovWierZucman2023}.
Related work quantifies profit shifting from FDI returns \citep{JanskyPalansky2019} and traces its footprint in the balance of payments \citep{HebousKlemmWu2021}.
Network studies of corporate control \citep{Vitalietal2011} classify Cyprus as a sink offshore financial centre \citep{GarciaBernardoetal2017}.
Russian round-tripping through Cyprus is documented by \citet{Ledyaevaetal2015} and \citet{RepousisLoisKougioumtsidis2019}, and IMF surveillance repeatedly flags the SPE-driven volatility of Cyprus's external accounts \citep{IMF2023CyprusSI,IMF2024Cyprus}.
We adopt the IMF SPE boundary \citep{SanchezMunozetal2022} and the Central Bank of Cyprus's SPE-separated statistics \citep{CBC2026External}.
This lets us remove pass-through flows explicitly, rather than counting them either as domestic retention or as genuine foreign capture.

Finally, for a tourism-intensive economy, the older tourism-leakage literature \citep{Sinclair1998} and recent work on platform intermediation \citep{RochetTirole2003,Hunoldetal2020,UNCTAD2019DER} point to a further channel.
Commissions paid to foreign platforms are value generated by local suppliers and captured abroad.
The tensor gives them an explicit recipient.

Relative to these literatures, our contribution is integration rather than a new estimator.
We join the residence, ownership and value-chain layers into a single recipient-country by sector tensor.
The tensor adds up to GDP, is consistent with BPM6 primary income and FATS ownership, excludes double counting between imported-input leakage and foreign capital-income leakage, and is adjusted for SPEs.
Every cell is traceable to a published source.
```

## 5. Verification

- 56 entries. 52 have a Crossref DOI whose title, authors, year, venue, volume and pages were checked against the Crossref API. The 4 URL-only entries (Eurostat2019FIGARO, ESRG2016, BlanchardAcalin2016, CBC2026External) were checked as live institutional pages returning HTTP 200, with the page title matched for FIGARO and PIIE.
- `verify_bib.py`: 40 ok, 16 flagged. Every flag was reviewed and is benign:
  - subtitle truncated in Crossref (MillerBlair2009, Ahmadetal2017, UN2023GVC, SanchezMunozetal2022, UNCTAD2019DER, IMF Cyprus reports);
  - corporate or escaped author names (UN2009SNA, FitzGerald2018 is listed under the ESRI publisher, TorslovWierZucman2023's `{\o}`);
  - print year vs DOI-registration year (SNA 2008, BPM6, OECD BMD: conventional citation years kept);
  - URL-only entries that the script tries to match by title search (FIGARO, ESRG, PIIE, CBC).
- Author rosters for the OECD papers were checked through OpenAlex. This caught "Timon" (not "Tanja") Bohn in Ahmadetal2017.
- Page ranges are omitted for Lipsey2010 and Rassier2017 because neither Crossref nor OpenAlex records them.
- Semantic Scholar was rate-limited (HTTP 429) for the whole session, so all verification used Crossref and OpenAlex.
- Two items are still open. The skill's quality gate requires the user to confirm this map before the prose is final. No Cyprus Economic Policy Review or CBC working paper is included yet.
