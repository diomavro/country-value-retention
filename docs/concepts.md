# Who captures the value created in a country? — the concepts, step by step

This guide explains every idea the project uses, in plain language first and
with a small worked example, before any formula.  All numbers in this file are
**illustrative** (made up to be easy to follow); they never enter the results.

---

## 1. Revenue is not value

When you pay a delivery platform €20, it is tempting to say "€20 left Cyprus"
if the platform is foreign.  That is wrong, for the same reason a bakery's
€100 of bread sales is not €100 of the baker's income: most of the €100 paid
for flour, electricity and rent — things *other* people produced.

The value a firm **adds** is what is left after paying for the goods and
services it used up:

> **value added = revenue − intermediate inputs**

Adding up value added across every firm gives GDP.  Revenue double-counts
(the flour is counted in the miller's sales *and* again in the baker's);
value added does not.  This is why the project works in value added, never
revenue.

*Example.* A bakery sells €100 of bread, buys €40 of flour and €10 of
electricity.  Value added = €50.  If the flour was imported, €40 of the €100
paid for something produced abroad — but that €40 is the **foreign miller's**
value added (plus whatever *they* bought), not "leakage of the bakery".

## 2. Where does value added go? Three kinds of income

A firm's value added is used to pay three groups:

| Component | National-accounts code | Who receives it |
|---|---|---|
| Compensation of employees | D1 | the workers |
| Taxes on production (net of subsidies) | D29−D39 | the government |
| Gross operating surplus | B2G | the owners and lenders (profits, interest, rent, depreciation) |

So in the bakery's €50: perhaps €30 wages, €2 taxes, €18 operating surplus.

## 3. Residence, not nationality

"Foreign" in this project means **not resident in the country**, the rule
used by the national accounts and the balance of payments.  A Greek
citizen who lives and works in Nicosia is a resident of Cyprus; their wage stays
in Cyprus's economy.  A worker who lives in Greece and flies in for a
three-month job is a non-resident; their wage is a payment abroad.  The
project never uses citizenship or country of birth as a stand-in for residence.

## 4. Ownership moves only the owners' share of profit

If an American company owns a Cypriot hotel outright, what flows to the
United States? Not the room revenue, not the wages of the Cypriot staff, and
not the taxes paid in Limassol: those stay. What accrues to the US owner is the
**profit**, and only in proportion to its ownership share.

Profit here means what is left of operating surplus after three deductions:
**depreciation** (the wear and tear of buildings and machines, which has to be
replaced), **interest** (which belongs to whoever lent the money), and
**Cypriot corporate tax**, in that order. Then comes the owner's share.
The methodology uses one number, θ, for every foreign-controlled firm: the
share of its equity held by non-residents. For Cyprus it is calibrated on the
filings of large firms, so it is an estimate, not a measurement; for other
countries the Cyprus value is simply assumed.

*Example.* The bakery's operating surplus is €18. Depreciation is €5 and
interest to a Cypriot bank is €3, leaving a profit before tax of €10. After
12.5% Cypriot corporate tax, €8.75 is left. A foreign owner with 60% of the
shares has a claim on €5.25 of the €50 of value added. The other €44.75 stays:
wages, taxes, the bank's interest, and the local shareholders' 40%.

**Lenders are a separate channel.** If the bakery had borrowed from a German
bank, its €3 of interest would accrue to Germany. It would be counted once, as
interest, and never again inside the owner's profit.

**"Accrues" is not "is paid".** If the US owner leaves its €5.25 in the Cypriot
firm to build a new oven, the profit has still accrued to the US owner: it owns
it. Official statistics treat this the same way, recording it as *reinvested
earnings*. So the numbers in this project measure who has a claim on the
value, not how much cash crossed the border this year.

**Workers are treated like owners.** A non-resident worker's pay includes the
employer's social-security contributions, which go to the Cypriot social
insurance fund. That part stays in Cyprus, just as the corporate tax on a
foreign owner's profit does.

