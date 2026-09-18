---
id: carlras-customer-insights-poc
ts: 2026-09-18T07:10:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:session_01P1qZjJ14dHz6gjhBLtip8t
tags: [project, customer-insights, cdp, segmentation, fabric, lakehouse, shortcuts, marketo]
status: distilled
description: "Customer Insights - Data proved on Carl Ras TEST data: curated fact.SalesTransactions has no primary key so the activity is built from enriched invoice journals; the OneLake connector cannot read views; dim.Customer is 73 % closed accounts, which is what broke the measure-based suggestions until the population was cut to 24,173 business customers"
---

Built 2026-09-16/18 in a Customer Insights trial on `Fabric-ETL-TEST` data, billed to `CarlRData-557`
(the app delivery). Full setup and rebuild instructions: `datahub/design/CUSTOMER_INSIGHTS_SETUP.md`;
customer note: `datahub/design/CUSTOMER_INSIGHTS_POC_NOTE.md`. Nothing in a repo by choice.

- **Curated cannot carry an activity.** `fact.SalesTransactions` has no key column and no `RecId`
  (`Fabric-ETL` `01 - Curated/.../fact/Tables/SalesTransactions.sql`), and its view is a `UNION ALL`
  of invoice lines and open order lines at two different grains. The activity was built from
  `enriched.SalesInvoiceTransactions` instead, one row per invoice journal, key
  `UPPER(PIN_DataAreaId)|RecId_CustInvoiceJour`. Verified unique in DEV (4,396,186) and TEST
  (4,458,613), 0 invoices lost to the `dim.Customer` join, 3 enriched lines carry no journal.
  `InvoiceId` alone would not do: 2 ids occur on more than one journal inside the same company.
- **The OneLake connector reads managed Delta tables only** (MS Learn, *Connect to Microsoft Fabric
  OneLake*): a lakehouse SQL-endpoint view is invisible to it, warehouse tables are unsupported. A
  view therefore has to go in through the Power Query **SQL Server database** connector, which copies
  the data and reloads it in full on every refresh. Microsoft advises against that path for Fabric.
- **A lakehouse SQL endpoint cannot resolve three-part names across workspaces** (`Invalid object
  name`). OneLake shortcuts to the two warehouse tables fix it; the view then reads `dbo.<table>`.
- **`dim.Customer` is mostly dead accounts**: of ~240,400 rows, 132,258 are group 996 *Midlertidig
  lukket* and 42,348 are 999 *Lukket / Udgaaet* (73 % together), plus 33,372 Web and 4,676 Kontant
  salg. Only 41,953 have an invoice in the last 12 months. That is what made the suggestions refuse
  to run ("more than 80 percent missing values"); CVR fields are filled for ~40 % of all customers
  but ~90 % of the business population.
- **Population used:** business accounts with a purchase in the last 36 months, 24,173 customers
  (exclude groups 996, 999, 997, 998, 902, 901, 989, 904, 979, 978). Swapping it in without being
  able to edit the locked unify source worked by adding `CI_Customer` as a second source and turning
  off "include all records" on the old table.
- **Suggestion outcome.** Activity-based (RFM) works and produced 27 groups, but only over a bounded
  period: over "all time" the data starts in 2002 and the numbers are meaningless. Measure-based
  produced nothing on any configuration; after the population fix the warning changed from missing
  values to "not able to find meaningful segments" from customer group, segment, business area,
  business type and employee interval. Influencing attributes are capped at 100 categories, which
  silently rules out `SubSegmentName` (756) and `CVRIndustry` (1,156).
- **Manual rules on own measures gave the answer instead.** Thresholds measured on the business
  population, 12 months (20,339 customers): median revenue 6,623 DKK, p80 31,658, p90 74,563,
  p95 172,859; median 7 invoices, p90 58. Segments: Noeglekunder (>75,000), Vaekstpotentiale
  (30,000-75,000), Hyppige koebere (>58 invoices), SleepingCustomers (bought within 36 months, not
  within 12) = 3,753 customers, which matched the warehouse prediction of ~3,800.
- **Two setup traps.** The suggestion wizard's Timestamp/Value dropdowns stay empty unless the
  activity itself carries the SalesOrder field mapping (Sales order ID / Order date / Sales amount);
  they then list the semantic names `OrderDate` and `SalesAmount`, not the column names. And measure
  Rules (null -> 0) do not reach customers with no activity rows at all, because the measure never
  produces a row for them.
- **Marketo:** the product that would replace Marketo is Customer Insights - **Journeys** (email,
  SMS, push, forms, events, lead scoring, journeys; interaction data flows back into - Data when
  both run in the same environment). - Data, what was tested, never sends anything. Niels: Journeys
  is a later decision, taken with Impact.
