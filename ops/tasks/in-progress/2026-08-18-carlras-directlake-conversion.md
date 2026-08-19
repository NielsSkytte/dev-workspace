---
title: Carl Ras — convert the semantic model from Import to Direct Lake (composite on OneLake)
status: in-progress
created: 2026-08-18
project: customers/Carl-Ras/datahub
owner: semantic
priority: high
blocked_by:
activity: SemanticModel
fno_task:
source: session
---

## What

Replace the Import semantic model with `Model_OneLake` — a Direct Lake **on OneLake** composite over
`Warehouse_Curated`. Built and verified in DEV on 2026-08-18. Full assessment, every measurement and
every MS Learn citation: `customers/Carl-Ras/datahub/design/DIRECTLAKE_CONVERSION_ASSESSMENT.md`.

Shape: 25 tables Direct Lake, 3 Import (`Date`, `Alternative Chart of Account`, `Last Refresh` —
they carry the two calculated columns and the Power Query timestamp), 6 calculated/parameter tables,
177 measures, 55 relationships, 3 calculation groups.

## Why

The Import model can no longer refresh. On 2026-08-18 the DEV model failed at 122 s with
`consumed 4665 MB, memory limit 4661 MB`; TEST fails the same way and `NB_Refresh_SemanticModel_Full`
exists only to work around it with an adaptive batch-halving ladder. Direct Lake removes the rebuild
entirely — framing is metadata only.

## Measured in DEV, 2026-08-18

| | Import | Direct Lake composite |
|---|---|---|
| refresh / frame | **fails, out of memory** | **21.8 s** |
| all 177 measures evaluate | — | 177 OK, 0 failed |
| `Sales \| Revenue \| Std` vs SQL | — | within 0.011 kr on 2.8 bn |
| report render, median of 3 (Salg / Finance / Kunde) | 11.0 / 10.0 / 11.0 s | 9.1 / 9.0 / 12.0 s |
| Inventory Transactions rows carried | 3.3M | 17M |
| cold query after a rebuild | — | 1.1 s simple, 5.8 s heavy |
| parquet files per table (guardrail 1,000) | — | max 84 |
| curated size on OneLake (guardrail 10 GB) | — | 3.15 GB |

## Done

- **`Model_OneLake` is now PURE Direct Lake** (`6f816c58-faf6-458c-afd5-76c4d2add4ef`,
  Semantic-Model-DEV): 27 Direct Lake tables, 7 calculated/parameter tables, **no Import tables**,
  one data source (`AzureDataLakeStorage`), no SQL connection, no credentials.
  `Semantic-Model` `503b5d4`.
- **GEN-008 / GEN-009** moved both calculated columns into the curated views
  (`Fabric-ETL` `98cba4c`, `ac959df`, `c4a0f85`) and both dims were rebuilt in DEV.
  `Last Refresh` dropped; the utility measure now reports data freshness from
  `MAX('Sales Transactions'[Financial Date])`.
- Verified: frame 22 s, 177/177 measures evaluate, revenue unchanged at 2,814,856,410.6069,
  `Linje` 1,321 distinct (identical to the Import model), render times within a few hundred ms of
  Import across three reports.