The code enforces the income boundaries. Profit, dividends and interest paid
abroad by firms and households can only come out of operating surplus, and pay
to non-resident workers only out of compensation. Only two foreign claims are
charged to taxes: taxes the EU collects directly, and interest the government
pays abroad (by convention, since taxes finance it). No domestic tax is ever
counted as foreign in its own right.

## 5. Following ownership to the end of the chain

Company ownership is often layered: a Cypriot subsidiary is owned by a Dutch
holding company, which is owned by a US parent, which is owned by thousands
of shareholders.  Stopping at the first foreign company would say "the
Netherlands" when the value really belongs to US shareholders.  The project
represents ownership as a directed graph and follows it recursively to the
ultimate owners.  Where the records run out, the remaining share is labelled
**unresolved**, never assigned a guessed country.

*Cross-holdings.* If firm A owns 20% of B and B owns 20% of A, simply
following arrows would loop forever.  The standard fix (the same algebra as
the Leontief inverse below) adds up all the paths once each, so every euro of
ownership is assigned exactly once.

## 6. Imported inputs, and the chain behind the chain

A Cypriot restaurant imports olive oil directly — that is a **direct**
foreign input.  It also buys bread from a Cypriot bakery that imports flour —
that flour is an **indirect** foreign input.  To catch the indirect part we
need the whole web of who buys from whom: the **input-output table**.

The input-output table records, for each industry, how much it buys from every
other industry, from abroad, and how much value it adds.  Dividing by output
gives the *recipe*: for every €1 of output, industry *k* uses €a from
industry *i*.  Following the recipe back through suppliers of suppliers of
suppliers gives the **Leontief inverse**, L = (I − A)⁻¹.  Its intuition:
producing €1 of restaurant meals needs some bread, which needs some flour,
which needs some transport, and so on; L adds up that infinite chain in one
step.

The key identity: every €1 of final spending on domestic output ends up as
exactly one of three things —

> **domestic value added + imported inputs + taxes on products = €1**

The code checks this for every industry and every year.  It is why imports
and value added can never be double-counted: they are two slices of the same
euro.

## 7. Two questions, two frames

**Frame A — "Of the value created in Cyprus this year, who receives it?"**
Start from GDP (all value added in Cyprus).  Subtract income paid to
non-residents: wages of non-resident workers, profits, dividends and interest
paid to foreign owners and lenders, and taxes paid to EU institutions.  What
remains is **retained**.

> Domestic Value Retention (DVR) = retained ÷ GDP;  Foreign Value Leakage = 1 − DVR.

"Retained" is whatever is left after the outflows we can measure. Any outflow
the statistics miss (for example, rent earned by foreign owners of holiday homes)
therefore shows up as retained. DVR is best read as an **upper bound**.

**Frame B — "Of €1 spent on a Cypriot product, where does it end up?"**
Use the input-output model to split the euro into Cypriot value added (in
every industry along the supply chain), imported inputs, and taxes.  Then
send the Cypriot value added through Frame A's recipient shares, and the
imported inputs to the countries they came from.  This answers the €20
platform question.

## 8. Why GNI is not the answer (and why Cyprus is special)

Gross National Income (GNI) = GDP + primary income received from abroad −
primary income paid abroad (wages, profits, interest and dividends, plus taxes
paid to and subsidies received from EU institutions).  It is tempting to call GDP − GNI "leakage".  Two problems:

1. GNI *adds* income Cypriot residents earn abroad.  That is value generated
   elsewhere, not in Cyprus.  Our question is about value generated in Cyprus,
   so we use only the outflows.
2. Cyprus hosts many **special purpose entities** (SPEs): holding
   companies with few or no employees that receive dividends from abroad and pay
   them on to foreign owners.  Those payments are recorded as primary income paid
   by Cyprus but were never generated by Cypriot production — the money merely
   passes through.  Counting them would make Cyprus's "leakage" enormous and
   meaningless.  The primary series therefore **leaves out the income paid by
   financial companies other than banks**, the sector where Cyprus's SPEs are
   recorded.  This also drops some insurers and funds that are not SPEs, and
   misses the few SPEs recorded elsewhere.  The unadjusted official outflow is
   shown alongside for comparison.

