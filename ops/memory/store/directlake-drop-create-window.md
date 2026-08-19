---
id: directlake-drop-create-window
type: semantic
status: distilled
created: 2026-08-19
source: ops/memory/daily/2026-08-18.md
project: customers/Carl-Ras/datahub
---

# Drop-create deletes the parquet files Direct Lake reads: ~25 s per table, self-healing

Direct Lake reads the actual parquet files. Atomic's curated `sp_CreateTableAsSelect` DROPs and
re-CREATEs each table, so the model is left framed on files that no longer exist.

**Measured, one clean CTAS on a settled model:**
- resident columns keep answering throughout, with the pre-rebuild values - polled every second
  across two full cycles, never an error, never zero
- a column **not** resident fails: `ParquetStatusException ... StatusCode = 404`, then
  "OneLake security configuration has changed"
- **+24.8 s: automatic `DirectLakeFraming` completes and everything reads again**

So the model never goes empty; it partly works and partly errors. A three-minute block seen earlier
was self-inflicted - five rebuilds in forty minutes with manual reframes racing the automatic ones.

**Therefore keep "Keep your Direct Lake data up to date" ON**, which is the opposite of the usual MS
advice. That advice assumes append/merge ETL where the old files survive a load; with drop-create
they are deleted, so disabling automatic framing stretches the failure window from ~25 s per table to
the entire build.

Acceptable for a nightly build that finishes before anyone opens a report. It becomes urgent the
moment curated is rebuilt during working hours - then merge/append is required.
