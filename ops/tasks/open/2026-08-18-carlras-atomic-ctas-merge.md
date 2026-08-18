---
title: Carl Ras — Atomic curated drop-create deletes the files Direct Lake reads; move to merge/append
status: open
created: 2026-08-18
project: customers/Carl-Ras/datahub
owner: fabric-back
priority: normal
blocked_by: only worth doing once the Direct Lake conversion is committed to
activity:
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
- 2026-08-18 — created from the drop-create test during the Direct Lake trial.
