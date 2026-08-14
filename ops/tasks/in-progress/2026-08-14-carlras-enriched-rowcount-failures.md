---
title: Carl Ras — three enriched tables inflate their row count, and audit which row-checks can actually fail
status: in-progress
created: 2026-08-14
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by:
activity: AX09Import
fno_task:
source: direct
---

## What

Two related pieces of work, both surfaced by replacing `PIN_RowCheck` with the post-load
check (commit `5ce780f`, DEV run 2026-08-13).

### 1. Three enriched tables produce more rows than their source says they should

Measured twice by independent paths — a same-moment build before deployment, and the first
real `transform.RowCheckLog` population after it — with identical numbers both times:

| table | actual | expected | excess |
|---|---|---|---|
| `GeneralLedgerTransactions` | 113,276,717 | 113,276,713 | **+4** |
| `SalesInvoiceTransactions` | 12,300,942 | 12,236,327 | **+64,615** |
| `SalesLineTransactions` | 5,849,022 | 5,812,056 | **+36,966** |

All three **over**-produce. That is the signature of a join matching more rows than it
should, not of rows going missing. Every total built on these tables is inflated by the
same factor.

These are not new. They were failing under the old `PIN_RowCheck` too — `SalesInvoiceTransactions`
and `SalesLineTransactions` have carried a `Failure` since at least the 2026-08-07 build.
Nothing read the column, so nobody was told.

**Lead to start with:** `crreportinggroups` is joined in `viewtransform.SalesInvoiceTransactions`
**without** a `SCDcurrent` filter, while the same join in `SalesLineTransactions` **has** one.
If that table carries SCD history, every matching row fans out. Verify before assuming — it is
one hypothesis, not a diagnosis.

`GeneralLedgerTransactions` at +4 rows in 113 million should be the easiest to pin down: a
`GROUP BY` on the primary key with `HAVING COUNT(*) > 1` isolates exactly four rows, and
whatever they have in common names the faulty join.

### 2. Audit which expectation queries can actually fail

The expectation is hand-written per view and lifted verbatim into `rowcheck.<Table>`. Two
kinds exist, and only one is a real check:

- **Independent** — e.g. `rowcheck.InventorySite` counts `inventsite` directly. A fan-out in
  the view changes the actual and not the expected, so it is caught. Genuine.
- **Mirrored** — `rowcheck.ChartOfAccountToAlternativeChartOfAccount` reproduces the view's own
  joins including the row-multiplying range expansion. The code comment says so outright:
  *"range expansion — row-multiplying, mirrored"*. It compares the view against a copy of
  itself and can only ever return `Success`.

25 of 28 tables currently report `Success`. Until each expectation is classified, that green
light is not evidence. Go through all 28, label each independent or mirrored, and rewrite the
mirrored ones against the primary source table.

## Why

The row-count check exists to catch silent join fan-out — the failure mode where data still
looks plausible and every figure downstream is quietly wrong. It has been correctly detecting
three real cases and reporting them to nobody.

Now that the verdict lands in `transform.RowCheckLog` and is queryable, the finding is
actionable. Fixing the three tables is the point of having built the check. Auditing the
expectations decides how much the 25 passes are worth.

## How to see it

```sql
SELECT TableName, ActualRowCount, ExpectedRowCount, Difference, Status, CheckedAtUtc
FROM transform.RowCheckLog
WHERE Status = 'Failure'
ORDER BY CheckedAtUtc DESC;
```

## Notes

- `enriched.DeliveryAddress` is a separate loose end: 8 columns, **no** `viewtransform` view,
  no consumer, and it was the fourth table carrying a `Failure`. Its 1,851,644 rows dated
  2026-05-25 were lost when the deployment recreated the table empty, and nothing rebuilds it.
  Nothing downstream reads it — Curated's `dim.DeliveryAddress` reads `enriched.PackingSlips`.
  Decide whether to delete it or give it a view.
- Once a table is fixed, `sp_RowCheck` can be made blocking rather than logging — the `THROW`
  block is in the procedure header. Do not switch it on before the three are green.
