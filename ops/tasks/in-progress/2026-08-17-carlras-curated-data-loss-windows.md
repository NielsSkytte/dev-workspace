---
title: Carl Ras — data missing in Curated: fact.GeneralLedgerTransactions holds only the current month; audit every curated window
status: in-progress
created: 2026-08-17
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: high
blocked_by:
activity: AX09Import
fno_task:
source: direct
---

## What

Niels, 2026-08-17: *"GeneralLedgerTransactions only has data for august this year."* Confirmed by
measurement, and the cause is a one-character-class difference in a generated view.

### Measured 2026-08-17 (DEV, read-only via `tools/wh_query.py`)

| layer | object | range | rows |
|---|---|---|---|
| Enriched | `enriched.GeneralLedgerTransactions` | 2001 → 2026, every year populated | 113,276,717 |
| Curated | `fact.GeneralLedgerTransactions` | **2026-08-01 → 2026-09-01** | **226,262** |

So nothing is missing on ingest. **The history is dropped between Enriched and Curated.**

### Cause — the window on the curated fact view

`viewfacttransform.GeneralLedgerTransactions` (line 86-87):

```sql
WHERE
    TransDate >= DATEFROMPARTS(YEAR(GETDATE()), MONTH(GETDATE()), 1)
```

No year offset. It resolves to the 1st of the *current month*, so the fact is rebuilt each run
holding one partial month and the previous month's rows disappear the moment the month rolls over.

Every other curated fact view uses the same expression **with** an offset:

| view | filter column | window |
|---|---|---|
| `SalesTransactions` | `FinancialDate` / `SalesTable_CreatedDate` | `YEAR(GETDATE()) - 3` |
| `InventoryTransactions` | `DateFinancial` | `YEAR(GETDATE()) - 3` |
| `SalesForecasts` | `TransactionDate` | `YEAR(GETDATE()) - 5` |
| **`GeneralLedgerTransactions`** | `TransDate` | **`YEAR(GETDATE())` — no offset** |

That the shape is identical to the others except for the missing `- N` is why a slipped offset is
the leading hypothesis. **It is inference, not a diagnosis** — nobody has confirmed the intended
window for GL, and "current month only" could in principle be deliberate.

### Provenance

The line arrived in `Fabric-ETL` `c860a50` (2026-06-24, a workspace commit); the file's only
earlier commit is `a6b1a33`. The file carries the `-- Auto Generated (Do not modify)` header, so
the window comes from the Atomic generator's metadata for this entity — the same generator-
ownership problem as GEN-002/003/005 (`design/ATOMIC_GENERATOR_CHANGES.md`, owner: Simon).

## To do

1. **Establish the intended window for GL with the business** — 3 years like Sales, 5 like
   Forecasts, or full history. GL is 113M rows at full depth; a 3-year window is ~22M.
2. **Fix the window** in the generator metadata, or as a documented GEN-00x change if the
   generator cannot be reached first. Then rebuild `fact.GeneralLedgerTransactions`.
3. **Audit every curated window against what the reports actually need** — `CampaignForecasts`,
   `InventoryOnHand`, `OutputOrders`, `PickingRoutes` have no date filter at all; the three that do
   disagree (3 / 3 / 5 years). Nobody has checked those numbers against a stated requirement.
4. **Check the semantic model's own filters** — a second, independent window may sit in the model's
   partitions, so fixing Curated alone may not surface the history in reports.
5. **Decide whether a row-check should cover this class.** The enriched row-check compares a view
   against its source; nothing compares Curated against Enriched, which is why a fact holding
   0.2% of its source rows passed unnoticed.

## Why

A window that silently truncates is the same failure class as the enriched fan-out work
(`2026-08-14-carlras-enriched-rowcount-failures`): the data still looks plausible and every figure
is wrong. Here it is worse in one respect — the fan-out overstated revenue by 2.68%, while the GL
fact is missing essentially all of its history.

## How to see it

```sql
-- Warehouse_Curated
SELECT MIN(TransDate), MAX(TransDate), COUNT(*) FROM fact.GeneralLedgerTransactions;
-- Warehouse_Enriched_AX09
SELECT YEAR(TransDate) y, COUNT(*) FROM enriched.GeneralLedgerTransactions GROUP BY YEAR(TransDate) ORDER BY y;
```

## Log
- 2026-08-17 — created from Niels's observation; measured both layers in DEV and located the
  window in `viewfacttransform.GeneralLedgerTransactions`. Nothing changed yet.
- 2026-08-19 — **time attribution note.** Session `b436423e` carried this task's tag from 08-17 to
  08-19, but only the 08-17 work (measuring every enriched table, every curated window, and locating
  the GL fact's current-month filter) belongs here. From the Direct Lake assessment onward the work is
  `2026-08-18-carlras-directlake-conversion`; the tag was switched there on 08-19 17:25Z. Reassign the
  08-18 and 08-19 hours at the review gate.
