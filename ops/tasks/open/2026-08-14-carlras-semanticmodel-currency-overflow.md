---
title: Carl Ras — semantic model refresh fails on a Currency overflow (PL_MainExecution's last stage)
status: open
created: 2026-08-14
project: customers/Carl-Ras/datahub
owner: semantic
priority: normal
blocked_by: needs the semantic model developer consulted first
activity:
fno_task:
source: direct
---

## What

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

**This is a different failure from the previous one.** `PL_Update_SemanticModel` last failed
2026-08-11 with `403 Forbidden` on the refresh POST. That authorisation problem is not what
happened here — the refresh started and ran. Whether the 403 is also still latent is unknown;
it did not surface this time.

It is also **not a regression**. This is the first refresh ever attempted against a
freshly-built Curated layer — `PL_Transform_Curated` had never completed before 2026-08-14.

## Why

It is the only thing standing between DEV and a green end-to-end chain, which is the goal of
`2026-08-11-carlras-operation-hardening`. Everything upstream now works.

## Where to look

Sweep the money columns of the Curated facts for out-of-range values:

```sql
-- per candidate column, on Warehouse_Curated
SELECT MIN([col]), MAX([col]) FROM [fact].[SalesTransactions];
-- anything beyond ±922,337,203,685,477.5807 cannot land in a Currency column
```

**Lead, inference not diagnosis:** `viewtransform.SalesLineTransactions` and
`SalesInvoiceTransactions` both compute money through divisions guarded only by `NULLIF`, e.g.
`/ salesline.[Qty_Scaled]` and `/ COALESCE(NULLIF(exchrates.[EXCHRATE],0)/100,1)`. `NULLIF`
catches an exact zero but not a very small non-zero denominator, which would produce an
enormous quotient. Worth checking before assuming bad source data.

Also worth ruling in or out: whether the three tables inflating their row counts
(task `2026-08-14-carlras-enriched-rowcount-failures`) contribute. Duplicated rows do not
change an individual value, so they are unlikely to cause a per-value overflow — but both
findings sit in the same fact lineage.

## Blocked on

**Consult the semantic model developer first** (Niels's call, 2026-08-14). The fix may belong
in the model (column data type — Fixed Decimal vs Decimal) rather than in Curated, and that is
the model owner's decision. Do not change Curated column types unilaterally.

## Notes

- The model in DEV was last refreshed successfully well before this; the chain has never
  completed end to end.
- `PL_MainExecution` history: 8 runs, this is the first to clear Raw. Raw/Enriched/Curated
  passing is itself new ground.

## Log
2026-08-14 — created from the first PL_MainExecution run to reach the semantic model stage.
