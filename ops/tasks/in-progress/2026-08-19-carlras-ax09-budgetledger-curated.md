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

## Built 2026-08-20 — `Fabric-ETL` `995f187` (pushed, not yet in the service)

Five new files, nothing existing modified:

| File | What |
|---|---|
| `…Enriched_AX09/viewtransform/Views/BudgetLedger.sql` | 60 cols, all 21 models, joins to ledgertable / budgetmodel / currency / companyinfo / dimensions / LEDGERACCOUNTTYPE enum / sqldictionary |
| `…Enriched_AX09/rowcheck/Views/BudgetLedger.sql` | expectation = count of current `ledgerbudget` rows |
| `…Enriched_AX09/enriched/Tables/BudgetLedger.sql` | DDL, script-derived from the view's CONVERT types |
| `…Curated/viewfacttransform/Views/BudgetLedger.sql` | 34 cols, surrogate keys to ChartOfAccount / LegalEntity / SalesChannel, `ModelNum = '2010'` |
| `…Curated/fact/Tables/BudgetLedger.sql` | DDL, script-derived |

Verified read-only against DEV before commit: enriched builds **1,596,773** rows = rowcheck exactly
(no fan-out); curated builds **842,590** rows, 1 model, 0 orphans on ChartOfAccount and LegalEntity,
6,933 (0.8%) on SalesChannel — `fact.GeneralLedgerTransactions` runs 31% on that same join.

**Model filter confirmed by the customer 2026-08-21** — a Carl Ras employee's own reporting query
filters `MODELNUM = N'2010'` and `DATAAREAID = N'CR'`, and our fact reproduces it exactly (account
`01021` Varesalg, 2026: 10,542 rows, −1,146,443,286.98, 40 departments). Supporting evidence:
`MODIFIEDDATETIME` shows `2010` written every year for seventeen years, each year touching that year
and the next, last write 2026-03-26 — the most recent of all 21 models by seven weeks.
`REVISIONDATE` is `1900-01-01` everywhere and `BLOCKED` is `0` on all 29, so neither discriminates.
**Do not derive the model from recency** — "most recently modified" would have picked `0-PKT` (335
rows, last period 2012) for six weeks earlier this year.

**No date window, deliberately** — sibling facts disagree (3/3/5 years, four with none) and GL holds
one month (`2026-08-17-carlras-curated-data-loss-windows`). A budget fact shorter than the actuals it
is compared against would silently drop variance rows. Apply GL's window here when GL's is fixed.

## Live in DEV 2026-08-21

| Object | Rows | Check |
|---|---|---|
| `enriched.BudgetLedger` | 1,596,773 | `rowcheck` **Success**, difference 0 (`transform.RowCheckLog`, 08:16:34Z) |
| `fact.BudgetLedger` | 842,590 | 1 model, 0 orphans on ChartOfAccount + LegalEntity, 6,933 (0.8%) on SalesChannel, 2010-01-04 → 2026-12-31 |

Every figure matches what was measured read-only before the commit. Built by calling
`transform.sp_CreateTableAsSelect` and `sp_RowCheck`, then `facttransform.sp_CreateFactTableAsSelect`,
scoped to this table — neither transform pipeline takes a table parameter, so running them whole
would have rebuilt all 31 enriched tables for nothing.

**Cross-warehouse ordering cost one failed sync.** `995f187` carried both warehouses in one commit and
Update from git failed with `DmsImportDatabaseException … Invalid object name
'Warehouse_Enriched_AX09.enriched.BudgetLedger'` — Fabric imports warehouse items independently and
does not order them, and the import rolls back whole (verified: neither warehouse gained an object).
This is `fabric-warehouse-git` skill failure 4, and the cure is two commits, producer first: `7d393a0`
held the curated half back, `3c98cde` returned it once enriched existed. Two syncs is the minimum for
a new cross-warehouse entity — worth saying up front next time.

Both normalising commits from the workspace have landed (`cf9da70`, `0575f41`). Note for anyone
regenerating these files: re-running the emitter rewrites the `Auto Generated` hash on the enriched
views and would revert Fabric's normalisation — that hash comes from Fabric's parsed model and cannot
be recomputed locally.

## Semantic model — Direct Lake, pushed 2026-08-21 (`Semantic-Model` `c14e9d3`)

`Model_OneLake.SemanticModel` only; `Model.SemanticModel` (Import, 36 import partitions) untouched.

- `tables/Budget Ledger.tmdl` — new, 34 columns, `mode: directLake` over `fact.BudgetLedger` via
  `DatabaseQuery`. Columns generated from the warehouse DDL so the model cannot drift from the table.
  Folders/hidden flags/`summarizeBy` follow `General Ledger Transactions`. `lineageTag`s are uuid5 of
  the object name, so regenerating is idempotent rather than churning GUIDs.
- `relationships.tmdl` — +5: Chart of Account, Legal Entity, Sales Channel via the surrogate keys;
  `Start Date` → `Date.Date` active, `End Date` → `Date.Date` inactive (mirrors GL's
  Trans Date / Document Date).
