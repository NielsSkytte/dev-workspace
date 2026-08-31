---
title: Carl Ras — AX09 data correctness (enriched row-count fan-outs, row-check audit, raw SCD key map)
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

Three related pieces of work. Parts 1 and 2 were surfaced by replacing `PIN_RowCheck` with the
post-load check (commit `5ce780f`, DEV run 2026-08-13); part 3 is the raw-layer cause found while
diagnosing part 1, merged back in on 2026-08-17.

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

### 3. Raw AX09 keeps two SCDcurrent rows per key on `sqldictionary` (bad key map)

*(merged 2026-08-17 from `2026-08-14-carlras-raw-scd-key-sqldictionary`)*

`Lakehouse_Raw_AX09.sqldictionary` holds **more than one row flagged `SCDcurrent = 'true'` for the
same business key**. Measured 2026-08-14: **549 `(TABLEID, FIELDID)` keys across 1,427 rows.**

**Cause.** `Lakehouse_Util.rawtablekeymap_ax09` keys this table on `RECID` alone:

| COLUMN | SCDType | TABLE |
|---|---|---|
| `RECID,DATAAREAID` | 2 | DEFAULT |
| `Dataareaid,Itemid,Inventlocationid` | 2 | Inventsumdim |
| `RECID` | 2 | DATAAREA |
| **`RECID`** | 2 | **SQLDICTIONARY** |

`RECID` is not the business key of `sqldictionary` — `(TABLEID, FIELDID)` is. When AX re-creates a
dictionary entry it gets a **new `RECID`**, so the SCD2 load sees a brand-new record rather than an
update to an existing one, and never closes the old row. Both stay current, forever.

Concrete: `SALESLINE`, `FIELDID` 0, `TABLEID` 359 — two rows, `RECID` 5637429721 (effective
2026-04-21) and 5637466263 (effective **2026-08-14 07:09:33**). `CRREPORTINGGROUPS` has been in the
same state since 2026-05-07.

**Why it matters.** Every enriched view that joins `sqldictionary` for `PIN_PrimaryTable` /
`PIN_PrimaryTableId` gets one output row per duplicate. It already caused a real defect: it doubled
**8,544 rows** in `enriched.SalesLineTransactions` — every line with no `inventtrans` match — which
is the entire unexplained remainder of that table's row-count failure. That symptom is patched
defensively in the view (GEN-005, `Fabric-ETL` `3a72fca`), **but the raw data is still wrong** and
anything else joining `sqldictionary` inherits it. It is also growing: a new duplicate appeared the
morning of 2026-08-14.

**Latent, not yet firing:** `viewtransform.SalesInvoiceTransactions` has the same unguarded
dictionary join, resolving to `custinvoicetrans` / `inventtrans`. Both have exactly one current row
today so that view is correct — it doubles the day AX re-creates either entry.

**To do**

1. **Re-key `SQLDICTIONARY` to `TABLEID,FIELDID`** in `NB_Table_PrimaryKeyMap_AX09` (the notebook
   that populates `rawtablekeymap_ax09`; `PL_IaC_PopulateLakehouseUtil` runs it). Ship it in git,
   then re-seed each environment.
2. **Repair the existing raw rows** — the key-map change fixes future loads, not the 549 keys
   already duplicated. Needs a re-ingest or a targeted close-out of the superseded rows.
3. **Audit every other table for the same class of error.** `DATAAREA` also keys on bare `RECID`,
   and the `DEFAULT` is `RECID,DATAAREAID`. The general test: for each raw table, does any business
   key carry more than one `SCDcurrent = 'true'` row? Anything that answers yes is silently
   fanning out every view that joins it.
4. Once raw is clean, decide whether GEN-005's defensive `TOP (1)` stays or is reverted.

**How to see it**

```sql
SELECT TABLEID, FIELDID, COUNT(*) AS current_rows
FROM [Lakehouse_Raw_AX09].[dbo].[sqldictionary]
WHERE SCDcurrent = 'true'
GROUP BY TABLEID, FIELDID
HAVING COUNT(*) > 1;
```

Run it with `tools/wh_query.py` against `Warehouse_Enriched_AX09` (cross-database) — the
`Lakehouse_Raw_AX09` SQL endpoint still cannot serve data itself.

This is **not** an Atomic generator issue. The generated view is reasonable; the raw layer is
breaking the one-current-row-per-key contract the view assumes. Do not hand it to Simon.
Full write-up: `design/ATOMIC_GENERATOR_CHANGES.md` > GEN-005.

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

**`SalesLineTransactions` — surplus 45,735, attributed in full.** No `RecId` column varies here
either; the duplicate rows are byte-identical across all 226 columns.

| source | surplus rows |
|---|---|
| `InventTrans_Purchace` (view line 512-516) | 37,191 |
| `sqldictionary` (view line ~801) | 8,544 |

`sqldictionary` holds **two `SCDcurrent` rows for `SALESLINE`** (`TABLEID` 359), so the lookup
returned two rows and doubled every line with no `inventtrans` match — exactly the 8,544 base rows
in that state. **Raw-layer defect, not a view defect:** `rawtablekeymap_ax09` keys `SQLDICTIONARY`
on `RECID` alone. Split out as `2026-08-14-carlras-raw-scd-key-sqldictionary`.

