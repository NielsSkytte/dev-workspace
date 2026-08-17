---
title: Carl Ras — operation_hardening (keep PL_MainExecution running green across DEV/TEST/PROD)
status: in-progress
created: 2026-08-11
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by: semantic model developer must be consulted on the Currency overflow (model data type vs Curated)
activity:
fno_task:
source: direct
---

## What
operation_hardening — make the daily `PL_MainExecution` chain run green and keep it that way.
Covers the run-failure work that follows the SPN-auth migration and the key-map/join fixes:
diagnosing and closing each remaining failure in the chain, and removing the classes of
fragility that produce them.

Open at creation (measured 2026-08-11):
- **TEST**: scheduled runs 08-10 and 08-11 fail at the last stage only — `Semantic Model` →
  `PL_Update_SemanticModel` → `Notebook1` (`NB_Refresh_SemanticModel`), `403 Forbidden` on the
  refresh POST. Raw/Enriched/Curated pass. TEST `Model` last refreshed 2026-08-07 06:54 UTC.
- **DEV**: no run since 2026-08-07 12:09 (Failed on `VL_ConnectionId|CON-SQLFabric-ETL_Lakehouse_Util`
  → `VariableNotFound`); that run predates commits `0d2dc5b` and `9153a8e`. Both DEV schedules disabled.
- **PROD**: no job instances; schedule disabled, owner is a user account.

### Current blocker — semantic model refresh fails on a Currency overflow

*(merged 2026-08-17 from `2026-08-14-carlras-semanticmodel-currency-overflow`; owner: semantic)*

`PL_MainExecution` in DEV now reaches its final stage and fails there. Run 2026-08-14
07:03:13 → 08:50:18 UTC (1h47m): **Raw, Enriched and Curated all passed**, `Semantic Model`
failed.

```
Operation on target Semantic Model failed:
  Operation on target Notebook1 failed:  (NB_Refresh_SemanticModel)
    refresh Failed:
      "Retry attempts for failures while executing the refresh exceeded the retry limit"
      0xC112001A  "Value was either too large or too small for a Currency.
                   The exception was raised by the IDataReader interface."
```

A value arriving from Curated is outside the range a Fixed Decimal / Currency column can
hold (±922,337,203,685,477.5807). The refresh retries, keeps hitting it, and gives up.

**This is a different failure from the 403.** `PL_Update_SemanticModel` last failed 2026-08-11 with
`403 Forbidden` on the refresh POST. That authorisation problem is not what happened here — the
refresh started and ran. Whether the 403 is also still latent is unknown; it did not surface this
time. It is also **not a regression**: this is the first refresh ever attempted against a
freshly-built Curated layer — `PL_Transform_Curated` had never completed before 2026-08-14.

**Where to look.** Sweep the money columns of the Curated facts for out-of-range values:

```sql
-- per candidate column, on Warehouse_Curated
SELECT MIN([col]), MAX([col]) FROM [fact].[SalesTransactions];
-- anything beyond ±922,337,203,685,477.5807 cannot land in a Currency column
```

**Lead, inference not diagnosis:** `viewtransform.SalesLineTransactions` and
`SalesInvoiceTransactions` both compute money through divisions guarded only by `NULLIF`, e.g.
`/ salesline.[Qty_Scaled]` and `/ COALESCE(NULLIF(exchrates.[EXCHRATE],0)/100,1)`. `NULLIF`
catches an exact zero but not a very small non-zero denominator, which would produce an
enormous quotient. Worth checking before assuming bad source data. Also worth ruling in or out:
whether the tables inflating their row counts
(`2026-08-14-carlras-enriched-rowcount-failures`) contribute — duplicated rows do not change an
individual value, so unlikely, but both findings sit in the same fact lineage.

**Blocked on: consult the semantic model developer first** (Niels's call, 2026-08-14). The fix may
belong in the model (column data type — Fixed Decimal vs Decimal) rather than in Curated, and that
is the model owner's decision. Do not change Curated column types unilaterally.

## Why
The chain is the platform's daily heartbeat. Raw/Enriched/Curated are current but the TEST
semantic model has been stale since 2026-08-07, and PROD has never been exercised. Every failure
so far has been an identity, variable-library or key-map issue rather than data logic — the same
classes will keep recurring until they are closed deliberately.

## Context
- `customers/Carl-Ras/datahub/CONTEXT.md` — project state; the semantic-model refresh/memory work.
- `customers/Carl-Ras/datahub/CLAUDE.md` — the 2026-08-11 conventions: nothing per-environment
  hardcoded; variable libraries are the environment contract; `Lakehouse_Util` must be seeded.
- `Fabric-ETL/Orchestration/Schedule/PL_MainExecution.DataPipeline` → Raw / Enriched / Curated /
  Semantic Model; the last stage is `PL_Update_SemanticModel` → notebook logicalId
  `33e45f7b-5e2d-86e7-48fb-e834b0d9a6f2` (`NB_Refresh_SemanticModel`, the old per-table plan).
  `NB_Refresh_SemanticModel_Full` exists but the pipeline does not point at it.
- `tools/fabric_identity.py` — the SPN identity migration; it has no semantic-model takeover.
- Measured on the 403: the SPN (`aa462763…` / object `f05f446a…`, the TEST schedule owner) reads
  the dataset and its refresh history over the Power BI API (200), and the dataset's
  `configuredBy` is `EXT_NSKC@carl-ras.dk`. Model ownership as the cause is inference, untested.
- Related tasks: `2026-07-07-carlras-fabric-scaleup` (capacity/model processing),
  `2026-07-16-carlras-gtm-inbound-ingest` (GTM is not yet in `PL_Execute_Raw`).

## Log
- 2026-08-11 — created; started (session task)
- 2026-08-17 — MERGED: `2026-08-14-carlras-semanticmodel-currency-overflow` folded in as the
  current blocker — it is the last stage of this same chain and was created stating so.
  `blocked_by` now carries the semantic-model-developer consult.