- `model.tmdl` — +1 `ref table 'Budget Ledger'`.

**Line-ending trap in this repo:** `relationships.tmdl` and `model.tmdl` are CRLF, the table `.tmdl`
files are LF. Writing everything LF silently no-op'd the `model.tmdl` edit — the anchor string never
matched. The emitter now preserves each file's own convention.

**Noted, not acted on:** `Model_OneLake` is not pure Direct Lake — 7 partitions are still `mode:
import` (the `CG | …` / `FP | …` / `PM | …` helper and measure tables). Belongs to
`2026-08-18-carlras-directlake-conversion`.

## Live in TEST 2026-08-21

Deployed `Warehouse_Enriched_AX09` then `Warehouse_Curated` — separate deployments, dependency
order — then built with the same three statements used in DEV. Every figure matches DEV exactly:
enriched **1,596,773** (row check Success, difference 0), fact **842,590**, 1 model, orphans
0 / 0 / 6,933, span 2010-01-04 → 2026-12-31, ΣAmountMst −517,770,124.91. Both environments read the
same shared landing zone, so an exact match is expected and a difference would have meant a build
fault. No ingest or chain rebuild was needed: TEST's raw already held `ledgerbudget` in full.

Two authoring defects were found and fixed on the way, both surfacing as the same
`Incorrect syntax near '-'` — now rules in `datahub/CLAUDE.md` > Conventions: never write the
`-- Auto Generated` header on a new file (Fabric owns line 1, and it eats the first character of
yours), and serialised `.sql` must be pure ASCII (an em dash does not survive the round trip).
Also fixed `tools/wh_query.py`, which reported error 15816 from its `nextset()` probe after DDL
that had already applied — that cost a misdiagnosis.

**Recurring, not yet solved:** every Update from git touching `Warehouse_Curated` empties
`dim.Date` and `dim.AlternativeChartOfAccount` (DacFx rebuild). Rebuilt twice this session. The
other fifteen dims survive, which points at something specific to these two — likely the
GEN-008/009 column additions not matching the table DDL in git. It is silent: the schema looks
right and the table is simply empty.

## To do

1. **Niels: Update from git on `Semantic-Model-DEV`**, then a framing refresh so `Budget Ledger`
   binds to the Delta files and answers a query.
2. **PROD** — same two-deployment order, then the same three statements.
3. **Direct Lake model in TEST is a separate piece of work.** `Model_OneLake` has never been paired
   to TEST (`targetItemId: null`); TEST carries a TEST-only `Model_Optimized` instead, and only the
   Import `Model` is paired through. `Model_OneLake`'s `DatabaseQuery` also hardcodes the DEV
   workspace and curated warehouse GUIDs. Belongs to `2026-08-18-carlras-directlake-conversion`.
4. Chase the two dims that empty on every curated sync (see above).
5. Confirm the SCD2 key handling for `ledgerbudget` in `Lakehouse_Util.rawtablekeymap_ax09` /
   `NB_Table_PrimaryKeyMap_AX09` — raw already carries `SCDcurrent`/`SCDeffectiveDate`, so this is a
   check, not expected work.

No registration step is needed: `PL_Transform_Enriched_AX09` and `PL_Transform_Curated_Fact`
enumerate `INFORMATION_SCHEMA.VIEWS`, so both views join the chain as soon as they exist.

## Why

Budget against actual is the most common finance reporting there is and it is absent from the model
today. The entity touches all four layers, so it also tests whether "a new AX09 entity" is a routine
for us yet.

## Log
- 2026-08-19 — created. First pass read only the git repos and concluded no source existed; Niels
  pointed out `ledgerbudget` in raw. Measured in DEV: the table is present with 1.6M rows across 21
  budget models, only model `2010` current. Ingest is done — the gap is enriched → curated → model.
  Nothing changed.
- 2026-08-20 — built and pushed (`Fabric-ETL` `995f187`, approved): five new files, no existing file
  modified. Both views validated read-only against DEV first — row counts and orphan rates in the
  section above. Awaiting Niels's Update from git on `Fabric-ETL-DEV`, then the transform runs.
- 2026-08-21 — **BudgetLedger is in the curated layer in DEV.** One failed sync from the
  cross-warehouse ordering rule, resolved by splitting producer-first (`7d393a0`, `3c98cde`). Built
  and verified: 1,596,773 enriched / 842,590 curated, every number matching the pre-commit
  measurement. Remaining: Finance confirmation of the model, the semantic model, the GEN log entry,
  and promotion to TEST/PROD.
- 2026-08-21 — model `2010` confirmed by Niels; GEN-011 logged (`datahub` `2fde2cf`, which also
  added the missing GEN-010 index row); Direct Lake model updated and pushed (`Semantic-Model`
  `c14e9d3`). Deployment question answered: the deployment pipeline works, but as two deployments in
  dependency order — `Warehouse_Enriched_AX09` first, then `Warehouse_Curated` — for the same reason
  the git sync needed two commits. Both in one selection reproduces the failure, and a failed
  warehouse import leaves an orphan that makes the retry fail with "already exists".