- Deploying this change to TEST/PROD needs `tools/predeploy_enriched_ax09.sql` run first,
  otherwise DacFx rebuilds every affected table and empties it.

## Diagnosis (2026-08-14, measured against DEV)

Queried with `tools/wh_query.py` (pyodbc + AAD token, read-only). Numbers are from the
DEV build of 2026-08-14 10:17, so they differ slightly from the ones captured above.

**`SalesInvoiceTransactions` — surplus 64,814, attributed in full.** Modelling each base row's
multiplicity as `n_InventTrans_Purchace × n_crreportinggroups` predicts **12,340,951**, which is
the actual row count to the row.

| source | surplus rows |
|---|---|
| `InventTrans_Purchace` join | 63,890 |
| `crreportinggroups` missing `SCDcurrent` | 924 |

1. **`InventTrans_Purchace` (view line 553-556) is the main cause.** It LEFT JOINs `inventtrans`
   on `INVENTTRANSID` + `DATAAREAID`, and `INVENTTRANSID` is **not unique** in `inventtrans` —
   7,214,332 ids carry more than one current row, up to 352. 39,014 base rows fan out. The join's
   only consumer is `VendTable_CustVendAccount` via `CUSTVENDAC`. Among the multi-row ids only
   **577 disagree on `CUSTVENDAC`** and **1 on `TRANSTYPE`**, so collapsing to one row changes the
   vendor for a negligible set.
2. **`crreportinggroups` (view line 731-734) has no `SCDcurrent` filter.** The table holds 85 rows
   / 73 current; 12 reporting groups (`cr`, ids 11-67) carry a second SCD row.
   `SalesLineTransactions` and `SalesChannel` both filter it — the invoice view is the outlier.

Ruled out by measurement, all unique on their join keys: `unit`, `inventtable`,
`inventtablemodule`, `unitconvert` (incl. the generic `''`/`'0'` collision), `crenumvalues`,
`dlvmode`, `sqldictionary`, `crdimensions`, `dimensions`. `custinvoicetrans.RECID` is unique.

**`SalesLineTransactions` — surplus 45,735, 37,191 attributed (81%).** Same `InventTrans_Purchace`
join (view line 512-516). **8,544 rows remain unattributed** — not yet diagnosed.
`InventTrans_EstimatedCostPrice` is a `GROUP BY` subquery and cannot fan out.

**`GeneralLedgerTransactions` (+4)** — not started.

## Implications

- The duplicates are **exact copies**: 0 duplicate groups differ in `LineAmountMST` or `Quantity`.
  So every additive measure is multiplied, not perturbed.
- **Nothing downstream removes them.** `viewfacttransform.SalesTransactions` is a `UNION ALL` with
  a 3-year `FinancialDate` filter and no `DISTINCT`; the enriched window holds 6,849,300 rows and
  `fact.SalesTransactions` holds exactly 6,849,300 for that entity — 1:1.
- **The semantic model does not compensate.** The `Sales Transactions` partition is a plain import
  of `fact.SalesTransactions`, and `Sales | Amount | Std` = `SUM('Sales Transactions'[Line Amount
  Mst])`. `DISTINCTCOUNT` measures (`Sales | Order Count | Std`,
  `Customer | Count | With Sales | Std`) are immune.
- **Overstatement of invoiced revenue:** 99,872,381.32 of 3,723,381,006.87 inside the curated
  3-year window (**2.68%**); 214,947,102.40 of 6,597,816,949.21 across the whole enriched table
  (**3.26%**).
- Both fixes land in files carrying the `Auto Generated (Do not modify)` header — same generator
  ownership problem as the contact-link extension (next action 20).
- Side observation: `fact.SalesTransactions` now reaches `FinancialDate` **2026-08-13** for both
  entities. The "curated invoice facts are ~7 weeks behind" thread in `CONTEXT.md` is stale.

## Log
2026-08-14 — created after the DEV deployment of `5ce780f` and the first `RowCheckLog` run.
2026-08-14 — started (session task)
2026-08-14 — diagnosed SalesInvoiceTransactions in full and SalesLineTransactions to 81%;
             measured the downstream impact. Fix not yet authored.
