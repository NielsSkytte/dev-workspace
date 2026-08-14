---
id: carlras-pin-rowcheck-replacement
ts: 2026-08-14T12:45:00Z
type: semantic
scope: project:customers/Carl-Ras/datahub
source: session:d96c18e1-0555-475f-a4be-0c76a71e9ca1
tags: [project, fabric, warehouse, performance, data-quality]
status: distilled
description: "Carl Ras AX09: a per-row row-count check nothing ever read cost 74% of enriched build time; replacing it with a post-load check took six failed git syncs and exposed three tables silently inflating their row counts"
---

Hand-written, not distilled. Sentinel returned 39 fidelity flags on `daily/2026-08-13.md` and
`daily/2026-08-14.md` and confirmed none of the key facts below appear in any assistant body, so
distillation would have produced nothing usable.

## What PIN_RowCheck was

Every `viewtransform` view in `Warehouse_Enriched_AX09` ended with:

```sql
PIN_RowCheck = IIF(COUNT(*) OVER() = (SELECT COUNT(*) FROM <source>), 'Success','Failure')
```

A grain guard — does one row in still equal one row out — stamped as a single word on **every
row** of 29 tables. Sound instinct: silent join fan-out is the nastiest bug in a medallion layer
because the data still looks plausible and every downstream total is quietly inflated.

Three things were wrong with it.

**Nobody read it.** Zero references in `Fabric-ETL`, `Landingzone-ETL` or `Semantic-Model` — no
Curated view, pipeline, sproc, notebook or semantic-model column. Written on 133M rows, consumed
by nothing.

**It was the wrong shape, and expensive.** `COUNT(*) OVER()` with no `PARTITION BY` is a blocking
operator: every row must be produced before any row can return. Beside it a scalar subquery re-ran
the base join. Two extra full passes per build, forever, to store one word.

**Some of the checks could not fail.** The expectation is hand-written per view. Where it is an
independent count of the source (`InventorySite` counts `inventsite`) it is a real check. Where it
mirrors the view's own joins including the row-multiplying ones — `ChartOfAccountToAlternative
ChartOfAccount`'s comment says *"range expansion - row-multiplying, mirrored"* — it compares the
view against a copy of itself and can only return Success.

## Measured, not assumed

2x2 factorial, 3 CTAS runs per cell, order rotated each round, all four cells in one session:

| joins | check | mean |
|---|---|---|
| original | yes | 404.8s |
| original | **no** | 208.7s |
| rewritten | yes | 311.9s |
| rewritten | **no** | 157.7s |

**2.57x overall. Dropping the check is 74% of it; join rewrites 16%.** Ranges did not overlap.
Variance also collapsed — baseline spread 137s (34% of mean) against 15.6s (10%), which matters
more than the mean for a chain that must finish before a model refresh.

Equivalence proven twice on **230 columns x 12,300,942 rows** (`EXCEPT` both directions, zero rows
each way), and verdicts agree on **28 of 28** tables from a same-moment build.

## The replacement

`rowcheck.<T>` view (expectation lifted verbatim per table) + `transform.sp_RowCheck` +
`transform.RowCheckLog` + a `ForEach RowCheck` stage discovering work via `INFORMATION_SCHEMA`
exactly like the existing loop. Shipped `5ce780f`. The whole check runs in **~1 minute across 28
tables**. Logs rather than throws; the `THROW` block is in the sproc header.

## What it immediately caught

Three tables **over**-produce against their own declared expectation — join fan-out, not loss:

| table | excess |
|---|---|
| `SalesLineTransactions` | +45,735 |
| `SalesInvoiceTransactions` | +64,814 |
| `GeneralLedgerTransactions` | **+4 in 113M** |

Failing since at least 2026-08-07 with nobody told. `GeneralLedgerTransactions` holding at exactly
+4 across two independent runs points at four specific rows, not proportional fan-out. Lead:
`crreportinggroups` is joined in `SalesInvoiceTransactions` **without** a `SCDcurrent` filter while
the same join in `SalesLineTransactions` has one. Task
`2026-08-14-carlras-enriched-rowcount-failures`.

## Cost of getting it deployed

Six failed "Update from git" over two days. See `fabric-warehouse-git` skill — the durable lesson
is that removing a column needs **three** files, not two: the view, the table DDL, and `xmla.json`.

Real casualty: **`enriched.DeliveryAddress` lost 1,851,644 rows permanently.** It has no
`viewtransform` view so nothing rebuilds it. Nothing downstream reads it (Curated's
`dim.DeliveryAddress` reads `enriched.PackingSlips`), so no impact — but it is the one table where
"data will be deleted" meant gone. Everything else in enriched/curated is derived and was rebuilt.

## Rule earned

A validation result that is written and never read is not a check, it is a cost. Put the verdict
somewhere queryable, give it a magnitude rather than a boolean, and compute it once against the
built table instead of inside the query that builds it.

Related: [[carlras-viewtransform-workspace-drift]]
