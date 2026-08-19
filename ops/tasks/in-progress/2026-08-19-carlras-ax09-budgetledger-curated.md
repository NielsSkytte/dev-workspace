---
title: Carl Ras — BudgetLedger (AX09) into curated — a new fact through raw → enriched → curated
status: in-progress
created: 2026-08-19
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: medium
blocked_by:
activity: AX09Import
fno_task:
source: direct
---

## What

Niels, 2026-08-19: budgetledger needs to be in the curated layer. AX09 data.

**The source is already in raw.** The work is enriched + curated + model, not ingest.

### Measured 2026-08-19 (DEV, read-only via `tools/wh_query.py`)

| Layer | Budget object | Status |
|---|---|---|
| Raw | `Lakehouse_Raw_AX09.dbo.ledgerbudget` | **present** — 1,596,773 rows, 44 columns (SCD2), `STARTDATE` 2002 → 2026, 21 `MODELNUM`, 2 `DATAAREAID` |
| Raw | `Lakehouse_Raw_AX09.dbo.budgetmodel` | present |
| Enriched | `viewtransform` (30 views) | none |
| Curated | `viewfacttransform` (8), `viewdimtransform` (17), `viewbridgetransform` (3) | none |

`ledgerbudget` is a single flat table — no header/line split. Amount columns: `AMOUNT`, `AMOUNTMST`,
plus `QTY`/`PRICE`. Dimension columns `DIMENSION`, `DIMENSION2_`…`DIMENSION4_`, account on
`ACCOUNTNUM`, scenario on `MODELNUM`, period on `STARTDATE`/`ENDDATE` (+ `FREQCODE`/`FREQ` for
periodisation).

### Budget models present (rows / STARTDATE span)

Only `2010` carries current data: 842,590 rows, 2010 → 2026. The other 20 are historic or test —
`TestEH` (193k, incl. 1900 dates), `EST`/`EST1`/`EST2 test`, `Forecast` (2021-2023), `BUD*`, year-named
models. **Which model(s) count as the live budget is the first business question** — a fact built over
all 21 would double-count everything.

### Open points

1. **Which `MODELNUM` is the live budget**, and how new models get adopted over time (a hardcoded
   `= '2010'` would break next time Finance opens a new model).
2. **`STARTDATE` = 1900 on 54,438 rows** (all in `TestEH` plus some spillover) — decide whether they
   are filtered or corrected.
3. **`FREQCODE`/`FREQ` semantics.** A row spans `STARTDATE`→`ENDDATE`; whether the fact holds the
   period row as-is or is exploded to a monthly grain decides how it joins `dim.Date`.
4. **Grain, and the relation to `fact.GeneralLedgerTransactions`.** Budget and actual share
   ChartOfAccount / Dimensions / Date — decide whether this becomes its own fact on the same
   dimensions or a measure on the existing one.
5. **BudgetModel as a dimension.** `budgetmodel` already lands; a budget fact without the model
   dimension cannot separate scenarios (budget / revised / forecast). Note
   `viewtransform.SalesForecastLines` already has a commented-out `budgetmodel` join (lines 47, 66-69).
6. **Why the table is invisible in git — answered, and it is a risk of its own.** The repo holds a
   2026-04-29 snapshot of `PL_Ingest_AX09` (40 tables); every workspace runs 88-92 including
   `ledgerbudget`, uncommitted. Tracked in `2026-08-19-carlras-landingzone-dev-drift` — **do not run
   Update from git on `Landingzone-Code-DEV` until that is committed**, or the source for this fact
   stops being ingested.

## To do

1. Settle the live `MODELNUM` (or the rule that picks it) with Finance — see open point 1.
2. Confirm the SCD2 key handling for `ledgerbudget` in `Lakehouse_Util.rawtablekeymap_ax09` /
   `NB_Table_PrimaryKeyMap_AX09` (`RECID` + `SCDcurrent`).
3. `viewtransform.BudgetLedger` in `Warehouse_Enriched_AX09` + a `rowcheck` view, same pattern as the
   rest (cf. `2026-08-14-carlras-enriched-rowcount-failures`).
4. `viewfacttransform.BudgetLedger` + `fact.BudgetLedger` in `Warehouse_Curated`, registered in the
   execute chain (`PL_Transform_Curated_Fact` enumerates `INFORMATION_SCHEMA.VIEWS`).
   **Set the date window deliberately** — the existing facts disagree (3/3/5 years, four with no
   filter at all), see `2026-08-17-carlras-curated-data-loss-windows`.
5. Into the semantic model — relationships to Date / ChartOfAccount / Dimensions, and the Direct Lake
   constraint from `2026-08-18-carlras-directlake-conversion` (drop-create on curated deletes the
   files Direct Lake reads — `2026-08-18-carlras-atomic-ctas-merge`).
6. The files carry the `-- Auto Generated (Do not modify)` header: log new/changed views as GEN-xxx in
   `design/ATOMIC_GENERATOR_CHANGES.md` and keep the header line byte-intact.

## Why

Budget against actual is the most common finance reporting there is and it is absent from the model
today. The entity touches all four layers, so it also tests whether "a new AX09 entity" is a routine
for us yet.

## Log
- 2026-08-19 — created. First pass read only the git repos and concluded no source existed; Niels
  pointed out `ledgerbudget` in raw. Measured in DEV: the table is present with 1.6M rows across 21
  budget models, only model `2010` current. Ingest is done — the gap is enriched → curated → model.
  Nothing changed.
