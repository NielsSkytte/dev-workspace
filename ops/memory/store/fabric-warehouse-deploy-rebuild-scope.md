---
id: fabric-warehouse-deploy-rebuild-scope
ts: 2026-08-18T21:35:00Z
type: semantic
scope: workspace
tags: [fabric, warehouse, deployment, dacfx, data-loss]
source: session:1515f867-fcac-47e5-97f0-1366fb517bfb
status: distilled
description: "A Fabric warehouse deployment rebuilds and empties a table on a column DROP, not only on an ordinal change - 31 of 33 tables emptied in one TEST hop while the prediction was 1"
---

## What happened

DEV -> TEST deployment of the Carl Ras `Fabric-ETL` stage, 2026-08-18. The pre-flight predicted
**one** emptied table (`enriched.SalesInvoiceTransactions`, which gained two columns and reordered
110). Measured after the deploy:

| Warehouse | Emptied | Kept |
|---|---|---|
| `Warehouse_Enriched_AX09` | **29 of 33** - every table that lost `PIN_RowCheck` | `Identity.SalesToCampaigns` 11.3M, `enriched.SalesResponsible`, `enriched.WorkCalendar` |
| `Warehouse_Enriched_CVR` | `enriched.CentralCompanyRegister` (6 column **type** changes) | - |
| `Warehouse_Curated` | `fact.SalesTransactions` (one added column), `outbound.Marketo_Lead` (new) | 27 tables incl. all dims |
| `Warehouse_Enriched_GTM` / `_Marketo` | none (schema-identical) | 6.9M activities, 31k leads |

## The correction

The rebuild trigger is wider than "column order changed". **Any** shape change DacFx cannot express
as an in-place `ALTER` rebuilds the table, and it arrives empty:

- column **added**
- column **dropped** - including a trailing one, which is the case that was mis-predicted
- column **type** changed
- ordinal position changed

Rule of thumb that would have been right: **a table whose column list differs at all between source
and target comes back empty.** Diff `INFORMATION_SCHEMA.COLUMNS` between the two environments before
the hop and count the tables, rather than reasoning about which change is "in-place".

## Also learned

`sys.partitions.rows` is **not populated** in a Fabric Warehouse - it returned 0 for tables holding
113M rows. Use `COUNT_BIG(*)` per table. A row-count sweep built on `sys.partitions` will report a
healthy warehouse as empty and an empty one as healthy.

## Consequence, and why it was still acceptable

Nothing was lost: raw lakehouses are untouched by a warehouse deploy, and enriched/curated are CTAS
derivations rebuilt by the chain. But between the deploy and the next full run the target is
**internally inconsistent** - in this case curated held pre-deploy dims and
`fact.GeneralLedgerTransactions` (289,596 rows) beside an empty `fact.SalesTransactions`. Nothing
should read the environment in that window, and the recovery run must be planned into the same
sitting as the deploy.
