---
title: Carl Ras — Atomic curated drop-create deletes the files Direct Lake reads; move to merge/append
status: open
created: 2026-08-18
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by: only worth doing once the Direct Lake conversion is committed to
activity: SemanticModel
fno_task:
source: session
---

## What

`transform.sp_CreateTableAsSelect` and its siblings (`facttransform.sp_CreateFactTableAsSelect`,
`dimtransform.*`, `bridgetransform.*`, `outboundtransform.*`) all do the same thing:

```sql
DROP TABLE IF EXISTS fact.<T>;
CREATE TABLE fact.<T> AS SELECT * FROM viewfacttransform.<T>;
```

A Direct Lake semantic model reads the **actual parquet files**. The DROP deletes them, so the model
is left framed on files that no longer exist. Replace drop-create with a MERGE/append pattern for at
least the large facts, so the files survive the load.

## The measured effect (DEV, 2026-08-18)

One CTAS on `fact.SalesTransactions`, model left alone, no manual reframe:

| t after CTAS | |
|---|---|
| +0.0 s | column not already in memory → `ParquetStatusException ... StatusCode = 404` |
| +6.7 → +18.8 s | → *"OneLake security configuration has changed"* |
| **+24.8 s** | automatic `DirectLakeFraming` completes, everything reads again |

**Columns already resident keep answering throughout, with the pre-rebuild values** — polled once a
second across two full cycles, never an error, never zero. So a report mid-rebuild does not go blank;
it partly works and partly errors, depending on which columns happen to be in memory.

Every curated table behaves this way, so a full `PL_Transform_Curated` produces ~29 of these windows
spread through the build.

## Why it can wait

For a nightly build that finishes before anyone opens a report, ~25 s per table is acceptable, and it
self-repairs. Compare the alternative it replaces: a 20-60 minute import refresh that currently fails
outright on memory. The trade is strongly favourable as it stands.

**It stops being acceptable if curated is ever rebuilt during working hours** — intra-day refreshes,
a re-run after a fix, or a move to more frequent loads. That is the trigger for doing this work.

## Also worth having

- **Incremental framing.** Overwriting a Delta table erases the Delta log, so Direct Lake cannot frame
  incrementally and re-transcodes columns from cold after every build (measured: 1.1 s simple / 5.8 s
  heavy on the first query afterwards). A merge/append pattern keeps the log and the dictionaries.
- **Consistency during the build.** With drop-create plus automatic framing, mid-build the model holds
  a mixture of rebuilt and not-yet-rebuilt tables.

## Not this

Do **not** treat this as a Direct Lake problem or a composite-model problem. Direct Lake works fine
over a warehouse that appends or merges, and the three Import tables play no part in it. The cause is
the drop-create, and nothing else.

## Context

- `customers/Carl-Ras/datahub/design/DIRECTLAKE_CONVERSION_ASSESSMENT.md` — the full test.
- Atomic is Simon's generator; changing the CTAS procedures is a framework change, not a
  Carl Ras-local one. Same ownership route as GEN-002/003/005.
- Related: `2026-08-18-carlras-directlake-conversion`.

## Log
- 2026-08-31 — **VERIFIED ACCURATE.** All five procedures still drop-then-create, byte-identical to
  the repo, in the live warehouses: `transform.sp_CreateTableAsSelect`,
  `facttransform.sp_CreateFactTableAsSelect`, `dimtransform.sp_CreateDimTableAsSelect`,
  `bridgetransform.sp_CreateBridgeTableAsSelect`, `outboundtransform.sp_CreateOutboundTableAsSelect`.
  No MERGE or append anywhere. `blocked_by` still holds.
  - View count is **30** today, not ~29 (`viewfacttransform` 9, `viewdimtransform` 17,
    `viewbridgetransform` 3, `viewoutboundtransform` 1) — the +1 is `fact.BudgetLedger`.
  - **The trigger condition has technically fired**, twice, by our own hands: a Completed
    `PL_MainExecution` in DEV 2026-08-20 12:19-14:00 UTC (14:19-16:00 CEST) and two in TEST on
    2026-08-05 during working hours. All `invokeType: Manual`, none from the nightly schedule, and
    neither environment carries live report traffic. So the letter of "rebuilt during working hours"
    is met while the spirit — production load hitting a rebuild window — is not.
  - **Direct Lake is still not committed to**, so `blocked_by` is correct: `Model_OneLake` exists
    only in DEV; Sales-DEV's five production-named reports remain bound to the Import `Model` with
    only the five `[OneLake]` clones on Direct Lake; Sales-TEST has no Direct Lake reports; and the
    **Sales PROD workspace holds zero reports and zero datasets**.
  - **Scope correction:** the sibling claim that `dim.Date` / `dim.AlternativeChartOfAccount`
    "rebuild EMPTY" is **not reproducible** — both are populated and match their views in DEV and
    TEST. That emptying is tied to `Update from git` / DacFx warehouse rebuilds, a different
    mechanism from the routine drop-create examined here. It belongs on
    `2026-08-19-carlras-ax09-budgetledger-curated` to-do 4, not on this task.
- 2026-08-18 — created from the drop-create test during the Direct Lake trial.