**Netting hides the outflow.** Because GNI subtracts payments from receipts, a
country whose residents earn a lot abroad can show no gap at all while a large
part of its own output goes to non-residents.  In 2023 the Netherlands' GNI was
€1,054.5bn, slightly *above* its GDP of €1,050.1bn, yet 7.2% of Dutch GDP accrued
to non-residents as profit, dividends, interest, pay and EU taxes.  Dutch
residents received about as much from abroad (39% of GDP) as the Netherlands
officially paid out (39%), so the two cancel in GNI.  GDP − GNI answers "is the country a net payer
of income?", not "who receives the value produced here?".

**One number cannot say where the value goes.** This system splits the outflow
by mechanism (foreign-owned profit, intra-group interest, other interest and
investment income, portfolio income, interest on public debt, pay to
non-resident workers, taxes to EU institutions), by industry and, where the
statistics name one, by recipient country (for Cyprus in 2023 about 46% of the
outflow cannot be assigned to any recipient, and another 11% goes to "offshore
financial centres", a group of territories rather than one country).  Profit, dividends and interest
that firms pay abroad are capped at the gross operating surplus of the industry
they are charged to: all foreign claims on an industry together cannot exceed
that industry's surplus.  Interest on public debt is charged to taxes instead,
by convention.  Each row also
says where the number comes from and whether it was observed or estimated.

**What the difference looks like (2023, central estimates; `src/cvr/compare.py`).**

| | GDP − GNI, % of GDP | Official income paid abroad, % of GDP | Value produced that accrues to non-residents (this system), % of GDP |
|---|---:|---:|---:|
| Cyprus | 10.5 | 108 | 7.1 |
| Netherlands | −0.4 | 39 | 7.2 |
| Ireland | 25.5 | 74 | 28.3 |
| Luxembourg | 32.2 | 443 | 26.0 |

Official payments above 100% of GDP are mostly money passing through holding
companies and funds, not income earned from local production.  Cyprus and the
Netherlands look very different on both official measures, but about the same
share of what they produce accrues to non-residents.  In Luxembourg the
largest single line, 17.5% of GDP, is pay to cross-border commuters: they live
in France, Belgium and Germany, so they are non-residents (section 3), whatever
their nationality.  Outside Cyprus the figures use Cyprus's θ (section 4), which may be too high
or too low for another country.  Separately, Luxembourg keeps confidential
much of the interest and dividends paid abroad by its firms, households, banks
and government; these are left out, so its figure is too low on that count.

## 9. The headline measures, and why they are never added up

| Measure | Question it answers |
|---|---|
| Domestic Value Retention | Share of GDP whose income stays with residents |
| Foreign Value Leakage | 1 − DVR |
| Foreign Input Exposure | Share of intermediate inputs that are imported (direct and total) |
| Foreign Ownership Capture | Share of the operating surplus of Cypriot non-financial companies generated in foreign-controlled firms, weighted by the foreign owners' equity share (before interest and tax) |
| Foreign Labour Income | Share of compensation paid to non-resident workers (after Cypriot employer contributions) |
| Primary-income outflow ÷ GDP | The official, unadjusted balance-of-payments figure (includes pass-through) |

These describe different mechanisms measured on different bases (GDP,
intermediate inputs, operating surplus, wages).  Adding them would mix
denominators and double-count — e.g. imported inputs are *not part of* GDP at
all, so "leakage through imports" plus "leakage through profits" is not a
share of anything.

## 10. How sure are we? Status and confidence

Every number carries a **status**:

- **observed** — printed by an official source (only units/labels changed);
- **modelled** — computed deterministically from observed inputs (e.g. through L);
- **estimated** — needed an allocation key or assumption, written down next to it;
- **illustrative** — a teaching example; never part of the results.

…and a **confidence** (high / medium / low).  Where an assumption drives a
result (for example, what share of a sector's profits goes abroad), the result
is shown across a range of values rather than as a single falsely precise
number.