- Five Sales-DEV reports cloned, suffixed `[OneLake]`, rebound to the pure model; originals untouched.
- Earlier composite scaffolding (`CON-WI-SQL-Warehouse_Curated_DEV`, Contributor on Fabric-ETL-DEV
  for Semantic-Model-DEV's identity) is no longer required by the model but is left in place.

## Next session — deploy to TEST, in this order

TEST is **not ready**: `viewdimtransform.Date.MonthSelector` and
`viewdimtransform.AlternativeChartOfAccount.Linje` are both missing there, as are the columns on the
dims. Deploying the model first would fail on framing.

1. **Deploy `Fabric-ETL` DEV→TEST** so the curated views carry GEN-008/009. Audit what else is
   pending in that pipeline first — it has not been reviewed.
2. **Rebuild `dim.Date` and `dim.AlternativeChartOfAccount` in TEST**
   (`EXEC dimtransform.sp_CreateDimTableAsSelect '<table>'`, seconds each), or wait for the nightly
   `PL_Transform_Curated`.
3. **Grant Semantic-Model-TEST's workspace identity Contributor on Fabric-ETL-TEST.** Not proven
   necessary for a pure Direct Lake model — DEV frames without an explicit connection — but the DEV
   grant is in place and cannot be ruled out as the reason. Cheap insurance.
4. **One data source rule on the Model pipeline's Test stage**, pointing the `AzureDataLakeStorage`
   source at Fabric-ETL-TEST's `Warehouse_Curated` OneLake path
   (`c2792367-e5e1-411f-bdac-5c493733b911` / `908304be-23f1-4da8-9559-c7d24f271ba4`). Direct Lake
   models do **not** autobind; without the rule TEST reads Fabric-ETL-DEV, silently.
5. **Deploy `Model` DEV→TEST**, frame, verify. Note this also promotes the Import `Model`, including
   the `Campaign Forecasts[Forecast Quantity]` retype.

## Also to do

1. **Framing step at the end of `PL_Transform_Curated`, with retry and backoff.**
   `PL_Update_SemanticModel` becomes a framing call instead of a memory-managed import refresh.
   Retry is required — framing immediately after a rebuild fails ("A direct lake table ... is not
   found", and "source tables do not exist or access was denied").
2. **Leave "Keep your Direct Lake data up to date" ON.** With drop-create the old files are deleted,
   so disabling it extends the failure window from ~25 s per table to the whole build. This is the
   opposite of the usual MS guidance and the reasoning is in the assessment.
3. **Deployment rules per target stage — two per stage.** Direct Lake models do **not** autobind;
   without rules, TEST would deploy still reading Fabric-ETL-DEV, silently. One rule for the SQL
   source (Import tables), one for the ADLS/OneLake source (Direct Lake tables).
4. **Per-stage identity grants:** Semantic-Model-TEST's workspace identity → Contributor on
   Fabric-ETL-TEST, and the same for PROD.
5. **Decide the GL window** now that memory is no longer the constraint. 3 years costs ~2.1 GB on
   OneLake and fits the current SKU; full history is ~10.3 GB and does not.
6. **Agree with Mads that derived columns go in the curated view, not the model.** Direct Lake accepts
   no calculated columns. Two exist today and one arrived on 2026-08-05 as ordinary report work; the
   composite keeps them alive on Import tables, but that is a workaround, not a policy.
7. Repeat the report render test across a working day — two Direct Lake outliers (16.7 s, 31.3 s) had
   no Import equivalent and the cause is not established.

## Open

- The workspace is git-connected to `main`, but `main` refuses direct commits, so anyone editing a
  model in the DEV workspace cannot commit it back. `Model` has been sitting with uncommitted
  workspace changes because of this. Not a Direct Lake problem, but it blocks Update from git.
- Related: `2026-08-18-carlras-atomic-ctas-merge` (the drop-create pattern behind the 25 s windows).

## Log
- 2026-08-18 — created. Model built, verified and benchmarked in DEV; reports cloned and rebound.
- 2026-08-19 — model taken to **pure Direct Lake** and re-verified end to end. Two traps found and
  fixed on the way: a Fabric Warehouse CTAS rejects `nvarchar` (so `NCHAR(8203)` needs a `VARCHAR`
  cast — and because the proc drops before it creates, the failure left `dim.AlternativeChartOfAccount`
  missing until it was fixed), and the warehouse's BIN2 collation versus DAX's case-insensitive
  comparison made `Linje` 1,320 distinct in SQL but 1,316 in the model until it was partitioned by
  `UPPER(Txt)`. Parked before the TEST deployment — see *Next session*.
- 2026-08-19 — **time attribution split.** Session `b436423e` ran 08-17 → 08-19 and was tagged
  `2026-08-17-carlras-curated-data-loss-windows` throughout, because that is what it started on. Only
  the first stretch on 08-17 (measuring the curated windows and the GL fact) belongs there; everything
  from the Direct Lake assessment onward belongs to this task. The session tag was switched here on
  08-19 17:25Z, so the earlier hours need reassigning at the review gate.