**CORRECTION — `inventsumdim` was never a cause.** An earlier revision of this file attributed
2,705 rows to it and left 5,819 unexplained. Both numbers were wrong: the probe grouped with
`UPPER()` while the join compares raw under the warehouse's case-sensitive `BIN2` collation.
Grouped as the join actually compares, `inventsumdim` has zero duplicated keys and cannot fan out.

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
2026-08-31 — **VERIFIED; the "CLOSED" claim on `SalesInvoiceTransactions` no longer holds, and TEST
             carries five failures this task has never mentioned.**
             - **Count correction: there are 29 rowcheck expectations, not 28.** Every "28" / "25 of
               28" / "27 of 28" in this file is off by one; 29 `rowcheck/Views/*.sql` files exist and
               match the live log.
             - **DEV, last full run 2026-08-20 13:44 (11 days stale), 27/29 pass:**
               `GeneralLedgerTransactions` +4 (unchanged, view untouched, still not started) and
               **`SalesInvoiceTransactions` -1,871 — a FAILURE, four days after the 08-16 "green,
               12,276,137" reading.** It has flipped from overcount to undercount. The view has not
               changed since `0a7f826`, so if real this is data-driven, not a code regression. DEV
               needs a fresh row check before this table can be re-closed.
             - **TEST, run today 08:43-08:44, 23/29 pass — six failures:**
               `GeneralLedgerTransactions` **+58** (stable every run since 08-19, a different figure
               from DEV's +4 and never recorded), plus `CustomerAccounts` -253, `Items` -312,
               `OutputOrders` -14,684, `PickingRoutes` -12,849, `SalesChannel` -2. None of the five
               appear anywhere in this task. `SalesInvoiceTransactions` and `SalesLineTransactions`
               are both green in TEST.
             - **Part 3 unchanged and unshipped.** `rawtablekeymap_ax09` still keys `SQLDICTIONARY`
               and `DATAAREA` on bare `RECID`, in the repo and in both environments —
               `NB_Table_PrimaryKeyMap_AX09` line 70 still reads `"COLUMN":"RECID"`. sqldictionary
               duplicates: DEV **549 keys / 878 surplus rows, byte-identical to 2026-08-14** (DEV's
               raw layer has been frozen); TEST **903 keys / 1,336 surplus** — so "growing" is true
               of TEST, not of DEV.
             - Bounded 5-table audit (part 3 item 3): `dataarea`, `ledgertable` clean;
               `crreportinggroups` has **improved to 0** duplicate keys from the 12 groups measured
               08-14, by a raw-data change rather than a fix. `inventtrans` shows ~7.2M duplicate
               `(INVENTTRANSID, DATAAREAID)` keys — **flagged, not diagnosed**: `INVENTTRANSID` may
               legitimately be one-to-many in AX, so this needs a decision on its true business key
               before being treated as the same defect class.
             - **Part 2 still not done, and its own citation is unverifiable:** the quoted
               `"range expansion — row-multiplying, mirrored"` comment on
               `ChartOfAccountToAlternativeChartOfAccount` **does not exist anywhere in the repo
               today**. Re-establish where it came from before relying on it.
             - `enriched.DeliveryAddress`: still present and empty in DEV with no view, as recorded;
               it **does not exist at all in TEST**.
2026-08-14 — created after the DEV deployment of `5ce780f` and the first `RowCheckLog` run.
2026-08-14 — started (session task)
2026-08-14 — diagnosed SalesInvoiceTransactions in full and SalesLineTransactions to 87%;
             measured the downstream impact.
2026-08-14 — SalesInvoiceTransactions FIXED and verified read-only: GEN-002 (SCDcurrent on
             crreportinggroups) + GEN-003 (InventTrans_Purchace -> OUTER APPLY TOP 1). The view
             body now returns 12,276,137 = ExpectedRowCount exactly. Uncommitted in Fabric-ETL.
             Handover doc for Simon created: design/ATOMIC_GENERATOR_CHANGES.md.
             Remaining: GEN-003b + GEN-004 on SalesLineTransactions, and GeneralLedgerTransactions.
2026-08-14 — committed (Fabric-ETL 0a7f826, pushed) and VERIFIED IN DEV. Niels ran Update from
             git; rebuilt that one table with transform.sp_CreateTableAsSelect (224 s) and ran
             sp_RowCheck. RowCheckLog: Success, difference 0, 12,276,137 rows. Revenue dropped
             from 6,597,816,949.21 to 6,382,869,846.81 exactly as predicted. Zero duplicate base
             keys left; the vendor and reporting-group columns are still populated.
             NOT YET DONE: curated still holds the inflated fact.SalesTransactions - it needs
             PL_Transform_Curated to pick this up, which rebuilds the whole curated layer.
2026-08-16 — CLOSED for the two sales tables. Both are green in DEV: SalesInvoiceTransactions
             12,276,137 and SalesLineTransactions 5,855,702, each equal to ExpectedRowCount.
             27 of 28 tables pass on the 08-16 08:31 run.
             Shipped: Fabric-ETL 0a7f826 (GEN-002 + GEN-003), 3a72fca (GEN-003b + GEN-005),
             4328657 (GEN-005 reshaped to a derived table after admission control rejected the
             correlated apply). GEN-004 withdrawn - my probe error, not a defect.
             Incident: enriched.SalesLineTransactions was absent from DEV for 47 minutes because
             sp_CreateTableAsSelect drops before it creates and the CTAS was rejected. Restored.
             STILL OPEN, and why this task stays in-progress:
               - GeneralLedgerTransactions +4 rows: not started.
               - Part 2 of the task, auditing which of the 28 expectations are independent vs
                 mirrored, is NOT done. 27 greens are not yet evidence.
             Split out: 2026-08-14-carlras-raw-scd-key-sqldictionary (raw key map).
2026-08-17 — MERGED: 2026-08-14-carlras-raw-scd-key-sqldictionary folded back in as part 3
             (same investigation, same fix window). Open work is now: GeneralLedgerTransactions
             +4, the 28-expectation audit, and the raw key-map re-key + repair + audit.

