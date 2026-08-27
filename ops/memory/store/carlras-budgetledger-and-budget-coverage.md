---
id: carlras-budgetledger-and-budget-coverage
ts: 2026-08-27T10:10:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:50082637-f235-4ee7-be0d-fd881b292a68
tags: [project, ax09, curated, finance, data-quality]
status: distilled
description: "Carl Ras BudgetLedger: model '2010' is the live budget, customer-confirmed - and the budget covers only 111 of the 230 operating accounts that actually post, which is what every budget-vs-actual gap is made of"
---

Hand-written from the session. Detail in `design/ATOMIC_GENERATOR_CHANGES.md` > GEN-011.

## The entity

`ledgerbudget` -> `enriched.BudgetLedger` (all 21 models, 1,596,773 rows) ->
`fact.BudgetLedger` (model `2010` only, 842,590 rows). Live in DEV and TEST, identical.

## Which model is live

**Confirmed by the customer**: a Carl Ras employee's own reporting query filters
`MODELNUM = N'2010'` and `DATAAREAID = N'CR'`; our fact reproduces it exactly (account `01021`
Varesalg, 2026: 10,542 rows, -1,146,443,286.98, 40 departments).

Supporting evidence, in order of trust: `MODIFIEDDATETIME` shows `2010` written every year for
seventeen years, each year touching that year and the next, last write the most recent of all 21
models by seven weeks; `budgetmodel.TXT` names it *"Budget master"*. `BLOCKED` is `0` on all 29
models and `REVISIONDATE` is `1900-01-01` everywhere - neither discriminates.

**Do not derive the model from recency.** "Most recently modified" would have picked `0-PKT`
(335 rows, last budget period 2012) for six weeks in early 2026.

## The finding to take to Finance

For 2025 operating accounts: **111 carry a budget, 230 carry actuals, 122 post real amounts and
were never budgeted.** That, not overspend, is what the budget-vs-actual gap is made of in every
year. It is a fact about the source data, not about the build - but anyone opening a budget report
will read the bars as variance.
